#!/usr/bin/env python3
"""Mirror the live KV ledger into the flat-file book of record [D7].

  bell counters  -> data/traffic/bell-YYYY-MM.csv   (date,path,count; __total__ row per day)
  referrers      -> data/traffic/refs-YYYY-MM.csv   (date,referrer,count)
  orders         -> data/orders/orders.csv + orders.json  (full resync)

Auth: PRESS_TOKEN env var. Target: shop.config.json -> site_url (override
with SITE_URL env for previews). KV is the live truth; these files are the
durable memory — run daily (Chronicler's charter). Stdlib only [D2].
"""
import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get(url: str, token: str):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def write_month(month: str, data: dict) -> None:
    tdir = ROOT / "data" / "traffic"
    tdir.mkdir(parents=True, exist_ok=True)

    bell_rows = []
    for day, total in sorted(data.get("bell", {}).items()):
        bell_rows.append([day, "__total__", total])
        for path, n in sorted((data.get("paths", {}).get(day) or {}).items()):
            bell_rows.append([day, path, n])
    with open(tdir / f"bell-{month}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "path", "count"])
        w.writerows(bell_rows)

    ref_rows = []
    for day, refs in sorted(data.get("refs", {}).items()):
        for ref, n in sorted(refs.items()):
            ref_rows.append([day, ref, n])
    with open(tdir / f"refs-{month}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "referrer", "count"])
        w.writerows(ref_rows)


def write_orders(orders: list) -> None:
    odir = ROOT / "data" / "orders"
    odir.mkdir(parents=True, exist_ok=True)
    orders.sort(key=lambda o: o.get("ts", ""))
    cols = ["id", "ts", "status", "kind", "name", "email", "items",
            "amount_usd", "source", "address", "note"]
    with open(odir / "orders.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for o in orders:
            w.writerow([o.get(c, "") for c in cols])
    with open(odir / "orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)


def main() -> None:
    cfg = json.loads((ROOT / "shop.config.json").read_text(encoding="utf-8"))
    site = os.environ.get("SITE_URL", cfg["site_url"]).rstrip("/")
    token = os.environ.get("PRESS_TOKEN", "")
    if not token:
        sys.exit("PRESS_TOKEN env var is required (docs/DEPLOY.md §3)")

    today = date.today()
    months = {today.strftime("%Y-%m"), (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")}
    try:
        for month in sorted(months):
            data = get(f"{site}/api/ledger?month={month}", token)
            write_month(month, data)
            days = len(data.get("bell", {}))
            print(f"bell {month}: {days} day(s) mirrored")
        spike = get(f"{site}/api/spike?limit=500", token)
        orders = spike.get("orders", [])
        write_orders(orders)
        print(f"orders: {len(orders)} mirrored to data/orders/")
    except urllib.error.HTTPError as e:
        sys.exit(f"the ledger tap refused: HTTP {e.code} — check PRESS_TOKEN and the deploy")
    except urllib.error.URLError as e:
        sys.exit(f"could not reach {site}: {e.reason}")


if __name__ == "__main__":
    main()
