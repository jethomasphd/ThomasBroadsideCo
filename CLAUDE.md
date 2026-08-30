# Thomas Broadside Co. — for the clerks

You are working inside a real company: a family print shop in Austin
selling founding documents printed on its own press. **Read
`agents/00-ORIENTATION.md` before doing anything.** Then read the charter
for the role you are performing (`agents/*.md`) and the Register of
Decisions at the end of `docs/FOUNDING_DIALOGUE.md` — D1 through D12 bind
every change in this repo.

## Commands

```bash
python3 tools/selfcheck.py          # run before every commit; must be green
python3 tools/build_site.py         # data/*.json → site pages (generated files are committed)
python3 tools/pull_ledger.py        # live KV → data/*.csv (needs PRESS_TOKEN env)
python3 tools/make_dashboard.py     # data/*.csv → site/ledger/index.html
python3 tools/make_job_tickets.py   # orders → pressroom/ tickets (--sample to rehearse)
npx wrangler pages dev site         # local dev with functions + KV
```

## Hard rules (the short list — the long list is in the orientation)

- Machines draft, humans sign: prices, publications, citations, refunds,
  outbound mail, and anything marked `SHIPPED` require a named human [D9].
- The catalog is nineteen designs until the 2027-01-31 gate (sixteen at
  founding; Jacob amended D3 on 2026-08-30 to add the Lincoln portrait
  and two Lincoln quotes — see the Register); sets are bundles, never
  new designs [D3][D11].
- No frameworks, no dependencies, no third-party analytics, no external
  font/script calls. Static HTML + CSS + vanilla JS; Python stdlib only;
  flat JSON/CSV in `data/` is the book of record [D2][D10].
- Never hand-edit generated output (`site/documents/`, `site/journal/`,
  `site/ledger/`, `pressroom/`); change data or templates, then rebuild.
- No customer-facing surface mentions AI; the one honest sentence lives on
  the Press page [D1]. No secrets in the repo, ever.
- Prefer editing existing files; new scope goes to `docs/AFTER_THE_GATE.md`
  unless Jacob says otherwise [D12].

## Map

Data: `data/` · Store: `site/` · Workers: `functions/api/` · Tools:
`tools/` · Charters: `agents/` · Operating docs: `docs/` · Relay output:
`pressroom/` · Config: `shop.config.json` + `wrangler.toml`.
