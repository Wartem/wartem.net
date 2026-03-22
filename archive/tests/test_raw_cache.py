from __future__ import annotations

import shutil
import unittest
from pathlib import Path

from raw_cache import fetch_url_bytes, read_cached_bytes, write_cached_response


class RawCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.site_root = Path("M:/projects/wartem.net/archive/tmp-raw-cache-tests")
        if self.site_root.exists():
            shutil.rmtree(self.site_root)
        self.site_root.mkdir(parents=True)

    def tearDown(self) -> None:
        if self.site_root.exists():
            shutil.rmtree(self.site_root)

    def test_fetch_url_bytes_returns_existing_cache_without_network(self):
        url = "https://example.invalid/test"
        write_cached_response(self.site_root, url, b"cached-body", source="test")
        data = fetch_url_bytes(
            self.site_root,
            url,
            source="test",
            user_agent="raw-cache-test/1.0",
            max_retries=0,
        )
        self.assertEqual(data, b"cached-body")
        cached = read_cached_bytes(self.site_root, url)
        self.assertEqual(cached, b"cached-body")


if __name__ == "__main__":
    unittest.main()
