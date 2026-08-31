# Feeding Flow — the Herald's briefing kit

How to use this file: open Flow (labs.google/flow), make a project named
**Thomas Broadside Co. — Meta Ads**, upload the ingredient images listed
in §3, then paste **Block 1** into the chat as your first message. When
it acknowledges, paste **Block 2** (the first media request). Iterate
scene by scene — Veo clips run ~8 seconds, so a 15-second ad is two
generated scenes plus a built end card, assembled in Flow's scenebuilder.

House rules that bind every ad before anything is generated: paid
creative sells **editions and sets only** (GROWTH.md — a $9 digital can
never afford acquisition); every visible quote is the real text with its
citation (the uploaded sheet renders already carry both); pre-partisan,
always; nothing in the ad may claim generated footage is our shop floor —
the real sheets ARE the product, so the honest move is to make them the
stars. Never let the model draw lettering: AI-rendered type mangles, and
our type is the product. All words on screen come from the uploaded
renders or from overlay text added in the editor.

Finished cuts and stills come back to the repo at **`ads/incoming/`** —
the clerks frame-check every candidate (type unwarped, colors true, safe
zones clear) before anything reaches Ads Manager, and Jacob signs the
final [D9].

---

## Block 1 — paste this first (project context)

```
PROJECT CONTEXT — THOMAS BROADSIDE CO.

You are helping produce advertising video for Thomas Broadside Co., a
real family print shop in Austin, Texas that prints museum-grade
broadsides of America's founding documents on its own press. This is not
a dropshipper or a poster store: the product is provenance. Every sheet
is typeset in Caslon (the typeface of the original 1776 Dunlap
broadside), printed in the two inks of the early press (black carries
the words, red carries the structure), on heavy cream stock, in Austin.
Editions are numbered of 250 on cotton paper with an embossed maker's
mark, inspected by hand.

BRAND VOICE: a small museum that happens to sell. Confident, warm,
plainspoken, zero hype. Think wall placards, not banner ads. We never
use exclamation points. We say true things slowly.

VISUAL SYSTEM (use these exactly):
- Paper cream: #FAF6EA (the sheet itself)
- Ink black:  #201A10
- Press red:  #9E3123 (kickers, rules, highlights — the second ink)
- Gallery wall: #F1ECE0 · Walnut frame: #241C12
- Type: Caslon serifs. All typography on screen must come from the
  product images I upload, or be added later as overlays — NEVER
  generate lettering, documents, signs, or labels in the video model.
- Light: warm, raking, archival — late-afternoon museum light, soft
  shadows, paper texture visible. Never neon, never cold blue, never
  glossy stock-footage look.

HARD RULES:
1. Never generate readable text, documents, or signage — the uploaded
   sheet images are the only typography allowed on screen.
2. Never depict a specific print shop presented as OUR shop, and no
   faces. Abstract macro craft imagery (ink on rollers, paper fibers,
   kraft tube, twine) is welcome as atmosphere.
3. Non-partisan, timeless, civic — no modern politics, no crowds, no
   flags waving over battle scenes. The mood is a quiet archive, not a
   rally.
4. Everything must compose center-safe so a 16:9 master crops cleanly
   to 4:5 and 1:1 (key action inside the middle 60% of frame).
5. Design for sound-off viewing; if audio is generated, it is quiet
   room tone, paper sounds, a single low piano note — never voiceover,
   never epic trailer music.

WHAT WE ADVERTISE: only the numbered editions ($145–175) and the sets
($85–150). The hero product is The Declaration of Independence numbered
edition, $175 — the uploaded render shows it: "We hold these truths"
set monumental with a red kicker reading IN CONGRESS, JULY 4, 1776.

AUDIENCE: US adults who buy history books, museum memberships, classical
and homeschool education materials, Texas history; gift buyers. They are
allergic to junk posters and they can tell real typesetting from fake.

Acknowledge this context and wait for my first media request.
```

## Block 2 — paste second (the first media request)

```
MEDIA REQUEST 001 — "TEN THOUSAND DECLARATIONS"
15-second Meta feed/Reels ad · master 16:9, center-safe for 4:5 crop ·
target the numbered Declaration edition, $175.

Build three scenes:

SCENE 1 (0:00–0:03) — THE HOOK, macro atmosphere.
Prompt: Extreme macro, shallow depth of field: a deep red line of ink
(#9E3123) freshly pressed into thick cream paper (#FAF6EA), fibers and
letterpress impression visible, warm raking light sweeping across the
surface, slow camera drift. Photographic, tactile, archival mood. No
readable letters, no words, no logos, no hands, no faces.

SCENE 2 (0:03–0:10) — THE SHEET, from the uploaded ingredient.
Use the uploaded image "declaration-of-independence.jpg" exactly as-is —
it is finished artwork and must not be redrawn, warped, retyped, or
recolored. Prompt: Begin close on the red kicker line at the top of the
provided sheet, then a slow, steady pull back and tilt down revealing
the monumental words and the whole broadside lying flat on a dark walnut
surface (#241C12), warm museum light raking across the cream paper, the
paper's texture catching the light, dust motes. Camera movement only —
the artwork itself must remain pixel-faithful and legible throughout.

SCENE 3 (0:10–0:15) — THE END CARD, built not generated.
A still frame of plain cream (#FAF6EA) with a fine double rule border.
I will add overlay text in the editor. Generate only the background:
Prompt: Static full-frame of warm cream paper texture (#FAF6EA), subtle
grain, a thin dark double-rule border inset from the edges, soft even
archival light, nothing else. No text, no marks.

OVERLAY TEXT PLAN (added in scenebuilder/editor, not generated —
IBM Plex Mono style for small lines, Caslon style for large):
- Scene 1: "There are ten thousand Declarations on the internet."
- Scene 2, beat 1: "This one comes off a real press."
- Scene 2, beat 2: "Numbered of 250 · every word from the National
  Archives"
- Scene 3 end card, stacked:
      ★ THOMAS BROADSIDE CO.
      Founding documents, printed here.
      The Declaration · numbered edition · $175
      thomasbroadside.co

Pace: unhurried but tight; hard cut between scenes; total exactly 15s.
Audio: room tone and paper sounds only, very quiet — the ad must work
silent. Deliver the 16:9 master, then a 4:5 crop if the tool supports
it.
```

---

## 3. Ingredients to upload to Flow (from this repo)

| File | Why |
|---|---|
| `site/art/declaration-of-independence.jpg` | The hero — the real sheet, 1950×2600. Scene 2's ingredient |
| `site/art/preamble-to-the-constitution.jpg` | For variant/set requests later |
| `site/art/abraham-lincoln-after-healy.jpg` | For a Lincoln-wall variant later |

Upload the full renders, never the `-card` files. If Flow's ingredient
mode warps or redraws the sheet in motion (check every frame — the type
must stay crisp and true), fall back to animating the still directly:
a slow push/pan on the image with light effects only.

## 4. What comes back, and the checks before it ships

Deposit every candidate cut and still at **`ads/incoming/`** in the
repo (mp4/mov/png as Flow exports them). The clerks then run the bench
on each: frame-by-frame type fidelity against the real render, palette
against the hexes, safe-zone crop test at 4:5 and 1:1, the 15.0s
duration, and a silent-viewing pass. Nothing goes to Ads Manager until
Jacob signs the cut [D9].

Meta mechanics when it ships (GROWTH.md governs):
- Destination: `https://thomasbroadside.co/documents/declaration-of-independence.html?utm_source=fb-paid`
  — the bell counts `utm-fb-paid`; ROAS is graded from our own ledger
  against the 2.0 kill-line. No pixel, ever [D2].
- $500 test budget per campaign; editions/sets only; paid stays under
  the 20% pre-gate cap [D11].
- Expect Meta may flag civic-adjacent content as a "social issues" ad —
  keep copy commerce-framed (a product, a price, a press); if flagged,
  complete advertiser authorization rather than rewording the founding
  documents.
- Meta requires disclosure when ads contain photoreal AI-generated
  imagery. Scene 1's macro atmosphere may qualify: tick the disclosure
  in Ads Manager honestly. That is a platform compliance field, not our
  storefront [D1 stands]; Jacob decides at publish [D9]. If the label
  ever feels wrong for the brand, drop Scene 1 for a second real-sheet
  move — the product needs no fiction.

## 5. Next requests in the queue (after 001 ships)

- **002 "Six Documents, One Wall"** — the classroom set ($150), the
  shelf of sheets assembling; September back-to-school angle.
- **003 "The Texas Sheet"** — the Texas Declaration edition for the
  home market; "printed an hour from where it was declared."
- **004 "With Malice Toward None"** — the Lincoln wall (portrait +
  quote pair) for the gift angle, once Jacob clears the Lincoln
  verifications on the Registrar's list.
