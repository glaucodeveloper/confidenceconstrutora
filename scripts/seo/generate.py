#!/usr/bin/env python3
"""Generate indexable, self-contained static work pages from the public CMS JSON.
No external dependencies. Does NOT mutate site data, CMS index, or uploads.
"""
from pathlib import Path
from urllib.parse import urljoin, quote, urlparse
from xml.sax.saxutils import escape as xml_escape
from datetime import datetime
import html
import json
import re
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.')
BASE = 'https://construtoraconfidence.com/'
DATAPATH = ROOT / 'data/site-data.json'
data = json.loads(DATAPATH.read_text(encoding='utf-8'))
works = data.get('works') if isinstance(data.get('works'),list) else []
brand = data.get('brand') if isinstance(data.get('brand'),dict) else {}
name = brand.get('name') or 'Confidence Construtora'
logo_url = BASE + 'assets/branding/logo-confidence-azul.png'
now_date = datetime.now().strftime('%Y-%m-%d')
updated = str(data.get('updatedAt',''))[:10]
lastmod = updated if re.fullmatch(r'\d{4}-\d{2}-\d{2}',updated) else now_date

def esc(s):
    return html.escape(str(s or ''),quote=True)

def absolute_asset(s):
    if not s: return ''
    text = str(s).strip()
    if text.startswith('assets/'):
        return urljoin(BASE,quote(text, safe='/:?=&%#'))
    parts = urlparse(text)
    return text if parts.scheme in ('http','https') and parts.netloc else ''

def safe_text(s,n=360):
    plain = re.sub(r'<[^>]+>', ' ',str(s or ''))
    plain = re.sub(r'\s+', ' ', plain).strip()
    return (plain[:n].rsplit(' ',1)[0]+'…') if len(plain)>n else plain

def jsonld(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

def head(title,description,url,cover,kind='website',schema=None):
    cover = cover or logo_url
    return f'''<!doctype html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#082d4c">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="{esc(url)}">
<link rel="icon" href="/assets/branding/favicon-confidence.png" type="image/png" sizes="256x256">
<meta property="og:type" content="{esc(kind)}"><meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{esc(name)}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(cover)}"><meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{esc(cover)}">
{f'<script type="application/ld+json">{jsonld(schema)}</script>' if schema else ''}
<style>
:root{{--ink:#0a314d;--blue:#105584;--soft:#eef5f9;--line:#cddce6}}
*{{box-sizing:border-box}}body{{margin:0;background:#f7fafc;color:var(--ink);font-family:Inter,"Segoe UI",Arial,sans-serif}}
header{{background:#fff;border-bottom:1px solid var(--line)}}nav{{max-width:1120px;margin:auto;padding:18px 22px;display:flex;align-items:center;justify-content:space-between;gap:20px}}
nav img{{width:min(205px,45vw);height:auto}}a{{color:var(--blue)}}.back{{font-weight:750;text-decoration:none;font-size:14px}}
main{{max-width:1120px;margin:auto;padding:45px 22px 65px}}.eyebrow{{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--blue);font-weight:800}}
h1{{font-size:clamp(34px,5.4vw,64px);letter-spacing:-.045em;line-height:1.04;max-width:850px;margin:15px 0}}
.lead{{font-size:clamp(16px,2vw,21px);line-height:1.55;color:#3d6076;max-width:850px}}
.hero{{width:100%;max-height:540px;aspect-ratio:16/9;object-fit:cover;background:#dfeaf1;border-radius:15px;margin-top:26px}}
.cta{{display:inline-block;background:var(--blue);color:#fff;font-weight:750;padding:15px 19px;margin-top:20px;border-radius:7px;text-decoration:none}}
h2{{font-size:clamp(23px,3vw,33px);letter-spacing:-.035em}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:20px}}
.card{{display:block;background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden;text-decoration:none;color:inherit}}
.card img{{width:100%;aspect-ratio:16/10;object-fit:cover;background:#e0eaf0}}.card>div{{padding:15px 17px}}.card h3{{margin:0 0 8px;font-size:18px}}.card p{{margin:0;color:#577185;line-height:1.5}}
.list{{padding:0;list-style:none}}.list li{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:15px;margin-bottom:10px;line-height:1.6}}
.photogrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:15px}}.photogrid img{{width:100%;height:230px;object-fit:cover;border-radius:10px;background:#e4edf4}}
footer{{background:#082d4c;color:#e3edf4;text-align:center;padding:29px 20px;font-size:13px}}footer a{{color:#e3edf4}}
@media(max-width:520px){{nav{{padding:15px}}main{{padding:28px 15px 50px}}.hero{{aspect-ratio:4/3}}}}
</style></head><body><header><nav><a href="/"><img src="{logo_url}" alt="{esc(name)}"></a><a class="back" href="/">Página inicial ↗</a></nav></header>'''

def foot():
    return f'<footer>{esc(name)} · Engenharia e infraestrutura na Bahia · <a href="/">Site institucional</a></footer></body></html>'

work_dir = ROOT / 'obras'
work_dir.mkdir(exist_ok=True)
expected = set()
listing=[]
entries=[(BASE,'1.0') ,(BASE+'obras/','0.85')]
for w in works:
    if not isinstance(w,dict): continue
    slug=str(w.get('slug') or '')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
        print('IGNORADO: slug não suportado',repr(slug)); continue
    expected.add(slug)
    title = str(w.get('name') or 'Obra')
    city = str(w.get('city') or 'Bahia')
    state = str(w.get('state') or 'Bahia')
    summary = safe_text(w.get('summary') or f'Conheça esta obra da Confidence Construtora em {city}, {state}.',290)
    url = BASE + 'obras/' + slug + '/'
    cover = absolute_asset(w.get('cover'))
    image = cover or logo_url
    activities = w.get('activities') or []
    photos = [cover] if cover else []
    for u in w.get('gallery') or []:
        au = absolute_asset(u)
        if au and au not in photos:photos.append(au)
    for a in activities:
        if not isinstance(a,dict):continue
        urls = a.get('images') or [a.get('image')]
        for u in urls:
            au=absolute_asset(u)
            if au and au not in photos: photos.append(au)
    # Only real photos; no invented dates, clients, status, or certifications.
    descriptions=[]
    for activity in activities[:20]:
        if not isinstance(activity,dict): continue
        desc=safe_text(activity.get('description') or activity.get('title'),400)
        if desc: descriptions.append(desc)
    ld=[
      {'@context':'https://schema.org','@type':'WebPage','name':title+' — '+city,
       'url':url,'inLanguage':'pt-BR','description':summary,
       'about':{'@type':'Thing','name':title}},
      {'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[
        {'@type':'ListItem','position':1,'name':'Início','item':BASE},
        {'@type':'ListItem','position':2,'name':'Obras','item':BASE+'obras/'},
        {'@type':'ListItem','position':3,'name':title,'item':url}]}]
    imgtag=f'<img class="hero" src="{esc(cover)}" alt="{esc(title)} em {esc(city)}" fetchpriority="high">' if cover else ''
    activity_markup='<ul class="list">'+''.join(f'<li>{esc(x)}</li>' for x in descriptions)+'</ul>' if descriptions else '<p>Consulte a página interativa para ver os registros disponíveis desta obra.</p>'
    more_photos=''.join(f'<img src="{esc(src)}" loading="lazy" alt="{esc(title)} — fotografia {i+1}">' for i,src in enumerate(photos[:12]))
    body=(f'<main><div class="eyebrow">Obras · {esc(city)} · {esc(state)}</div>'
          f'<h1>{esc(title)}</h1><p class="lead">{esc(summary)}</p>{imgtag}'
          f'<p><a class="cta" href="/#/obra/{esc(slug)}">Abrir galeria interativa e registros</a></p>'
          f'<section><h2>Atividades e serviços documentados</h2>{activity_markup}</section>'
          f'<section><h2>Registros fotográficos</h2><div class="photogrid">{more_photos}</div></section></main>')
    target=work_dir/slug
    target.mkdir(parents=True,exist_ok=True)
    (target/'index.html').write_text(head(title+f' em {city} | Confidence Construtora',summary,url,image,schema=ld)+body+foot(),encoding='utf-8')
    entries.append((url,'0.7'))
    listing.append(f'<a class="card" href="/obras/{esc(slug)}/">'+
                   (f'<img src="{esc(cover)}" loading="lazy" alt="{esc(title)}">' if cover else '')+
                   f'<div><h3>{esc(title)}</h3><p>{esc(city)} · {esc(state)}</p></div></a>')

# Remove only pages generated by this tool, never arbitrary data files.
for folder in work_dir.iterdir():
    if folder.is_dir() and folder.name not in expected and (folder/'index.html').is_file():
        text=(folder/'index.html').read_text(encoding='utf-8')
        if '<meta property="og:site_name" content="Confidence Construtora">' in text:
            (folder/'index.html').unlink()
            try: folder.rmdir()
            except OSError: pass

index_body='<main><div class="eyebrow">Portfólio de engenharia</div><h1>Obras da Confidence Construtora</h1>'
index_body+='<p class="lead">Projetos e registros de execução em municípios da Bahia.</p>'
index_body+='<div class="grid">'+''.join(listing)+'</div></main>'
(work_dir/'index.html').write_text(head('Obras na Bahia | Confidence Construtora','Portfólio de obras e serviços de engenharia da Confidence Construtora na Bahia.',BASE+'obras/',logo_url)+index_body+foot(),encoding='utf-8')

xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url,priority in entries:
    xml.append(f'  <url><loc>{xml_escape(url)}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>')
xml.append('</urlset>')
(ROOT/'sitemap.xml').write_text('\n'.join(xml)+'\n',encoding='utf-8')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n',encoding='utf-8')
print(f'SEO: {len(expected)} obras, {len(entries)} entradas de sitemap; domínio {BASE}')
