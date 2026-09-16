# The First Impression

**Distinct-scene edition · September 16, 2026.** Every chapter has its own scene. Matching website, film and promotional materials remain consistent. The introduction now has a dedicated paper-and-type study; the Austin passage uses two unrepeated shots. All four films, the website hero and poster, social cover/share artwork, three email sets and three print PDFs are updated.


**Before it was a relic, it was news.**

A complete heritage campaign for Thomas Broadside Co. Open **index.html** for the visual library. The website entry is **Origin Story**, linked from the main navigation and the homepage feature.

## Start here

1. Review the branch preview and the 65-second film. The new website and campaign asset URLs become public on the main domain after the website change is merged and deployed.
2. Choose a channel below, then copy its finished text from **CAMPAIGN.md** and its tracked destination from **links.json**.
3. Upload the finished media and publish through your own account. Nothing in this kit has been sent, scheduled, or placed as a paid advertisement.

| Use | Finished file | Format |
|---|---|---|
| Website / YouTube / LinkedIn film | films/the-first-impression-65s.mp4 | 1920 × 1080, 65 seconds, narrated |
| Reels / Stories | films/the-printers-night-30s-vertical.mp4 | 1080 × 1920, 30 seconds, narrated |
| Square feed video | films/the-printers-night-30s-square.mp4 | 1080 × 1080, 30 seconds, narrated |
| Short teaser | films/the-first-impression-15s-teaser.mp4 | 1080 × 1920, 15 seconds, score and titles |
| Eight-card story carousel | social/01-cover.png through 08-closing.png | 1080 × 1350; upload in numerical order |
| LinkedIn / link share | social/09-linkedin-share.png | 1200 × 630 |
| Collector / education handout | print/the-first-impression-field-guide.pdf | 12 pages; 6 × 9 inch trim |
| Direct mail | print/the-first-impression-postcard-6x9.pdf | Front/back; 9 × 6 inch trim |
| Institutional introduction | print/the-first-impression-partner-sheet.pdf | 8.5 × 11 inch trim |
| Email | email/origin-story, july-fourth, partner-introduction | Each includes HTML, plain text, local preview and unsent EML |

The three narrated films include optional **.vtt** caption files. Captions are off by default on the website and visual library. Narrative chapter titles are part of the film artwork. The teaser has no spoken narration.

## Launch sequence

**Day 1:** Lead with the 65-second film on LinkedIn and the 30-second vertical film on Meta. Link to the origin story. Send the evergreen origin-story letter to the shop's opted-in list.

**Day 3:** Publish the complete eight-card carousel. The final card invites the collection visit.

**Days 5–12:** Use the Franklin, Jefferson, Dunlap, Washington and Hamilton cards individually, alternating a historical story with the actual Austin shop.

**Day 14:** Publish the 15-second teaser and the collection invitation. Use the partner sheet and field guide for relevant library, classroom and museum-shop conversations.

The July 4 email is yearless anniversary copy. Use it for a future Independence Day; it is not scheduled and does not imply July 2026 is still ahead. Keep the evergreen campaign available year-round.

## Email handoff

Open an **.eml** as an unsent draft, add the intended recipient and review in your mail client. It includes an embedded hero image, text alternative, approved From/Reply-To address, physical footer and an unsubscribe-by-email link. For a mailing platform, import the **.html**, retain the text alternative, and map its native unsubscribe field. Honor replies to the listed unsubscribe address. Gmail/Outlook rendering and your platform's final send preview should be checked in the sending account. This kit does not configure a mailing list, authenticate a domain, or claim inbox placement.

Approved contact: **9501 N Interstate Hwy 35, Austin, TX 78753 · JEThomasPhD@gmail.com**.

## Print handoff

All three PDFs have embedded type, vector QR codes, TrimBox and BleedBox, and 0.125 inch bleed on all sides. The field guide is in reader order, one page per PDF page; ask the printer to impose it for the chosen binding. The postcard is front followed by back. The right side of the back is intentionally open for recipient addressing, postage and the mail house's barcode treatment.

These are finished **RGB design masters**. Thomas Graphics should apply the actual press/paper ICC conversion, proof the warm cream/red, and confirm stock, finishing and postal layout for the chosen service. No arbitrary CMYK conversion or postal indicia has been invented. Do not enlarge the small original-document reproductions without obtaining a larger institutional source image. The original imagery is a reference, not the product sold.

## Historical and production record

**PROVENANCE.md** records sources, reconstruction choices, original media and generation IDs. Exact image and video prompts, narration, score prompt, timelines, fonts and clean clips are in **source/**. The verified source record remains accessible on the page. Historical research is prepared for Jacob's editorial review; no human source-verification signature has been supplied or fabricated.

The Declaration product is the existing contemporary composition of its celebrated passage. The campaign does not describe it as Dunlap's full-text facsimile or an original artifact. Prices, edition quantities, stock claims and catalog attribution have not been invented for this campaign.

## Edit and rebuild

Use a repository checkout and install the optional design-bench dependencies from **source/requirements-design.txt**. The storefront build remains Python standard library only.

```sh
python tools/build_site.py
python marketing/the-first-impression/source/build_media.py
python marketing/the-first-impression/source/build_print.py
python marketing/the-first-impression/source/build_email.py
python tools/selfcheck.py
python marketing/the-first-impression/source/refresh_manifest.py
python tools/test_origin_story.py
node tools/test_living_press.cjs
```

The historical story is authored in `data/campaigns/the-first-impression.json`. After editing it, refresh the snapshot `source/story.json` before rebuilding print. The film script is in `source/video-prompts.json`; changing that script requires matching new speech recordings, not simply changing captions.

Editable graphics: **source/campaign-art.html?design=cover**. Other designs: franklin, jefferson, dunlap, washington, hamilton, austin, closing. Default portrait is 1080 × 1350; `format=wide` is 1200 × 630, `format=filmwide` is 1920 × 1080, `format=vertical` is 1080 × 1920, `format=square` is 1080 × 1080. Film end cards use design=closing. Export the full page at the exact dimensions after local fonts and images load. The source HTML is the editable composition; generated scenes are preserved separately.

Scene assignments are documented in **source/scene-assignments.json**. The opening image belongs to covers and introductions; it must not be substituted for a founder’s chapter. The film builder rejects duplicate clip content, duplicate chapters and clips shorter than their allotted screen time. Optional **source/build_austin.py PATH_TO_ORIGINAL_MOV_DIRECTORY** rebuilds the included Austin edit; the normal film build needs no raw MOV files.

The media builder consumes the included clips and speech files and re-renders the edit on each run. It does not call Runway or spend credits. Its temporary files live under the repo's ignored work/ directory. Asset checksums and technical metadata are in **manifest.json**; run **source/refresh_manifest.py** after editing any packaged files. Email drafts embed **source/email-header.jpg**, so rebuilding them also works from the standalone kit.
