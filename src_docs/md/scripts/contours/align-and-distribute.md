---
this_file: src_docs/md/scripts/contours/align-and-distribute.md
tags: ["Contours"]
categories: ["Contours"]
---

# Align And Distribute

Align selected geometry or space selected nodes at equal intervals.

What: Six alignment choices and horizontal or vertical node distribution share
one non-modal panel. Whole selected contours move as units. Partial contours
contribute selected nodes. Components move by their transform; their base
glyphs stay. Anchors are never moved: this tool cannot read anchor selection.
Use Contour > Align Points to align selected anchors.

How: Work in upright glyph coordinates; italic angle is not applied. Alignment
uses the minimum, maximum or midpoint, or an explicit coordinate. Bounds
include selected control points, so results can differ from Contour > Align
Points. Component bounds use the transformed local bounding rectangle.
Distribution sorts selected nodes on the chosen axis, keeps both endpoints,
and divides their span equally. Ties keep contour/node order. Unselected
adjacent handles follow their moved on-curve node by the same offset. Selected
handles use their own targets. Node types and connection flags stay.

Why: Contour > Align Points aligns points on the current layer.
Element > Align / Distribute Shapes operates on shapes. This tool adds node
distribution, several glyph layers or masters in one Undo step, and a numeric
preview.

Use: Select nodes or components in a Glyph window. Choose an operation, inspect
the table and Apply. All nodes is for alignment only; distribution requires
selected nodes. All masters processes each loaded glyph's masters; node
selection is read separately in each layer. Reload selection after choosing
other glyphs or editor layers. Apply reads selected layers and geometry again.
A single item with Selection bounds has no move. Choose Coordinate to move it.
Two selected nodes that share one curve handle are kept; select the handle
too, or align them one at a time.
Automatic guide/metric snapping and italic deskew are not provided.

Benefit: Repeat alignment without reopening a dialog. Each Apply is recorded
as one Undo step. Automatic-layer glyphs and their bases are skipped. Locked
layers/shapes, shared node data and contours with their own transform are kept
and named in the preview; the other eligible items can still change. Advances,
anchors and guides stay. FontLab can round coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov,
https://github.com/slobzheninov/Glyphs-Scripts, Align/Align Top.py,
Align Bottom.py, Align Left.py, Align Right.py, Align Horizontal Center.py,
Align Vertical Center.py, Distribute Nodes Horizontally.py and Distribute Nodes
Vertically.py, Apache-2.0. The sources credit Rainer Erich Scheichelbauer
(mekkablue, Apache-2.0). No source code, identifiers or comments were copied.

Run **Contours > Align And Distribute** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/43b86780dd5c80484cf556cb3398aea2684fba718bf508deac9bac8398be54bc.py)
<!--/codeinclude-->
