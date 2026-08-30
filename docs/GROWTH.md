# Growth — Profitable From Day One

Owner: Jacob. Operator: the Herald (channels) and the Chronicler (grading).
Binding alongside the Register [D8][D11] and proposal §VI–§VII. Written
2026-08-30, when the pure-paid math was run and rejected: at average CTR
(1.0%), average site conversion (2.0%), and ~$12 CPM, ads alone return
roughly **$0.80 per $1.00 spent** at our $48 blended average order. The
company therefore grows on owned and earned channels, and paid exists only
as a **profit-taking accelerant on proven designs**.

## The float rule (the whole doctrine in one paragraph)

The company fronts at most **$25,000** as a revolving advertising float —
working capital, not a budget. Stripe pays out in ~2 days, so a campaign
holding its target return recycles its own cash inside a week. Two hard
rules make day-one profitability structural: **(1) cumulative paid spend
may never exceed cumulative paid *contribution* to date** — ads buy their
own next month or they stop — and **(2) the float is never more than half
committed** at once. The float may grow only from paid profits. It is
never topped up from press revenue to chase a losing campaign.

## Paid discipline

| Rule | Value | Why |
|---|---|---|
| Breakeven ROAS | ~1.6 blended (1.7 editions, 1.6 print) | 62.5% blended contribution margin |
| **Kill-line** | **ROAS 2.0**, trailing 14 days | Margin of safety + labor unpriced in margins |
| Graded by | **Our ledger**: UTM-tagged bell traffic + Stripe revenue via `data/orders/orders.csv` | Never the platform's self-graded attribution |
| Test size | $500 per campaign, then hold ROAS ≥ 2.0 or kill without sentiment | Small tuition |
| What paid may sell | **Editions and sets only** ($85–$175) | An edition carries ~$99 contribution and can afford acquisition; a $9 digital never can — digitals arrive free and become the list |
| Starting cadence | ~$450/month (proposal §VI), scaling only per the float rule | The plan's own number |
| **Pre-gate cap** | Paid ≤ **20% of orders** before 2027-01-31 | The gate [D11] measures organic legs; buying orders to pass your own kill-test is self-deception |

**The one Meta structure that clears the bar and keeps [D2]:** cold
video-view campaigns on press-floor footage (ThruPlays cost pennies; the
footage is the moat — §VI), then retargeting **video viewers** with
edition/set creative. Those audiences are built from Meta's own
on-platform engagement signals: **no pixel on our site, ever.** A
server-side Conversions API feed (purchase events from the Stripe webhook
to Meta, first-party, no browser code) would improve Meta's optimization
at real scale — it is **not built and may not be built** without Jacob's
written sign-off and a line in the Register's amendments table, because
sending customer purchase events to a platform is a new data-sharing
decision [D9][D8].

## Measurement (how the Chronicler grades every dollar)

- All paid links carry `?utm_source=<channel>` — convention: `fb-paid`,
  `ig-paid`, `pin-paid`, `pc-mail` (postcards), `cat-mail` (catalog).
  The bell counts `utm_source` as a first-party aggregate referrer
  (`utm-fb-paid` in the "who sent them" table); no per-visitor anything.
- Weekly, the Chronicler lines up: spend (platform invoice) → UTM door
  swings → Stripe revenue by window → ROAS by channel, in the chronicle.
  Paid rows in the ledger are always reported separately from organic so
  the gate reads clean [D11].

## The channel ladder (where volume actually comes from)

1. **Pinterest, 5 pins/day** — pins live for years; the compounding
   workhorse (§VII). Free.
2. **SEO** — museum-label pages are real text with commercial-intent
   queries ("bill of rights print"). Matures in 12–18 months. Free.
3. **Email on anniversaries only** — every digital buyer is an address;
   the list is the compounding asset [D8]. Near-free.
4. **Direct mail via the family mailhouse** — the unfair advantage
   nobody else in the category can afford (§VII). First-party and
   business lists only; never Etsy data [D8].
5. **Etsy window** — pay-per-*sale* acquisition (~9.5% fees), margin-safe
   by construction; package inserts bring buyers home.
6. **Wholesale through Ben's network** — zero-CAC invoiced volume (§III).
7. **Paid accelerant** — everything above this line grows the company;
   this line only harvests proven demand at ROAS ≥ 2.

## The scale picture (for calibration, not prediction)

At 3,000 orders/month (10% edition / 60% print / 30% digital at working
prices): **~$144,600/month revenue, ~$90,400 contribution** before labor
and fixed costs. That volume is 4–5× the proposal's year-three upside and
is reached by compounding — not bought: at average ad rates it would take
~15M impressions and ~$180K/month to buy outright, at a loss. Two
physical truths cap and shape it: editions are a scarcity engine (13
designs × 250 = **3,250 numbered slots in the whole catalog**; sell-outs
are marketing, and steady edition revenue requires the second sixteen
[D3]); and 2,100 physical orders/month ≈ 95 tubes per working day, which
is a pressroom question long before it is a platform question. The press
is the brake, by design (Session 001).

## Review

The Herald runs channels by this file; the Chronicler grades them weekly
in `docs/chronicle/`; Jacob signs any change to the kill-line, the float,
the cap, or the CAPI question [D9]. This file amends only in writing,
here, like the Register.
