"""Check the delivered kit against its SHA-256 manifest; stdlib only."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
errors=[]
for item in manifest['files']:
    p=root/item['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append(item['path'])
if errors:raise SystemExit('Missing or changed: '+', '.join(errors))
print(f"Verified {len(manifest['files'])} files.")
