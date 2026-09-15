"""Build the source-led origin story; historical scenes are reconstructions."""
import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
def build_origin():
    data = json.loads((ROOT / 'data/campaigns/the-first-impression.json').read_text(encoding='utf-8'))
    esc = html.escape
    sources = {s['id']: s for s in data['sources']}
    chapters = []
    for c in data['chapters']:
        paragraphs = ''.join(f'<p>{esc(p)}</p>' for p in c['body'])
        refs = ' · '.join(f'<a href="{esc(sources[s]["url"])}">{esc(sources[s]["title"])}</a>' for s in c['sources'])
        chapters.append(f'''<section class="origin-chapter" id="{c['id']}" aria-labelledby="{c['id']}-title">
<figure><picture><source srcset="/media/origin/{c['image']}.webp" type="image/webp"><img src="/media/origin/{c['image']}.jpg" width="1672" height="941" alt="{esc(c['alt'])}" loading="lazy" decoding="async"></picture><figcaption>{esc(c['caption'])}</figcaption></figure>
<div class="origin-chapter__text"><p class="kicker">{c['number']} / {esc(c['eyebrow'])}</p><h2 id="{c['id']}-title">{esc(c['title'])}</h2><p class="origin-date">{esc(c['date'])}</p>{paragraphs}<p class="origin-ref">Read the sources: {refs}</p><a class="origin-link" href="/documents/{c['slug']}.html">{esc(c['cta'])} ↗</a></div></section>''')
    nav = ''.join(f'<a href="#{c["id"]}"><span>{c["number"]}</span> {c["id"].title()}</a>' for c in data['chapters'])
    refs = ''.join(f'<li id="source-{s["id"]}"><a href="{esc(s["url"])}">{esc(s["title"])}</a><span>{esc(s["institution"])}</span><p>{esc(s["note"])}</p></li>' for s in data['sources'])
    portraits = ''.join(f'<a href="/documents/{c["slug"]}.html"><img src="/art/{c["slug"]}.jpg" width="600" height="800" loading="lazy" alt="{esc(c["id"].title())} portrait broadside from the collection"><span>{c["id"].title()} ↗</span></a>' for c in data['chapters'] if c['id'] != 'dunlap')
    template = Template((ROOT / 'tools/templates/origins.html').read_text(encoding='utf-8'))
    (ROOT / 'site/origins.html').write_text(template.substitute(chapters='\n'.join(chapters), chapter_nav=nav, sources=refs, portraits=portraits), encoding='utf-8')
    print('built The First Impression origin story')

if __name__ == '__main__':
    build_origin()
