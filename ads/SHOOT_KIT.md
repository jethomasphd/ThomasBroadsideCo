# The Shoot Kit — real footage from the real floor

**Decision, Jacob, 2026-08-31: AI-generated video is dead.** The results
weren't worth the paper. Everything on camera comes from the shop —
which was always the honest version anyway; the whole store rests on
"printed here." This file replaces the Flow briefing kit and is the
working plan for shooting with a phone on the floor.

The distribution mechanics survive the kill unchanged (GROWTH.md still
governs): paid creative sells editions and sets only, links carry
`?utm_source=fb-paid`, ROAS is graded on our own ledger against the 2.0
kill-line, no pixel ever [D2].

---

## How to shoot (ten minutes of rules, then just press record)

- **Lock the phone.** Tripod, or brace it on a ream of stock. No
  handheld drift, no walking shots. A locked-off shot looks intentional;
  a wobbling one looks like a phone.
- **4K, 30 fps.** Bump to 60 fps only for shots you might slow down
  (paper falling onto the stack, the press cycling).
- **Shoot every setup twice: horizontal and vertical.** Horizontal
  (16:9) feeds the website; vertical (9:16) feeds Reels/feed ads later.
- **Ten seconds minimum per take**, camera rolling before and after the
  action. Short clips are uncuttable.
- **Light:** kill the overhead fluorescents where you can and use
  window light or one warm work lamp raking low across the paper — the
  texture of the stock is the product; flat light erases it.
- **Wipe the lens.** Shop dust is real.
- **Audio:** don't talk over takes. Separately, record 30 seconds of
  the press just running — that room sound becomes the bed under
  everything.

## The shot list (an afternoon, in this order)

**The press**
1. Wide: the press running, sheets moving through. The money shot.
2. Close: ink rollers turning.
3. Close: a printed sheet coming off / being lifted off the delivery.
4. The pile of finished broadsides growing on the stack.

**The craft (David)**
5. Macro: the embossing seal pressing the maker's mark into cotton
   paper, then raking light across the finished emboss.
6. Close on hands numbering an edition sheet — pencil, "12 / 250."
7. David's inspection: sheet lifted to the light, the nod or the
   set-aside. (Hands and profile are fine; nobody has to act.)

**The object**
8. The Declaration sheet flat on the walnut bench, camera slowly
   pushed closer on the red kicker (slide the phone on a rag if no
   slider — slow and steady).
9. Rolling a print around the core; kraft wrap; twine; cap in the tube.
10. The tube standing by the door with the label on straight (Ben's
    department).

**The place**
11. The building: sign, door, the floor from the doorway — five seconds
    each, morning light.
12. One wall with a framed sheet hung square.

## What the footage becomes

- **Homepage film:** one 8–12 second locked-off cut (shot 1, 3, or 8),
  muted, looping behind or beside the hero. Web spec: H.264 MP4,
  1080p, aim under ~6 MB, `muted loop playsinline`, poster frame = the
  Declaration render already on the page. The clerks wire it when the
  file lands.
- **The 15-second Meta cut:** hook (press cycling, 0–3s) → the real
  sheet coming off the press (3–8s) → number + emboss (8–12s) → end
  card (13–15s: ★ THOMAS BROADSIDE CO. · Founding documents, printed
  here. · thomasbroadside.co · edition price). Text goes on as
  overlays in the edit, never expected from the footage.
- **The Press page:** stills pulled from the same takes replace nothing
  yet, but give the Journal its photographs.

## Where it goes

Drop raw takes and cuts at **`ads/incoming/`** in the repo. The clerks
frame-check, compress for web, and stage; Jacob signs anything that
ships [D9]. Raw takes too big for the repo can wait on a drive — bring
the selects.
