#!/usr/bin/env python3
"""The shop's typesetting press: renders every design in the catalog to a
complete, print-ready flat file. The site displays these files; the press
prints them; the digital tier sells them.

  data/texts/<slug>.txt  +  site/art masters   ──►  art_src/<slug>.svg   (design source, committed)
  tools/render_art.py (chromium)               ──►  print/<slug>.pdf     (true sheet size, vector)
                                               ──►  site/art/<slug>.jpg  (what the store hangs)

Sheets carry ONLY what belongs on the printed work: the document, its own
kicker/attribution lines, and the printer's imprint. Marketing badges live
on the wall placards, never on the art.

Design-bench dependencies (this tool only; the store itself stays
dependency-free [D2]): pip install pillow fonttools brotli
"""
import base64
import json
import re
from pathlib import Path

from PIL import Image, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "site" / "fonts"
TEXTS = ROOT / "data" / "texts"
OUT = ROOT / "art_src"

PAPER, INK, RED, SOFT = "#FAF6EA", "#201A10", "#9E3123", "#574E3D"
SIZES = {  # points at 72/in
    "p34": (1296, 1728),   # 18 x 24
    "p23": (1728, 2592),   # 24 x 36
    "l43": (1728, 1296),   # 24 x 18
    "l32": (1728, 1152),   # 24 x 16
}
IMPRINT = "AUSTIN · PRINTED BY THOMAS GRAPHICS · MMXXVI"

FACES = {
    "text": "LibreCaslonText-400.woff2",
    "italic": "LibreCaslonText-400i.woff2",
    "bold": "LibreCaslonText-700.woff2",
    "display": "LibreCaslonDisplay-400.woff2",
    "mono": "IBMPlexMono-500.woff2",
}
FAMILY = {"text": "LCT", "italic": "LCT", "bold": "LCT", "display": "LCD", "mono": "PLEX"}
STYLE = {"italic": ' font-style="italic"', "bold": ' font-weight="700"'}

_ttf_cache: dict = {}


def _ttf_path(face: str) -> Path:
    p = OUT / ".ttf" / FACES[face].replace(".woff2", ".ttf")
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        f = TTFont(FONTS / FACES[face])
        f.flavor = None
        f.save(p)
    return p


def _font(face: str, size: float) -> ImageFont.FreeTypeFont:
    key = (face, round(size * 4))
    if key not in _ttf_cache:
        _ttf_cache[key] = ImageFont.truetype(str(_ttf_path(face)), int(round(size * 4)))
    return _ttf_cache[key]


def width_of(text: str, face: str, size: float, tracking: float = 0.0) -> float:
    w = _font(face, size).getlength(text) / 4.0
    return w + tracking * max(len(text) - 1, 0)


def wrap(text: str, face: str, size: float, measure: float) -> list:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if width_of(trial, face, size) <= measure or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Sheet:
    def __init__(self, fmt: str):
        self.w, self.h = SIZES[fmt]
        self.fmt = fmt
        self.parts: list = []

    # ── primitives ──
    def text(self, x, y, s, face, size, fill=INK, anchor="start",
             tracking=0.0, text_length=None):
        a = {"start": "", "middle": ' text-anchor="middle"', "end": ' text-anchor="end"'}[anchor]
        ls = f' letter-spacing="{tracking}"' if tracking else ""
        tl = (f' textLength="{text_length:.1f}" lengthAdjust="spacing"'
              if text_length else "")
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY[face]}"'
            f'{STYLE.get(face, "")} font-size="{size}" fill="{fill}"{a}{ls}{tl}>{esc(s)}</text>')

    def rule(self, x1, y, x2, stroke=INK, w=1.0):
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{stroke}" stroke-width="{w}"/>')

    def image(self, x, y, w, h, jpg_path: Path):
        b64 = base64.b64encode(jpg_path.read_bytes()).decode()
        self.parts.append(
            f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,{b64}"/>')

    # ── composites ──
    def para(self, y, text, face, size, leading, measure, x=None, justify=True):
        """Justified paragraph; returns y after the paragraph."""
        x = (self.w - measure) / 2 if x is None else x
        lines = wrap(text, face, size, measure)
        for i, line in enumerate(lines):
            last = i == len(lines) - 1
            tl = None if (last or not justify) else measure
            self.text(x, y, line, face, size, text_length=tl)
            y += leading
        return y

    def centered_block(self, y, text, face, size, leading, measure):
        for line in wrap(text, face, size, measure):
            self.text(self.w / 2, y, line, face, size, anchor="middle")
            y += leading
        return y

    def fit_display(self, text, measure, max_size, min_size=30, max_lines=4):
        size = max_size
        while size > min_size:
            if len(wrap(text, "display", size, measure)) <= max_lines:
                return size
            size -= 2
        return min_size

    def border(self, inset=34):
        self.parts.append(
            f'<rect x="{inset}" y="{inset}" width="{self.w - 2*inset}" height="{self.h - 2*inset}" '
            f'fill="none" stroke="{INK}" stroke-width="1.6"/>')
        self.parts.append(
            f'<rect x="{inset+8}" y="{inset+8}" width="{self.w - 2*inset - 16}" height="{self.h - 2*inset - 16}" '
            f'fill="none" stroke="{INK}" stroke-width="0.5" opacity="0.55"/>')

    def imprint(self):
        self.text(self.w / 2, self.h - 58, IMPRINT, "mono", 9.5, fill=SOFT,
                  anchor="middle", tracking=2.4)

    def svg(self) -> str:
        css = []
        for face in ("text", "italic", "bold"):
            pass
        defs = []
        for fam, wof, weight, style in (
            ("LCT", FACES["text"], 400, "normal"),
            ("LCT", FACES["italic"], 400, "italic"),
            ("LCT", FACES["bold"], 700, "normal"),
            ("LCD", FACES["display"], 400, "normal"),
            ("PLEX", FACES["mono"], 500, "normal"),
        ):
            b64 = base64.b64encode((FONTS / wof).read_bytes()).decode()
            defs.append(
                f"@font-face{{font-family:'{fam}';font-weight:{weight};font-style:{style};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">'
            f"<style>{''.join(defs)}</style>"
            f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>'
            + "".join(self.parts) + "</svg>")


def blocks(slug: str) -> list:
    return [b.strip() for b in (TEXTS / f"{slug}.txt").read_text(encoding="utf-8").split("===")]


# ── composers ───────────────────────────────────────────────────────────

def two_column_document(slug, fmt="p34", body_size=13.0, leading=16.6):
    kicker, title, body, close = blocks(slug)
    s = Sheet(fmt)
    s.border()
    margin, gutter = 108, 44
    col_w = (s.w - 2 * margin - gutter) / 2
    y = 168
    s.text(s.w / 2, y, kicker.upper(), "mono", 15, fill=RED, anchor="middle", tracking=6)
    y += 54
    dsize = s.fit_display(title, s.w - 2 * margin, 52, max_lines=3)
    for line in wrap(title, "display", dsize, s.w - 2 * margin):
        s.text(s.w / 2, y, line, "display", dsize, anchor="middle")
        y += dsize * 1.14
    y += 6
    s.rule(s.w / 2 - 60, y, s.w / 2 + 60, w=1.2)
    y0 = y + 44

    # two-pass balanced columns: measure everything, split at half height,
    # then draw — columns end together, whitespace sits evenly at the foot
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    units = []  # (kind, text) — kind: 'line' advances leading, 'gap' advances less
    for p in paras:
        lines = wrap(p, "text", body_size, col_w)
        for i, line in enumerate(lines):
            units.append(("line", line, i < len(lines) - 1))  # justify unless last of para
        units.append(("gap", "", False))
    if units and units[-1][0] == "gap":
        units.pop()

    def height_of(us):
        return sum(leading if u[0] == "line" else leading * 0.55 for u in us)

    total = height_of(units)
    split, acc = len(units), 0.0
    for i, u in enumerate(units):
        acc += leading if u[0] == "line" else leading * 0.55
        if acc >= total / 2:
            split = i + 1
            break
    while split < len(units) and units[split][0] == "gap":
        split += 1
    for col, chunk in ((0, units[:split]), (1, units[split:])):
        x = margin + col * (col_w + gutter)
        y = y0
        for kind, line, justify in chunk:
            if kind == "gap":
                y += leading * 0.55
                continue
            natural = width_of(line, "text", body_size)
            tl = col_w if (justify and natural >= col_w * 0.84) else None
            s.text(x, y, line, "text", body_size, text_length=tl)
            y += leading
    yc = s.h - 118
    for line in close.split("\n"):
        s.text(s.w / 2, yc, line.strip(), "italic", 12.5, anchor="middle")
        yc += 18
    s.imprint()
    return s


def bill_of_rights():
    kicker, preamble, amendments = blocks("bill-of-rights")
    title = "The Bill of Rights"
    s = Sheet("p23")
    s.border()
    margin, gutter = 140, 64
    col_w = (s.w - 2 * margin - gutter) / 2
    y = 210
    k1, k2 = kicker.split("\n", 1)
    s.text(s.w / 2, y, k1.upper(), "mono", 17, fill=RED, anchor="middle", tracking=7)
    y = s.centered_block(y + 40, k2, "italic", 17, 25, s.w - 2 * margin - 120) + 14
    s.text(s.w / 2, y + 78, title, "display", 100, anchor="middle")
    y += 116
    s.rule(s.w / 2 - 80, y, s.w / 2 + 80, w=1.3)
    y = s.para(y + 56, preamble, "italic", 17.5, 25, s.w - 2 * margin - 150) + 40

    items = [a.strip() for a in amendments.split("\n\n") if a.strip()]
    y0, bottom = y, s.h - 180
    x = margin
    for item in items:
        head, text = item.split("\n", 1)
        lines = wrap(text.strip(), "text", 19.5, col_w)
        need = 38 + len(lines) * 27 + 32
        if y + need > bottom and x == margin:
            x, y = margin + col_w + gutter, y0
        s.text(x, y, head.upper(), "mono", 15, fill=RED, tracking=3.5)
        y += 34
        for i, line in enumerate(lines):
            s.text(x, y, line, "text", 19.5,
                   text_length=col_w if i < len(lines) - 1 else None)
            y += 27
        y += 32
    s.text(s.w / 2, s.h - 128, "Ratified December 15, 1791", "italic", 15, anchor="middle")
    s.imprint()
    return s


def preamble_sheet():
    kicker, display, body, close = blocks("preamble-to-the-constitution")
    s = Sheet("p34")
    s.border()
    y = 224
    s.text(s.w / 2, y, kicker.upper(), "mono", 15.5, fill=RED, anchor="middle", tracking=7)
    s.text(s.w / 2, y + 230, "We the", "display", 168, anchor="middle")
    s.text(s.w / 2, y + 420, "People", "display", 168, anchor="middle")
    yy = y + 500
    s.rule(s.w / 2 - 76, yy, s.w / 2 + 76, w=1.2)
    yy = s.para(yy + 82, body, "text", 23.5, 38, s.w - 2 * 180)
    s.text(s.w / 2, s.h - 138, close, "mono", 11.5, fill=SOFT, anchor="middle", tracking=4.5)
    s.imprint()
    return s


def gettysburg():
    kicker, title, body, close = blocks("gettysburg-address")
    s = Sheet("p34")
    s.border()
    y = 196
    s.text(s.w / 2, y, kicker.upper(), "mono", 14.5, fill=RED, anchor="middle", tracking=6)
    y = s.centered_block(y + 64, title, "display", 46, 58, s.w - 240) + 10
    s.rule(s.w / 2 - 60, y, s.w / 2 + 60, w=1.2)
    y += 74
    measure = s.w - 2 * 168
    for p in [p.strip() for p in body.split("\n\n") if p.strip()]:
        y = s.para(y, p, "text", 20, 31.5, measure) + 20
    y += 14
    s.rule(s.w / 2 - 46, y, s.w / 2 + 46, w=1.0)
    s.text(s.w / 2, y + 38, close, "italic", 16, anchor="middle")
    s.imprint()
    return s


def quote_sheet(slug):
    kicker, quote, attr = blocks(slug)
    s = Sheet("l43")
    s.border()
    s.text(s.w / 2, 168, kicker.upper(), "mono", 15, fill=RED, anchor="middle", tracking=8)
    measure = s.w - 2 * 190
    size = s.fit_display(quote, measure, 96, min_size=40, max_lines=4)
    lines = wrap(quote, "display", size, measure)
    lh = size * 1.26
    block = len(lines) * lh + 66
    y = (s.h - block) / 2 + size * 0.68
    for line in lines:
        s.text(s.w / 2, y, line, "display", size, anchor="middle")
        y += lh
    s.rule(s.w / 2 - 50, y + 8, s.w / 2 + 50, w=1.1)
    s.text(s.w / 2, y + 46, attr, "italic", 16.5, anchor="middle")
    s.imprint()
    return s


def timeline():
    kicker, span, rows, close = blocks("the-revolution-1765-to-1789")
    s = Sheet("p23")
    s.border()
    y = 250
    s.text(s.w / 2, y, kicker.upper(), "mono", 19, fill=RED, anchor="middle", tracking=10)
    s.text(s.w / 2, y + 120, span, "display", 104, anchor="middle")
    y += 186
    s.rule(s.w / 2 - 90, y, s.w / 2 + 90, w=1.3)
    y += 130
    left, right = 230, s.w - 230
    for row in [r for r in rows.split("\n") if "\t" in r]:
        yr, event = row.split("\t", 1)
        s.text(left, y, yr, "mono", 34, fill=RED, tracking=2)
        s.text(left + 200, y, event, "text", 36)
        s.rule(left, y + 34, right, stroke=SOFT, w=0.6)
        y += 118
    s.text(s.w / 2, s.h - 132, close.title(), "mono", 11, fill=SOFT, anchor="middle", tracking=3.5)
    s.imprint()
    return s


def image_sheet(d, master: Path):
    fmt = d["format"]
    s = Sheet(fmt)
    s.border()
    with Image.open(master) as im:
        iw, ih = im.size
    margin = 96
    caption_h = 150 if fmt in ("l43", "l32") else 190
    box_w, box_h = s.w - 2 * margin, s.h - margin - 90 - caption_h
    scale = min(box_w / iw, box_h / ih)
    w, h = iw * scale, ih * scale
    x, y = (s.w - w) / 2, 90 + (box_h - h) / 2
    s.image(x, y, w, h, master)
    cy = s.h - caption_h + 10
    s.text(s.w / 2, cy, d["title"], "display", 34, anchor="middle")
    sub = d.get("kicker", "").title()
    for a, b in ((" Of ", " of "), (" The ", " the "), (" C. ", " c. "), ("After", "after"),
                 ("Begun", "begun"), ("Engraved", "engraved")):
        sub = sub.replace(a, b)
    sub = sub[0].upper() + sub[1:] if sub else sub
    dates = d.get("date_label", "").replace(" TO ", "–").replace(" · ", " · ")
    s.text(s.w / 2, cy + 34, f"{sub} · {dates}", "italic", 13.5, anchor="middle")
    s.imprint()
    return s


# ── main ────────────────────────────────────────────────────────────────

TYPESET = {
    "declaration-of-independence": lambda d: two_column_document("declaration-of-independence", body_size=12.8, leading=16.2),
    "texas-declaration-of-independence": lambda d: two_column_document("texas-declaration-of-independence", body_size=12.6, leading=16.2),
    "bill-of-rights": lambda d: bill_of_rights(),
    "preamble-to-the-constitution": lambda d: preamble_sheet(),
    "gettysburg-address": lambda d: gettysburg(),
    "washingtons-farewell-address": lambda d: quote_sheet("washingtons-farewell-address"),
    "well-done-is-better-than-well-said": lambda d: quote_sheet("well-done-is-better-than-well-said"),
    "facts-are-stubborn-things": lambda d: quote_sheet("facts-are-stubborn-things"),
    "the-revolution-1765-to-1789": lambda d: timeline(),
}

RAW_ART = ROOT / "art_masters" / "raw"   # the paintings/maps behind image sheets


def main() -> None:
    catalog = json.loads((ROOT / "data" / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    only = set(__import__("sys").argv[1:])
    for d in catalog["designs"]:
        slug = d["slug"]
        if only and slug not in only:
            continue
        if slug in TYPESET:
            sheet = TYPESET[slug](d)
        else:
            master = RAW_ART / f"{slug}.jpg"
            if not master.exists():
                print(f"!! {slug}: no raw art at {master} — skipped")
                continue
            sheet = image_sheet(d, master)
        (OUT / f"{slug}.svg").write_text(sheet.svg(), encoding="utf-8")
        print(f"set {slug} ({sheet.fmt}, {len(sheet.svg()) // 1024} KB)")


if __name__ == "__main__":
    main()
