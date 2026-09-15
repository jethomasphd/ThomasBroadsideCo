# Release checks

Prepared 2026-09-15. See `source/validation.json` for measured media, print and email results.

- Repository selfcheck: GREEN, with the same 16 existing human-verification warnings. No catalog values changed.
- Shared living-media behavioral checks pass: lazy film loading, responsive source choice, manual pause, offscreen/background pause, reduced motion, data saving, blocked autoplay, fallback and modal focus.
- Browser review at 1440 × 1000 and 390 × 844: no horizontal document overflow. Reading layout and gallery inspected; product images resolve. The homepage Canon link and Room IV feature lead to the campaign.
- Actual native browser playback verified: duration 70.016 seconds, readyState 4, playback advanced; English captions disabled initially. Escape closes, pauses the film, and returns focus to the play button.
- Four original generated clips sampled at 0.2, 3, 6 and 9 seconds. Finished films sampled at chapter interiors and end cards. All MP4s decode through FFmpeg without errors.
- Narration durations fit their segments with a half-second lead and room at the end. Main film 70 seconds; social films 30/30/15. Stock narrator is Miriam.
- All 11 social PNG dimensions and three end-card dimensions verified. Source attribution and scripture text visible in the compositions.
- All 15 PDF pages rendered and visually inspected. TrimBox/BleedBox difference confirms 0.125-inch bleed. QR codes in all three PDFs decoded to their channel-specific campaign URLs.
- All three EMLs parsed as unsent, no recipients, with plain text, HTML, embedded JPEG and unsubscribe address. HTML and local preview variants included. Final sending requires the ordinary mail-platform send test.
- Matthew 5:7 and 16:26 matched against the Project Gutenberg KJV text. Homer, Augustine and Dante compared with the primary-text editions; all three museum records reviewed. Human catalog signatures remain pending.

## Delivery limits

Generated motion sources are 1280 × 720, scaled for 1080-format marketing delivery. Main website film is about 15.3 MB and loads only on request. Ambient loops are about 1.08 MB landscape and 0.50 MB portrait, muted, with reduced-motion and data-saving support. No web asset exceeds Cloudflare’s 25 MiB per-file limit. No tracking pixel or new external player is added.

The marketing kit contains source masters; it is intentionally larger than the website delivery folder. It is excluded from the deployed `site/` tree. Original Shopify migration remains deferred.
