# Commerce — Three Buys, No Cart

The proposal's storefront rule: **digital, print, and edition on one
page. Nobody leaves because the price was wrong** (§V). The store rents
exactly one thing — the payment rail — and owns everything else [D2].
No cart at launch: each buy is a Stripe Payment Link; wholesale is
invoiced, not carted (§III). A cart earns its way in only via
`docs/AFTER_THE_GATE.md`.

## The flow

```
product page ──[Buy digital $9]──► Stripe Payment Link (Stripe-hosted checkout)
                                        │ payment succeeds
                                        ▼
                          functions/api/stripe-webhook.js
                          verifies signature, writes order:<id> to KV
                          status CONFIRMED · parcel token for digital
                                        │
             ┌──────────────────────────┴───────────────────────────┐
             ▼ digital                                              ▼ physical
  email w/ download link (Resend, if set;               Foreman's morning tickets →
  else Shopkeeper letters it by hand)                   pressroom → Ben & David [D5]
  /api/parcel?o=<id>&t=<token> → 302 to the PDF
```

If Stripe isn't wired yet (or a link field is empty), the page shows an
**inquiry button** instead: it posts to `/api/counter`, lands as a `NEW`
order, and the Shopkeeper letters the customer a payment link by hand.
The store therefore works on day one regardless [D12].

## Setting up Stripe (Jacob, ~an hour)

1. Create the Stripe account under Thomas Graphics Inc.; enable Stripe
   Tax (Texas origin; it handles the sales-tax question the right way —
   confirm specifics with the accountant).
2. For each design tier to sell at launch, create a **Product** and a
   **Payment Link**:
   - Name them exactly `<Title> — <Tier>` (e.g. `Preamble to the
     Constitution — Print, 18x24`).
   - Physical tiers: enable shipping address collection (US at launch),
     and set shipping: flat $8 tube, **free over $75** via a shipping
     rate condition (matches `shop.config.json`).
   - **Metadata on the Payment Link: `sku` and `tier`** (e.g.
     `sku=TB-DOC-PREA`, `tier=print`) — the webhook reads these to write
     the order book. Do not skip the metadata.
3. Paste each link URL into `data/catalog/catalog.json →
   tiers.<tier>.stripe_link`, run `python3 tools/build_site.py`, commit.
4. Add a webhook endpoint: `https://thomasbroadside.co/api/stripe-webhook`,
   event `checkout.session.completed`. Put its signing secret in the
   `STRIPE_WEBHOOK_SECRET` Pages secret.
5. Test with one real $9 purchase, then refund yourself from the Stripe
   dashboard. Confirm the order appeared in KV (`/api/spike` or
   `pull_ledger.py`) and the parcel link resolved.

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
