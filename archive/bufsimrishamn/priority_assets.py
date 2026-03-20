from __future__ import annotations

import argparse
import json
import posixpath
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit

import reconstruct_site


ALLOWED_IMAGE_HOST_PATTERNS = (
    "bufsimrishamn.files.wordpress.com",
    "farm",
    "live.staticflickr.com",
    "www.simrishamn.se",
    "simrishamn.se",
)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}


@dataclass(frozen=True)
class AssetGroup:
    host: str
    path: str
    candidates: tuple[str, ...]
    best_url: str
    score: tuple[int, int, int]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch representative image assets by grouping duplicate thumbnail variants into one preferred file."
    )
    parser.add_argument("--domain", default="bufsimrishamn.wordpress.com")
    parser.add_argument("--site-dir", default="site")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--limit", type=int, help="Optional limit after prioritization.")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-backoff-seconds", type=float, default=3.0)
    return parser.parse_args(argv)


def iter_html_files(site_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in site_dir.rglob("*.html")
        if "recovery" not in path.parts and "_assets" not in path.parts and "browse" not in path.parts
    )


def candidate_urls_from_html(html_text: str, current_url: str, domain: str) -> set[str]:
    collector = reconstruct_site.HTMLAssetCollector(current_url, domain, f"{domain.split('.', 1)[0]}.files.wordpress.com")
    collector.feed(html_text)
    collector.close()
    urls = set()
    for url in collector.urls:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        if not any(host == pattern or host.startswith(pattern) for pattern in ALLOWED_IMAGE_HOST_PATTERNS):
            continue
        if PurePosixPath(path).suffix.lower() not in IMAGE_EXTENSIONS and "imagevaulthandler.aspx" not in path:
            continue
        urls.add(url)
    return urls


def collect_asset_candidates(site_dir: Path, domain: str) -> list[str]:
    candidates: set[str] = set()
    for html_file in iter_html_files(site_dir):
        current_url = f"https://{domain}/{html_file.relative_to(site_dir).as_posix().replace('index.html', '')}"
        html_text = html_file.read_text(encoding="utf-8", errors="replace")
        candidates.update(candidate_urls_from_html(html_text, current_url, domain))
    return sorted(candidates)


def asset_key(url: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    return ((parsed.hostname or "").lower(), parsed.path)


def candidate_score(url: str) -> tuple[int, int, int]:
    parsed = urlsplit(url)
    params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    width = int(params.get("w", "0")) if params.get("w", "0").isdigit() else 0
    height = int(params.get("h", "0")) if params.get("h", "0").isdigit() else 0
    area = width * height
    no_query = 1 if not parsed.query else 0
    not_thumb = 1 if width >= 440 or not parsed.query else 0
    return (no_query, not_thumb, area)


def prioritize_candidates(candidates: Iterable[str]) -> list[AssetGroup]:
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for candidate in candidates:
        grouped[asset_key(candidate)].append(candidate)

    prioritized: list[AssetGroup] = []
    for (host, path), urls in grouped.items():
        scored = sorted(urls, key=lambda item: (candidate_score(item), item), reverse=True)
        prioritized.append(
            AssetGroup(
                host=host,
                path=path,
                candidates=tuple(sorted(set(urls))),
                best_url=scored[0],
                score=candidate_score(scored[0]),
            )
        )
    prioritized.sort(key=lambda group: (group.score, len(group.candidates), group.path), reverse=True)
    return prioritized


def archive_lookup_candidates(group: AssetGroup) -> list[str]:
    # Prefer visually useful variants first, but try every known variant before giving up.
    ordered = sorted(group.candidates, key=lambda item: (candidate_score(item), item), reverse=True)
    seen: set[str] = set()
    result: list[str] = []
    for candidate in ordered:
        if candidate not in seen:
            seen.add(candidate)
            result.append(candidate)
    if group.best_url not in seen:
        result.insert(0, group.best_url)
    return result


def relative_asset_path(url: str) -> str:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    base = PurePosixPath("_assets") / host / parsed.path.lstrip("/")
    if parsed.query:
        digest = reconstruct_site.slugify_query(parsed.query)
        return str(base.with_name(f"{base.stem}--{digest}{base.suffix}"))
    return str(base)


def build_link_map(groups: Iterable[AssetGroup]) -> dict[str, str]:
    link_map: dict[str, str] = {}
    for group in groups:
        relative_path = relative_asset_path(group.best_url)
        for url in group.candidates:
            normalized = reconstruct_site.cdx_inventory.normalize_url(url)
            link_map[normalized] = relative_path
            link_map[url] = relative_path
        link_map[reconstruct_site.cdx_inventory.normalize_url(group.best_url)] = relative_path
    return link_map


def rewrite_html_files(site_dir: Path, domain: str, link_map: dict[str, str]) -> None:
    for html_file in iter_html_files(site_dir):
        relative_path = html_file.relative_to(site_dir).as_posix()
        current_url = f"https://{domain}/{relative_path.replace('index.html', '')}"
        html_text = html_file.read_text(encoding="utf-8", errors="replace")
        rewritten = reconstruct_site.rewrite_html(html_text, current_url, relative_path, link_map)
        html_file.write_text(rewritten, encoding="utf-8")


def fetch_asset(
    group: AssetGroup,
    site_dir: Path,
    client: reconstruct_site.ArchiveClient,
    *,
    max_retries: int,
    retry_backoff_seconds: float,
) -> dict[str, str]:
    lookup_urls = archive_lookup_candidates(group)
    errors: list[str] = []

    for candidate in lookup_urls:
        relative_path = relative_asset_path(candidate)
        destination = site_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            return {"stage": "skipped_existing", "url": candidate, "path": relative_path}

        try:
            content, _ = client.download(candidate)
            destination.write_bytes(content)
            return {"stage": "downloaded", "url": candidate, "path": relative_path}
        except (HTTPError, URLError, TimeoutError) as exc:
            errors.append(f"{candidate}: {exc}")

        entry, error = reconstruct_site.resolve_best_entry(
            candidate,
            from_year=None,
            to_year=None,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )
        if entry is None:
            if error:
                errors.append(str(error))
            continue

        archive_url = reconstruct_site.build_archive_raw_url(entry.best_timestamp, entry.best_original)
        try:
            content, _ = client.download(archive_url)
            destination.write_bytes(content)
            return {
                "stage": "downloaded_via_wayback",
                "url": candidate,
                "path": relative_path,
                "archive_url": archive_url,
            }
        except (HTTPError, URLError, TimeoutError) as archive_exc:
            errors.append(f"{archive_url}: {archive_exc}")

    return {
        "stage": "download_failed",
        "url": group.best_url,
        "path": relative_asset_path(group.best_url),
        "error": " | ".join(errors[-8:]) if errors else "No downloadable variant found",
    }


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    site_dir = Path(args.site_dir)
    recovery_dir = site_dir / "recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)

    all_candidates = collect_asset_candidates(site_dir, args.domain)
    groups = prioritize_candidates(all_candidates)
    if args.offset:
        groups = groups[args.offset :]
    if args.limit is not None:
        groups = groups[: args.limit]

    summary_path = recovery_dir / "priority-assets-summary.json"
    log_path = recovery_dir / "priority-assets-log.jsonl"
    candidate_path = recovery_dir / "priority-assets-candidates.json"
    candidate_path.write_text(
        json.dumps(
            [
                {
                    "best_url": group.best_url,
                    "host": group.host,
                    "path": group.path,
                    "variants": list(group.candidates),
                    "score": list(group.score),
                }
                for group in groups
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    client = reconstruct_site.ArchiveClient(
        max_retries=args.max_retries,
        retry_backoff_seconds=args.retry_backoff_seconds,
    )

    results: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                fetch_asset,
                group,
                site_dir,
                client,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
            ): group
            for group in groups
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")

    rewrite_html_files(site_dir, args.domain, build_link_map(groups))

    downloaded = sum(1 for result in results if result["stage"] in {"downloaded", "downloaded_via_wayback"})
    skipped = sum(1 for result in results if result["stage"] == "skipped_existing")
    failed = sum(1 for result in results if result["stage"] == "download_failed")
    summary = {
        "raw_candidate_count": len(all_candidates),
        "group_count": len(prioritize_candidates(all_candidates)),
        "offset": args.offset,
        "processed_group_count": len(groups),
        "downloaded_count": downloaded,
        "skipped_existing_count": skipped,
        "failed_count": failed,
        "candidate_file": str(candidate_path),
        "log_file": str(log_path),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
