#!/usr/bin/env python3
"""Fetch the full-resolution print masters for every design that carries
art. Web-weight JPEGs live in site/art/ (committed); the true masters are
large (the NGA Adams is 6811x8259) and land in art_masters/ (git-ignored)
for the pressroom's PDF composition. Stdlib only [D2].

  python3 tools/fetch_art.py                # all masters
  python3 tools/fetch_art.py <slug> [...]   # just these designs

Sources and rights are recorded per design in data/catalog/catalog.json
(art.credit / art.master_url / source_verified_by). Fetching does not
verify: a human confirms every object before its sheet goes on press
[D9, house rule one].
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art_masters"


def main() -> None:
    catalog = json.loads((ROOT / "data" / "catalog" / "catalog.json").read_text(encoding="utf-8"))
    want = set(sys.argv[1:])
    OUT.mkdir(exist_ok=True)
    n = 0
    for d in catalog["designs"]:
        art = d.get("art")
        if not art or (want and d["slug"] not in want):
            continue
        url = art.get("master_url")
        if not url:
            continue
        dest = OUT / f"{d['slug']}.jpg"
        print(f"{d['slug']} <- {url[:90]}...")
        if art.get("master_note"):
            print(f"   note: {art['master_note']}")
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.5"})
        with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
            while chunk := r.read(1 << 16):
                f.write(chunk)
        print(f"   -> {dest.name} ({dest.stat().st_size // 1024} KB)")
        n += 1
    print(f"{n} master(s) in {OUT}/ (git-ignored; the repo carries the web versions in site/art/)")


if __name__ == "__main__":
    main()
