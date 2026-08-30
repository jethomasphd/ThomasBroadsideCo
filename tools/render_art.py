#!/usr/bin/env python3
"""Render the committed design sources to what the store and the press use:

  art_src/<slug>.svg ──► site/art/<slug>.jpg   (display, ~2200 px long side)
                     ──► print/<slug>.pdf      (vector, true sheet size)

Requires a Chromium binary (CHROMIUM env var, or the Playwright install at
/opt/pw-browsers/chromium) and Pillow. Run typeset.py first.
    python3 tools/render_art.py [slug ...]
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "art_src"
JPG = ROOT / "site" / "art"
PDF = ROOT / "print"


def chromium() -> str:
    for cand in (os.environ.get("CHROMIUM"), "/opt/pw-browsers/chromium",
                 "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if cand and Path(cand).exists():
            return cand
    sys.exit("no chromium found — set CHROMIUM env var")


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])


def main() -> None:
    only = set(sys.argv[1:])
    JPG.mkdir(parents=True, exist_ok=True)
    PDF.mkdir(exist_ok=True)
    chrome = chromium()
    for svg in sorted(SRC.glob("*.svg")):
        slug = svg.stem
        if only and slug not in only:
            continue
        m = re.search(r'width="(\d+)" height="(\d+)"', svg.read_text(encoding="utf-8")[:300])
        w, h = int(m.group(1)), int(m.group(2))
        # screenshot at the exact display scale — no resample afterwards
        # (a LANCZOS pass softens type) — and save with full chroma so red
        # ink and fine serifs stay crisp
        scale = 2600 / max(w, h)
        with tempfile.TemporaryDirectory() as td:
            png = Path(td) / "shot.png"
            run("node", str(ROOT / "tools" / "render_art.js"),
                str(svg.resolve()), str(png), str(w), str(h), f"{scale:.4f}")
            im = Image.open(png).convert("RGB")
            im.save(JPG / f"{slug}.jpg", "JPEG", quality=90, subsampling=0,
                    progressive=True, optimize=True)

            wrapper = Path(td) / "page.html"
            wrapper.write_text(
                f"<!doctype html><html><head><style>"
                f"@page{{size:{w / 72}in {h / 72}in;margin:0}}"
                f"html,body{{margin:0;padding:0}}"
                f"svg,img{{display:block;width:{w / 72}in;height:{h / 72}in}}"
                f"</style></head><body>"
                + svg.read_text(encoding="utf-8") + "</body></html>", encoding="utf-8")
            out = Path(td) / "out.pdf"
            run(chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
                f"--print-to-pdf={out}", "--no-pdf-header-footer", wrapper.as_uri())
            (PDF / f"{slug}.pdf").write_bytes(out.read_bytes())
        jk = (JPG / f"{slug}.jpg").stat().st_size // 1024
        pk = (PDF / f"{slug}.pdf").stat().st_size // 1024
        print(f"rendered {slug}: jpg {jk} KB · pdf {pk} KB")


if __name__ == "__main__":
    main()
