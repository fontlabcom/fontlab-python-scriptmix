---
this_file: src_docs/md/scripts/contours/transform.md
tags: ["Contours"]
categories: ["Contours"]
---

# Transform

Scale, skew, rotate and move the outlines of the selected glyphs, with a
preview.

What: Set scale (x and y, in %), skew and rotation (in degrees) and a move
(in units), and pick the origin. The preview paints the first selected glyph
of the current master before (faint) and after (accent). The table lists
each glyph and master with its node count and origin. Transform applies it.

How: The script builds one affine matrix: move the origin to 0, 0; scale;
skew; rotate; move back; then move by the offset. The origin is computed per
layer: bounding box centre or bottom-left, the glyph origin, or the advance
centre on the baseline. Each shape gets the matrix the way FontLab's own
layer transform does: a plain own outline gets new node positions (FontLab
may round them); a component, a shared outline or a scaled shape keeps its
nodes and gets the composed transform. Anchors follow when you tick "Move
anchors too". The advance width and the guides stay.

Why: One panel does what otherwise takes several steps, for many glyphs and
masters at once, and shows the result first. For a slant about the x-height
with the font's italic angle, use Contours > Slant.

Use: Select glyphs. Run the script. Set the values, the origin and the
masters. Press Transform. Press Reload selection after you change the
selection.

Benefit: Exact, repeatable transforms over many glyphs and masters in one
Undo step.

Safety: These cases block or limit the edit:

- an anchor that would move onto 0, 0 blocks Apply: FontLab cannot redo that
  move (fl#8527);
- a glyph that has an automatic layer is listed and skipped.

So is a glyph that is a base of an automatic composite, also through other
composites, unless you tick "Also edit bases of automatic composites"
(FontLab then rebuilds those composites; Undo may not restore their
anchors). The script refuses before any history exists when FontLab holds
queued glyph updates. After the write, it reads transforms, a node per baked
shape and the anchors back. If FontLab fails part-way, the error says that
native changes may remain. The change is recorded as one Undo step. The
one-step write, the automatic-layer rule, the pending-update check, the
preview and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_transform); the matrix math is fly.ap.affine; the planner
belongs to this script.

Source: the author's own FontLab sample outlines_transform_dialog.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Transform** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/84b3c25820ec0cddd676d89c8f6f8a2d1bd28f9a5b5cd47e65b5135e22dd754f.py)
<!--/codeinclude-->
