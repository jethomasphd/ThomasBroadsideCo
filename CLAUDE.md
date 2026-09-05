# Thomas Broadside Co. — for the clerks

You are working inside a real company: a family print shop in Austin
selling founding documents printed on its own press. **Read
`agents/00-ORIENTATION.md` before doing anything.** Then read the charter
for the role you are performing (`agents/*.md`) and the Register of
Decisions at the end of `docs/FOUNDING_DIALOGUE.md` — D1 through D12 bind
every change in this repo.

## Commands

```bash
# the factory (the living commands)
python3 tools/selfcheck.py          # run before every commit; must be green
python3 tools/typeset.py            # data/texts + art masters → art_src/*.svg
python3 tools/render_art.py         # art_src → print/*.pdf + site/art/*.jpg
python3 tools/fetch_art.py          # re-download open-access masters (git-ignored)
python3 tools/make_shopify.py       # catalog + print/ → shopify/ import artifacts

# the retired owned store (until Demolition Day — see SHOPIFY_RUNBOOK)
python3 tools/build_site.py         # data → site pages (still the live site pre-cutover)
python3 tools/make_job_tickets.py   # order export → paper tickets, if the floor wants paper
```

## Hard rules (the short list — the long list is in the orientation)

- Machines draft, humans sign: prices, publications, citations, refunds,
  outbound mail, and anything marked `SHIPPED` require a named human [D9].
- The catalog is thirty-one designs until the 2027-01-31 gate (sixteen
  at founding; Jacob amended D3 on 2026-08-30 for Lincoln, and twice on
  2026-09-05 — Room IV, then four founders' quotes and three canon
  plates — see the Register); sets are bundles, never new designs
  [D3][D11].
- The storefront runs on Shopify (Jacob amended D2 on 2026-09-05 — see
  the Register); this repo remains the factory and book of record. The
  factory's code rules stand: no frameworks, no dependencies; Python
  stdlib only; flat JSON/CSV in `data/` is the book of record; the
  catalog is the one source of truth and `tools/make_shopify.py`
  regenerates the store import from it [D2][D10].
- Never hand-edit generated output (`site/documents/`, `site/journal/`,
  `site/ledger/`, `pressroom/`); change data or templates, then rebuild.
- No customer-facing surface mentions AI; the one honest sentence lives on
  the Press page [D1]. No secrets in the repo, ever.
- Prefer editing existing files; new scope goes to `docs/AFTER_THE_GATE.md`
  unless Jacob says otherwise [D12].

## Map

Data: `data/` · Shopify import artifacts: `shopify/` · Retired owned
storefront (kept for the record): `site/` + `functions/api/` · Tools:
`tools/` · Charters: `agents/` · Operating docs: `docs/` (the live one:
`SHOPIFY_RUNBOOK.md`) · Relay output: `pressroom/` · Config:
`shop.config.json` + `wrangler.toml`.
