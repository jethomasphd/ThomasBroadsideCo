"""Build the Western Canon reading room from campaign data and existing catalog."""
import html
import json
import hashlib
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent

def validate_scene_images(data):
    images = ['room', *[c['image'] for c in data['chapters']]]
    if len(images) != len(set(images)):
        raise ValueError('Each reading chapter needs its own scene, separate from the opening room.')
    hashes = [hashlib.sha256((ROOT/'site/media/canon'/f'{name}.webp').read_bytes()).digest() for name in images]
    if len(hashes) != len(set(hashes)):
        raise ValueError('Renaming a shared image does not make a distinct chapter scene.')

def build_canon():
    data = json.loads((ROOT/'data/campaigns/words-to-live-with.json').read_text(encoding='utf-8'))
    validate_scene_images(data)
    catalog = json.loads((ROOT/'data/catalog/catalog.json').read_text(encoding='utf-8'))
    products = {p['slug']: p for p in catalog['designs']}
    sources = {s['id']: s for s in data['sources']}
    e = html.escape
    chapters = []
    for c in data['chapters']:
        src = sources[c['ref']]
        chapters.append(f'''<article class="canon-reading" id="{c['id']}" aria-labelledby="{c['id']}-title"><figure><img src="/media/canon/{c['image']}.webp" width="1672" height="941" alt="{e(c['image_alt'])}" loading="lazy"><figcaption>A contemporary visual meditation</figcaption></figure><div class="canon-reading__text"><p class="kicker">{c['no']} / {e(c['theme'])}</p><h2 id="{c['id']}-title">{e(c['title'])}</h2><blockquote><p>{e(c['quote'])}</p><footer>{e(c['source'])}</footer></blockquote><p>{e(c['body'])}</p><div class="canon-reading__links"><a href="{e(src['url'])}">Read the source ↗</a><a href="/documents/{c['slug']}.html">Examine the sheet ↗</a></div></div></article>''')
    cards = []
    for slug in data['products']:
        p = products[slug]
        cards.append(f'''<a class="canon-sheet" href="/documents/{slug}.html"><div><img src="{e(p['art']['src'])}" width="900" height="1200" loading="lazy" alt="{e(p['art']['alt'])}"></div><h3>{e(p['title'])}</h3><p>{e(p['date_label'])}</p><span>Explore the formats ↗</span></a>''')
    art=[]
    for slug,ref in [('christ-preaching-hundred-guilder','rembrandt-christ'),('aristotle-with-a-bust-of-homer','rembrandt-homer'),('the-circle-of-the-lustful','blake')]:
        p=products[slug];s=sources[ref]
        art.append(f'''<figure><a href="/documents/{slug}.html"><img src="{p['art']['src']}" alt="{e(p['art']['alt'])}" width="900" height="1200" loading="lazy"></a><figcaption><strong>{e(p['title'])}</strong><span>{e(s['credit'])}</span><a href="{e(s['url'])}">View the museum record ↗</a></figcaption></figure>''')
    refs=''.join(f'<li><a href="{e(s["url"])}">{e(s["title"])}</a><p>{e(s["credit"])}. {e(s["note"])}</p></li>' for s in data['sources'])
    nav=''.join(f'<a href="#{c["id"]}"><span>{c["no"]}</span> {e(c["theme"])}</a>' for c in data['chapters'])
    text=Template((ROOT/'tools/templates/canon.html').read_text(encoding='utf-8')).substitute(film_duration=data['film']['duration_seconds'],film_file=data['film']['file'],film_captions=data['film']['captions'],chapters='\n'.join(chapters),chapter_nav=nav,art='\n'.join(art),products='\n'.join(cards),sources=refs,transcript=e(' '.join(line for _,line in data['narration'])))
    (ROOT/'site/canon.html').write_text(text,encoding='utf-8')
    print('built Words to Live With / Western Canon')

if __name__ == '__main__':
    build_canon()
