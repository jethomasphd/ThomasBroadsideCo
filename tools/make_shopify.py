#!/usr/bin/env python3
"""Generate the Shopify import artifacts from the catalog — the factory
stays in this repo [D2, amended 2026-09-05]; Shopify is the storefront.

  data/catalog/catalog.json ──► shopify/products.csv    (24 designs + 4 sets, tiers as variants)
  print/<slug>.pdf          ──► shopify/parcels.zip     (SKU-named files for Digital Downloads)
                            ──► shopify/redirects.csv   (old exhibit URLs → /products/<handle>)

Run after any catalog or render change, re-import the CSV, and Shopify
matches by Handle. Image URLs point at the live site's art files, so
IMPORT PRODUCTS BEFORE MOVING DNS — Shopify copies the images to its CDN
at import time. Prices are the human-signed figures from the catalog
[D9]. Stdlib only.
"""
import csv
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "shopify"
SITE_URL = "https://thomasbroadside.co"

TIER_LABEL = {"digital": "Digital download", "print": "Press print", "edition": "Numbered edition"}
TIER_SUFFIX = {"digital": "DIG", "print": "PRT", "edition": "EDN"}
TIER_GRAMS = {"digital": 0, "print": 700, "edition": 1100}
TIER_NOTE = {
    "digital": "Instant download — print-ready PDF, the same typesetting as the press run.",
    "print": "Printed on 100 lb cream cover in Austin, shipped rolled in a tube.",
    "edition": "Cotton paper, numbered of 250, embossed maker's mark, inspected by hand.",
}

COLS = ["Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
        "Option1 Name", "Option1 Value", "Variant SKU", "Variant Grams",
        "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
        "Variant Requires Shipping", "Variant Taxable",
        "Image Src", "Image Position", "Image Alt Text",
        "SEO Title", "SEO Description", "Status"]


def esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def body_html(d: dict) -> str:
    """The museum label travels inside the product body — no apps needed."""
    parts = [f"<p><em>{esc(d.get('one_line', ''))}</em></p>",
             f"<p>{esc(d.get('provenance', ''))}</p>"]
    rows = "".join(
        f"<tr><td><strong>{esc(k.title())}</strong></td><td>{esc(v)}</td></tr>"
        for k, v in (d.get("label") or {}).items() if v and v != "—")
    if rows:
        parts.append(f'<table>{rows}</table>')
    parts.append("<p>Rolled in a tube from Austin. Free U.S. shipping on prints over $75. "
                 "Every sheet inspected by hand before it leaves the shop.</p>")
    return "".join(parts)


def set_body_html(s: dict, by_slug: dict) -> str:
    names = "".join(f"<li>{esc(by_slug[i]['title'])}</li>" for i in s.get("includes", []) if i in by_slug)
    return (f"<p><em>{esc(s.get('one_line', ''))}</em></p>"
            f"<p>{esc(s.get('audience', ''))}</p>"
            f"<p><strong>In the set:</strong></p><ul>{names}</ul>"
            "<p>Printed sets ship in one tube from Austin. Every sheet sourced and dated.</p>")


def main() -> None:
    cat = json.loads((ROOT / "data" / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    designs, sets = cat["designs"], cat.get("sets", [])
    by_slug = {d["slug"]: d for d in designs}
    OUT.mkdir(exist_ok=True)

    rows = []
    for d in designs:
        art = d.get("art") or {}
        img = f"{SITE_URL}{art.get('src', '')}"
        tags = f"{d.get('line', '')}, broadside, printed in austin"
        first = True
        for tier in ("digital", "print", "edition"):
            t = (d.get("tiers") or {}).get(tier)
            if not t:
                continue
            row = {c: "" for c in COLS}
            row["Handle"] = d["slug"]
            if first:
                row.update({
                    "Title": d["title"],
                    "Body (HTML)": body_html(d),
                    "Vendor": "Thomas Broadside Co.",
                    "Type": "Broadside",
                    "Tags": tags,
                    "Published": "TRUE",
                    "Image Src": img,
                    "Image Position": "1",
                    "Image Alt Text": art.get("alt", d["title"]),
                    "SEO Title": f"{d['title']} — broadside, printed in Austin, TX",
                    "SEO Description": (d.get("one_line", "") or "")[:320],
                    "Status": "active",
                })
            row.update({
                "Option1 Name": "Tier",
                "Option1 Value": TIER_LABEL[tier],
                "Variant SKU": f"{d['sku']}-{TIER_SUFFIX[tier]}",
                "Variant Grams": str(TIER_GRAMS[tier]),
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": f"{t['price']:.2f}",
                "Variant Requires Shipping": "FALSE" if tier == "digital" else "TRUE",
                "Variant Taxable": "TRUE",
            })
            rows.append(row)
            first = False

    for s in sets:
        flag = by_slug.get((s.get("includes") or [""])[0]) or {}
        img = f"{SITE_URL}{(flag.get('art') or {}).get('src', '')}"
        first = True
        for tier in ("digital", "print"):
            t = (s.get("tiers") or {}).get(tier)
            if not t:
                continue
            row = {c: "" for c in COLS}
            row["Handle"] = s["slug"]
            if first:
                row.update({
                    "Title": s["title"],
                    "Body (HTML)": set_body_html(s, by_slug),
                    "Vendor": "Thomas Broadside Co.",
                    "Type": "Set",
                    "Tags": "set, broadside, printed in austin",
                    "Published": "TRUE",
                    "Image Src": img,
                    "Image Position": "1",
                    "Image Alt Text": s["title"],
                    "SEO Title": f"{s['title']} — broadsides, printed in Austin, TX",
                    "SEO Description": (s.get("one_line", "") or "")[:320],
                    "Status": "active",
                })
            row.update({
                "Option1 Name": "Format",
                "Option1 Value": "Digital set" if tier == "digital" else "Printed set",
                "Variant SKU": f"{s['sku']}-{TIER_SUFFIX[tier]}",
                "Variant Grams": "0" if tier == "digital" else "2200",
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": f"{t['price']:.2f}",
                "Variant Requires Shipping": "FALSE" if tier == "digital" else "TRUE",
                "Variant Taxable": "TRUE",
            })
            rows.append(row)
            first = False
        # the rest of the set's sheets ride along as extra product images
        for pos, inc in enumerate(s.get("includes", [])[1:], start=2):
            m = by_slug.get(inc) or {}
            row = {c: "" for c in COLS}
            row["Handle"] = s["slug"]
            row["Image Src"] = f"{SITE_URL}{(m.get('art') or {}).get('src', '')}"
            row["Image Position"] = str(pos)
            row["Image Alt Text"] = m.get("title", "")
            rows.append(row)

    with open(OUT / "products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    with open(OUT / "redirects.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Redirect from", "Redirect to"])
        for d in designs + sets:
            w.writerow([f"/documents/{d['slug']}.html", f"/products/{d['slug']}"])
        w.writerow(["/classroom.html", "/collections/sets"])
        w.writerow(["/press.html", "/pages/the-press"])
        w.writerow(["/journal/", "/"])

    with zipfile.ZipFile(OUT / "parcels.zip", "w", zipfile.ZIP_DEFLATED) as z:
        n = 0
        for d in designs:
            pdf = ROOT / "print" / f"{d['slug']}.pdf"
            if pdf.exists():
                z.write(pdf, f"{d['sku']}.pdf")
                n += 1
    print(f"shopify/products.csv: {len(rows)} rows ({len(designs)} designs + {len(sets)} sets)")
    print(f"shopify/redirects.csv: {len(designs) + len(sets) + 3} redirects")
    print(f"shopify/parcels.zip: {n} SKU-named print masters "
          f"({(OUT / 'parcels.zip').stat().st_size // 1048576} MB)")


if __name__ == "__main__":
    main()
