from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from raw_cache import fetch_url_bytes  # type: ignore
INVENTORY_PATH = ROOT / "out" / "urls_unique.csv"
SITE_DIR = ROOT / "site"
RECOVERY_DIR = SITE_DIR / "recovery"
RETRYABLE = {429, 500, 502, 503, 504}
HTML_MIME_PREFIXES = ("text/html", "application/xhtml+xml")
MONTH_ARCHIVE_RE = re.compile(r"^/\d{4}/\d{2}/$")
NOISE_PREFIXES = (
    "/feed",
    "/comments/feed",
    "/search/",
    "/wp-",
    "/xmlrpc",
)
NOISE_EXACT = {
    "/robots.txt",
    "/favicon.ico",
    "/a.thickbox",
    "/div.post",
}


def decode_html(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def build_archive_raw_url(timestamp: str, original: str) -> str:
    return f"https://web.archive.org/web/{timestamp}id_/{original}"


def entry_relative_path(normalized_url: str, kind: str) -> str:
    parts = urlsplit(normalized_url)
    path = parts.path or "/"
    if kind == "homepage" or path == "/":
        return "index.html"
    base = PurePosixPath(path.lstrip("/"))
    if path.endswith("/"):
        return str(base / "index.html")
    suffix = base.suffix
    if suffix:
        return str(base.with_name(base.stem + ".html"))
    return str(base / "index.html")


def is_noise_path(path: str) -> bool:
    if path in NOISE_EXACT:
        return True
    return any(path.startswith(prefix) for prefix in NOISE_PREFIXES)


def should_include(row: dict[str, str]) -> bool:
    if row.get("best_statuscode") != "200":
        return False
    mime = (row.get("best_mimetype") or "").lower()
    if mime and not mime.startswith(HTML_MIME_PREFIXES):
        return False
    path = urlsplit(row["normalized_url"]).path or "/"
    if is_noise_path(path):
        return False
    kind = row["kind"]
    if kind in {"homepage", "post_like", "category", "pagination"}:
        return True
    if kind == "other":
        return True
    if MONTH_ARCHIVE_RE.match(path):
        return True
    return False


def load_rows() -> list[dict[str, str]]:
    with INVENTORY_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows = [row for row in rows if should_include(row)]
    rows.sort(key=lambda row: (row["kind"] != "homepage", row["normalized_url"]))
    return rows


class Downloader:
    def __init__(self, max_retries: int = 4, retry_backoff_seconds: float = 2.0) -> None:
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def fetch(self, url: str) -> bytes:
        return fetch_url_bytes(
            ROOT,
            url,
            source="cwastes/restore_html_subset.py",
            user_agent="cwastes-html-subset/1.0",
            max_retries=self.max_retries,
            retry_backoff_seconds=self.retry_backoff_seconds,
            retryable_statuses=RETRYABLE,
        )


def write_manifest(downloaded: list[dict[str, str]], failed: list[dict[str, str]]) -> None:
    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "mode": "html-subset",
        "downloaded_count": len(downloaded),
        "failed_count": len(failed),
        "downloaded": downloaded,
        "failed": failed,
    }
    (RECOVERY_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    rows = load_rows()
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    downloader = Downloader()
    downloaded: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []

    for row in rows:
        archive_url = build_archive_raw_url(row["best_timestamp"], row["best_original"])
        relative_path = entry_relative_path(row["normalized_url"], row["kind"])
        destination = SITE_DIR / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = downloader.fetch(archive_url)
            destination.write_text(decode_html(data), encoding="utf-8")
            downloaded.append(
                {
                    "url": row["normalized_url"],
                    "kind": row["kind"],
                    "path": relative_path,
                    "archive_url": archive_url,
                }
            )
        except (HTTPError, URLError, TimeoutError) as exc:
            failed.append({"url": row["normalized_url"], "archive_url": archive_url, "error": str(exc)})

    write_manifest(downloaded, failed)
    print(f"Downloaded {len(downloaded)} HTML pages, failed {len(failed)}.", file=sys.stderr)
    return 0 if downloaded else 1


if __name__ == "__main__":
    raise SystemExit(main())
