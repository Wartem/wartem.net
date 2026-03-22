from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
SITE_DIR = ROOT / "site"
RECOVERY_DIR = SITE_DIR / "recovery"
INVENTORY_PATH = ROOT / "out" / "urls_unique.csv"
SUMMARY_PATH = RECOVERY_DIR / "harvest-article-links-summary.json"
CANDIDATES_PATH = RECOVERY_DIR / "harvest-article-links-candidates.json"
POST_LIKE_RE = re.compile(r"^/\d{4}/\d{2}/\d{2}/[^/]+/?$")
MONTH_ARCHIVE_RE = re.compile(r"^/\d{4}/\d{2}/$")
CONTENT_PAGE_PATHS = {"/om/", "/om-mig/", "/about/"}
HTML_MIME_PREFIXES = ("text/html", "application/xhtml+xml")

sys.path.insert(0, str((ROOT.parent / "bufsimrishamn").resolve()))
import cdx_inventory  # type: ignore
import reconstruct_site  # type: ignore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Harvest more article URLs from multiple archived listing pages.")
    parser.add_argument("--offset", type=int, default=0, help="Candidate offset for download batching.")
    parser.add_argument("--limit", type=int, default=20, help="Candidate limit for download batching.")
    parser.add_argument("--max-captures-per-seed", type=int, default=4, help="How many captures to inspect per listing seed.")
    parser.add_argument("--skip-harvest", action="store_true", help="Reuse the last saved candidate list instead of rescanning listing pages.")
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-backoff-seconds", type=float, default=3.0)
    return parser.parse_args()


def load_inventory_rows(path: Path = INVENTORY_PATH) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def path_from_url(url: str) -> str:
    return urlsplit(url).path or "/"


def canonicalize_candidate_url(url: str) -> str:
    normalized = cdx_inventory.normalize_url(url)
    parts = urlsplit(normalized)
    path = parts.path or "/"
    if path != "/" and not PurePosixPath(path).suffix and not path.endswith("/"):
        normalized = normalized.replace(path, path + "/", 1)
    return normalized


def is_listing_seed(row: dict[str, str]) -> bool:
    kind = row.get("kind", "")
    path = path_from_url(row.get("normalized_url", ""))
    if kind in {"homepage", "category", "pagination"}:
        return True
    if kind == "other" and (MONTH_ARCHIVE_RE.match(path) or path in CONTENT_PAGE_PATHS):
        return True
    return False


def is_meaningful_target_url(url: str, *, allow_listing_pages: bool) -> bool:
    normalized = cdx_inventory.normalize_url(url)
    parts = urlsplit(normalized)
    path = parts.path or "/"
    if parts.query or parts.fragment:
        return False
    if path.endswith("/feed/") or path == "/feed/" or path.startswith("/feed/"):
        return False
    if "/comment-page-" in path or path.startswith("/comments/"):
        return False
    if path.startswith("/tag/"):
        return False
    if cdx_inventory.classify_url(normalized) == "media":
        return False
    if POST_LIKE_RE.match(path):
        return True
    if path in CONTENT_PAGE_PATHS:
        return True
    if allow_listing_pages and (path == "/" or MONTH_ARCHIVE_RE.match(path) or path.startswith("/category/") or path.startswith("/page/")):
        return True
    return False


def relative_path_for_url(url: str) -> str:
    path = path_from_url(url)
    if path == "/":
        return "index.html"
    base = PurePosixPath(path.lstrip("/"))
    if path.endswith("/"):
        return str(base / "index.html")
    if base.suffix:
        return str(base.with_name(base.stem + ".html"))
    return str(base / "index.html")


def local_file_exists(url: str, site_dir: Path = SITE_DIR) -> bool:
    return (site_dir / relative_path_for_url(url)).exists()


class InternalLinkCollector(HTMLParser):
    def __init__(self, current_url: str, primary_domain: str) -> None:
        super().__init__(convert_charrefs=False)
        self.current_url = current_url
        self.primary_domain = primary_domain
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        self._collect(attrs)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self._collect(attrs)

    def _collect(self, attrs) -> None:
        for name, value in attrs:
            if name.lower() != "href" or not value:
                continue
            if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            resolved = cdx_inventory.normalize_url(urljoin(self.current_url, value))
            if (urlsplit(resolved).hostname or "").lower() != self.primary_domain:
                continue
            self.links.add(resolved)


def extract_internal_links(html_text: str, current_url: str, primary_domain: str) -> set[str]:
    parser = InternalLinkCollector(current_url, primary_domain)
    parser.feed(html_text)
    parser.close()
    return parser.links


def fetch_capture_rows(seed_url: str, *, max_retries: int, retry_backoff_seconds: float) -> list[dict[str, str]]:
    client = cdx_inventory.CdxClient(max_retries=max_retries, retry_backoff_seconds=retry_backoff_seconds)
    rows = client.fetch_query(
        "listing_capture_lookup",
        {
            "url": seed_url,
            "fl": "timestamp,original,statuscode,mimetype",
            "filter": ["statuscode:200", "mimetype:text/html"],
        },
        page_size=100,
        paged=False,
    )
    return [row for row in rows if {"timestamp", "original", "statuscode", "mimetype"} <= row.keys()]


def resolve_candidate_entry(
    url: str,
    inventory_lookup: dict[str, dict[str, str]],
    *,
    primary_domain: str,
    max_retries: int,
    retry_backoff_seconds: float,
) -> tuple[reconstruct_site.SiteEntry | None, str | None]:
    normalized = canonicalize_candidate_url(url)
    inventory_row = inventory_lookup.get(normalized)
    if inventory_row and inventory_row.get("best_statuscode") == "200":
        return (
            reconstruct_site.SiteEntry(
                normalized_url=normalized,
                kind=inventory_row["kind"],
                first_timestamp=inventory_row["first_timestamp"],
                last_timestamp=inventory_row["last_timestamp"],
                capture_count=int(inventory_row["capture_count"]),
                best_timestamp=inventory_row["best_timestamp"],
                best_original=inventory_row["best_original"],
                best_statuscode=inventory_row["best_statuscode"],
                best_mimetype=inventory_row["best_mimetype"],
                best_wayback_url=inventory_row["best_wayback_url"],
            ),
            None,
        )

    direct_entry, direct_error = reconstruct_site.resolve_best_entry(
        normalized,
        from_year=None,
        to_year=None,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    if direct_entry is not None:
        return direct_entry, None

    path = path_from_url(normalized)
    lookup_path = path[:-1] if path.endswith("/") and path != "/" else path
    client = cdx_inventory.CdxClient(max_retries=max_retries, retry_backoff_seconds=retry_backoff_seconds)
    try:
        rows = client.fetch_query(
            "candidate_path_lookup",
            {
                "url": f"{primary_domain}{lookup_path}*",
                "fl": "timestamp,original,statuscode,mimetype",
                "filter": "statuscode:200",
            },
            page_size=50,
            paged=False,
        )
    except (HTTPError, URLError, TimeoutError) as exc:
        return None, str(exc)

    captures = []
    target_path = lookup_path.rstrip("/")
    for row in rows:
        if {"timestamp", "original", "statuscode", "mimetype"} - row.keys():
            continue
        original_normalized = canonicalize_candidate_url(row["original"])
        original_path = path_from_url(original_normalized).rstrip("/")
        if original_path != target_path:
            continue
        captures.append(
            cdx_inventory.CaptureRecord(
                query_id="candidate_path_lookup",
                timestamp=row["timestamp"],
                original=row["original"],
                statuscode=row["statuscode"],
                mimetype=row["mimetype"],
            )
        )
    if not captures:
        return None, direct_error

    captures.sort(key=lambda record: record.timestamp)
    kind = cdx_inventory.classify_url(normalized, captures[-1].mimetype)
    best = cdx_inventory.choose_best_capture(captures, kind)
    return (
        reconstruct_site.SiteEntry(
            normalized_url=normalized,
            kind=kind,
            first_timestamp=captures[0].timestamp,
            last_timestamp=captures[-1].timestamp,
            capture_count=len(captures),
            best_timestamp=best.timestamp,
            best_original=best.original,
            best_statuscode=best.statuscode,
            best_mimetype=best.mimetype,
            best_wayback_url=best.wayback_url,
        ),
        None,
    )


def choose_listing_captures(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen_year_month: set[str] = set()
    for row in sorted(rows, key=lambda item: item["timestamp"], reverse=True):
        stamp = row["timestamp"]
        bucket = stamp[:6]
        if bucket in seen_year_month:
            continue
        seen_year_month.add(bucket)
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def canonical_url_for_relative_path(relative: str, primary_domain: str) -> str:
    if relative == "index.html":
        return f"https://{primary_domain}/"
    if relative.endswith("/index.html"):
        return f"https://{primary_domain}/" + relative.removesuffix("index.html")
    return f"https://{primary_domain}/" + relative


def scan_local_pages_for_links(primary_domain: str) -> set[str]:
    links: set[str] = set()
    for html_path in SITE_DIR.rglob("index.html"):
        relative = html_path.relative_to(SITE_DIR).as_posix()
        if "_assets" in html_path.parts or "recovery" in html_path.parts:
            continue
        if relative.startswith("_recovery/"):
            continue
        current_url = canonical_url_for_relative_path(relative, primary_domain)
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        for link in extract_internal_links(html_text, current_url, primary_domain):
            if is_meaningful_target_url(link, allow_listing_pages=True):
                links.add(link)
    return links


def update_manifest(downloaded: list[dict[str, str]], failed: list[dict[str, str]]) -> None:
    manifest_path = RECOVERY_DIR / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"downloaded": [], "failed": []}

    downloaded_existing = {item.get("path"): item for item in manifest.get("downloaded", []) if item.get("path")}
    for item in downloaded:
        downloaded_existing[item["path"]] = item
    manifest["downloaded"] = sorted(downloaded_existing.values(), key=lambda item: item["path"])
    manifest["downloaded_count"] = len(manifest["downloaded"])

    failed_existing = [item for item in manifest.get("failed", []) if item.get("url") not in {entry["url"] for entry in failed}]
    failed_existing.extend(failed)
    manifest["failed"] = failed_existing
    manifest["failed_count"] = len(failed_existing)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_snippet_block(html_text: str, target_relative_path: str, original_url: str) -> tuple[str, str] | None:
    escaped_relative = re.escape(target_relative_path)
    escaped_original = re.escape(original_url)
    patterns = [
        rf'(<article\b[^>]*>.*?<a[^>]+href="(?:[^"]*{escaped_relative}|{escaped_original})"[^>]*>(.*?)</a>.*?</article>)',
        rf'(<div\b[^>]+class="[^"]*\bpost\b[^"]*"[^>]*>.*?<a[^>]+href="(?:[^"]*{escaped_relative}|{escaped_original})"[^>]*>(.*?)</a>.*?</div>\s*</div>?)',
        rf'(<div\b[^>]+class="[^"]*\bexcerpt\b[^"]*"[^>]*>.*?<a[^>]+href="(?:[^"]*{escaped_relative}|{escaped_original})"[^>]*>(.*?)</a>.*?</div>\s*<!--\s*\.excerpt\s*-->)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        title = re.sub(r"<[^>]+>", " ", match.group(2))
        title = re.sub(r"\s+", " ", html.unescape(title)).strip()
        block = match.group(1)
        content_match = re.search(
            r'<div class="entry-summary">(.*?)</div>|<div class="entry-content">(.*?)</div>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        content_html = content_match.group(1) or content_match.group(2) if content_match else ""
        if content_html:
            content_html = re.sub(r"<script\b.*?</script>", "", content_html, flags=re.IGNORECASE | re.DOTALL)
            content_html = re.sub(r"<form\b.*?</form>", "", content_html, flags=re.IGNORECASE | re.DOTALL)
        if not content_html:
            meta_html = re.sub(r"^.*?</strong>", "", block, count=1, flags=re.IGNORECASE | re.DOTALL)
            meta_html = re.sub(r"</div>\s*<!--\s*\.excerpt\s*-->.*$", "", meta_html, count=1, flags=re.IGNORECASE | re.DOTALL)
            content_html = meta_html.strip()
        return title or "Återfunnen artikel", content_html.strip()
    anchor_match = re.search(
        rf'<a[^>]+href="(?:[^"]*{escaped_relative}|{escaped_original})"[^>]*>(.*?)</a>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not anchor_match:
        return None
    title = re.sub(r"<[^>]+>", " ", anchor_match.group(1))
    title = re.sub(r"\s+", " ", html.unescape(title)).strip()
    tail = html_text[anchor_match.end() : anchor_match.end() + 2500]
    paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", tail, flags=re.IGNORECASE | re.DOTALL)
    cleaned: list[str] = []
    for paragraph in paragraphs[:4]:
        if "#comments" in paragraph or "commentlink" in paragraph or "postmetadata" in paragraph:
            continue
        paragraph = re.sub(r"<script\b.*?</script>", "", paragraph, flags=re.IGNORECASE | re.DOTALL)
        paragraph = re.sub(r"<form\b.*?</form>", "", paragraph, flags=re.IGNORECASE | re.DOTALL)
        if re.sub(r"<[^>]+>", "", paragraph).strip():
            cleaned.append(f"<p>{paragraph.strip()}</p>")
    if not cleaned:
        li_start = html_text.rfind("<li", 0, anchor_match.start())
        li_end = html_text.find("</li>", anchor_match.end())
        if li_start >= 0 and li_end > anchor_match.end():
            list_block = html_text[li_start : li_end + 5]
            list_block = re.sub(r"<script\b.*?</script>", "", list_block, flags=re.IGNORECASE | re.DOTALL)
            list_block = re.sub(r"<form\b.*?</form>", "", list_block, flags=re.IGNORECASE | re.DOTALL)
            if re.sub(r"<[^>]+>", "", list_block).strip():
                cleaned.append(list_block.strip())
    if not cleaned:
        list_items = re.findall(r"<li\b[^>]*>(.*?)</li>", tail, flags=re.IGNORECASE | re.DOTALL)
        for item in list_items[:4]:
            if "#comments" in item or "commentlink" in item or "postmetadata" in item:
                continue
            item = re.sub(r"<script\b.*?</script>", "", item, flags=re.IGNORECASE | re.DOTALL)
            item = re.sub(r"<form\b.*?</form>", "", item, flags=re.IGNORECASE | re.DOTALL)
            if re.sub(r"<[^>]+>", "", item).strip():
                cleaned.append(f"<li>{item.strip()}</li>")
    if cleaned:
        return title or "Återfunnen artikel", "\n".join(cleaned)
    return None


def extract_legacy_or_feed_snippet_block(html_text: str, original_url: str) -> tuple[str, str] | None:
    escaped_original = re.escape(original_url)
    legacy_match = re.search(
        rf'<div class="post">.*?<a[^>]+href="(?:[^"]*{escaped_original})"[^>]*>(.*?)</a>.*?<div class="entry">(.*?)</div>\s*<p class="postmetadata">',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if legacy_match:
        title = re.sub(r"<[^>]+>", " ", legacy_match.group(1))
        title = re.sub(r"\s+", " ", html.unescape(title)).strip()
        content_html = legacy_match.group(2)
        content_html = re.sub(r"<script\b.*?</script>", "", content_html, flags=re.IGNORECASE | re.DOTALL)
        content_html = re.sub(r"<form\b.*?</form>", "", content_html, flags=re.IGNORECASE | re.DOTALL)
        return title or "Ã…terfunnen artikel", content_html.strip()
    feed_match = re.search(
        rf"<entry>.*?<link rel=\"alternate\" type=\"text/html\" href=\"{escaped_original}\" ?/?>.*?<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>.*?<content type=\"html\"[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</content>.*?</entry>",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if feed_match:
        title = re.sub(r"\s+", " ", html.unescape(feed_match.group(1))).strip()
        return title or "Ã…terfunnen artikel", feed_match.group(2).strip()
    return None


def extract_position_based_post_snippet(html_text: str, original_url: str) -> tuple[str, str] | None:
    if original_url not in html_text:
        return None
    anchor_index = html_text.find(original_url)
    if anchor_index < 0:
        return None
    start = html_text.rfind('<div class="post">', 0, anchor_index)
    if start < 0:
        return None
    entry_start_marker = '<div class="entry">'
    entry_start = html_text.find(entry_start_marker, anchor_index)
    if entry_start < 0:
        return None
    entry_start += len(entry_start_marker)
    entry_end = html_text.find('<p class="postmetadata">', entry_start)
    if entry_end < 0:
        return None
    block = html_text[start:entry_end]
    title_match = re.search(r'<h2[^>]*>\s*<a[^>]+>(.*?)</a>\s*</h2>', block, flags=re.IGNORECASE | re.DOTALL)
    if not title_match:
        return None
    title = re.sub(r"<[^>]+>", " ", title_match.group(1))
    title = re.sub(r"\s+", " ", html.unescape(title)).strip()
    content_html = html_text[entry_start:entry_end]
    content_html = re.sub(r"<script\b.*?</script>", "", content_html, flags=re.IGNORECASE | re.DOTALL)
    content_html = re.sub(r"<form\b.*?</form>", "", content_html, flags=re.IGNORECASE | re.DOTALL)
    content_html = content_html.strip()
    if not content_html:
        return None
    return title or "Ãƒâ€¦terfunnen artikel", content_html


def find_local_snippets(target_url: str, primary_domain: str) -> list[dict[str, str]]:
    snippets: list[dict[str, str]] = []
    target_relative_path = relative_path_for_url(target_url)
    candidate_paths = list(SITE_DIR.rglob("index.html")) + list((SITE_DIR / "feed").glob("*.xml")) + list(SITE_DIR.rglob("feed/index.html"))
    seen_paths: set[Path] = set()
    for html_path in candidate_paths:
        if html_path in seen_paths:
            continue
        seen_paths.add(html_path)
        if "_assets" in html_path.parts or "recovery" in html_path.parts:
            continue
        relative = html_path.relative_to(SITE_DIR).as_posix()
        if relative == target_relative_path:
            continue
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        extracted = extract_snippet_block(html_text, target_relative_path, target_url)
        if extracted and not extracted[1]:
            extracted = None
        if not extracted:
            extracted = extract_legacy_or_feed_snippet_block(html_text, target_url)
        if extracted and not extracted[1]:
            extracted = None
        if not extracted:
            extracted = extract_position_based_post_snippet(html_text, target_url)
        if not extracted:
            continue
        title, content_html = extracted
        if not content_html:
            continue
        snippets.append(
            {
                "source_path": relative,
                "source_url": f"https://{primary_domain}/" + relative.removesuffix("index.html"),
                "title": title,
                "content_html": content_html,
            }
        )
    return snippets


def build_stub_page(url: str, snippets: list[dict[str, str]]) -> str:
    title = snippets[0]["title"] if snippets else "Återfunnen artikel"
    sections = []
    for snippet in snippets:
        sections.append(
            f'<section class="recovery-context"><p><strong>Källa:</strong> <a href="../../../../{html.escape(snippet["source_path"])}">{html.escape(snippet["source_path"])}</a></p>{snippet["content_html"]}</section>'
        )
    sections_html = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
</head>
<body class="single post recovery-enhanced">
<div id="page">
<div id="content" role="main">
<article class="post type-post status-publish format-standard hentry">
<header class="entry-header">
<h1 class="entry-title">{html.escape(title)}</h1>
<div class="entry-meta"><span>Rekonstruerad från arkivlistningar</span></div>
</header>
<div class="entry-content">
<p>Den fullständiga artikelsidan kunde inte återfinnas som egen capture i Wayback Machine. Textutdrag nedan är återfunna från arkiv-, kategori- eller startsidor där artikeln listades.</p>
{sections_html}
</div>
</article>
</div>
</div>
</body>
</html>"""


def load_cached_candidates() -> tuple[list[str], int, int]:
    if not CANDIDATES_PATH.exists():
        return [], 0, 0
    payload = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    urls = [canonicalize_candidate_url(url) for url in payload.get("candidate_urls", [])]
    return sorted(dict.fromkeys(urls)), int(payload.get("seed_count", 0) or 0), int(payload.get("listing_candidate_count", 0) or 0)


def main() -> int:
    args = parse_args()
    rows = load_inventory_rows()
    inventory_lookup = {canonicalize_candidate_url(row["normalized_url"]): row for row in rows}
    primary_domain = (urlsplit(rows[0]["normalized_url"]).hostname or "").lower()
    seeds = [cdx_inventory.normalize_url(row["normalized_url"]) for row in rows if is_listing_seed(row)]
    seeds = sorted(dict.fromkeys(seeds))

    client = reconstruct_site.ArchiveClient(max_retries=args.max_retries, retry_backoff_seconds=args.retry_backoff_seconds)
    RECOVERY_DIR.mkdir(parents=True, exist_ok=True)

    listing_scan_results: list[dict[str, object]] = []
    if args.skip_harvest:
        candidate_urls, cached_seed_count, cached_listing_candidate_count = load_cached_candidates()
        seeds = seeds or ["cached"]
        harvested_from_listings = set()
        harvested_from_local_posts = scan_local_pages_for_links(primary_domain)
        candidate_urls = sorted(
            {canonicalize_candidate_url(url) for url in (set(candidate_urls) | harvested_from_local_posts)},
            key=lambda url: (0 if POST_LIKE_RE.match(path_from_url(url)) else 1, url),
        )
        listing_candidate_count = cached_listing_candidate_count
        seed_count = cached_seed_count or len(seeds)
    else:
        harvested_from_listings: set[str] = set()
        for seed in seeds:
            try:
                capture_rows = fetch_capture_rows(seed, max_retries=args.max_retries, retry_backoff_seconds=args.retry_backoff_seconds)
            except (HTTPError, URLError, TimeoutError) as exc:
                listing_scan_results.append({"seed": seed, "status": "capture_lookup_failed", "error": str(exc)})
                continue
            selected_captures = choose_listing_captures(capture_rows, args.max_captures_per_seed)
            capture_reports: list[dict[str, object]] = []
            for row in selected_captures:
                archive_url = reconstruct_site.build_archive_raw_url(row["timestamp"], row["original"])
                try:
                    content, _content_type = client.download(archive_url)
                    html_text = reconstruct_site.decode_html(content)
                    extracted = [
                        link
                        for link in extract_internal_links(html_text, row["original"], primary_domain)
                        if is_meaningful_target_url(link, allow_listing_pages=False)
                    ]
                    harvested_from_listings.update(extracted)
                    capture_reports.append(
                        {
                            "timestamp": row["timestamp"],
                            "original": row["original"],
                            "archive_url": archive_url,
                            "extracted_count": len(extracted),
                        }
                    )
                except (HTTPError, URLError, TimeoutError) as exc:
                    capture_reports.append(
                        {
                            "timestamp": row["timestamp"],
                            "original": row["original"],
                            "archive_url": archive_url,
                            "status": "download_failed",
                            "error": str(exc),
                        }
                    )
            listing_scan_results.append({"seed": seed, "capture_count": len(selected_captures), "captures": capture_reports})

        harvested_from_local_posts = scan_local_pages_for_links(primary_domain)
        candidate_urls = sorted(
            {canonicalize_candidate_url(url) for url in (harvested_from_listings | harvested_from_local_posts)},
            key=lambda url: (0 if POST_LIKE_RE.match(path_from_url(url)) else 1, url),
        )
        CANDIDATES_PATH.write_text(
            json.dumps(
                {
                    "seed_count": len(seeds),
                    "listing_candidate_count": len(harvested_from_listings),
                    "local_link_candidate_count": len(harvested_from_local_posts),
                    "candidate_count": len(candidate_urls),
                    "candidate_urls": candidate_urls,
                    "listing_scans": listing_scan_results,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        listing_candidate_count = len(harvested_from_listings)
        seed_count = len(seeds)

    selected_urls = candidate_urls[args.offset : args.offset + args.limit]
    downloaded: list[dict[str, str]] = []
    failed: list[dict[str, str]] = []
    skipped_existing = 0

    for url in selected_urls:
        relative_path = relative_path_for_url(url)
        destination = SITE_DIR / relative_path
        if destination.exists():
            skipped_existing += 1
            continue

        entry, resolve_error = resolve_candidate_entry(
            url,
            inventory_lookup,
            primary_domain=primary_domain,
            max_retries=args.max_retries,
            retry_backoff_seconds=args.retry_backoff_seconds,
        )
        if entry is None:
            snippets = find_local_snippets(url, primary_domain)
            if snippets:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(build_stub_page(url, snippets), encoding="utf-8")
                downloaded.append(
                    {
                        "url": canonicalize_candidate_url(url),
                        "kind": "post_like",
                        "path": relative_path,
                        "archive_url": "local-snippet-reconstruction",
                    }
                )
                continue
            failed.append({"url": url, "path": relative_path, "status": "resolve_failed", "error": str(resolve_error or "")})
            continue

        archive_url = reconstruct_site.build_archive_raw_url(entry.best_timestamp, entry.best_original)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            content, _content_type = client.download(archive_url)
            destination.write_text(reconstruct_site.decode_html(content), encoding="utf-8")
            downloaded.append(
                {
                    "url": entry.normalized_url,
                    "kind": entry.kind,
                    "path": relative_path,
                    "archive_url": archive_url,
                }
            )
        except (HTTPError, URLError, TimeoutError) as exc:
            failed.append({"url": url, "path": relative_path, "status": "download_failed", "archive_url": archive_url, "error": str(exc)})
        time.sleep(0.1)

    update_manifest(downloaded, failed)

    summary = {
        "seed_count": seed_count,
        "listing_candidate_count": listing_candidate_count,
        "candidate_count": len(candidate_urls),
        "offset": args.offset,
        "limit": args.limit,
        "selected_count": len(selected_urls),
        "downloaded_count": len(downloaded),
        "skipped_existing_count": skipped_existing,
        "failed_count": len(failed),
        "downloaded": downloaded,
        "failed": failed,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
