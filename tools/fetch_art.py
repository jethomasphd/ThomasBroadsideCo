#!/usr/bin/env python3
"""Fetch the full-resolution masters for every design that carries art,
then prep the plate versions the typesetting press embeds:

  art.master_url  ──►  art_masters/<slug>.jpg       (the archive's file, as-is)
                  ──►  art_masters/raw/<slug>.jpg   (plate: ≤3400 px, q92;
                                                     the Franklin oval is
                                                     composited onto cream here)

Both directories are git-ignored — everything here is reproducible from
the public URLs recorded in the catalog. The committed record is
data/catalog/catalog.json (art.credit / art.master_url /
source_verified_by) plus the rendered art_src/, print/, site/art/.
Fetching does not verify: a human confirms every object before its sheet
goes on press [D9, house rule one].

  python3 tools/fetch_art.py                # all masters
  python3 tools/fetch_art.py <slug> [...]   # just these designs

Design-bench dependency (like typeset.py, not the store): pillow.
"""
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art_masters"
RAW = OUT / "raw"
CREAM = (250, 246, 234)
PLATE_LONG = 3400  # covers the 3200 px plate renders with margin to spare


def fit(im: Image.Image, long_side: int = PLATE_LONG) -> Image.Image:
    w, h = im.size
    if max(w, h) <= long_side:
        return im
    s = long_side / max(w, h)
    return im.resize((round(w * s), round(h * s)), Image.LANCZOS)


def prep_plate(slug: str, master: Path) -> None:
    im = fit(Image.open(master).convert("RGB"))
    if slug == "benjamin-franklin-after-duplessis":
        # honor the painting's oval, but let the poster's own cream border
        # it — no black surround (Jacob, 2026-08-30)
        w, h = im.size
        mask = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(mask)
        ix, iy = int(w * 0.030), int(h * 0.024)
        d.ellipse([ix, iy, w - ix, h - iy], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(22))
        mw, mh = int(w * 0.10), int(h * 0.06)
        canvas = Image.new("RGB", (w + 2 * mw, h + 2 * mh), CREAM)
        canvas.paste(im, (mw, mh), mask)
        ring = ImageDraw.Draw(canvas)
        pad = 40
        ring.ellipse([mw + ix - pad, mh + iy - pad, mw + w - ix + pad, mh + h - iy + pad],
                     outline=(32, 26, 16), width=11)
        im = fit(canvas)
    im.save(RAW / f"{slug}.jpg", quality=92, optimize=True)
    print(f"   -> raw/{slug}.jpg {im.size}")


def main() -> None:
    catalog = json.loads((ROOT / "data" / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    want = set(sys.argv[1:])
    OUT.mkdir(exist_ok=True)
    RAW.mkdir(exist_ok=True)
    n = 0
    for d in catalog["designs"]:
        art = d.get("art")
        if not art or (want and d["slug"] not in want):
            continue
        url = art.get("master_url")
        if not url:
            continue
        dest = OUT / f"{d['slug']}.jpg"
        print(f"{d['slug']} <- {url[:90]}...")
        if art.get("master_note"):
            print(f"   note: {art['master_note']}")
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.5"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
            while chunk := r.read(1 << 16):
                f.write(chunk)
        print(f"   -> {dest.name} ({dest.stat().st_size // 1024} KB)")
        prep_plate(d["slug"], dest)
        n += 1
    print(f"{n} master(s) in {OUT}/ (git-ignored; reproducible from the catalog's URLs)")


if __name__ == "__main__":
    main()
