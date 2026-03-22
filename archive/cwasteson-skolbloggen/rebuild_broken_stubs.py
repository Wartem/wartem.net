from __future__ import annotations

import json
from pathlib import Path

import harvest_article_links


ROOT = Path(__file__).resolve().parent
BROKEN_LIST_PATH = ROOT / "site" / "recovery" / "broken-posts.txt"
SITE_DIR = ROOT / "site"
REPORT_PATH = SITE_DIR / "recovery" / "rebuild-broken-stubs-summary.json"
PRIMARY_DOMAIN = "cwasteson.skolbloggen.se"


def relative_to_url(relative_path: str) -> str:
    if relative_path == "index.html":
        return f"https://{PRIMARY_DOMAIN}/"
    if relative_path.endswith("/index.html"):
        return f"https://{PRIMARY_DOMAIN}/" + relative_path.removesuffix("index.html")
    return f"https://{PRIMARY_DOMAIN}/" + relative_path


def main() -> int:
    targets = [
        line.strip()
        for line in BROKEN_LIST_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    results: dict[str, object] = {
        "target_count": len(targets),
        "rebuilt_count": 0,
        "failed_count": 0,
        "rebuilt": [],
        "failed": [],
    }

    for relative_path in targets:
        target_url = relative_to_url(relative_path)
        snippets = []
        for item in harvest_article_links.find_local_snippets(target_url, PRIMARY_DOMAIN):
            source_path = item["source_path"]
            if source_path in {"index.html", "browse/index.html", "recovery/index.html"}:
                continue
            source_file = SITE_DIR / source_path
            if not source_file.exists():
                continue
            source_text = source_file.read_text(encoding="utf-8", errors="replace")
            if "Den fullständiga artikelsidan kunde inte återfinnas som egen capture i Wayback Machine." in source_text:
                continue
            snippets.append(item)
        if not snippets:
            results["failed"].append({"path": relative_path, "error": "no-local-snippets-found"})
            continue
        destination = SITE_DIR / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(harvest_article_links.build_stub_page(target_url, snippets), encoding="utf-8")
        results["rebuilt"].append(
            {"path": relative_path, "snippet_count": len(snippets), "source_paths": [item["source_path"] for item in snippets]}
        )

    results["rebuilt_count"] = len(results["rebuilt"])
    results["failed_count"] = len(results["failed"])
    REPORT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if not results["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
