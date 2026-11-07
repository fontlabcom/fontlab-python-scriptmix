---
this_file: src_docs/md/scripts/contours/reflect-horizontally.md
tags: ["Contours"]
categories: ["Contours"]
---

# Reflect Horizontally

Reflect selected nodes and components horizontally about their combined centre.


How: A glyph-space reflection maps selected own nodes and composes selected
component placements. Shape transforms are accounted for. Selected node bounds include handles;
component bounds use the transformed local bounding rectangle. Unselected
geometry stays; the table identifies the per-layer centre before Apply.

Why: FontLab's Tools > Flip Horizontal command covers this reflection.
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
Behaviour source: Reflect/Reflect Horizontally.py.

Run **Contours > Reflect Horizontally** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `42d40f633234a89585e1181c5ee3c191357feec18cdca8fe543caeb3e3e022ae`

[Python source at `c2b34988556c`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/c2b34988556c9214a67f800f68565b7a32df832a/Scripts/Contours/Reflect%20Horizontally.py)
