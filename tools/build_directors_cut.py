"""Keep the flagship film, accessible transcript and its entry points in sync."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_directors_cut():
    data = json.loads((ROOT / 'data/campaigns/history-has-a-pulse.json').read_text(encoding='utf-8'))
    media = data['media']
    dialog = f'''<dialog class="press-film" data-press-film aria-labelledby="film-title">
  <div class="press-film__top"><span id="film-title">HISTORY HAS A PULSE / THE DIRECTOR’S CUT</span><button class="press-film__close" data-film-close aria-label="Close director’s cut">Close ×</button></div>
  <video controls playsinline preload="none" data-src="/media/press/{media['film']}" poster="/media/press/{media['poster']}" aria-label="History has a pulse: a 60-second film weaving our Austin presses, the founding story, and the Western Canon">
    <track kind="captions" src="/media/press/{media['captions']}" srclang="en" label="English">
  </video>
  <div class="press-film__bottom"><p>Our working presses. The first printed Declaration. Words to live with. A one-minute film with narration, an original score, and the sounds of the shop.</p><a href="/#documents">Explore the collection ↗</a><a href="/press.html#film-notes">Transcript &amp; film notes ↗</a></div>
</dialog>'''
    script = '\n'.join(f'<p>{html.escape(v["text"])}</p>' for v in data['narration'])
    notes = f'''<!-- GEN:DIRECTOR_NOTES -->
<section class="band" id="film-notes"><div class="wrap prose">
<p class="kicker">History has a pulse / The director’s cut</p><h2>The press makes words public.</h2>
<p>The words become part of a life. From a Philadelphia print shop in 1776 to the presses working in Austin today, this film brings our founding story and the Western Canon into one frame.</p>
<details><summary>Read the film transcript</summary><p><em>The film opens with the sound of a working press.</em></p>{script}</details>
<details><summary>About the images and sound</summary><p>Twenty-five and a half seconds show our actual shop, drawn from four original recordings. The historical scenes are AI-assisted contemporary reconstructions; the Canon landscapes and reading room are visual meditations. They are not archival footage or claims about a specific biblical location.</p><p>A new synthetic narrator and an original AI-generated chamber score accompany the real machinery. No historical or sacred figure is given invented dialogue. The closing images are the collection’s existing broadside designs.</p><p>Explore the history and its sources in <a href="/origins.html">The First Impression</a>, and the texts and their sources in <a href="/canon.html">Words to Live With</a>.</p></details>
</div></section>
<!-- /GEN:DIRECTOR_NOTES -->'''
    for name in ('index.html', 'press.html'):
        path = ROOT / 'site' / name
        text = path.read_text(encoding='utf-8')
        text, n = re.subn(r'<dialog class="press-film".*?</dialog>', lambda _: dialog, text, flags=re.S)
        if n != 1:
            raise ValueError(f'{name}: expected one flagship film dialog, got {n}')
        text = re.sub(r'(<button class="press-play" data-film-open hidden><span aria-hidden="true">▷</span>).*?(</button>)', r'\g<1>Watch the director’s cut · 60 sec\2', text)
        if name == 'index.html':
            text = re.sub(r'(<meta property="og:image" content=").*?(">)', rf'\g<1>https://thomasbroadside.co/media/press/{media["share"]}\2', text)
        else:
            if '<!-- GEN:DIRECTOR_NOTES -->' in text:
                text = re.sub(r'<!-- GEN:DIRECTOR_NOTES -->.*?<!-- /GEN:DIRECTOR_NOTES -->', lambda _: notes, text, flags=re.S)
            else:
                text = text.replace('</main>', notes + '\n</main>')
        path.write_text(text, encoding='utf-8')
    print('built History has a pulse director’s cut entry points and transcript')


if __name__ == '__main__':
    build_directors_cut()
