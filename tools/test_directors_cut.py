"""Guard the flagship edit and its public entry points. Standard library only."""
import hashlib
import json
import re
import unittest
from pathlib import Path

R=Path(__file__).resolve().parent.parent
K=R/'marketing/history-has-a-pulse/directors-cut'
D=json.loads((R/'data/campaigns/history-has-a-pulse.json').read_text(encoding='utf-8'))


class DirectorsCut(unittest.TestCase):
    def test_one_complete_distinct_edit(self):
        self.assertEqual(D,json.loads((K/'source/edit.json').read_text(encoding='utf-8')))
        scenes=D['scenes'];self.assertEqual(len(scenes),14)
        self.assertEqual(len({s['id'] for s in scenes}),len(scenes))
        t=0
        for s in scenes:
            self.assertEqual(s['at'],t);t+=s['duration']
        self.assertEqual(t,60)
        self.assertEqual(sum(s['duration'] for s in scenes if s['kind']=='shop'),25.5)
        clips=[s for s in scenes if s['id']!='closing']
        self.assertEqual(len({s['sha256'] for s in clips}),len(clips))
        for s in clips:
            self.assertEqual(hashlib.sha256((K/s['clip']).read_bytes()).hexdigest(),s['sha256'])
        originals=json.loads((K/'source/shop-selects.json').read_text(encoding='utf-8'))
        self.assertEqual(len({s['original'] for s in originals}),4)
        for i,a in enumerate(originals):
            for b in originals[i+1:]:
                if a['original']==b['original']:
                    self.assertTrue(a['start']+a['duration']<=b['start'] or b['start']+b['duration']<=a['start'])

    def test_format_and_audio_consistency(self):
        for fmt in ('wide','vertical','square'):
            timeline=json.loads((K/f'source/timeline-{fmt}.json').read_text(encoding='utf-8'))
            self.assertEqual(timeline['duration'],60)
            self.assertEqual(timeline['narration'],D['narration'])
            self.assertEqual(timeline['captions_default'],'off')
            self.assertEqual([s['id'] for s in timeline['shots']],[s['id'] for s in D['scenes']])
            self.assertTrue((K/f'films/history-has-a-pulse-directors-cut-60s-{fmt}.mp4').exists())
        previous_end=0
        for v in D['narration']:
            self.assertGreaterEqual(v['at'],previous_end)
            previous_end=v['at']+v['duration'];self.assertLessEqual(previous_end,60)
            self.assertTrue((K/v['file']).exists())
        for cue,scene in [('wisdom','sea'),('mercy','hill'),('courage','wood')]:
            v=next(v for v in D['narration'] if v['id']==cue);s=next(s for s in D['scenes'] if s['id']==scene)
            self.assertGreaterEqual(v['at'],s['at']);self.assertLessEqual(v['at']+v['duration'],s['at']+s['duration'])

    def test_public_replacement_and_captions(self):
        for name in ('index.html','press.html'):
            text=(R/'site'/name).read_text(encoding='utf-8')
            self.assertIn('Watch the director’s cut · 60 sec',text)
            self.assertIn('/media/press/'+D['media']['film'],text)
            self.assertNotIn('24 sec',text)
            video=re.search(r'<video[^>]+data-src="/media/press/.*?</video>',text,re.S).group()
            self.assertIn('preload="none"',video);self.assertNotRegex(video,r'\bautoplay\b')
        for page in [R/'site/index.html',R/'site/press.html',K/'index.html',K.parent/'index.html']:
            text=page.read_text(encoding='utf-8')
            text=re.sub(r'<script\b[^>]*>.*?</script>','',text,flags=re.S)
            for track in re.findall(r'<track\b[^>]*>',text):
                self.assertNotRegex(track,r'\sdefault(?:\s|=|>)')
            for target in re.findall(r'(?:href|src|poster)="([^"]+)"',text):
                if target.startswith(('http','mailto:','#','data:')):continue
                clean=target.split('?')[0].split('#')[0]
                if not clean or clean=='/':continue
                resolved=R/'site'/clean.lstrip('/') if clean.startswith('/') else page.parent/clean
                self.assertTrue(resolved.exists(),f'{page.name}: missing {clean}')
        redirects=(R/'site/_redirects').read_text()
        self.assertIn('/media/press/history-has-a-pulse-film.mp4 /media/press/'+D['media']['film']+' 301',redirects)
        for field in ('film','captions','poster','share'):self.assertTrue((R/'site/media/press'/D['media'][field]).exists())
        self.assertLess((R/'site/media/press'/D['media']['film']).stat().st_size,25*1024*1024)
        self.assertIn('60 seconds:',(R/'tools/templates/product.html').read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()
