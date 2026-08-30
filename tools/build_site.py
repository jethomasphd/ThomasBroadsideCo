#!/usr/bin/env python3
"""Build the store from the data layer. Python stdlib only [D2].

data/catalog/catalog.json  -> site/documents/<slug>.html   (16 designs + 3 sets)
                           -> site/js/catalog-data.js       (titles/prices for the cart)
                           -> functions/api/checkout.js     (GEN:PRICES block refreshed)
data/journal/entries.json  -> site/journal/<slug>.html + site/journal/index.html
site/index.html            -> generated sections refreshed between GEN markers
site/classroom.html        -> classroom sets refreshed between GEN markers

Generated files are committed; never hand-edit them — change data or
templates and rebuild (orientation, global never-list).
"""
import html
import json
import re
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TPL = Path(__file__).resolve().parent / "templates"

ROOMS = {
    "documents": ("Room I · The Documents", "/#documents"),
    "quotes": ("Room II · The Cited Quotes", "/#quotes"),
    "founders": ("Room III · The Founders", "/#founders"),
    "maps": ("Room III · Maps", "/#founders"),
    "texas": ("Room III · Texas", "/#founders"),
    "classroom": ("The Classroom Room", "/classroom.html"),
    "sets": ("The Classroom Room", "/classroom.html"),
}

TIER_NOTES = {
    "digital": "Instant download · 8.5×11, 11×17 &amp; 18×24 · print it tonight",
    "print": "18 × 24 on 100 lb cream cover · off our press · in a tube",
    "edition": "Numbered of 250 · cotton paper · embossed maker's mark · inspected &amp; numbered by hand",
}
SET_TIER_NOTES = {
    "digital": "Instant download · every sheet, all sizes",
    "print": "Off our press · ships in one tube",
}


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def money(n) -> str:
    return f"${n:,.0f}" if isinstance(n, (int, float)) else "—"


# ── excerpt rendering: the typeset sheet inside the frame ────────────────

def truncate_words(text: str, n: int) -> str:
    words = text.split()
    return text if len(words) <= n else " ".join(words[:n]) + " …"


def excerpt_block(d: dict, for_card: bool = False) -> str:
    art = d.get("art")
    if art:
        return (f'<img class="sheet__img" src="{esc(art["src"])}" '
                f'alt="{esc(art.get("alt", d.get("title", "")))}" loading="lazy">')
    style = d.get("excerpt_style", "columns")
    text = d.get("excerpt", "")
    if style == "columns":
        if for_card:
            text = truncate_words(text, 70 if d.get("format") == "p23" else 44)
        return f'<p class="sheet__text sheet__text--columns">{esc(text)}</p>'
    if style == "center":
        return f'<p class="sheet__text sheet__text--center">{esc(text)}</p>'
    if style == "quote":
        attr = d.get("attribution", "")
        out = f'<p class="sheet__text--quote">{esc(text)}</p>'
        if attr:
            out += f'<p class="sheet__attr">{esc(attr)}</p>'
        return out
    if style == "amendments":
        paras = []
        lines = text.split("\n")
        if for_card:
            lines = lines[:1] + ["Amendments II through X follow, set in two columns."]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"(AMENDMENT [IVX]+\.)\s*(.*)", line)
            if m:
                paras.append(f'<p class="sheet__amend"><b>{esc(m.group(1))}</b> {esc(m.group(2))}</p>')
            else:
                paras.append(f'<p class="sheet__amend">{esc(line)}</p>')
        return "\n".join(paras)
    if style == "timeline":
        items = []
        rows = text.split("\n")
        if for_card:
            rows = rows[:6] + ["\u2026\tthrough Washington's inauguration, 1789"]
        for line in rows:
            if "\t" in line:
                yr, ev = line.split("\t", 1)
                items.append(f'<li><span class="yr">{esc(yr)}</span><span>{esc(ev)}</span></li>')
        return f'<ul class="sheet__timeline">{"".join(items)}</ul>'
    # portrait / map: an engraved awaiting-acquisition label until the
    # open-access art is placed — honest, but hung like everything else
    if style == "portrait":
        words = [w for w in re.sub(r"[^A-Za-z ]", "", d.get("title", "")).split() if w[0].isupper()]
        oval = "·".join(w[0] for w in (words[:1] + words[-1:])) if words else "★"
    else:
        m = re.search(r"\b(1\d{3})\b", d.get("date_label", "") + " " + d.get("title", ""))
        oval = m.group(1) if m else "★"
    return (f'<div class="sheet__placeholder">'
            f'<div class="sheet__oval">{esc(oval)}</div>'
            f'<p class="sheet__attr">{esc(d.get("kicker", ""))}</p>'
            f'<p class="sheet__pending">Final art, from open-access holdings, is placed before the first press run.</p>'
            f"</div>")


# ── the acquire panel: one Add-to-cart per tier ──────────────────────────

def buys_block(item: dict, notes: dict) -> str:
    rows = []
    sku = item.get("sku", "")
    for tier in ("digital", "print", "edition"):
        t = (item.get("tiers") or {}).get(tier)
        if not t:
            continue
        rows.append(
            '        <div class="buy">'
            f'<span class="buy__tier">{tier}</span>'
            f'<span class="buy__price">{money(t.get("price"))}</span>'
            f'<span class="buy__note">{notes.get(tier, "")}</span>'
            f'<button class="btn btn--solid" data-add="{esc(sku)}:{tier}">Add to cart</button>'
            "</div>"
        )
    return "\n".join(rows)


def label_rows(d: dict) -> str:
    rows = []
    for key in ("source", "typeface", "paper", "press", "edition"):
        val = (d.get("label") or {}).get(key)
        if val:
            rows.append(f"        <tr><th>{key}</th><td>{esc(val)}</td></tr>")
    return "\n".join(rows)


def from_price(item: dict) -> str:
    prices = [t.get("price") for t in (item.get("tiers") or {}).values()
              if t and isinstance(t.get("price"), (int, float))]
    return money(min(prices)) if prices else "—"


# ── the exhibit card: framed sheet + wall placard ────────────────────────

def price_line(item: dict) -> str:
    parts = []
    for tier in ("digital", "print", "edition"):
        t = (item.get("tiers") or {}).get(tier)
        if t:
            parts.append(f"{tier.capitalize()} <b>{money(t.get('price'))}</b>")
    return '<span class="dot">·</span>'.join(parts)


def card(d: dict) -> str:
    foot = d.get("card_footer", ["", ""])
    # a quote sheet's excerpt IS its heading; printing both says it twice
    title_block = "" if d.get("excerpt_style") == "quote" else (
        f"""<p class="sheet__title">{d.get('display_heading', esc(d.get('title', '')))}</p>
      <hr class="sheet__rule">
      """)
    fmt = d.get("format", "p34")
    span = " card--wide" if fmt in ("l43", "l32") else ""
    return f"""<a class="card{span}" href="/documents/{esc(d['slug'])}.html">
  <div class="exhibit"><div class="exhibit__mat">
    <div class="sheet sheet--{fmt}"><div class="sheet__inner">
      <p class="sheet__kicker">{esc(d.get('kicker', ''))}</p>
      {title_block}<div class="sheet__body{' sheet__body--art' if d.get('art') else ''}">{excerpt_block(d, for_card=True)}</div>
      <div class="sheet__footer"><span>{esc(foot[0])}</span><span>{esc(foot[1])}</span></div>
    </div></div>
  </div></div>
  <span class="placard">
    <span class="placard__title" style="display:block;">{esc(d.get('title', ''))}</span>
    <span class="placard__meta" style="display:block;">{esc(d.get('date_label', ''))}</span>
    <span class="placard__prices" style="display:block;">{price_line(d)}</span>
  </span>
</a>"""


def room_head(no: str, title: str, curator: str) -> str:
    return f"""<div class="room-head">
  <p class="room-no">{esc(no)}</p>
  <h2>{esc(title)}</h2>
  <p class="curator">{esc(curator)}</p>
</div>"""


def set_band(s: dict, designs_by_slug: dict) -> str:
    dig = (s.get("tiers") or {}).get("digital") or {}
    prt = (s.get("tiers") or {}).get("print") or {}
    minis = []
    for slug in s.get("includes", [])[:4]:
        d = designs_by_slug.get(slug)
        if d:
            minis.append(
                f'<div class="sheet" style="border:1px solid var(--rule-faint);">'
                f'<div class="sheet__inner" style="min-height:8rem;">'
                f'<p class="sheet__kicker">{esc(d.get("date_label", ""))}</p>'
                f'<p class="sheet__title" style="font-size:1rem;">{d.get("display_heading", esc(d["title"]))}</p>'
                f"</div></div>"
            )
    return f"""<div class="grid grid--2" style="align-items:center;gap:3.5rem;">
  <div>
    <p class="kicker">For the classroom</p>
    <h2>{esc(s.get('strap', s.get('title', '')))}</h2>
    <p class="lede">{esc(s.get('one_line', ''))}</p>
    <p class="placard__prices" style="margin:1.4rem 0 1.8rem;font-size:.78rem;">Digital set <b>{money(dig.get('price'))}</b> <span class="dot">·</span> Printed set <b>{money(prt.get('price'))}</b></p>
    <p style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a class="btn btn--solid" href="/documents/{esc(s['slug'])}.html">See the set</a>
      <a class="btn" href="/classroom.html#coops">Teachers and co-ops</a>
    </p>
  </div>
  <div class="exhibit"><div class="exhibit__mat"><div class="grid grid--2" style="gap:1rem;">
    {''.join(minis)}
  </div></div></div>
</div>"""


def replace_gen(page_path: Path, marker: str, content: str) -> None:
    text = page_path.read_text(encoding="utf-8")
    begin, end = f"<!-- GEN:{marker} -->", f"<!-- /GEN:{marker} -->"
    if begin not in text or end not in text:
        raise SystemExit(f"marker GEN:{marker} missing from {page_path}")
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    text = pattern.sub(begin + "\n" + content + "\n    " + end, text)
    page_path.write_text(text, encoding="utf-8")


# ── main builds ──────────────────────────────────────────────────────────

def related_block(d: dict, designs: list) -> str:
    same = [x for x in designs if x["slug"] != d["slug"] and x["line"] == d["line"]]
    rest = [x for x in designs if x["slug"] != d["slug"] and x["line"] != d["line"]]
    picks = (same + rest)[:3]
    return "\n".join(card(x) for x in picks)


def build_products(catalog: dict) -> int:
    tpl = Template((TPL / "product.html").read_text(encoding="utf-8"))
    outdir = SITE / "documents"
    outdir.mkdir(parents=True, exist_ok=True)
    designs = catalog["designs"]
    n = 0
    for d in designs:
        foot = d.get("card_footer", ["", ""])
        room_label, room_href = ROOMS.get(d.get("line", ""), ("The Collection", "/"))
        page = tpl.substitute(
            title=esc(d["title"]),
            meta_description=esc(d.get("one_line", "")),
            kicker=esc(d.get("kicker", "")),
            display_heading="" if d.get("excerpt_style") == "quote"
            else d.get("display_heading", esc(d["title"])),
            excerpt_block=excerpt_block(d),
            body_mod=" sheet__body--art" if d.get("art") else "",
            footer_left=esc(foot[0]),
            footer_right=esc(foot[1]),
            date_label=esc(d.get("date_label", "")),
            one_line=esc(d.get("one_line", "")),
            buys_block=buys_block(d, TIER_NOTES),
            label_rows=label_rows(d),
            provenance=esc(d.get("provenance", "")),
            room_label=esc(room_label),
            room_href=room_href,
            from_price=from_price(d),
            sheet_format=d.get("format", "p34"),
            related_block=related_block(d, designs),
        )
        (outdir / f"{d['slug']}.html").write_text(page, encoding="utf-8")
        n += 1

    by_slug = {x["slug"]: x for x in designs}
    for s in catalog.get("sets", []):
        listing = "".join(
            f"<li><span class='yr'>·</span><span>{esc(by_slug[slug]['title'])}</span></li>"
            for slug in s.get("includes", []) if slug in by_slug
        )
        picks = [by_slug[slug] for slug in s.get("includes", [])[:3] if slug in by_slug]
        page = tpl.substitute(
            title=esc(s["title"]),
            meta_description=esc(s.get("one_line", "")),
            kicker="THE SETS · BUNDLES OF THE SIXTEEN",
            display_heading=esc(s.get("strap", s["title"])),
            excerpt_block=(f'<p class="sheet__text sheet__text--center">{esc(s.get("one_line", ""))}</p>'
                           f'<ul class="sheet__timeline" style="margin-top:.8rem;">{listing}</ul>'),
            body_mod="",
            footer_left="ONE TUBE",
            footer_right="SOURCED &amp; DATED",
            date_label="THE SETS",
            one_line=esc(s.get("audience", "")),
            buys_block=buys_block(s, SET_TIER_NOTES),
            label_rows=(f"        <tr><th>includes</th><td>{len(s.get('includes', []))} sheets, "
                        f"each sourced and dated</td></tr>\n"
                        f"        <tr><th>press</th><td>Thomas Graphics, Austin, Texas</td></tr>"),
            provenance=esc("Sets are bundles of the sixteen designs, never new designs, so every "
                           "set sells through the same press runs."),
            room_label="The Classroom Room",
            room_href="/classroom.html",
            from_price=from_price(s),
            sheet_format="p34",
            related_block="\n".join(card(x) for x in picks),
        )
        (outdir / f"{s['slug']}.html").write_text(page, encoding="utf-8")
        n += 1
    return n


def build_catalog_data(catalog: dict) -> None:
    """The cart's knowledge: titles and prices, generated from the one source
    of truth. Also refreshed inside the checkout worker so the server never
    trusts a browser's price."""
    data = {}
    for item in catalog["designs"] + catalog.get("sets", []):
        tiers = {}
        for tier, t in (item.get("tiers") or {}).items():
            if t and isinstance(t.get("price"), (int, float)):
                tiers[tier] = {"price": t["price"], "physical": tier != "digital"}
        data[item["sku"]] = {"title": item["title"], "slug": item["slug"], "tiers": tiers}

    js = ("// Generated by tools/build_site.py from data/catalog/catalog.json — do not hand-edit.\n"
          f"window.TB_CATALOG = {json.dumps(data, indent=2, sort_keys=True)};\n")
    (SITE / "js").mkdir(parents=True, exist_ok=True)
    (SITE / "js" / "catalog-data.js").write_text(js, encoding="utf-8")

    worker = ROOT / "functions" / "api" / "checkout.js"
    text = worker.read_text(encoding="utf-8")
    begin, end = "/* GEN:PRICES */", "/* /GEN:PRICES */"
    if begin not in text or end not in text:
        raise SystemExit("GEN:PRICES markers missing from functions/api/checkout.js")
    block = f"{begin}\nconst PRICES = {json.dumps(data, sort_keys=True)};\n{end}"
    text = re.sub(re.escape(begin) + r".*?" + re.escape(end), block, text, flags=re.S)
    worker.write_text(text, encoding="utf-8")


def build_journal(journal: dict) -> int:
    tpl = Template((TPL / "journal.html").read_text(encoding="utf-8"))
    outdir = SITE / "journal"
    outdir.mkdir(parents=True, exist_ok=True)
    published = [e for e in journal["entries"] if e.get("status") in ("published", "scheduled")]
    published.sort(key=lambda e: e["date"], reverse=True)
    for e in published:
        body_html = "\n".join(f"    <p>{esc(p)}</p>" for p in e["body"].split("\n\n"))
        page = tpl.substitute(
            title=esc(e["title"]),
            meta_description=esc(e["body"].split("\n")[0][:150]),
            date_label=esc(e["date"]),
            body_html=body_html,
            signed=esc(e.get("signed", "the shop")),
        )
        (outdir / f"{e['slug']}.html").write_text(page, encoding="utf-8")

    items = "\n".join(
        f"""      <div class="journal-item">
        <p class="date">{esc(e['date'])}</p>
        <h3><a href="/journal/{esc(e['slug'])}.html">{esc(e['title'])}</a></h3>
        <p>{esc(e['body'].split(chr(10))[0][:160])}</p>
      </div>"""
        for e in published
    )
    index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Journal — Thomas Broadside Co.</title>
<meta name="description" content="One entry per anniversary. Each entry is also the sheet we printed for it.">
<link rel="stylesheet" href="/css/broadside.css">
</head>
<body>
<div class="topbar">Printed on our own press in Austin, Texas <span class="sep">·</span> Every quote cited</div>
<header class="masthead">
  <a class="brand" href="/"><span class="star">★</span>Thomas Broadside Co.</a>
  <nav>
    <a href="/#documents">Documents</a>
    <a href="/#quotes">Quotes</a>
    <a href="/#founders">Founders</a>
    <a href="/classroom.html">Classroom</a>
    <a href="/press.html">The Press</a>
    <a href="/journal/">Journal</a>
  </nav>
  <span class="desk"><a class="cartlink" href="/cart.html">Cart<b data-cart-count></b></a></span>
</header>
<main class="band">
  <div class="wrap">
    <div class="room-head">
      <p class="room-no">From the pressroom</p>
      <h2>Journal</h2>
      <p class="curator">One entry per anniversary — the story behind each sheet, told from the shop floor. The anniversaries are our editorial calendar for a decade.</p>
    </div>
    <div class="journal-list">
{items}
    </div>
  </div>
</main>
<footer class="colophon"><div class="wrap">
  <p class="motto">Build something that lasts</p>
  <p class="fine">Austin: Printed by Thomas Graphics Inc.</p>
</div></footer>
<div class="toast" data-toast></div>
<script src="/js/catalog-data.js" defer></script>
<script src="/js/cart.js" defer></script>
<script src="/js/bell.js" defer></script>
</body>
</html>
"""
    (outdir / "index.html").write_text(index, encoding="utf-8")
    return len(published)


def build_index_sections(catalog: dict, journal: dict) -> None:
    designs = catalog["designs"]
    docs = [d for d in designs if d["line"] == "documents"]
    quotes = [d for d in designs if d["line"] == "quotes"]
    rest = [d for d in designs if d["line"] in ("founders", "maps", "texas")]
    by_slug = {d["slug"]: d for d in designs}

    docs_html = (
        room_head("Room I", "The Documents",
                  "Five sheets that argued a nation into existence. Read them the way they "
                  "were first read — in ink, at arm's length, on a wall.")
        + '\n<div class="wall wall--4">\n' + "\n".join(card(d) for d in docs) + "\n</div>"
    )
    quotes_html = (
        room_head("Room II", "No spurious Jefferson.",
                  "Half the founder quotes on the internet were never said. Every line we "
                  "print carries its source, date, and document — on the page and on the "
                  "sheet. If we cannot cite it, we do not print it.")
        + '\n<div class="wall wall--2">\n' + "\n".join(card(d) for d in quotes) + "\n</div>"
    )
    rest_html = (
        room_head("Room III", "Founders, Maps & Texas",
                  "The signers sat for history and the painters knew it. A country drawn on "
                  "paper before it existed on land — and the Republic next door, printed an "
                  "hour from where it was declared.")
        + '\n<div class="wall wall--3">\n' + "\n".join(card(d) for d in rest) + "\n</div>"
    )

    founding_set = next((s for s in catalog.get("sets", []) if s["slug"] == "founding-documents-set"), None)
    sets_html = set_band(founding_set, by_slug) if founding_set else ""

    published = sorted(
        [e for e in journal["entries"] if e.get("status") in ("published", "scheduled")],
        key=lambda e: e["date"], reverse=True,
    )[:3]
    journal_html = '<div class="journal-list" style="margin-top:2.5rem;">\n' + "\n".join(
        f"""      <div class="journal-item">
        <p class="date">{esc(e['date'])}</p>
        <h3><a href="/journal/{esc(e['slug'])}.html">{esc(e['title'])}</a></h3>
        <p>{esc(e['body'].split(chr(10))[0][:160])}</p>
      </div>"""
        for e in published
    ) + "\n</div>"

    index = SITE / "index.html"
    replace_gen(index, "DOCUMENTS", docs_html)
    replace_gen(index, "QUOTES", quotes_html)
    replace_gen(index, "SIXTEEN", rest_html)
    replace_gen(index, "SETS", sets_html)
    replace_gen(index, "JOURNAL", journal_html)

    all_sets = "\n".join(
        f'<div style="margin-bottom:4.5rem;">{set_band(s, by_slug)}</div>' for s in catalog.get("sets", [])
    )
    replace_gen(SITE / "classroom.html", "CLASSROOM_SETS", all_sets)


def stamp_assets() -> None:
    """Cache-bust every stylesheet/script URL so a browser can never pair
    fresh markup with a stale broadside.css (seen in the wild, 2026-08-30).
    The stamp is a CRC of the assets themselves: unchanged assets keep
    their stamp, changed assets force a refetch."""
    import zlib
    stamp = 0
    for rel in ("css/broadside.css", "js/bell.js", "js/cart.js",
                "js/counter.js", "js/catalog-data.js"):
        p = SITE / rel
        if p.exists():
            stamp = zlib.crc32(p.read_bytes(), stamp)
    v = format(stamp & 0xFFFFFFFF, "x")
    pat = re.compile(r'((?:href|src)="/(?:css|js)/[^"?]+)(?:\?v=[0-9a-f]+)?"')
    n = 0
    for page in SITE.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        new = pat.sub(lambda m: f'{m.group(1)}?v={v}"', text)
        if new != text:
            page.write_text(new, encoding="utf-8")
            n += 1
    print(f"assets stamped ?v={v} across {n} page(s)")


def main() -> None:
    catalog = load("data/catalog/catalog.json")
    journal = load("data/journal/entries.json")
    n_products = build_products(catalog)
    build_catalog_data(catalog)
    n_journal = build_journal(journal)
    build_index_sections(catalog, journal)
    stamp_assets()
    print(f"built {n_products} exhibit pages, {n_journal} journal entries, "
          f"catalog data + checkout prices, index + classroom refreshed")


if __name__ == "__main__":
    main()
