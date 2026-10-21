---
this_file: src_docs/md/scripts/contours/straighten-all-curves.md
tags: ["Contours"]
categories: ["Contours"]
---

# Straighten All Curves

Replace every cubic segment with its straight chord.

What: Replace every cubic segment with its straight chord. How: Native conversion
removes handles; endpoints stay in place. FontLab may reset the smooth flags of both end
nodes during conversion. Why: Create a polygonal version of an outline.
Use: Select nodes in the current layer to choose whole contours, or leave nodes
unselected for all contours. The same contour and endpoint indices apply only to layers
with matching contour counts, node counts and point types. Incompatible layers are
listed as kept. Inspect the curve counts, then press Apply.
Benefit: Converts the chosen contours across compatible layers with a preview.

The non-modal panel previews the selected glyphs and chosen masters. A layer that has a shared, scaled or
rotated outline shape is kept as a whole. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Straighten All
Curves.py, MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.

Run **Contours > Straighten All Curves** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e2dfd2f697267957a495bd144d225a4c6a747792645a26b4c52f97578e9b37f6.py)
<!--/codeinclude-->
