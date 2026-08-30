# Deploying the Store

The whole estate is: **Cloudflare Pages** (serving `site/` + the workers
in `functions/`), **one KV namespace**, **a handful of env vars**, and
**DNS on our own domain** [D2]. Owner: the Keeper; hands: Jacob.

## 0. Prerequisites

- A Cloudflare account (free plan carries this fine at launch scale).
- The domain (`thomasbroadside.co` — working name; any custom domain
  works, update `shop.config.json` when it's final).
- Node for local dev (`npx wrangler`), Python 3.9+ for the tools. No
  other installs; the site has no build step — Python pre-generates the
  pages and they are committed.

## 1. Create the Pages project

Dashboard → Workers & Pages → Create → Pages → **Connect to Git** → this
repository.

- Production branch: `main`
- Build command: *(none)*
- Build output directory: `site`
- The `functions/` directory at the repo root is picked up automatically
  as Pages Functions.

(Equivalent CLI: `npx wrangler pages project create thomas-broadside-co`,
then deploys ride `git push` or `npx wrangler pages deploy site`.)

## 2. Create the KV namespace and bind it

```bash
npx wrangler kv namespace create SHOPKV
```

Copy the returned id into `wrangler.toml` (`kv_namespaces` →
`id = "..."`), replacing `SET_AFTER_CREATE`, and into
`shop.config.json → cloudflare.kv_namespace_id`. Commit. In the Pages
project settings, confirm the binding **SHOPKV** appears for Production
(and Preview, pointing at a *separate* preview namespace if you want
rehearsal data kept apart).

## 3. Environment variables (Pages → Settings → Variables and secrets)

| Var | Required | What |
|---|---|---|
| `PRESS_TOKEN` | yes | The shop token guarding `/api/spike`, `/api/ledger`, `/api/llm`. Generate: `openssl rand -hex 24`. Write it on the card in the supply cabinet; give it to the tools via env. |
| `ANTHROPIC_API_KEY` | for `/api/llm` | From the Anthropic console. Without it, the drafting endpoint returns 503 and everything else still works. |
| `LLM_MODEL` | for `/api/llm` | The pinned model id. Choose the current Sonnet-class model from the models page at docs.claude.com; the Keeper reviews quarterly. Never hardcoded in the repo. |
| `RESEND_API_KEY` | optional | Enables order emails (confirmation + shipped notes) via Resend. Without it, the Shopkeeper letters by hand from the order book. |
| `MAIL_FROM` | with Resend | e.g. `Thomas Broadside Co. <press@thomasbroadside.co>` (domain verified in Resend). |
| `STRIPE_SECRET_KEY` | for checkout | The one secret that turns the register on: `/api/checkout` creates Stripe Checkout Sessions with it. Without it the cart falls back to the shop desk. |
| `STRIPE_WEBHOOK_SECRET` | with Stripe | From the webhook endpoint you create in Stripe (docs/COMMERCE.md). |
| `STRIPE_TAX` | optional | Set to `1` after enabling Stripe Tax in the dashboard; sessions then request automatic tax. |
| `PARCEL_BASE_URL` | for digital delivery | Base URL where the print-ready PDFs live (an R2 bucket with an unguessable prefix works: `https://<bucket-host>/<random-prefix>`). `/api/parcel` 302s paid customers to `<base>/<sku>.pdf`. |

## 4. Custom domain

Pages project → Custom domains → add `thomasbroadside.co` (and `www`,
redirecting to apex). If the domain's DNS is on Cloudflare this is two
clicks; the certificate is automatic.

## 5. Wall the private rooms with Cloudflare Access

Zero Trust → Access → Applications → Add → Self-hosted:

- Application 1: `thomasbroadside.co/pressroom*`
- Application 2: `thomasbroadside.co/ledger*`
- Policy on both: Allow → Emails: Jacob, Ben, David. Session: 1 month
  (the pressroom must not nag [D5]).

The API routes (`/api/spike`, `/api/ledger`, `/api/llm`) are guarded by
`PRESS_TOKEN` instead of Access so the Python tools can reach them
headlessly. Keep it that way — two locks, each where it belongs.

## 6. Wire the tools (Jacob's machine / the clerks' environment)

```bash
export PRESS_TOKEN=...            # same value as the Pages secret
python3 tools/pull_ledger.py      # mirrors KV → data/
python3 tools/make_dashboard.py   # data/ → site/ledger/
python3 tools/selfcheck.py        # must be green before any commit
```

The tools read `shop.config.json → site_url`; point it at a preview
deployment URL to rehearse against preview data.

## 7. Local development

```bash
npx wrangler pages dev site       # serves site/ + functions/ with a local KV
python3 -m http.server -d site    # static-only preview, zero installs
```

## 8. Go-live checklist (target: 2026-09-17 [D12])

- [ ] Pages project live on the custom domain, HTTPS green
- [ ] KV bound; `POST /api/bell` returns 204 from the homepage
- [ ] `PRESS_TOKEN` set; `/pressroom` behind Access; tablet logged in
- [ ] `STRIPE_SECRET_KEY` set; test cart purchase of the $9 Preamble
      end-to-end (COMMERCE.md)
- [ ] Webhook endpoint verified (Stripe CLI or a live $9 test), order
      appears in KV and in `pull_ledger.py`'s CSV
- [ ] `PARCEL_BASE_URL` serving the launch PDFs; parcel link tested
- [ ] Registrar's `PENDING` cleared on every `digital_ready` design
- [ ] Sixty pins banked, first five videos shot (Herald), business
      mailing at the mailhouse (Ben)
- [ ] The gate is printed at the top of `/ledger` [D11]
- [ ] `docs/AFTER_THE_GATE.md` holds everything that didn't make it —
      shipped beats finished [D12]

## Incidents & restore

The disaster-recovery plan is `git clone` + this file: the repo carries
the site, the data mirrors, and the config. KV loss loses at most the
hours since the last `pull_ledger.py` (run it daily; the Chronicler
does). Write every incident, however small, to `docs/incidents/` in
plain English the same day.
