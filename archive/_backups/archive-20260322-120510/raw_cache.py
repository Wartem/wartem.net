from __future__ import annotations

import hashlib
import json
from pathlib import Path


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
