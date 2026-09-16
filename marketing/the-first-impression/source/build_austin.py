"""Optional: rebuild the included 12-second Austin edit from the owner's originals.

Usage: python source/build_austin.py PATH_TO_ORIGINAL_MOV_DIRECTORY
The finished source/clips/austin.mp4 is included; other builders need no raw files.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
import imageio_ffmpeg

K = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('originals', type=Path)
args = parser.parse_args()
recipe = json.loads((K / 'source/austin-edit.json').read_text(encoding='utf-8'))
ff = imageio_ffmpeg.get_ffmpeg_exe()
temp = K.parents[1] / 'work/origin-austin'
temp.mkdir(parents=True, exist_ok=True)
parts = []
for i, shot in enumerate(recipe['shots']):
    original = args.originals / shot['file']
    assert hashlib.sha256(original.read_bytes()).hexdigest() == shot['sha256'], f'Unexpected original: {original.name}'
    dest = temp / f'{i}.mp4'
    subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(shot['start_seconds']), '-i', str(original), '-t', str(shot['duration_seconds']), '-an', '-vf', recipe['filter'], '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dest)], check=True)
    parts.append(dest)
listing = temp / 'concat.txt'
listing.write_text('\n'.join(f"file '{p.as_posix()}'" for p in parts), encoding='utf-8')
subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-c', 'copy', '-movflags', '+faststart', str(K / 'source/clips/austin.mp4')], check=True)
print('Austin: two real-time shots, 12 seconds, no repeated or reversed footage.')
