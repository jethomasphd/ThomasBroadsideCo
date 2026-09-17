"""Render the current director’s cut. The original ambient website loops are retained."""
from pathlib import Path
import subprocess, sys
P = Path(__file__).resolve().parents[1]
R = P.parents[1]
command = [sys.executable, str(P/'directors-cut/source/build_film.py')]
if (R/'site/media/press').is_dir():
    command += ['--web-root', str(R/'site/media/press')]
subprocess.run(command + sys.argv[1:], check=True)
