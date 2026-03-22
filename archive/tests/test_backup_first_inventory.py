from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cwaste-skolbloggen"))

import backup_first_inventory  # type: ignore


class BackupFirstInventoryTests(unittest.TestCase):
    def test_content_reason_keeps_post_id_redirects(self):
        keep, reason = backup_first_inventory.content_reason(
            "http://cwaste.skolbloggen.se/?p=609",
            "homepage",
            "301",
            "text/html",
        )
        self.assertTrue(keep)
        self.assertEqual(reason, "query-post-id")

    def test_content_reason_filters_noise_paths(self):
        keep, reason = backup_first_inventory.content_reason(
            "http://cwaste.skolbloggen.se/wp-content/themes/blix/style.css?1",
            "other",
            "200",
            "text/css",
        )
        self.assertFalse(keep)
        self.assertEqual(reason, "extension:.css")

    def test_content_reason_filters_wp_json_noise(self):
        keep, reason = backup_first_inventory.content_reason(
            "http://cwaste.skolbloggen.se/wp-json/",
            "other",
            "200",
            "text/html",
        )
        self.assertFalse(keep)
        self.assertEqual(reason, "noise-path")

    def test_destination_hint_from_root(self):
        self.assertEqual(
            backup_first_inventory.destination_hint_from_url("http://cwaste.skolbloggen.se/"),
            "index.html",
        )

    def test_destination_hint_from_nested_path(self):
        self.assertEqual(
            backup_first_inventory.destination_hint_from_url("http://cwaste.skolbloggen.se/svenska/referera/fler-exempel/"),
            "svenska/referera/fler-exempel/index.html",
        )

    def test_extract_original_url_from_wayback_wrapper(self):
        self.assertEqual(
            backup_first_inventory.extract_original_url(
                "https://web.archive.org/web/20180301022907/http://cwaste.skolbloggen.se/svenska/referera/ex-pa-kallhanvisning/"
            ),
            "http://cwaste.skolbloggen.se/svenska/referera/ex-pa-kallhanvisning/",
        )


if __name__ == "__main__":
    unittest.main()
