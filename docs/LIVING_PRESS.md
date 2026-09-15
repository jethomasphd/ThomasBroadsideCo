# The living press / September 2026

## Current storefront

Jacob confirmed on September 15 that the original website is live and that
Shopify will wait until the visual work is ready. The current implementation
therefore lives in `site/`. `shopify/theme/` is a migration copy, not a live
theme installation. The canonical catalog and its verified sources remain in
`data/`; nothing in this change modifies prices or fulfillment.

## What changed

- The home page opens with **History has a pulse**, real muted press footage,
  a direct Declaration link, and an optional 24-second shop film.
- The flagship Declaration keeps its own product feature directly below the
  opening. The pre-collection introduction is shorter. The old placeholder
  promising press photography is replaced by the actual press story.
- The Press page includes the enhanced still and the film. Its existing
  family, house rules, and honest sentence remain in the page.
- Every product page links back to the shop film through the product template.
- Portrait/Maps/Texas navigation now uses the actual `#maps-texas` anchor.
- Share metadata carries the campaign image. New CSS/JS join the existing
  content-based asset stamp so markup and behavior deploy together.
- `marketing/history-has-a-pulse/` holds the complete campaign, source builders,
  contact details approved in session, and production provenance.

## Playback and access

The decorative video has no audio stream. The wide loop is 1280 x 720; phone
viewports select a 720 x 1280 delivery shot. It loads only when visible and
when the visitor has not requested reduced motion or data saving. A visible
pause/play button gives direct control. Manual pause survives scrolling. A
failed or blocked video leaves the poster and readable page intact.

The shop film is loaded after a click, uses the browser's controls, and has
English captions. Opening it pauses the background. Escape/Close pauses the
film and returns focus to the trigger. No third-party player, new tracker,
framework, or runtime package is added to the storefront.

## Local review

```sh
python tools/selfcheck.py
node tools/test_living_press.cjs
python -m http.server 8766 --directory site
```

Open `http://localhost:8766`. The static preview does not emulate the existing
Cloudflare cart/API. For the kit, open its `index.html` directly, or serve the
repository root and visit `/marketing/history-has-a-pulse/`.

## Validation recorded for this change

- The existing selfcheck is green, with its 16 pre-existing PENDING source
  warnings preserved for the Registrar.
- Media-control behavioral checks cover lazy film loading, source choice,
  manual pause, visibility, reduced motion, data saving, denied autoplay,
  poster fallback, and dialog focus return.
- Browser review covers desktop and phone layout, no horizontal overflow,
  live playback, native controls/caption track, and Escape dismissal.
- Every finished PDF page is rendered and visually inspected. Both printed
  QR codes decode to the intended campaign URLs. Fonts and trim/bleed boxes
  are checked. The PDFs still need the pressroom's color conversion and proof.
- All films decode through FFmpeg; dimensions, duration, audio streams and
  web file weights are checked. Exported media strips source GPS metadata.
- Shopify section schema and JavaScript syntax are checked locally. The
  migration section has not been tested inside a live Shopify theme.

## Release and rollback

This work is prepared on `codex/living-press-campaign` for review. The existing
Cloudflare instructions name `main` as the production branch. Merge only when
the visual review is complete; verify the resulting Pages deployment and the
real product/contact flow. Sending email or starting ads is a separate action;
the campaign files do not send, schedule, or buy anything.

To roll back, revert the campaign commit through Git and let the normal Pages
deployment run. The previous site and product templates remain in history;
the catalog, checkout worker, order data and customer records were not changed.
