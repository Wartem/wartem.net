from __future__ import annotations

import json
import sys
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
ARCHIVE_ROOT = THIS_DIR.parent
sys.path.insert(0, str(ARCHIVE_ROOT))
sys.path.insert(0, str(ARCHIVE_ROOT / "bufsimrishamn"))

from raw_cache import cache_paths  # type: ignore
import enhance_site  # type: ignore


SITE_DIR = THIS_DIR / "site"
INVENTORY_PATH = THIS_DIR / "backup-first" / "inventory.json"
REPORT_PATH = SITE_DIR / "recovery" / "raw-backup-restore-manifest.json"


def decode_html(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def load_inventory() -> list[dict[str, object]]:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def choose_entries(entries: list[dict[str, object]]) -> list[dict[str, object]]:
    chosen: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not entry.get("content_candidate") or not entry.get("downloaded"):
            continue
        path = str(entry.get("final_destination_hint") or entry.get("destination_hint") or "")
        if not path:
            continue
        current = chosen.get(path)
        if current is None:
            chosen[path] = entry
            continue
        current_ts = str(current.get("best_timestamp") or "")
        new_ts = str(entry.get("best_timestamp") or "")
        if new_ts >= current_ts:
            chosen[path] = entry
    return [chosen[path] for path in sorted(chosen)]


def restore_raw_entries(entries: list[dict[str, object]]) -> dict[str, object]:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    restored: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []
    for entry in entries:
        fetch_url = str(entry["fetch_url"])
        destination_hint = str(entry.get("final_destination_hint") or entry.get("destination_hint") or "")
        cache_body_path, _cache_meta_path = cache_paths(THIS_DIR, fetch_url)
        if not cache_body_path.exists():
            failed.append({"fetch_url": fetch_url, "path": destination_hint, "error": "missing raw cache"})
            continue
        destination = SITE_DIR / destination_hint
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(decode_html(cache_body_path.read_bytes()), encoding="utf-8")
        restored.append(
            {
                "path": destination_hint,
                "fetch_url": fetch_url,
                "final_url": str(entry.get("final_url") or ""),
                "normalized_url": str(entry.get("final_normalized_url") or entry.get("normalized_url") or ""),
            }
        )
    payload = {
        "mode": "raw-backup-restore",
        "restored_count": len(restored),
        "failed_count": len(failed),
        "restored": restored,
        "failed": failed,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def rebuild_site() -> int:
    return enhance_site.run(
        [
            "--site-dir",
            str(SITE_DIR),
            "--site-title",
            "Fröken Wastesons länksida",
            "--site-label",
            "cwaste.skolbloggen.se",
            "--site-intro",
            "Detta är en lokal, återställd version av Fröken Wastesons länksida. Sajten är återuppbyggd från lokalt sparad råbackup från Wayback Machine.",
            "--collection-file",
            str((ARCHIVE_ROOT / "archive-data" / "collections.json").resolve()),
            "--collection-slug",
            "charlotta-wasteson",
            "--cleanup-level",
            "none",
        ]
    )


def main() -> int:
    entries = choose_entries(load_inventory())
    payload = restore_raw_entries(entries)
    rebuild_site()
    print(json.dumps({"selected_entries": len(entries), "restored_count": payload["restored_count"], "failed_count": payload["failed_count"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
