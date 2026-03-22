from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "cwasteson-skolbloggen"
sys.path.insert(0, str(MODULE_DIR))

import harvest_article_links


class HarvestArticleLinksTests(unittest.TestCase):
    def test_is_listing_seed_accepts_archives_and_rejects_tags(self):
        self.assertTrue(
            harvest_article_links.is_listing_seed(
                {"kind": "homepage", "normalized_url": "http://cwasteson.skolbloggen.se/"}
            )
        )
        self.assertTrue(
            harvest_article_links.is_listing_seed(
                {"kind": "other", "normalized_url": "http://cwasteson.skolbloggen.se/2010/06/"}
            )
        )
        self.assertFalse(
            harvest_article_links.is_listing_seed(
                {"kind": "tag", "normalized_url": "http://cwasteson.skolbloggen.se/tag/animoto/"}
            )
        )

    def test_is_meaningful_target_url_prefers_posts_and_excludes_noise(self):
        self.assertTrue(
            harvest_article_links.is_meaningful_target_url(
                "http://cwasteson.skolbloggen.se/2010/06/13/en-mindmap-over-google-dokument/",
                allow_listing_pages=False,
            )
        )
        self.assertTrue(
            harvest_article_links.is_meaningful_target_url(
                "http://cwasteson.skolbloggen.se/om/",
                allow_listing_pages=False,
            )
        )
        self.assertFalse(
            harvest_article_links.is_meaningful_target_url(
                "http://cwasteson.skolbloggen.se/tag/animoto/",
                allow_listing_pages=True,
            )
        )
        self.assertFalse(
            harvest_article_links.is_meaningful_target_url(
                "http://cwasteson.skolbloggen.se/comments/feed/",
                allow_listing_pages=True,
            )
        )

    def test_extract_internal_links_collects_same_host_targets(self):
        html_text = """
        <a href="/2010/06/13/en-mindmap-over-google-dokument/">Artikel</a>
        <a href="http://cwasteson.skolbloggen.se/om/">Om</a>
        <a href="http://example.com/external">Extern</a>
        <a href="#fragment">Lokalt ankare</a>
        """
        links = harvest_article_links.extract_internal_links(
            html_text,
            "http://cwasteson.skolbloggen.se/2010/06/",
            "cwasteson.skolbloggen.se",
        )
        self.assertEqual(
            links,
            {
                "http://cwasteson.skolbloggen.se/2010/06/13/en-mindmap-over-google-dokument/",
                "http://cwasteson.skolbloggen.se/om/",
            },
        )

    def test_extract_legacy_or_feed_snippet_block_supports_legacy_post_listing(self):
        html_text = """
        <div class="post">
            <h2 id="post-635"><a href="http://cwasteson.skolbloggen.se/2010/03/16/jag-ar-lite-avundsjuk/" rel="bookmark">Jag är lite avundsjuk</a></h2>
            <div class="entry">
                <p>Jag är lite avundsjuk på dem som är ungdomar i dag.</p>
                <p>Hur gör du för att återknyta kontakter?</p>
            </div>
            <p class="postmetadata"><a href="http://cwasteson.skolbloggen.se/2010/03/16/jag-ar-lite-avundsjuk/#respond">Leave A Comment</a></p>
        </div>
        """
        extracted = harvest_article_links.extract_legacy_or_feed_snippet_block(
            html_text,
            "http://cwasteson.skolbloggen.se/2010/03/16/jag-ar-lite-avundsjuk/",
        )
        self.assertIsNotNone(extracted)
        title, content_html = extracted
        self.assertEqual(title, "Jag är lite avundsjuk")
        self.assertIn("ungdomar i dag", content_html)

    def test_extract_legacy_or_feed_snippet_block_supports_feed_entry(self):
        html_text = """
        <entry>
            <link rel="alternate" type="text/html" href="http://cwasteson.skolbloggen.se/2010/06/19/karlek-och-hat/" />
            <title type="html"><![CDATA[Kärlek och hat]]></title>
            <content type="html" xml:base="http://cwasteson.skolbloggen.se/2010/06/19/karlek-och-hat/"><![CDATA[<p>Hat föder hat och kärlek föder kärlek.</p>]]></content>
        </entry>
        """
        extracted = harvest_article_links.extract_legacy_or_feed_snippet_block(
            html_text,
            "http://cwasteson.skolbloggen.se/2010/06/19/karlek-och-hat/",
        )
        self.assertIsNotNone(extracted)
        title, content_html = extracted
        self.assertEqual(title, "Kärlek och hat")
        self.assertIn("kärlek föder kärlek", content_html)

    def test_extract_position_based_post_snippet_supports_month_archive_markup(self):
        html_text = """
        <div class="post">
            <h2 id="post-1058"><a href="http://cwasteson.skolbloggen.se/2010/05/10/har-du-svart-for-att-bestamma-dig/" rel="bookmark">Har du svårt för att bestämma dig?</a></h2>
            <small>Posted in funderingar</small>
            <div class="entry">
                <p>Ibland kan jag ha svårt för att bestämma mig.</p>
                <p>Det är nog viktigt att inte låta beslutsångesten göra en helt handlingsförlamad.</p>
            </div>
            <p class="postmetadata"><a href="http://cwasteson.skolbloggen.se/2010/05/10/har-du-svart-for-att-bestamma-dig/#respond">Leave A Comment</a></p>
        </div>
        """
        extracted = harvest_article_links.extract_position_based_post_snippet(
            html_text,
            "http://cwasteson.skolbloggen.se/2010/05/10/har-du-svart-for-att-bestamma-dig/",
        )
        self.assertIsNotNone(extracted)
        title, content_html = extracted
        self.assertEqual(title, "Har du svårt för att bestämma dig?")
        self.assertIn("beslutsångesten", content_html)

    def test_extract_snippet_block_supports_excerpt_metadata_only_listing(self):
        html_text = """
        <div id="post-excerpt-605" class="excerpt post-605 post type-post status-publish format-standard hentry category-bild">
            <strong class="entry-title"><a href="https://ikttips.skolbloggen.se/2010/12/08/creative-commons-wikimedia-commons-och-flickr/" title="Permanent link to Creative Commons, wikimedia commons och flickr">Creative Commons, wikimedia commons och flickr</a></strong>
            <span class="date small"><abbr class="published" title="2010-12-08T21:53">december 8, 2010</abbr></span>
            <p class="categories filed alt-font">Posted in <a href="https://ikttips.skolbloggen.se/category/bild/">Bild</a>.</p>
            <span class="comments-link"><a href="https://ikttips.skolbloggen.se/2010/12/08/creative-commons-wikimedia-commons-och-flickr/#respond">No comments</a></span>
        </div><!-- .excerpt -->
        """
        extracted = harvest_article_links.extract_snippet_block(
            html_text,
            "2010/12/08/creative-commons-wikimedia-commons-och-flickr/index.html",
            "https://ikttips.skolbloggen.se/2010/12/08/creative-commons-wikimedia-commons-och-flickr/",
        )
        self.assertIsNotNone(extracted)
        title, content_html = extracted
        self.assertEqual(title, "Creative Commons, wikimedia commons och flickr")
        self.assertIn("december 8, 2010", content_html)
        self.assertIn("Posted in", content_html)

    def test_extract_snippet_block_falls_back_to_list_items_after_anchor(self):
        html_text = """
        <p>Vidare läsning:</p>
        <ul>
            <li>Nästa steg är att vi ska titta på inställningarna för bloggen:
                <a href="http://ikttips.skolbloggen.se/2011/02/02/andra-installningar-pa-bloggen/">Ändra inställningar på bloggen</a>
            </li>
        </ul>
        """
        extracted = harvest_article_links.extract_snippet_block(
            html_text,
            "2011/02/02/andra-installningar-pa-bloggen/index.html",
            "http://ikttips.skolbloggen.se/2011/02/02/andra-installningar-pa-bloggen/",
        )
        self.assertIsNotNone(extracted)
        title, content_html = extracted
        self.assertEqual(title, "Ändra inställningar på bloggen")
        self.assertIn("Nästa steg", content_html)

    def test_find_local_snippets_falls_back_when_primary_extractor_returns_empty_content(self):
        original_extract = harvest_article_links.extract_snippet_block
        original_legacy = harvest_article_links.extract_legacy_or_feed_snippet_block
        original_position = harvest_article_links.extract_position_based_post_snippet
        original_site_dir = harvest_article_links.SITE_DIR
        try:
            test_site = ROOT / "tests" / "_tmp_harvest_site"
            test_page = test_site / "2010" / "03" / "index.html"
            test_page.parent.mkdir(parents=True, exist_ok=True)
            test_page.write_text("<div>placeholder</div>", encoding="utf-8")
            harvest_article_links.SITE_DIR = test_site
            harvest_article_links.extract_snippet_block = lambda html_text, target_relative_path, original_url: ("Titel", "")
            harvest_article_links.extract_legacy_or_feed_snippet_block = lambda html_text, original_url: ("Titel", "<p>Återfunnet innehåll</p>")
            harvest_article_links.extract_position_based_post_snippet = lambda html_text, original_url: None
            snippets = harvest_article_links.find_local_snippets(
                "http://cwasteson.skolbloggen.se/2010/03/16/jag-ar-lite-avundsjuk/",
                "cwasteson.skolbloggen.se",
            )
            self.assertEqual(len(snippets), 1)
            self.assertIn("Återfunnet innehåll", snippets[0]["content_html"])
        finally:
            harvest_article_links.extract_snippet_block = original_extract
            harvest_article_links.extract_legacy_or_feed_snippet_block = original_legacy
            harvest_article_links.extract_position_based_post_snippet = original_position
            harvest_article_links.SITE_DIR = original_site_dir
            if test_site.exists():
                import shutil
                shutil.rmtree(test_site)


if __name__ == "__main__":
    unittest.main()
