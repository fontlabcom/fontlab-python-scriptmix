---
this_file: src_docs/md/scripts/contours/sandblast.md
tags: ["Contours"]
categories: ["Contours"]
---

# Sandblast

Add small irregular counters inside closed outlines.

What: Add small irregular counters inside closed outlines. How: Use a reproducible seed
and bounded placement attempts. Keep each hole wholly inside the combined filled shape,
outside existing counters, and separate from other holes. Cache placements per scan and
control setting. Orient each hole opposite its innermost containing contour. Why: Create
a distressed outline without a rejection loop that can hang. Use: Set hole count, radius
and seed. Inspect the placed count, then Apply. Benefit: Creates editable counters; the
preview reports the count actually placed.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Sandblast.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.

Run **Contours > Sandblast** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5eb830bdacbff9445bd3b0cc83805fb705afe505d35cb649ce38c1fa00540adb`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Contours/Sandblast.py)
