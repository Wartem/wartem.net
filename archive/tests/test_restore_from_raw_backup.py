from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cwaste-skolbloggen"))

import restore_from_raw_backup  # type: ignore


class RestoreFromRawBackupTests(unittest.TestCase):
    def test_choose_entries_prefers_latest_timestamp_for_same_path(self):
        entries = [
            {
                "content_candidate": True,
                "downloaded": True,
                "best_timestamp": "20180321020140",
                "destination_hint": "index.html",
                "fetch_url": "a",
            },
            {
                "content_candidate": True,
                "downloaded": True,
                "best_timestamp": "20190822221227",
                "destination_hint": "index.html",
                "fetch_url": "b",
            },
        ]
        chosen = restore_from_raw_backup.choose_entries(entries)
        self.assertEqual(len(chosen), 1)
        self.assertEqual(chosen[0]["fetch_url"], "b")

    def test_choose_entries_uses_final_destination_hint_when_present(self):
        entries = [
            {
                "content_candidate": True,
                "downloaded": True,
                "best_timestamp": "20180329122410",
                "destination_hint": "studieteknik/uppgift/index.html",
                "final_destination_hint": "studieteknik/uppgift/index.html",
                "fetch_url": "x",
            }
        ]
        chosen = restore_from_raw_backup.choose_entries(entries)
        self.assertEqual(chosen[0]["fetch_url"], "x")


if __name__ == "__main__":
    unittest.main()
