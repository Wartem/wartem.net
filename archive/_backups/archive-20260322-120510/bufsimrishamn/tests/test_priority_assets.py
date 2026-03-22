from __future__ import annotations

import unittest

import priority_assets


class PriorityAssetsTests(unittest.TestCase):
    def test_prioritize_prefers_original_over_thumbnail(self):
        candidates = [
            "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=300&h=199",
            "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=704&h=468",
            "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg",
        ]

        groups = priority_assets.prioritize_candidates(candidates)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].best_url, "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg")

    def test_relative_asset_path_hashes_query_variants(self):
        path = priority_assets.relative_asset_path("https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=300&h=199")
        self.assertTrue(path.startswith("_assets/bufsimrishamn.files.wordpress.com/2014/02/dsc_0244--"))
        self.assertTrue(path.endswith(".jpg"))

    def test_archive_lookup_candidates_prefers_larger_variants_before_smaller(self):
        group = priority_assets.AssetGroup(
            host="bufsimrishamn.files.wordpress.com",
            path="/2014/02/dsc_0244.jpg",
            candidates=(
                "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=150&h=100",
                "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=704&h=468",
                "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg",
            ),
            best_url="https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg",
            score=(1, 1, 0),
        )

        ordered = priority_assets.archive_lookup_candidates(group)

        self.assertEqual(ordered[0], "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg")
        self.assertIn("https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg?w=704&h=468", ordered[:3])

    def test_filter_candidates_by_host_patterns_keeps_only_matching_hosts(self):
        candidates = [
            "https://farm5.staticflickr.com/4775/40093665024_a6ae0cfa6b_z.jpg",
            "https://live.staticflickr.com/65535/example.jpg",
            "https://bufsimrishamn.files.wordpress.com/2014/02/dsc_0244.jpg",
        ]

        filtered = priority_assets.filter_candidates_by_host_patterns(
            candidates,
            ["farm", "live.staticflickr.com"],
        )

        self.assertEqual(
            filtered,
            [
                "https://farm5.staticflickr.com/4775/40093665024_a6ae0cfa6b_z.jpg",
                "https://live.staticflickr.com/65535/example.jpg",
            ],
        )

    def test_candidate_urls_from_html_finds_flickr_images(self):
        html = '<p><img src="https://farm5.staticflickr.com/4775/40093665024_a6ae0cfa6b_z.jpg" alt="bild" /></p>'

        urls = priority_assets.candidate_urls_from_html(
            html,
            "https://bufsimrishamn.wordpress.com/2017/12/05/kulturpedagogiska-enheten/",
            "bufsimrishamn.wordpress.com",
        )

        self.assertIn("https://farm5.staticflickr.com/4775/40093665024_a6ae0cfa6b_z.jpg", urls)

    def test_candidate_urls_from_html_with_options_finds_extra_asset_hosts(self):
        html = '<p><img src="https://blogger.googleusercontent.com/img/a/sample.jpg" alt="bild" /></p>'

        urls = priority_assets.candidate_urls_from_html_with_options(
            html,
            "https://cwasteson.blogspot.com/2011/01/post/",
            "cwasteson.blogspot.com",
            extra_asset_hosts=["blogger.googleusercontent.com"],
        )

        self.assertIn("https://blogger.googleusercontent.com/img/a/sample.jpg", urls)


if __name__ == "__main__":
    unittest.main()
