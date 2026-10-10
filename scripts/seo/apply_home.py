#!/usr/bin/env python3
"""Apply minimal, idempotent metadata and brand URL fixes to the existing CMS index.
Does not touch routes, CMS data, pending edits, or user-generated content.
"""
from pathlib import Path
import html, json, re, sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path('.')
index = ROOT / 'index.html'
s = index.read_text(encoding='utf-8')
url = 'https://construtoraconfidence.com/'
content = json.loads((ROOT / 'data/site-data.json').read_text(encoding='utf-8'))
works = content.get('works') or []
brand = content.get('brand') or {}
name = brand.get('name') or 'Confidence Construtora'
description = ('Confidence Construtora: obras de construção, reforma e infraestrutura na Bahia. '
               'Conheça projetos, registros de execução e serviços de engenharia.')
raw_cover = next((w.get('cover') for w in works if w.get('cover')), 'assets/branding/logo-confidence-horizontal.png')
from urllib.parse import urljoin,quote
cover = urljoin(url, quote(str(raw_cover),safe='/:?=&%#'))
# Older records contain github.io media URLs; those are valid media resources, not the page canonical.
logo = url + 'assets/branding/logo-confidence-horizontal.png'

schema = [
    {'@context':'https://schema.org','@type':'GeneralContractor','@id':url+'#empresa','name':name,
     'url':url,'logo':logo,
     'description':'Construtora com atuação em obras, infraestrutura e serviços de engenharia na Bahia.',
     'telephone':brand.get('phone') or '(77) 99824-3876',
     'email':brand.get('email') or 'comercial@construtoraconfidence.com',
     'address':{'@type':'PostalAddress','streetAddress':'Av. Juracy Magalhães, 3340',
                'addressLocality':'Vitória da Conquista','addressRegion':'BA', 'addressCountry':'BR'}},
    {'@context':'https://schema.org','@type':'WebSite','@id':url+'#website','url':url,
     'name':name,'inLanguage':'pt-BR','publisher':{'@id':url+'#empresa'}},
]

head_tags = f'''  <!-- SEO_CONFIDENCE_V1 -->
  <title>{html.escape(name)} | Engenharia, obras e infraestrutura na Bahia</title>
  <meta name="description" content="{html.escape(description, quote=True)}" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <link rel="canonical" href="{url}" />
  <link rel="icon" href="/assets/branding/logo-confidence-compacta.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/assets/branding/logo-confidence-compacta.svg" />
  <meta name="application-name" content="{html.escape(name, quote=True)}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="pt_BR" />
  <meta property="og:site_name" content="{html.escape(name, quote=True)}" />
  <meta property="og:title" content="{html.escape(name, quote=True)} | Obras e engenharia na Bahia" />
  <meta property="og:description" content="{html.escape(description, quote=True)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{html.escape(cover, quote=True)}" />
  <meta property="og:image:alt" content="Obra documentada pela Confidence Construtora" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(name, quote=True)} | Obras e engenharia na Bahia" />
  <meta name="twitter:description" content="{html.escape(description, quote=True)}" />
  <meta name="twitter:image" content="{html.escape(cover, quote=True)}" />
  <script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')}</script>
  <!-- /SEO_CONFIDENCE_V1 -->
'''
# Replace the SEO block on subsequent runs; otherwise migrate only the original head tags.
if '<!-- SEO_CONFIDENCE_V1 -->' in s:
    s, count = re.subn(r'  <!-- SEO_CONFIDENCE_V1 -->.*?<!-- /SEO_CONFIDENCE_V1 -->\n',
                       lambda _: head_tags, s, count=1, flags=re.S)
else:
    s, count = re.subn(r'^\s*<title>[^\n]*</title>\s*\n\s*<meta name="description"[^\n]*>\s*\n',
                       lambda _: '\n'+head_tags, s, count=1, flags=re.M)
if count != 1:
    raise SystemExit('Não foi possível localizar metadados originais ou bloco SEO. Nada salvo.')

# Preserve any custom logo the CMS user has supplied. Only built-in official remote URLs get mapped.
helper = '''    /* SEO: disponibilizar localmente os arquivos oficiais de marca, sem alterar imagens personalizadas. */
    const seoLocalBrandLogo = value => {
      const current=String(value || '');
      const prefix='https://raw.githubusercontent.com/glaucodeveloper/proposta-confidence/main/imagens/';
      if(current===prefix+'logo_oficial_aplicacao_azul.png') return 'assets/branding/logo-confidence-horizontal.png';
      if(current===prefix+'logo_oficial_aplicacao_clara.png') return 'assets/branding/logo-confidence-horizontal.png';
      return current;
    };
'''
if 'const seoLocalBrandLogo =' not in s:
    marker='  <script type="module">\n'
    if marker not in s:
        raise SystemExit('Script principal não localizado; operação cancelada.')
    s=s.replace(marker, marker+helper, 1)
s=s.replace('${BRAND.logoBlue}', '${seoLocalBrandLogo(BRAND.logoBlue)}')
s=s.replace('${BRAND.logoLight}', '${seoLocalBrandLogo(BRAND.logoLight)}')

# Dynamic titles when navigating inside the SPA. The static /obras/... pages are the crawler entrypoints.
route_js = '''
    /* SEO: título e robots coerentes com a rota visível; páginas estáticas são o ponto de indexação. */
    function seoRefreshRouteMeta(){
      const match=location.hash.match(/^#\\/obra\\/([^/?]+)/);
      const work=match && (typeof WORKS!=='undefined' ? WORKS : []).find(w=>w.slug===decodeURIComponent(match[1]));
      const login=/^#\\/(login|nova-obra)/.test(location.hash);
      document.title=work ? `${work.name} em ${work.city}, BA | Confidence Construtora` :
        login ? 'Área administrativa | Confidence Construtora' :
        'Confidence Construtora | Engenharia, obras e infraestrutura na Bahia';
      const robots=document.querySelector('meta[name="robots"]');
      if(robots) robots.content=login ? 'noindex,nofollow' : 'index,follow,max-image-preview:large';
    }
    window.addEventListener('hashchange',seoRefreshRouteMeta);
    window.addEventListener('cms-content-loaded',seoRefreshRouteMeta);
    queueMicrotask(seoRefreshRouteMeta);
'''
if 'function seoRefreshRouteMeta()' not in s:
    closing='  </script>\n</body>'
    if closing not in s: raise SystemExit('Fim do script principal não identificado.')
    s=s.replace(closing, route_js + '  </script>\n</body>', 1)

index.write_text(s,encoding='utf-8')
print('SEO: index.html atualizado sem substituir conteúdo das páginas.')
