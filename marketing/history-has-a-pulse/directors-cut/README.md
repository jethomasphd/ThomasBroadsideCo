# History has a pulse. — The director’s cut

Open **index.html** for the three finished 75-second films, covers, captions, launch email, script and production record. Read **CAMPAIGN.md** for ready-to-use social copy. The new film replaces the original 24-second website film and 15-second social cuts.

The press makes words public. The words become part of a life.

This edition combines 25.5 seconds of owner-supplied shop imagery with the founding story and Western Canon. Elias provides a measured, stoic male voice; an original chamber score accompanies the machinery. The first 3.5 seconds hold on a still Heidelberg frame while the narrator begins; the same shot then plays at real speed with its original sound. After “just listen,” four seconds belong to the machinery alone. Three subtle book-cover overlays identify Homer, Matthew and Dante. Each shot appears once. Captions remain optional and off by default.

## Rebuild

The complete selected footage, narration, score, end cards, fonts and exact edit are included. No generation calls or Runway account are needed to re-render.

```sh
python -m pip install -r source/requirements-design.txt
python source/build_film.py
python source/build_campaign.py
```

Optional: `--format wide|vertical|square` renders one format. From a repo checkout, add `--web-root site/media/press` to export the 720p website version. That option requires a current landscape master. The storefront itself retains its standard-library-only build.

To change the edit, update `data/campaigns/history-has-a-pulse.json` in the repo and copy it to `source/edit.json`. End cards are editable in `source/endcard.html?format=wide|vertical|square`; capture full-page PNGs at 1920×1080, 1080×1920 and 1080×1080 respectively, with fonts and images loaded. The checked-in PNGs make the film render portable without a browser.

No messages or social posts have been sent. Launch destinations use the original storefront at thomasbroadside.co. Deploy the site update before releasing the campaign.

Book references are editable in `source/book-covers.html?book=sea|hill|wood`, captured at 600×860 into `source/book-covers/`. These are campaign cover designs, not facsimiles or additional products. The principal brand line is “Words to live with.”
