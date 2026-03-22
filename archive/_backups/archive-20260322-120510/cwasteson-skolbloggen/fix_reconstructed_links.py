from __future__ import annotations

import re
from pathlib import Path

MARKER = "Den fullständiga artikelsidan kunde inte återfinnas som egen capture i Wayback Machine."
SITE_DIR = Path(__file__).resolve().parent / "site"

ROOTISH_PREFIXES = (
    "browse/",
    "recovery/",
    "author/",
    "category/",
    "tag/",
    "page/",
    "feed/",
    "comments/",
    "2010/",
    "2011/",
    "2012/",
    "2013/",
    "2014/",
    "2015/",
    "2016/",
    "2017/",
    "2018/",
    "2019/",
    "2020/",
)


def rel_prefix(path: Path) -> str:
    depth = len(path.relative_to(SITE_DIR).parts) - 1
    return "../" * depth


def rewrite_attr(match: re.Match[str], prefix: str) -> str:
    attr = match.group(1)
    quote = match.group(2)
    value = match.group(3)
    if value.startswith(("http://", "https://", "mailto:", "#", "javascript:", "../", "./", "//", "?")):
        return match.group(0)
    if not value.startswith(ROOTISH_PREFIXES):
        return match.group(0)
    return f'{attr}={quote}{prefix}{value}{quote}'


def fix_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    if MARKER not in html:
        return False
    prefix = rel_prefix(path)
    updated = re.sub(r'\b(href|src)=(["\'])([^"\']+)\2', lambda m: rewrite_attr(m, prefix), html)
    if updated == html:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for path in SITE_DIR.rglob("index.html"):
        if fix_file(path):
            changed += 1
    print(f"updated {changed} reconstructed pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
