"""Refresh the portable kit inventory after rebuilding its assets."""
from pathlib import Path
import hashlib, json
from PIL import Image

K = Path(__file__).resolve().parents[1]
for path in K.rglob('*'):
    if path.suffix in ['.md', '.txt', '.json', '.html', '.py', '.vtt']:
        path.write_text(path.read_text(encoding='utf-8-sig').rstrip()+'\n', encoding='utf-8', newline='\n')
manifest = {'campaign':'The First Impression', 'created':'2026-09-15', 'revision':'2026-09-16 / distinct scenes', 'files':[]}
for path in sorted(K.rglob('*')):
    if not path.is_file() or path.name == 'manifest.json' or '__pycache__' in path.parts:
        continue
    row = {'path':path.relative_to(K).as_posix(), 'bytes':path.stat().st_size, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.suffix in ['.png', '.jpg']:
        with Image.open(path) as img:
            row['width'], row['height'] = img.size
    manifest['files'].append(row)
(K/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8', newline='\n')
print(f'Inventoried {len(manifest["files"])} campaign files.')
