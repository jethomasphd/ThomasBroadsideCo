"""Regression checks for distinct reading scenes across the campaign surfaces."""
import copy
import hashlib
import json
import re
import unittest
from build_canon import ROOT, validate_scene_images

KIT = ROOT/'marketing/words-to-live-with'
DATA = json.loads((ROOT/'data/campaigns/words-to-live-with.json').read_text(encoding='utf-8'))

class CanonScenes(unittest.TestCase):
    def test_rejects_shared_matthew_scene_and_opening_reuse(self):
        for chapter, image in [('the-soul','hill'),('rest','room')]:
            bad = copy.deepcopy(DATA)
            next(c for c in bad['chapters'] if c['id']==chapter)['image'] = image
            with self.assertRaisesRegex(ValueError, 'own scene'):
                validate_scene_images(bad)

    def test_distinct_assets_and_consistent_surface_assignments(self):
        validate_scene_images(DATA)
        self.assertEqual(DATA,json.loads((KIT/'source/campaign.json').read_text(encoding='utf-8')))
        artwork = (KIT/'source/campaign-art.html').read_text(encoding='utf-8')
        website = (ROOT/'site/canon.html').read_text(encoding='utf-8')
        aliases = {'the-soul':'soul','the-way':'way'}
        for chapter in DATA['chapters']:
            scene = chapter['image']; key = aliases.get(chapter['id'],chapter['id'])
            self.assertIn(key+":{image:'"+scene+"'",artwork)
            article = re.search(r'<article[^>]+id="'+chapter['id']+r'".*?</article>',website,re.S)
            self.assertIsNotNone(article)
            self.assertIn('/media/canon/'+scene+'.webp',article.group())
        for directory,suffix in [('artwork','.png'),('source/clips','.mp4')]:
            hashes = [hashlib.sha256((KIT/directory/(s+suffix)).read_bytes()).hexdigest() for s in ['room',*[c['image'] for c in DATA['chapters']]]]
            self.assertEqual(len(hashes),len(set(hashes)))

    def test_film_timing_and_scenes(self):
        for path in (KIT/'source').glob('*-timeline.json'):
            timeline=json.loads(path.read_text(encoding='utf-8'))
            scenes=[s[0] for s in timeline['segments']]
            self.assertEqual(len(scenes),len(set(scenes)),path.name)
            self.assertEqual(sum(s[2] for s in timeline['segments']),timeline['duration'])
            self.assertEqual(timeline['captions_default'],'off')
            if path.name.startswith('words-to-live-with-80s'):
                self.assertEqual(timeline['duration'],DATA['film']['duration_seconds'])
                self.assertTrue(set(c['image'] for c in DATA['chapters']).issubset(scenes))
        self.assertFalse((KIT/'films/words-to-live-with-70s.mp4').exists())
        source=(KIT/'source/build_media.py').read_text(encoding='utf-8')
        self.assertNotIn('-stream_loop',source)
        website=(ROOT/'site/canon.html').read_text(encoding='utf-8')
        self.assertIn(DATA['film']['file'],website)
        self.assertTrue((ROOT/'site/media/canon'/DATA['film']['file']).is_file())
        for track in re.findall(r'<track\b[^>]*>',website):self.assertNotRegex(track,r'\bdefault\b')

if __name__=='__main__':unittest.main()
