---
this_file: src_docs/md/scripts/contours/superaligner.md
tags: ["Contours"]
categories: ["Contours"]
---

# Superaligner

Align contour start nodes and directions to the first declared master.

What: Align contour start nodes and directions to the first declared master. How:
Compare normalized point geometry among cyclic point-type matches in both directions.
Choose the unique closest order; keep a glyph when scores tie. Read back the actual
point coordinates, start and winding after each write. Why: Repair master point ordering
before interpolation. Use: Choose All masters, inspect the start and direction changes,
then Apply. Benefit: Adds a batch preview to start-node and direction commands.

The non-modal panel previews the selected glyphs and chosen masters. A glyph with
shared, scaled or rotated outline shapes is kept as a whole. Automatic-layer owners are
kept. Bases of automatic composites are kept unless the shared consent option is
enabled. Each Apply is recorded as one Undo step through the App history writer. Reload
after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Superaligner.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.

Run **Contours > Superaligner** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b020ca7890e04af368961cc6a49d6ffe26ee6bf439994da125756b0a631323c9.py)
<!--/codeinclude-->
