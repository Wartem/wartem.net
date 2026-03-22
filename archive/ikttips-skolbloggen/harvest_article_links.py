from __future__ import annotations

import importlib.util
import json
import sys
from urllib.parse import urlsplit
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "cwasteson-skolbloggen" / "harvest_article_links.py"

spec = importlib.util.spec_from_file_location("shared_harvest_article_links", SOURCE)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

module.ROOT = ROOT
module.SITE_DIR = ROOT / "site"
module.RECOVERY_DIR = module.SITE_DIR / "recovery"
module.INVENTORY_PATH = ROOT / "out" / "urls_unique.csv"
module.SUMMARY_PATH = module.RECOVERY_DIR / "harvest-article-links-summary.json"
module.CANDIDATES_PATH = module.RECOVERY_DIR / "harvest-article-links-candidates.json"


def _bootstrap_local_candidates() -> None:
    rows = module.load_inventory_rows(module.INVENTORY_PATH)
    if not rows:
        raise SystemExit("Inventory saknas eller är tom.")
    primary_domain = (urlsplit(rows[0]["normalized_url"]).hostname or "").lower()
    candidate_urls = sorted(
        {
            module.canonicalize_candidate_url(url)
            for url in module.scan_local_pages_for_links(primary_domain)
            if module.is_meaningful_target_url(url, allow_listing_pages=False)
        },
        key=lambda url: (0 if module.POST_LIKE_RE.match(module.path_from_url(url)) else 1, url),
    )
    module.RECOVERY_DIR.mkdir(parents=True, exist_ok=True)
    module.CANDIDATES_PATH.write_text(
        json.dumps(
            {
                "seed_count": 0,
                "listing_candidate_count": 0,
                "local_link_candidate_count": len(candidate_urls),
                "candidate_count": len(candidate_urls),
                "candidate_urls": candidate_urls,
                "listing_scans": [],
                "mode": "local-link-bootstrap",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> int:
    if "--bootstrap-local-candidates" in sys.argv[1:]:
        _bootstrap_local_candidates()
        return 0
    if "--local-only" in sys.argv[1:]:
        sys.argv = [arg for arg in sys.argv if arg != "--local-only"]

        def _resolve_candidate_entry_local_only(*args, **kwargs):
            return None, "local_only"

        module.resolve_candidate_entry = _resolve_candidate_entry_local_only
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
