# CWas AI-handbok (statisk Astro-sajt)

Statisk webbplats för CWas som personlig referens/handbok för AI i skolbiblioteks- och politikvardag.

## Stack

- `Astro` med `output: "static"`
- Endast statiska filer vid build (`dist/`)

## Kom igång lokalt

```bash
npm install
npm run dev
```

## Bygg statiskt

```bash
npm run build
```

Byggda filer hamnar i `dist/` och kan deployas till valfri statisk hosting (t.ex. GitHub Pages, Netlify eller vanlig webbserver).

## Struktur

- `src/pages` sidor
- `src/components` UI-komponenter
- `src/content` innehållsunderlag/markdown
- `src/layouts` globala layouter
- `src/styles` globala stilar
