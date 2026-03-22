from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener


def raw_cache_dir(site_root: Path) -> Path:
    path = site_root / "raw-cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_key(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def cache_paths(site_root: Path, url: str, suffix: str = ".html") -> tuple[Path, Path]:
    key = cache_key(url)
    root = raw_cache_dir(site_root)
    return root / f"{key}{suffix}", root / f"{key}.json"


def read_cached_text(site_root: Path, url: str, encoding: str = "utf-8") -> str | None:
    data_path, _meta_path = cache_paths(site_root, url)
    if not data_path.exists():
        return None
    return data_path.read_text(encoding=encoding, errors="replace")


def read_cached_bytes(site_root: Path, url: str) -> bytes | None:
    data_path, _meta_path = cache_paths(site_root, url)
    if not data_path.exists():
        return None
    return data_path.read_bytes()


def write_cached_response(site_root: Path, url: str, body: bytes, *, source: str, encoding: str | None = None, extra: dict[str, object] | None = None) -> Path:
    data_path, meta_path = cache_paths(site_root, url)
    data_path.write_bytes(body)
    payload: dict[str, object] = {
        "url": url,
        "source": source,
        "body_path": data_path.name,
    }
    if encoding:
        payload["encoding"] = encoding
    if extra:
        payload.update(extra)
    meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return data_path


def fetch_url_bytes(
    site_root: Path,
    url: str,
    *,
    source: str,
    user_agent: str,
    timeout: float = 60,
    max_retries: int = 4,
    retry_backoff_seconds: float = 2.0,
    retryable_statuses: set[int] | None = None,
    headers: dict[str, str] | None = None,
    suffix: str = ".html",
    opener=None,
    extra: dict[str, object] | None = None,
) -> bytes:
    cached = read_cached_bytes(site_root, url)
    if cached is not None:
        return cached
    retryable_statuses = retryable_statuses or {429, 500, 502, 503, 504}
    effective_headers = {"User-Agent": user_agent, "Accept-Encoding": "identity"}
    if headers:
        effective_headers.update(headers)
    request = Request(url, headers=effective_headers)
    http_opener = opener or build_opener()
    attempt = 0
    while True:
        try:
            with http_opener.open(request, timeout=timeout) as response:
                body = response.read()
                write_cached_response(
                    site_root,
                    url,
                    body,
                    source=source,
                    extra={
                        "status": getattr(response, "status", None),
                        "final_url": getattr(response, "url", url),
                        **(extra or {}),
                    },
                    suffix=suffix,
                )
                return body
        except HTTPError as exc:
            if exc.code not in retryable_statuses or attempt >= max_retries:
                raise
        except URLError:
            if attempt >= max_retries:
                raise
        attempt += 1
        time.sleep(retry_backoff_seconds * attempt)
