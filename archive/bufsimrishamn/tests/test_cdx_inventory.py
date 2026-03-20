from __future__ import annotations

import csv
import json
import shutil
import unittest
from pathlib import Path
from urllib.error import HTTPError

import cdx_inventory


class FakeClient:
    def __init__(self, payloads):
        self.payloads = payloads

    def fetch_query(self, query_id, params, *, page_size, sleep_seconds, paged=True):
        return self.payloads[query_id]


class ParseCdxJsonTests(unittest.TestCase):
    def test_parses_rows_and_resume_key(self):
        payload = json.dumps(
            [
                ["timestamp", "original", "statuscode", "mimetype"],
                ["20200101000000", "https://example.com/", "200", "text/html"],
                [],
                ["resume-token"],
            ]
        )

        rows, resume_key = cdx_inventory.parse_cdx_json(payload)

        self.assertEqual(
            rows,
            [
                {
                    "timestamp": "20200101000000",
                    "original": "https://example.com/",
                    "statuscode": "200",
                    "mimetype": "text/html",
                }
            ],
        )
        self.assertEqual(resume_key, "resume-token")

    def test_single_column_rows_are_not_mistaken_for_resume_keys(self):
        payload = json.dumps(
            [
                ["original"],
                ["https://example.com/"],
                ["https://example.com/post/"],
            ]
        )

        rows, resume_key = cdx_inventory.parse_cdx_json(payload)

        self.assertEqual(
            rows,
            [
                {"original": "https://example.com/"},
                {"original": "https://example.com/post/"},
            ],
        )
        self.assertIsNone(resume_key)


class CdxClientPaginationTests(unittest.TestCase):
    def test_fetch_query_uses_resume_key_until_exhausted(self):
        class StubClient(cdx_inventory.CdxClient):
            def __init__(self):
                super().__init__(endpoint="https://example.test/cdx")
                self.calls = []

            def _request(self, params):
                self.calls.append(params)
                if "resumeKey" not in params:
                    return json.dumps(
                        [
                            ["timestamp", "original", "statuscode", "mimetype"],
                            ["20200101000000", "https://example.com/", "200", "text/html"],
                            [],
                            ["page-2"],
                        ]
                    ).encode("utf-8")
                return json.dumps(
                    [
                        ["timestamp", "original", "statuscode", "mimetype"],
                        ["20200102000000", "https://example.com/post/", "200", "text/html"],
                    ]
                ).encode("utf-8")

        client = StubClient()

        rows = client.fetch_query(
            "raw",
            {"url": "example.com/*", "fl": "timestamp,original,statuscode,mimetype"},
            page_size=2,
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(client.calls[0]["showResumeKey"], "true")
        self.assertEqual(client.calls[1]["resumeKey"], "page-2")

    def test_request_retries_retryable_http_errors(self):
        class RetryClient(cdx_inventory.CdxClient):
            def __init__(self):
                super().__init__(
                    endpoint="https://example.test/cdx",
                    max_retries=2,
                    retry_backoff_seconds=0.0,
                )
                self.attempts = 0

            @property
            def opener(self):
                return self

            @opener.setter
            def opener(self, value):
                pass

            def open(self, request):
                self.attempts += 1
                if self.attempts < 3:
                    raise HTTPError(request.full_url, 504, "Gateway Timeout", {}, None)
                return self

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'[["timestamp","original","statuscode","mimetype"]]'

        client = RetryClient()

        payload = client._request({"url": "example.com/*"})

        self.assertEqual(client.attempts, 3)
        self.assertEqual(payload, b'[["timestamp","original","statuscode","mimetype"]]')


class NormalizationAndClassificationTests(unittest.TestCase):
    def test_normalize_url_lowercases_and_strips_fragment_and_default_port(self):
        normalized = cdx_inventory.normalize_url("HTTPS://Example.COM:443/category/news/#frag")
        self.assertEqual(normalized, "https://example.com/category/news/")

    def test_classifies_expected_wordpress_shapes(self):
        self.assertEqual(cdx_inventory.classify_url("https://example.com/"), "homepage")
        self.assertEqual(cdx_inventory.classify_url("https://example.com/2015/12/11/post-slug/"), "post_like")
        self.assertEqual(cdx_inventory.classify_url("https://example.com/category/news/"), "category")
        self.assertEqual(cdx_inventory.classify_url("https://example.com/tag/local/"), "tag")
        self.assertEqual(cdx_inventory.classify_url("https://example.com/feed/"), "feed")
        self.assertEqual(cdx_inventory.classify_url("https://example.com/page/2/"), "pagination")
        self.assertEqual(cdx_inventory.classify_url("https://example.com/wp-content/uploads/file.jpg"), "media")


class InventoryLogicTests(unittest.TestCase):
    def test_dedupes_same_capture_found_by_multiple_queries(self):
        records = [
            cdx_inventory.CaptureRecord("a", "20200101000000", "https://example.com/", "200", "text/html"),
            cdx_inventory.CaptureRecord("b", "20200101000000", "https://example.com/", "200", "text/html"),
            cdx_inventory.CaptureRecord("b", "20200102000000", "https://example.com/", "200", "text/html"),
        ]

        deduped = cdx_inventory.dedupe_captures(records)

        self.assertEqual(len(deduped), 2)

    def test_html_best_capture_prefers_latest_200_html(self):
        records = [
            cdx_inventory.CaptureRecord("raw", "20200101000000", "https://example.com/2015/01/01/post/", "200", "text/html"),
            cdx_inventory.CaptureRecord("raw", "20200102000000", "https://example.com/2015/01/01/post/", "404", "text/html"),
            cdx_inventory.CaptureRecord("raw", "20200103000000", "https://example.com/2015/01/01/post/", "200", "text/html"),
        ]

        unique = cdx_inventory.build_unique_records(records)

        self.assertEqual(unique[0].best_timestamp, "20200103000000")
        self.assertEqual(unique[0].best_original, "https://example.com/2015/01/01/post/")
        self.assertEqual(unique[0].kind, "post_like")

    def test_media_best_capture_prefers_latest_200_regardless_of_mimetype(self):
        records = [
            cdx_inventory.CaptureRecord("raw", "20200101000000", "https://example.com/file.pdf", "200", "application/pdf"),
            cdx_inventory.CaptureRecord("raw", "20200102000000", "https://example.com/file.pdf", "200", "warc/revisit"),
            cdx_inventory.CaptureRecord("raw", "20200103000000", "https://example.com/file.pdf", "404", "application/pdf"),
        ]

        unique = cdx_inventory.build_unique_records(records)

        self.assertEqual(unique[0].kind, "media")
        self.assertEqual(unique[0].best_timestamp, "20200102000000")

    def test_build_summary_reports_counts(self):
        query_results = {
            "raw": [{"timestamp": "1", "original": "https://example.com/", "statuscode": "200", "mimetype": "text/html"}],
            "unique": [{"original": "https://example.com/"}],
        }
        captures = [
            cdx_inventory.CaptureRecord("raw", "1", "https://example.com/", "200", "text/html"),
        ]
        unique = cdx_inventory.build_unique_records(captures)

        summary = cdx_inventory.build_summary(query_results, captures, unique)

        self.assertEqual(summary["capture_count"], 1)
        self.assertEqual(summary["unique_url_count"], 1)
        self.assertEqual(summary["kind_counts"]["homepage"], 1)


class QueryDefinitionTests(unittest.TestCase):
    def test_year_filters_are_applied(self):
        definitions = cdx_inventory.build_query_definitions("example.com", "all-public", 2014, 2018)

        raw_prefix = next(defn for defn in definitions if defn.query_id == "raw_prefix_root")
        html_200 = next(defn for defn in definitions if defn.query_id == "html_200_root")
        unique_domain = next(defn for defn in definitions if defn.query_id == "unique_domain")

        self.assertEqual(raw_prefix.params["from"], "2014")
        self.assertEqual(raw_prefix.params["to"], "2018")
        self.assertEqual(html_200.params["filter"], ["statuscode:200", "mimetype:text/html"])
        self.assertFalse(unique_domain.paged)

    def test_validate_args_accepts_retry_options(self):
        args = cdx_inventory.parse_args(["--output-dir", ".\\out", "--max-retries", "3", "--retry-backoff-seconds", "1.5"])
        cdx_inventory.validate_args(args)


class FileOutputTests(unittest.TestCase):
    def test_writes_expected_files(self):
        payloads = {
            "raw_prefix_root": [
                {"timestamp": "20200101000000", "original": "https://example.com/", "statuscode": "200", "mimetype": "text/html"}
            ],
            "raw_http_prefix": [
                {"timestamp": "20200101000000", "original": "https://example.com/", "statuscode": "200", "mimetype": "text/html"}
            ],
            "raw_https_prefix": [],
            "raw_www_prefix": [],
            "raw_domain_match": [],
            "wp_posts_prefix": [],
            "wp_category_prefix": [],
            "wp_tag_prefix": [],
            "wp_feed_prefix": [],
            "wp_page_prefix": [],
            "html_200_root": [
                {"timestamp": "20200101000000", "original": "https://example.com/", "statuscode": "200", "mimetype": "text/html"}
            ],
            "unique_domain": [{"original": "https://example.com/"}],
        }
        client = FakeClient(payloads)
        definitions = cdx_inventory.build_query_definitions("example.com", "all-public", None, None)
        output_dir = Path(__file__).resolve().parents[1] / ".test-output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir()
        try:
            query_results = cdx_inventory.fetch_all_queries(client, definitions, page_size=1000, sleep_seconds=0.0)
            captures = cdx_inventory.collect_capture_records(query_results)
            unique = cdx_inventory.build_unique_records(captures)
            summary = cdx_inventory.build_summary(query_results, captures, unique)
            cdx_inventory.write_captures_csv(output_dir / "captures_raw.csv", captures)
            cdx_inventory.write_unique_csv(output_dir / "urls_unique.csv", unique)
            cdx_inventory.write_summary_json(output_dir / "summary.json", summary)

            self.assertTrue((output_dir / "captures_raw.csv").exists())
            self.assertTrue((output_dir / "urls_unique.csv").exists())
            self.assertTrue((output_dir / "summary.json").exists())

            with (output_dir / "captures_raw.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["wayback_url"], "https://web.archive.org/web/20200101000000/https://example.com/")

            with (output_dir / "urls_unique.csv").open(encoding="utf-8", newline="") as handle:
                unique_rows = list(csv.DictReader(handle))
            self.assertEqual(unique_rows[0]["best_original"], "https://example.com/")

            with (output_dir / "summary.json").open(encoding="utf-8") as handle:
                saved_summary = json.load(handle)
            self.assertEqual(saved_summary["unique_url_count"], 1)
        finally:
            shutil.rmtree(output_dir)


if __name__ == "__main__":
    unittest.main()
