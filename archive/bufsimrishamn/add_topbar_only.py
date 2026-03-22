from __future__ import annotations

import re
from pathlib import Path

from enhance_site import (
    ROBOTS_META_TAG,
    THEME_RELATIVE_PATH,
    TOPBAR_SCRIPT_RELATIVE_PATH,
    build_page_meta,
    build_topbar,
    iter_html_files,
    load_collection_nav,
    relpath_to_theme,
)


def ensure_body_classes(html: str, kind: str) -> str:
    body_match = re.search(r"<body([^>]*)>", html, flags=re.IGNORECASE)
    if not body_match:
        return html
    attrs = body_match.group(1)
    class_values = re.findall(r'class="([^"]*)"', attrs, flags=re.IGNORECASE)
    classes: list[str] = []
    for value in class_values:
        for item in value.split():
            if item not in classes:
                classes.append(item)
    if "recovery-enhanced" not in classes:
        classes.append("recovery-enhanced")
    kind_class = f"recovery-kind-{kind}"
    if kind_class not in classes:
        classes.append(kind_class)
    if class_values:
        attrs = re.sub(r'\s*class="[^"]*"', "", attrs, flags=re.IGNORECASE)
    attrs = attrs + f' class="{" ".join(classes)}"'
    return re.sub(r"<body([^>]*)>", f"<body{attrs}>", html, count=1, flags=re.IGNORECASE)


def strip_existing_topbar(html: str) -> str:
    marker = '<div class="recovery-topbar"'
    start = html.find(marker)
    if start == -1:
        return html
    scan = start
    depth = 0
    div_token = re.compile(r"</?div\b", flags=re.IGNORECASE)
    for match in div_token.finditer(html, start):
        token = match.group(0).lower()
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                close = re.search(r"</div\s*>", html[match.start() :], flags=re.IGNORECASE)
                if close:
                    end = match.start() + close.end()
                    return html[:start] + html[end:]
                break
        else:
            depth += 1
        scan = match.end()
    return html


def replace_topbar_only(html: str, topbar: str) -> str:
    html = strip_existing_topbar(html)
    return re.sub(r"(<body[^>]*>)", r"\1\n" + topbar, html, count=1, flags=re.IGNORECASE)


def main() -> int:
    site_dir = Path("site")
    pages = build_page_meta(site_dir)
    pages_by_path = {page.path: page for page in pages}
    collection_items = load_collection_nav(site_dir, "../archive-data/collections.json", "charlotta-wasteson")

    for html_path in iter_html_files(site_dir):
        relative = html_path.relative_to(site_dir).as_posix()
        meta = pages_by_path.get(relative)
        if not meta:
            continue
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        topbar = build_topbar(relative, "bufsimrishamn.wordpress.com", collection_items)
        html = ensure_body_classes(html, meta.kind)
        html = replace_topbar_only(html, topbar)
        if "name=\"robots\"" not in html.lower():
            html = html.replace("</head>", f"{ROBOTS_META_TAG}\n</head>")
        theme_href = relpath_to_theme(html_path, site_dir)
        if THEME_RELATIVE_PATH not in html:
            html = html.replace("</head>", f'<link rel="stylesheet" href="{theme_href}" />\n</head>')
        topbar_script_href = theme_href.replace(THEME_RELATIVE_PATH, TOPBAR_SCRIPT_RELATIVE_PATH)
        if TOPBAR_SCRIPT_RELATIVE_PATH not in html:
            html = html.replace("</head>", f'<script defer src="{topbar_script_href}"></script>\n</head>')
        html_path.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
