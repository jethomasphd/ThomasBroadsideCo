# Thomas Broadside Co.

**Founding documents of America and of the West, printed on our own
press in Austin, Texas.** A venture of Thomas Graphics Inc.

> *Sell provenance, not posters.* There are ten thousand three-dollar
> Declarations on the internet, and every one was made in a browser.
> What nobody else can sell is what we already own: a working press, a
> family that has printed in Austin for decades, and someone who will
> check the quotes.

Three humans own it — **Jacob E. Thomas** (the catalog and the quotes),
**Ben Thomas** (operations and the mailhouse), **David Olivo** (craft,
the veto) — and the machines draft while the humans sign.

## The three house rules

1. **Cited.** Every quote carries source, date, and document — on the
   page and on the sheet. No spurious Jefferson.
2. **Pre-partisan.** The founding era and the Western canon, not a party.
3. **Printed here.** Off our press in Austin. Not print on demand.

## How the company runs

**The storefront is Shopify** — thomasbroadside.co, checkout, orders,
digital delivery, analytics (Register, D2 amendment, 2026-09-05).
Operating it is `docs/SHOPIFY_RUNBOOK.md`; the plain-words tour for the
floor is `docs/HOW_THE_SHOP_WORKS.md`.

**This repository is the factory and the book of record** — the part no
platform can hold:

```
data/texts/            the verified transcriptions (the words themselves)
data/catalog/          the thirty-one designs and four sets — one source of truth
        │
        ▼  tools/typeset.py            (composes each design at true print size)
art_src/*.svg          the committed design sources
        │
        ▼  tools/render_art.py         (chromium renders each source)
print/*.pdf            the press masters            site/art/*.jpg   the display renders
        │
        ▼  tools/make_shopify.py       (generates the store from the catalog)
shopify/               products.csv · parcels.zip · redirects.csv → import into Shopify
```

Change a text, a price, or a design in `data/`; run the press; re-import.
The store is always a *product* of this repo, never the master of it.

## Quickstart

```bash
python3 tools/selfcheck.py       # the bench — run before every commit; must be green
python3 tools/typeset.py         # texts + art masters → art_src/*.svg
python3 tools/render_art.py      # art_src → print/*.pdf + site/art/*.jpg
python3 tools/fetch_art.py       # re-download open-access masters (art_masters/, git-ignored)
python3 tools/make_shopify.py    # catalog → shopify/ import artifacts
```

Design-bench dependencies (tools only): `pillow`, `fonttools`, `brotli`,
and Node with Playwright for rendering. The data layer stays plain JSON
and CSV a person can read in a text editor in ten years [D7].

## The papers

- `docs/SHOPIFY_RUNBOOK.md` — **the live operating document**: turning
  the store on, running it, and Demolition Day for the retired code.
- `docs/HOW_THE_SHOP_WORKS.md` — the two-pager for Ben and David.
- `docs/FOUNDING_DIALOGUE.md` — Companion Session 001 and the **Register
  of Decisions** (D1–D12, with amendments). Binding on every change here.
- `docs/GROWTH.md` — the paid-growth doctrine and its kill-line.
- `docs/AFTER_THE_GATE.md` and `docs/IDEAS.md` — where scope waits.
- `agents/` — the seven clerk charters under `agents/00-ORIENTATION.md`.
- `docs/proposal/` — the original proposal and mockup (August 2026).

**The gate:** 150 orders or $5,000 by **January 31, 2027**, or the press
does not run again [D11]. Launch: **September 17, 2026 — Constitution
Day** [D12].

## Retired, pending demolition

`site/` (except `art/` and `fonts/`), `functions/`, `wrangler.toml`, and
the owned-store tools still serve thomasbroadside.co until the DNS
cutover to Shopify. On Demolition Day (SHOPIFY_RUNBOOK, final section)
they leave the working tree; git history keeps the record.

---

*Set in Libre Caslon, an open revival of the letters William Caslon cut
in London in the 1720s and the face of the first printed Declaration,
with IBM Plex Mono for figures.*

**BUILD SOMETHING THAT LASTS**
