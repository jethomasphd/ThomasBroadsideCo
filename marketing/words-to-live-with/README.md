# Words to Live With — campaign kit

## Corrected edition · 16 September 2026

This edition replaces the original 70-second film with the 80-second film and gives each reading its own imagery. Use the files in this package when replacing previously downloaded or scheduled creative.

| Reading | Dedicated scene | Full film | Social card | Reading guide |
|---|---|---|---|---|
| Homer / Homecoming | Sea at dawn | 00:09–00:20 | 02 | Page 3 |
| Matthew 5:7 / Mercy | Olive hillside and lake | 00:20–00:32 | 03 | Page 4 |
| Matthew 16:26 / The soul | Open stone doorway and dry path | 00:32–00:42 | 04 | Page 5 |
| Augustine / Rest | Cypress courtyard | 00:42–00:52 | 05 | Page 6 |
| Dante / The way | Woodland path | 00:52–01:00 | 06 | Page 7 |

Each subject has one distinct visual identity carried across its corresponding surfaces. The opening reading room remains the general campaign cover; it no longer represents Augustine. No narrative shot loops within a film. The website background remains an intentional silent ambient loop. Captions still start off.

New image masters: `artwork/soul.png` and `artwork/rest.png`, made with the built-in image generation tool. Exact still, Runway motion and Miriam narration prompts are preserved in `source/generation-record.json`. The corrected website film has a new URL to avoid cached copies; old direct URLs redirect to it after deployment.

Start with **`index.html`** for the visual asset library. Everything needed to use and re-edit this campaign is included here.

## Launch

1. Merge the reviewed campaign change and confirm `https://thomasbroadside.co/canon` opens on the original storefront. The homepage Canon navigation and Room IV feature lead there.
2. Use the 80-second film for the full story, the 30-second portrait or square film for a shorter invitation, and the 15-second score-only teaser for Stories. Optional VTT captions accompany the narrated films; captions start off.
3. Copy the channel text from `CAMPAIGN.md`. Use the ordered social PNGs, or upload individual cards with their matching alt text. Copy the relevant URL from `links.json`.
4. Choose an email from `email/`. The EML files are unsent drafts with an embedded image and plain-text alternative. Set the recipients in your mail tool. For an email platform, use the HTML and run its send test; its image URL works after deployment.
5. Give `print/` to the shop. PDFs include embedded fonts, vector type and QR codes, TrimBox and 0.125-inch bleed. The guide is 12 single pages at 6 × 9 inches; the postcard is 9 × 6; the partner sheet is US Letter. They are RGB masters for the shop’s paper/profile and final proof.

**Owner:** Jacob E. Thomas. **Shop contact:** JEThomasPhD@gmail.com · 9501 N Interstate Hwy 35, Austin, TX 78753.

## What is included

- Four finished MP4 films and three optional caption tracks.
- Eleven social PNGs, including the ten-card carousel and LinkedIn/email share image.
- Three print PDFs and three complete email sets.
- Six generated still masters, six original Runway clips, eight Miriam narration clips and the original score.
- Editable HTML artwork, print/email/film builders, local fonts with license notices, exact product-image and text snapshots, generation prompts and IDs, edit timelines, provenance and QA records.

The 1920 × 1080 main film is a delivery master. Runway returned 1280 × 720 source motion clips; those are preserved and scaled in the edit. No native-1080p or archival-footage claim is made. Stills are 1672 × 941.

## Rebuild

Use a separate design environment with `source/requirements-design.txt`; the storefront and catalog builder remain dependency-free. Python 3.10+ is recommended.

Open `source/campaign-art.html?design=cover` in a browser. Set a 1080 × 1350 viewport and export full-page PNGs for the ten designs: `cover`, `homecoming`, `mercy`, `soul`, `rest`, `way`, `christ`, `aristotle`, `blake`, `end`. Use `design=cover&format=share` at 1200 × 630. Use `design=end&format=wide`, `square`, and `vertical` at 1920 × 1080, 1080 × 1080, and 1080 × 1920, saving `source/endcard-FORMAT.png`. Wait for local fonts and images before capture. `source/export-spec.json` lists each output.

Then run `python source/build_media.py`, `python source/build_print.py`, and `python source/build_email.py` from the kit. No model calls or new generation costs occur. Film intermediates stay in `source/.render/`, excluded from Git and the deliverable ZIP. Inside the repository, the film builder also refreshes website derivatives; a standalone kit rebuild makes the marketing films only.

Run `python source/verify_manifest.py` to check the supplied file hashes. Re-edits naturally invalidate the supplied manifest; make a new manifest for a revised release.

## Source review

`PROVENANCE.md` records the production and primary-source checks. Existing catalog PENDING/VERIFY entries remain for Jacob’s human source review. This campaign adds no product, price, fulfillment promise, human verification signature, sending action, or advertising charge beyond the authorized media generation.
