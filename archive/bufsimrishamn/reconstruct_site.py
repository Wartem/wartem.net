from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import posixpath
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit
from urllib.request import Request, build_opener

import cdx_inventory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from raw_cache import fetch_url_bytes  # type: ignore


ARCHIVE_RAW_BASE = "https://web.archive.org/web"
RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}
HTML_MIME_PREFIXES = ("text/html", "application/xhtml+xml")
XML_MIME_HINTS = ("xml", "rss", "atom")
NOISE_QUERY_KEYS = {"share", "replytocom", "w", "h", "zoom"}
EXCLUDED_PATHS = {"/wp-login.php", "/xmlrpc.php", "/wp-includes/wlwmanifest.xml"}
ASSET_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".avif",
    ".pdf",
    ".mp3",
    ".mp4",
    ".mov",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
}


@dataclass(frozen=True)
class SiteEntry:
    normalized_url: str
    kind: str
    first_timestamp: str
    last_timestamp: str
    capture_count: int
    best_timestamp: str
    best_original: str
    best_statuscode: str
    best_mimetype: str
    best_wayback_url: str

    @property
    def is_html(self) -> bool:
        mime = self.best_mimetype.lower()
        return mime.startswith(HTML_MIME_PREFIXES) or self.kind in {
            "homepage",
            "post_like",
            "category",
            "tag",
            "pagination",
            "other",
        }


@dataclass(frozen=True)
class DownloadedFile:
    entry: SiteEntry
    relative_path: str
    archive_url: str
    status: str
    note: str = ""


class ArchiveClient:
    def __init__(self, cache_root: Path, *, max_retries: int = 5, retry_backoff_seconds: float = 2.0) -> None:
        self.cache_root = cache_root
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.opener = build_opener()

    def download(self, url: str) -> tuple[bytes, str]:
        content = fetch_url_bytes(
            self.cache_root,
            url,
            source="bufsimrishamn/reconstruct_site.py",
            user_agent="site-reconstructor/1.0",
            max_retries=self.max_retries,
            retry_backoff_seconds=self.retry_backoff_seconds,
            retryable_statuses=RETRYABLE_HTTP_STATUSES,
            opener=self.opener,
        )
        return content, mimetypes.guess_type(url)[0] or "application/octet-stream"


def build_archive_raw_url(timestamp: str, original: str) -> str:
    return f"{ARCHIVE_RAW_BASE}/{timestamp}id_/{original}"


def load_unique_records(path: Path) -> list[SiteEntry]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        records = []
        for row in reader:
            records.append(
                SiteEntry(
                    normalized_url=row["normalized_url"],
                    kind=row["kind"],
                    first_timestamp=row["first_timestamp"],
                    last_timestamp=row["last_timestamp"],
                    capture_count=int(row["capture_count"]),
                    best_timestamp=row["best_timestamp"],
                    best_original=row.get("best_original") or row["normalized_url"],
                    best_statuscode=row["best_statuscode"],
                    best_mimetype=row["best_mimetype"],
                    best_wayback_url=row["best_wayback_url"],
                )
            )
        return records


def is_noise_entry(entry: SiteEntry) -> bool:
    parts = urlsplit(entry.normalized_url)
    if parts.path in EXCLUDED_PATHS or parts.path.startswith("/wp-admin/"):
        return True

    query_keys = {key for key, _ in parse_qsl(parts.query, keep_blank_values=True)}
    if query_keys and query_keys.issubset(NOISE_QUERY_KEYS):
        return True

    if entry.best_statuscode != "200":
        return True

    return False


def slugify_query(query: str) -> str:
    return hashlib.sha1(query.encode("utf-8")).hexdigest()[:10]


def guess_extension(entry: SiteEntry) -> str:
    mime = entry.best_mimetype.lower()
    if entry.is_html:
        return ".html"
    if any(hint in mime for hint in XML_MIME_HINTS):
        return ".xml"
    guessed, _ = mimetypes.guess_type(entry.normalized_url)
    extension = PurePosixPath(urlsplit(entry.normalized_url).path).suffix
    if extension:
        return extension
    if guessed == "application/json" or "json" in mime:
        return ".json"
    if mime.startswith("text/"):
        return ".txt"
    return ""


def entry_relative_path(entry: SiteEntry, primary_domain: str | None = None) -> str:
    parts = urlsplit(entry.normalized_url)
    hostname = (parts.hostname or "").lower()
    path = parts.path or "/"
    suffix = PurePosixPath(path).suffix
    query_suffix = f"--{slugify_query(parts.query)}" if parts.query else ""
    base_prefix = PurePosixPath()
    if primary_domain and hostname and hostname != primary_domain:
        base_prefix = PurePosixPath("_assets") / hostname

    if entry.kind == "homepage":
        filename = f"index{query_suffix}.html" if query_suffix else "index.html"
        return str(base_prefix / filename)

    if entry.is_html:
        if path.endswith("/"):
            base = PurePosixPath(path.lstrip("/"))
            return str(base_prefix / base / f"index{query_suffix}.html")
        if suffix:
            base = PurePosixPath(path.lstrip("/"))
            stem = base.stem + query_suffix
            return str(base_prefix / base.with_name(stem + ".html"))
        return str(base_prefix / PurePosixPath(path.lstrip("/")) / f"index{query_suffix}.html")

    base = PurePosixPath(path.lstrip("/"))
    if suffix:
        stem = base.stem + query_suffix
        return str(base_prefix / base.with_name(stem + base.suffix))
    extension = guess_extension(entry)
    filename = base.name + query_suffix + extension
    return str(base_prefix / base.with_name(filename))


def make_aliases(entry: SiteEntry) -> set[str]:
    normalized = cdx_inventory.normalize_url(entry.normalized_url)
    parts = urlsplit(normalized)
    aliases = {normalized}
    if parts.hostname:
        aliases.add(cdx_inventory.normalize_url(normalized.replace("https://", "http://", 1)))
        aliases.add(cdx_inventory.normalize_url(normalized.replace("http://", "https://", 1)))
    return aliases


def decode_html(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def default_files_domain(primary_domain: str) -> str:
    site_prefix = primary_domain.split(".", 1)[0]
    return f"{site_prefix}.files.wordpress.com"


def extract_asset_urls(
    html_text: str,
    current_url: str,
    primary_domain: str,
    *,
    extra_asset_hosts: Iterable[str] | None = None,
    files_domain: str | None = None,
    primary_media_path_prefixes: Iterable[str] | None = None,
) -> set[str]:
    asset_urls: set[str] = set()
    parser = HTMLAssetCollector(
        current_url,
        primary_domain,
        files_domain or default_files_domain(primary_domain),
        extra_asset_hosts=extra_asset_hosts,
        primary_media_path_prefixes=primary_media_path_prefixes,
    )
    parser.feed(html_text)
    parser.close()
    return parser.urls


def rewrite_srcset(value: str, current_url: str, current_relative_path: str, link_map: dict[str, str]) -> str:
    rewritten_parts: list[str] = []
    for item in value.split(","):
        candidate = item.strip()
        if not candidate:
            continue
        url_part, *descriptor = candidate.split()
        rewritten_url = rewrite_single_url(url_part, current_url, current_relative_path, link_map)
        if descriptor:
            rewritten_parts.append(" ".join([rewritten_url, *descriptor]))
        else:
            rewritten_parts.append(rewritten_url)
    return ", ".join(rewritten_parts)


def rewrite_single_url(value: str, current_url: str, current_relative_path: str, link_map: dict[str, str]) -> str:
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return value

    resolved = urljoin(current_url, value)
    normalized = cdx_inventory.normalize_url(resolved)
    if normalized not in link_map:
        return value

    target_relative_path = link_map[normalized]
    current_parent = PurePosixPath(current_relative_path).parent
    relative = posixpath.relpath(target_relative_path, start=str(current_parent) or ".")
    return relative.replace("\\", "/")


class HtmlLinkRewriter(HTMLParser):
    URL_ATTRIBUTES = {"href", "src", "action", "poster", "data-src", "data-large-file", "data-orig-file"}
    BACKUP_ATTRIBUTES = {"src", "data-src", "poster", "data-large-file", "data-orig-file", "srcset"}
    LOCAL_FALLBACK_JS = (
        "this.onerror=null;"
        "if(this.dataset.localSrc){"
        "this.removeAttribute('srcset');"
        "this.src=this.dataset.localSrc;"
        "}"
    )

    def __init__(self, current_url: str, current_relative_path: str, link_map: dict[str, str]) -> None:
        super().__init__(convert_charrefs=False)
        self.current_url = current_url
        self.current_relative_path = current_relative_path
        self.link_map = link_map
        self.output: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        self.output.append(self._render_tag(tag, attrs, closing=">"))

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.output.append(self._render_tag(tag, attrs, closing=" />"))

    def handle_endtag(self, tag: str) -> None:
        self.output.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.output.append(data)

    def handle_comment(self, data: str) -> None:
        self.output.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.output.append(f"<!{decl}>")

    def handle_entityref(self, name: str) -> None:
        self.output.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.output.append(f"&#{name};")

    def handle_pi(self, data: str) -> None:
        self.output.append(f"<?{data}>")

    def rewritten_html(self) -> str:
        return "".join(self.output)

    def _render_tag(self, tag: str, attrs, *, closing: str) -> str:
        parts = [f"<{tag}"]
        attribute_lookup = {name.lower(): value for name, value in attrs}
        backup_attributes: list[tuple[str, str]] = []
        fallback_enabled = False
        for name, value in attrs:
            if value is None:
                parts.append(f" {name}")
                continue
            rewritten = value
            lower_name = name.lower()
            if lower_name in self.URL_ATTRIBUTES:
                rewritten = rewrite_single_url(value, self.current_url, self.current_relative_path, self.link_map)
            elif lower_name == "srcset":
                rewritten = rewrite_srcset(value, self.current_url, self.current_relative_path, self.link_map)
            elif lower_name == "content" and tag.lower() == "meta":
                if attribute_lookup.get("property", "").lower() in {"og:image", "og:url"}:
                    rewritten = rewrite_single_url(value, self.current_url, self.current_relative_path, self.link_map)
            if tag.lower() == "img":
                original_backup = attribute_lookup.get(f"data-original-{lower_name}")
                if lower_name in {"src", "srcset"} and original_backup and original_backup.startswith(("http://", "https://")):
                    if rewritten != original_backup:
                        if f"data-local-{lower_name}" not in attribute_lookup:
                            backup_attributes.append((f"data-local-{lower_name}", rewritten))
                        rewritten = original_backup
                        fallback_enabled = fallback_enabled or lower_name == "src"
                elif lower_name == "src" and rewritten != value and value.startswith(("http://", "https://")):
                    if "data-local-src" not in attribute_lookup:
                        backup_attributes.append(("data-local-src", rewritten))
                    rewritten = value
                    fallback_enabled = True
                elif lower_name == "srcset" and rewritten != value and value.startswith(("http://", "https://")):
                    if "data-local-srcset" not in attribute_lookup:
                        backup_attributes.append(("data-local-srcset", rewritten))
                    rewritten = value
            parts.append(f' {name}="{escape(rewritten, quote=True)}"')
            if (
                lower_name in self.BACKUP_ATTRIBUTES
                and rewritten != value
                and value.startswith(("http://", "https://"))
                and f"data-original-{lower_name}" not in attribute_lookup
            ):
                backup_attributes.append((f"data-original-{lower_name}", value))
        if tag.lower() == "img" and fallback_enabled and "onerror" not in attribute_lookup:
            parts.append(f' onerror="{escape(self.LOCAL_FALLBACK_JS, quote=True)}"')
        for name, value in backup_attributes:
            parts.append(f' {name}="{escape(value, quote=True)}"')
        parts.append(closing)
        return "".join(parts)


class HTMLAssetCollector(HTMLParser):
    URL_ATTRIBUTES = {"href", "src", "action", "poster", "data-src", "data-large-file", "data-orig-file", "srcset"}

    def __init__(
        self,
        current_url: str,
        primary_domain: str,
        files_domain: str,
        *,
        extra_asset_hosts: Iterable[str] | None = None,
        primary_media_path_prefixes: Iterable[str] | None = None,
    ) -> None:
        super().__init__(convert_charrefs=False)
        self.current_url = current_url
        self.primary_domain = primary_domain
        self.files_domain = files_domain
        self.extra_asset_hosts = {(host or "").lower() for host in (extra_asset_hosts or []) if host}
        prefixes = tuple(primary_media_path_prefixes or ("/wp-content/",))
        self.primary_media_path_prefixes = tuple(prefix.lower() for prefix in prefixes if prefix)
        self.urls: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        self._collect(attrs)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self._collect(attrs)

    def _collect(self, attrs) -> None:
        for name, value in attrs:
            if not value:
                continue
            if name.lower() == "srcset":
                for item in value.split(","):
                    candidate = item.strip().split()[0]
                    self._maybe_add(candidate)
            elif name.lower() in self.URL_ATTRIBUTES:
                self._maybe_add(value)

    def _maybe_add(self, value: str) -> None:
        if value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            return
        resolved = urljoin(self.current_url, value)
        parts = urlsplit(resolved)
        host = (parts.hostname or "").lower()
        allowed_hosts = {self.primary_domain, self.files_domain, *self.extra_asset_hosts}
        if host not in allowed_hosts:
            return
        if host == self.primary_domain and self.primary_media_path_prefixes:
            if not any(parts.path.lower().startswith(prefix) for prefix in self.primary_media_path_prefixes):
                return
        if host == self.primary_domain and not self.primary_media_path_prefixes:
            if PurePosixPath(parts.path).suffix.lower() not in ASSET_EXTENSIONS:
                return
        if host in self.extra_asset_hosts and PurePosixPath(parts.path).suffix.lower() not in ASSET_EXTENSIONS:
            return
        if PurePosixPath(parts.path).suffix.lower() not in ASSET_EXTENSIONS and host != self.files_domain:
            return
        self.urls.add(resolved)


def rewrite_html(html_text: str, current_url: str, current_relative_path: str, link_map: dict[str, str]) -> str:
    parser = HtmlLinkRewriter(current_url, current_relative_path, link_map)
    parser.feed(html_text)
    parser.close()
    return parser.rewritten_html()


def ensure_inventory(
    *,
    domain: str,
    inventory_dir: Path,
    from_year: int | None,
    to_year: int | None,
    scope: str,
    page_size: int,
    sleep_seconds: float,
    max_retries: int,
    retry_backoff_seconds: float,
) -> None:
    definitions = cdx_inventory.build_query_definitions(domain, scope, from_year, to_year)
    client = cdx_inventory.CdxClient(
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    query_results = cdx_inventory.fetch_all_queries(
        client,
        definitions,
        page_size=page_size,
        sleep_seconds=sleep_seconds,
    )
    captures = cdx_inventory.collect_capture_records(query_results)
    unique = cdx_inventory.build_unique_records(captures)
    summary = cdx_inventory.build_summary(query_results, captures, unique)
    inventory_dir.mkdir(parents=True, exist_ok=True)
    cdx_inventory.write_captures_csv(inventory_dir / "captures_raw.csv", captures)
    cdx_inventory.write_unique_csv(inventory_dir / "urls_unique.csv", unique)
    cdx_inventory.write_summary_json(inventory_dir / "summary.json", summary)


def should_skip_url_before_lookup(original_url: str) -> bool:
    normalized = cdx_inventory.normalize_url(original_url)
    parts = urlsplit(normalized)
    if parts.path in EXCLUDED_PATHS or parts.path.startswith("/wp-admin/"):
        return True
    query_keys = {key for key, _ in parse_qsl(parts.query, keep_blank_values=True)}
    return bool(query_keys and query_keys.issubset(NOISE_QUERY_KEYS))


def fetch_unique_originals(
    *,
    domain: str,
    from_year: int | None,
    to_year: int | None,
    max_retries: int,
    retry_backoff_seconds: float,
) -> list[str]:
    client = cdx_inventory.CdxClient(
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    params: dict[str, str | list[str]] = {"url": f"*.{domain}/*", "fl": "original", "collapse": "urlkey"}
    if from_year is not None:
        params["from"] = str(from_year)
    if to_year is not None:
        params["to"] = str(to_year)
    rows = client.fetch_query("unique_domain", params, paged=False)
    originals = sorted({row["original"] for row in rows if row.get("original") and not should_skip_url_before_lookup(row["original"])})
    return originals


def resolve_best_entry(
    original_url: str,
    *,
    from_year: int | None,
    to_year: int | None,
    max_retries: int,
    retry_backoff_seconds: float,
) -> tuple[SiteEntry | None, str | None]:
    client = cdx_inventory.CdxClient(
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    params: dict[str, str | list[str]] = {
        "url": original_url,
        "fl": "timestamp,original,statuscode,mimetype",
        "filter": "statuscode:200",
    }
    if from_year is not None:
        params["from"] = str(from_year)
    if to_year is not None:
        params["to"] = str(to_year)

    try:
        rows = client.fetch_query("best_capture_lookup", params, page_size=50, paged=False)
    except (HTTPError, URLError, TimeoutError) as exc:
        return None, f"{original_url}: {exc}"

    captures = [
        cdx_inventory.CaptureRecord(
            query_id="best_capture_lookup",
            timestamp=row["timestamp"],
            original=row["original"],
            statuscode=row["statuscode"],
            mimetype=row["mimetype"],
        )
        for row in rows
        if {"timestamp", "original", "statuscode", "mimetype"} <= row.keys()
    ]
    if not captures:
        return None, None

    normalized_url = cdx_inventory.normalize_url(original_url)
    captures.sort(key=lambda record: record.timestamp)
    kind = cdx_inventory.classify_url(normalized_url, captures[-1].mimetype)
    best = cdx_inventory.choose_best_capture(captures, kind)
    return (
        SiteEntry(
            normalized_url=normalized_url,
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


def refresh_inventory_url_first(
    *,
    domain: str,
    inventory_dir: Path,
    from_year: int | None,
    to_year: int | None,
    max_retries: int,
    retry_backoff_seconds: float,
    workers: int,
) -> None:
    originals = fetch_unique_originals(
        domain=domain,
        from_year=from_year,
        to_year=to_year,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    entries: list[SiteEntry] = []
    failed: list[dict[str, str]] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {
            executor.submit(
                resolve_best_entry,
                original,
                from_year=from_year,
                to_year=to_year,
                max_retries=max_retries,
                retry_backoff_seconds=retry_backoff_seconds,
            ): original
            for original in originals
        }
        for future in as_completed(future_map):
            entry, error = future.result()
            if entry is not None:
                entries.append(entry)
            elif error:
                failed.append({"url": future_map[future], "error": error})

    entries.sort(key=lambda entry: entry.normalized_url)
    captures = [
        cdx_inventory.CaptureRecord(
            query_id="best_capture_lookup",
            timestamp=entry.best_timestamp,
            original=entry.best_original,
            statuscode=entry.best_statuscode,
            mimetype=entry.best_mimetype,
        )
        for entry in entries
    ]
    unique_records = [
        cdx_inventory.UniqueUrlRecord(
            normalized_url=entry.normalized_url,
            kind=entry.kind,
            first_timestamp=entry.first_timestamp,
            last_timestamp=entry.last_timestamp,
            capture_count=entry.capture_count,
            best_timestamp=entry.best_timestamp,
            best_original=entry.best_original,
            best_statuscode=entry.best_statuscode,
            best_mimetype=entry.best_mimetype,
            best_wayback_url=entry.best_wayback_url,
        )
        for entry in entries
    ]
    summary = {
        "mode": "url-first-best-capture",
        "unique_url_count": len(unique_records),
        "capture_count": len(captures),
        "failed_best_capture_lookups": failed,
        "kind_counts": dict(sorted(Counter(entry.kind for entry in entries).items())),
    }

    inventory_dir.mkdir(parents=True, exist_ok=True)
    cdx_inventory.write_captures_csv(inventory_dir / "captures_raw.csv", captures)
    cdx_inventory.write_unique_csv(inventory_dir / "urls_unique.csv", unique_records)
    cdx_inventory.write_summary_json(inventory_dir / "summary.json", summary)


def write_recovery_index(site_dir: Path, manifest: dict[str, object]) -> None:
    recovery_dir = site_dir / "recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)
    (recovery_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    html = [
        "<!doctype html>",
        "<html lang=\"sv\">",
        "<head><meta charset=\"utf-8\"><title>Återställningsrapport</title></head>",
        "<body>",
        "<h1>Återställningsrapport</h1>",
        f"<p>Nedladdade filer: {manifest['downloaded_count']}</p>",
        f"<p>Hoppade över: {manifest['skipped_count']}</p>",
        f"<p>Misslyckade: {manifest['failed_count']}</p>",
        "<p>Detaljer finns i <code>recovery/manifest.json</code>.</p>",
        "</body></html>",
    ]
    (recovery_dir / "index.html").write_text("".join(html), encoding="utf-8")


def reconstruct_site(
    entries: Iterable[SiteEntry],
    *,
    domain: str,
    site_dir: Path,
    extra_asset_hosts: Iterable[str] | None = None,
    primary_media_path_prefixes: Iterable[str] | None = None,
    skip_asset_pass: bool = False,
    max_retries: int,
    retry_backoff_seconds: float,
    sleep_seconds: float,
    workers: int,
) -> dict[str, object]:
    site_dir.mkdir(parents=True, exist_ok=True)
    included_entries = [entry for entry in entries if not is_noise_entry(entry)]
    link_map: dict[str, str] = {}
    for entry in included_entries:
        relative_path = entry_relative_path(entry, primary_domain=domain)
        for alias in make_aliases(entry):
            link_map[alias] = relative_path

    downloaded: list[DownloadedFile] = []
    failed: list[dict[str, str]] = []
    skipped = [
        {"url": entry.normalized_url, "reason": "noise-or-non-200"}
        for entry in entries
        if is_noise_entry(entry)
    ]
    html_files: list[tuple[Path, SiteEntry, str]] = []

    def download_entry(entry: SiteEntry) -> tuple[SiteEntry, str, bytes | None, str | None, str | None]:
        archive_url = build_archive_raw_url(entry.best_timestamp, entry.best_original)
        relative_path = entry_relative_path(entry, primary_domain=domain)
        client = ArchiveClient(site_root, max_retries=max_retries, retry_backoff_seconds=retry_backoff_seconds)
        try:
            content, response_mime = client.download(archive_url)
            return entry, relative_path, content, response_mime, None
        except (HTTPError, URLError, TimeoutError) as exc:
            return entry, relative_path, None, None, str(exc)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_map = {executor.submit(download_entry, entry): entry for entry in included_entries}
        for future in as_completed(future_map):
            entry, relative_path, content, response_mime, error = future.result()
            archive_url = build_archive_raw_url(entry.best_timestamp, entry.best_original)
            destination = site_dir / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if error:
                failed.append({"url": entry.normalized_url, "archive_url": archive_url, "error": error})
                continue
            assert content is not None
            if entry.is_html or (response_mime or "").startswith(HTML_MIME_PREFIXES):
                html_files.append((destination, entry, decode_html(content)))
            else:
                destination.write_bytes(content)
            downloaded.append(DownloadedFile(entry=entry, relative_path=relative_path, archive_url=archive_url, status="downloaded"))
            if sleep_seconds:
                time.sleep(sleep_seconds)

    if not skip_asset_pass:
        asset_urls: set[str] = set()
        for _, entry, html_text in html_files:
            asset_urls.update(
                extract_asset_urls(
                    html_text,
                    entry.best_original,
                    domain,
                    extra_asset_hosts=extra_asset_hosts,
                    primary_media_path_prefixes=primary_media_path_prefixes,
                )
            )

        asset_entries: list[SiteEntry] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    resolve_best_entry,
                    asset_url,
                    from_year=None,
                    to_year=None,
                    max_retries=max_retries,
                    retry_backoff_seconds=retry_backoff_seconds,
                ): asset_url
                for asset_url in sorted(asset_urls)
                if cdx_inventory.normalize_url(asset_url) not in link_map
            }
            for future in as_completed(future_map):
                entry, error = future.result()
                if entry is not None:
                    asset_entries.append(entry)
                elif error:
                    failed.append({"url": future_map[future], "archive_url": "", "error": error})

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {executor.submit(download_entry, entry): entry for entry in asset_entries}
            for future in as_completed(future_map):
                entry, relative_path, content, _, error = future.result()
                archive_url = build_archive_raw_url(entry.best_timestamp, entry.best_original)
                destination = site_dir / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                if error:
                    failed.append({"url": entry.normalized_url, "archive_url": archive_url, "error": error})
                    continue
                assert content is not None
                destination.write_bytes(content)
                for alias in make_aliases(entry):
                    link_map[alias] = relative_path
                downloaded.append(DownloadedFile(entry=entry, relative_path=relative_path, archive_url=archive_url, status="downloaded"))

    for destination, entry, html_text in html_files:
        rewritten = rewrite_html(html_text, entry.best_original, entry_relative_path(entry, primary_domain=domain), link_map)
        destination.write_text(rewritten, encoding="utf-8")

    manifest = {
        "downloaded_count": len(downloaded),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "downloaded": [
            {
                "url": item.entry.normalized_url,
                "kind": item.entry.kind,
                "path": item.relative_path,
                "archive_url": item.archive_url,
            }
            for item in downloaded
        ],
        "skipped": skipped,
        "failed": failed,
    }
    write_recovery_index(site_dir, manifest)
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download archived captures and reconstruct a static site from the best archived version per URL."
    )
    parser.add_argument("--domain", default="bufsimrishamn.wordpress.com")
    parser.add_argument("--inventory-dir", default="out", help="Directory containing or receiving inventory CSV/JSON files.")
    parser.add_argument("--site-dir", default="site", help="Directory for reconstructed site output.")
    parser.add_argument("--scope", default="all-public")
    parser.add_argument("--from-year", type=int)
    parser.add_argument("--to-year", type=int)
    parser.add_argument("--page-size", type=int, default=250)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-backoff-seconds", type=float, default=3.0)
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers for capture lookup and downloads.")
    parser.add_argument(
        "--asset-host",
        action="append",
        dest="asset_hosts",
        help="Optional extra asset hostname to keep when rewriting or downloading media, for example blogger.googleusercontent.com.",
    )
    parser.add_argument(
        "--primary-media-path",
        action="append",
        dest="primary_media_paths",
        help="Optional allowed path prefix on the primary domain for media URLs. Repeat to allow multiple prefixes. Default is /wp-content/.",
    )
    parser.add_argument("--skip-asset-pass", action="store_true", help="Skip asset lookup and asset downloads to prioritize fast HTML reconstruction.")
    parser.add_argument("--refresh-inventory", action="store_true", help="Refetch CDX inventory before reconstruction.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    inventory_dir = Path(args.inventory_dir)
    site_dir = Path(args.site_dir)
    inventory_path = inventory_dir / "urls_unique.csv"

    try:
        if args.refresh_inventory or not inventory_path.exists():
            refresh_inventory_url_first(
                domain=args.domain,
                inventory_dir=inventory_dir,
                from_year=args.from_year,
                to_year=args.to_year,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
                workers=args.workers,
            )

        entries = load_unique_records(inventory_path)
        reconstruct_site(
            entries,
            domain=args.domain,
            site_dir=site_dir,
            extra_asset_hosts=args.asset_hosts,
            primary_media_path_prefixes=args.primary_media_paths,
            skip_asset_pass=args.skip_asset_pass,
            max_retries=args.max_retries,
            retry_backoff_seconds=args.retry_backoff_seconds,
            sleep_seconds=args.sleep_seconds,
            workers=args.workers,
        )
    except (RuntimeError, ValueError, HTTPError, URLError, TimeoutError) as exc:
        print(f"Site reconstruction failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
