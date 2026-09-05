# Commerce — Three Buys, One Cart, One Secret

> **SUPERSEDED — 2026-09-05.** Commerce runs through Shopify now
> (Register, D2 amendment); see `docs/SHOPIFY_RUNBOOK.md`. This page
> describes the retired owned cart and checkout, kept for the record
> until Demolition Day.

The proposal's storefront rule stands: **digital, print, and edition on
one page. Nobody leaves because the price was wrong** (§V). The store
rents exactly one thing — the payment rail — and owns everything else
[D2]. Every tier has an **Add to cart**; the cart checks out through one
worker that creates a Stripe Checkout Session server-side, priced from
the catalog. No per-SKU payment links to hand-make, no cart platform to
rent: one secret wires the whole register. Wholesale stays invoiced,
never carted (§III).

## The flow

```
product page ──[Add to cart]──► cart.html (localStorage; display prices only)
                                     │ [Check out]
                                     ▼
                        functions/api/checkout.js
                        re-prices every line from the catalog (GEN:PRICES),
                        computes tube shipping (free ≥ $75), creates a
                        Stripe Checkout Session ──► Stripe-hosted payment page
                                     │ payment succeeds (Apple/Google Pay included)
                                     ▼
                        functions/api/stripe-webhook.js
                        verifies signature, writes order:<id> to KV
                        status CONFIRMED · parcel token if any digital
                                     │
        ┌────────────────────────────┴───────────────────────────┐
        ▼ digital items                                          ▼ physical items
  email w/ one download link per sheet                 Foreman's morning tickets →
  (Resend, if set; else the Shopkeeper                 pressroom → Ben & David [D5]
  letters it) /api/parcel?o=&t=&sku= → 302
```

If `STRIPE_SECRET_KEY` isn't set yet, checkout answers 503 and the cart
opens the **desk fallback**: the customer leaves name, email, and
address, the order lands as `NEW`, and the Shopkeeper replies with a
payment link by hand. The store therefore sells on day one regardless
[D12].

## Setting up Stripe (Jacob, ~15 minutes)

1. Create the Stripe account under Thomas Graphics Inc.
2. Developers → API keys → copy the **secret key** into the Pages secret
   `STRIPE_SECRET_KEY`. That alone turns the register on.
3. Add a webhook endpoint: `https://thomasbroadside.co/api/stripe-webhook`,
   event `checkout.session.completed`. Put its signing secret in the
   `STRIPE_WEBHOOK_SECRET` Pages secret.
4. Optional: enable **Stripe Tax** in the dashboard (set the Austin
   origin address), then set Pages variable `STRIPE_TAX=1` so sessions
   request automatic tax. Confirm specifics with the accountant.
5. Test with one real $9 purchase, then refund yourself from the Stripe
   dashboard. Confirm the order appeared in KV (`/api/spike` or
   `pull_ledger.py`) and the parcel link resolved.

Prices live only in `data/catalog/catalog.json`; `tools/build_site.py`
copies them into the checkout worker's `GEN:PRICES` block and the cart's
`catalog-data.js`, so the browser can never invent a price and a price
change is still one reviewed commit [D9]. (The catalog's old
`stripe_link` fields remain harmless; the cart supersedes them.)

## Digital delivery

Print-ready PDFs are **not** in this repo and never in the public site
tree. Host them at an unguessable base (`PARCEL_BASE_URL`) — an R2
bucket works and keeps the whole estate on one bill. `/api/parcel`
checks the order's token, counts downloads (limit 5), and 302s to
`<PARCEL_BASE_URL>/<sku>.pdf`. Filenames are the SKUs, e.g.
`TB-DOC-PREA.pdf`. Rotating `PARCEL_BASE_URL` invalidates all old
links; do it if a link leaks to a forum.

## Wholesale (invoiced, not carted)

`kind=wholesale` inquiries from the site (or Ben's handshake deals) go:
Shopkeeper drafts the quote → Ben prices labor and freight → Jacob signs
→ Stripe Invoice (or paper invoice for institutions that need one) →
Foreman tickets it like any physical order once paid or terms-approved.
Law firms, schools, co-ops, museum shops, veterans' posts (§III).

## Refund & reprint policy

We are a press: **reprint first, refund second**, never argue twice.
Damaged in transit: reprint ships on the next run, no return needed
(photo suffices). Refunds are issued by Jacob in Stripe; the Shopkeeper
records the outcome in the order note. Digital sales: refund on request
within 14 days, no interrogation — a $9 goodwill decision is not worth a
paragraph of policy.

## The Etsy window (sixty days)

Per §V/§VII: the same catalog listed on Etsy at launch as a demand test;
winners inform the October press run; Etsy stays a discovery window,
never the home. Hard rules [D8]: never mail Etsy buyers, never compete
on price there (provenance is the moat; discounting erases it, §X), and
listings say plainly the home is thomasbroadside.co.

## Reconciliation

Weekly, Shopkeeper + Chronicler: Stripe gross = KV order sum = CSV
mirror, to the dollar. Any gap is investigated the day found. Monthly,
export Stripe's balance report for the accountant; the CSV order book is
the operational record, Stripe is the financial one.
