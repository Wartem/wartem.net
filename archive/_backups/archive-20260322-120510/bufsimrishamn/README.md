# CDX Inventory Tool

Det här verktyget hämtar CDX-indexposter från Wayback Machine för en borttagen sajt, deduplicerar captures, klassificerar URL-typer och exporterar:

- `captures_raw.csv`
- `urls_unique.csv`
- `summary.json`
- en rekonstruerad statisk sajt i lokal katalog

## Körning

```powershell
python .\cdx_inventory.py --output-dir .\out
```

Exempel med årsfönster:

```powershell
python .\cdx_inventory.py --output-dir .\out --from-year 2014 --to-year 2018
```

Viktiga flaggor:

- `--domain` default `bufsimrishamn.wordpress.com`
- `--scope` default `all-public`
- `--page-size` default `1000`
- `--sleep-seconds` för paus mellan paginerade anrop
- `--max-retries` och `--retry-backoff-seconds` för tåligare CDX-körningar
- `--cdx-endpoint` för test eller spegel

Vid `504 Gateway Time-out` från CDX är det ofta bättre att sänka sidstorleken:

```powershell
python .\cdx_inventory.py --output-dir .\out --page-size 250 --max-retries 6 --retry-backoff-seconds 3
```

## Utdata

- `captures_raw.csv`: `query_id,timestamp,original,statuscode,mimetype,wayback_url`
- `urls_unique.csv`: `normalized_url,kind,first_timestamp,last_timestamp,capture_count,best_timestamp,best_statuscode,best_mimetype,best_wayback_url`
- `summary.json`: antal per query, statuskod, mime type, URL-typ samt totaler

## Test

```powershell
python -m unittest discover -s .\tests -v
```

## Återskapa en statisk sajt

Det här kommandot uppdaterar inventeringen vid behov, laddar ner bästa arkivversion per URL och skriver en statisk sajt till `.\site`:

```powershell
python .\reconstruct_site.py --inventory-dir .\out --site-dir .\site --refresh-inventory
```

Efter körningen finns en rapport i `.\site\recovery\index.html` och rådata i `.\site\recovery\manifest.json`.
