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


if __name__ == "__main__":
    unittest.main()
