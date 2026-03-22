from __future__ import annotations

import json
import posixpath
from html import escape
from pathlib import Path, PurePosixPath
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent
METADATA_PATH = ROOT_DIR / "archive-data" / "collections.json"
CSS_PATH = ROOT_DIR / "_archive" / "archive.css"
OUTPUT_PATH = ROOT_DIR / "index.html"
ROBOTS_PATH = ROOT_DIR / "robots.txt"


def load_metadata(path: Path = METADATA_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def status_class(status: str) -> str:
    lowered = status.strip().lower()
    if lowered in {"återställd", "extern referens"}:
        return "chip chip--ok"
    if lowered in {"kandidat", "redo för inventering", "pågående kartläggning"}:
        return "chip chip--warn"
    return "chip"


def relative_href(from_path: str, to_path: str) -> str:
    start = str(PurePosixPath(from_path).parent) or "."
    return posixpath.relpath(to_path, start=start).replace("\\", "/")


def local_target(entry: dict[str, Any], root_dir: Path = ROOT_DIR) -> tuple[str | None, bool]:
    local_path = entry.get("local_path")
    if not local_path:
        return None, False
    target = root_dir / local_path
    return local_path, target.exists()


def render_link(href: str, label: str, *, primary: bool = False) -> str:
    class_name = "action action--primary" if primary else "action"
    return f'<a class="{class_name}" href="{escape(href, quote=True)}">{escape(label)}</a>'


def render_entry(entry: dict[str, Any], collection_title: str) -> str:
    local_path, exists = local_target(entry)
    links: list[str] = [render_link(entry["canonical_url"], "Öppna originaladress")]
    links.extend(render_link(link["url"], link["label"]) for link in entry.get("wayback_links", []))
    if local_path:
        label = "Öppna lokal plats" if exists else "Öppna planerad lokal sida"
        links.append(render_link(local_path, label, primary=True))

    path_note = ""
    if local_path and exists:
        path_note = f'<p class="path-note">Lokal sökväg: <code>{escape(local_path)}</code>.</p>'
    elif local_path:
        path_note = (
            f'<p class="path-note">Planerad lokal sökväg: <code>{escape(local_path)}</code>. '
            "En placeholder-sida har skapats tills återställningen finns lokalt.</p>"
        )

    evidence = "".join(f"<li>{escape(item)}</li>" for item in entry.get("evidence", []))
    return f"""
<article class="entry-card" id="{escape(entry['slug'])}">
  <div class="entry-top">
    <div>
      <h3>{escape(entry['title'])}</h3>
      <p class="muted">{escape(collection_title)} · {escape(entry['platform'])}</p>
    </div>
    <span class="{status_class(entry['status'])}">{escape(entry['status'])}</span>
  </div>
  <div class="entry-meta">
    <span class="chip">{escape(entry['confidence'])}</span>
    <span class="chip">{escape(entry['platform'])}</span>
  </div>
  <p><strong>Koppling:</strong> {escape(entry['owner_relation'])}</p>
  <p>{escape(entry['summary_long'])}</p>
  <p><strong>Källadress:</strong> <a href="{escape(entry['canonical_url'], quote=True)}">{escape(entry['canonical_url'])}</a></p>
  {path_note}
  <p><strong>Forskningsspår:</strong></p>
  <ul>{evidence}</ul>
  <div class="linklist">{''.join(links)}</div>
</article>
""".strip()


def render_collection(collection: dict[str, Any]) -> str:
    intros = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in collection.get("intro", []))
    entries = "\n".join(render_entry(entry, collection["title"]) for entry in collection.get("entries", []))
    return f"""
<section class="section" id="{escape(collection['slug'])}">
  <div class="collection-block">
    <div class="collection-head">
      <div class="collection-copy">
        <h2>{escape(collection['title'])}</h2>
        <p><span class="{status_class(collection['status'])}">{escape(collection['status'])}</span></p>
        {intros}
      </div>
    </div>
    <div class="stack">
      {entries}
    </div>
  </div>
</section>
""".strip()


def iter_restored_sites(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    restored = list(metadata.get("standalone_sites", []))
    for collection in metadata.get("collections", []):
        for entry in collection.get("entries", []):
            local_path, exists = local_target(entry)
            if local_path and exists and entry.get("status") in {"delvis återställd", "återställd"}:
                restored.append(
                    {
                        "slug": entry["slug"],
                        "title": entry["title"],
                        "summary": entry["summary_long"],
                        "status": entry["status"],
                        "local_path": local_path,
                    }
                )
    return restored


def iter_ongoing_entries(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    ongoing: list[dict[str, Any]] = []
    for collection in metadata.get("collections", []):
        for entry in collection.get("entries", []):
            local_path, exists = local_target(entry)
            if entry["status"] == "extern referens":
                continue
            if local_path and exists and entry["status"] in {"delvis återställd", "återställd"}:
                continue
            ongoing.append(entry)
    return ongoing


def render_root_html(metadata: dict[str, Any]) -> str:
    collections = metadata.get("collections", [])
    restored = iter_restored_sites(metadata)
    ongoing = iter_ongoing_entries(metadata)

    collection_cards = []
    for collection in collections:
        collection_cards.append(
            f"""
<article class="card">
  <h3>{escape(collection['title'])}</h3>
  <p>{escape(collection['summary'])}</p>
  <p><span class="{status_class(collection['status'])}">{escape(collection['status'])}</span></p>
  <p>{render_link(f"#{collection['slug']}", "Öppna samlingen", primary=True)}</p>
</article>
""".strip()
        )

    restored_cards = []
    for site in restored:
        restored_cards.append(
            f"""
<article class="card">
  <h3>{escape(site['title'])}</h3>
  <p>{escape(site['summary'])}</p>
  <p><span class="{status_class(site['status'])}">{escape(site['status'])}</span></p>
  <p>{render_link(site['local_path'], "Öppna lokal sajt", primary=True)}</p>
</article>
""".strip()
        )

    ongoing_cards = []
    for entry in ongoing:
        local_path, _ = local_target(entry)
        action = render_link(local_path, "Öppna planerad lokal sida") if local_path else ""
        ongoing_cards.append(
            f"""
<article class="card">
  <h3>{escape(entry['title'])}</h3>
  <p>{escape(entry['summary_long'])}</p>
  <p><span class="{status_class(entry['status'])}">{escape(entry['status'])}</span> <span class="chip">{escape(entry['confidence'])}</span></p>
  <p>{action}</p>
</article>
""".strip()
        )

    about_html = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in metadata.get("about", []))
    collections_html = "\n".join(render_collection(collection) for collection in collections)
    status_scale = ", ".join(escape(item) for item in metadata["site"]["status_scale"])
    ongoing_nav = '<a href="#pagaende">Pågående återställningar</a>' if ongoing else ""
    ongoing_section = ""
    if ongoing:
        ongoing_section = f"""
    <section class="section" id="pagaende">
      <h2>Pågående återställningar</h2>
      <p class="section-intro">Dessa spår är dokumenterade i samlingen men ännu inte återställda fullt ut. Placeholder-sidorna fungerar som stabila länkmål under arbetets gång.</p>
      <div class="grid">{''.join(ongoing_cards)}</div>
    </section>"""

    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(metadata['site']['title'])}</title>
  <meta name="robots" content="noindex, nofollow, noarchive" />
  <link rel="stylesheet" href="_archive/archive.css" />
</head>
<body>
  <header class="topbar">
    <div class="shell topbar__inner">
      <div class="brand">{escape(metadata['site']['title'])}</div>
      <nav class="navlinks">
        <a href="#samlingar">Samlingar</a>
        <a href="#aterstallda">Återställda sajter</a>
        {ongoing_nav}
        <a href="#om-arkivet">Om arkivet</a>
      </nav>
    </div>
  </header>
  <main class="shell">
    <section class="hero">
      <div class="hero__grid">
        <div class="card">
          <p><span class="chip">{escape(metadata['site']['tagline'])}</span></p>
          <h1>{escape(metadata['site']['title'])}</h1>
          <p class="lede">{escape(metadata['site']['summary'])}</p>
        </div>
        <aside class="card">
          <div class="meta-grid">
            <div><strong>{len(collections)}</strong><span>samlingar</span></div>
            <div><strong>{len(restored)}</strong><span>lokala sajter</span></div>
            <div><strong>{len(ongoing)}</strong><span>pågående spår</span></div>
            <div><strong>{len(metadata['site']['status_scale'])}</strong><span>statusnivåer</span></div>
          </div>
        </aside>
      </div>
    </section>
    <section class="section" id="samlingar">
      <h2>Samlingar</h2>
      <p class="section-intro">Root-sajten är generell från start. Samlingar kan gälla personer, projekt, organisationer eller avgränsade tematiska arkiv.</p>
      <div class="grid">{''.join(collection_cards)}</div>
    </section>
    {collections_html}
    <section class="section" id="aterstallda">
      <h2>Återställda sajter</h2>
      <p class="section-intro">Här syns lokala sajter som redan har en läsbar startsida i archive.</p>
      <div class="grid">{''.join(restored_cards)}</div>
    </section>
    {ongoing_section}
    <section class="section" id="om-arkivet">
      <h2>Om arkivet</h2>
      <div class="card">
        {about_html}
        <p><strong>Statusskala:</strong> {status_scale}</p>
      </div>
    </section>
  </main>
</body>
</html>
"""


def render_placeholder_html(collection: dict[str, Any], entry: dict[str, Any], local_path: str) -> str:
    css_href = relative_href(local_path, "_archive/archive.css")
    home_href = relative_href(local_path, "index.html")
    collection_href = f"{home_href}#{collection['slug']}"
    wayback_links = "".join(
        f'<li><a href="{escape(link["url"], quote=True)}">{escape(link["label"])}</a></li>'
        for link in entry.get("wayback_links", [])
    )
    evidence = "".join(f"<li>{escape(item)}</li>" for item in entry.get("evidence", []))
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(entry['title'])} · planerad återställning</title>
  <meta name="robots" content="noindex, nofollow, noarchive" />
  <link rel="stylesheet" href="{escape(css_href, quote=True)}" />
</head>
<body class="placeholder">
  <main class="card">
    <p><span class="{status_class(entry['status'])}">{escape(entry['status'])}</span></p>
    <h1>{escape(entry['title'])}</h1>
    <p><strong>Samling:</strong> {escape(collection['title'])}</p>
    <p><strong>Plattform:</strong> {escape(entry['platform'])}</p>
    <p><strong>Attribuering:</strong> {escape(entry['confidence'])}</p>
    <p>{escape(entry['summary_long'])}</p>
    <p><strong>Koppling:</strong> {escape(entry['owner_relation'])}</p>
    <p><strong>Källadress:</strong> <a href="{escape(entry['canonical_url'], quote=True)}">{escape(entry['canonical_url'])}</a></p>
    <p>Den här sidan är en stabil lokal hållplats innan full inventering och återställning har genomförts. När en faktisk lokal kopia finns kommer den här platsen att ersättas av den återställda sajten.</p>
    <h2>Wayback-spår</h2>
    <ul>{wayback_links}</ul>
    <h2>Forskningsspår</h2>
    <ul>{evidence}</ul>
    <p>{render_link(home_href, "Till archive-startsidan")} {render_link(collection_href, "Till Charlotta-sektionen", primary=True)}</p>
  </main>
</body>
</html>
"""


def build_site(
    metadata: dict[str, Any],
    *,
    root_dir: Path = ROOT_DIR,
    output_path: Path = OUTPUT_PATH,
    robots_path: Path = ROBOTS_PATH,
) -> None:
    output_path.write_text(render_root_html(metadata), encoding="utf-8")
    robots_path.write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    for collection in metadata.get("collections", []):
        for entry in collection.get("entries", []):
            local_path, exists = local_target(entry, root_dir=root_dir)
            if not local_path or exists:
                continue
            destination = root_dir / local_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(render_placeholder_html(collection, entry, local_path), encoding="utf-8")


def main() -> int:
    metadata = load_metadata()
    build_site(metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
