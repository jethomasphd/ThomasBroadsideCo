#!/usr/bin/env python3
"""Build the store from the data layer. Python stdlib only [D2].

data/catalog/catalog.json  -> site/documents/<slug>.html  (16 designs + 3 sets)
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


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def money(n) -> str:
    return f"${n:,.0f}" if isinstance(n, (int, float)) else "—"


# ── excerpt rendering: the typeset sheet preview ─────────────────────────

def excerpt_block(d: dict) -> str:
    style = d.get("excerpt_style", "columns")
    text = d.get("excerpt", "")
    if style == "columns":
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
        for line in text.split("\n"):
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
        for line in text.split("\n"):
            if "\t" in line:
                yr, ev = line.split("\t", 1)
                items.append(f'<li><span class="yr">{esc(yr)}</span><span>{esc(ev)}</span></li>')
        return f'<ul class="sheet__timeline">{"".join(items)}</ul>'
    # portrait / map: honest placeholder until the open-access art is placed
    return f'<div class="sheet__placeholder">{esc(text)}</div>'


# ── tier rows: the three buys ────────────────────────────────────────────

TIER_NOTES = {
    "digital": "Instant download · 8.5×11, 11×17 &amp; 18×24 · print it tonight",
    "print": "18 × 24 on 100 lb cream cover · off our press · in a tube",
    "edition": "Numbered of 250 · cotton paper · embossed maker's mark",
}
SET_TIER_NOTES = {
    "digital": "Instant download · every sheet, all sizes",
    "print": "Off our press · ships in one tube",
}


def buys_block(item: dict, notes: dict) -> str:
    rows = []
    for tier in ("digital", "print", "edition"):
        t = (item.get("tiers") or {}).get(tier)
        if not t:
            continue
        link = (t.get("stripe_link") or "").strip()
        sku = item.get("sku", "")
        if link:
            btn = f'<a class="btn btn--solid" href="{esc(link)}">Buy</a>'
        else:
            btn = (f'<button class="btn" data-reserve="{esc(sku)}:{tier}:1">'
                   f"Reserve</button>")
        rows.append(
            '        <div class="buy">'
            f'<span class="buy__tier">{tier}</span>'
            f'<span class="buy__price">{money(t.get("price"))}</span>'
            f'<span class="buy__note">{notes.get(tier, "")}</span>'
            f"{btn}</div>"
        )
    return "\n".join(rows)


def label_rows(d: dict) -> str:
    rows = []
    for key in ("source", "typeface", "paper", "press", "edition"):
        val = (d.get("label") or {}).get(key)
        if val:
            rows.append(f"        <tr><th>{key}</th><td>{esc(val)}</td></tr>")
    return "\n".join(rows)


# ── cards for the index grids ────────────────────────────────────────────

def price_line(item: dict) -> str:
    parts = []
    for tier in ("digital", "print", "edition"):
        t = (item.get("tiers") or {}).get(tier)
        if t:
            parts.append(f"{tier.capitalize()} <b>{money(t.get('price'))}</b>")
    return '<span class="dot">·</span>'.join(parts)


def card(d: dict) -> str:
    foot = d.get("card_footer", ["", ""])
    return f"""<a class="card" href="/documents/{esc(d['slug'])}.html">
  <div class="sheet"><div class="sheet__inner">
    <p class="sheet__kicker">{esc(d.get('kicker', ''))}</p>
    <p class="sheet__title">{d.get('display_heading', esc(d.get('title', '')))}</p>
    <hr class="sheet__rule">
    {excerpt_block(d)}
    <div class="sheet__footer"><span>{esc(foot[0])}</span><span>{esc(foot[1])}</span></div>
  </div></div>
  <h3 class="card__title">{esc(d.get('title', ''))}</h3>
  <p class="card__meta">{esc(d.get('date_label', ''))}</p>
  <p class="card__prices">{price_line(d)}</p>
</a>"""


def set_band(s: dict, designs_by_slug: dict) -> str:
    dig = (s.get("tiers") or {}).get("digital") or {}
    prt = (s.get("tiers") or {}).get("print") or {}
    minis = []
    for slug in s.get("includes", [])[:4]:
        d = designs_by_slug.get(slug)
        if d:
            minis.append(sheet_mini(d.get("display_heading", esc(d["title"])), d.get("date_label", "")))
    return f"""<div class="grid grid--2" style="align-items:center;gap:3.5rem;">
  <div>
    <p class="kicker">For the classroom</p>
    <h2>{esc(s.get('strap', s.get('title', '')))}</h2>
    <p class="lede">{esc(s.get('one_line', ''))}</p>
    <p class="card__prices" style="margin:1.4rem 0 1.8rem;">Digital set <b>{money(dig.get('price'))}</b> <span class="dot">·</span> Printed set <b>{money(prt.get('price'))}</b></p>
    <p style="display:flex;gap:1rem;flex-wrap:wrap;">
      <a class="btn btn--solid" href="/documents/{esc(s['slug'])}.html">Shop the set</a>
      <a class="btn" href="/classroom.html">Teachers and co-ops</a>
    </p>
  </div>
  <div class="grid grid--2" style="gap:1.2rem;">
    {''.join(minis)}
  </div>
</div>"""


def sheet_mini(title_html: str, kicker: str) -> str:
    return (f'<div class="sheet"><div class="sheet__inner" style="min-height:8rem;">'
            f'<p class="sheet__kicker">{esc(kicker)}</p>'
            f'<p class="sheet__title" style="font-size:1rem;">{title_html}</p>'
            f"</div></div>")


def replace_gen(page_path: Path, marker: str, content: str) -> None:
    text = page_path.read_text(encoding="utf-8")
    begin, end = f"<!-- GEN:{marker} -->", f"<!-- /GEN:{marker} -->"
    if begin not in text or end not in text:
        raise SystemExit(f"marker GEN:{marker} missing from {page_path}")
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    text = pattern.sub(begin + "\n" + content + "\n    " + end, text)
    page_path.write_text(text, encoding="utf-8")


# ── main builds ──────────────────────────────────────────────────────────

def build_products(catalog: dict) -> int:
    tpl = Template((TPL / "product.html").read_text(encoding="utf-8"))
    outdir = SITE / "documents"
    outdir.mkdir(parents=True, exist_ok=True)
    n = 0
    for d in catalog["designs"]:
        foot = d.get("card_footer", ["", ""])
        page = tpl.substitute(
            title=esc(d["title"]),
            meta_description=esc(d.get("one_line", "")),
            kicker=esc(d.get("kicker", "")),
            display_heading=d.get("display_heading", esc(d["title"])),
            excerpt_block=excerpt_block(d),
            footer_left=esc(foot[0]),
            footer_right=esc(foot[1]),
            date_label=esc(d.get("date_label", "")),
            one_line=esc(d.get("one_line", "")),
            buys_block=buys_block(d, TIER_NOTES),
            label_rows=label_rows(d),
            provenance=esc(d.get("provenance", "")),
        )
        (outdir / f"{d['slug']}.html").write_text(page, encoding="utf-8")
        n += 1
    for s in catalog.get("sets", []):
        includes = {x["slug"]: x for x in catalog["designs"]}
        listing = "".join(
            f"<li>{esc(includes[slug]['title'])} — {esc(includes[slug].get('date_label',''))}</li>"
            for slug in s.get("includes", []) if slug in includes
        )
        page = tpl.substitute(
            title=esc(s["title"]),
            meta_description=esc(s.get("one_line", "")),
            kicker="THE SETS · BUNDLES OF THE SIXTEEN",
            display_heading=esc(s.get("strap", s["title"])),
            excerpt_block=(f'<p class="sheet__text sheet__text--center">{esc(s.get("one_line", ""))}</p>'
                           f'<ul class="sheet__timeline" style="margin-top:.8rem;">{listing}</ul>'),
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
        )
        (outdir / f"{s['slug']}.html").write_text(page, encoding="utf-8")
        n += 1
    return n


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
        <h3><a href="/journal/{esc(e['slug'])}.html" style="text-decoration:none;">{esc(e['title'])}</a></h3>
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
    <a href="/#founders">Founders</a>
    <a href="/#maps-texas">Maps &amp; Texas</a>
    <a href="/classroom.html">Classroom</a>
    <a href="/press.html">The Press</a>
    <a href="/journal/">Journal</a>
  </nav>
</header>
<main class="band">
  <div class="wrap">
    <h1>Journal</h1>
    <p class="lede">One entry per anniversary, roughly twice a month. The anniversaries are the editorial calendar for a decade.</p>
    <div class="journal-list" style="margin-top:3rem;">
{items}
    </div>
  </div>
</main>
<footer class="colophon"><div class="wrap">
  <p class="motto">Build something that lasts</p>
  <p class="fine">Austin: Printed by Thomas Graphics Inc.</p>
</div></footer>
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

    docs_html = '<div class="grid grid--4" style="margin-top:2.5rem;">\n' + "\n".join(card(d) for d in docs) + "\n</div>"

    quotes_html = '<div class="grid grid--2" style="margin-top:2.5rem;">\n' + "\n".join(card(d) for d in quotes) + "\n</div>"
    rest_html = '<div class="grid grid--3" style="margin-top:2.5rem;">\n' + "\n".join(card(d) for d in rest) + "\n</div>"

    by_slug = {d["slug"]: d for d in designs}
    founding_set = next((s for s in catalog.get("sets", []) if s["slug"] == "founding-documents-set"), None)
    sets_html = set_band(founding_set, by_slug) if founding_set else ""

    published = sorted(
        [e for e in journal["entries"] if e.get("status") in ("published", "scheduled")],
        key=lambda e: e["date"], reverse=True,
    )[:3]
    journal_html = '<div class="journal-list" style="margin-top:2.5rem;">\n' + "\n".join(
        f"""      <div class="journal-item">
        <p class="date">{esc(e['date'])}</p>
        <h3><a href="/journal/{esc(e['slug'])}.html" style="text-decoration:none;">{esc(e['title'])}</a></h3>
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
        f'<div style="margin-bottom:4rem;">{set_band(s, by_slug)}</div>' for s in catalog.get("sets", [])
    )
    replace_gen(SITE / "classroom.html", "CLASSROOM_SETS", all_sets)


def main() -> None:
    catalog = load("data/catalog/catalog.json")
    journal = load("data/journal/entries.json")
    n_products = build_products(catalog)
    n_journal = build_journal(journal)
    build_index_sections(catalog, journal)
    print(f"built {n_products} product pages, {n_journal} journal entries, "
          f"index + classroom sections refreshed")


if __name__ == "__main__":
    main()
