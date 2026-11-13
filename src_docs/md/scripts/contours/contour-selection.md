---
this_file: src_docs/md/scripts/contours/contour-selection.md
tags: ["Contours"]
categories: ["Contours"]
---

# Contour Selection

Preview and apply complete, partial or small contour selection in one studio.

Requires FontLab App with Contour Selection and fontlab-fly. The first selected
layer is captured; Preview Changes stages selection and Apply Selection rechecks
it before writing. Geometry is never changed. Small-contour selection clears
other selected items. Partial selection retains the original cross-contour toggle.

Choose a task tab, then inspect the before/after counts in its sortable table.
Drag column edges to resize them or filter the rows. The read-only glyph pane
shows the captured glyph and layer; it cannot move nodes. Tab switches retain
your staged selection. Use Discard Preview before Refresh if the source changes.
Native context, topology and selection are checked again immediately before
the write; a stale target is refused instead of redirecting to another layer.

Independent adaptations after Pedro Arilla, glyphs-scripts (2018–2022),
Apache-2.0. See NOTICE and additional-tools.json for original source identities.

Run **Contours > Contour Selection** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `c806bdb567d2c28f3793607ca20638f40c7136cfdaab214f135a1406c9ed0395`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Contours/Contour%20Selection.py)
