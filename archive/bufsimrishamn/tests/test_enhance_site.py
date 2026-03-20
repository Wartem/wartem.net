from __future__ import annotations

import shutil
import unittest
from pathlib import Path

import enhance_site


class EnhanceSiteTests(unittest.TestCase):
    def test_classify_post_path(self):
        kind, year, month, day = enhance_site.classify_path("2014/02/06/oppna-klassrumsdorrar-ger-inspiration/index.html")
        self.assertEqual((kind, year, month, day), ("post", 2014, 2, 6))

    def test_inject_theme_adds_topbar_and_theme(self):
        meta = enhance_site.PageMeta("example/index.html", "Exempel", "other", None, None, None, "", "Sida", "")
        html = "<html><head></head><body><div id=\"content\" role=\"main\"></div></body></html>"
        updated = enhance_site.inject_theme(
            html,
            "_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
        )
        self.assertIn("_recovery/recovery.css", updated)
        self.assertIn("recovery-topbar", updated)
        self.assertIn("recovery-context", updated)
        self.assertIn('name="robots"', updated)

    def test_inject_theme_does_not_duplicate_existing_robots_meta(self):
        meta = enhance_site.PageMeta("example/index.html", "Exempel", "other", None, None, None, "", "Sida", "")
        html = '<html><head><meta name="robots" content="noindex"></head><body><div id="content" role="main"></div></body></html>'
        updated = enhance_site.inject_theme(
            html,
            "_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
        )
        self.assertEqual(updated.lower().count('name="robots"'), 1)

    def test_inject_theme_preserves_existing_body_classes(self):
        meta = enhance_site.PageMeta("example/index.html", "Exempel", "other", None, None, None, "", "Sida", "")
        html = '<html><head></head><body class="home blog"><div id="content" role="main"></div></body></html>'
        updated = enhance_site.inject_theme(
            html,
            "_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
        )
        self.assertIn('class="home blog recovery-enhanced"', updated)

    def test_pretty_slug_for_category(self):
        self.assertEqual(enhance_site.pretty_slug("category/forskola-och-pedagogisk-omsorg/index.html"), "Forskola Och Pedagogisk Omsorg")

    def test_extract_title_prefers_page_title(self):
        html = '<header class="page-header"><h1 class="page-title">Gymnasium</h1></header><h1 class="entry-title">Artikel</h1>'
        self.assertEqual(enhance_site.extract_title(html), "Gymnasium")

    def test_clean_html_removes_nonfunctional_wordpress_artifacts(self):
        html = """
<div id="page">Innehåll</div><!-- #page -->
<footer id="colophon" role="contentinfo"><div id="site-info"><a href="https://wordpress.com/?ref=footer_website">Blogga med WordPress.com.</a></div></footer><!-- #colophon -->
<div id="carousel-reblog-box"><form><textarea placeholder="Skriv dina tankar här... (valfritt)"></textarea><label>Posta till</label></form></div>
<div class="widget widget_eu_cookie_law_widget"><div id="eu-cookie-law"><form><input type="submit" value="Stäng och acceptera" /> <a href="https://automattic.com/cookies">Cookie-policy</a></form></div></div>
<div id="comments"><form id="commentform"></form></div><!-- #comments -->
<nav id="access" role="navigation">meny</nav><!-- #access -->
<div id="secondary" class="widget-area" role="complementary"><aside id="archives-1" class="widget widget_archive">Arkiv</aside></div><!-- #secondary .widget-area -->
<div id="tertiary" class="widget-area" role="complementary"><aside id="meta-1" class="widget widget_meta">Meta</aside></div><!-- #tertiary .widget-area -->
<div id="sharing_email">delning</div>
</body>
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("Blogga med WordPress.com.", cleaned)
        self.assertNotIn("Skriv dina tankar", cleaned)
        self.assertNotIn("Cookie-policy", cleaned)
        self.assertNotIn("commentform", cleaned)
        self.assertNotIn("delning", cleaned)
        self.assertNotIn('id="secondary"', cleaned)
        self.assertNotIn('id="tertiary"', cleaned)
        self.assertNotIn('id="access"', cleaned)

    def test_search_index_records_include_post_kind(self):
        pages = [
            enhance_site.PageMeta(
                path="2014/02/06/test/index.html",
                title="Test",
                kind="post",
                year=2014,
                month=2,
                day=6,
                summary="Sammanfattning",
                kind_label="Artikel",
                date_label="2014-02-06",
            )
        ]
        records = enhance_site.search_index_records(pages)
        self.assertEqual(records[0]["kind"], "post")
        self.assertEqual(records[0]["sort_date"], "2014-02-06")

    def test_theme_css_resets_legacy_article_floats_and_captions(self):
        self.assertIn(".single .alignleft,.single .alignright,.single .aligncenter", enhance_site.THEME_CSS)
        self.assertIn(".single .wp-caption,.single-post .wp-caption,.post-template-default .wp-caption", enhance_site.THEME_CSS)
        self.assertIn(".single .entry-content::after", enhance_site.THEME_CSS)
        self.assertIn(".single #primary,.single-post #primary,.post-template-default #primary{display:block!important;float:none!important;width:100%!important", enhance_site.THEME_CSS)
        self.assertIn(".single #content,.single-post #content,.post-template-default #content{display:block!important;float:none!important;width:100%!important", enhance_site.THEME_CSS)
        self.assertIn(".single #masthead img,.single-post #masthead img,.post-template-default #masthead img{float:none!important}", enhance_site.THEME_CSS)

    def test_theme_css_resets_archive_and_category_layout(self):
        self.assertIn(".archive #primary,.category #primary,.tag #primary,.author #primary,.blog #primary{display:block!important;float:none!important;width:100%!important", enhance_site.THEME_CSS)
        self.assertIn(".archive #masthead img,.category #masthead img,.tag #masthead img,.author #masthead img,.blog #masthead img{float:none!important}", enhance_site.THEME_CSS)
        self.assertIn(".archive article.post,.category article.post,.tag article.post,.author article.post,.blog article.post{max-width:var(--listing-measure)", enhance_site.THEME_CSS)

    def test_rewrite_listing_articles_builds_compact_card(self):
        meta = enhance_site.PageMeta("category/gymnasium/index.html", "Gymnasium", "category", None, None, None, "", "Kategori", "")
        linked_page = enhance_site.PageMeta(
            path="2017/12/01/oppet-hus-pa-osterlengymnasiet/index.html",
            title="Öppet hus på Österlengymnasiet",
            kind="post",
            year=2017,
            month=12,
            day=1,
            summary="Kort sammanfattning av artikeln.",
            kind_label="Artikel",
            date_label="2017-12-01",
        )
        html = """
<header class="page-header"><h1 class="page-title">Gymnasium</h1></header>
<article id="post-1" class="post type-post">
  <header class="entry-header">
    <h1 class="entry-title"><a href="../../2017/12/01/oppet-hus-pa-osterlengymnasiet/index.html">Gammal titel</a></h1>
    <div class="entry-meta"><span class="author vcard"><a href="../../author/test/index.html">Redaktionen</a></span></div>
  </header>
  <div class="entry-content"><p>Lång text</p><p><img src="image.jpg" alt="bild" /></p></div>
  <footer class="entry-meta"><p class="cat-links"><a href="../gymnasium/index.html">Gymnasium</a></p></footer>
</article>
"""
        updated = enhance_site.rewrite_listing_articles(html, meta, {linked_page.path: linked_page})
        self.assertIn("recovery-listing-card", updated)
        self.assertIn("2017-12-01", updated)
        self.assertIn("Kort sammanfattning av artikeln.", updated)
        self.assertIn("Läs artikeln", updated)

    def test_inject_theme_places_listing_tools_after_context(self):
        meta = enhance_site.PageMeta("category/gymnasium/index.html", "Gymnasium", "category", None, None, None, "", "Kategori", "")
        record = enhance_site.PostRecord(
            path="2017/12/01/test/index.html",
            title="Test",
            summary="Sammanfattning",
            date_label="2017-12-01",
            sort_key=(2017, 12, 1, "2017/12/01/test/index.html"),
            author="Redaktionen",
            image_src="image.jpg",
            image_alt="bild",
            categories=[("category/gymnasium/index.html", "Gymnasium")],
            tags=[],
        )
        html = "<html><head></head><body><div id=\"content\" role=\"main\"><header class=\"page-header\"><h1 class=\"page-title\">Gymnasium</h1></header></div><!-- #content --></body></html>"
        context = "<div class='recovery-context'></div>"
        updated = enhance_site.inject_theme(
            html,
            "_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            context,
            meta,
            {meta.path: meta},
            [record],
        )
        self.assertIn("recovery-listing-tools", updated)
        self.assertLess(updated.index("recovery-context"), updated.index("recovery-listing-tools"))

    def test_build_report_page_uses_recovery_layout(self):
        site_dir = Path("M:/projects/bufsimrishamn/site")
        pages = [
            enhance_site.PageMeta("index.html", "Startsida", "home", None, None, None, "", "Startsida", ""),
            enhance_site.PageMeta("2017/12/01/test/index.html", "Test", "post", 2017, 12, 1, "Sammanfattning", "Artikel", "2017-12-01"),
        ]
        report = enhance_site.build_report_page(site_dir, pages)
        self.assertIn("recovery-topbar", report)
        self.assertIn("Återställningsrapport", report)
        self.assertIn("manifest.json", report)
        self.assertIn('name="robots"', report)

    def test_build_browse_page_prioritizes_categories_archives_and_tag_panel(self):
        pages = [
            enhance_site.PageMeta("2017/12/01/test/index.html", "Test", "post", 2017, 12, 1, "Sammanfattning", "Artikel", "2017-12-01"),
            enhance_site.PageMeta("2017/12/index.html", "2017-12", "archive", 2017, 12, None, "", "Arkiv", "2017-12"),
            enhance_site.PageMeta("category/gymnasium/index.html", "Gymnasium", "category", None, None, None, "", "Kategori", ""),
            enhance_site.PageMeta("tag/charlotta-wasteson/index.html", "Charlotta Wasteson", "tag", None, None, None, "", "Tagg", ""),
        ]
        records = [
            enhance_site.PostRecord(
                path="2017/12/01/test/index.html",
                title="Test",
                summary="Sammanfattning",
                date_label="2017-12-01",
                sort_key=(2017, 12, 1, "2017/12/01/test/index.html"),
                author="Redaktionen",
                image_src="",
                image_alt="",
                categories=[("category/gymnasium/index.html", "Gymnasium")],
                tags=[("tag/charlotta-wasteson/index.html", "Charlotta Wasteson")],
            )
        ]
        browse = enhance_site.build_browse_page(pages, records)
        self.assertIn("recovery-browse-layout", browse)
        self.assertIn("recovery-browse-sidebar", browse)
        self.assertIn('id="categories"', browse)
        self.assertIn('id="archives"', browse)
        self.assertIn('id="recent"', browse)
        self.assertIn('id="tags"', browse)
        self.assertNotIn('id="tags-all"', browse)
        self.assertNotIn("Visa fler taggar", browse)
        self.assertIn('name="robots"', browse)

    def test_build_home_page_includes_robots_meta(self):
        pages = [
            enhance_site.PageMeta("2017/12/01/test/index.html", "Test", "post", 2017, 12, 1, "Sammanfattning", "Artikel", "2017-12-01"),
        ]
        home = enhance_site.build_home_page(pages)
        self.assertIn('name="robots"', home)

    def test_write_support_files_emits_crawler_blocking_files(self):
        site_dir = Path("test-output-support-files")
        shutil.rmtree(site_dir, ignore_errors=True)
        try:
            enhance_site.write_support_files(site_dir, [])
            self.assertEqual((site_dir / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nDisallow: /\n")
            self.assertIn("X-Robots-Tag", (site_dir / ".htaccess").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(site_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
