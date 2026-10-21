---
this_file: src_docs/md/scripts/contours/add-extremes.md
tags: ["Contours"]
categories: ["Contours"]
---

# Add Extremes

Add on-curve nodes at the horizontal and vertical extremes of curves.

What: For each selected glyph and master, the table lists every contour
whose curves have an extreme without a node: the node count now and the
number of extremes to add. Add Extremes inserts them.

How: For each cubic curve, the script solves the derivative of x and of y
for t; extremes closer than 2 % of the parameter t to an end node are
ignored. FontLab's own split, flContour.insertNodeTo, inserts each node, so
the curve keeps its shape up to FontLab's rounding of the new node. Cuts
within 0.1 Manhattan units of an end or an earlier cut are not offered. The
splits run from the last curve back, so the segment numbers of the earlier
curves stay valid. TrueType (quadratic) contours and open contours are left
alone.

Why: Fonts need nodes at extremes for good hinting and rasterisation, and
font tests flag missing extremes. With "Keep masters compatible" ticked, a
glyph is held back when the masters would get different nodes, or when only
some masters are in scope: different nodes break interpolation.

Use: Select glyphs. Run the script. Choose the masters. Press Add Extremes.
Press Reload selection after you change the selection.

Benefit: Fixes many glyphs over many masters in one Undo step, and keeps the
masters compatible.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (an extreme in stored coordinates is
  not an extreme on screen).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
After the write, it reads the node counts back. If FontLab fails part-way,
the error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_add_extremes.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Add Extremes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c992a8d1e42d52305d044c9418a62965eaa94e87ca0048455e7735f1cdb9ce6a.py)
<!--/codeinclude-->
