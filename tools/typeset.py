#!/usr/bin/env python3
"""The shop's typesetting press: renders every design in the catalog to a
complete, print-ready flat file. The site displays these files; the press
prints them; the digital tier sells them.

  data/texts/<slug>.txt  +  art_masters/raw   ──►  art_src/<slug>.svg   (design source, committed)
  tools/render_art.py (chromium)              ──►  print/<slug>.pdf     (true sheet size, vector)
                                              ──►  site/art/<slug>.jpg  (what the store hangs)

The house style is the two inks of the early press: black carries the
words, red carries the structure — kickers, heads, numbers, and the short
rules. Rubrication, the way the first printers used it. Documents are set
as broadside posters: the monumental passage large, not the whole act in
agate. The full transcriptions stay in data/texts/ as the book of record;
every word on a sheet is pulled verbatim from its file.

Sheets carry ONLY what belongs on the printed work: the document, its own
kicker/attribution lines, and the printer's imprint. Marketing badges live
on the wall placards, never on the art.

Design-bench dependencies (this tool only; the store itself stays
dependency-free [D2]): pip install pillow fonttools brotli
"""
import base64
import json
import re
from itertools import combinations
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
IMPRINT = "AUSTIN, TX · PRINTED BY THE THOMAS BROADSIDE CO. · MMXXVI"

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


def balance(text: str, face: str, size: float, measure: float, max_lines: int = 3) -> list:
    """Centered display lines read best balanced — near-equal widths, no
    orphan word — so pick the split that minimizes the widest line."""
    words = text.split()
    need = len(wrap(text, face, size, measure))
    n = max(need, 1)
    if n == 1 or n > max_lines or len(words) > 24:
        return wrap(text, face, size, measure)
    best, best_w = None, float("inf")
    for cuts in combinations(range(1, len(words)), n - 1):
        bounds = (0,) + cuts + (len(words),)
        lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:])]
        widest = max(width_of(l, face, size) for l in lines)
        if widest <= measure and widest < best_w:
            best, best_w = lines, widest
    return best or wrap(text, face, size, measure)


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

    def crule(self, y, half=60, w=1.2):
        """The short red center rule — the sheet's rubric mark."""
        self.rule(self.w / 2 - half, y, self.w / 2 + half, stroke=RED, w=w)

    def image(self, x, y, w, h, jpg_path: Path):
        b64 = base64.b64encode(jpg_path.read_bytes()).decode()
        self.parts.append(
            f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,{b64}"/>')

    # ── composites ──
    def para(self, y, text, face, size, leading, measure, x=None, justify=True):
        """Paragraph; a line is only stretched when it nearly fills the
        measure — stretching short lines opens ugly word-gaps."""
        x = (self.w - measure) / 2 if x is None else x
        lines = wrap(text, face, size, measure)
        for i, line in enumerate(lines):
            last = i == len(lines) - 1
            natural = width_of(line, face, size)
            tl = measure if (justify and not last and natural >= measure * 0.88) else None
            self.text(x, y, line, face, size, text_length=tl)
            y += leading
        return y

    def centered_block(self, y, text, face, size, leading, measure, fill=INK, balanced=False):
        lines = (balance if balanced else wrap)(text, face, size, measure)
        for line in lines:
            self.text(self.w / 2, y, line, face, size, fill=fill, anchor="middle")
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
        """Outer black rule, inner red hairline — both inks on every sheet."""
        self.parts.append(
            f'<rect x="{inset}" y="{inset}" width="{self.w - 2*inset}" height="{self.h - 2*inset}" '
            f'fill="none" stroke="{INK}" stroke-width="1.6"/>')
        self.parts.append(
            f'<rect x="{inset+8}" y="{inset+8}" width="{self.w - 2*inset - 16}" height="{self.h - 2*inset - 16}" '
            f'fill="none" stroke="{RED}" stroke-width="0.8" opacity="0.85"/>')

    def imprint(self):
        self.text(self.w / 2, self.h - 58, IMPRINT, "mono", 9.5, fill=SOFT,
                  anchor="middle", tracking=2.4)

    def svg(self) -> str:
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
            f"<style>{''.join(defs)}text{{text-rendering:geometricPrecision}}</style>"
            f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>'
            + "".join(self.parts) + "</svg>")


def blocks(slug: str) -> list:
    return [b.strip() for b in (TEXTS / f"{slug}.txt").read_text(encoding="utf-8").split("===")]


def passage(slug: str, start: str, end: str) -> str:
    """A verbatim passage from the book of record — the sheet never carries
    words the transcription file doesn't."""
    body = blocks(slug)[2]
    i = body.find(start)
    j = body.find(end, i)
    if i < 0 or j < 0:
        raise SystemExit(f"{slug}: passage '{start[:30]}…{end[-20:]}' not in data/texts — the record is the source")
    return " ".join(body[i:j + len(end)].split())


# ── composers ───────────────────────────────────────────────────────────

def declaration_poster():
    """The Preamble treatment: the truths held self-evident, monumental."""
    kicker, title, _, close = blocks("declaration-of-independence")
    truths = passage("declaration-of-independence",
                     "We hold these truths", "pursuit of Happiness.")
    monumental = "We hold these truths to be self-evident,"
    rest = truths[len(monumental):].strip()
    s = Sheet("p34")
    s.border()
    y = 200
    s.text(s.w / 2, y, kicker.upper(), "mono", 15, fill=RED, anchor="middle", tracking=6)
    y += 76
    for line in balance(title, "display", 41, s.w - 300, max_lines=2):
        s.text(s.w / 2, y, line, "display", 41, anchor="middle")
        y += 56
    y += 4
    s.crule(y, half=70)

    y += 196
    for line in ("We hold these", "truths to be", "self-evident,"):
        s.text(s.w / 2, y, line, "display", 138, anchor="middle")
        y += 170
    y += 40
    y = s.centered_block(y, rest, "text", 26.5, 43, s.w - 2 * 150)
    y += 26
    s.crule(y, half=52, w=1.0)

    yc = s.h - 148
    for line in close.split("\n"):
        s.text(s.w / 2, yc, line.strip(), "italic", 13.5, anchor="middle")
        yc += 22
    s.imprint()
    return s


def texas_poster():
    """The same concept an hour up the road: the resolve, then the republic."""
    _, sub, _, close = blocks("texas-declaration-of-independence")
    resolve = passage("texas-declaration-of-independence",
                      "We, therefore, the delegates", "do now constitute")
    passage("texas-declaration-of-independence",  # the monumental line, verified in the record
            "a free, Sovereign, and independent republic",
            "a free, Sovereign, and independent republic")
    conscious = passage("texas-declaration-of-independence",
                        "conscious of the rectitude", "destinies of nations.")
    made_by = sub.split(", at the Town")[0]
    made_by = made_by[0].upper() + made_by[1:]
    s = Sheet("p34")
    s.border()
    y = 208
    s.text(s.w / 2, y, "WASHINGTON-ON-THE-BRAZOS · MARCH 2, 1836", "mono", 15,
           fill=RED, anchor="middle", tracking=6)
    y += 78
    for line in balance("The Texas Declaration of Independence", "display", 46, s.w - 260, max_lines=2):
        s.text(s.w / 2, y, line, "display", 46, anchor="middle")
        y += 62
    y = s.centered_block(y + 10, made_by, "italic", 15.5, 24, s.w - 320)
    y += 4
    s.crule(y, half=70)

    y = s.centered_block(y + 110, resolve + " —", "text", 22.5, 36.5, s.w - 2 * 168)
    y += 80
    for line in ("a free, Sovereign, and", "independent republic"):
        s.text(s.w / 2, y, line, "display", 96, anchor="middle")
        y += 128
    y += 30
    y = s.centered_block(y, conscious[0].upper() + conscious[1:],
                         "italic", 18.5, 31, s.w - 2 * 200)
    y += 28
    s.crule(y, half=52, w=1.0)

    s.text(s.w / 2, s.h - 132, close.replace(" · ", "   ·   "), "mono", 10.5,
           fill=SOFT, anchor="middle", tracking=3)
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
    s.crule(y, half=80, w=1.3)
    y = s.para(y + 56, preamble, "italic", 17.5, 26, s.w - 2 * margin - 150) + 44

    # balance the two columns: split the ten near half the total height so
    # both feet land together instead of the right column hanging short
    items = []
    for item in [a.strip() for a in amendments.split("\n\n") if a.strip()]:
        head, text = item.split("\n", 1)
        lines = wrap(text.strip(), "text", 20, col_w)
        items.append((head, lines, 36 + len(lines) * 28.5 + 36))
    total = sum(h for _, _, h in items)
    split, acc = len(items), 0.0
    for i, (_, _, h) in enumerate(items):
        acc += h
        if acc >= total / 2:
            split = i + 1
            break
    y0 = y
    for col, chunk in ((0, items[:split]), (1, items[split:])):
        x = margin + col * (col_w + gutter)
        y = y0
        for head, lines, _ in chunk:
            s.text(x, y, head.upper(), "mono", 15.5, fill=RED, tracking=3.5)
            y += 36
            for i, line in enumerate(lines):
                natural = width_of(line, "text", 20)
                tl = col_w if (i < len(lines) - 1 and natural >= col_w * 0.88) else None
                s.text(x, y, line, "text", 20, text_length=tl)
                y += 28.5
            y += 36
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
    s.crule(yy, half=76)
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
    y = s.centered_block(y + 64, title, "display", 46, 58, s.w - 240, balanced=True) + 10
    s.crule(y)
    y += 96
    measure = s.w - 2 * 148
    for p in [p.strip() for p in body.split("\n\n") if p.strip()]:
        y = s.para(y, p, "text", 24, 37.5, measure) + 26
    y += 16
    s.crule(y, half=46, w=1.0)
    s.text(s.w / 2, y + 44, close, "italic", 16.5, anchor="middle")
    s.imprint()
    return s


def quote_sheet(slug):
    kicker, quote, attr = blocks(slug)
    s = Sheet("l43")
    s.border()
    s.text(s.w / 2, 172, kicker.upper(), "mono", 15.5, fill=RED, anchor="middle", tracking=8)
    measure = s.w - 2 * 180
    if "\n" in quote:
        # verse keeps its own line breaks — Dante's tercet is not prose
        lines = [l.strip() for l in quote.split("\n") if l.strip()]
        size = 98.0
        while size > 40 and max(width_of(l, "display", size) for l in lines) > measure:
            size -= 2
    else:
        size = s.fit_display(quote, measure, 98, min_size=40, max_lines=4)
        lines = balance(quote, "display", size, measure, max_lines=4)
    lh = size * 1.26
    block = len(lines) * lh + 70
    y = (s.h - block) / 2 + size * 0.72
    for line in lines:
        s.text(s.w / 2, y, line, "display", size, anchor="middle")
        y += lh
    s.crule(y + 8, half=50, w=1.1)
    s.text(s.w / 2, y + 50, attr, "italic", 17.5, anchor="middle")
    s.imprint()
    return s


def farewell_poster():
    """Room I density for the Farewell: the good-faith counsel entire,
    then the alliances sentence split Texas-style — lead-in, monumental
    phrase, italic continuation — all of it verbatim."""
    kicker, title, p1, lead, monumental, tail, close = blocks("washingtons-farewell-address")
    s = Sheet("p34")
    s.border()
    y = 200
    s.text(s.w / 2, y, kicker.upper(), "mono", 15, fill=RED, anchor="middle", tracking=6)
    s.text(s.w / 2, y + 94, title, "display", 66, anchor="middle")
    y += 134
    s.crule(y, half=70)
    y = s.centered_block(y + 150, p1, "text", 22, 34.5, s.w - 2 * 158, balanced=True)
    y += 96
    y = s.centered_block(y, lead, "text", 23.5, 36, s.w - 2 * 168)
    y += 40
    for line in balance(monumental, "display", 96, s.w - 2 * 130, max_lines=2):
        s.text(s.w / 2, y + 60, line, "display", 96, anchor="middle")
        y += 122
    y += 42
    y = s.centered_block(y, tail, "italic", 19, 31, s.w - 2 * 200)
    y += 32
    s.crule(y, half=52, w=1.0)
    s.text(s.w / 2, s.h - 138, close, "italic", 15.5, anchor="middle")
    s.imprint()
    return s


def beatitudes():
    """Ten verses, rubricated the way scripture always was: the verse
    numbers in red, the words in black, chapter and verse on the sheet."""
    kicker, title, body, close = blocks("the-beatitudes")
    s = Sheet("p34")
    s.border()
    y = 200
    s.text(s.w / 2, y, kicker.upper(), "mono", 15, fill=RED, anchor="middle", tracking=6)
    s.text(s.w / 2, y + 104, title, "display", 84, anchor="middle")
    y += 148
    s.crule(y, half=70)

    # measure the verse block first, then center it between rule and close
    measure = s.w - 2 * 168
    size, leading, ref_h, gap = 23.0, 33.0, 30, 26
    verses = []
    total = 0.0
    for v in [v.strip() for v in body.split("\n\n") if v.strip()]:
        ref, text = v.split("\t", 1)
        lines = balance(text.strip(), "text", size, measure, max_lines=3)
        verses.append((ref, text.strip()))
        total += ref_h + len(lines) * leading + gap
    total -= gap
    top, bottom = y + 40, s.h - 190
    y = top + max((bottom - top - total) / 2, 0) + 18
    for ref, text in verses:
        s.text(s.w / 2, y, ref, "mono", 11, fill=RED, anchor="middle", tracking=3)
        y += ref_h
        y = s.centered_block(y, text, "text", size, leading, measure, balanced=True)
        y += gap
    s.crule(s.h - 178, half=46, w=1.0)
    s.text(s.w / 2, s.h - 136, close, "italic", 15.5, anchor="middle")
    s.imprint()
    return s


def odyssey_poster():
    """The road-opening lines of Western literature, set the way the
    Preamble is set: the address monumental, the sentence flowing on."""
    kicker, monumental, passage, close = blocks("the-odyssey")
    s = Sheet("p34")
    s.border()
    y = 224
    s.text(s.w / 2, y, kicker.upper(), "mono", 15.5, fill=RED, anchor="middle", tracking=7)
    s.text(s.w / 2, y + 360, monumental, "display", 150, anchor="middle")
    yy = y + 452
    s.crule(yy, half=76)
    yy = s.para(yy + 96, passage, "text", 26, 42, s.w - 2 * 164)
    yy += 40
    s.crule(yy, half=52, w=1.0)
    s.text(s.w / 2, s.h - 138, close, "italic", 16.5, anchor="middle")
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
    s.crule(y, half=90, w=1.3)
    y += 148
    left, right = 220, s.w - 220
    for row in [r for r in rows.split("\n") if "\t" in r]:
        yr, event = row.split("\t", 1)
        s.text(left, y, yr, "mono", 38, fill=RED, tracking=2)
        s.text(left + 220, y, event, "text", 41)
        s.rule(left, y + 42, right, stroke=SOFT, w=0.6)
        y += 152
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
    # when the date label only repeats the credit line, print the credit once
    toks = lambda s_: set(re.findall(r"[A-Z0-9]+", s_.upper()))
    caption = sub if toks(dates) <= toks(sub) else f"{sub} · {dates}"
    s.text(s.w / 2, cy + 34, caption, "italic", 13.5, anchor="middle")
    s.imprint()
    return s


# ── main ────────────────────────────────────────────────────────────────

TYPESET = {
    "declaration-of-independence": lambda d: declaration_poster(),
    "texas-declaration-of-independence": lambda d: texas_poster(),
    "bill-of-rights": lambda d: bill_of_rights(),
    "preamble-to-the-constitution": lambda d: preamble_sheet(),
    "gettysburg-address": lambda d: gettysburg(),
    "washingtons-farewell-address": lambda d: farewell_poster(),
    "a-republic-if-you-can-keep-it": lambda d: quote_sheet("a-republic-if-you-can-keep-it"),
    "give-me-liberty": lambda d: quote_sheet("give-me-liberty"),
    "times-that-try-mens-souls": lambda d: quote_sheet("times-that-try-mens-souls"),
    "sworn-upon-the-altar": lambda d: quote_sheet("sworn-upon-the-altar"),
    "well-done-is-better-than-well-said": lambda d: quote_sheet("well-done-is-better-than-well-said"),
    "facts-are-stubborn-things": lambda d: quote_sheet("facts-are-stubborn-things"),
    "with-malice-toward-none": lambda d: quote_sheet("with-malice-toward-none"),
    "a-house-divided": lambda d: quote_sheet("a-house-divided"),
    "the-beatitudes": lambda d: beatitudes(),
    "what-is-a-man-profited": lambda d: quote_sheet("what-is-a-man-profited"),
    "the-odyssey": lambda d: odyssey_poster(),
    "our-heart-is-restless": lambda d: quote_sheet("our-heart-is-restless"),
    "midway-upon-the-journey": lambda d: quote_sheet("midway-upon-the-journey"),
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
