#!/usr/bin/env python3
"""The shop's own inspection bench. Run before every commit; a red bench is
a broken build even when nothing crashed (Keeper's charter).

Checks the data layer, the house rules that machines can check, rebuilds
the generated pages, and verifies the estate's files are all present.
Exit 0 green · exit 1 red. Stdlib only [D2].
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS: list[str] = []
WARNINGS: list[str] = []


def problem(msg: str) -> None:
    PROBLEMS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def check_config():
    cfg = json.loads((ROOT / "shop.config.json").read_text(encoding="utf-8"))
    for key in ("name", "site_url", "gate", "launch", "house_rules", "people", "cloudflare"):
        if key not in cfg:
            problem(f"shop.config.json missing '{key}'")
    g = cfg.get("gate", {})
    if g.get("orders") != 150 or g.get("revenue_usd") != 5000 or g.get("date") != "2027-01-31":
        problem("the gate has been altered — 150 orders / $5,000 / 2027-01-31 is D11 and only Jacob amends it in the dialogue file")
    return cfg


def check_catalog():
    cat = json.loads((ROOT / "data" / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    designs = cat.get("designs", [])
    if len(designs) != 24:
        problem(f"the catalog is twenty-four [D3, amended by Jacob 2026-08-30 and 2026-09-05] — found {len(designs)}")
    slugs, skus = set(), set()
    restricted = re.compile(r"official seal|military insignia|park service|arrowhead|america\s*250", re.I)
    for d in designs:
        for key in ("no", "slug", "sku", "line", "title", "kicker", "label", "provenance", "tiers", "status", "source_verified_by"):
            if key not in d:
                problem(f"design {d.get('slug', '?')} missing '{key}'")
        if d.get("slug") in slugs:
            problem(f"duplicate slug {d['slug']}")
        if d.get("sku") in skus:
            problem(f"duplicate sku {d['sku']}")
        slugs.add(d.get("slug")); skus.add(d.get("sku"))
        for tier, t in (d.get("tiers") or {}).items():
            if t is None:
                continue
            price = t.get("price")
            if not isinstance(price, (int, float)) or not (1 <= price <= 2000):
                problem(f"{d['slug']} {tier} price {price!r} fails sanity")
        if d.get("status") == "digital_ready" and "PENDING" in str(d.get("source_verified_by", "")).upper():
            warn(f"{d['slug']} is digital_ready with PENDING verification — Registrar must clear before launch [house rule: cited]")
        blob = json.dumps(d)
        if restricted.search(blob) and "restricted" not in blob.lower():
            warn(f"{d['slug']} mentions a restricted-marks term — Registrar eyes required (proposal §X)")
        # every design is a rendered flat file: sheet on the site (full +
        # card renditions), master for the press
        if not (ROOT / "site" / "art" / f"{d['slug']}.jpg").exists():
            problem(f"{d['slug']}: no flat sheet at site/art/{d['slug']}.jpg — run typeset.py + render_art.py")
        if not (ROOT / "site" / "art" / f"{d['slug']}-card.jpg").exists():
            problem(f"{d['slug']}: no card rendition at site/art/{d['slug']}-card.jpg — run render_art.py")
        if not (ROOT / "print" / f"{d['slug']}.pdf").exists():
            problem(f"{d['slug']}: no print master at print/{d['slug']}.pdf — run render_art.py")
    for s in cat.get("sets", []):
        for inc in s.get("includes", []):
            if inc not in slugs:
                problem(f"set {s['slug']} includes unknown design '{inc}' — sets are bundles of the twenty-four [D3]")
    return cat


def check_calendar_journal():
    cal = json.loads((ROOT / "data" / "calendar" / "anniversaries.json").read_text(encoding="utf-8"))
    for entry in cal.get("dates", []):
        try:
            date.fromisoformat(entry["date"])
        except Exception:
            problem(f"calendar date unparseable: {entry.get('date')!r}")
    if not any(e.get("kind") == "gate" for e in cal.get("dates", [])):
        problem("the gate is missing from the calendar [D11]")
    jr = json.loads((ROOT / "data" / "journal" / "entries.json").read_text(encoding="utf-8"))
    for e in jr.get("entries", []):
        if e.get("status") not in ("draft", "scheduled", "published"):
            problem(f"journal {e.get('slug')} has unknown status {e.get('status')!r}")
        if e.get("status") == "published" and not e.get("signed"):
            problem(f"journal {e.get('slug')} published unsigned — humans sign [D9]")


def check_estate():
    required = [
        "wrangler.toml", "CLAUDE.md", "README.md",
        "docs/FOUNDING_DIALOGUE.md", "docs/DEPLOY.md", "docs/COMMERCE.md",
        "docs/PRESSROOM_RUNBOOK.md", "docs/AFTER_THE_GATE.md",
        "docs/HOW_THE_SHOP_WORKS.md",
        "agents/00-ORIENTATION.md", "agents/REGISTRAR.md", "agents/TYPOGRAPHER.md",
        "agents/SHOPKEEPER.md", "agents/HERALD.md", "agents/FOREMAN.md",
        "agents/CHRONICLER.md", "agents/KEEPER.md",
        "functions/api/bell.js", "functions/api/counter.js", "functions/api/spike.js",
        "functions/api/ledger.js", "functions/api/llm.js",
        "functions/api/stripe-webhook.js", "functions/api/parcel.js",
        "functions/api/checkout.js",
        "site/index.html", "site/press.html", "site/classroom.html",
        "site/pressroom.html", "site/404.html", "site/robots.txt",
        "site/cart.html", "site/thanks.html",
        "site/css/broadside.css", "site/js/bell.js", "site/js/counter.js",
        "site/js/cart.js", "site/js/catalog-data.js",
        "site/fonts/LibreCaslonText-400.woff2",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            problem(f"estate file missing: {rel}")


def check_no_secrets():
    patterns = re.compile(r"(sk_live_|whsec_[A-Za-z0-9]{8,}|api-key\s*[:=]\s*['\"][A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9])")
    me = Path(__file__).resolve()
    for path in ROOT.rglob("*"):
        if path.is_dir() or ".git" in path.parts or path.suffix in (".png", ".pdf", ".woff2", ".zip", ".jpg", ".svg"):
            continue
        if path.resolve() == me:  # the scanner's own pattern source is not a secret
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if patterns.search(text):
            problem(f"possible secret committed in {path.relative_to(ROOT)} — secrets live in Cloudflare env only")


def check_customer_surfaces():
    ban = re.compile(r"AI-powered|powered by AI|artificial intelligence", re.I)
    for page in (ROOT / "site").rglob("*.html"):
        if "ledger" in page.parts or "pressroom" in page.name:
            continue
        if ban.search(page.read_text(encoding="utf-8")):
            problem(f"customer surface leads with AI [D1]: {page.relative_to(ROOT)}")


def rebuild():
    tools = ROOT / "tools"
    for cmd in (
        [sys.executable, str(tools / "build_site.py")],
        [sys.executable, str(tools / "make_dashboard.py")],
        [sys.executable, str(tools / "make_job_tickets.py"), "--sample"],
    ):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            problem(f"{Path(cmd[1]).name} failed:\n{r.stderr.strip()[:400]}")
        else:
            print(f"  · {Path(cmd[1]).name}: {r.stdout.strip()}")


def main() -> None:
    print("The bench — inspecting the shop\n")
    check_config()
    check_catalog()
    check_calendar_journal()
    check_estate()
    check_no_secrets()
    print("rebuilding generated pages:")
    rebuild()
    check_customer_surfaces()

    print()
    for w in WARNINGS:
        print(f"  ⚠ {w}")
    if PROBLEMS:
        for p in PROBLEMS:
            print(f"  ✗ {p}")
        print(f"\nRED — {len(PROBLEMS)} problem(s). A red bench is a broken build.")
        sys.exit(1)
    print(f"GREEN — the bench is clear ({len(WARNINGS)} warning(s) for the Registrar's list).")


if __name__ == "__main__":
    main()
