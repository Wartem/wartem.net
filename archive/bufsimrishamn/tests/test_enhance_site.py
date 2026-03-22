from __future__ import annotations

import shutil
import unittest
from pathlib import Path
import json

import enhance_site


class EnhanceSiteTests(unittest.TestCase):
    def test_run_refuses_cleanup_without_explicit_flag(self):
        with self.assertRaises(SystemExit):
            enhance_site.run(["--site-dir", "site", "--cleanup-level", "minimal"])

    def test_classify_post_path(self):
        kind, year, month, day = enhance_site.classify_path("2014/02/06/oppna-klassrumsdorrar-ger-inspiration/index.html")
        self.assertEqual((kind, year, month, day), ("post", 2014, 2, 6))

    def test_classify_feed_path_before_category_or_tag(self):
        kind, year, month, day = enhance_site.classify_path("category/funderingar/feed/index.html")
        self.assertEqual((kind, year, month, day), ("feed", None, None, None))

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
            "example.org",
        )
        self.assertIn("_recovery/recovery.css", updated)
        self.assertIn("_recovery/recovery-topbar.js", updated)
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
            "example.org",
        )
        self.assertEqual(updated.lower().count('name="robots"'), 1)

    def test_inject_theme_replaces_existing_topbar(self):
        meta = enhance_site.PageMeta("2011/03/31/test/index.html", "Exempel", "post", 2011, 3, 31, "", "Artikel", "2011-03-31")
        html = '<html><head></head><body><div class="recovery-topbar"><div class="recovery-topbar__inner"><strong>Old</strong></div></div><div id="content" role="main"></div></body></html>'
        updated = enhance_site.inject_theme(
            html,
            "../../../../_recovery/recovery.css",
            '<div class="recovery-topbar"><div class="recovery-topbar__inner"><a class="recovery-topbar__brand" href="../../../../index.html">example.org</a><nav><a class="recovery-topbar__rootlink" href="../../../../../../index.html">← Till arkivet</a></nav></div></div>',
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
            "example.org",
        )
        self.assertIn("example.org", updated)
        self.assertIn(">← Till arkivet<", updated)
        self.assertNotIn("<strong>Old</strong>", updated)
        self.assertIn('<div id="content" role="main">', updated)

    def test_strip_existing_topbar_removes_only_topbar(self):
        html = (
            '<body><div class="recovery-topbar"><div class="recovery-topbar__inner"><div>Menu</div></div></div>'
            '<div id="page"><div id="content">Bevara detta</div></div></body>'
        )
        stripped = enhance_site.strip_existing_topbar(html)
        self.assertNotIn('class="recovery-topbar"', stripped)
        self.assertIn("Bevara detta", stripped)

    def test_promote_cwaste_navigation_panel_moves_navigation_into_sidepanel(self):
        meta = enhance_site.PageMeta("svenska/bedomning/test/index.html", "Test", "other", None, None, None, "", "Innehållssida", "")
        html = (
            '<html><body><div id="header"><div id="navigation"><ul class="nav"><li><a href="/svenska/">Svenska</a></li>'
            '<li class="secondary"><a href="/wp-login.php">Logga in</a></li></ul></div><!-- #navigation --></div>'
            '<div id="sub-header"><div id="all-categories"><ul class="nav"><li><a href="/category/x/">X</a></li></ul></div><!-- #list-categories --></div>'
            '<div class="entry-content"><p>Brödtext</p></div></body></html>'
        )
        updated = enhance_site.promote_cwaste_navigation_panel(html, meta, "cwaste.skolbloggen.se")
        self.assertIn("recovery-sidepanel--toc", updated)
        self.assertIn("Avdelningar", updated)
        self.assertIn("Kategorier", updated)
        panel_fragment = updated.split('recovery-sidepanel--toc', 1)[1]
        self.assertNotIn("Logga in", panel_fragment)
        self.assertIn("Brödtext", updated)

    def test_promote_ikttips_navigation_panel_moves_navigation_into_sidepanel(self):
        meta = enhance_site.PageMeta("lag-och-ratt/index.html", "Lag och rätt", "other", None, None, None, "", "InnehÃ¥llssida", "")
        html = (
            '<html><body><div id="header"><div class="wrapper"><div id="navigation"><ul class="nav">'
            '<li><a href="../ikt-verktyg/index.html">IKT-verktyg</a></li>'
            '<li><a href="index.html">Lag och rätt</a></li>'
            '<li class="secondary"><a href="/wp-login.php">Logga in</a></li>'
            '</ul></div><!-- #navigation --></div></div>'
            '<div id="sub-header"><div class="wrapper"><form method="get" id="cfct-search"><input type="text" /></form>'
            '<div id="all-categories"><strong>Categories:</strong><ul class="nav"><li><a href="../category/plagiatkontroll/index.html">Plagiatkontroll</a></li></ul></div>'
            '</div><!-- .wrapper --></div>'
            '<div class="entry-content"><p>BrÃ¶dtext</p></div></body></html>'
        )
        updated = enhance_site.promote_ikttips_navigation_panel(html, meta, "ikttips.skolbloggen.se")
        self.assertIn("recovery-sidepanel--toc", updated)
        self.assertIn("Avdelningar", updated)
        self.assertIn("Kategorier", updated)
        panel_fragment = updated.split('recovery-sidepanel--toc', 1)[1]
        self.assertIn("IKT-verktyg", panel_fragment)
        self.assertIn("Plagiatkontroll", panel_fragment)
        self.assertNotIn("cfct-search", panel_fragment)
        self.assertNotIn("Logga in", panel_fragment)
        self.assertIn("BrÃ¶dtext", updated)

    def test_inject_cwaste_section_overview_populates_empty_section_page(self):
        meta = enhance_site.PageMeta("svenska/index.html", "Svenska", "other", None, None, None, "", "InnehÃ¥llssida", "")
        child_one = enhance_site.PageMeta("svenska/referera/index.html", "Referera", "other", None, None, None, "", "InnehÃ¥llssida", "")
        child_two = enhance_site.PageMeta("svenska/referera/ex-pa-kallhanvisning/index.html", "Ett exempel", "other", None, None, None, "", "InnehÃ¥llssida", "")
        pages_by_path = {page.path: page for page in (meta, child_one, child_two)}
        html = '<html><body><div class="entry-content full-content"></div><!--/entry-content--></body></html>'
        updated = enhance_site.inject_cwaste_section_overview(html, meta, pages_by_path, "cwaste.skolbloggen.se")
        self.assertIn("Innehåll i avdelningen", updated)
        self.assertIn("Referera", updated)
        self.assertIn("Ett exempel", updated)
        self.assertIn('href="referera/index.html"', updated)

    def test_inject_cwaste_section_overview_skips_non_cwaste_pages(self):
        meta = enhance_site.PageMeta("example/index.html", "Example", "other", None, None, None, "", "InnehÃ¥llssida", "")
        html = '<html><body><div class="entry-content full-content"></div><!--/entry-content--></body></html>'
        updated = enhance_site.inject_cwaste_section_overview(html, meta, {meta.path: meta}, "example.org")
        self.assertNotIn("recovery-generated-overview", updated)

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
            "example.org",
        )
        self.assertIn('class="home blog recovery-enhanced recovery-kind-other recovery-site-example-org"', updated)

    def test_inject_theme_adds_kind_class_for_post_pages(self):
        meta = enhance_site.PageMeta("2011/01/21/test/index.html", "Exempel", "post", 2011, 1, 21, "", "Artikel", "2011-01-21")
        html = "<html><head></head><body><div id=\"content\" role=\"main\"></div></body></html>"
        updated = enhance_site.inject_theme(
            html,
            "../../../../_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
            "example.org",
            "aggressive",
        )
        self.assertIn('class="recovery-enhanced recovery-kind-post recovery-site-example-org"', updated)

    def test_build_topbar_includes_collection_menu(self):
        items = [enhance_site.CollectionNavItem("IKT-tips", "ikttips-skolbloggen/site/index.html")]
        topbar = enhance_site.build_topbar("index.html", "cwasteson.skolbloggen.se", items)
        self.assertIn("Samlingen", topbar)
        self.assertIn("../../ikttips-skolbloggen/site/index.html", topbar)
        self.assertNotIn(">Startsida<", topbar)
        self.assertIn(">← Till arkivet<", topbar)

    def test_load_collection_nav_reads_sibling_sites(self):
        temp_root = Path("M:/projects/wartem.net/archive/tmp-enhance-collection")
        if temp_root.exists():
            shutil.rmtree(temp_root)
        site_dir = temp_root / "cwasteson-skolbloggen" / "site"
        site_dir.mkdir(parents=True)
        collection_path = temp_root / "collections.json"
        collection_path.write_text(
            json.dumps(
                {
                    "collections": [
                        {
                            "slug": "charlotta-wasteson",
                            "entries": [
                                {"title": "Bollplanket", "local_path": "cwasteson-skolbloggen/site/index.html"},
                                {"title": "IKT-tips", "local_path": "ikttips-skolbloggen/site/index.html"},
                            ],
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        items = enhance_site.load_collection_nav(site_dir, str(collection_path), "charlotta-wasteson")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "IKT-tips")
        self.assertEqual(items[0].href, "ikttips-skolbloggen/site/index.html")
        shutil.rmtree(temp_root)

    def test_inject_theme_strips_pre_main_legacy_blocks_from_post_pages(self):
        meta = enhance_site.PageMeta("2011/01/21/test/index.html", "Exempel", "post", 2011, 1, 21, "", "Artikel", "2011-01-21")
        html = (
            "<html><head></head><body>"
            "<div id=\"page\"><div id=\"top\">Top</div><div id=\"header\">Header</div><div id=\"sub-header\">Sub</div>"
            "<div id=\"main\"><div id=\"content\" role=\"main\"><article class=\"post\"><div class=\"entry-content\"><p>Text</p></div></article></div></div>"
            "</div></body></html>"
        )
        updated = enhance_site.inject_theme(
            html,
            "../../../../_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
            "example.org",
            "aggressive",
        )
        self.assertNotIn('id="top"', updated)
        self.assertNotIn('id="header"', updated)
        self.assertNotIn('id="sub-header"', updated)
        self.assertIn('id="main"', updated)

    def test_rewrite_internal_anchors_retargets_existing_local_pages_only(self):
        meta = enhance_site.PageMeta(
            "2012/04/26/sank-priserna-pa-kollektivtrafiken/index.html",
            "Sänk priserna på kollektivtrafiken",
            "post",
            2012,
            4,
            26,
            "",
            "Artikel",
            "2012-04-26",
        )
        pages_by_path = {
            meta.path: meta,
            "2012/04/12/alla-butiker-borde-anvanda-sig-av-nathandel/index.html": enhance_site.PageMeta(
                "2012/04/12/alla-butiker-borde-anvanda-sig-av-nathandel/index.html",
                "Alla butiker borde använda sig av näthandel",
                "post",
                2012,
                4,
                12,
                "",
                "Artikel",
                "2012-04-12",
            ),
        }
        html = (
            '<div class="nav-previous"><a href="http://cwastes.skolbloggen.se/2012/04/12/alla-butiker-borde-anvanda-sig-av-nathandel/" rel="prev">Prev</a></div>'
            '<p><a href="http://example.com/other">Extern</a></p>'
            '<p><a href="http://cwastes.skolbloggen.se/2012/04/26/att-sanka-ungdomslonerna-ar-daligt/" rel="next">Missing local</a></p>'
        )
        updated = enhance_site.rewrite_internal_anchors(html, meta, pages_by_path, "cwastes.skolbloggen.se")
        self.assertIn('href="../../12/alla-butiker-borde-anvanda-sig-av-nathandel/index.html"', updated)
        self.assertIn('href="http://example.com/other"', updated)
        self.assertIn('href="http://cwastes.skolbloggen.se/2012/04/26/att-sanka-ungdomslonerna-ar-daligt/"', updated)

    def test_pretty_slug_for_category(self):
        self.assertEqual(enhance_site.pretty_slug("category/forskola-och-pedagogisk-omsorg/index.html"), "Forskola Och Pedagogisk Omsorg")

    def test_extract_title_prefers_page_title(self):
        html = '<header class="page-header"><h1 class="page-title">Gymnasium</h1></header><h1 class="entry-title">Artikel</h1>'
        self.assertEqual(enhance_site.extract_title(html), "Gymnasium")

    def test_normalize_display_text_repairs_mojibake_and_trims_blog_suffix(self):
        self.assertEqual(
            enhance_site.normalize_display_text("&raquo; Pippi som fÃ¶rebild Bollplanket"),
            "Pippi som förebild",
        )

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

    def test_clean_html_removes_platform_footer_and_admin_login_bar(self):
        html = """
<div id="footer">
  <p>&copy; 2017 Bollplanket Theme: Blix by <a href="http://www.kingcosmonaut.de/">Sebastian Schmieg</a>. Powered by <a href="http://wordpressmu.org">WordPress MU</a>.<br />Hosted by <a href="http://skolbloggen.se/">Skolbloggen</a></p>
  <div id="wpadminbar" class="nojq nojs">
    <a class="screen-reader-shortcut" href="#wp-toolbar">Hoppa till verktygsfältet</a>
    <div class="quicklinks" id="wp-toolbar">
      <ul id="wp-admin-bar-root-default">
        <li id="wp-admin-bar-login"><div class="ab-item ab-empty-item">
          <form name="adminloginform" id="adminloginform" action="http://cwasteson.skolbloggen.se/wp-login.php" method="post">
            <label for="user_login">Användarnamn eller e-postadress</label>
            <input type="text" name="log" id="user_login" />
            <input type="submit" id="wp-submit" value="Logga in" />
          </form>
        </div></li>
        <li id="wp-admin-bar-lostpassword"><a class="ab-item" href="http://skolbloggen.se/wp-login.php?action=lostpassword">Glömt lösenordet?</a></li>
        <li id="wp-admin-bar-register"><a class="ab-item" href="http://cwasteson.skolbloggen.se/wp-login.php?action=register">Registrera</a></li>
      </ul>
    </div>
  </div>
</div> <!-- /footer -->
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("WordPress MU", cleaned)
        self.assertNotIn("Hoppa till verktygsfältet", cleaned)
        self.assertNotIn("Användarnamn eller e-postadress", cleaned)
        self.assertNotIn("Glömt lösenordet?", cleaned)
        self.assertNotIn("Registrera", cleaned)

    def test_minimal_clean_html_keeps_large_blocks_but_removes_login_ui(self):
        html = """
<div id="page">
  <div id="secondary">Behåll sidebar</div>
  <div id="footer"><p>Powered by WordPress. Built on the Thematic Theme Framework.</p></div>
  <div id="wpadminbar"><form id="adminloginform"><label>Användarnamn eller e-postadress</label></form></div>
  <div class="entry-content"><p>Riktig artikeltext som ska vara kvar.</p></div>
</div>
"""
        cleaned = enhance_site.minimal_clean_html(html)
        self.assertIn("Behåll sidebar", cleaned)
        self.assertIn("Powered by WordPress", cleaned)
        self.assertIn("Riktig artikeltext som ska vara kvar.", cleaned)
        self.assertNotIn("Användarnamn eller e-postadress", cleaned)

    def test_inject_theme_none_preserves_large_blocks_by_default(self):
        meta = enhance_site.PageMeta("2011/01/21/test/index.html", "Exempel", "post", 2011, 1, 21, "", "Artikel", "2011-01-21")
        html = (
            "<html><head></head><body>"
            "<div id=\"page\"><div id=\"sidebar\">Sidebar kvar</div><div id=\"footer\">Powered by WordPress</div><div id=\"main\"><div id=\"content\" role=\"main\">"
            "<article class=\"post\"><div class=\"entry-content\"><p>Text</p></div></article>"
            "</div></div></div></body></html>"
        )
        updated = enhance_site.inject_theme(
            html,
            "../../../../_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
            "example.org",
        )
        self.assertIn("Sidebar kvar", updated)
        self.assertIn("Powered by WordPress", updated)
        self.assertIn("<p>Text</p>", updated)

    def test_inject_theme_minimal_preserves_sidebar_blocks(self):
        meta = enhance_site.PageMeta("2011/01/21/test/index.html", "Exempel", "post", 2011, 1, 21, "", "Artikel", "2011-01-21")
        html = (
            "<html><head></head><body>"
            "<div id=\"page\"><div id=\"sidebar\">Sidebar kvar</div><div id=\"main\"><div id=\"content\" role=\"main\">"
            "<article class=\"post\"><div class=\"entry-content\"><p>Text</p></div></article>"
            "</div></div></div></body></html>"
        )
        updated = enhance_site.inject_theme(
            html,
            "../../../../_recovery/recovery.css",
            "<div class='recovery-topbar'></div>",
            "<div class='recovery-context'></div>",
            meta,
            {meta.path: meta},
            [],
            "example.org",
            "minimal",
        )
        self.assertIn("Sidebar kvar", updated)
        self.assertIn("<p>Text</p>", updated)

    def test_clean_html_does_not_truncate_page_after_admin_bar_or_footer_marker(self):
        html = """
<body>
<div id="wpadminbar"><div class="quicklinks">Admin</div></div>
<div id="page"><div id="content" role="main"><div class="post"><p>Bevara artikeltexten.</p></div></div></div>
<!-- footer ................................. -->
<div id="footer"><p>Theme: Blix by <a href="http://example.com">Tema</a>. Powered by <a href="http://wordpressmu.org">WordPress MU</a>. Hosted by <a href="http://skolbloggen.se/">Skolbloggen</a></p></div> <!-- /footer -->
</body>
"""
        cleaned = enhance_site.clean_html(html)
        self.assertIn("Bevara artikeltexten.", cleaned)
        self.assertNotIn('id="wpadminbar"', cleaned)
        self.assertNotIn("WordPress MU", cleaned)

    def test_clean_html_preserves_published_comments_but_removes_comment_form(self):
        html = """
<div id="comments">
  <ol class="commentlist">
    <li class="comment byuser"><div class="comment-body"><p>Det här är en riktig kommentar från en läsare.</p></div></li>
  </ol>
  <div id="respond">
    <h3 id="reply-title">Lämna ett svar</h3>
    <form id="commentform"><textarea name="comment"></textarea></form>
  </div>
</div><!-- #comments -->
"""
        cleaned = enhance_site.clean_html(html)
        self.assertIn("Det här är en riktig kommentar från en läsare.", cleaned)
        self.assertIn('id="comments"', cleaned)
        self.assertNotIn("commentform", cleaned)
        self.assertNotIn("Lämna ett svar", cleaned)

    def test_clean_html_removes_pingbacks_and_login_prompt_but_keeps_comments(self):
        html = """
<div id="comments">
  <p id="you-must-be-logged-in-to-comment">Du måste vara inloggad för att kommentera.</p>
  <p>Stay in touch with the conversation, subscribe to the RSS feed for comments on this post.</p>
  <h3 class="pings">Continuing the Discussion</h3>
  <ol class="pinglist commentlist hfeed"><li class="comment">Pingback</li></ol>
  <ol class="commentlist"><li class="comment"><div class="comment-body"><p>Riktig kommentar.</p></div></li></ol>
</div>
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("Du måste vara inloggad", cleaned)
        self.assertNotIn("Stay in touch with the conversation", cleaned)
        self.assertNotIn("Continuing the Discussion", cleaned)
        self.assertNotIn("pinglist", cleaned)
        self.assertIn("Riktig kommentar.", cleaned)

    def test_clean_html_removes_bp_admin_bar_variant_and_footer_comment(self):
        html = """
<!-- footer ................................. -->
<li class="align-right" id="bp-adminbar-visitrandom-menu">
  <a href="#">BesÃ¶k</a>
  <ul class="random-list"><li><a href="http://skolbloggen.se/blogs/?random-blog">SlumpmÃ¤ssig webbplats</a></li></ul>
</li>
</ul></div></div><!-- #wp-admin-bar -->
<div id="footer"><p>Theme: Blix by <a href="http://www.kingcosmonaut.de/">Sebastian Schmieg</a>. Powered by <a href="http://wordpressmu.org">WordPress MU</a>. Hosted by <a href="http://skolbloggen.se/">Skolbloggen</a></p></div> <!-- /footer -->
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("BesÃ¶k", cleaned)
        self.assertNotIn("SlumpmÃ¤ssig webbplats", cleaned)
        self.assertNotIn("WordPress MU", cleaned)
        self.assertNotIn("Hosted by", cleaned)
        self.assertNotIn("Theme: Blix", cleaned)

    def test_clean_html_removes_carrington_footer_search_and_signup_noise(self):
        html = """
<div id="footer" class="section">
  <div class="wrapper">
    <p id="generator-link">Proudly powered by <a href="http://wordpress.org/" rel="generator">WordPress</a> and <a href="http://carringtontheme.com" title="Carrington theme for WordPress">Carrington</a>.</p>
    <p id="developer-link"><a href="http://crowdfavorite.com">Carrington Theme by Crowd Favorite</a></p>
  </div>
</div>
<form method="get" id="cfct-search" action="http://ikttips.skolbloggen.se/">
  <div><input type="text" id="cfct-search-input" name="s" value="" /><input type="submit" value="Search" /></div>
</form>
<li class="secondary"><a href="http://ikttips.skolbloggen.se/wp-login.php">Logga in</a></li>
<li class="secondary"><a href="http://ikttips.skolbloggen.se/wp-login.php?action=register">Registrera</a></li>
<a class="screen-reader-shortcut" href="#wp-toolbar" tabindex="1">Hoppa till verktygsfältet</a>
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("Proudly powered by", cleaned)
        self.assertNotIn("Carrington Theme by", cleaned)
        self.assertNotIn('id="cfct-search"', cleaned)
        self.assertNotIn(">Registrera<", cleaned)
        self.assertNotIn(">Logga in<", cleaned)
        self.assertNotIn("Hoppa till verktygsfältet", cleaned)

    def test_clean_html_removes_meta_widget_and_random_blog_tail(self):
        html = """
<li id="meta-3" class="widget widget_meta"><h2 class="widgettitle">Meta</h2>
  <ul>
    <li><a href="http://skolbloggen.se/register/">Registrera</a></li>
    <li><a href="http://smeste09.skolbloggen.se/feed/">Inlägg via RSS</a></li>
    <li><a href="https://wordpress.org/">WordPress.org</a></li>
  </ul>
</li>
</li></ul></li>
  <li class="alt"><a href="http://skolbloggen.se/groups/?random-group" rel="nofollow">Slumpad grupp</a></li>
  <li><a href="http://skolbloggen.se/blogs/?random-blog" rel="nofollow">Slumpmässig webbplats</a></li>
<!-- Generated in 0,949 seconds. (132 q) -->
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("WordPress.org", cleaned)
        self.assertNotIn("Slumpad grupp", cleaned)
        self.assertNotIn("Slumpmässig webbplats", cleaned)
        self.assertNotIn("Generated in", cleaned)

    def test_clean_html_removes_sidebar_widgets_but_keeps_main_comments(self):
        html = """
<div id="secondary" class="widget-area" role="complementary">
  <div id="carrington-subscribe" class="widget">Prenumerera</div>
  <div id="linkcat-34367" class="widget widget_links"><h2 class="widget-title">Tips kring digitala resurser och verktyg:</h2><ul><li><a href="http://example.com">Extern länk</a></li></ul></div>
</div><!-- #secondary .widget-area -->
<ul id="comments" class="commentlist">
  <li class="comment"><div class="comment-body"><p>Bevara den här kommentaren.</p></div></li>
</ul>
<li id="recent-comments-4" class="widgetcontainer widget_recent_comments"><h3 class="widgettitle">Senaste kommentarer</h3></li>
<li id="tag_cloud-5" class="widgetcontainer widget_tag_cloud"><h3 class="widgettitle">Taggar</h3></li>
"""
        cleaned = enhance_site.clean_html(html)
        self.assertNotIn("Prenumerera", cleaned)
        self.assertNotIn("Tips kring digitala resurser och verktyg:", cleaned)
        self.assertNotIn("Senaste kommentarer", cleaned)
        self.assertNotIn(">Taggar<", cleaned)
        self.assertIn("Bevara den här kommentaren.", cleaned)

    def test_lift_repeated_post_links_moves_footer_meta_into_sidepanel(self):
        html = """
<div class="post">
  <div class="entrytext">
    <p>Brödtext.</p>
    <p class="postmetadata alt"><small>This entry was posted in <a href="/category/test/">Test</a>.</small></p>
    <p class="postfeedback"><a href="/2011/01/01/test/" class="permalink">Permalink</a></p>
  </div>
</div>
"""
        updated = enhance_site.lift_repeated_post_links(html)
        self.assertIn('class="recovery-sidepanel"', updated)
        self.assertIn("Artikelinfo", updated)
        self.assertIn("Permalink", updated)
        self.assertEqual(updated.count("postmetadata alt"), 1)
        self.assertLess(updated.find('class="recovery-sidepanel"'), updated.find("<p>Brödtext.</p>"))

    def test_lift_repeated_post_links_replaces_existing_recovery_sidepanel(self):
        html = """
<div class="post">
  <div class="entrytext">
    <aside class="recovery-sidepanel"><h3>Artikelinfo</h3></aside>
    <p>BrÃ¶dtext.</p>
    <p class="postfeedback"><a href="/2011/01/01/test/" class="permalink">Permalink</a></p>
  </div>
</div>
"""
        updated = enhance_site.lift_repeated_post_links(html)
        self.assertEqual(updated.count('class="recovery-sidepanel"'), 1)
        self.assertIn("Permalink", updated)

    def test_theme_css_shows_published_comments(self):
        self.assertIn(".single #comments,.single-post #comments,.post-template-default #comments,.recovery-kind-post #comments{display:block", enhance_site.THEME_CSS)
        self.assertIn(".single #comments .commentlist,.single-post #comments .commentlist,.post-template-default #comments .commentlist", enhance_site.THEME_CSS)

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

    def test_split_post_pages_separates_reconstructed_posts(self):
        pages = [
            enhance_site.PageMeta("2011/03/10/full/index.html", "Full", "post", 2011, 3, 10, "Vanlig sammanfattning", "Artikel", "2011-03-10"),
            enhance_site.PageMeta(
                "2011/03/10/reconstructed/index.html",
                "Rekonstruerad",
                "post",
                2011,
                3,
                10,
                "Den fullständiga artikelsidan kunde inte återfinnas som egen capture i Wayback Machine. Textutdrag nedan är återfunna från arkivlistningar.",
                "Artikel",
                "2011-03-10",
            ),
        ]
        full_posts, reconstructed_posts = enhance_site.split_post_pages(pages)
        self.assertEqual(len(full_posts), 1)
        self.assertEqual(len(reconstructed_posts), 1)

    def test_extract_taxonomy_pairs_supports_legacy_filed_in_markup(self):
        html_text = (
            '<div class="entrymeta"><div class="postinfo">'
            '<span class="filedto">Filed in '
            '<a href="../../../../category/internet/index.html" rel="category tag">Internet</a>, '
            '<a href="../../../../category/funderingar/index.html" rel="category tag">funderingar</a>'
            '<br />Etiketter:'
            '<a href="../../../../tag/dokument/index.html" rel="tag">dokument</a>, '
            '<a href="../../../../tag/google/index.html" rel="tag">google</a>'
            '<br /></span></div></div>'
        )
        categories = enhance_site.extract_taxonomy_pairs(
            html_text,
            "cat-links",
            "2010/06/13/en-mindmap-over-google-dokument/index.html",
        )
        tags = enhance_site.extract_taxonomy_pairs(
            html_text,
            "tag-links",
            "2010/06/13/en-mindmap-over-google-dokument/index.html",
        )
        self.assertEqual(
            categories,
            [
                ("category/internet/index.html", "Internet"),
                ("category/funderingar/index.html", "funderingar"),
            ],
        )
        self.assertEqual(
            tags,
            [
                ("tag/dokument/index.html", "dokument"),
                ("tag/google/index.html", "google"),
            ],
        )

    def test_extract_taxonomy_pairs_normalizes_absolute_internal_urls(self):
        html_text = (
            '<p>Published under '
            '<a href="http://cwaste.skolbloggen.se/category/introduktion/" rel="category tag">Introduktion</a>'
            ' and tagged: '
            '<a href="http://cwaste.skolbloggen.se/tag/presentation/" rel="tag">presentation</a></p>'
        )
        categories = enhance_site.extract_taxonomy_pairs(
            html_text,
            "cat-links",
            "2010/01/05/valkommen-till-sv-b/index.html",
        )
        tags = enhance_site.extract_taxonomy_pairs(
            html_text,
            "tag-links",
            "2010/01/05/valkommen-till-sv-b/index.html",
        )
        self.assertEqual(categories, [("category/introduktion/index.html", "Introduktion")])
        self.assertEqual(tags, [("tag/presentation/index.html", "presentation")])

    def test_theme_css_resets_legacy_article_floats_and_captions(self):
        self.assertIn(".single .alignleft,.single .alignright,.single .aligncenter", enhance_site.THEME_CSS)
        self.assertIn(".single .wp-caption,.single-post .wp-caption,.post-template-default .wp-caption", enhance_site.THEME_CSS)
        self.assertIn(".single .entry-content::after", enhance_site.THEME_CSS)
        self.assertIn(".single #primary,.single-post #primary,.post-template-default #primary{display:block!important;float:none!important;width:100%!important", enhance_site.THEME_CSS)
        self.assertIn(".single #content,.single-post #content,.post-template-default #content,.recovery-kind-post #content,.recovery-kind-post .wrapper>#content{display:block!important;float:none!important;width:100%!important", enhance_site.THEME_CSS)
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
            "example.org",
        )
        self.assertIn("recovery-listing-tools", updated)
        self.assertLess(updated.index("recovery-context"), updated.index("recovery-listing-tools"))

    def test_build_report_page_uses_recovery_layout(self):
        site_dir = Path("M:/projects/bufsimrishamn/site")
        pages = [
            enhance_site.PageMeta("index.html", "Startsida", "home", None, None, None, "", "Startsida", ""),
            enhance_site.PageMeta("2017/12/01/test/index.html", "Test", "post", 2017, 12, 1, "Sammanfattning", "Artikel", "2017-12-01"),
            enhance_site.PageMeta("browse/index.html", "Utforska", "browse", None, None, None, "", "Utforskare", ""),
            enhance_site.PageMeta("2017/12/index.html", "2017-12", "archive", 2017, 12, None, "", "Arkiv", "2017-12"),
            enhance_site.PageMeta("category/gymnasium/index.html", "Gymnasium", "category", None, None, None, "", "Kategori", ""),
            enhance_site.PageMeta("tag/test/index.html", "Test", "tag", None, None, None, "", "Tagg", ""),
            enhance_site.PageMeta("feed/index.html", "Feed", "feed", None, None, None, "", "Flöde", ""),
        ]
        report = enhance_site.build_report_page(site_dir, pages)
        self.assertIn("recovery-topbar", report)
        self.assertIn("Återställningsrapport", report)
        self.assertIn("manifest.json", report)
        self.assertIn('name="robots"', report)
        self.assertIn("Artikelsidor:</strong> 1", report)
        self.assertIn("Rekonstruerade artikelposter:</strong> 0", report)
        self.assertIn("Navigationssidor:</strong> 3", report)
        self.assertIn("Tagg/Kategori/Arkiv:</strong> 3", report)
        self.assertIn("lokala HTML-sidor totalt", report)

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

    def test_build_browse_page_hides_empty_taxonomy_and_archive_entries_when_nonempty_exist(self):
        pages = [
            enhance_site.PageMeta("2017/12/01/test/index.html", "Test", "post", 2017, 12, 1, "Sammanfattning", "Artikel", "2017-12-01"),
            enhance_site.PageMeta("2017/12/index.html", "2017-12", "archive", 2017, 12, None, "", "Arkiv", "2017-12"),
            enhance_site.PageMeta("2017/11/index.html", "2017-11", "archive", 2017, 11, None, "", "Arkiv", "2017-11"),
            enhance_site.PageMeta("category/gymnasium/index.html", "Gymnasium", "category", None, None, None, "", "Kategori", ""),
            enhance_site.PageMeta("category/gymnasium/feed/index.html", "Gymnasium feed", "feed", None, None, None, "", "Flöde", ""),
            enhance_site.PageMeta("tag/charlotta-wasteson/index.html", "Charlotta Wasteson", "tag", None, None, None, "", "Tagg", ""),
            enhance_site.PageMeta("tag/tomt/index.html", "Tomt", "tag", None, None, None, "", "Tagg", ""),
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
        self.assertIn("Gymnasium", browse)
        self.assertIn("Charlotta Wasteson", browse)
        self.assertNotIn("Tomt", browse)
        self.assertNotIn("2017-11", browse)

    def test_build_home_page_includes_robots_meta(self):
        pages = [
            enhance_site.PageMeta("2017/12/01/test/index.html", "Test", "post", 2017, 12, 1, "Sammanfattning", "Artikel", "2017-12-01"),
        ]
        home = enhance_site.build_home_page(pages)
        self.assertIn('name="robots"', home)
        self.assertIn(">← Till arkivet<", home)

    def test_build_home_page_surfaces_content_sections(self):
        pages = [
            enhance_site.PageMeta("svenska/index.html", "Svenska", "other", None, None, None, "Material", "Innehållssida", ""),
            enhance_site.PageMeta("svenska/referera/index.html", "Referera", "other", None, None, None, "Material", "Innehållssida", ""),
            enhance_site.PageMeta("studieteknik/index.html", "Studieteknik", "other", None, None, None, "Material", "Innehållssida", ""),
        ]
        home = enhance_site.build_home_page(pages)
        self.assertIn("Större innehållsavdelningar", home)
        self.assertIn("svenska/index.html", home)
        self.assertIn("2 innehållssidor", home)

    def test_write_support_files_emits_crawler_blocking_files(self):
        site_dir = Path("test-output-support-files")
        shutil.rmtree(site_dir, ignore_errors=True)
        try:
            enhance_site.write_support_files(site_dir, [])
            self.assertEqual((site_dir / "robots.txt").read_text(encoding="utf-8"), "User-agent: *\nDisallow: /\n")
            self.assertIn("X-Robots-Tag", (site_dir / ".htaccess").read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(site_dir, ignore_errors=True)

    def test_unwrap_wayback_url_returns_original_url(self):
        self.assertEqual(
            enhance_site.unwrap_wayback_url(
                "https://web.archive.org/web/20120126060026/http://cwasteson.skolbloggen.se/2011/04/29/en-forfarlig-paskhelg-pa-osterlen/"
            ),
            "http://cwasteson.skolbloggen.se/2011/04/29/en-forfarlig-paskhelg-pa-osterlen/",
        )

    def test_minimal_clean_html_removes_wayback_toolbar(self):
        html = """
<html><head>
<link rel="stylesheet" type="text/css" href="https://web-static.archive.org/_static/css/banner-styles.css?v=1" />
</head><body>
<!-- BEGIN WAYBACK TOOLBAR INSERT -->
<div id="wm-ipp-base"><div id="wm-ipp"></div></div>
<div id="wm-ipp-print">The Wayback Machine</div>
<!-- END WAYBACK TOOLBAR INSERT -->
<div id="content" role="main"><p>Innehåll</p></div>
</body></html>
"""
        cleaned = enhance_site.minimal_clean_html(html)
        self.assertNotIn("wm-ipp-base", cleaned)
        self.assertNotIn("banner-styles.css", cleaned)
        self.assertIn("<p>Innehåll</p>", cleaned)


if __name__ == "__main__":
    unittest.main()
