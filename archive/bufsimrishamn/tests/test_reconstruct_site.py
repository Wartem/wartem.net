from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

import reconstruct_site


class EntryPathTests(unittest.TestCase):
    def test_entry_relative_path_for_homepage_and_post(self):
        homepage = reconstruct_site.SiteEntry(
            normalized_url="https://example.com/",
            kind="homepage",
            first_timestamp="1",
            last_timestamp="2",
            capture_count=2,
            best_timestamp="2",
            best_original="https://example.com/",
            best_statuscode="200",
            best_mimetype="text/html",
            best_wayback_url="https://web.archive.org/web/2/https://example.com/",
        )
        post = reconstruct_site.SiteEntry(
            normalized_url="https://example.com/2015/12/11/post/",
            kind="post_like",
            first_timestamp="1",
            last_timestamp="2",
            capture_count=2,
            best_timestamp="2",
            best_original="https://example.com/2015/12/11/post/",
            best_statuscode="200",
            best_mimetype="text/html",
            best_wayback_url="https://web.archive.org/web/2/https://example.com/2015/12/11/post/",
        )

        self.assertEqual(reconstruct_site.entry_relative_path(homepage), "index.html")
        self.assertEqual(reconstruct_site.entry_relative_path(post), "2015/12/11/post/index.html")

    def test_noise_entry_filters_share_urls_and_admin_paths(self):
        share = reconstruct_site.SiteEntry(
            normalized_url="https://example.com/post/?share=facebook",
            kind="other",
            first_timestamp="1",
            last_timestamp="2",
            capture_count=2,
            best_timestamp="2",
            best_original="https://example.com/post/?share=facebook",
            best_statuscode="200",
            best_mimetype="text/html",
            best_wayback_url="x",
        )
        admin = reconstruct_site.SiteEntry(
            normalized_url="https://example.com/wp-login.php",
            kind="other",
            first_timestamp="1",
            last_timestamp="2",
            capture_count=2,
            best_timestamp="2",
            best_original="https://example.com/wp-login.php",
            best_statuscode="200",
            best_mimetype="text/html",
            best_wayback_url="x",
        )

        self.assertTrue(reconstruct_site.is_noise_entry(share))
        self.assertTrue(reconstruct_site.is_noise_entry(admin))


class HtmlRewriteTests(unittest.TestCase):
    def test_rewrites_internal_links_and_images_to_local_paths(self):
        link_map = {
            "https://example.com/": "index.html",
            "https://example.com/2015/12/11/post/": "2015/12/11/post/index.html",
            "https://example.com/wp-content/uploads/img.jpg": "wp-content/uploads/img.jpg",
        }
        html = """
        <html><body>
        <a href="https://example.com/">Hem</a>
        <a href="/2015/12/11/post/">Post</a>
        <img src="/wp-content/uploads/img.jpg" />
        </body></html>
        """

        rewritten = reconstruct_site.rewrite_html(
            html,
            "https://example.com/2015/12/11/post/",
            "2015/12/11/post/index.html",
            link_map,
        )

        self.assertIn('href="../../../../index.html"', rewritten)
        self.assertIn('href="index.html"', rewritten)
        self.assertIn('src="../../../../wp-content/uploads/img.jpg"', rewritten)

    def test_extract_asset_urls_finds_files_wordpress_images(self):
        html = """
        <html><body>
        <img src="http://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=352&amp;h=234" />
        <a href="http://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg">full</a>
        </body></html>
        """

        assets = reconstruct_site.extract_asset_urls(html, "https://bufsimrishamn.wordpress.com/", "bufsimrishamn.wordpress.com")

        self.assertIn("http://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=352&h=234", assets)
        self.assertIn("http://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg", assets)


class ManifestTests(unittest.TestCase):
    def test_write_recovery_index_outputs_manifest_and_html(self):
        site_dir = Path(__file__).resolve().parents[1] / ".site-test-output"
        if site_dir.exists():
            shutil.rmtree(site_dir)
        site_dir.mkdir()
        try:
            manifest = {"downloaded_count": 1, "skipped_count": 2, "failed_count": 3, "downloaded": [], "skipped": [], "failed": []}

            reconstruct_site.write_recovery_index(site_dir, manifest)

            saved = json.loads((site_dir / "recovery" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["failed_count"], 3)
            self.assertTrue((site_dir / "recovery" / "index.html").exists())
        finally:
            shutil.rmtree(site_dir)


if __name__ == "__main__":
    unittest.main()
