# Production record / The director’s cut

Produced September 17, 2026. This edition replaces the original generic shop film with one coherent 75-second narrative. Source of truth: `data/campaigns/history-has-a-pulse.json` in the repository; portable snapshot: `source/edit.json`. The script and human-readable picture ledger are in `SCRIPT.md`.

## Editorial frame

The press makes words public. The words become part of a life. The edit moves between the actual Austin shop, the first printed Declaration, the act of drafting and public reading, and the enduring texts of the Western Canon. It ends with three existing catalog designs. These designs, their words, prices and source-verification status were not altered.

## The real shop / 25.5 seconds

All four supplied MOV files are represented. `source/shop-selects.json` records original SHA-256 hashes and exact source intervals. The selected source clips retain their original stereo shop audio. FFmpeg applies reframing, restrained warm color grading, sharpening, 24fps delivery and audio conditioning. It does not synthesize, replace or invent any machinery or activity in the owner’s footage. The two selections from IMG_7241 use different, nonoverlapping intervals. There is no repeated source interval in the final edit. Original phone metadata is stripped from exports.

The working shop footage does not document a production run of the particular broadsides shown on the end card. Other printed sheets visible in finishing equipment are not labeled as Thomas Broadside products.

## History / contemporary reconstructions

Dunlap, Jefferson and Washington come from the distinct-scene edition of The First Impression campaign. They are photorealistic AI-assisted interpretations, not archival records. The Washington scene shows him beside an officer reading a sheet, not claiming that he personally read the Declaration aloud. The narration assigns no invented quotation to any figure.

The new inked-type shot is an imagined close view of an eighteenth-century printer’s bench. Built-in imagegen used the existing Dunlap artwork as a period and color reference, with a new composition. Runway gen4.5 supplied a slow moving shot. Its exact image and motion prompts, task ID, and chosen source interval are preserved in `source/generation-record.json` and `source/edit.json`. It contains no purported transcription of the Declaration.

`source/the-first-impression-generation-record.json`, image/video prompt files and provenance copy preserve the inherited record. They describe the wider original campaign; only the Dunlap, Jefferson and Washington clips listed in this edit are used here. Source references are preserved in `source/historical-sources.json`.

## Canon / respectful visual meditations

The sea evokes Homer’s Odyssey; the olive hillside accompanies the Beatitudes; the woodland path evokes Dante’s Inferno; the reading room supplies the closing invitation. These are distinct selected scenes from Words to Live With. They are contemporary visual meditations, not asserted historical or biblical locations. No sacred figure is portrayed. The narration says “the search for wisdom,” “the call to mercy,” and “the courage to find our way”; these are campaign prose, not presented as quotations from scripture or literature.

The inherited Canon generation record and provenance are included with `words-to-live-with-` prefixes. Only sea, hill, wood and room are used in this cut.

## Voice, score and actual machinery

Elias is Runway’s older male preset voice, delivered calmly and deliberately through `eleven_multilingual_v2` at speed 0.85. It does not impersonate a historical figure. Sixteen separately generated cues retain their natural generated timing; the edit adds explicit gaps between the opening and closing phrases rather than relying on punctuation alone. The exact text, task IDs, files and timings are preserved in the generation record and edit.

After “just listen,” 4.05 seconds of real machinery play without narration or music (4.947–9.000 seconds). The original AI-generated chamber score enters at 9 seconds. It is an original contemporary composition, not period music. Its first 67 seconds join its final nine seconds with a one-second crossfade. Voice-driven compression lowers accompaniment during speech. The original 147-credit production and prompts remain recorded; the narration revision used sixteen new speech tasks without a subscription change or top-up.

Three restrained cover overlays identify *The Odyssey* (Samuel Butler, 1900), the Gospel according to Matthew (Authorized Version, 1611), and Dante’s *Inferno* (Henry Wadsworth Longfellow, 1867), matching the catalog’s source editions. These are newly typeset campaign reference covers, not photographs of historical bindings, facsimiles, or additional products for sale. Their editable HTML, local fonts and three PNG exports are included. They fade gently into the corresponding sea, hillside and woodland scenes and out before the following shot.

## Formats and accessibility

Landscape: 1920×1080. Portrait: 1080×1920, with individually framed square moving images inside the editorial layout. Square: 1080×1080. All are H.264/AAC, 24fps, exactly 75 seconds, with fast-start metadata. The web film is a smaller 1280×720 encode. No captions are burned into the image; the small curatorial labels identify the scene and its nature. VTT and SRT files are optional; supplied players default to off.

The portrait and square framing is deliberate, not an automated center crop of the finished landscape film. Product artwork is copied unchanged from the catalog. Local Libre Caslon and IBM Plex Mono fonts and their licenses are included. The closing composition remains editable HTML; committed full-size PNGs support reproducible rendering.

## Verification and rebuild

`source/timeline-wide.json`, `timeline-vertical.json` and `timeline-square.json` preserve rendered order and source hashes. `manifest.json` inventories distributable files. The repository regression check validates a single 75-second edit, the 25.5-second shop total, unique scenes and nonoverlapping original intervals, cross-format consistency, source hashes, website targets and captions off. Picture review uses scene contact sheets in all formats; the media check fully decodes all deliverables and measures the mix. See `source/qa.json` for measured results.

Rebuild instructions are in `README.md`. Re-rendering uses the included files and makes no new AI calls. This package contains no credentials or expiring service URLs. The parent kit’s print pieces and static artwork remain compatible; its active film library and email links now use this director’s cut.
