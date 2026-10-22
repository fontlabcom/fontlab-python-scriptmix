---
this_file: src_docs/md/scripts/anchors/place-from-bounds.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Place From Bounds

Add or move top and bottom anchors from the outline bounds.

What: Puts top, bottom, _top and _bottom anchors on the ink box of each layer.
Each anchor sits at the horizontal centre of the box, on the chosen edge,
plus an offset. The offset pushes the anchor away from the glyph.

How: top follows the upper edge; bottom follows the lower edge; _top follows
the lower edge; _bottom follows the upper edge. A missing anchor is
added with its name-derived appearance. An existing anchor moves and
keeps its style. Empty layers are left alone. The centre rounds half up.

Why: This gives a quick first anchor set for a new font. Refine it later by hand.

Use: Select glyphs. Run the script. Tick the anchors. Set offsets. Check the
table. Press Place.

Benefit: Many glyphs get consistent starter anchors in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
The edit is recorded as one Undo step. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_place_from_bounds.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Place From Bounds** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6f8ab4ddf8311c401a86e8bb8566d27b8e665fd1b96fbeee08b994ef17202f5c.py)
<!--/codeinclude-->
