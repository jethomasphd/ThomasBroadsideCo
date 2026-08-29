# The Door Count

First-party traffic, counted by our own bell (`site/js/bell.js` →
`functions/api/bell.js` → Cloudflare KV). No third-party analytics, no
cookies, no fingerprinting — a door-swing counter, nothing more [D2][D7].
Respects `DNT`. The pressroom and ledger pages are not counted.

`tools/pull_ledger.py` mirrors the KV counters into monthly CSVs here; the
Chronicler rebuilds `site/ledger/` from them.

## Files

- `bell-YYYY-MM.csv` — columns `date,path,count`. The row with path
  `__total__` is the day's door swings; other rows are per-page.
- `refs-YYYY-MM.csv` — columns `date,referrer,count`. Referrer hostnames
  only (`pinterest.com`, `etsy.com`, `direct`), never full URLs.

`*.sample.csv` files are fabricated demonstration data so the dashboard can
be exercised before launch; the first real pull replaces their role and the
dashboard drops its SAMPLE watermark.
