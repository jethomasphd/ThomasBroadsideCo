# Production provenance

## Historical record

The page and print story draw on the Library of Congress and National Archives records below. Research is prepared for Jacob E. Thomas's editorial review; no human `source_verified_by` signature has been asserted. The primary story data is `data/campaigns/the-first-impression.json`, with a kit snapshot in `source/story.json`.

### The first printing, July 4–5, 1776

Library of Congress / National Archives: https://www.loc.gov/resource/gdcwdl.wdl_02716/

The surviving printed broadside and the dispatch of copies on July 5. Historical print-run and survivor counts are intentionally omitted.

### Jefferson's original Rough draught

Library of Congress, Jefferson Papers: https://www.loc.gov/exhibits/declara/declara4.html#obj3

Draft, alterations by Adams and Franklin, and congressional revisions. The approved text preceded the later engrossed parchment.

### Franklin, printer and writer

Library of Congress: https://www.loc.gov/exhibits/franklin/franklin-printer.html

Primary printed examples of Poor Richard's Almanack and Franklin's printing work.

### Washington's copy of the Declaration

Library of Congress, George Washington Papers: https://www.loc.gov/exhibits/declara/declara4.html#obj4

Hancock sent the printed Declaration to Washington on July 6; Washington had it read to the troops in New York on July 9.

### The Federalist in historic newspapers

Library of Congress: https://guides.loc.gov/federalist-essays-in-historic-newspapers

Essays by Hamilton, Madison and Jay under Publius, supporting ratification in 1787–1788; the guide indexes original newspaper printings.

### Printing the Declaration of Independence

Library of Congress, Rare Book and Special Collections: https://blogs.loc.gov/bibliomania/2023/07/04/printing-the-declaration-of-independence/

The approved wording was sent to Dunlap's shop; the first printing belongs to the evening of July 4 and early July 5.

### Declaring Independence: drafting the documents

Library of Congress: https://www.loc.gov/exhibits/declara/declara3.html

The vote for independence on July 2, adoption on July 4, and the later engrossed copy ordered July 19 and signed beginning August 2.

## Reconstruction policy

The five period stills were generated with built-in imagegen. Their exact prompts are in `source/image-prompts.json`. They depict recognizable historical figures in imagined scenes, not archival photographs. The Dunlap scene represents a printer at work; it does not claim an authenticated likeness of John Dunlap or a measured reconstruction of his particular shop. Rooms, incidental people, gestures, papers and actions are imagined. No legible generated manuscript is treated as a source text. No founder voice, quotation or endorsement is fabricated.

Runway animated those five starting images into five ten-second scenes. Motion is restrained: writing, reading, breathing, small hand movements and a slow camera move. The clips have been inspected at multiple points for facial, hand, page and mechanical consistency. They remain dramatizations, with no claim of exact historical action. Website ambient loops play a four-second selection forward and reverse to soften the reset; the history film uses forward motion.

Franklin is the printer and draft editor. Jefferson is the principal draftsman, with colleagues and Congress revising the text. Dunlap's shop prints the adopted Declaration on the night of July 4–5. Washington orders a reading; the image shows an officer reading beside him. Hamilton's chapter moves explicitly to the later 1787–1788 ratification debate and includes Madison and Jay. The campaign does not depict the five men as jointly operating the press or meeting for an undocumented event. It omits disputed exact print-run and surviving-copy counts.

Historical context matters: the Declaration's promise of equality coexisted with slavery and exclusion. The webpage's source notes acknowledge that context. The commercial theme is access to public words, not an endorsement of every founder's conduct or a modern political cause.

## The actual shop and product

`source/clips/austin.mp4` is the earlier campaign's graded, silent wide loop, selected from owner-supplied `IMG_7243.MOV`. The new film repeats that short loop across its twelve-second Austin passage. It shows the real working shop, without claiming it records a Declaration production run. Raw files remain with the owner.

`source/austin.jpg` is the earlier campaign's art-directed press still, originally based on a clean frame extracted from the same clip. Built-in imagegen refined its lighting, tone and clarity. It is an enhanced photograph of the shop, not a forensic record. The earlier `marketing/history-has-a-pulse/PROVENANCE.md` preserves that prompt and the original reference frame.

All five product JPGs are unchanged copies of the existing catalog renders. The Declaration is a contemporary composition of its celebrated passage, not a full-text Dunlap facsimile or an original artifact. Original portrait artwork and product source attribution remain on their canonical product pages. This campaign does not claim a historical figure endorsed the shop.

## Original-document reference images

- Dunlap broadside: https://www.loc.gov/exhibits/declara/images/dunlap.jpg
- Jefferson draft: https://www.loc.gov/exhibits/declara/images/draft1.jpg

These reproductions of public-domain historical documents were obtained from the Library of Congress exhibition. They are supplied for source study, with institutional links. The small print placements preserve their native resolution; no generated enlargement or invented text was substituted.

## Film sound

The narrator is the stock Benjamin voice, generated through Runway's speech tool using `eleven_multilingual_v2` at speed 0.94. It is a modern narrator, not an imitation of a founder's voice. The eight exact passages are in `source/video-prompts.json`, and each corresponding MP3 is in `audio/`.

The original generated chamber score uses the Runway music tool with Lyria 3 Pro. The full prompt and generation ID are in `source/generation-record.json`. It is a contemporary cinematic accompaniment, not historical performance or a recognizable anthem. The supplied full-length score is trimmed for each edit. Voice and score are normalized separately and mixed with limited peak level. No archival sound is claimed.

## Assets and edit

Four final films: 65-second landscape, two 30-second social edits, and a 15-second score-led vertical teaser. Timelines are recorded in `source/*-timeline.json`. The clean five video masters were transcoded to browser-friendly H.264/24 fps/1080p without adding captions. Web film is a smaller 720p encoding; the marketing master remains 1080p. Playback is native, sound requires a viewer action, ambient motion respects reduced-motion/data-saving preferences, and text tracks have no default attribute.

The graphic layouts use Caslon Display, Caslon Text and IBM Plex Mono, the shop's cream/ink/red palette, and local product assets. Editable HTML and PDF/media builders accompany the finished exports. Fonts are redistributed with their OFL notices in `source/fonts/`. The generated artwork and clips should retain this production record when reused. No third-party music, seals, false signatures or commercial endorsements were inserted.

## Runway account usage

Five historical clips, eight narration passages and one score were generated. The tools reported 2,250 credits before this work and 1,625 remaining after the final generation: 625 credits used. No plan change, credit purchase, or advertising spend was performed. The account owner can inspect the source tasks in Runway using the IDs in `source/generation-record.json`; temporary signed download URLs are deliberately excluded from the repo.

## Release

The website change is prepared on a review branch. Marketing files are ready to select and use after editorial review and site deployment. No mail, social post, paid placement or production-site merge is performed by the builders. Approved mailing address and email are the values supplied by Jacob in this task.
