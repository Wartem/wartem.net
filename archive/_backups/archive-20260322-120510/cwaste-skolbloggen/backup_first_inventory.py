from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, build_opener


THIS_DIR = Path(__file__).resolve().parent
ARCHIVE_ROOT = THIS_DIR.parent
sys.path.insert(0, str(ARCHIVE_ROOT))
sys.path.insert(0, str(ARCHIVE_ROOT / "bufsimrishamn"))

from cdx_inventory import classify_url, normalize_url  # type: ignore
from raw_cache import cache_paths, read_cached_bytes, write_cached_response  # type: ignore


CONTENT_KINDS = {"homepage", "post_like", "category", "tag", "other"}
RETRYABLE = {429, 500, 502, 503, 504}
NOISE_PATH_RE = re.compile(
    r"(?i)(^|/)(wp-content|wp-includes|wp-admin|wp-login\.php|xmlrpc\.php|wp-json|favicon\.ico|robots\.txt|"
    r"global-adminbar\.php|adminbar\.css|dashicons(?:\.min)?\.css|css(?:/|\.php)|js/|comments/feed|a\.thickbox|div\.post)(/|$)"
)
NOISE_EXTENSIONS = {
    ".css",
    ".js",
    ".json",
    ".xml",
    ".ico",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".mp3",
    ".m4a",
    ".wav",
    ".ogg",
    ".mp4",
    ".mov",
    ".avi",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".rar",
    ".7z",
    ".swf",
}


@dataclass
class CandidateEntry:
    normalized_url: str
    kind: str
    best_statuscode: str
    best_mimetype: str
    best_timestamp: str
    best_original: str
    best_wayback_url: str
    fetch_url: str
    content_candidate: bool
    reason: str
    destination_hint: str
    redirect_candidate: bool
    downloaded: bool = False
    cache_hit: bool = False
    final_url: str = ""
    final_normalized_url: str = ""
    final_kind: str = ""
    final_destination_hint: str = ""
    error: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a backup-first raw HTML cache and content inventory for cwaste.skolbloggen.se.")
    parser.add_argument("--site-root", default=".")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--retry-backoff-seconds", type=float, default=2.0)
    parser.add_argument("--skip-download", action="store_true")
    return parser.parse_args()


def build_archive_raw_url(timestamp: str, original: str) -> str:
    return f"https://web.archive.org/web/{timestamp}id_/{original}"


def content_reason(normalized_url: str, kind: str, statuscode: str, mimetype: str) -> tuple[bool, str]:
    parts = urlsplit(normalized_url)
    path = parts.path or "/"
    suffix = PurePosixPath(path).suffix.lower()
    query = parts.query
    mime = (mimetype or "").lower()
    if kind not in CONTENT_KINDS:
        return False, f"kind:{kind}"
    if suffix in NOISE_EXTENSIONS:
        return False, f"extension:{suffix}"
    if NOISE_PATH_RE.search(path):
        return False, "noise-path"
    if "text/html" not in mime and "application/xhtml+xml" not in mime:
        return False, f"mime:{mime or 'unknown'}"
    if query:
        parsed_qs = parse_qs(query, keep_blank_values=True)
        if set(parsed_qs).issubset({"p"}):
            return True, "query-post-id"
        return False, f"query:{query}"
    if path.endswith("/feed/") or path.endswith("/comments/feed/"):
        return False, "feed"
    if statuscode in {"301", "302"}:
        return True, f"redirect:{statuscode}"
    return True, "html-content"


def destination_hint_from_url(normalized_url: str) -> str:
    parts = urlsplit(normalized_url)
    path = parts.path or "/"
    if path == "/":
        return "index.html"
    base = PurePosixPath(path.lstrip("/"))
    if path.endswith("/"):
        return str(base / "index.html")
    if base.suffix:
        return str(base.with_name(base.stem + ".html"))
    return str(base / "index.html")


def load_candidates(site_root: Path) -> list[CandidateEntry]:
    inventory_path = site_root / "out" / "urls_unique.csv"
    with inventory_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        entries: list[CandidateEntry] = []
        for row in reader:
            normalized_url = row["normalized_url"]
            best_statuscode = row["best_statuscode"]
            best_timestamp = row["best_timestamp"]
            best_original = row["best_original"]
            best_wayback_url = row["best_wayback_url"]
            best_mimetype = row["best_mimetype"]
            kind = row["kind"] or classify_url(normalized_url, best_mimetype)
            keep, reason = content_reason(normalized_url, kind, best_statuscode, best_mimetype)
            fetch_url = build_archive_raw_url(best_timestamp, best_original) if best_statuscode == "200" else best_wayback_url
            entries.append(
                CandidateEntry(
                    normalized_url=normalized_url,
                    kind=kind,
                    best_statuscode=best_statuscode,
                    best_mimetype=best_mimetype,
                    best_timestamp=best_timestamp,
                    best_original=best_original,
                    best_wayback_url=best_wayback_url,
                    fetch_url=fetch_url,
                    content_candidate=keep,
                    reason=reason,
                    destination_hint=destination_hint_from_url(normalized_url),
                    redirect_candidate=best_statuscode in {"301", "302"},
                )
            )
    return entries


def fetch_with_cache(site_root: Path, entry: CandidateEntry, *, max_retries: int, retry_backoff_seconds: float) -> CandidateEntry:
    cached = read_cached_bytes(site_root, entry.fetch_url)
    if cached is not None:
        hydrate_from_cache(site_root, entry)
        return entry

    opener = build_opener()
    request = Request(entry.fetch_url, headers={"User-Agent": "cwaste-backup-first/1.0", "Accept-Encoding": "identity"})
    attempt = 0
    while True:
        try:
            with opener.open(request, timeout=30) as response:
                body = response.read()
                final_url = response.geturl()
                content_type = response.headers.get_content_type() if response.headers else ""
            write_cached_response(
                site_root,
                entry.fetch_url,
                body,
                source="backup_first_inventory.py",
                extra={
                    "requested_url": entry.fetch_url,
                    "final_url": final_url,
                    "normalized_url": entry.normalized_url,
                    "best_wayback_url": entry.best_wayback_url,
                    "best_statuscode": entry.best_statuscode,
                    "content_type": content_type,
                },
            )
            entry.downloaded = True
            entry.final_url = final_url
            entry.final_normalized_url = normalize_url(extract_original_url(final_url) or entry.normalized_url)
            entry.final_kind = classify_url(entry.final_normalized_url, content_type or entry.best_mimetype)
            entry.final_destination_hint = destination_hint_from_url(entry.final_normalized_url)
            return entry
        except HTTPError as exc:
            if exc.code not in RETRYABLE or attempt >= max_retries:
                entry.error = f"HTTP {exc.code}"
                return entry
        except URLError as exc:
            if attempt >= max_retries:
                entry.error = str(exc)
                return entry
        attempt += 1
        time.sleep(retry_backoff_seconds * attempt)


def extract_original_url(url: str) -> str:
    match = re.match(r"^https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://.+)$", url, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return url


def hydrate_from_cache(site_root: Path, entry: CandidateEntry) -> CandidateEntry:
    cached = read_cached_bytes(site_root, entry.fetch_url)
    if cached is None:
        return entry
    _body_path, meta_path = cache_paths(site_root, entry.fetch_url)
    final_url = entry.fetch_url
    if meta_path.exists():
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            if isinstance(payload.get("final_url"), str) and payload["final_url"]:
                final_url = payload["final_url"]
        except (OSError, json.JSONDecodeError):
            pass
    entry.downloaded = True
    entry.cache_hit = True
    entry.final_url = final_url
    entry.final_normalized_url = normalize_url(extract_original_url(final_url) or entry.normalized_url)
    entry.final_kind = classify_url(entry.final_normalized_url, entry.best_mimetype)
    entry.final_destination_hint = destination_hint_from_url(entry.final_normalized_url)
    return entry


def write_inventory(site_root: Path, entries: list[CandidateEntry]) -> None:
    output_dir = site_root / "backup-first"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "inventory.json"
    csv_path = output_dir / "inventory.csv"
    summary_path = output_dir / "summary.json"

    payload = [asdict(entry) for entry in entries]
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = list(CandidateEntry.__dataclass_fields__.keys())
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for item in payload:
            writer.writerow(item)

    content_entries = [entry for entry in entries if entry.content_candidate]
    downloaded_entries = [entry for entry in content_entries if entry.downloaded]
    redirect_entries = [entry for entry in content_entries if entry.redirect_candidate]
    summary = {
        "total_entries": len(entries),
        "content_candidates": len(content_entries),
        "redirect_candidates": len(redirect_entries),
        "downloaded": len(downloaded_entries),
        "cache_hits": sum(1 for entry in downloaded_entries if entry.cache_hit),
        "errors": sum(1 for entry in content_entries if entry.error),
        "kinds": {
            kind: sum(1 for entry in content_entries if entry.kind == kind)
            for kind in sorted({entry.kind for entry in content_entries})
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    site_root = Path(args.site_root).resolve()
    entries = load_candidates(site_root)
    if args.limit > 0:
        content_entries = [entry for entry in entries if entry.content_candidate][: args.limit]
        keep_urls = {entry.normalized_url for entry in content_entries}
        entries = [entry for entry in entries if not entry.content_candidate or entry.normalized_url in keep_urls]
    if not args.skip_download:
        for entry in entries:
            if not entry.content_candidate:
                continue
            fetch_with_cache(
                site_root,
                entry,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
            )
    else:
        for entry in entries:
            if entry.content_candidate:
                hydrate_from_cache(site_root, entry)
    write_inventory(site_root, entries)
    content_count = sum(1 for entry in entries if entry.content_candidate)
    downloaded_count = sum(1 for entry in entries if entry.content_candidate and entry.downloaded)
    print(
        json.dumps(
            {
                "total_entries": len(entries),
                "content_candidates": content_count,
                "downloaded": downloaded_count,
                "inventory_json": str((site_root / "backup-first" / "inventory.json").resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
