from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
SITE_DIR = THIS_DIR / "site"
ARCHIVE_ROOT = THIS_DIR.parent
sys.path.insert(0, str(ARCHIVE_ROOT / "bufsimrishamn"))
sys.path.insert(0, str(ARCHIVE_ROOT))

from enhance_site import (  # type: ignore
    build_context_box,
    build_page_meta,
    build_post_records,
    build_topbar,
    inject_theme,
    load_collection_nav,
    relpath_to_theme,
)
from raw_cache import fetch_url_bytes  # type: ignore


def load_archive_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    csv_path = THIS_DIR / "out" / "urls_unique.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 10:
                continue
            original = row[0]
            kind = row[1]
            archive_url = row[9]
            if kind != "post_like":
                continue
            if "cwasteson.skolbloggen.se/" not in original:
                continue
            path = original.split("cwasteson.skolbloggen.se/", 1)[1].strip("/")
            if not path:
                continue
            mapping[f"{path}/index.html"] = archive_url
    return mapping


def fetch_html(url: str) -> str:
    raw = fetch_url_bytes(
        THIS_DIR,
        url,
        source="restore_direct_capture.py",
        user_agent="Mozilla/5.0",
        timeout=30,
    )
    return raw.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("relative_path")
    args = parser.parse_args()

    archive_map = load_archive_map()
    relative_path = args.relative_path.replace("\\", "/")
    archive_url = archive_map.get(relative_path)
    if not archive_url:
        raise SystemExit(f"No archive URL found for {relative_path}")

    raw_html = fetch_html(archive_url)

    pages = build_page_meta(SITE_DIR)
    pages_by_path = {page.path: page for page in pages}
    meta = pages_by_path.get(relative_path)
    if meta is None:
        raise SystemExit(f"No page metadata found for {relative_path}")
    post_records = build_post_records(SITE_DIR, pages)
    collection_items = load_collection_nav(SITE_DIR, "../archive-data/collections.json", "charlotta-wasteson")

    html_path = SITE_DIR / Path(relative_path)
    updated = inject_theme(
        raw_html,
        relpath_to_theme(html_path, SITE_DIR),
        build_topbar(relative_path, "cwasteson.skolbloggen.se", collection_items),
        build_context_box(meta, relative_path),
        meta,
        pages_by_path,
        post_records,
        "cwasteson.skolbloggen.se",
        "none",
    )
    html_path.write_text(updated, encoding="utf-8")
    print(f"restored {relative_path} from {archive_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
