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

## Source identity

SHA256: `dec288cd87dc461cf6344ca90d7d2a81cec3614e5e8509dd673ea1e81a566f25`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Contours/Reflect%20Vertically.py)
