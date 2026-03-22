from __future__ import annotations

import argparse
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener


RETRYABLE = {429, 500, 502, 503, 504}
HTML_MIME_PREFIXES = ("text/html", "application/xhtml+xml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore post pages from Wayback inventory for a recovered site.")
    parser.add_argument("--site-root", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-bytes", type=int, default=12000)
    return parser.parse_args()


def decode_html(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def build_archive_raw_url(timestamp: str, original: str) -> str:
    return f"https://web.archive.org/web/{timestamp}id_/{original}"


def entry_relative_path(normalized_url: str) -> str:
    path = urlsplit(normalized_url).path or "/"
    base = PurePosixPath(path.lstrip("/"))
    if path.endswith("/"):
        return str(base / "index.html")
    if base.suffix:
        return str(base.with_name(base.stem + ".html"))
    return str(base / "index.html")


def load_candidates(site_root: Path, max_bytes: int) -> list[dict[str, str]]:
    inventory_path = site_root / "out" / "urls_unique.csv"
    site_dir = site_root / "site"
    with inventory_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    candidates: list[dict[str, str]] = []
    for row in rows:
        if row.get("kind") != "post_like":
            continue
        if row.get("best_statuscode") != "200":
            continue
        mime = (row.get("best_mimetype") or "").lower()
        if mime and not mime.startswith(HTML_MIME_PREFIXES):
            continue
        relative = entry_relative_path(row["normalized_url"])
        destination = site_dir / relative
        if destination.exists() and destination.stat().st_size > max_bytes:
            continue
        row["relative_path"] = relative
        candidates.append(row)
    return candidates


def fetch_and_write(site_root: Path, row: dict[str, str], max_retries: int = 4) -> tuple[str, bool, str]:
    site_dir = site_root / "site"
    destination = site_dir / row["relative_path"]
    archive_url = build_archive_raw_url(row["best_timestamp"], row["best_original"])
    opener = build_opener()
    request = Request(archive_url, headers={"User-Agent": "targeted-post-restore/1.0", "Accept-Encoding": "identity"})
    attempt = 0
    while True:
        try:
            with opener.open(request) as response:
                data = response.read()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(decode_html(data), encoding="utf-8")
            return row["relative_path"], True, ""
        except HTTPError as exc:
            if exc.code not in RETRYABLE or attempt >= max_retries:
                return row["relative_path"], False, str(exc)
        except URLError as exc:
            if attempt >= max_retries:
                return row["relative_path"], False, str(exc)
        attempt += 1
        time.sleep(attempt * 2)


def main() -> int:
    args = parse_args()
    site_root = Path(args.site_root).resolve()
    candidates = load_candidates(site_root, args.max_bytes)
    if not candidates:
        print("No small post files needed restoration.")
        return 0
    restored = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(fetch_and_write, site_root, row) for row in candidates]
        for future in as_completed(futures):
            relative_path, ok, error = future.result()
            if ok:
                restored += 1
            else:
                failed += 1
                print(f"FAILED {relative_path}: {error}")
    print(f"Restored {restored} post files; failed {failed}.")
    return 0 if restored or not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
