# The Order Book

`orders.csv` is the book of record for every order the store has ever taken
[D7]. It is a **mirror** written by `tools/pull_ledger.py` from the live
ledger in Cloudflare KV — the KV is the live truth, this CSV is the durable
memory that survives every platform. Do not hand-edit it; pull it.

## Columns

| column | meaning |
|---|---|
| `id` | `TB-YYYYMMDD-XXXX`, assigned at the counter |
| `ts` | ISO timestamp, UTC |
| `status` | `NEW → CONFIRMED → QUEUED → ON_PRESS → SHIPPED` (+ `HOLD`, `CANCELED`) [D5] |
| `kind` | `order`, `wholesale`, or `note` |
| `name`, `email` | the customer. First-party data; never leaves the family [D8] |
| `items` | `sku:tier:qty` joined by `\|`, e.g. `TB-DOC-DECL:print:1\|TB-SET-FOUND:digital:1` |
| `amount_usd` | dollars collected (0 until confirmed) |
| `source` | `site` (inquiry counter), `stripe` (paid), `manual` (Ben/Jacob entered) |
| `address` | shipping address for physical tiers, single line |
| `note` | customer note or history summary |

`orders.sample.csv` is fabricated demonstration data (obviously fake names,
`example.com` addresses) so the dashboard and ticket tools can be exercised
before launch. It is never merged into `orders.csv`.

## Who touches what

- **The Shopkeeper** watches for `NEW` and `wholesale` rows and drafts replies.
- **The Foreman** turns `CONFIRMED` physical orders into job tickets and
  advances statuses from the pressroom.
- **The Chronicler** counts everything here against the gate: 150 orders or
  $5,000 by 2027-01-31 [D11].
- **Humans** mark `SHIPPED` — a machine never claims a package is in the
  mail [D9].
