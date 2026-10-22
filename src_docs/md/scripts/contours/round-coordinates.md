---
this_file: src_docs/md/scripts/contours/round-coordinates.md
tags: ["Contours"]
categories: ["Contours"]
---

# Round Coordinates

Round node coordinates, anchors and component offsets to a grid.

What: For each selected glyph and master, the table shows how many nodes are
off the grid and which component offsets change. Round snaps them to the
nearest multiple of the grid (1 unit by default).

How: A node is rounded in glyph coordinates. When its shape is moved (a
plain shape offset), the script rounds the visible position and stores the
matching local value, so the node lands on the grid where you see it. Halves
round up (2.5 -> 3, -2.5 -> -2), as Qt's qRound and Anchors > Round To Grid
do. Component offsets are rounded; the scale and slant of a component stay.
Nodes are moved in place, which is meant to keep node names and flags
(FontLab’s source; not measured).

Why: Scaling, interpolation and imports leave fractional or off-grid
coordinates. They cost file size and can cause rendering noise. Optional
anchor rounding uses fly.ap.anchor_writer in the same transaction. A layer
with ambiguous anchor names or an existing anchor that would move to 0, 0
is listed and kept (fl#8527).

Use: Select glyphs. Run the script. Set the grid and the masters; untick
"Component offsets" to keep them. Anchors starts ticked; untick Anchors to
round only nodes and offsets. Press Round. Press Reload selection after
you change the selection.

Benefit: Cleans many glyphs over many masters in one Undo step, and shows
the count before anything changes.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (their stored grid is not the visible
  grid);
- shapes moved by a fraction of a unit (FontLab may round the stored nodes,
  so the visible nodes could not land on the grid).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
After the write, it reads every value back. If FontLab fails part-way, the
error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_round_coordinates.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Round Coordinates** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/26221318bd8a21042c3bd74e3b67b3caf2b8d04c269b52992a6f70882f7ef4b8.py)
<!--/codeinclude-->
