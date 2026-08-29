#!/usr/bin/env python3
"""The Ledger — five numbers and the gate, as one static page [D7][D11].

Reads data/traffic/*.csv, data/orders/orders.csv, data/stock/stock.json.
Writes site/ledger/index.html (deployed behind Cloudflare Access).
Falls back to *.sample.csv with a visible SAMPLE watermark until the first
real pull. Stdlib only; sparklines are inline SVG.
"""
import csv
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRAFFIC = ROOT / "data" / "traffic"
ORDERS = ROOT / "data" / "orders"


def read_csvs(pattern: str):
    files = sorted(TRAFFIC.glob(pattern))
    rows = []
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            rows.extend(list(csv.DictReader(fh)))
    return rows


def pick_traffic():
    real = read_csvs("bell-????-??.csv")
    if real:
        return real, read_csvs("refs-????-??.csv"), False
    return read_csvs("bell-*.sample.csv"), read_csvs("refs-*.sample.csv"), True


def pick_orders():
    real = ORDERS / "orders.csv"
    if real.exists():
        with open(real, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh)), False
    sample = ORDERS / "orders.sample.csv"
    if sample.exists():
        with open(sample, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh)), True
    return [], True


def sparkline(values, width=260, height=44):
    if not values:
        return ""
    mx = max(values) or 1
    step = width / max(len(values) - 1, 1)
    pts = [(i * step, height - (v / mx) * (height - 4) - 2) for i, v in enumerate(values)]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    fill = line + f" L{pts[-1][0]:.1f},{height} L0,{height} Z"
    return (f'<svg class="spark" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="daily door swings">'
            f'<path class="fillpath" d="{fill}"></path><path d="{line}"></path></svg>')


def main() -> None:
    cfg = json.loads((ROOT / "shop.config.json").read_text(encoding="utf-8"))
    gate = cfg["gate"]
    bell_rows, ref_rows, traffic_sample = pick_traffic()
    order_rows, orders_sample = pick_orders()
    stock = json.loads((ROOT / "data" / "stock" / "stock.json").read_text(encoding="utf-8"))
    sample = traffic_sample or orders_sample

    # ── the five numbers ──
    daily = {}
    for r in bell_rows:
        if r["path"] == "__total__":
            daily[r["date"]] = daily.get(r["date"], 0) + int(r["count"])
    door_swings = sum(daily.values())
    spark_vals = [v for _, v in sorted(daily.items())][-30:]

    confirmed = [r for r in order_rows if r["status"] not in ("CANCELED", "NEW")]
    downloads = sum(1 for r in confirmed if ":digital:" in (r.get("items") or ""))
    n_orders = len(confirmed)
    dollars = sum(int(float(r.get("amount_usd") or 0)) for r in confirmed)
    sheets_left = sum(int(s.get("sheets_on_hand") or 0) for s in stock.get("sheets", {}).values())

    # ── the gate ──
    days_left = (date.fromisoformat(gate["date"]) - date.today()).days
    o_pct = min(100, round(n_orders / gate["orders"] * 100))
    d_pct = min(100, round(dollars / gate["revenue_usd"] * 100))

    # ── tables ──
    page_counts, ref_counts, design_counts, status_counts = {}, {}, {}, {}
    for r in bell_rows:
        if r["path"] != "__total__":
            page_counts[r["path"]] = page_counts.get(r["path"], 0) + int(r["count"])
    for r in ref_rows:
        ref_counts[r["referrer"]] = ref_counts.get(r["referrer"], 0) + int(r["count"])
    for r in order_rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
        for item in (r.get("items") or "").split("|"):
            sku = item.split(":")[0]
            if sku:
                design_counts[sku] = design_counts.get(sku, 0) + 1

    def table(counts, k1, limit=10):
        rows = sorted(counts.items(), key=lambda kv: -kv[1])[:limit]
        body = "\n".join(
            f'<tr><td>{html.escape(k)}</td><td class="num">{v}</td></tr>' for k, v in rows)
        return (f'<table class="ledger-table"><tr><th>{k1}</th><th style="text-align:right;">count</th></tr>'
                f"{body}</table>")

    low = [(sku, s) for sku, s in stock.get("sheets", {}).items()
           if (s.get("sheets_on_hand") or 0) < cfg.get("reprint_trigger_sheets", 50)]
    stamp = date.today().isoformat()
    watermark = ('<p class="kicker" style="color:var(--red);">SAMPLE DATA — fabricated for rehearsal; '
                 "the first real pull_ledger.py run replaces this</p>") if sample else ""

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Ledger — Thomas Broadside Co.</title>
<meta name="robots" content="noindex, nofollow">
<link rel="stylesheet" href="/css/broadside.css">
</head>
<body class="workroom">
<div class="topbar">The ledger <span class="sep">·</span> five numbers and the gate <span class="sep">·</span> rebuilt {stamp}</div>
<header class="masthead">
  <a class="brand" href="/ledger/"><span class="star">★</span>The Ledger</a>
  <nav><a href="/pressroom.html">Pressroom</a><a href="/" target="_blank">The store</a></nav>
</header>
<main class="wrap" style="padding-top:2.5rem;padding-bottom:4rem;">
{watermark}
<div class="gatebox">
  <p class="k">The Gate — {gate['orders']} orders or ${gate['revenue_usd']:,} by {gate['date']} · {days_left} days remain</p>
  <div class="figures">Orders: {n_orders} of {gate['orders']}</div>
  <div class="bar"><i style="width:{o_pct}%;"></i></div>
  <div class="figures">Dollars: ${dollars:,} of ${gate['revenue_usd']:,}</div>
  <div class="bar"><i style="width:{d_pct}%;"></i></div>
  <p class="figures" style="color:var(--ink-soft);">Below the line: {html.escape(gate['below'])} Above: {html.escape(gate['above'])} Nobody negotiates with it in January [D11].</p>
</div>

<div class="statgrid">
  <div class="stat"><div class="k">Door swings</div><div class="v">{door_swings:,}</div><div class="d">{sparkline(spark_vals)}</div></div>
  <div class="stat"><div class="k">Downloads</div><div class="v">{downloads:,}</div><div class="d">digital orders — the doorway</div></div>
  <div class="stat"><div class="k">Orders</div><div class="v">{n_orders:,}</div><div class="d">confirmed, all tiers</div></div>
  <div class="stat"><div class="k">Dollars</div><div class="v">${dollars:,}</div><div class="d">confirmed revenue</div></div>
  <div class="stat"><div class="k">Sheets left</div><div class="v">{sheets_left:,}</div><div class="d">{len(low)} design(s) under reprint line</div></div>
</div>

<div class="grid grid--3" style="margin-top:3rem;gap:2.5rem;">
  <div><h3>Doors by page</h3>{table(page_counts, 'page')}</div>
  <div><h3>Who sent them</h3>{table(ref_counts, 'referrer')}</div>
  <div><h3>Designs ordered</h3>{table(design_counts, 'sku')}<h3 style="margin-top:1.5rem;">Order statuses</h3>{table(status_counts, 'status')}</div>
</div>

<p class="form-note" style="margin-top:3rem;">Five numbers; a sixth requires deleting one [D7]. Counted by our own bell — aggregate only, no cookies, DNT honored. The CSV mirror in <code>data/</code> is the book of record.</p>
</main>
</body>
</html>
"""
    outdir = ROOT / "site" / "ledger"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "index.html").write_text(page, encoding="utf-8")
    mode = "SAMPLE" if sample else "live"
    print(f"ledger rebuilt ({mode}): {door_swings} swings, {n_orders} orders, ${dollars}, gate {o_pct}%/{d_pct}%")


if __name__ == "__main__":
    main()
