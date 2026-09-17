# Production and source record

Prepared 2026-09-15 for Jacob E. Thomas. Campaign: Words to Live With. Existing catalog work and its source-verification status are preserved.

## Texts

- **Homer:** The Odyssey, Book I, Samuel Butler translation. [Primary text](https://www.gutenberg.org/cache/epub/1727/pg1727-images.html). The campaign quotes the first sentence; the product includes a longer extract stopping at “safely home”, where the source sentence continues. We do not repeat the catalog’s unsupported “oldest opening lines” claim.
- **Matthew:** [King James Version](https://www.gutenberg.org/ebooks/10), Matthew 5:3–12 and 16:26. The exact campaign verse, Matthew 5:7, and both questions of 16:26 were compared with the downloadable Project Gutenberg text. The film introduces the quoted blessing as Jesus’s teaching in Matthew. Authorized Version/1611 names the translation; modern-spelling typography is not represented as a facsimile of a 1611 page.
- **Augustine:** [Confessions, Book I, Pusey translation](https://www.gutenberg.org/cache/epub/3296/pg3296-images.html). The quoted clause is extracted from the opening prayer; the surrounding sentence begins “Thou awakest us to delight in Thy praise; for”. The address to God remains intact.
- **Dante:** [Inferno, Canto I, lines 1–3, Longfellow translation](https://www.gutenberg.org/cache/epub/1001/pg1001-images.html). The campaign uses the exact three lines in `source/texts/midway-upon-the-journey.txt`, including capital “For”. Line wraps may occur within a verse at small sizes.

The texts and these translations are public domain in the United States. Exact excerpts come from the existing shop text files and catalog, checked against the editions above. No new quotation broadside or SKU is created. Human catalog verification remains with Jacob; automated/source preparation is not a substitute signature.

## Museum artworks

The campaign uses unchanged product JPGs from the repository, preserved in `source/products/`. These show the shop’s existing contemporary broadside compositions around the historical artwork.

| Work | Record and rights |
|---|---|
| Rembrandt, Christ Preaching (The Hundred Guilder Print), c. 1649 | [National Gallery of Art, object 9969](https://www.nga.gov/artworks/9969-christ-preaching-hundred-guilder-print). Record identifies the image as free and public domain. |
| Rembrandt, Aristotle with a Bust of Homer, 1653 | [The Metropolitan Museum of Art, object 437394](https://www.metmuseum.org/art/collection/search/437394). Public Domain / Open Access. |
| William Blake, The Circle of the Lustful: Paolo and Francesca, 1827 | [National Gallery of Art, object 797](https://www.nga.gov/artworks/797-circle-lustful-paolo-and-francesca). Public-domain open-access image. |

We did not animate, regenerate, retouch, or alter the sacred figures or historical paintings. Framing and scaling for a layout preserve each complete product design. No institutional sponsorship is implied.

## Generated stills and motion

Six original images were made with the built-in image generation tool: `room`, `sea`, `hill`, `soul`, `rest`, `wood`. Each PNG is 1672 × 941. Exact prompts and original generated filenames are in `source/generation-record.json`. Imagined landscapes and architecture are not asserted historical places; the reading room is a conceptual interior, not a photograph of the shop or a product installation.

The 2026-09-16 revision assigns a distinct visual to every reading chapter. Matthew 5:7 retains the olive hillside; Matthew 16:26 has an open stone threshold and dry path; Augustine has a secluded courtyard and cypress. Neither new image depicts a recorded Biblical event or Augustine's actual home. The corresponding scene stays consistent across its website chapter, film chapter, social card and reading-guide page. The opening room remains the campaign cover image, never another reading chapter's illustration.

Runway animated each still with camera and environmental motion. Requested model: Gen-4.5, no generated audio. Returned clips are 1280 × 720 at 24 fps, approximately 10.04 seconds each. The original four used a 1080p request; the two revision clips used the model's default. Original files are retained. Finished 1080-format marketing exports scale this footage; website delivery is 1280 × 720.

The customer-facing description is “A contemporary visual meditation.” Full machine-production details remain here for transparent review. No generated footage is passed off as a recording of a sacred event, historical event, or the actual Austin press.

## Narration and score

Narrator: **Miriam**, stock calm British feminine narrator, distinct from Benjamin in The First Impression. Model: eleven_multilingual_v2, speed 0.94. Eight segments; exact script and task IDs are in the generation record. This is a modern narration. Jesus is identified as the speaker of the quoted blessing, while the actual reading voice is Miriam; it is not a purported voice of Jesus. The soul segment is a modern introductory paraphrase, not a scripture quotation; both questions of Matthew 16:26 remain verbatim in the website, social card and reading guide.

Music: original generated instrumental piano/viola/cello score, Runway Lyria 3 Pro. Exact brief and task ID included. No existing hymn was requested. The full film spaces the scripture reading before the later collection invitation. The short promotional cuts omit the scripture-reading segment. There is no claim that buying a print supplies a spiritual benefit.

Runway credits: 1925 at the start, 1423 after generation (502 used: four video tasks at 120, seven speech tasks at 2, one score at 8). No new subscription or credit purchase was made.

Revision credits: 1423 before the correction, 1181 after (242 used: two motion clips at 120, one narration at 2). The existing score and other narration segments are retained.

## Editing

`source/build_media.py` records the timing, scales, text overlays, fades, narration delays and audio mix. The six source clips are unchanged. The full film is now 80 seconds, including its own Matthew 16:26 scene. Every narrative shot appears once per film; longer holds gently slow the source instead of looping it. The ambient website loop uses a short forward/reverse room movement and has no audio. Film captions are separate optional VTT tracks, default off; chapter titles remain part of the graphic design. Versioned website film and caption URLs prevent the old movie from being reused from a browser cache; redirects retain older direct links.

The print builder embeds the house fonts and supplies 0.125-inch bleed with trim boxes. PDF photographs use high-quality JPEG embedding; untouched PNG masters are in `artwork/`. The email builder creates unsent MIME drafts with an embedded image and no recipients. No mailing or posting occurred.

## Review memo

The existing eight catalog entries retain their PENDING/VERIFY human checks. In addition to the familiar wording comparisons, review the Odyssey extract’s stopping point, the modern-spelling Authorized Version label, Augustine’s clause in its prayer context, Dante’s line breaks, and the three institutional object IDs before a production print run. The campaign’s five-sheet set list is taken from the current catalog; the three art reproductions are not included in that set.
