---
this_file: src_docs/md/scripts/contours/overlap-nodes.md
tags: ["Contours"]
categories: ["Contours"]
---

# Overlap Nodes

Move a tip's adjacent corner onto the tip and align the next handle.

What: Create coincident nodes for alternate contour construction. This does
not merge contours or remove overlap area.
How: For each selected on-curve tip, inspect the next corner first, then
the previous corner. Move the first corner followed by a control onto the
tip, make it sharp, and align the control x along its master's italic angle.
The layer name identifies its master, including auxiliary layers. The control
y stays. Handle x is truncated to an integer in glyph space.
Why: Explicit node selection, conflict refusal and a preview protect the
neighbourhood. Selected-layer/all-master scope uses each layer's stored selection.
Use: Select one tip per corner. Open the panel, inspect the rows and press
Overlap. Reload selection after choosing other glyphs. Scaled and rotated
shapes are refused; plain shape translations are supported.
Benefit: Repeat a precise tip construction without dragging two nodes.

Safety: Locked layers, locked shapes and shared selected outline data are
refused. Contours with their own transform are refused. Automatic-layer
glyphs and their bases are skipped. The action replans live node selection before writing. A failed write names Edit > Undo.
The change is recorded as one Undo step. Anchors, guides, widths and node
order stay. FontLab can round node coordinates to its grid.

Source: Independent behaviour-only rewrite after Alex Slobzheninov
(slobzheninov), https://github.com/slobzheninov/Glyphs-Scripts,
Apache-2.0. No source code, identifiers or comments were copied.
Additional idea credit: Rainer Erich Scheichelbauer (mekkablue), whose
italic-coordinate snippet is credited by the source; independent rewrite.
Behaviour source: Overlap nodes.py.

Run **Contours > Overlap Nodes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/15b1d2140eaab85922e7bfb14271dc41fae8d8c5bca3f9ecbf517be41b5bd33a.py)
<!--/codeinclude-->
