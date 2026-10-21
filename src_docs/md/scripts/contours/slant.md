---
this_file: src_docs/md/scripts/contours/slant.md
tags: ["Contours"]
categories: ["Contours"]
---

# Slant

Slant the selected glyphs by an angle, optionally the font's italic angle.

What: Set an angle, or press the italic-angle button, and choose the pivot:
the baseline, or half the x-height of each master. The preview paints the
first selected glyph of the current master with the pivot line. The table
lists each glyph and master with its node count and pivot. Slant applies it.

How: x' = x + tan(angle) × (y − pivot); y stays. Each shape gets the matrix
the way FontLab's own layer transform does: a plain own outline gets new
node positions (FontLab may round them); a component, a shared outline or a
scaled shape keeps its nodes and gets the composed transform. Anchors follow
when you tick "Slant anchors too". The advance width and the guides stay.

Why: A slant about the baseline pushes tall glyphs to the right. A slant
about half the x-height keeps the glyph centred in its advance: this is the
usual first step of an oblique or italic. Contours > Transform has a skew
too, but no italic angle and no per-master x-height pivot. Compared with
Tools > Actions > Slant, this panel offers a half-x-height pivot per master.
The italic button copies the current master’s angle into the shared angle
field; that same angle is then applied to every chosen master.

Use: Select glyphs. Run the script. Set the angle, the pivot and the
masters. Press Slant. Press Reload selection after you change the selection.

Benefit: A consistent oblique over many glyphs and masters in one Undo step.

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

Source: the author's own FontLab sample outlines_slant.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Contours > Slant** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/01989245039b9079d3b088e68206cd3e27aeb6e6f530e953ed83b602ba0369fb.py)
<!--/codeinclude-->
