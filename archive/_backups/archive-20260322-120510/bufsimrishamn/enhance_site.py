from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
from urllib.parse import quote_plus, urlsplit
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

THEME_RELATIVE_PATH = "_recovery/recovery.css"
SEARCH_SCRIPT_RELATIVE_PATH = "_recovery/recovery-search.js"
ROBOTS_META_TAG = '<meta name="robots" content="noindex, nofollow, noarchive" />'
ROBOTS_TXT_CONTENT = "User-agent: *\nDisallow: /\n"
HTACCESS_CONTENT = """<IfModule mod_headers.c>
Header set X-Robots-Tag "noindex, nofollow, noarchive"
</IfModule>
"""

THEME_CSS = """
:root { --bg:#efe7d8; --paper:#fffdf8; --paper-alt:#faf5ea; --ink:#1f2b2a; --muted:#5d6d69; --accent:#0d6e73; --accent-soft:#d9ece9; --border:#d7cfbe; --shadow:0 20px 55px rgba(57,40,11,.09); --max:1280px; --measure:52rem; --listing-measure:66rem; }
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:
radial-gradient(circle at top,#f8f3ea 0%,rgba(248,243,234,.92) 25%,rgba(248,243,234,0) 55%),
linear-gradient(180deg,#f7f3eb 0%,#efe7d8 100%);color:var(--ink);font:16px/1.7 Georgia,"Times New Roman",serif}
body.recovery-enhanced{padding-top:5.1rem}
a{color:var(--accent)}
img{max-width:100%;height:auto}
#page{max-width:var(--max);margin:1.4rem auto 3rem;background:var(--paper);border:1px solid var(--border);border-radius:18px;box-shadow:var(--shadow);overflow:hidden}
#main{display:grid;grid-template-columns:minmax(0,1fr) minmax(240px,320px)}
#primary{padding:2rem}
#secondary{padding:1.5rem;background:#f8f2e7;border-left:1px solid var(--border)}
.entry-title,.entry-title a{color:var(--ink);text-decoration:none}
.entry-content blockquote{border-left:4px solid var(--accent);background:#e6f2f2;padding:.8rem 1rem}
.recovery-topbar{position:fixed;top:0;left:0;right:0;z-index:999;background:rgba(17,36,35,.94);color:#f5f3ee;border-bottom:1px solid rgba(255,255,255,.08);backdrop-filter:blur(12px)}
.recovery-topbar__inner{max-width:calc(var(--max) + 2rem);margin:0 auto;display:grid;grid-template-columns:auto 1fr auto;gap:.75rem 1rem;align-items:center;padding:.8rem 1rem}
.recovery-topbar__brand{display:inline-flex;align-items:center;font-weight:700;color:#f5f3ee;text-decoration:none;padding:0;background:none;border-radius:0}
.recovery-topbar nav{display:flex;flex-wrap:wrap;gap:.65rem}
.recovery-topbar a{color:#d7f1ef;text-decoration:none;padding:.3rem .65rem;border-radius:999px;background:rgba(215,241,239,.08)}
.recovery-topbar__rootlink{margin-left:auto;background:#d7f1ef!important;color:#123130!important;font-weight:700}
.recovery-collection-menu{position:relative}
.recovery-collection-menu summary{list-style:none;cursor:pointer;color:#d7f1ef;padding:.3rem .65rem;border-radius:999px;background:rgba(215,241,239,.08)}
.recovery-collection-menu summary::-webkit-details-marker{display:none}
.recovery-collection-menu[open] summary{background:rgba(215,241,239,.16)}
.recovery-collection-menu__panel{position:absolute;top:calc(100% + .45rem);left:0;min-width:18rem;max-width:min(28rem,80vw);padding:.5rem;background:#173331;border:1px solid rgba(255,255,255,.1);border-radius:14px;box-shadow:0 18px 34px rgba(0,0,0,.24);display:grid;gap:.2rem}
.recovery-collection-menu__panel a{display:block;background:transparent;padding:.55rem .7rem;border-radius:10px}
.recovery-collection-menu__panel a:hover{background:rgba(215,241,239,.1)}
.recovery-collection-menu__panel strong{display:block;color:#fff;font-size:.94rem}
.recovery-collection-menu__panel span{display:block;color:#c5dad8;font-size:.82rem}
.recovery-topbar__search form{display:flex;gap:.5rem}
.recovery-topbar__search input{width:min(18rem,42vw);padding:.55rem .9rem;border-radius:999px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.08);color:#fff}
.recovery-topbar__search button{padding:.55rem .9rem;border:0;border-radius:999px;background:#d7f1ef;color:#123130;font-weight:700}
.recovery-context{margin:0 0 1.5rem;padding:1rem 1.1rem;background:linear-gradient(135deg,#eef6f5,#f8f1e4);border:1px solid var(--border);border-radius:12px}
.recovery-context__crumbs{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.35rem}
.recovery-catalog{max-width:var(--max);margin:2rem auto 3rem;background:var(--paper);border:1px solid var(--border);border-radius:16px;padding:2rem}
.recovery-hero{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(260px,.9fr);gap:1.25rem;margin-bottom:1.25rem}
.recovery-intro,.recovery-card,.recovery-search-panel,.recovery-result{border:1px solid var(--border);border-radius:14px;background:#faf6ee;padding:1rem}
.recovery-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}
.recovery-grid + .recovery-search-panel{margin-top:1.1rem}
.recovery-grid--balanced{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.recovery-browse-intro{margin:0}
.recovery-browse-layout{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,.8fr);gap:1rem;align-items:start}
.recovery-browse-main{display:grid;gap:1rem}
.recovery-browse-sidebar{display:grid;gap:1rem}
.recovery-card--dense{padding:1.1rem 1.05rem}
.recovery-card--dense h2,.recovery-search-panel h2,.recovery-tag-panel h2{margin-top:0}
.recovery-card__header{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;margin-bottom:.8rem}
.recovery-card__header h2{margin:0}
.recovery-card__header .recovery-meta{white-space:nowrap}
.recovery-card__footer{margin-top:1rem;padding-top:.85rem;border-top:1px solid var(--border)}
.recovery-card__footer a{text-decoration:none;font-weight:700}
.recovery-link-list{list-style:none;margin:0;padding:0;display:grid;gap:.75rem}
.recovery-link-list li{break-inside:auto;margin:0;padding:0}
.recovery-link-list a{text-decoration:none}
.recovery-link-list strong{display:block;color:var(--ink);font-size:1.04rem;line-height:1.2}
.recovery-link-list span{display:block;color:var(--muted);font-size:.93rem}
.recovery-tag-cloud{display:flex;flex-wrap:wrap;gap:.55rem;margin-bottom:.9rem}
.recovery-tag-cloud .recovery-chip{display:inline-flex;align-items:center;gap:.35rem}
.recovery-tag-cloud .recovery-chip strong{font-size:.82rem}
.recovery-results-meta{margin:.15rem 0 .9rem;color:var(--muted);font-size:.94rem}
.recovery-section-header{display:flex;justify-content:space-between;gap:1rem;align-items:end;margin-bottom:.85rem}
.recovery-section-header h2{margin:0}
.recovery-section-header p{margin:.25rem 0 0;color:var(--muted)}
.recovery-search-controls{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(180px,.6fr);gap:.85rem;margin-bottom:.75rem}
.recovery-field label{display:block;font-size:.92rem;color:var(--muted);margin-bottom:.35rem}
.recovery-field input,.recovery-field select{width:100%;padding:.7rem .85rem;border:1px solid var(--border);border-radius:12px;background:#fffdf8}
.recovery-filter-row{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.75rem}
.recovery-filter-row button{border:1px solid rgba(13,110,115,.14);background:rgba(13,110,115,.08);color:#0a4d52;border-radius:999px;padding:.45rem .8rem}
.recovery-filter-row button.is-active{background:var(--accent);color:#fff;border-color:var(--accent)}
.recovery-results{display:grid;gap:.75rem}
.recovery-result__meta,.recovery-meta{color:var(--muted);font-size:.92rem}
.recovery-result__path{font-family:Consolas,"Courier New",monospace;font-size:.84rem}
.recovery-list{columns:2 18rem;column-gap:2rem}
.recovery-list li{break-inside:avoid;margin-bottom:.45rem}
.recovery-quicklinks,.recovery-index-links{display:flex;flex-wrap:wrap;gap:.5rem}
.recovery-quicklinks a,.recovery-chip{text-decoration:none;color:#0a4d52;padding:.45rem .8rem;background:rgba(13,110,115,.08);border:1px solid rgba(13,110,115,.14);border-radius:999px}
.recovery-section{scroll-margin-top:6.5rem;padding-top:.25rem}
.recovery-empty{border:1px dashed var(--border);border-radius:12px;padding:1rem;color:var(--muted);background:#fffdf8}
.archive #main,.category #main,.tag #main,.author #main,.blog #main{display:block!important;grid-template-columns:minmax(0,1fr)}
.archive #primary,.category #primary,.tag #primary,.author #primary,.blog #primary{display:block!important;float:none!important;width:100%!important;max-width:none!important;margin:0!important;padding:0}
.archive #content,.category #content,.tag #content,.author #content,.blog #content{display:block!important;float:none!important;width:100%!important;max-width:none!important;margin:0!important;padding:1.65rem clamp(1rem,2vw,1.85rem) 2.4rem}
.archive #secondary,.category #secondary,.tag #secondary,.author #secondary,.blog #secondary,.archive #tertiary,.category #tertiary,.tag #tertiary,.author #tertiary,.blog #tertiary{display:none!important}
.archive #masthead,.category #masthead,.tag #masthead,.author #masthead,.blog #masthead{padding-bottom:0;background:linear-gradient(180deg,#fffdf8 0%,#fbf7ef 100%)}
.archive #masthead a,.category #masthead a,.tag #masthead a,.author #masthead a,.blog #masthead a{display:block}
.archive #masthead img,.category #masthead img,.tag #masthead img,.author #masthead img,.blog #masthead img{float:none!important}
.archive .site-branding,.category .site-branding,.tag .site-branding,.author .site-branding,.blog .site-branding{max-width:var(--listing-measure);margin:0 auto;padding:1.2rem clamp(1rem,2vw,1.85rem) .7rem}
.archive #site-title,.category #site-title,.tag #site-title,.author #site-title,.blog #site-title{font-size:clamp(1.45rem,2vw,1.95rem);margin:0}
.archive #site-description,.category #site-description,.tag #site-description,.author #site-description,.blog #site-description{font-size:.98rem;margin:.3rem 0 0;color:var(--muted)!important}
.archive #header-image,.category #header-image,.tag #header-image,.author #header-image,.blog #header-image{display:block;width:min(calc(var(--listing-measure) + 1rem),100%);max-height:15rem;margin:0 auto 1.1rem;object-fit:cover;object-position:center 35%;border-radius:18px;box-shadow:0 18px 38px rgba(55,42,14,.12)}
.archive #content > .recovery-context,.category #content > .recovery-context,.tag #content > .recovery-context,.author #content > .recovery-context,.blog #content > .recovery-context,.archive .page-header,.category .page-header,.tag .page-header,.author .page-header,.blog .page-header,.archive #nav-above,.category #nav-above,.tag #nav-above,.author #nav-above,.blog #nav-above,.archive #nav-below,.category #nav-below,.tag #nav-below,.author #nav-below,.blog #nav-below,.recovery-listing-tools{max-width:var(--listing-measure);margin-left:auto;margin-right:auto}
.archive .page-header,.category .page-header,.tag .page-header,.author .page-header,.blog .page-header{margin-bottom:1.4rem;padding:0 0 1rem;border-bottom:1px solid var(--border)}
.archive .page-title,.category .page-title,.tag .page-title,.author .page-title,.blog .page-title{font-size:clamp(2rem,4vw,3.2rem);line-height:1.04;letter-spacing:-.03em;margin:.1rem 0 .4rem}
.recovery-listing-tools{display:flex;flex-wrap:wrap;gap:.6rem;margin:0 auto 1.2rem}
.recovery-listing-tools a{text-decoration:none;color:#0a4d52;padding:.48rem .82rem;background:rgba(13,110,115,.08);border:1px solid rgba(13,110,115,.14);border-radius:999px}
.archive #nav-above,.category #nav-above,.tag #nav-above,.author #nav-above,.blog #nav-above,.archive #nav-below,.category #nav-below,.tag #nav-below,.author #nav-below,.blog #nav-below{display:flex;justify-content:space-between;gap:1rem;margin:0 auto 1.5rem;padding:1rem 1.1rem;border:1px solid var(--border);border-radius:14px;background:linear-gradient(180deg,#f7f1e6 0%,#fbf7ef 100%)}
.archive #nav-above .nav-next,.category #nav-above .nav-next,.tag #nav-above .nav-next,.author #nav-above .nav-next,.blog #nav-above .nav-next,.archive #nav-below .nav-next,.category #nav-below .nav-next,.tag #nav-below .nav-next,.author #nav-below .nav-next,.blog #nav-below .nav-next{text-align:right;margin-left:auto}
.archive #nav-above a,.category #nav-above a,.tag #nav-above a,.author #nav-above a,.blog #nav-above a,.archive #nav-below a,.category #nav-below a,.tag #nav-below a,.author #nav-below a,.blog #nav-below a{text-decoration:none;color:#0a4d52;font-weight:600}
.archive article.post,.category article.post,.tag article.post,.author article.post,.blog article.post{max-width:var(--listing-measure);margin:0 auto 1.35rem;padding:1.2rem 1.2rem 1.1rem;border:1px solid var(--border);border-radius:18px;background:linear-gradient(180deg,#fffdf8 0%,#f9f4ea 100%);box-shadow:0 14px 34px rgba(55,42,14,.06)}
.archive article.post .entry-header,.category article.post .entry-header,.tag article.post .entry-header,.author article.post .entry-header,.blog article.post .entry-header{margin:0 0 1rem;padding:0 0 .9rem;border-bottom:1px solid var(--border)}
.archive article.post .entry-title,.category article.post .entry-title,.tag article.post .entry-title,.author article.post .entry-title,.blog article.post .entry-title{font-size:clamp(1.55rem,2.8vw,2.2rem);line-height:1.12;margin:0 0 .45rem}
.archive article.post .entry-meta,.category article.post .entry-meta,.tag article.post .entry-meta,.author article.post .entry-meta,.blog article.post .entry-meta,.recovery-listing-card__meta{display:flex;flex-wrap:wrap;gap:.45rem .8rem;color:var(--muted);font-size:.96rem}
.recovery-listing-card__meta .recovery-chip{padding:.18rem .55rem;background:#edf6f5}
.archive article.post .entry-content,.category article.post .entry-content,.tag article.post .entry-content,.author article.post .entry-content,.blog article.post .entry-content{font-size:1.04rem;line-height:1.75}
.archive article.post .entry-content::after,.category article.post .entry-content::after,.tag article.post .entry-content::after,.author article.post .entry-content::after,.blog article.post .entry-content::after{content:"";display:block;clear:both}
.archive article.post .entry-content img,.category article.post .entry-content img,.tag article.post .entry-content img,.author article.post .entry-content img,.blog article.post .entry-content img,.recovery-listing-card__media img{display:block;max-width:100%!important;height:auto!important;margin:1rem auto;border-radius:14px}
.archive article.post .alignleft,.archive article.post .alignright,.archive article.post .aligncenter,.category article.post .alignleft,.category article.post .alignright,.category article.post .aligncenter,.tag article.post .alignleft,.tag article.post .alignright,.tag article.post .aligncenter,.author article.post .alignleft,.author article.post .alignright,.author article.post .aligncenter,.blog article.post .alignleft,.blog article.post .alignright,.blog article.post .aligncenter{float:none!important;display:block!important;margin:1rem auto!important}
.archive article.post .wp-caption,.category article.post .wp-caption,.tag article.post .wp-caption,.author article.post .wp-caption,.blog article.post .wp-caption{width:min(100%,100%)!important;max-width:100%!important;padding:.7rem;border:1px solid var(--border);border-radius:16px;background:var(--paper-alt)}
.archive article.post footer.entry-meta,.category article.post footer.entry-meta,.tag article.post footer.entry-meta,.author article.post footer.entry-meta,.blog article.post footer.entry-meta{margin-top:1.3rem;padding-top:1rem;border-top:1px solid var(--border);background:none}
.recovery-listing-card__body{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(220px,.78fr);gap:1.2rem;align-items:start}
.recovery-listing-card__summary p{margin:.25rem 0 .85rem}
.recovery-listing-card__summary a.recovery-listing-card__more{display:inline-block;text-decoration:none;font-weight:700}
.recovery-listing-card__media{margin:0}
.recovery-listing-card__media img{width:100%;margin:0}
.recovery-listing-card__date{font-weight:700;color:#0a4d52}
.recovery-listing-card__title-link{text-decoration:none}
.single #main,.single-post #main,.post-template-default #main,.recovery-kind-post #main{display:block!important;grid-template-columns:minmax(0,1fr)}
.recovery-kind-post #header,.recovery-kind-post #sub-header,.recovery-kind-post #sidebar,.recovery-kind-post #access{display:none!important}
.recovery-kind-post #page{max-width:min(var(--measure) + 8rem,var(--max))}
.single #primary,.single-post #primary,.post-template-default #primary{display:block!important;float:none!important;width:100%!important;max-width:none!important;margin:0!important;padding:0}
.single #secondary,.single-post #secondary,.post-template-default #secondary,.single #tertiary,.single-post #tertiary,.post-template-default #tertiary{display:none!important}
.single #content,.single-post #content,.post-template-default #content,.recovery-kind-post #content,.recovery-kind-post .wrapper>#content{display:block!important;float:none!important;width:100%!important;max-width:none!important;margin:0 auto!important;padding:1.65rem clamp(1rem,2vw,1.85rem) 2.4rem}
.single #content > .recovery-context,.single-post #content > .recovery-context,.post-template-default #content > .recovery-context{max-width:var(--measure);margin-left:auto;margin-right:auto}
.single #masthead,.single-post #masthead,.post-template-default #masthead{padding-bottom:0;background:linear-gradient(180deg,#fffdf8 0%,#fbf7ef 100%)}
.single #masthead a,.single-post #masthead a,.post-template-default #masthead a{display:block}
.single #masthead img,.single-post #masthead img,.post-template-default #masthead img{float:none!important}
.single .site-branding,.single-post .site-branding,.post-template-default .site-branding{max-width:var(--measure);margin:0 auto;padding:1.2rem clamp(1rem,2vw,1.85rem) .7rem}
.single #site-title,.single-post #site-title,.post-template-default #site-title{font-size:clamp(1.45rem,2vw,1.95rem);margin:0}
.single #site-description,.single-post #site-description,.post-template-default #site-description{font-size:.98rem;margin:.3rem 0 0;color:var(--muted)!important}
.single #header-image,.single-post #header-image,.post-template-default #header-image{display:block;width:min(calc(var(--measure) + 1rem),100%);max-height:15rem;margin:0 auto 1.1rem;object-fit:cover;object-position:center 35%;border-radius:18px;box-shadow:0 18px 38px rgba(55,42,14,.12)}
.single article.post,.single-post article.post,.post-template-default article.post{max-width:var(--measure);margin:0 auto;border-bottom:0;padding:0}
.single .entry-header,.single-post .entry-header,.post-template-default .entry-header{margin:0 0 1.55rem;padding:0 0 1.25rem;border-bottom:1px solid var(--border)}
.single .entry-title,.single-post .entry-title,.post-template-default .entry-title{font-size:clamp(2.35rem,5vw,4.3rem);line-height:1.02;letter-spacing:-.03em;margin:.15rem 0 .85rem;text-wrap:balance}
.single .entry-meta,.single-post .entry-meta,.post-template-default .entry-meta{display:flex;flex-wrap:wrap;gap:.55rem 1rem;color:var(--muted);font-size:.98rem}
.single .entry-content,.single-post .entry-content,.post-template-default .entry-content{font-size:1.14rem;line-height:1.86;overflow-wrap:anywhere}
.single .entry-content::after,.single-post .entry-content::after,.post-template-default .entry-content::after{content:"";display:block;clear:both}
.single .entry-content > *,.single-post .entry-content > *,.post-template-default .entry-content > *{max-width:var(--measure);margin-left:auto;margin-right:auto}
.single .entry-content p,.single .entry-content ul,.single .entry-content ol,.single .entry-content blockquote,.single .entry-content h1,.single .entry-content h2,.single .entry-content h3,.single .entry-content h4,.single-post .entry-content p,.single-post .entry-content ul,.single-post .entry-content ol,.single-post .entry-content blockquote,.single-post .entry-content h1,.single-post .entry-content h2,.single-post .entry-content h3,.single-post .entry-content h4,.post-template-default .entry-content p,.post-template-default .entry-content ul,.post-template-default .entry-content ol,.post-template-default .entry-content blockquote,.post-template-default .entry-content h1,.post-template-default .entry-content h2,.post-template-default .entry-content h3,.post-template-default .entry-content h4{max-width:var(--measure)}
.single .entry-content h1,.single-post .entry-content h1,.post-template-default .entry-content h1{font-size:clamp(1.65rem,3vw,2.35rem);line-height:1.14;margin:2.1rem auto .8rem}
.single .entry-content h2,.single-post .entry-content h2,.post-template-default .entry-content h2{font-size:clamp(1.35rem,2.2vw,1.85rem);line-height:1.2;margin:1.8rem auto .7rem}
.single .entry-content ul,.single .entry-content ol,.single-post .entry-content ul,.single-post .entry-content ol,.post-template-default .entry-content ul,.post-template-default .entry-content ol{padding-left:1.3rem}
.single .entry-content img,.single-post .entry-content img,.post-template-default .entry-content img{display:block;max-width:100%!important;height:auto!important;border-radius:14px}
.single .entry-content a > img,.single-post .entry-content a > img,.post-template-default .entry-content a > img{box-shadow:0 18px 38px rgba(55,42,14,.11)}
.single .recovery-sidepanel,.single-post .recovery-sidepanel,.post-template-default .recovery-sidepanel{float:right;width:min(18rem,42%);margin:.2rem 0 1.2rem 1.4rem;padding:1rem 1.05rem;border:1px solid var(--border);border-radius:16px;background:linear-gradient(180deg,#f7f1e6 0%,#fbf7ef 100%);box-shadow:0 12px 28px rgba(55,42,14,.07)}
.single .recovery-sidepanel h3,.single-post .recovery-sidepanel h3,.post-template-default .recovery-sidepanel h3{margin:0 0 .7rem;font-size:1rem;line-height:1.2;color:#0a4d52}
.single .recovery-sidepanel p,.single-post .recovery-sidepanel p,.post-template-default .recovery-sidepanel p,.single .recovery-sidepanel ul,.single-post .recovery-sidepanel ul,.post-template-default .recovery-sidepanel ul,.single .recovery-sidepanel ol,.single-post .recovery-sidepanel ol,.post-template-default .recovery-sidepanel ol,.single .recovery-sidepanel small,.single-post .recovery-sidepanel small,.post-template-default .recovery-sidepanel small{margin:.45rem 0;font-size:.95rem;line-height:1.6}
.single .recovery-sidepanel a,.single-post .recovery-sidepanel a,.post-template-default .recovery-sidepanel a{text-decoration:none}
.single .recovery-sidepanel small,.single-post .recovery-sidepanel small,.post-template-default .recovery-sidepanel small{display:block;color:var(--muted)}
.single .alignleft,.single .alignright,.single .aligncenter,.single-post .alignleft,.single-post .alignright,.single-post .aligncenter,.post-template-default .alignleft,.post-template-default .alignright,.post-template-default .aligncenter,.single .wp-caption.alignleft,.single .wp-caption.alignright,.single .wp-caption.aligncenter,.single-post .wp-caption.alignleft,.single-post .wp-caption.alignright,.single-post .wp-caption.aligncenter,.post-template-default .wp-caption.alignleft,.post-template-default .wp-caption.alignright,.post-template-default .wp-caption.aligncenter{float:none!important;display:block!important;margin:1.6rem auto!important}
.single .wp-caption,.single-post .wp-caption,.post-template-default .wp-caption{width:min(100%,var(--measure))!important;max-width:100%!important;padding:.7rem;border:1px solid var(--border);border-radius:16px;background:var(--paper-alt);box-shadow:0 16px 35px rgba(55,42,14,.08)}
.single .wp-caption img,.single-post .wp-caption img,.post-template-default .wp-caption img{width:100%!important;height:auto!important;margin:0}
.single .wp-caption-text,.single-post .wp-caption-text,.post-template-default .wp-caption-text{margin:.75rem 0 0;color:var(--muted);font-size:.95rem;line-height:1.55}
.single .jetpack-video-wrapper,.single-post .jetpack-video-wrapper,.post-template-default .jetpack-video-wrapper{max-width:var(--measure);margin:2rem auto;padding:1rem;border:1px solid var(--border);border-radius:18px;background:linear-gradient(180deg,#faf7ef 0%,#f3ecdf 100%)}
.single .jetpack-video-wrapper iframe,.single .entry-content iframe,.single-post .jetpack-video-wrapper iframe,.single-post .entry-content iframe,.post-template-default .jetpack-video-wrapper iframe,.post-template-default .entry-content iframe{display:block;width:100%!important;max-width:100%!important;aspect-ratio:16/9;height:auto!important;margin:0 auto;border-radius:12px}
.single #nav-above,.single-post #nav-above,.post-template-default #nav-above,.single #nav-below,.single-post #nav-below,.post-template-default #nav-below{max-width:var(--measure);display:flex;justify-content:space-between;gap:1rem;margin:0 auto 1.5rem;padding:1rem 1.1rem;border:1px solid var(--border);border-radius:14px;background:linear-gradient(180deg,#f7f1e6 0%,#fbf7ef 100%)}
.single #nav-above .nav-previous,.single-post #nav-above .nav-previous,.post-template-default #nav-above .nav-previous,.single #nav-below .nav-previous,.single-post #nav-below .nav-previous,.post-template-default #nav-below .nav-previous{max-width:50%}
.single #nav-above .nav-next,.single-post #nav-above .nav-next,.post-template-default #nav-above .nav-next,.single #nav-below .nav-next,.single-post #nav-below .nav-next,.post-template-default #nav-below .nav-next{text-align:right;max-width:50%;margin-left:auto}
.single #nav-above a,.single-post #nav-above a,.post-template-default #nav-above a,.single #nav-below a,.single-post #nav-below a,.post-template-default #nav-below a{text-decoration:none;color:#0a4d52;font-weight:600}
.single #nav-below,.single-post #nav-below,.post-template-default #nav-below{margin-top:2.2rem}
.single .entry-meta:last-child,.single-post .entry-meta:last-child,.post-template-default .entry-meta:last-child{margin-bottom:0}
.single article footer.entry-meta,.single-post article footer.entry-meta,.post-template-default article footer.entry-meta{max-width:var(--measure);margin:2.2rem auto 0;padding:1.35rem 1.4rem;border-top:1px solid var(--border);background:#f9f4ea;border-radius:16px}
.single article footer.entry-meta p,.single-post article footer.entry-meta p,.post-template-default article footer.entry-meta p{margin:.45rem 0}
.single .date-link,.single-post .date-link,.post-template-default .date-link{display:none}
.single .tiled-gallery,.single-post .tiled-gallery,.post-template-default .tiled-gallery{max-width:100%!important;width:100%!important;margin:1.7rem auto!important}
.single .tiled-gallery .gallery-row,.single-post .tiled-gallery .gallery-row,.post-template-default .tiled-gallery .gallery-row,.single .tiled-gallery .gallery-group,.single-post .tiled-gallery .gallery-group,.post-template-default .tiled-gallery .gallery-group{width:100%!important;height:auto!important;display:flex;flex-wrap:wrap;gap:.6rem}
.single .tiled-gallery-item,.single-post .tiled-gallery-item,.post-template-default .tiled-gallery-item{width:calc(50% - .3rem)!important;height:auto!important;flex:1 1 240px}
.single .tiled-gallery-item img,.single-post .tiled-gallery-item img,.post-template-default .tiled-gallery-item img{width:100%!important;height:auto!important;display:block;border-radius:10px}
.single #comments,.single-post #comments,.post-template-default #comments,.recovery-kind-post #comments{display:block;max-width:var(--measure);margin:2.4rem auto 0;padding:1.35rem 1.4rem;border-top:1px solid var(--border);background:#fbf7ef;border-radius:16px}
.single #comments .commentlist,.single-post #comments .commentlist,.post-template-default #comments .commentlist{margin:1rem 0 0;padding-left:1.2rem}
.single #comments .comment,.single-post #comments .comment,.post-template-default #comments .comment{margin-bottom:1rem}
.recovery-kind-post .pagination-single{max-width:var(--measure);display:flex;justify-content:space-between;gap:1rem;margin:2rem auto 0;padding:1rem 1.1rem;border:1px solid var(--border);border-radius:14px;background:linear-gradient(180deg,#f7f1e6 0%,#fbf7ef 100%)}
.recovery-kind-post .pagination-single .next{text-align:right;margin-left:auto}
.wpcnt,[id^="atatags-"],script,.sharedaddy,.sd-content,.jp-relatedposts,.widget_facebook_likebox,.widget_wpcom_social_media_icons_widget,.widget_flickr,.widget_twitter_timeline,.widget_links,.widget_text .wpcnt,#access,.menu-toggle,.comments-link,.assistive-text.section-heading,[id^="like-post-wrapper-"]{display:none!important}
@media (max-width:980px){body.recovery-enhanced{padding-top:8.2rem}.recovery-topbar__inner{grid-template-columns:1fr}.recovery-topbar__search,.recovery-topbar__search form,.recovery-topbar__search input{width:100%}.recovery-search-controls,.recovery-browse-layout{grid-template-columns:1fr}}
@media (max-width:900px){#main{grid-template-columns:1fr}#secondary{border-left:0;border-top:1px solid var(--border)}.recovery-hero{grid-template-columns:1fr}#primary,#secondary,.recovery-catalog{padding:1.2rem}.recovery-list{columns:1}.archive #content,.category #content,.tag #content,.author #content,.blog #content,.single #content,.single-post #content,.post-template-default #content,.recovery-kind-post #content,.recovery-kind-post .wrapper>#content{padding:1rem}.archive #nav-above,.category #nav-above,.tag #nav-above,.author #nav-above,.blog #nav-above,.archive #nav-below,.category #nav-below,.tag #nav-below,.author #nav-below,.blog #nav-below,.single #nav-above,.single-post #nav-above,.post-template-default #nav-above,.single #nav-below,.single-post #nav-below,.post-template-default #nav-below,.recovery-section-header{flex-direction:column;align-items:flex-start}.archive #nav-above .nav-next,.category #nav-above .nav-next,.tag #nav-above .nav-next,.author #nav-above .nav-next,.blog #nav-above .nav-next,.archive #nav-below .nav-next,.category #nav-below .nav-next,.tag #nav-below .nav-next,.author #nav-below .nav-next,.blog #nav-below .nav-next,.single #nav-above .nav-previous,.single-post #nav-above .nav-previous,.post-template-default #nav-above .nav-previous,.single #nav-below .nav-previous,.single-post #nav-below .nav-previous,.post-template-default #nav-below .nav-previous,.single #nav-above .nav-next,.single-post #nav-above .nav-next,.post-template-default #nav-above .nav-next,.single #nav-below .nav-next,.single-post #nav-below .nav-next,.post-template-default #nav-below .nav-next,.recovery-kind-post .pagination-single{max-width:none;text-align:left;margin-left:0;flex-direction:column}.recovery-listing-card__body{grid-template-columns:1fr}.single .tiled-gallery-item,.single-post .tiled-gallery-item,.post-template-default .tiled-gallery-item{width:100%!important;flex-basis:100%}.single .recovery-sidepanel,.single-post .recovery-sidepanel,.post-template-default .recovery-sidepanel{float:none;width:auto;margin:1rem 0}}
"""

SEARCH_SCRIPT = r"""
(function(){function n(t){return(t||"").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"")}function e(t){return String(t||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;")}function m(d,terms){if(!terms.length)return true;var h=n([d.title,d.kind_label,d.path,d.summary].join(" "));return terms.every(function(term){return h.indexOf(term)!==-1})}function render(docs){var c=document.querySelector("[data-search-results]"),meta=document.querySelector("[data-search-meta]");if(!c||!meta)return;meta.textContent=docs.length?(docs.length+" traffar"):"Inga traffar";if(!docs.length){c.innerHTML='<div class="recovery-empty">Ingen sida matchade sokningen.</div>';return}c.innerHTML=docs.map(function(d){return '<article class="recovery-result"><h3><a href="../'+encodeURI(d.path)+'">'+e(d.title)+'</a></h3><div class="recovery-result__meta">'+e([d.kind_label,d.date_label].filter(Boolean).join(" · "))+'</div>'+(d.summary?'<p>'+e(d.summary)+'</p>':'')+'<p class="recovery-result__path">'+e(d.path)+'</p></article>'}).join("")}function apply(index){var q=document.querySelector("[data-search-query]").value||"",y=document.querySelector("[data-search-year]").value||"all",k=(document.querySelector("[data-search-kind].is-active")||{}).dataset.searchKind||"all",terms=n(q).split(/\s+/).filter(Boolean),docs=index.filter(function(d){if(k!=="all"&&d.kind!==k)return false;if(y!=="all"&&String(d.year||"")!==y)return false;return m(d,terms)});docs.sort(function(a,b){return (a.sort_date||"")<(b.sort_date||"")?1:-1});render(docs.slice(0,250));var u=new URL(window.location.href);q?u.searchParams.set("q",q):u.searchParams.delete("q");k!=="all"?u.searchParams.set("kind",k):u.searchParams.delete("kind");y!=="all"?u.searchParams.set("year",y):u.searchParams.delete("year");history.replaceState(null,"",u.toString())}fetch("./search-index.json").then(function(r){return r.json()}).then(function(index){var u=new URL(window.location.href),q=document.querySelector("[data-search-query]"),y=document.querySelector("[data-search-year]");q.value=u.searchParams.get("q")||"";if(u.searchParams.get("year"))y.value=u.searchParams.get("year");document.querySelectorAll("[data-search-kind]").forEach(function(b){if(b.dataset.searchKind===(u.searchParams.get("kind")||"all"))b.classList.add("is-active");b.addEventListener("click",function(){document.querySelectorAll("[data-search-kind]").forEach(function(x){x.classList.remove("is-active")});b.classList.add("is-active");apply(index)})});q.addEventListener("input",function(){apply(index)});y.addEventListener("change",function(){apply(index)});document.querySelector("[data-search-form]").addEventListener("submit",function(ev){ev.preventDefault();apply(index)});apply(index)}).catch(function(){var c=document.querySelector("[data-search-results]"),m=document.querySelector("[data-search-meta]");if(m)m.textContent="Sokindex kunde inte lasas";if(c)c.innerHTML='<div class="recovery-empty">Det gick inte att lasa sokindexet.</div>'})})();
"""


@dataclass
class PageMeta:
    path: str
    title: str
    kind: str
    year: int | None
    month: int | None
    day: int | None
    summary: str
    kind_label: str
    date_label: str


@dataclass
class PostRecord:
    path: str
    title: str
    summary: str
    date_label: str
    sort_key: tuple[int, int, int, str]
    author: str
    image_src: str
    image_alt: str
    categories: list[tuple[str, str]]
    tags: list[tuple[str, str]]


@dataclass
class CollectionNavItem:
    title: str
    href: str


CURRENT_COLLECTION_ITEMS: list[CollectionNavItem] = []


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enhance the recovered site with local navigation and search.")
    parser.add_argument("--site-dir", default="site")
    parser.add_argument("--site-title", default="Barn- och utbildning Simrishamn")
    parser.add_argument("--site-label", default="BUF Simrishamn")
    parser.add_argument(
        "--site-intro",
        default="Detta är en lokal, återställd version av den borttagna sajten. Startsidan är omgjord för att göra materialet mer läsbart och lättare att hitta i.",
    )
    parser.add_argument("--collection-file", default="")
    parser.add_argument("--collection-slug", default="")
    parser.add_argument("--cleanup-level", choices=["minimal", "aggressive"], default="minimal")
    return parser.parse_args(argv)


def iter_html_files(site_dir: Path) -> list[Path]:
    return sorted(path for path in site_dir.rglob("*.html") if "_assets" not in path.parts and "recovery" not in path.parts)


def relpath_to_theme(html_path: Path, site_dir: Path) -> str:
    depth = len([part for part in html_path.relative_to(site_dir).as_posix().split("/")[:-1] if part])
    return ("../" * depth) + THEME_RELATIVE_PATH


def classify_path(relative: str) -> tuple[str, int | None, int | None, int | None]:
    if relative == "index.html":
        return "home", None, None, None
    if relative == "browse/index.html":
        return "browse", None, None, None
    if relative.endswith("/feed/index.html") or relative == "feed/index.html":
        return "feed", None, None, None
    post_match = re.match(r"(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/[^/]+/index\.html$", relative)
    if post_match:
        return "post", int(post_match.group("year")), int(post_match.group("month")), int(post_match.group("day"))
    archive_match = re.match(r"(?P<year>\d{4})/(?P<month>\d{2})/index\.html$", relative)
    if archive_match:
        return "archive", int(archive_match.group("year")), int(archive_match.group("month")), None
    if relative.startswith("category/"):
        return "category", None, None, None
    if relative.startswith("tag/"):
        return "tag", None, None, None
    if relative.startswith("page/"):
        return "pagination", None, None, None
    if relative.endswith("feed.xml"):
        return "feed", None, None, None
    return "other", None, None, None


def kind_label(kind: str) -> str:
    return {
        "home": "Startsida",
        "browse": "Utforskare",
        "post": "Artikel",
        "archive": "Arkiv",
        "category": "Kategori",
        "tag": "Tagg",
        "pagination": "Paginering",
        "feed": "Flöde",
        "other": "Sida",
    }.get(kind, "Sida")


def date_label(year: int | None, month: int | None, day: int | None) -> str:
    if year and month and day:
        return f"{year:04d}-{month:02d}-{day:02d}"
    if year and month:
        return f"{year:04d}-{month:02d}"
    return f"{year:04d}" if year else ""


def maybe_fix_mojibake(text: str) -> str:
    markers = ("Ã", "Â", "â", "¤", "�")
    if not text or not any(marker in text for marker in markers):
        return text
    try:
        repaired = text.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return text
    original_score = sum(text.count(marker) for marker in markers)
    repaired_score = sum(repaired.count(marker) for marker in markers)
    return repaired if repaired_score < original_score else text


def repair_common_mojibake_sequences(text: str) -> str:
    replacements = {
        "Ã¥": "å",
        "Ã¤": "ä",
        "Ã¶": "ö",
        "Ã…": "Å",
        "Ã„": "Ä",
        "Ã–": "Ö",
        "Ã©": "é",
        "Ã‰": "É",
        "Â»": "»",
        "Â«": "«",
        "Â": "",
        "â€“": "–",
        "â€”": "—",
        "â€œ": "“",
        "â€": "”",
        "â€˜": "‘",
        "â€™": "’",
        "â€¦": "…",
    }
    fixed = text
    for source, target in replacements.items():
        fixed = fixed.replace(source, target)
    return fixed


def normalize_display_text(text: str) -> str:
    fixed = repair_common_mojibake_sequences(maybe_fix_mojibake(html.unescape(text or ""))).strip()
    fixed = re.sub(r"^\s*(?:&raquo;|»)\s*", "", fixed)
    fixed = re.sub(r"\s+Bollplanket\s*$", "", fixed).strip()
    return fixed


def strip_html_text(text: str) -> str:
    return normalize_display_text(re.sub(r"<[^>]+>", " ", text or ""))


def is_probable_spam_comment(comment_html: str) -> bool:
    plain = strip_html_text(comment_html).lower()
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', comment_html, flags=re.IGNORECASE)
    suspicious_host = any(
        re.search(r"https?://", href, flags=re.IGNORECASE)
        and not re.search(
            r"(?:^https?://)?(?:[^/]+\.)?(?:skolbloggen\.se|blogspot\.com|blogger\.com|wordpress\.com)(?:/|$)",
            href,
            flags=re.IGNORECASE,
        )
        for href in hrefs
    )
    suspicious_name = bool(
        re.search(
            r"\b(?:casino|loan|credit|seo|marketing|renovation|roofing|plumbing|supplier|furniture|real\s*estate)\b",
            plain,
            flags=re.IGNORECASE,
        )
        or re.search(r"[a-z0-9]+(?:-[a-z0-9]+){1,}", plain)
    )
    suspicious_body = bool(
        re.search(
            r"\b(?:net worth|montreal area|project manager|material suppliers|furniture outlets|owning a home|renovation work|real estate|payday loan|online casino|essay writing|seo services|viagra)\b",
            plain,
            flags=re.IGNORECASE,
        )
    )
    english_seo_style = bool(
        suspicious_host
        and re.search(r"\b(?:the|and|you|your|home|work|project|suppliers|manager|increase)\b", plain)
        and not re.search(r"\b(?:och|att|det|som|jag|inte|med|för|på|är|du)\b", plain)
    )
    return sum([suspicious_host, suspicious_name, suspicious_body, english_seo_style]) >= 2


def remove_probable_spam_comments(html_text: str) -> str:
    pattern = re.compile(r'(<li\b[^>]*\bid=["\']comment-\d+["\'][^>]*>.*?</li>)', flags=re.IGNORECASE | re.DOTALL)

    def replace(match: re.Match[str]) -> str:
        comment_html = match.group(1)
        return "" if is_probable_spam_comment(comment_html) else comment_html

    cleaned = pattern.sub(replace, html_text)
    cleaned = re.sub(r"<ol class=\"commentlist\">\s*</ol>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<ul id=\"comments\" class=\"commentlist\">\s*</ul>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    return cleaned


def extract_title(html_text: str) -> str:
    for pattern in (r'<h1 class="page-title">(.*?)</h1>', r'<h1 class="entry-title">(.*?)</h1>', r'<h1 class="entry-title"><a [^>]+>(.*?)</a></h1>', r"<title>(.*?)</title>"):
        match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return normalize_display_text(re.sub(r"<[^>]+>", "", match.group(1)))
    return "Utan titel"


def extract_summary(html_text: str) -> str:
    for pattern in (r'<div class="entry-summary">(.*?)</div>', r'<div class="entry-content">(.*?)</div>', r"<p>(.*?)</p>"):
        match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            text = normalize_display_text(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(1))))
            if text:
                return text[:220].rstrip() + ("..." if len(text) > 220 else "")
    return ""


def is_reconstructed_post_summary(summary: str) -> bool:
    normalized = normalize_display_text(summary).lower()
    return normalized.startswith("den fullständiga artikelsidan kunde inte återfinnas som egen capture i wayback machine")


def split_post_pages(pages: list[PageMeta]) -> tuple[list[PageMeta], list[PageMeta]]:
    full_posts: list[PageMeta] = []
    reconstructed_posts: list[PageMeta] = []
    for page in pages:
        if page.kind != "post":
            continue
        if is_reconstructed_post_summary(page.summary):
            reconstructed_posts.append(page)
        else:
            full_posts.append(page)
    return full_posts, reconstructed_posts


def pretty_slug(relative: str) -> str:
    cleaned = relative.removesuffix("/index.html").strip("/")
    if cleaned.startswith("category/"):
        cleaned = cleaned[len("category/") :]
    elif cleaned.startswith("tag/"):
        cleaned = cleaned[len("tag/") :]
    cleaned = cleaned.replace("/page/", " sida ").replace("-", " ")
    return " ".join(part.capitalize() for part in cleaned.split())


def build_page_meta(site_dir: Path) -> list[PageMeta]:
    pages: list[PageMeta] = []
    for html_path in iter_html_files(site_dir):
        relative = html_path.relative_to(site_dir).as_posix()
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        kind, year, month, day = classify_path(relative)
        pages.append(PageMeta(relative, extract_title(html_text), kind, year, month, day, extract_summary(html_text), kind_label(kind), date_label(year, month, day)))
    return pages


def search_index_records(pages: list[PageMeta]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for page in pages:
        if page.kind == "browse":
            continue
        records.append({"path": page.path, "title": page.title, "kind": page.kind, "kind_label": page.kind_label, "year": page.year, "date_label": page.date_label, "sort_date": f"{page.year or 0:04d}-{page.month or 0:02d}-{page.day or 0:02d}", "summary": page.summary})
    return records


def build_topbar_search(prefix: str) -> str:
    return f'<div class="recovery-topbar__search"><form action="{prefix}browse/index.html" method="get"><input type="search" name="q" placeholder="Sök bland artiklar och sidor" /><button type="submit">Sök</button></form></div>'


def build_topbar_brand(label: str) -> str:
    return f'<a class="recovery-topbar__brand" href="index.html">{html.escape(label)}</a>'


def build_browse_page(pages: list[PageMeta], post_records: list[PostRecord], site_label: str = "BUF Simrishamn", collection_items: list[CollectionNavItem] | None = None) -> str:
    full_posts, reconstructed_posts = split_post_pages(pages)
    posts = sorted((p for p in pages if p.kind == "post"), key=lambda p: (p.year or 0, p.month or 0, p.day or 0, p.path), reverse=True)
    archives = sorted((p for p in pages if p.kind == "archive"), key=lambda p: (p.year or 0, p.month or 0), reverse=True)
    categories = sorted((p for p in pages if p.kind == "category"), key=lambda p: p.title.lower())
    tags = sorted((p for p in pages if p.kind == "tag"), key=lambda p: p.title.lower())
    years = sorted({p.year for p in pages if p.year is not None}, reverse=True)
    year_options = "\n".join(f'<option value="{year}">{year}</option>' for year in years)
    archive_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    for record in post_records:
        archive_path = "/".join(record.path.split("/")[:2]) + "/index.html"
        archive_counts[archive_path] = archive_counts.get(archive_path, 0) + 1
        for href, _ in record.categories:
            category_counts[href] = category_counts.get(href, 0) + 1
        for href, _ in record.tags:
            tag_counts[href] = tag_counts.get(href, 0) + 1
    visible_archives = [page for page in archives if archive_counts.get(page.path, 0) > 0] or archives
    visible_categories = [page for page in categories if category_counts.get(page.path, 0) > 0] or categories
    visible_tags = [page for page in tags if tag_counts.get(page.path, 0) > 0] or tags
    recent_cards = "\n".join(
        f'<li><a href="../{p.path}"><strong>{html.escape(p.title)}</strong><span>{html.escape(p.date_label or "Artikel")}</span></a></li>'
        for p in posts[:10]
    )
    archive_cards = "\n".join(
        f'<li><a href="../{p.path}"><strong>{p.year:04d}-{p.month:02d}</strong><span>{archive_counts.get(p.path, 0)} artiklar</span></a></li>'
        for p in visible_archives[:14]
        if p.year and p.month
    )
    category_cards = "\n".join(
        f'<li><a href="../{p.path}"><strong>{html.escape(pretty_slug(p.path))}</strong><span>{category_counts.get(p.path, 0)} artiklar</span></a></li>'
        for p in sorted(visible_categories, key=lambda page: (-category_counts.get(page.path, 0), page.title.lower()))[:14]
    )
    tag_cloud = " ".join(
        f'<a class="recovery-chip" href="../{p.path}">{html.escape(pretty_slug(p.path))} <strong>{tag_counts.get(p.path, 0)}</strong></a>'
        for p in sorted(visible_tags, key=lambda page: (-tag_counts.get(page.path, 0), page.title.lower()))[:36]
    )
    archive_list = "\n".join(
        f'<li><a href="../{p.path}"><strong>{p.year:04d}-{p.month:02d}</strong><span>{archive_counts.get(p.path, 0)} artiklar</span></a></li>'
        for p in visible_archives[:48]
        if p.year and p.month
    )
    category_list = "\n".join(
        f'<li><a href="../{p.path}"><strong>{html.escape(pretty_slug(p.path))}</strong><span>{category_counts.get(p.path, 0)} artiklar</span></a></li>'
        for p in sorted(visible_categories, key=lambda page: (-category_counts.get(page.path, 0), page.title.lower()))[:60]
    )
    tag_list = "\n".join(
        f'<li><a href="../{p.path}"><strong>{html.escape(pretty_slug(p.path))}</strong><span>{tag_counts.get(p.path, 0)} artiklar</span></a></li>'
        for p in sorted(visible_tags, key=lambda page: (-tag_counts.get(page.path, 0), page.title.lower()))[:108]
    )
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Utforska \u00e5terst\u00e4lld sajt</title>
{ROBOTS_META_TAG}
<link rel="stylesheet" href="../{THEME_RELATIVE_PATH}" />
<script defer src="../{SEARCH_SCRIPT_RELATIVE_PATH}"></script>
</head>
<body class="recovery-enhanced">
{build_topbar("browse/index.html", site_label, collection_items)}
<main class="recovery-catalog">
<section class="recovery-browse-layout">
<div class="recovery-browse-main">
<section id="search" class="recovery-section recovery-search-panel"><div class="recovery-section-header"><div><h2>S\u00f6k i den lokala kopian</h2><p>S\u00f6k i titlar, sammanfattningar, kategorier, taggar och \u00e5r. Resultaten uppdateras direkt.</p></div></div><form data-search-form><div class="recovery-search-controls"><div class="recovery-field"><label for="recovery-search-query">S\u00f6kord</label><input id="recovery-search-query" data-search-query type="search" placeholder="Titel, \u00e4mne, person, kategori..." /></div><div class="recovery-field"><label for="recovery-search-year">\u00c5r</label><select id="recovery-search-year" data-search-year><option value="all">Alla \u00e5r</option>{year_options}</select></div></div><div class="recovery-filter-row" aria-label="Filtrera p\u00e5 typ"><button type="button" class="is-active" data-search-kind="all">Allt</button><button type="button" data-search-kind="post">Artiklar</button><button type="button" data-search-kind="archive">Arkiv</button><button type="button" data-search-kind="category">Kategorier</button><button type="button" data-search-kind="tag">Taggar</button><button type="button" data-search-kind="other">\u00d6vriga sidor</button><button type="button" data-search-kind="feed">Fl\u00f6den</button></div></form><div class="recovery-results-meta" data-search-meta>Laddar s\u00f6kindex...</div><div class="recovery-results" data-search-results></div></section>
</div>
<aside class="recovery-browse-sidebar">
<section id="categories" class="recovery-card recovery-card--dense"><div class="recovery-card__header"><h2>Alla kategorier</h2><span class="recovery-meta">{len(categories)} st</span></div><ul class="recovery-link-list">{category_list}</ul></section>
<section id="archives" class="recovery-card recovery-card--dense"><div class="recovery-card__header"><h2>Alla m\u00e5nadsarkiv</h2><span class="recovery-meta">{len(archives)} st</span></div><ul class="recovery-link-list">{archive_list}</ul></section>
<section id="recent" class="recovery-card recovery-card--dense"><div class="recovery-card__header"><h2>Senaste poster</h2><span class="recovery-meta">{len(full_posts)} artikelsidor, {len(reconstructed_posts)} rekonstruerade poster</span></div><ul class="recovery-link-list">{recent_cards}</ul><p class="recovery-card__footer"><a href="#search">S\u00f6k bland alla poster</a></p></section>
<section id="tags" class="recovery-card recovery-card--dense recovery-tag-panel"><div class="recovery-card__header"><h2>Taggar</h2><span class="recovery-meta">{len(tags)} st</span></div><div class="recovery-tag-cloud">{tag_cloud}</div><ul class="recovery-link-list">{tag_list}</ul></section>
</aside>
</section>
</main>
</body>
</html>"""


def build_home_page(
    pages: list[PageMeta],
    site_title: str = "Barn- och utbildning Simrishamn",
    site_label: str = "BUF Simrishamn",
    site_intro: str = "Detta är en lokal, återställd version av den borttagna sajten. Startsidan är omgjord för att göra materialet mer läsbart och lättare att hitta i.",
) -> str:
    full_posts, reconstructed_posts = split_post_pages(pages)
    posts = sorted((p for p in pages if p.kind == "post"), key=lambda p: (p.year or 0, p.month or 0, p.day or 0, p.path), reverse=True)
    years = sorted({p.year for p in posts if p.year is not None}, reverse=True)
    by_year: dict[int, list[PageMeta]] = {year: [] for year in years}
    for post in posts:
        if post.year is not None:
            by_year.setdefault(post.year, []).append(post)
    year_cards = "\n".join(
        f'<article class="recovery-card"><h2><a href="browse/index.html?year={year}&kind=post">{year}</a></h2><p class="recovery-meta">{len(by_year[year])} poster</p><p><a class="recovery-chip" href="browse/index.html?year={year}&kind=post">Visa poster fr\u00e5n {year}</a></p></article>'
        for year in years
    )
    latest = "\n".join(f'<li><a href="{p.path}">{html.escape(p.title)}</a></li>' for p in posts[:18])
    year_summary = "\n".join(f"<li><strong>{year}</strong>: {len(by_year[year])} poster</li>" for year in years)
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(site_title)}</title>
{ROBOTS_META_TAG}
<link rel="stylesheet" href="{THEME_RELATIVE_PATH}" />
</head>
<body class="recovery-enhanced">
{build_topbar("index.html", site_label, CURRENT_COLLECTION_ITEMS)}
<main class="recovery-catalog">
<div class="recovery-hero"><section class="recovery-intro"><h1>{html.escape(site_title)}</h1><p>{html.escape(site_intro)}</p><div class="recovery-quicklinks"><a href="browse/index.html">\u00d6ppna utforskaren</a><a href="browse/index.html#search">S\u00f6k direkt</a><a href="recovery/index.html">L\u00e4s rapporten</a></div></section><section class="recovery-card"><h2>Tidslinje</h2><ul>{year_summary}</ul><p class="recovery-meta">{len(full_posts)} artikelsidor och {len(reconstructed_posts)} rekonstruerade poster i den lokala kopian.</p></section></div>
<section class="recovery-section"><h2>\u00c5r f\u00f6r \u00e5r</h2><div class="recovery-grid">{year_cards}</div></section>
<section class="recovery-section"><h2>Senast \u00e5terfunna poster</h2><ul class="recovery-list">{latest}</ul></section>
<section class="recovery-section"><h2>Orientering</h2><div class="recovery-grid"><article class="recovery-card"><h2>Utforska allt</h2><p>S\u00f6k och filtrera bland artiklar, arkiv, kategorier och taggar.</p><p><a class="recovery-chip" href="browse/index.html">Till utforskaren</a></p></article><article class="recovery-card"><h2>Kategorier och taggar</h2><p>Om du letar efter \u00e4mnen eller personer \u00e4r taggar och kategorier ofta snabbaste v\u00e4gen.</p><p><a class="recovery-chip" href="browse/index.html#categories">Kategorier</a> <a class="recovery-chip" href="browse/index.html#tags">Taggar</a></p></article></div></section>
</main>
</body>
</html>"""


def load_json_file(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def build_report_page(
    site_dir: Path,
    pages: list[PageMeta],
    site_title: str = "Barn- och utbildning Simrishamn",
    site_label: str = "BUF Simrishamn",
) -> str:
    manifest = load_json_file(site_dir / "recovery" / "manifest.json")
    summary = load_json_file(site_dir.parent / "out" / "summary.json")
    assets_summary = load_json_file(site_dir / "recovery" / "assets-summary.json")
    priority_assets_summary = load_json_file(site_dir / "recovery" / "priority-assets-summary.json")
    full_posts, reconstructed_posts = split_post_pages(pages)
    post_count = len(full_posts)
    reconstructed_post_count = len(reconstructed_posts)
    archive_count = sum(1 for page in pages if page.kind == "archive")
    tag_count = sum(1 for page in pages if page.kind == "tag")
    category_count = sum(1 for page in pages if page.kind == "category")
    pagination_count = sum(1 for page in pages if page.kind == "pagination")
    home_count = sum(1 for page in pages if page.kind == "home")
    browse_count = sum(1 for page in pages if page.kind == "browse")
    other_count = sum(1 for page in pages if page.kind == "other")
    feed_count = sum(1 for page in pages if page.kind == "feed")
    taxonomy_count = archive_count + category_count + tag_count
    navigation_count = home_count + browse_count + pagination_count + other_count + feed_count
    local_page_count = len(pages)
    downloaded_count = int(manifest.get("downloaded_count", 0) or 0)
    skipped_count = int(manifest.get("skipped_count", 0) or 0)
    failed_count = int(manifest.get("failed_count", 0) or 0)
    unique_url_count = int(summary.get("unique_url_count", 0) or 0)
    capture_count = int(summary.get("capture_count", 0) or 0)
    asset_downloaded_count = int(assets_summary.get("downloaded_count", 0) or 0)
    priority_group_count = int(priority_assets_summary.get("group_count", 0) or 0)
    priority_downloaded_count = int(priority_assets_summary.get("downloaded_count", 0) or 0)
    priority_failed_count = int(priority_assets_summary.get("failed_count", 0) or 0)
    local_asset_count = sum(1 for path in (site_dir / "_assets").rglob("*") if path.is_file()) if (site_dir / "_assets").exists() else 0
    if asset_downloaded_count == 0 and priority_downloaded_count:
        asset_downloaded_count = priority_downloaded_count
    asset_downloaded_count = max(asset_downloaded_count, priority_downloaded_count, local_asset_count)
    kind_counts = summary.get("kind_counts", {}) if isinstance(summary.get("kind_counts"), dict) else {}
    kind_list = "".join(
        f"<li><strong>{html.escape(str(kind))}</strong>: {html.escape(str(count))}</li>"
        for kind, count in sorted(kind_counts.items())
    )
    return f"""<!DOCTYPE html>
<html lang="sv">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Återställningsrapport</title>
{ROBOTS_META_TAG}
<link rel="stylesheet" href="../{THEME_RELATIVE_PATH}" />
</head>
<body class="recovery-enhanced">
{build_topbar("recovery/index.html", site_label, CURRENT_COLLECTION_ITEMS)}
<main class="recovery-catalog">
<div class="recovery-hero">
<section class="recovery-intro">
<h1>Återställningsrapport</h1>
<p>Den här sidan sammanfattar vad som faktiskt har återställts lokalt för {html.escape(site_title)}, vilka datakällor som användes och vilka delar som fortfarande bara finns som rådata eller delvis kompletterad media.</p>
<div class="recovery-quicklinks"><a href="../index.html">Till startsidan</a><a href="../browse/index.html">Öppna utforskaren</a><a href="../browse/index.html?kind=post">Visa artiklar</a></div>
</section>
<section class="recovery-card">
<h2>Status</h2>
<p>{downloaded_count} filer återställda lokalt, {failed_count} misslyckade och {skipped_count} hoppade över i grundkörningen.</p>
<p class="recovery-meta">Rapportsidan bygger på filer i <code>site/recovery</code> och <code>out</code>.</p>
</section>
</div>
<section class="recovery-section">
<div class="recovery-grid">
<article class="recovery-card"><h2>Återställda sidor</h2><p><strong>{local_page_count}</strong> lokala HTML-sidor totalt.</p><ul><li><strong>Artikelsidor:</strong> {post_count}</li><li><strong>Rekonstruerade artikelposter:</strong> {reconstructed_post_count}</li><li><strong>Navigationssidor:</strong> {navigation_count}</li><li><strong>Tagg/Kategori/Arkiv:</strong> {taxonomy_count}</li><li><strong>Assets:</strong> {asset_downloaded_count}</li></ul></article>
<article class="recovery-card"><h2>CDX-inventering</h2><p><strong>{unique_url_count}</strong> unika URL:er och <strong>{capture_count}</strong> captures i sammanställningen från CDX.</p></article>
<article class="recovery-card"><h2>Media</h2><p><strong>{asset_downloaded_count}</strong> assets hämtade i stegvisa batchar. Prioriterad mediaanalys omfattade <strong>{priority_group_count}</strong> grupper och gav <strong>{priority_failed_count}</strong> kvarstående fel i senaste snabbspåret.</p></article>
</div>
</section>
<section class="recovery-section">
<div class="recovery-grid">
<article class="recovery-card">
<h2>Källfiler</h2>
<ul>
<li><a href="manifest.json">manifest.json</a></li>
<li><a href="assets-summary.json">assets-summary.json</a></li>
<li><a href="priority-assets-summary.json">priority-assets-summary.json</a></li>
<li><a href="../../out/summary.json">out/summary.json</a></li>
<li><a href="../../out/urls_unique.csv">out/urls_unique.csv</a></li>
<li><a href="../../out/captures_raw.csv">out/captures_raw.csv</a></li>
</ul>
</article>
<article class="recovery-card">
<h2>Innehållstyper</h2>
<ul>{kind_list}</ul>
</article>
<article class="recovery-card">
<h2>Tolkning</h2>
<p>Lokalsajten är avsedd som en läsbar arkivkopia. Interaktiva WordPress-funktioner, inloggning, registrering, cookie-dialoger och annan teknisk plattformsbrus har därför tagits bort, medan publicerat innehåll, bevarade kommentarer, intern navigering och arkivstruktur har behållits eller byggts om för statisk visning.</p>
</article>
</div>
</section>
</main>
</body>
</html>"""


def clean_html(html_text: str) -> str:
    html_text = maybe_fix_mojibake(html_text)
    patterns = [
        r"<script\b[^>]*>.*?</script>",
        r'<link\b[^>]+rel="dns-prefetch"[^>]*>\s*',
        r'<link\b[^>]+rel="pingback"[^>]*>\s*',
        r'<link\b[^>]+rel="profile"[^>]*>\s*',
        r'<link\b[^>]+rel="EditURI"[^>]*>\s*',
        r'<link\b[^>]+rel="wlwmanifest"[^>]*>\s*',
        r'<link\b[^>]+rel="shortlink"[^>]*>\s*',
        r'<link\b[^>]+rel="openid[^"]*"[^>]*>\s*',
        r'<link\b[^>]+rel="apple-touch-icon-precomposed"[^>]*>\s*',
        r'<link\b(?=[^>]*\brel="stylesheet")(?=[^>]*\bhref="(?:https?:)?//[^"]+")([^>]*)>\s*',
        r'<link\b[^>]+href="[^"]*(?:wp\.com|wordpress\.com|widgets\.wp\.com)[^"]*"[^>]*>\s*',
        r"<link\b[^>]+href='[^']*(?:wp\.com|wordpress\.com|widgets\.wp\.com)[^']*'[^>]*>\s*",
        r'<link\b[^>]+rel="(?:shortcut )?icon"[^>]*>\s*',
        r'<link\b[^>]+rel="search"[^>]*>\s*',
        r'<style id="jetpack-custom-fonts-css"></style>\s*',
        r'<meta name="generator"[^>]*>\s*',
        r'<meta name="twitter:[^"]*"[^>]*>\s*',
        r'<meta property="og:[^"]*"[^>]*>\s*',
        r'<meta property="fb:app_id"[^>]*>\s*',
        r'<div id="sharing_email"[^>]*>.*?</div>\s*',
        r'<div id="carousel-reblog-box"[^>]*>.*?</div>\s*',
        r'<div class="widget widget_eu_cookie_law_widget"[^>]*>.*?</div>\s*',
        r'<div id="likes-other-gravatars"[^>]*>.*?</div>\s*',
        r'<iframe[^>]+id="likes-master"[^>]*>.*?</iframe>\s*',
        r'<div id="jp-post-flair"[^>]*>.*?</div>\s*',
        r'<li[^>]*id="bp-adminbar-[^"]*"[^>]*>.*?</li>\s*',
        r'<li[^>]*class="[^"]*\bbp-login\b[^"]*"[^>]*>.*?</li>\s*',
        r'<li[^>]*class="[^"]*\bbp-signup\b[^"]*"[^>]*>.*?</li>\s*',
        r'<form\b[^>]*id="adminloginform"[^>]*>.*?</form>\s*',
        r'<form\b[^>]*action="[^"]*wp-login\.php"[^>]*>.*?</form>\s*',
        r'<li>\s*<a href="[^"]*wp-login\.php\?action=register"[^>]*>Registrera</a>\s*</li>\s*',
        r'<li>\s*<a href="[^"]*wp-login\.php"[^>]*>Logga in</a>\s*</li>\s*',
        r'<li[^>]*class="secondary"[^>]*>\s*<a href="[^"]*wp-login\.php(?:\?action=register)?"[^>]*>(?:Registrera|Logga in)</a>\s*</li>\s*',
        r'<div id="respond"[^>]*>.*?</div><!-- #respond -->\s*',
        r'<div id="respond"[^>]*>.*?</div>\s*',
        r'<form\b[^>]*id="commentform"[^>]*>.*?</form>\s*',
        r'<form\b[^>]*class="comment-form"[^>]*>.*?</form>\s*',
        r'<a [^>]*class="comment-reply-link"[^>]*>.*?</a>\s*',
        r'<h3[^>]*id="reply-title"[^>]*>.*?</h3>\s*',
        r'<p class="must-log-in">.*?</p>\s*',
        r'<p class="comment-notes">.*?</p>\s*',
        r'<p[^>]*id="you-must-be-logged-in-to-comment"[^>]*>.*?</p>\s*',
        r'<p[^>]*>\s*Stay in touch with the conversation.*?</p>\s*',
        r'<h3[^>]*class="pings"[^>]*>.*?</h3>\s*',
        r'<ol[^>]*class="[^"]*\bpinglist\b[^"]*\bcommentlist\b[^"]*"[^>]*>.*?</ol>\s*',
        r'<footer id="colophon"[^>]*>.*?</footer><!-- #colophon -->\s*',
        r'<aside id="meta-[^"]*" class="widget widget_meta">.*?</aside>\s*',
        r'<aside id="blog_subscription-[^"]*" class="widget widget_blog_subscription[^"]*">.*?</aside>\s*',
        r'<aside id="search-[^"]*" class="widget widget_search">.*?</aside>\s*',
        r'<nav id="access"[^>]*>.*?</nav><!-- #access -->\s*',
        r'<div id="secondary" class="widget-area"[^>]*>.*?</div><!-- #secondary \.widget-area -->\s*',
        r'<div id="tertiary" class="widget-area"[^>]*>.*?</div><!-- #tertiary \.widget-area -->\s*',
        r'<div class="wpcnt">.*?</div>\s*',
        r'<div class="wpa [^"]*">.*?</div>\s*',
        r'<aside id="flickr-[^"]*" class="widget widget_flickr">.*?</aside>\s*',
        r'<aside id="archives-[^"]*" class="widget widget_archive">.*?</aside>\s*',
        r'<aside id="categories-[^"]*" class="widget widget_categories">.*?</aside>\s*',
        r'<aside id="recent-posts-[^"]*" class="widget widget_recent_entries">.*?</aside>\s*',
        r'<div id="carrington-subscribe" class="widget">.*?</div>\s*',
        r'<div id="linkcat-[^"]*" class="widget widget_links">.*?</div>\s*',
        r'<li id="recent-comments-[^"]*" class="widget[^"]*widget_recent_comments[^"]*">.*?</li>\s*',
        r'<li id="tag_cloud-[^"]*" class="widget[^"]*widget_tag_cloud[^"]*">.*?</li>\s*',
        r'<li id="archives-[^"]*" class="widget[^"]*widget_archive[^"]*">.*?</li>\s*',
        r'<li id="categories-[^"]*" class="widget[^"]*widget_categories[^"]*">.*?</li>\s*',
        r'<li id="recent-posts-[^"]*" class="widget[^"]*widget_recent_entries[^"]*">.*?</li>\s*',
        r'<li id="pages-[^"]*" class="widget[^"]*widget_pages[^"]*">.*?</li>\s*',
        r'<li id="linkcat-[^"]*" class="widget[^"]*widget_links[^"]*">.*?</li>\s*',
        r'<div id="recent-comments-[^"]*" class="widget[^"]*widget_recent_comments[^"]*">.*?</div>\s*',
        r'<div id="tag_cloud-[^"]*" class="widget[^"]*widget_tag_cloud[^"]*">.*?</div>\s*',
        r'<div id="archives-[^"]*" class="widget[^"]*widget_archive[^"]*">.*?</div>\s*',
        r'<div id="categories-[^"]*" class="widget[^"]*widget_categories[^"]*">.*?</div>\s*',
        r'<div id="recent-posts-[^"]*" class="widget[^"]*widget_recent_entries[^"]*">.*?</div>\s*',
        r'<div id="pages-[^"]*" class="widget[^"]*widget_pages[^"]*">.*?</div>\s*',
        r'<li id="search-[^"]*" class="widget widget_search">.*?</li>\s*',
        r'<div id="search-[^"]*" class="widget widget_search">.*?</div>\s*',
        r'<li id="meta-[^"]*" class="widget widget_meta">.*?</li>\s*',
        r'<form method="get" id="cfct-search" .*?</form>\s*',
        r'<div style="display:none">\s*</div>\s*',
        r'<noscript><img src="https://pixel\.wp\.com/b\.gif[^"]*"[^>]*></noscript>\s*',
    ]
    cleaned = html_text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<div id="wpadminbar"[^>]*>.*?</div>\s*', "", cleaned, count=1, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<li[^>]*id="wp-admin-bar-lostpassword"[^>]*>.*?</li>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<li[^>]*id="wp-admin-bar-register"[^>]*>.*?</li>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(
        r'<!-- footer .*?-->\s*(?:<div id="footer">.*?(?:</div>\s*<!-- /footer -->|</div>)\s*)?',
        "",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(r'<div id="footer">.*?(?:</div>\s*<!-- /footer -->|</div>)', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'&copy;\s*\d{4}\s+[^<]*Theme:.*?(?:Hosted by\s*<a[^>]+>Skolbloggen</a>)?\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<a href="http://wordpress\.org">WordPress</a>\.\s*Powered by\s*<a href="http://wordpressmu\.org">WordPress MU</a>\.\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<br\s*/?>\s*Powered by\s*<a href="http://mu\.wordpress\.org">WordPress MU</a>\s*&amp;\s*designed by\s*<a href="http://ifelse\.co\.uk">Phu Ly</a>\.\s*Powered by\s*<a href="http://wordpressmu\.org">WordPress MU</a>\.\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Powered by\s*<a[^>]+>\s*WordPress MU\s*</a>\.?\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Proudly powered by\s*<a[^>]+>\s*WordPress\s*</a>\s*and\s*<a[^>]+>\s*Carrington\s*</a>\.?\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Carrington Theme by\s*<a[^>]+>.*?</a>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Powered by WordPress\.\s*Built on the\s*Thematic Theme Framework\.?\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Built on the\s*<a[^>]+>\s*Thematic Theme Framework\s*</a>\.?\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Hosted by\s*<a[^>]+>\s*Skolbloggen\s*</a>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'Theme:\s*[^<]+by\s*<a[^>]+>.*?</a>\.?\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<p id="generator-link">.*?</p>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<p id="developer-link">.*?</p>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<a class="screen-reader-shortcut" href="#wp-toolbar"[^>]*>Hoppa till verktygsfältet</a>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<li class="alt"><a href="https?://skolbloggen\.se/groups/\?random-group"[^>]*>.*?</a></li>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<li>\s*<a href="https?://skolbloggen\.se/blogs/\?random-blog"[^>]*>.*?</a>\s*</li>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<li>\s*<a href="https?://skolbloggen\.se/register/"[^>]*>Registrera</a>\s*</li>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<li>\s*<a href="https?://wordpress\.org/"[^>]*>WordPress\.org</a>\s*</li>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'</form><div class="clear"></div></div>', "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'</li></ul></li>\s*<li class="alt"><a href="https?://skolbloggen\.se/groups/\?random-group"[^>]*>.*$', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<!-- Generated in .*?seconds\.\s*\(\d+\s*q\)\s*-->', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<!--\s*#wp-admin-bar\s*-->', "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'<!--\s*/footer\s*-->', "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'<div id="secondary"[^>]*>.*?</div>\s*(?:<!--\s*#secondary.*?-->)?', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<div id="tertiary"[^>]*>.*?</div>\s*(?:<!--\s*#tertiary.*?-->)?', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<aside id="secondary"[^>]*>.*?</aside>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<aside id="tertiary"[^>]*>.*?</aside>\s*', "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'(</div><!-- #page -->).*?(</body>)', r"\1\n\n\2", cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'<!-- #masthead -->', "", cleaned, flags=re.IGNORECASE)
    return cleaned


def minimal_clean_html(html_text: str) -> str:
    cleaned = maybe_fix_mojibake(html_text)
    safe_patterns = [
        r'<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->\s*',
        r'<link rel="stylesheet" type="text/css" href="https://web-static\.archive\.org/_static/css/banner-styles\.css[^"]*" */?>\s*',
        r'<link rel="stylesheet" type="text/css" href="https://web-static\.archive\.org/_static/css/iconochive\.css[^"]*" */?>\s*',
        r'<div id="wm-ipp-print">.*?</div>\s*',
        r"<script\b[^>]*>.*?</script>",
        r'<li[^>]*id="bp-adminbar-[^"]*"[^>]*>.*?</li>\s*',
        r'<li[^>]*class="[^"]*\bbp-login\b[^"]*"[^>]*>.*?</li>\s*',
        r'<li[^>]*class="[^"]*\bbp-signup\b[^"]*"[^>]*>.*?</li>\s*',
        r'<li[^>]*id="wp-admin-bar-lostpassword"[^>]*>.*?</li>\s*',
        r'<li[^>]*id="wp-admin-bar-register"[^>]*>.*?</li>\s*',
        r'<form\b[^>]*id="adminloginform"[^>]*>.*?</form>\s*',
        r'<form\b[^>]*action="[^"]*wp-login\.php"[^>]*>.*?</form>\s*',
        r'<li>\s*<a href="[^"]*wp-login\.php\?action=register"[^>]*>Registrera</a>\s*</li>\s*',
        r'<li>\s*<a href="[^"]*wp-login\.php"[^>]*>Logga in</a>\s*</li>\s*',
        r'<li[^>]*class="secondary"[^>]*>\s*<a href="[^"]*wp-login\.php(?:\?action=register)?"[^>]*>(?:Registrera|Logga in)</a>\s*</li>\s*',
        r'<div id="respond"[^>]*>.*?</div><!-- #respond -->\s*',
        r'<div id="respond"[^>]*>.*?</div>\s*',
        r'<form\b[^>]*id="commentform"[^>]*>.*?</form>\s*',
        r'<form\b[^>]*class="comment-form"[^>]*>.*?</form>\s*',
        r'<a [^>]*class="comment-reply-link"[^>]*>.*?</a>\s*',
        r'<h3[^>]*id="reply-title"[^>]*>.*?</h3>\s*',
        r'<p class="must-log-in">.*?</p>\s*',
        r'<p class="comment-notes">.*?</p>\s*',
        r'<p[^>]*id="you-must-be-logged-in-to-comment"[^>]*>.*?</p>\s*',
        r'<p[^>]*>\s*Stay in touch with the conversation.*?</p>\s*',
        r'<h3[^>]*class="pings"[^>]*>.*?</h3>\s*',
        r'<ol[^>]*class="[^"]*\bpinglist\b[^"]*\bcommentlist\b[^"]*"[^>]*>.*?</ol>\s*',
        r'<a class="screen-reader-shortcut" href="#wp-toolbar"[^>]*>Hoppa till verktygsf[^<]*</a>\s*',
        r'<!--\s*#wp-admin-bar\s*-->',
    ]
    for pattern in safe_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    return cleaned


def unwrap_wayback_url(url: str) -> str:
    match = re.match(r"^https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://.+)$", url, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return url


def lift_repeated_post_links(html_text: str) -> str:
    panel_blocks: list[str] = []
    html_text = re.sub(r'<aside class="recovery-sidepanel">.*?</aside>\s*', "", html_text, flags=re.IGNORECASE | re.DOTALL)

    def capture(pattern: str, text: str) -> str:
        def repl(match: re.Match[str]) -> str:
            block = match.group(0).strip()
            if block and block not in panel_blocks:
                panel_blocks.append(block)
            return ""

        return re.sub(pattern, repl, text, count=1, flags=re.IGNORECASE | re.DOTALL)

    updated = html_text
    updated = capture(r'<p class="postmetadata[^"]*">.*?</p>', updated)
    updated = capture(r'<p class="postfeedback">.*?</p>', updated)
    updated = capture(r'<p class="metadata">.*?(?:Etiketter:|Filed under|This entry was posted).*?</p>', updated)

    if not panel_blocks:
        return updated

    panel_content = "".join(block for block in panel_blocks if re.sub(r"<[^>]+>", "", block).strip())
    if not panel_content:
        return updated
    panel_html = '<aside class="recovery-sidepanel"><h3>Artikelinfo</h3>' + panel_content + "</aside>"
    for marker in ('<div class="entrytext">', '<div class="postentry">', '<div class="entry-content">'):
        if marker in updated:
            return updated.replace(marker, marker + panel_html, 1)
    return updated


def load_collection_nav(site_dir: Path, collection_file: str, collection_slug: str) -> list[CollectionNavItem]:
    if not collection_file or not collection_slug:
        return []
    collection_path = Path(collection_file)
    if not collection_path.is_absolute():
        collection_path = collection_path.resolve()
    if not collection_path.exists():
        return []
    try:
        payload = json.loads(collection_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    current_site_slug = site_dir.parent.name
    for collection in payload.get("collections", []):
        if collection.get("slug") != collection_slug:
            continue
        items: list[CollectionNavItem] = []
        for entry in collection.get("entries", []):
            local_path = entry.get("local_path")
            if not local_path:
                continue
            entry_slug = PurePosixPath(local_path).parts[0]
            if entry_slug == current_site_slug:
                continue
            href = PurePosixPath(*PurePosixPath(local_path).parts).as_posix()
            items.append(CollectionNavItem(title=entry.get("title", entry_slug), href=href))
        return items
    return []


def build_collection_menu(prefix: str, items: list[CollectionNavItem]) -> str:
    if not items:
        return ""
    archive_prefix = prefix + "../../"
    links = "".join(
        f'<a href="{html.escape(archive_prefix + item.href)}"><strong>{html.escape(item.title)}</strong><span>{html.escape(item.href.replace("/site/index.html", ""))}</span></a>'
        for item in items
    )
    return f'<details class="recovery-collection-menu"><summary>Samlingen</summary><div class="recovery-collection-menu__panel">{links}</div></details>'


def build_topbar(relative: str, site_label: str, collection_items: list[CollectionNavItem] | None = None) -> str:
    prefix = "../" * len([part for part in relative.split("/")[:-1] if part])
    collection_menu = build_collection_menu(prefix, collection_items or [])
    return f'<div class="recovery-topbar"><div class="recovery-topbar__inner"><a class="recovery-topbar__brand" href="{prefix}index.html">{html.escape(site_label)}</a><nav>{collection_menu}<a href="{prefix}browse/index.html">Utforska</a><a href="{prefix}recovery/index.html">Rapport</a><a class="recovery-topbar__rootlink" href="{prefix}../../index.html">← Till arkivet</a></nav>{build_topbar_search(prefix)}</div></div>'


def build_context_box(meta: PageMeta, relative: str) -> str:
    prefix = "../" * len([part for part in relative.split("/")[:-1] if part])
    crumbs = [f'<a href="{prefix}index.html">Startsida</a>']
    if meta.kind == "post":
        crumbs.append(f'<a href="{prefix}browse/index.html">Utforska</a>')
        if meta.year and meta.month:
            crumbs.append(f'<a href="{prefix}{meta.year:04d}/{meta.month:02d}/index.html">{meta.year:04d}-{meta.month:02d}</a>')
    elif meta.kind in {"archive", "category", "tag", "pagination", "other", "feed"}:
        crumbs.append(f'<a href="{prefix}browse/index.html">Utforska</a>')
    text = {
        "home": "Återställd startsida för den lokala kopian.",
        "post": "Återställd artikelsida med lokal navigation, lokal styling och sökbar katalog.",
        "archive": "Månadsarkiv från den återställda sajten.",
        "category": "Kategorisida från den återställda sajten.",
        "tag": "Taggsida från den återställda sajten.",
        "pagination": "Paginering i den återställda sajten.",
        "feed": "Arkiverat flöde i den lokala kopian.",
        "other": "Återställd sida i lokal visning.",
        "browse": "Katalog över den återställda sajten.",
    }[meta.kind]
    return f'<div class="recovery-context"><div class="recovery-context__crumbs">{" <span>/</span> ".join(crumbs)}</div><p>{html.escape(text)}</p></div>'


def extract_taxonomy_pairs(html_text: str, class_name: str, base_relative: str) -> list[tuple[str, str]]:
    match = re.search(rf'<p class="{class_name}[^"]*">(.*?)</p>', html_text, flags=re.IGNORECASE | re.DOTALL)
    pairs: list[tuple[str, str]] = []
    if match:
        pairs = re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', match.group(1), flags=re.IGNORECASE | re.DOTALL)
    elif class_name == "cat-links":
        pairs = re.findall(
            r'<a [^>]*href="([^"]+)"[^>]*rel="category tag"[^>]*>(.*?)</a>',
            html_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    elif class_name == "tag-links":
        pairs = re.findall(
            r'<a [^>]*href="([^"]+)"[^>]*rel="tag"[^>]*>(.*?)</a>',
            html_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
    result: list[tuple[str, str]] = []
    for href, label in pairs:
        text = normalize_display_text(re.sub(r"<[^>]+>", "", label))
        normalized = normalize_local_href(base_relative, href) or href
        if text:
            result.append((normalized, text))
    return result


def build_post_records(site_dir: Path, pages: list[PageMeta]) -> list[PostRecord]:
    records: list[PostRecord] = []
    for page in pages:
        if page.kind != "post":
            continue
        html_text = (site_dir / page.path).read_text(encoding="utf-8", errors="replace")
        image = extract_first_image(html_text) or ("", "")
        records.append(
            PostRecord(
                path=page.path,
                title=page.title,
                summary=page.summary,
                date_label=page.date_label,
                sort_key=(page.year or 0, page.month or 0, page.day or 0, page.path),
                author=extract_author_name(html_text),
                image_src=image[0],
                image_alt=image[1],
                categories=extract_taxonomy_pairs(html_text, "cat-links", page.path),
                tags=extract_taxonomy_pairs(html_text, "tag-links", page.path),
            )
        )
    return sorted(records, key=lambda record: record.sort_key, reverse=True)


def normalize_local_href(base_relative: str, href: str) -> str | None:
    if not href or href.startswith(("#", "mailto:", "tel:")):
        return None
    href = unwrap_wayback_url(href)
    if re.match(r"^[a-z]+://", href, flags=re.IGNORECASE):
        parsed = urlsplit(href)
        if parsed.path:
            base = PurePosixPath(parsed.path.lstrip("/"))
            if parsed.path.endswith("/"):
                return str(base / "index.html")
            suffix = base.suffix
            if suffix:
                return str(base.with_name(base.stem + ".html"))
            return str(base / "index.html")
        return None
    base_dir = PurePosixPath(base_relative).parent.as_posix()
    return posixpath.normpath(posixpath.join(base_dir, href))


def rewrite_internal_anchors(html_text: str, meta: PageMeta, pages_by_path: dict[str, PageMeta], site_label: str) -> str:
    site_host = site_label.strip().lower()

    def replace_anchor(match: re.Match[str]) -> str:
        href = match.group("href")
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            return match.group(0)

        unwrapped_href = unwrap_wayback_url(href)
        parsed = urlsplit(unwrapped_href)
        if parsed.scheme and parsed.netloc and parsed.netloc.lower() != site_host:
            return match.group(0)

        normalized = normalize_local_href(meta.path, unwrapped_href)
        if not normalized or normalized not in pages_by_path:
            return match.group(0)

        rewritten = posixpath.relpath(normalized, posixpath.dirname(meta.path))
        if parsed.query:
            rewritten += f"?{parsed.query}"
        if parsed.fragment:
            rewritten += f"#{parsed.fragment}"
        return match.group(0).replace(href, rewritten, 1)

    return re.sub(
        r'<a\b(?P<prefix>[^>]*?)\bhref=(?P<quote>"|\')(?P<href>.*?)(?P=quote)',
        replace_anchor,
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )


def extract_first_image(article_html: str) -> tuple[str, str] | None:
    content_match = re.search(r'<div class="entry-content">(.*?)</div>', article_html, flags=re.IGNORECASE | re.DOTALL)
    image_source = content_match.group(1) if content_match else article_html
    match = re.search(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*\balt="([^"]*)"[^>]*>', image_source, flags=re.IGNORECASE)
    if not match:
        match = re.search(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>', image_source, flags=re.IGNORECASE)
        if not match:
            return None
        return match.group(1), ""
    return match.group(1), html.unescape(match.group(2))


def extract_author_name(article_html: str) -> str:
    match = re.search(r'<span class="author vcard">.*?<a [^>]*>(.*?)</a>', article_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return normalize_display_text(re.sub(r"<[^>]+>", "", match.group(1)))


def extract_category_links(article_html: str) -> list[tuple[str, str]]:
    match = re.search(r'<p class="cat-links[^"]*">(.*?)</p>', article_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    pairs = re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', match.group(1), flags=re.IGNORECASE | re.DOTALL)
    result: list[tuple[str, str]] = []
    for href, label in pairs[:3]:
        text = html.unescape(re.sub(r"<[^>]+>", "", label)).strip()
        if text:
            result.append((href, text))
    return result


def build_listing_card(record: PostRecord, current_page: str) -> str:
    cards = [f'<span class="recovery-listing-card__date">{html.escape(record.date_label)}</span>'] if record.date_label else []
    if record.author:
        cards.append(f"<span>Publicerad av {html.escape(record.author)}</span>")
    for href, label in record.categories[:3]:
        cards.append(f'<a class="recovery-chip" href="{html.escape(posixpath.relpath(href, posixpath.dirname(current_page)))}">{html.escape(label)}</a>')
    media_html = ""
    if record.image_src:
        media_html = (
            '<figure class="recovery-listing-card__media">'
            f'<a href="{html.escape(posixpath.relpath(record.path, posixpath.dirname(current_page)))}"><img src="{html.escape(record.image_src)}" alt="{html.escape(record.image_alt)}" loading="lazy" /></a>'
            "</figure>"
        )
    return (
        '<article class="post recovery-listing-card">'
        '<header class="entry-header">'
        f'<h2 class="entry-title"><a class="recovery-listing-card__title-link" href="{html.escape(posixpath.relpath(record.path, posixpath.dirname(current_page)))}">{html.escape(record.title)}</a></h2>'
        f'<div class="entry-meta recovery-listing-card__meta">{"".join(cards)}</div>'
        "</header>"
        '<div class="entry-content recovery-listing-card__body">'
        f'<div class="recovery-listing-card__summary"><p>{html.escape(record.summary)}</p><a class="recovery-listing-card__more" href="{html.escape(posixpath.relpath(record.path, posixpath.dirname(current_page)))}">Läs artikeln</a></div>'
        f"{media_html}"
        "</div>"
        "</article>"
    )


def build_listing_tools(meta: PageMeta, relative: str) -> str:
    prefix = "../" * len([part for part in relative.split("/")[:-1] if part])
    links = [f'<a href="{prefix}browse/index.html">Alla sidor</a>']
    if meta.kind == "archive" and meta.year:
        links.append(f'<a href="{prefix}browse/index.html?kind=post&year={meta.year}">Fler artiklar från {meta.year}</a>')
    elif meta.kind == "category":
        links.append(f'<a href="{prefix}browse/index.html?kind=category">Fler kategorier</a>')
        links.append(f'<a href="{prefix}browse/index.html?kind=post&q={quote_plus(meta.title)}">Sök liknande artiklar</a>')
    elif meta.kind == "tag":
        links.append(f'<a href="{prefix}browse/index.html?kind=tag">Fler taggar</a>')
        links.append(f'<a href="{prefix}browse/index.html?kind=post&q={quote_plus(meta.title)}">Sök artiklar med taggen</a>')
    elif meta.kind == "pagination":
        links.append(f'<a href="{prefix}browse/index.html?kind=post">Till alla artiklar</a>')
    return f'<div class="recovery-listing-tools">{"".join(links)}</div>'


def select_listing_records(meta: PageMeta, records: list[PostRecord]) -> list[PostRecord]:
    if meta.kind == "archive" and meta.year and meta.month:
        return [record for record in records if record.date_label == f"{meta.year:04d}-{meta.month:02d}" or record.date_label.startswith(f"{meta.year:04d}-{meta.month:02d}-")]
    if meta.kind == "category":
        return [record for record in records if any(href == meta.path for href, _ in record.categories)]
    if meta.kind == "tag":
        return [record for record in records if any(href == meta.path for href, _ in record.tags)]
    return []


def rebuild_listing_page(html_text: str, meta: PageMeta, context_box: str, records: list[PostRecord]) -> str:
    selected = select_listing_records(meta, records)
    if not selected:
        return html_text
    cleaned = re.sub(r'<div class="recovery-listing-tools">.*?</div>', "", html_text, flags=re.IGNORECASE | re.DOTALL)
    cards_html = "\n".join(build_listing_card(record, meta.path) for record in selected)
    page_title = html.escape(meta.title or "Översikt")
    nav_html = ""
    nav_match = re.search(r'(<nav id="nav-above">.*?</nav><!-- #nav-above -->)', cleaned, flags=re.IGNORECASE | re.DOTALL)
    if nav_match:
        nav_html = nav_match.group(1)
    content_html = (
        f"{context_box}\n"
        f"{build_listing_tools(meta, meta.path)}\n"
        '<header class="page-header">'
        f'<h1 class="page-title">{page_title}</h1>'
        f'<p class="recovery-meta">{len(selected)} artiklar i denna översikt.</p>'
        "</header>\n"
        f"{nav_html}\n"
        f"{cards_html}\n"
    )
    return re.sub(
        r'(<div id="content" role="main">)(.*?)(</div><!-- #content -->)',
        r"\1\n" + content_html + r"\3",
        cleaned,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )


def rewrite_listing_articles(html_text: str, meta: PageMeta, pages_by_path: dict[str, PageMeta]) -> str:
    if meta.kind not in {"archive", "category", "tag", "pagination"}:
        return html_text

    def replace_article(match: re.Match[str]) -> str:
        article_html = match.group(0)
        href_match = re.search(r'<h1 class="entry-title"><a [^>]*href="([^"]+)"[^>]*>', article_html, flags=re.IGNORECASE)
        href = href_match.group(1) if href_match else ""
        resolved = normalize_local_href(meta.path, href) if href else None
        linked_page = pages_by_path.get(resolved or "")
        title = linked_page.title if linked_page else extract_title(article_html)
        summary = linked_page.summary if linked_page and linked_page.summary else extract_summary(article_html)
        date = linked_page.date_label if linked_page and linked_page.date_label else ""
        author = extract_author_name(article_html)
        image = extract_first_image(article_html)
        category_links = extract_category_links(article_html)
        chips = "".join(
            f'<a class="recovery-chip" href="{html.escape(cat_href)}">{html.escape(cat_label)}</a>'
            for cat_href, cat_label in category_links
        )
        media_html = ""
        if image:
            src, alt = image
            media_html = (
                '<figure class="recovery-listing-card__media">'
                f'<a href="{html.escape(href)}"><img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy" /></a>'
                "</figure>"
            )
        meta_bits: list[str] = []
        if date:
            meta_bits.append(f'<span class="recovery-listing-card__date">{html.escape(date)}</span>')
        if author:
            meta_bits.append(f"<span>Publicerad av {html.escape(author)}</span>")
        if chips:
            meta_bits.append(chips)
        meta_html = "".join(meta_bits)
        summary_html = f"<p>{html.escape(summary)}</p>" if summary else ""
        return (
            '<article class="post recovery-listing-card">'
            '<header class="entry-header">'
            f'<h2 class="entry-title"><a class="recovery-listing-card__title-link" href="{html.escape(href)}">{html.escape(title)}</a></h2>'
            f'<div class="entry-meta recovery-listing-card__meta">{meta_html}</div>'
            "</header>"
            '<div class="entry-content recovery-listing-card__body">'
            f'<div class="recovery-listing-card__summary">{summary_html}<a class="recovery-listing-card__more" href="{html.escape(href)}">Läs artikeln</a></div>'
            f"{media_html}"
            "</div>"
            "</article>"
        )

    return re.sub(r"<article\b[^>]*class=\"[^\"]*\bpost\b[^\"]*\"[^>]*>.*?</article>", replace_article, html_text, flags=re.IGNORECASE | re.DOTALL)


def inject_theme(html_text: str, theme_href: str, topbar: str, context_box: str, meta: PageMeta, pages_by_path: dict[str, PageMeta], post_records: list[PostRecord], site_label: str, cleanup_level: str = "minimal") -> str:
    updated = clean_html(html_text) if cleanup_level == "aggressive" else minimal_clean_html(html_text)
    if meta.kind == "post" and cleanup_level == "aggressive":
        updated = re.sub(r'(<div id="page">\s*).*?(?=<div id="main")', r"\1", updated, count=1, flags=re.IGNORECASE | re.DOTALL)
        updated = re.sub(r'<div id="sidebar"[^>]*>.*?</div><!-- #sidebar -->\s*', "", updated, flags=re.IGNORECASE | re.DOTALL)
        updated = re.sub(r'<div id="primary-sidebar"[^>]*>.*?</div><!-- #primary-sidebar -->\s*', "", updated, flags=re.IGNORECASE | re.DOTALL)
        updated = re.sub(r'<div id="secondary-sidebar"[^>]*>.*?</div><!-- #secondary-sidebar -->\s*', "", updated, flags=re.IGNORECASE | re.DOTALL)
    if meta.kind in {"archive", "category", "tag"}:
        updated = rebuild_listing_page(updated, meta, context_box, post_records)
    else:
        updated = rewrite_listing_articles(updated, meta, pages_by_path)
    if meta.kind == "post":
        updated = lift_repeated_post_links(updated)
    updated = rewrite_internal_anchors(updated, meta, pages_by_path, site_label)
    if 'name="robots"' not in updated.lower():
        updated = updated.replace("</head>", f"{ROBOTS_META_TAG}\n</head>")
    if THEME_RELATIVE_PATH not in updated:
        updated = updated.replace("</head>", f'<link rel="stylesheet" href="{theme_href}" />\n</head>')
    body_match = re.search(r"<body([^>]*)>", updated, flags=re.IGNORECASE)
    if body_match:
        attrs = body_match.group(1)
        class_values = re.findall(r'class="([^"]*)"', attrs, flags=re.IGNORECASE)
        if class_values:
            classes: list[str] = []
            for value in class_values:
                for item in value.split():
                    if item not in classes:
                        classes.append(item)
            if "recovery-enhanced" not in classes:
                classes.append("recovery-enhanced")
            kind_class = f"recovery-kind-{meta.kind}"
            if kind_class not in classes:
                classes.append(kind_class)
            attrs = re.sub(r'\s*class="[^"]*"', "", attrs, flags=re.IGNORECASE) + f' class="{" ".join(classes)}"'
        else:
            attrs = attrs + f' class="recovery-enhanced recovery-kind-{meta.kind}"'
        updated = re.sub(r"<body([^>]*)>", f"<body{attrs}>", updated, count=1, flags=re.IGNORECASE)
    updated = re.sub(
        r'(<body[^>]*>\s*)<div class="recovery-topbar">.*?</div></div>',
        r"\1",
        updated,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    updated = re.sub(r"(<body[^>]*>)", r"\1\n" + topbar, updated, count=1, flags=re.IGNORECASE)
    if meta.kind not in {"archive", "category", "tag"} and "recovery-context" not in updated:
        updated = updated.replace('<div id="content" role="main">', f'<div id="content" role="main">\n{context_box}', 1)
    if meta.kind == "pagination" and "recovery-listing-tools" not in updated:
        updated = updated.replace(context_box, context_box + "\n" + build_listing_tools(meta, meta.path), 1)
    return repair_common_mojibake_sequences(updated)


def write_support_files(site_dir: Path, pages: list[PageMeta]) -> None:
    theme_path = site_dir / THEME_RELATIVE_PATH
    theme_path.parent.mkdir(parents=True, exist_ok=True)
    theme_path.write_text(THEME_CSS.strip() + "\n", encoding="utf-8")
    search_script_path = site_dir / SEARCH_SCRIPT_RELATIVE_PATH
    search_script_path.parent.mkdir(parents=True, exist_ok=True)
    search_script_path.write_text(SEARCH_SCRIPT.strip() + "\n", encoding="utf-8")
    browse_dir = site_dir / "browse"
    browse_dir.mkdir(parents=True, exist_ok=True)
    (browse_dir / "search-index.json").write_text(json.dumps(search_index_records(pages), ensure_ascii=False, indent=2), encoding="utf-8")
    (site_dir / "robots.txt").write_text(ROBOTS_TXT_CONTENT, encoding="utf-8")
    (site_dir / ".htaccess").write_text(HTACCESS_CONTENT, encoding="utf-8")


def run(argv: list[str] | None = None) -> int:
    global CURRENT_COLLECTION_ITEMS
    args = parse_args(argv)
    site_dir = Path(args.site_dir)
    pages = build_page_meta(site_dir)
    pages_by_path = {page.path: page for page in pages}
    post_records = build_post_records(site_dir, pages)
    collection_items = load_collection_nav(site_dir, args.collection_file, args.collection_slug)
    CURRENT_COLLECTION_ITEMS = collection_items
    write_support_files(site_dir, pages)
    browse_dir = site_dir / "browse"
    browse_dir.mkdir(parents=True, exist_ok=True)
    (browse_dir / "index.html").write_text(
        repair_common_mojibake_sequences(build_browse_page(pages, post_records, args.site_label, collection_items)),
        encoding="utf-8",
    )
    (site_dir / "index.html").write_text(
        repair_common_mojibake_sequences(build_home_page(pages, args.site_title, args.site_label, args.site_intro)),
        encoding="utf-8",
    )
    recovery_dir = site_dir / "recovery"
    recovery_dir.mkdir(parents=True, exist_ok=True)
    (recovery_dir / "index.html").write_text(
        repair_common_mojibake_sequences(build_report_page(site_dir, pages, args.site_title, args.site_label)),
        encoding="utf-8",
    )
    for html_path in iter_html_files(site_dir):
        if html_path.relative_to(site_dir).as_posix() in {"browse/index.html", "index.html", "recovery/index.html"}:
            continue
        relative = html_path.relative_to(site_dir).as_posix()
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
        meta = next((page for page in pages if page.path == relative), None)
        if meta is None:
            continue
        updated = inject_theme(
            html_text,
            relpath_to_theme(html_path, site_dir),
            build_topbar(relative, args.site_label, collection_items),
            build_context_box(meta, relative),
            meta,
            pages_by_path,
            post_records,
            args.site_label,
            args.cleanup_level,
        )
        html_path.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
