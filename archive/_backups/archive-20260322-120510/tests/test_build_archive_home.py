from __future__ import annotations

import shutil
import unittest
from pathlib import Path

import build_archive_home


class ArchiveHomeTests(unittest.TestCase):
    def test_load_metadata_has_expected_collections(self):
        metadata = build_archive_home.load_metadata()

        self.assertIn("collections", metadata)
        self.assertEqual(metadata["collections"][0]["slug"], "charlotta-wasteson")
        self.assertEqual(metadata["standalone_sites"][0]["slug"], "bufsimrishamn")

    def test_build_site_creates_index_and_placeholder_pages(self):
        root = Path(__file__).resolve().parents[1] / ".tmp-build-archive-home"
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        try:
            metadata = {
                "site": {
                    "title": "Testarkiv",
                    "tagline": "test",
                    "summary": "testsummary",
                    "status_scale": ["kandidat", "återställd"]
                },
                "about": ["Om testarkivet."],
                "standalone_sites": [],
                "collections": [
                    {
                        "slug": "demo",
                        "title": "Demo",
                        "summary": "Samling",
                        "status": "pågående kartläggning",
                        "intro": ["Inledning"],
                        "entries": [
                            {
                                "slug": "demo-site",
                                "title": "Demo Site",
                                "canonical_url": "http://example.com/",
                                "platform": "Skolbloggen",
                                "confidence": "sannolik",
                                "status": "kandidat",
                                "owner_relation": "Testrelation",
                                "summary_long": "Längre text",
                                "evidence": ["Bevis ett"],
                                "wayback_links": [
                                    {
                                        "label": "Wayback",
                                        "url": "https://web.archive.org/web/*/http://example.com/"
                                    }
                                ],
                                "local_path": "demo-site/site/index.html"
                            }
                        ]
                    }
                ]
            }

            output = root / "index.html"
            robots = root / "robots.txt"
            build_archive_home.build_site(metadata, root_dir=root, output_path=output, robots_path=robots)

            self.assertTrue(output.exists())
            self.assertTrue(robots.exists())
            self.assertTrue((root / "demo-site" / "site" / "index.html").exists())
            html = output.read_text(encoding="utf-8")
            self.assertIn("Demo", html)
            self.assertIn("Pågående återställningar", html)
            placeholder = (root / "demo-site" / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn("stabil lokal hållplats", placeholder)
        finally:
            if root.exists():
                shutil.rmtree(root)

    def test_render_root_html_shows_existing_local_sites_as_restored(self):
        metadata = {
            "site": {
                "title": "Testarkiv",
                "tagline": "test",
                "summary": "summary",
                "status_scale": ["extern referens", "återställd"]
            },
            "about": [],
            "standalone_sites": [],
            "collections": [
                {
                    "slug": "demo",
                    "title": "Demo",
                    "summary": "Samling",
                    "status": "pågående kartläggning",
                    "intro": [],
                    "entries": [
                        {
                            "slug": "local-site",
                            "title": "Local Site",
                            "canonical_url": "http://example.com/",
                            "platform": "Skolbloggen",
                            "confidence": "verifierad",
                            "status": "återställd",
                            "owner_relation": "Test",
                            "summary_long": "Har lokal sida",
                            "evidence": [],
                            "wayback_links": [],
                            "local_path": "bufsimrishamn/site/index.html"
                        }
                    ]
                }
            ]
        }

        html = build_archive_home.render_root_html(metadata)

        self.assertIn("Återställda sajter", html)
        self.assertIn("Local Site", html)

    def test_render_root_html_hides_empty_ongoing_section(self):
        metadata = {
            "site": {
                "title": "Testarkiv",
                "tagline": "test",
                "summary": "summary",
                "status_scale": ["extern referens", "delvis återställd"]
            },
            "about": [],
            "standalone_sites": [],
            "collections": [
                {
                    "slug": "demo",
                    "title": "Demo",
                    "summary": "Samling",
                    "status": "pågående kartläggning",
                    "intro": [],
                    "entries": [
                        {
                            "slug": "local-site",
                            "title": "Local Site",
                            "canonical_url": "http://example.com/",
                            "platform": "Skolbloggen",
                            "confidence": "verifierad",
                            "status": "delvis återställd",
                            "owner_relation": "Test",
                            "summary_long": "Har lokal sida",
                            "evidence": [],
                            "wayback_links": [],
                            "local_path": "bufsimrishamn/site/index.html"
                        }
                    ]
                }
            ]
        }

        html = build_archive_home.render_root_html(metadata)

        self.assertNotIn("Pågående återställningar", html)
        self.assertIn("Återställda sajter", html)


if __name__ == "__main__":
    unittest.main()
