---
this_file: src_docs/md/scripts/contours/retract-handles.md
tags: ["Contours"]
categories: ["Contours"]
---

# Retract Handles

Retract cubic handles onto their attached on-curve nodes.

What: Retract every cubic handle, or only handles attached to selected on-curve
nodes, in selected glyphs on chosen masters. Node counts and types stay.
How: Resolve handles per segment, including the closing segment. Open contours
do not wrap. Quadratic contours and shared or transformed outlines are kept.
Why: Zero-length handles can prepare curves for deliberate corner edits.
Use: Select glyphs or on-curve nodes. Choose the node filter, inspect the table,
then press Retract. The change is recorded as one Undo step.
Benefit: Exact, repeatable retraction over many glyphs and masters. Automatic
layers are kept; leave the automatic-base consent off to keep their bases too.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Paths/Make zero handles selected glyphs.py and Make zero handles selected nodes.py,
Apache-2.0. Repository: https://github.com/pedroarilla/glyphs-scripts .
No source code copied. Per-contour indexing also handles open ends correctly.

Run **Contours > Retract Handles** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/50625ecbd5c94fff2d33a6ac91ce341d75a5bc3e45eb9a9f1891717b1d18fb72.py)
<!--/codeinclude-->
