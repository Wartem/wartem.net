from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from raw_cache import read_cached_bytes, write_cached_response  # type: ignore

INVENTORY_PATH = ROOT / "out" / "urls_unique.csv"
BROKEN_LIST_PATH = ROOT / "site" / "recovery" / "broken-posts.txt"
SITE_DIR = ROOT / "site"
REPORT_PATH = SITE_DIR / "recovery" / "repair-broken-posts-summary.json"
RETRYABLE = {429, 500, 502, 503, 504}
MARKER = "Den fullständiga artikelsidan kunde inte återfinnas som egen capture i Wayback Machine."


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


def load_inventory() -> dict[str, dict[str, str]]:
    with INVENTORY_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        entry_relative_path(row["normalized_url"], row["kind"]): row
        for row in rows
        if row.get("normalized_url") and row.get("kind")
    }


def load_targets() -> list[str]:
    return [
        line.strip()
        for line in BROKEN_LIST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def is_broken_target(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8", errors="replace")
    return MARKER in text


class Downloader:
    def __init__(self, max_retries: int = 4, retry_backoff_seconds: float = 2.0) -> None:
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.opener = build_opener()

    def fetch(self, url: str) -> bytes:
        cached = read_cached_bytes(ROOT, url)
        if cached is not None:
            return cached
        request = Request(url, headers={"User-Agent": "cwasteson-repair-broken-posts/1.0", "Accept-Encoding": "identity"})
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                with self.opener.open(request, timeout=60) as response:
                    body = response.read()
                    write_cached_response(ROOT, url, body, source="repair_broken_posts.py")
                    return body
            except HTTPError as exc:
                last_error = exc
                if exc.code not in RETRYABLE or attempt == self.max_retries - 1:
                    raise
            except URLError as exc:
                last_error = exc
                if attempt == self.max_retries - 1:
                    raise
            time.sleep(self.retry_backoff_seconds * (attempt + 1))
        if last_error:
            raise last_error
        raise RuntimeError(f"Unable to fetch {url}")


def main() -> int:
    inventory = load_inventory()
    targets = load_targets()
    downloader = Downloader()
    results: dict[str, object] = {
        "target_count": len(targets),
        "downloaded_count": 0,
        "failed_count": 0,
        "downloaded": [],
        "failed": [],
    }

    for relative_path in targets:
        target_path = SITE_DIR / relative_path
        if not is_broken_target(target_path):
            continue
        row = inventory.get(relative_path)
        if not row:
            results["failed"].append({"path": relative_path, "error": "not-found-in-inventory"})
            continue
        archive_url = row.get("best_wayback_url")
        if not archive_url:
            results["failed"].append({"path": relative_path, "error": "missing-archive-url"})
            continue
        try:
            data = downloader.fetch(archive_url)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(data)
            results["downloaded"].append({"path": relative_path, "archive_url": archive_url})
        except Exception as exc:  # noqa: BLE001
            results["failed"].append({"path": relative_path, "archive_url": archive_url, "error": str(exc)})

    results["downloaded_count"] = len(results["downloaded"])
    results["failed_count"] = len(results["failed"])
    REPORT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if not results["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
