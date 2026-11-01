---
this_file: src_docs/md/scripts/contours/delete-close-points.md
tags: ["Contours"]
categories: ["Contours"]
---

# Delete Close Points

Merge endpoints of segments shorter than a chosen distance.

What: Merge endpoints of segments shorter than a chosen distance. How: Measure cubic arc
lengths with 32 samples; remove short incoming spans. Closed contours retain at least
three endpoints. Why: Remove tiny segments left by tracing. Use: Set the distance in
font units, inspect the counts, then press Apply. Benefit: Shows exactly which segments
change before a batch edit.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Delete Close Points.py,
MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.

Run **Contours > Delete Close Points** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e28174d298944ee1cdae40634a4c7486d62d2cd33cd1e7b930f3d1eefe9709fb.py)
<!--/codeinclude-->
