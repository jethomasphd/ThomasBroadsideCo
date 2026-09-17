# Current film edition

The active film is now the 75-second **director’s cut**, with real shop footage, historical reconstructions, Canon landscapes, Elias’s narration and an original score. See [its production record](directors-cut/PROVENANCE.md) for the current edit, source selection and audio. The notes below preserve the original edition’s provenance; its 24/15-second films have been retired. Its static artwork, print assets and web loops remain in use.

# Production provenance / Original September 15 edition

## Source selection

The four MOV files and the JPEG supplied by Jacob on September 15, 2026 were inspected. Raw media remains with the owner; the repo carries selected exports and a reference frame. No source GPS/location metadata is retained in the exports.

| Source | Running time | Orientation | Editorial decision |
|---|---:|---|---|
| IMG_7243.MOV | 5.97 sec | landscape | Primary wide shot: Heidelberg identity, paper feed, restrained camera movement. Wide web loop and the opening of the film. |
| IMG_7249.MOV | 7.51 sec | portrait | Best close view of delivery motion. Portrait loop and social film opening. |
| IMG_7241.MOV | 11.27 sec | portrait | Select 6.3-10.3 sec for finishing equipment. The earlier moving survey is omitted from the finished film. |
| IMG_7248.MOV | 7.21 sec | portrait | Reviewed alternate. More ceiling and similar delivery action; 7249 is the stronger select. |
| IMG_7244.jpeg | still / 5712 x 4284 | landscape | Reviewed. Its multi-picture encoding produced decoding seams in available processing paths. A clean 1920 x 1080 frame at 2 sec from 7243 supplied the final enhancement instead. |

The footage shows the owner's working shop, not a documented production run of the Declaration. Existing printed sheets in the finishing footage are not labeled as Thomas Broadside products. The final Declaration image is the existing catalog render, unchanged.

## Enhancement

Built-in imagegen was used to relight and refine the extracted press frame. The final result is `artwork/press-portrait-enhanced.png`. `source/press-reference.jpg` preserves the clean input frame. This is art-directed campaign imagery, not a forensic photograph. It is used as the poster, campaign still, and a five-second insert in the wide film. The first generated variant changed machine geometry and was rejected; it is not in the kit.

Actual press motion is from the original MOV files. FFmpeg applies restrained color grading, light sharpening, reframing, typography, and audio conditioning. No motion is generated, no customer artwork is replaced, and no fictional press, operator, signature, edition number, or finished product is invented. The original stereo AAC stream is selected explicitly; unsupported auxiliary iPhone spatial audio is excluded.

### Final prompt / built-in imagegen

> Edit this photograph by changing ONLY lighting, tonal grade and subtle photographic clarity. Preserve the whole image composition, exact machine geometry, all mechanical parts, location and viewpoint with very high fidelity. Existing HEIDELBERG Speedmaster lettering must remain exactly unchanged. Warm raking light as in a fine industrial editorial portrait, rich charcoal shadows, muted warm cream paper, subtle bronze midtones, restrained saturation. A beautiful real working press for the Thomas Broadside Co. campaign. NO collage, NO changed angle, NO invented machine parts, NO new objects, NO extra text, NO removed parts, NO altered paper, no fog. Output landscape 16:9, 1920x1080 or larger. This source frame is the sole edit target. Make it look like an extraordinary photographic print of precisely this machine.

## Film edit decisions

- Wide film: 7243 at 0.3-5.3 sec; 7249 at 0.5-5.5 sec; 7241 at 6.3-10.3 sec; enhanced press portrait for 5 sec; Declaration end card for 5 sec. Approx. 24 sec.
- Vertical film: 7249 at 0.5-4.5 sec; 7241 at 6.3-9.3 sec; 7243 at 0.8-3.8 sec; Declaration end card for 5 sec. Approx. 15 sec.
- Square film: 7243 at 0.4-4.4 sec; 7249 at 0.5-3.5 sec; 7241 at 6.3-9.3 sec; Declaration end card for 5 sec. Approx. 15 sec.
- Web loops: 7243 at 0.2-5.7 sec and 7249 at 0.2-6.7 sec. Real-time, looping cuts; no claim of a seamless continuous take.
- Sound: original shop audio, high-pass filtering and loudness conditioning with short fades; no added music or voiceover. End cards are silent.

## Rebuild

From a checkout of the repo, install the optional **design-bench** dependencies in `source/requirements-design.txt`. These are not storefront or factory-data runtime dependencies.

```sh
python marketing/history-has-a-pulse/source/build_print.py
python marketing/history-has-a-pulse/source/build_email.py
python marketing/history-has-a-pulse/source/build_media.py
python tools/selfcheck.py
node tools/test_living_press.cjs
```

The media builder now delegates to `directors-cut/source/build_film.py`, which consumes the included footage, sound and current closing cards. The original silent film end cards have been retired. The social editor and visual library include local copies of their fonts and the unchanged Declaration artwork, so both open directly from the downloaded kit. Python builders run from a repository checkout to preserve their connection to the canonical catalog and storefront assets.

Social format queries: `?mode=pulse&format=portrait` (1080 x 1350); `format=vertical` (1080 x 1920); `format=square` (1080 x 1080); `format=landscape` (1200 x 627). Change `mode=product` for the Declaration composition. Add `export=1` to fix the artboard at the corresponding dimensions, then capture its exact rectangle from a full-page browser render. Current film closing cards have their own editable source in `directors-cut/source/endcard.html`.

## Sources and ownership

Catalog facts and product art: `data/catalog/catalog.json`, `shop.config.json`, `site/art/` and the existing verified source lines on the Declaration, Preamble, and Bill of Rights. Typefaces are the repo's existing Libre Caslon and IBM Plex Mono assets. Press footage is owner-supplied. Contact address/email and deferral of Shopify were approved by Jacob in this task. The exact asset checksums and sizes are in `manifest.json`.


Font license notices accompany the redistributed typefaces in `source/fonts/`.
