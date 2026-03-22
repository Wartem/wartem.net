from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from raw_cache import fetch_url_bytes  # type: ignore


CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
WAYBACK_BASE = "https://web.archive.org/web"
DEFAULT_PAGE_SIZE = 1000
RETRYABLE_HTTP_STATUSES = {429, 500, 502, 503, 504}
POST_LIKE_RE = re.compile(r"^/\d{4}/\d{2}/\d{2}/[^/]+/?$")
MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".avif",
    ".mp3",
    ".m4a",
    ".wav",
    ".ogg",
    ".mp4",
    ".mov",
    ".avi",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
    ".rar",
    ".7z",
}


@dataclass(frozen=True)
class CaptureRecord:
    query_id: str
    timestamp: str
    original: str
    statuscode: str
    mimetype: str

    @property
    def wayback_url(self) -> str:
        return build_wayback_url(self.timestamp, self.original)


@dataclass(frozen=True)
class UniqueUrlRecord:
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


@dataclass(frozen=True)
class QueryDefinition:
    query_id: str
    params: dict[str, str | list[str]]
    paged: bool = True


class CdxClient:
    def __init__(
        self,
        cache_root: Path,
        endpoint: str = CDX_ENDPOINT,
        user_agent: str = "cdx-inventory/1.0",
        *,
        max_retries: int = 5,
        retry_backoff_seconds: float = 2.0,
    ) -> None:
        self.cache_root = cache_root
        self.endpoint = endpoint
        self.user_agent = user_agent
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.opener = build_opener()

    def fetch_query(
        self,
        query_id: str,
        params: dict[str, str | list[str]],
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
        sleep_seconds: float = 0.0,
        paged: bool = True,
    ) -> list[dict[str, str]]:
        base_params = dict(params)
        base_params.setdefault("output", "json")
        if paged:
            base_params.setdefault("showResumeKey", "true")
            base_params.setdefault("limit", str(page_size))
        rows: list[dict[str, str]] = []
        resume_key: str | None = None

        while True:
            page_params = dict(base_params)
            if paged and resume_key:
                page_params["resumeKey"] = resume_key

            payload = self._request(page_params)
            page_rows, next_resume_key = parse_cdx_json(payload)
            rows.extend(page_rows)

            if not paged or not next_resume_key:
                break

            resume_key = next_resume_key
            if sleep_seconds:
                time.sleep(sleep_seconds)

        return rows

    def _request(self, params: dict[str, str | list[str]]) -> bytes:
        url = f"{self.endpoint}?{urlencode(params, doseq=True)}"
        return fetch_url_bytes(
            self.cache_root,
            url,
            source="bufsimrishamn/cdx_inventory.py",
            user_agent=self.user_agent,
            max_retries=self.max_retries,
            retry_backoff_seconds=self.retry_backoff_seconds,
            retryable_statuses=RETRYABLE_HTTP_STATUSES,
            opener=self.opener,
            suffix=".json",
        )


def parse_cdx_json(payload: bytes | str) -> tuple[list[dict[str, str]], str | None]:
    if isinstance(payload, bytes):
        text = payload.decode("utf-8")
    else:
        text = payload

    parsed = json.loads(text)
    if not parsed:
        return [], None

    header = parsed[0]
    if not isinstance(header, list):
        raise ValueError("CDX JSON payload missing header row")

    rows: list[dict[str, str]] = []
    resume_key: str | None = None

    for item in parsed[1:]:
        if item == []:
            continue
        if not isinstance(item, list):
            raise ValueError(f"Unexpected CDX row shape: {item!r}")
        if len(item) == len(header):
            row = {str(key): str(value) for key, value in zip(header, item)}
            rows.append(row)
            continue
        if len(item) == 1 and isinstance(item[0], str):
            resume_key = item[0]
            continue
        row = {str(key): str(value) for key, value in zip(header, item)}
        rows.append(row)

    return rows, resume_key


def build_wayback_url(timestamp: str, original: str) -> str:
    return f"{WAYBACK_BASE}/{timestamp}/{original}"


def normalize_url(original: str) -> str:
    parts = urlsplit(original)
    scheme = parts.scheme.lower() if parts.scheme else "https"
    hostname = (parts.hostname or "").lower()
    port = parts.port
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def classify_url(normalized_url: str, mimetype: str = "") -> str:
    parts = urlsplit(normalized_url)
    path = parts.path or "/"

    if path == "/":
        return "homepage"
    if path.startswith("/category/"):
        return "category"
    if path.startswith("/tag/"):
        return "tag"
    if path.endswith("/feed/") or path == "/feed/" or path.startswith("/feed/"):
        return "feed"
    if path.startswith("/page/"):
        return "pagination"
    if POST_LIKE_RE.match(path):
        return "post_like"

    mime = mimetype.lower()
    extension = Path(path).suffix.lower()
    guessed_mime, _ = mimetypes.guess_type(path)
    if mime and not mime.startswith("text/html"):
        if mime.startswith(("image/", "audio/", "video/", "application/pdf")):
            return "media"
    if extension in MEDIA_EXTENSIONS:
        return "media"
    if guessed_mime and guessed_mime.startswith(("image/", "audio/", "video/")):
        return "media"
    return "other"


def choose_best_capture(records: list[CaptureRecord], kind: str) -> CaptureRecord:
    preferred: list[CaptureRecord] = []
    if kind == "media":
        preferred = [r for r in records if r.statuscode == "200"]
    else:
        preferred = [r for r in records if r.statuscode == "200" and r.mimetype.lower() == "text/html"]

    pool = preferred or [r for r in records if r.statuscode == "200"] or records
    return max(pool, key=lambda record: record.timestamp)


def dedupe_captures(records: Iterable[CaptureRecord]) -> list[CaptureRecord]:
    seen: set[tuple[str, str, str, str]] = set()
    deduped: list[CaptureRecord] = []
    for record in sorted(records, key=lambda r: (r.timestamp, r.original, r.statuscode, r.mimetype, r.query_id)):
        key = (record.timestamp, record.original, record.statuscode, record.mimetype)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def build_unique_records(records: Iterable[CaptureRecord]) -> list[UniqueUrlRecord]:
    grouped: dict[str, list[CaptureRecord]] = defaultdict(list)
    for record in records:
        grouped[normalize_url(record.original)].append(record)

    unique_records: list[UniqueUrlRecord] = []
    for normalized_url, group in sorted(grouped.items()):
        group.sort(key=lambda r: r.timestamp)
        kind = infer_group_kind(normalized_url, group)
        best = choose_best_capture(group, kind)
        unique_records.append(
            UniqueUrlRecord(
                normalized_url=normalized_url,
                kind=kind,
                first_timestamp=group[0].timestamp,
                last_timestamp=group[-1].timestamp,
                capture_count=len(group),
                best_timestamp=best.timestamp,
                best_original=best.original,
                best_statuscode=best.statuscode,
                best_mimetype=best.mimetype,
                best_wayback_url=best.wayback_url,
            )
        )
    return unique_records


def infer_group_kind(normalized_url: str, group: list[CaptureRecord]) -> str:
    if group:
        ranked = Counter(classify_url(normalized_url, record.mimetype) for record in group)
        return ranked.most_common(1)[0][0]
    return classify_url(normalized_url)


def build_summary(
    query_results: dict[str, list[dict[str, str]]],
    raw_records: list[CaptureRecord],
    unique_records: list[UniqueUrlRecord],
) -> dict[str, Any]:
    status_counts = Counter(record.statuscode for record in raw_records)
    mimetype_counts = Counter(record.mimetype for record in raw_records)
    kind_counts = Counter(record.kind for record in unique_records)

    return {
        "query_counts": {query_id: len(rows) for query_id, rows in sorted(query_results.items())},
        "statuscode_counts": dict(sorted(status_counts.items())),
        "mimetype_counts": dict(sorted(mimetype_counts.items())),
        "kind_counts": dict(sorted(kind_counts.items())),
        "unique_url_count": len(unique_records),
        "capture_count": len(raw_records),
    }


def build_query_definitions(domain: str, scope: str, from_year: int | None, to_year: int | None) -> list[QueryDefinition]:
    if scope != "all-public":
        raise ValueError(f"Unsupported scope preset: {scope}")

    year_filters: dict[str, str] = {}
    if from_year is not None:
        year_filters["from"] = str(from_year)
    if to_year is not None:
        year_filters["to"] = str(to_year)

    base_definitions = [
        QueryDefinition("raw_prefix_root", {"url": f"{domain}/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition("raw_http_prefix", {"url": f"http://{domain}/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition("raw_https_prefix", {"url": f"https://{domain}/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition("raw_www_prefix", {"url": f"www.{domain}/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition(
            "raw_domain_match",
            {"url": f"*.{domain}/", "matchType": "domain", "fl": "timestamp,original,statuscode,mimetype"},
        ),
        QueryDefinition(
            "wp_posts_prefix",
            {"url": f"{domain}/20*", "matchType": "prefix", "fl": "timestamp,original,statuscode,mimetype"},
        ),
        QueryDefinition("wp_category_prefix", {"url": f"{domain}/category/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition("wp_tag_prefix", {"url": f"{domain}/tag/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition("wp_feed_prefix", {"url": f"{domain}/feed/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition("wp_page_prefix", {"url": f"{domain}/page/*", "fl": "timestamp,original,statuscode,mimetype"}),
        QueryDefinition(
            "html_200_root",
            {
                "url": f"{domain}/*",
                "fl": "timestamp,original,statuscode,mimetype",
                "filter": ["statuscode:200", "mimetype:text/html"],
            },
        ),
        QueryDefinition(
            "unique_domain",
            {"url": f"*.{domain}/*", "fl": "original", "collapse": "urlkey"},
            paged=False,
        ),
    ]

    definitions: list[QueryDefinition] = []
    for definition in base_definitions:
        params = dict(definition.params)
        params.update(year_filters)
        definitions.append(QueryDefinition(definition.query_id, params, definition.paged))
    return definitions


def fetch_all_queries(
    client: CdxClient,
    definitions: Iterable[QueryDefinition],
    *,
    page_size: int,
    sleep_seconds: float,
) -> dict[str, list[dict[str, str]]]:
    results: dict[str, list[dict[str, str]]] = {}
    for definition in definitions:
        try:
            results[definition.query_id] = client.fetch_query(
                definition.query_id,
                definition.params,
                page_size=page_size,
                sleep_seconds=sleep_seconds,
                paged=definition.paged,
            )
        except (HTTPError, URLError, TimeoutError) as exc:
            raise RuntimeError(f"Query '{definition.query_id}' failed with params={definition.params!r}: {exc}") from exc
    return results


def collect_capture_records(query_results: dict[str, list[dict[str, str]]]) -> list[CaptureRecord]:
    records: list[CaptureRecord] = []
    for query_id, rows in query_results.items():
        for row in rows:
            if {"timestamp", "original", "statuscode", "mimetype"} <= row.keys():
                records.append(
                    CaptureRecord(
                        query_id=query_id,
                        timestamp=row["timestamp"],
                        original=row["original"],
                        statuscode=row["statuscode"],
                        mimetype=row["mimetype"],
                    )
                )
    return dedupe_captures(records)


def write_captures_csv(path: Path, records: Iterable[CaptureRecord]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["query_id", "timestamp", "original", "statuscode", "mimetype", "wayback_url"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "query_id": record.query_id,
                    "timestamp": record.timestamp,
                    "original": record.original,
                    "statuscode": record.statuscode,
                    "mimetype": record.mimetype,
                    "wayback_url": record.wayback_url,
                }
            )


def write_unique_csv(path: Path, records: Iterable[UniqueUrlRecord]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "normalized_url",
                "kind",
                "first_timestamp",
                "last_timestamp",
                "capture_count",
                "best_timestamp",
                "best_original",
                "best_statuscode",
                "best_mimetype",
                "best_wayback_url",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "normalized_url": record.normalized_url,
                    "kind": record.kind,
                    "first_timestamp": record.first_timestamp,
                    "last_timestamp": record.last_timestamp,
                    "capture_count": record.capture_count,
                    "best_timestamp": record.best_timestamp,
                    "best_original": record.best_original,
                    "best_statuscode": record.best_statuscode,
                    "best_mimetype": record.best_mimetype,
                    "best_wayback_url": record.best_wayback_url,
                }
            )


def write_summary_json(path: Path, summary: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory archived CDX captures for a removed site and export Wayback-ready CSV/JSON files."
    )
    parser.add_argument("--domain", default="bufsimrishamn.wordpress.com", help="Domain to inventory.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated CSV/JSON files.")
    parser.add_argument("--from-year", type=int, help="Inclusive start year for CDX filtering.")
    parser.add_argument("--to-year", type=int, help="Inclusive end year for CDX filtering.")
    parser.add_argument("--scope", default="all-public", help="Scope preset. Default: all-public.")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="CDX page size per request.")
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Optional delay between paginated CDX requests.",
    )
    parser.add_argument(
        "--cdx-endpoint",
        default=CDX_ENDPOINT,
        help="CDX endpoint override, useful for tests or mirrors.",
    )
    parser.add_argument("--max-retries", type=int, default=5, help="Retry attempts for retryable CDX/network errors.")
    parser.add_argument(
        "--retry-backoff-seconds",
        type=float,
        default=2.0,
        help="Linear backoff base between retry attempts.",
    )
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    if args.page_size <= 0:
        raise ValueError("--page-size must be greater than zero")
    if args.max_retries < 0:
        raise ValueError("--max-retries must be zero or greater")
    if args.retry_backoff_seconds < 0:
        raise ValueError("--retry-backoff-seconds must be zero or greater")
    if args.from_year and args.to_year and args.from_year > args.to_year:
        raise ValueError("--from-year must be less than or equal to --to-year")


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validate_args(args)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    definitions = build_query_definitions(args.domain, args.scope, args.from_year, args.to_year)
    client = CdxClient(
        output_dir.parent,
        endpoint=args.cdx_endpoint,
        max_retries=args.max_retries,
        retry_backoff_seconds=args.retry_backoff_seconds,
    )

    try:
        query_results = fetch_all_queries(
            client,
            definitions,
            page_size=args.page_size,
            sleep_seconds=args.sleep_seconds,
        )
    except (HTTPError, URLError, TimeoutError, RuntimeError) as exc:
        print(f"CDX fetch failed: {exc}", file=sys.stderr)
        return 1

    capture_records = collect_capture_records(query_results)
    unique_records = build_unique_records(capture_records)
    summary = build_summary(query_results, capture_records, unique_records)

    write_captures_csv(output_dir / "captures_raw.csv", capture_records)
    write_unique_csv(output_dir / "urls_unique.csv", unique_records)
    write_summary_json(output_dir / "summary.json", summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
