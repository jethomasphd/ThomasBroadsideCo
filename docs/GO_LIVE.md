# Go Live — the switch-throwing checklist

Deposited 2026-08-31, after the estate merged to main. Work the phases
in order; each one ends with a check you can see. The store is built so
that **Phase 1 alone makes it live and taking money** — everything after
deepens it. Every fallback is honest: an unset rail degrades to "write
the desk," never to a broken page.

**The one env-var table** (Cloudflare dashboard → Workers & Pages →
your Pages project → Settings → Environment variables → Production;
after any change, redeploy):

| Variable | Set in | Unlocks |
|---|---|---|
| `PRESS_TOKEN` | ✅ already set | pressroom spike, ledger API, mirror tool |
| `STRIPE_SECRET_KEY` | Phase 1 | the register — real checkout |
| `STRIPE_WEBHOOK_SECRET` | Phase 1 | signed order confirmations into KV |
| `STRIPE_TAX` = `1` | Phase 1 (after tax setup) | Stripe automatic sales tax |
| `PARCEL_BASE_URL` | Phase 2 | digital download delivery |
| `RESEND_API_KEY` | Phase 3 | outbound mail (parcel links, shipped notices) |
| `MAIL_FROM` | Phase 3 | e.g. `The Shop Desk <desk@thomasbroadside.co>` |

---

## Phase 0 — confirm the merge deployed (5 minutes)

1. Cloudflare dashboard → the Pages project → Deployments: confirm the
   production deploy from the merge commit succeeded.
2. Open thomasbroadside.co in a private window: the homepage should show
   the "How it works" three-step band and Room III titled **Portraits,
   Maps & Texas** with Lincoln hanging in it. If you see the old site,
   the production branch isn't `main` — fix under Settings → Builds.
3. The bell is already recording: every visit counts into KV from the
   moment this deploy served its first page. Nothing to do.

## Phase 1 — the register: Stripe (≈45 minutes, makes the store LIVE)

1. **Activate the Stripe account** at dashboard.stripe.com: business
   details (Thomas Graphics Inc. / the DBA you sell under), the bank
   account for payouts, and a statement descriptor customers will
   recognize — `THOMASBROADSIDE`.
2. **Live secret key:** Stripe → Developers → API keys → reveal the
   **Secret key** (`sk_live_…`). Paste it into the Pages env as
   `STRIPE_SECRET_KEY`. Never into the repo, ever.
3. **Webhook:** Stripe → Developers → Webhooks → Add endpoint:
   - URL: `https://thomasbroadside.co/api/stripe-webhook`
   - Events: exactly one — `checkout.session.completed`
   - Copy the signing secret (`whsec_…`) into the Pages env as
     `STRIPE_WEBHOOK_SECRET`.
4. **Sales tax (Texas is not optional):** physical goods ship from
   Austin, so Texas sales tax applies. Get the Texas Comptroller sales
   tax permit (comptroller.texas.gov, free), then in Stripe enable
   **Stripe Tax**, add the Texas registration, and set `STRIPE_TAX=1`
   in the Pages env. Until this is done you can still test end-to-end;
   just don't announce.
5. **Redeploy** (Deployments → Retry/redeploy latest) so the functions
   pick up the env.
6. **Prove it:** buy the $9 digital Declaration with a real card.
   - Stripe shows the payment;
   - `/pressroom.html` (or `/api/spike`) shows the order **CONFIRMED**;
   - then refund yourself in the Stripe dashboard (Payments → refund).

**After this phase the store is live.** Cards clear, orders land on the
spike, the ledger counts. Digital buyers get their file by hand from the
desk until Phase 2; physical buyers were always fulfilled by hand.

## Phase 2 — digital parcels (≈1 hour, needs one build task first)

The parcel window 302s a paid customer to `PARCEL_BASE_URL/<SKU>.pdf`
(five downloads per order, tokened). So the files must be named by SKU,
hosted at a private base URL.

1. **Ask the clerks to cut the parcel pack** — this is a build task in
   the repo: SKU-named PDFs (`TB-DOC-DECL.pdf`, …) prepared from the
   print masters, staged in a folder ready to upload. (Not yet done —
   say the word.)
2. **Host on Cloudflare R2** (same dashboard, owned stack [D2]):
   create bucket `tb-parcels`, upload the SKU PDFs, enable public
   access via a custom domain like `parcels.thomasbroadside.co` (R2 →
   bucket → Settings → Custom Domains).
3. Set `PARCEL_BASE_URL=https://parcels.thomasbroadside.co` in the
   Pages env; redeploy.
4. **Prove it:** buy a digital again; the email (Phase 3) or the order's
   parcel link opens the PDF; the sixth click politely refuses.

## Phase 3 — the mail rail: Resend (≈30 minutes)

Without it: no automated emails; orders still record. With it: digital
buyers get their parcel link instantly, and the pressroom's **Shipped**
button emails the tracking number.

1. Create a **Resend** account (resend.com) → Domains → add
   `thomasbroadside.co` → it gives you 3–4 DNS records → add them in
   Cloudflare DNS → verify.
2. API key → Pages env `RESEND_API_KEY`.
3. `MAIL_FROM` = `The Shop Desk <desk@thomasbroadside.co>`.
4. Redeploy. Prove it: test digital order → parcel email arrives; mark
   a test order Shipped in the pressroom → tracking email arrives.

## Phase 4 — lock the back doors: Cloudflare Access (≈20 minutes)

The pressroom and ledger are token-guarded, but put a door in front of
the door: Cloudflare dashboard → Zero Trust → Access → Applications →
Add application (Self-hosted):

- App 1: `thomasbroadside.co/pressroom*` — policy: allow emails Jacob,
  Ben, David (they get a one-time code by email; the phone remembers).
- App 2: `thomasbroadside.co/ledger*` — allow Jacob.

## Phase 5 — the books run daily (≈10 minutes to set up the habit)

From any machine with the repo:

```bash
PRESS_TOKEN=<the token> python3 tools/pull_ledger.py   # KV → data/*.csv
python3 tools/make_dashboard.py                        # → site/ledger/
git add data site/ledger && git commit -m "ledger mirror" && git push
```

Daily, or at worst weekly [D7]. The dashboard shows swings, orders,
revenue, and the gate arithmetic (150 / $5,000 / 2027-01-31). If you
want this automated on a schedule instead of by hand, ask the clerks —
it's an afternoon's work, and the trade-off (a copy of PRESS_TOKEN
stored in the scheduler) is yours to sign [D9].

## Phase 6 — humans sign (the launch gate, no shortcuts)

- **Jacob (Registrar):** clear the bench's 7 PENDING verifications —
  Farewell, Gettysburg, both Franklin/Adams quotes, both Lincoln quotes,
  the Texas Declaration — plus the VERIFY lines on Hamilton (1757),
  Jefferson (Stuart), Lincoln (Healy 1860, 1809–1865). Each one: read
  the primary source, then change `source_verified_by` to your name and
  date. House rule one is not decoration.
- **Ben:** confirm the four trim sizes (18×24, 24×36, 24×18, 24×16),
  stock and tubes on hand, and that the working prices survive the cost
  sheet. Prices change only by Jacob's hand in `catalog.json` [D9].
- **David:** pull proofs of a few masters from `print/` and say whether
  the sheets are worthy of the press. His Hold is final.

## Phase 7 — dress rehearsal (one evening)

With real cards, then refunds: one digital, one print, one edition.
Walk the physical orders across the spike — Start press → Shipped with
a real tracking number → confirm the email. Check the ledger mirrored
all three. Break anything? The desk fallback catches customers while we
fix it.

## Phase 8 — launch day: September 17, 2026 [D12]

- Registrar list clear, rehearsal done, tax collecting.
- Sign and publish the Constitution Day journal entry.
- Announce organic only (the list, the network, the door). Paid waits
  for creative from the real shoot and clears GROWTH.md's bar.
- Then watch the ledger, not the feed.
