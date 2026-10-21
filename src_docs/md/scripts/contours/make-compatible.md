---
this_file: src_docs/md/scripts/contours/make-compatible.md
tags: ["Contours"]
categories: ["Contours"]
---

# Make Compatible

Promote straight segments where corresponding masters contain cubics.

What: Promote straight segments where corresponding masters contain cubics. How: Compare
each contour and segment with every declared master. Keep glyphs with mismatched contour
counts, open paths or quadratic outlines. Endpoints stay. Why: Repair line-versus-cubic
interpolation mismatches without moving endpoints. Use: Align starts and directions
first (run Superaligner), then select glyphs, choose All masters, inspect the conversion
rows, and Apply. Benefit: Repairs segment types across masters rather than merely
reporting them.

The non-modal panel previews the selected glyphs and chosen masters. A glyph with
shared, scaled or rotated outline shapes is kept as a whole. Automatic-layer owners are
kept. Bases of automatic composites are kept unless the shared consent option is
enabled. Each Apply is recorded as one Undo step through the App history writer. Reload
after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Make Compatible.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.

Run **Contours > Make Compatible** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/755ff2903a203254e9311c1499025a3d24960d51a328f28f138c888f081c2c03.py)
<!--/codeinclude-->
