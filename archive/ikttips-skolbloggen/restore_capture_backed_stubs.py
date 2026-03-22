from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


THIS_DIR = Path(__file__).resolve().parent
SITE_DIR = THIS_DIR / "site"
ARCHIVE_ROOT = THIS_DIR.parent
sys.path.insert(0, str(ARCHIVE_ROOT))
sys.path.insert(0, str(ARCHIVE_ROOT / "bufsimrishamn"))

from raw_cache import fetch_url_bytes  # type: ignore
from enhance_site import (  # type: ignore
    build_context_box,
    build_page_meta,
    build_post_records,
    build_topbar,
    inject_theme,
    load_collection_nav,
    relpath_to_theme,
    unwrap_wayback_url,
)


STUB_MARKERS = (
    "Rekonstruerad fr",
    "Wayback Machine",
)
HOSTS = {"ikttips.skolbloggen.se", "www.ikttips.skolbloggen.se"}


def load_archive_map() -> dict[str, str]:
    mapping: dict[str, tuple[int, str]] = {}
    csv_path = THIS_DIR / "out" / "urls_unique.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            original = (row.get("best_original") or "").strip()
            kind = (row.get("kind") or "").strip()
            archive_url = (row.get("best_wayback_url") or "").strip()
            raw_status = (row.get("best_statuscode") or "0").strip() or "0"
            statuscode = int(raw_status) if raw_status.isdigit() else 0
            if kind != "post_like" or not archive_url:
                continue
            parsed = urlsplit(original)
            hostname = (parsed.hostname or "").lower()
            if hostname not in HOSTS:
                continue
            path = parsed.path.strip("/")
            if not path:
                continue
            relative = f"{path}/index.html"
            current = mapping.get(relative)
            if current is None or (current[0] != 200 and statuscode == 200):
                mapping[relative] = (statuscode, archive_url)
    return {path: archive_url for path, (_status, archive_url) in mapping.items()}


def find_capture_backed_stubs(archive_map: dict[str, str]) -> list[str]:
    results: list[str] = []
    for html_path in SITE_DIR.rglob("index.html"):
        relative = html_path.relative_to(SITE_DIR).as_posix()
        if not re.match(r"^\d{4}/\d{2}/\d{2}/.+/index\.html$", relative):
            continue
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        if all(marker in text for marker in STUB_MARKERS) and relative in archive_map:
            results.append(relative)
    return sorted(results)


def fetch_html(url: str) -> str:
    raw = fetch_url_bytes(
        THIS_DIR,
        url,
        source="restore_capture_backed_stubs.py",
        user_agent="Mozilla/5.0",
        timeout=30,
    )
    return raw.decode("utf-8", errors="replace")


def sanitize_capture_html(html_text: str) -> str:
    cleaned = re.sub(
        r'<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->\s*',
        "",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(
        r'<link rel="stylesheet" type="text/css" href="https://web-static\.archive\.org/_static/css/banner-styles\.css[^"]*" */?>\s*',
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r'<link rel="stylesheet" type="text/css" href="https://web-static\.archive\.org/_static/css/iconochive\.css[^"]*" */?>\s*',
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r'<div id="wm-ipp-print">.*?</div>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(
        r'https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://[^"\'\s<>]+)',
        lambda match: unwrap_wayback_url(match.group(0)),
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned


def restore_path(relative_path: str, archive_url: str, pages_by_path, post_records, collection_items) -> None:
    html_path = SITE_DIR / Path(relative_path)
    raw_html = sanitize_capture_html(fetch_html(archive_url))
    meta = pages_by_path.get(relative_path)
    if meta is None:
        raise RuntimeError(f"Missing page metadata for {relative_path}")
    updated = inject_theme(
        raw_html,
        relpath_to_theme(html_path, SITE_DIR),
        build_topbar(relative_path, "ikttips.skolbloggen.se", collection_items),
        build_context_box(meta, relative_path),
        meta,
        pages_by_path,
        post_records,
        "ikttips.skolbloggen.se",
        "none",
    )
    html_path.write_text(updated, encoding="utf-8")


def main() -> int:
    archive_map = load_archive_map()
    targets = find_capture_backed_stubs(archive_map)
    pages = build_page_meta(SITE_DIR)
    pages_by_path = {page.path: page for page in pages}
    post_records = build_post_records(SITE_DIR, pages)
    collection_items = load_collection_nav(SITE_DIR, "../archive-data/collections.json", "charlotta-wasteson")

    restored: list[dict[str, str]] = []
    for relative_path in targets:
        archive_url = archive_map[relative_path]
        restore_path(relative_path, archive_url, pages_by_path, post_records, collection_items)
        restored.append({"path": relative_path, "archive_url": archive_url})

    report_path = SITE_DIR / "recovery" / "restore-capture-backed-stubs-summary.json"
    report_path.write_text(
        json.dumps({"restored_count": len(restored), "restored": restored}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"restored_count": len(restored), "restored": restored}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
