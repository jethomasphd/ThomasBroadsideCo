# The Shopify Runbook — turning the store on, hand in hand

Jacob's ruling of 2026-09-05 (Register, D2 amendment): the storefront
moves to Shopify; this repo remains the factory and the book of record.
Work these steps **in order** — the order matters once, at the DNS step,
and it's marked. Every step says who clicks. Budget: an afternoon for
Part One, an evening for Part Two, launch when the Registrar's list
clears [D9].

**Files you'll use (in `shopify/` in this repo — regenerate any time
with `python3 tools/make_shopify.py`):**

| File | What it is |
|---|---|
| `products.csv` | All 24 designs + 4 sets, tiers as variants, prices, images, museum labels |
| `parcels.zip` | The 24 print masters named by SKU, for Digital Downloads |
| `redirects.csv` | Old exhibit URLs → new product pages, so no link ever 404s |

---

## Part One — the store exists and takes money (≈2 hours)

**1. Create the store.** shopify.com → Start free trial → sign up with
jethomasphd@gmail.com. Store name: **Thomas Broadside Co.** (the
temporary `.myshopify.com` address doesn't matter — the real domain
comes later). Pick the **Basic** plan when the trial asks ($39/mo,
month-to-month).

**2. Import the products — BEFORE touching the domain.** Admin →
Products → Import → choose `shopify/products.csv` → Import. Shopify
pulls every image from the live thomasbroadside.co and copies them to
its own CDN — which is why this must happen while the old site is still
serving. Two minutes later you have 28 products with tiers, prices, and
the museum label inside each description. Spot-check the Declaration:
three tiers, the sheet image, the label table.

**3. Turn on payments — this is the trust hardware.** Settings →
Payments → Activate **Shopify Payments**: business details (Thomas
Graphics Inc. or the DBA you sell under), EIN, your bank account for
payouts. Statement descriptor: `THOMASBROADSIDE`. Activating it turns
on **Shop Pay, Apple Pay, and Google Pay automatically**. Then, same
page: add **PayPal** (connect or create the business PayPal account).
That's the full trust row at checkout.

**4. Sales tax.** Two halves:
- The permit (state's side): Texas Comptroller sales tax permit —
  comptroller.texas.gov, free, do the application today.
- The collection (Shopify's side): Settings → Taxes and duties →
  United States → add your Texas registration when the permit number
  arrives. Shopify calculates and collects from then on.

**5. Shipping.** Settings → Shipping and delivery → the default profile:
- Domestic: **Free shipping over $75** (condition-based rate), and a
  flat **$8 Standard** under $75 (Ben confirms the real tube cost and
  you adjust [D9]).
- Digital downloads never charge shipping — the CSV already marks them.

**6. Digital delivery.** Admin → Apps → search **"Digital Downloads"**
(Shopify's own, free) → Add. Unzip `parcels.zip`. For each product's
**Digital download** variant, attach its SKU-named PDF (24 uploads,
~30 minutes of clicking; do the flagship five first if you're
impatient). For the four sets' digital variants, attach every member
PDF to the set variant. Set downloads to send automatically on payment.

**7. The dress rehearsal.** Store → view as customer → buy the $9
digital Declaration with your real card. Confirm: Apple Pay/Shop Pay
offered at checkout, the download email arrives, the order shows in
Admin → Orders. Refund yourself (Orders → the order → Refund). Then one
print order the same way — confirm it sits in Orders awaiting
fulfillment — refund it too.

**The store now works end to end.** Everything after is dressing and
the door.

## Part Two — make it ours, then open the door (≈an evening)

**8. Collections (the Rooms).** Products → Collections → Create, four
times, each **automated** with condition *Product tag equals*:
- The Documents → tag `documents` · The Cited Quotes → tag `quotes`
- Portraits, Maps & Texas → tags `founders` OR `maps` OR `texas`
- The Western Canon → tag `canon` · The Sets → tag `set` (handle: `sets`)

**9. Theme.** Online Store → Themes → **Dawn** (free) → Customize:
- Colors: background `#F1ECE0` · text `#201A10` · buttons/solid
  `#201A10` · accent/links `#9E3123` · cards `#FAF6EA`
- Typography: headings — search **Libre Caslon Text** (if the font
  picker lacks it, use **EB Garamond** until the custom-theme pass);
  body the same serif; keep sizes generous.
- Header: text logo `★ THOMAS BROADSIDE CO.`; menu (Navigation →
  Main menu): the four collections + Sets + The Press.
- Homepage sections: Image banner (upload
  `site/art/declaration-of-independence.jpg` from the repo, headline
  "The Declaration, printed the way it was first printed."), then
  Featured collection (The Documents), then Collection list (the four
  rooms), then an Image-with-text telling the press story.
- Announcement bar: `Printed on our own press in Austin, Texas · Every
  quote cited · Free U.S. shipping on prints over $75`
**10. The Press page.** Online Store → Pages → Add page, title **The
Press** — paste the story from the live site's Press page (the house
rules, the family, the honest sentence — that sentence ships with us
[D1]). Add it to the main menu and footer.

**11. Policies.** Settings → Policies: generate the refund/privacy/
shipping templates, then read and edit them into the house voice — you
sign these [D9]. Footer picks them up automatically.

**12. Redirects.** Online Store → Navigation → URL redirects → Import →
`shopify/redirects.csv`. Every old exhibit link now lands on its
product.

**13. ⚠️ THE DOOR — DNS, only after steps 2–12.** Settings → Domains →
Connect existing domain → `thomasbroadside.co`. Shopify shows two DNS
records; set them in the Cloudflare DNS panel (the zone stays at
Cloudflare — only the records change: the A record to Shopify's IP, the
`www` CNAME to Shopify). Set both records to **DNS only** (grey cloud,
not proxied). Within an hour thomasbroadside.co is the Shopify store
with SSL. The old Pages project can be deleted from the Cloudflare
dashboard a week later, once you've seen a quiet, working store.

**14. Analytics and the pixel (now permitted — Register, 2026-09-05).**
Shopify Analytics is on by default. When paid ads start: Apps → Facebook
& Instagram channel → connect → the pixel and catalog sync install
themselves. GROWTH.md's discipline still stands: editions and sets only,
$500 tests, ROAS 2.0 kill-line, paid under the 20% pre-gate cap.

**15. Launch gate — humans sign [D9].** Before announcing: the
Registrar's twelve PENDING verifications cleared by Jacob; Ben confirms
trim sizes, tube costs, and the shipping rate; David proofs from
`print/`. Then Constitution Day, September 17, per D12 — the journal
entry, the list, the network, the door.

---

## The floor, after the switch

- **Ben:** install the **Shopify mobile app**, sign in, live in
  **Orders**. A paid physical order appears with everything on it;
  print what's queued; when it ships, open the order → **Fulfill items**
  → paste the tracking number → Fulfill. That click is the new SHIPPED:
  it emails the customer, and it only ever happens by a human hand —
  the clerks have no Shopify login.
- **David:** edition line items read *Numbered edition* — same gate as
  always: number, emboss, inspect, and only then does Ben fulfill.
- **Jacob:** refunds, prices, and the words stay yours. Monthly:
  Orders → Export → CSV → commit to `data/orders/` in this repo, so
  the book of record outlives any platform [D7].

## What retires, what remains

Retired with honor after DNS moves: the owned cart and checkout worker,
the KV spike, the bell, the parcel window, the pressroom page (the
runbook carries a superseded notice). Remaining, and still the point:
this repo — the texts, the typesetting press, the renders and print
masters (Shopify's product images come FROM here), the catalog as the
one source of truth (`make_shopify.py` regenerates the import any
time), the Register, the gate, and the charters. The factory is the
company; Shopify is the register at the front of the store.
