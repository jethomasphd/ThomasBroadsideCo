#!/usr/bin/env python3
"""The Foreman's hands: orders -> pressroom/RUN_SHEET.md + one ticket per
physical order [D5]. Big type, printable, three statuses. SHIPPED is never
written by this tool — humans ship [D9].

  python3 tools/make_job_tickets.py            # from data/orders/orders.csv
  python3 tools/make_job_tickets.py --sample   # rehearse from the sample book
"""
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRESSROOM = ROOT / "pressroom"
WORKED = ("CONFIRMED", "QUEUED", "ON_PRESS", "HOLD")


def load_orders(sample: bool):
    path = ROOT / "data" / "orders" / ("orders.sample.csv" if sample else "orders.csv")
    if not path.exists():
        sys.exit(f"{path.name} not found — run tools/pull_ledger.py first (or use --sample)")
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh)), path.name


def physical(o) -> bool:
    items = o.get("items") or ""
    return ":print:" in items or ":edition:" in items or o.get("kind") == "wholesale"


def sku_titles():
    catalog = json.loads((ROOT / "data" / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    names = {d["sku"]: d["title"] for d in catalog["designs"]}
    names.update({s["sku"]: s["title"] for s in catalog.get("sets", [])})
    return names


def items_lines(o, names):
    lines = []
    for item in (o.get("items") or "").split("|"):
        parts = item.split(":")
        if len(parts) == 3:
            sku, tier, qty = parts
            lines.append(f"| {qty} × | **{names.get(sku, sku)}** | {tier.upper()} | `{sku}` |")
    return lines


def ticket(o, names) -> str:
    is_edition = ":edition:" in (o.get("items") or "")
    header = "# 🗹 JOB TICKET — " + o["id"]
    rows = "\n".join(items_lines(o, names)) or "| — | (see note) | | |"
    edition_block = (
        "\n> **EDITION — DAVID NUMBERS & INSPECTS.** Pencil, bottom left, `N of 250`.\n"
        "> Emboss the maker's mark. Log the number below before packing.\n\n"
        "**Edition number(s) assigned:** ______________\n"
    ) if is_edition else ""
    addr = (o.get("address") or "").replace(", ", "\n")
    return f"""{header}

**Status:** {o['status']} &nbsp;·&nbsp; **Taken:** {o['ts'][:10]} &nbsp;·&nbsp; **Source:** {o.get('source', '')}

## The job

| Qty | Sheet | Tier | SKU |
|---|---|---|---|
{rows}
{edition_block}
## Ship to

```
{o.get('name', '')}
{addr or '(digital / no address — see order book)'}
```

{('**Note:** ' + o['note']) if o.get('note') else ''}

## The four boxes — in order, in pencil

- [ ] **PULLED** — stock counted out, backs clean
- [ ] **INSPECTED** — David's box. Front and back, square trim, true ink. *No signature, no shipping — no exceptions [D6].*
- [ ] **PACKED** — rolled loose on the core, kraft, caps taped flat, label straight, colophon card in
- [ ] **SHIPPED** — tracking number written here **and** tapped into the pressroom page (that sends the customer's note):

**Tracking:** ______________________________

---
*Thomas Broadside Co. · the spike keeps the truth: only a human hand marks shipped.*
"""


def main() -> None:
    sample = "--sample" in sys.argv
    orders, source = load_orders(sample)
    names = sku_titles()
    tickets_dir = PRESSROOM / "tickets"
    tickets_dir.mkdir(parents=True, exist_ok=True)

    queue = [o for o in orders if o["status"] in WORKED and physical(o)]
    queue.sort(key=lambda o: o["ts"])  # oldest first is honest work

    for old in tickets_dir.glob("TICKET-*.md"):
        old.unlink()
    for o in queue:
        (tickets_dir / f"TICKET-{o['id']}.md").write_text(ticket(o, names), encoding="utf-8")

    def job_summary(o) -> str:
        parts = []
        for item in (o.get("items") or "").split("|"):
            bits = item.split(":")
            if len(bits) == 3:
                sku, tier, qty = bits
                parts.append(f"{qty}× {names.get(sku, sku)} ({tier})")
        return "; ".join(parts)

    today = date.today().isoformat()
    rows = "\n".join(
        f"| {o['id']} | {o['status']} | {o['ts'][:10]} | {job_summary(o)} "
        f"| {'★ EDITION' if ':edition:' in (o.get('items') or '') else ''} |"
        for o in queue
    ) or "| — | the spike is clear | | | |"
    sheet = f"""# ☀ RUN SHEET — {today}

**{len(queue)} physical order(s) on the spike.** Oldest first. Editions marked ★ wait for David.
{'*(rehearsal from ' + source + ' — not live orders)*' if sample else ''}

| Order | Status | Taken | Job | |
|---|---|---|---|---|
{rows}

**The morning:** pull → press → David's eye → tube → label → tracking → tap SHIPPED
on the pressroom page. One ticket per order in `pressroom/tickets/`.

**The rule of the room:** three buttons, no passwords before coffee, and nothing
ships without the inspected box signed [D5][D6].

*Stock low? Tell the book — text Jacob the counts. The book flags reprints at 50 sheets.*
"""
    (PRESSROOM / "RUN_SHEET.md").write_text(sheet, encoding="utf-8")
    print(f"run sheet + {len(queue)} ticket(s) written from {source}")


if __name__ == "__main__":
    main()
