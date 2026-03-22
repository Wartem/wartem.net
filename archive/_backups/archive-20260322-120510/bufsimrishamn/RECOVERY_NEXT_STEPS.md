# Recovery Next Steps

Det här dokumentet beskriver vad som återstår om målet är att göra den återställda sajten så komplett som möjligt, förutsatt att man fortsätter med full återställning.

## Nuläge

- HTML-sidor, arkivsidor, taggsidor, kategorisidor och feeds är i huvudsak återställda i `site/`.
- Inventeringen finns i `out/`.
- Ett separat asset-pass laddar ner refererade filer stegvis till `site/_assets/`.
- Asset-pass körs återupptagbart i batcher och loggar till `site/recovery/`.

## Vad som återstår för ett nära perfekt resultat

1. Slutför asset-återställning för alla relevanta interna filer
- Kör återstående batchar eller en förbättrad variant av dem.
- Målet är att alla verkligt använda bilder och dokument som refereras från HTML ska finnas lokalt.
- Resultatet ska vara att HTML-sidor inte längre är beroende av externa `files.wordpress.com`-länkar för centralt innehåll.

2. Minska dubletter bland assets
- Samma bild förekommer ofta i flera WordPress-varianter: original, thumbnails och query-varianter som `?w=150`, `?w=300`, `?w=440`.
- Ett bättre slutläge är att föredra en representativ lokal variant per faktisk bild och skriva om HTML till den, i stället för att spara alla småvarianter.
- Om “perfekt” betyder visuell trohet bör man bevara tillräckligt många storlekar för att sidorna ska se rimliga ut, men inte nödvändigtvis varje möjlig variant.

3. Fånga fullstora originalbilder där det går
- Många sidor länkar från thumbnail till en större version eller original.
- Ett bättre slutresultat kräver att både inbäddad bild och klickbar större version fungerar lokalt.
- Det kan kräva ett särskilt pass som prioriterar länkar till originalfiler före små `?w=`-varianter.

4. Täta luckor i misslyckade hämtningar
- Några HTML-URL:er och vissa assets misslyckas på grund av tillfälliga nät- eller Wayback-fel.
- Ett slutpass bör samla alla misslyckanden från loggarna och försöka igen separat.
- Om vissa URL:er fortfarande misslyckas efter flera försök bör de markeras som permanenta luckor i en slutrapport.

5. Rensa och verifiera omskrivna länkar
- HTML är redan delvis omskriven till lokala länkar.
- Ett mer komplett slutläge kräver kontroll av:
  - `src`
  - `srcset`
  - `href` till bilder och bilagor
  - metadatafält som `data-large-file`, `data-orig-file` och liknande
- Målet är att centrala mediaflöden ska fungera lokalt även när användaren klickar vidare.

6. Hantera externa men viktiga beroenden
- Vissa sidor refererar externa resurser som:
  - WordPress CDN-skript
  - sociala widgets
  - externa kommun- eller tredjepartsbilder
- För ett verkligt arkivvänligt resultat bör man bestämma policy:
  - behåll externa länkar
  - neutralisera dem
  - eller spegla vissa viktiga resurser lokalt
- För “perfekt offline-kopia” behöver en del av detta hanteras, men allt är inte värt arbetet.

7. Kvalitetsgranska startsidan och representativa artiklar
- Kontrollera att några viktiga sidor faktiskt ser rätt ut:
  - startsidan
  - några tidiga poster
  - några bildtunga poster
  - några tagg- och kategorisidor
- Målet är att hitta systematiska fel, inte att manuellt läsa allt.

8. Bygg en slutrapport
- Slutrapporten bör sammanfatta:
  - antal återställda HTML-sidor
  - antal lokala assets
  - antal kvarvarande externa referenser
  - antal misslyckade objekt
  - kända kvalitetsbegränsningar

## Vad “perfekt” sannolikt fortfarande inte betyder

Även efter full körning finns det saker som sannolikt inte går att garantera:

- innehåll som aldrig arkiverades av Wayback
- privata eller ej publikt åtkomliga WordPress-resurser
- alla JS-beteenden från WordPress.com-miljön
- full funktion hos externa widgets, sociala embeds och tredjepartsskript

Det rimliga målet är därför:

- lokal läsbar kopia av sajten
- lokal tillgång till centrala bilder och filer
- så få brutna interna länkar som möjligt
- tydlig dokumentation av kvarvarande luckor

## Vad som är mest värt att göra härnäst

Om målet är maximal kvalitet:

1. Prioritera ett snabbare och smartare asset-pass
- deduplicera på faktisk bild, inte varje thumbnail-variant
- prioritera original och större storlekar
- använd befintliga loggar och tidigare resultat

2. Kör ett separat retry-pass för misslyckanden
- både för HTML och assets

3. Gör en riktad kvalitetsgranskning av några representativa sidor
- för att avgöra om ytterligare återställning ger verkligt värde

## Beslutsfråga inför nästa steg

Innan man gör mer arbete bör man välja mellan två mål:

- “Arkivkopia som är tillräckligt bra”
  - fokus på läsbarhet och rimlig bildtäckning
  - snabbare att nå

- “Så komplett återställning som möjligt”
  - fokus på maximal lokal spegling
  - mycket mer tidskrävande och med avtagande nytta
