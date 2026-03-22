from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SITE_DIR = ROOT / "site"
RECOVERY_DIR = SITE_DIR / "recovery"
SUMMARY_PATH = ROOT / "out" / "summary.json"
MANIFEST_PATH = RECOVERY_DIR / "manifest.json"
POST_LIKE_RE = re.compile(r"^https?://[^/]+/\d{4}/\d{2}/\d{2}/[^/]+/?$")
sys.path.insert(0, str(ROOT.parent))
from raw_cache import read_cached_bytes, write_cached_response  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retry targeted missing post pages for cwasteson.skolbloggen.se.")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=5)
    return parser.parse_args()


def entry_relative_path(normalized_url: str) -> str:
    path = urlsplit(normalized_url).path or "/"
    base = PurePosixPath(path.lstrip("/"))
    if path.endswith("/"):
        return str(base / "index.html")
    if base.suffix:
        return str(base.with_name(base.stem + ".html"))
    return str(base / "index.html")


def load_candidates() -> list[str]:
    candidates: list[str] = []

    if SUMMARY_PATH.exists():
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        for item in summary.get("failed_best_capture_lookups", []):
            url = item.get("url", "")
            if POST_LIKE_RE.match(url):
                candidates.append(url)

    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        for item in manifest.get("failed", []):
            url = item.get("url", "")
            if POST_LIKE_RE.match(url):
                candidates.append(url)

    seen: set[str] = set()
    deduped: list[str] = []
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        deduped.append(url)
    return deduped


def main() -> int:
    sys.path.insert(0, str((ROOT.parent / "bufsimrishamn").resolve()))
    import reconstruct_site  # type: ignore

    args = parse_args()
    all_candidates = load_candidates()
    selected = all_candidates[args.offset : args.offset + args.limit]
    client = reconstruct_site.ArchiveClient(max_retries=6, retry_backoff_seconds=3.0)

    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, str]] = []

    for url in selected:
        relative_path = entry_relative_path(url)
        destination = SITE_DIR / relative_path
        if destination.exists():
            results.append({"url": url, "path": relative_path, "status": "skipped_existing"})
            continue

        entry, error = reconstruct_site.resolve_best_entry(
            url,
            from_year=None,
            to_year=None,
            max_retries=6,
            retry_backoff_seconds=3.0,
        )
        if entry is None:
            results.append({"url": url, "path": relative_path, "status": "resolve_failed", "error": str(error or "")})
            continue

        archive_url = reconstruct_site.build_archive_raw_url(entry.best_timestamp, entry.best_original)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            cached = read_cached_bytes(ROOT, archive_url)
            if cached is None:
                content, _content_type = client.download(archive_url)
                write_cached_response(ROOT, archive_url, content, source="retry_missing_posts.py")
            else:
                content = cached
            destination.write_text(reconstruct_site.decode_html(content), encoding="utf-8")
            results.append({"url": url, "path": relative_path, "status": "downloaded", "archive_url": archive_url})
        except (HTTPError, URLError, TimeoutError) as exc:
            results.append({"url": url, "path": relative_path, "status": "download_failed", "archive_url": archive_url, "error": str(exc)})

    summary = {
        "candidate_count": len(all_candidates),
        "offset": args.offset,
        "limit": args.limit,
        "processed_count": len(selected),
        "downloaded_count": sum(1 for item in results if item["status"] == "downloaded"),
        "skipped_existing_count": sum(1 for item in results if item["status"] == "skipped_existing"),
        "failed_count": sum(1 for item in results if item["status"] not in {"downloaded", "skipped_existing"}),
        "results": results,
    }
    out_path = RECOVERY_DIR / f"retry-posts-summary-{args.offset:03d}-{args.limit:03d}.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
