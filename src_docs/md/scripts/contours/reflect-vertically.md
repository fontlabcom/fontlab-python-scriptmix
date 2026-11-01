---
this_file: src_docs/md/scripts/contours/reflect-vertically.md
tags: ["Contours"]
categories: ["Contours"]
---

# Reflect Vertically

Reflect selected nodes and components vertically about their combined centre.


How: A glyph-space reflection maps selected own nodes and composes selected
component placements. Shape transforms are accounted for. Selected node bounds include handles;
component bounds use the transformed local bounding rectangle. Unselected
geometry stays; the table identifies the per-layer centre before Apply.

Why: FontLab's Tools > Flip Vertical command covers this reflection.
This panel adds a preview and processes several masters or selected layers
in one action. Each action is recorded as one Undo step. Contours > Transform
instead transforms whole layers.

Use: Select nodes or components. Open the panel, inspect the table and
press Reflect. Choose all masters to process stored selections on multiple
master layers together. Reload selection after choosing other glyphs.

Benefit: Repeat a selection edit across glyphs with one planned batch action.

Safety: Locked layers, locked shapes and shared selected outline data are
refused. Contours with their own transform are refused. Automatic-layer
glyphs and their bases are skipped. The action replans live node selection before writing. A failed write names Edit > Undo.
The change is recorded as one Undo step. Anchors, guides, widths and node
order stay. FontLab can round node coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov
(slobzheninov), https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0. No source code, identifiers or comments were copied.
Behaviour source: Reflect/Reflect Vertically.py.

Run **Contours > Reflect Vertically** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/0965871b27b324df8bf564ac29135e8704f3bd6c7bc4099e0fac1c347db71b34.py)
<!--/codeinclude-->
