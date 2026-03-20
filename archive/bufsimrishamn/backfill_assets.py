from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

import reconstruct_site


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan reconstructed HTML, resolve referenced archived assets, download missing files, and rewrite asset links locally."
    )
    parser.add_argument("--domain", default="bufsimrishamn.wordpress.com")
    parser.add_argument("--site-dir", default="site")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--offset", type=int, default=0, help="Start index into the sorted candidate list.")
    parser.add_argument("--limit", type=int, help="Optional limit for small verification passes.")
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-backoff-seconds", type=float, default=3.0)
    return parser.parse_args(argv)


def iter_html_files(site_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in site_dir.rglob("*.html")
        if "recovery" not in path.parts and "_assets" not in path.parts
    )


def collect_asset_candidates(site_dir: Path, domain: str) -> list[str]:
    candidates: set[str] = set()
    for html_file in iter_html_files(site_dir):
        html_text = html_file.read_text(encoding="utf-8", errors="replace")
        candidates.update(reconstruct_site.extract_asset_urls(html_text, f"https://{domain}/", domain))
    return sorted(candidates)


def append_log(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def rewrite_html_files(site_dir: Path, link_map: dict[str, str], domain: str) -> None:
    for html_file in iter_html_files(site_dir):
        relative_path = html_file.relative_to(site_dir).as_posix()
        html_text = html_file.read_text(encoding="utf-8", errors="replace")
        rewritten = reconstruct_site.rewrite_html(
            html_text,
            f"https://{domain}/",
            relative_path,
            link_map,
        )
        html_file.write_text(rewritten, encoding="utf-8")


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    site_dir = Path(args.site_dir)
    recovery_dir = site_dir / "recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)

    candidates = collect_asset_candidates(site_dir, args.domain)
    if args.offset:
        candidates = candidates[args.offset :]
    if args.limit is not None:
        candidates = candidates[: args.limit]

    candidates_path = recovery_dir / "asset_candidates.txt"
    candidates_path.write_text("\n".join(candidates) + ("\n" if candidates else ""), encoding="utf-8")

    asset_log_path = recovery_dir / "assets-log.jsonl"
    resolved_entries: list[reconstruct_site.SiteEntry] = []
    failures: list[dict[str, str]] = []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(
                reconstruct_site.resolve_best_entry,
                candidate,
                from_year=None,
                to_year=None,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
            ): candidate
            for candidate in candidates
        }
        for future in as_completed(future_map):
            entry, error = future.result()
            if entry is not None:
                resolved_entries.append(entry)
                append_log(asset_log_path, {"stage": "resolved", "url": entry.normalized_url, "best_timestamp": entry.best_timestamp})
            elif error:
                failure = {"stage": "resolve_failed", "url": future_map[future], "error": error}
                failures.append(failure)
                append_log(asset_log_path, failure)

    link_map: dict[str, str] = {}
    client = reconstruct_site.ArchiveClient(
        max_retries=args.max_retries,
        retry_backoff_seconds=args.retry_backoff_seconds,
    )
    downloaded = 0
    skipped_existing = 0

    for entry in sorted(resolved_entries, key=lambda item: item.normalized_url):
        relative_path = reconstruct_site.entry_relative_path(entry, primary_domain=args.domain)
        destination = site_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)

        for alias in reconstruct_site.make_aliases(entry):
            link_map[alias] = relative_path

        if destination.exists():
            skipped_existing += 1
            append_log(asset_log_path, {"stage": "skipped_existing", "url": entry.normalized_url, "path": relative_path})
            continue

        archive_url = reconstruct_site.build_archive_raw_url(entry.best_timestamp, entry.best_original)
        try:
            content, _ = client.download(archive_url)
            destination.write_bytes(content)
            downloaded += 1
            append_log(asset_log_path, {"stage": "downloaded", "url": entry.normalized_url, "path": relative_path, "archive_url": archive_url})
        except (HTTPError, URLError, TimeoutError) as exc:
            failure = {"stage": "download_failed", "url": entry.normalized_url, "archive_url": archive_url, "error": str(exc)}
            failures.append(failure)
            append_log(asset_log_path, failure)

    rewrite_html_files(site_dir, link_map, args.domain)

    summary = {
        "offset": args.offset,
        "candidate_count": len(candidates),
        "resolved_count": len(resolved_entries),
        "downloaded_count": downloaded,
        "skipped_existing_count": skipped_existing,
        "failure_count": len(failures),
        "candidates_file": str(candidates_path),
        "log_file": str(asset_log_path),
    }
    (recovery_dir / "assets-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
