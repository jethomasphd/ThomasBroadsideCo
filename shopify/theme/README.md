# The living press / Shopify migration copy

The original site is primary as of Jacob's September 15, 2026 instruction.
This is a **section package**, not a complete theme or a live Shopify change.

When the storefront moves:

1. Duplicate the destination theme. Copy `sections/tb-living-press.liquid` and
   everything in `assets/` into that theme's matching directories.
2. Upload `site/media/press/press-loop-wide.mp4`, `press-loop-portrait.mp4`, and
   `history-has-a-pulse-75s-v3.mp4` to Shopify Files.
3. In the theme editor add **Thomas / Living press** near the top of the home
   page. Pick the Declaration product and the three uploaded videos.
4. The bundled poster and fonts work immediately. Select an optional poster
   override only if needed. Keep the normal featured product/collection
   sections below the film so the catalog stays shoppable.
5. Preview desktop and mobile. Confirm muted looping, pause/resume, reduced
   motion, the film dialog, captions, Escape, and the product link. Test this
   against the chosen theme before publishing. The section has been checked
   locally for schema and syntax; no Shopify store session was available.

The custom element cleans up observers/listeners when the theme editor
unloads the section. Video files are picked through Shopify's native
[video settings](https://shopify.dev/docs/storefronts/themes/architecture/settings/input-settings)
and their [video sources](https://shopify.dev/docs/api/liquid/objects/video_source).
No app or third-party video player is required.
