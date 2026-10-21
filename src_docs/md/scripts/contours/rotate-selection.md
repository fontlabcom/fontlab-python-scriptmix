---
this_file: src_docs/md/scripts/contours/rotate-selection.md
tags: ["Contours"]
categories: ["Contours"]
---

# Rotate Selection

Rotate selected nodes and components about their combined coordinate bounds centre.


How: A signed angle turns counterclockwise when positive. Component placements
compose with the same glyph-space matrix. Own nodes map through their shape
transform and back, so transformed outlines use the visible pivot. Bounds
include selected handles and transformed component bounding rectangles.

Why: FontLab's native Rotate commands and Transform panel cover rotation.
This panel adds a preview and processes several masters or selected layers
in one action. Each action is recorded as one Undo step. Contours > Transform
instead transforms whole layers.

Use: Select nodes or components. Open the panel. A 1, 10 or 45 degree
CW/CCW button applies that rotation immediately. For another angle, type the
value, inspect the table and press Rotate. Repeat without closing. Reload
selection after choosing other glyphs.

Benefit: Repeat a selection edit across glyphs with one planned batch action.

Safety: Locked layers, locked shapes and shared selected outline data are
refused. Contours with their own transform are refused. Automatic-layer
glyphs and their bases are skipped. The action replans live node selection before writing. A failed write names Edit > Undo.
The change is recorded as one Undo step. Anchors, guides, widths and node
order stay. FontLab can round node coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov
(slobzheninov), https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0. No source code, identifiers or comments were copied.
Behaviour source: Rotate/Rotate.py and the six Rotate 1/10/45 CW/CCW wrappers.

Run **Contours > Rotate Selection** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5a70a17803378552634cbdff7a72622fe244ccda0f78ae35187530c335995b71.py)
<!--/codeinclude-->
