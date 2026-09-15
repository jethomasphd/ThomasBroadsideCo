"""Release checks for the origin story and its portable campaign package."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib,json,re

ROOT=Path(__file__).resolve().parent.parent; SITE=ROOT/'site'; KIT=ROOT/'marketing/the-first-impression'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.refs=[];self.ids=[];self.tracks=[];self.videos=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.append(d['id'])
        if tag=='track':self.tracks.append(d)
        if tag=='video':self.videos.append(d)
        for attr in ['href','src','data-src','data-desktop','data-mobile']:
            if d.get(attr):self.refs.append(d[attr])
        if tag=='source' and d.get('srcset'):self.refs.extend(part.strip().split()[0] for part in d['srcset'].split(','))

def inspect_links(path,root):
    p=Page(path.read_text(encoding='utf-8'))
    assert len(p.ids)==len(set(p.ids)),f'duplicate id in {path}'
    for ref in p.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc:continue
        target=(root/unquote(url.path.lstrip('/'))) if url.path.startswith('/') else (path.parent/unquote(url.path)) if url.path else path
        if target.is_dir():target=target/'index.html'
        assert target.exists(),f'broken reference: {path.name}: {ref}'
        if url.fragment and target.suffix=='.html':
            ids=Page(target.read_text(encoding='utf-8')).ids
            assert unquote(url.fragment) in ids,f'broken anchor: {ref}'
    return p

story=inspect_links(SITE/'origins.html',SITE)
assert {'franklin','jefferson','dunlap','washington','hamilton','austin','original','sources','collection'} <= set(story.ids)
assert len(story.tracks)==1 and all('default' not in t for t in story.tracks),'captions must start off'
assert any('controls' in v and v.get('preload')=='none' for v in story.videos),'film must wait for intent'
assert any('muted' in v and 'data-press-loop' in v for v in story.videos),'ambient loop must be silent'
assert '/origins.html' in (SITE/'index.html').read_text(encoding='utf-8')
for p in (SITE/'media/origin').iterdir():assert p.stat().st_size < 25*1024*1024,f'oversized web asset: {p.name}'
for p in [KIT/'index.html',*(KIT/'email').glob('*-preview.html')]:inspect_links(p,KIT)
for p in [KIT/'index.html',SITE/'index.html',SITE/'press.html',SITE/'origins.html']:
    assert all('default' not in t for t in Page(p.read_text(encoding='utf-8')).tracks),f'default captions in {p}'
manifest=json.loads((KIT/'manifest.json').read_text(encoding='utf-8'))
for item in manifest['files']:
    p=KIT/item['path'];assert p.exists(),f'missing package file {p}'
    assert p.stat().st_size==item['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'asset changed without manifest update: {p}'
for p in [*(KIT/'source').glob('*.json'),KIT/'PROVENANCE.md']:
    assert 'jwt=' not in p.read_text(encoding='utf-8') and 'X-Amz-Signature' not in p.read_text(encoding='utf-8'),'temporary signed asset URL in package'
for name,duration in [('the-first-impression-65s',65),('the-printers-night-30s-vertical',30),('the-printers-night-30s-square',30)]:
    vtt=(KIT/'films'/f'{name}.vtt').read_text(encoding='utf-8');assert vtt.startswith('WEBVTT')
    previous=0
    for start,end in re.findall(r'(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)',vtt):
        def seconds(s):a,b,c=s.split(':');return int(a)*3600+int(b)*60+float(c)
        a,b=seconds(start),seconds(end);assert previous<=a<b<=duration;previous=b
print(f'PASS: story anchors, local assets, collection links, captions off, lazy film, silent loop, web size limits, portable library/email previews, {len(manifest["files"])} checksums, source URL hygiene, caption timing.')
