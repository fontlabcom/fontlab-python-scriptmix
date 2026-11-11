---
this_file: src_docs/md/scripts/contours/curve-all-straights.md
tags: ["Contours"]
categories: ["Contours"]
---

# Curve All Straights

Convert straight segments to cubic curves.

What: Convert straight segments to cubic curves. How: Native segment conversion inserts
handles. Marks every on-curve node of converted contours smooth, including ends of
existing curves. FontLab may realign handles at former corners when you edit them later.
Why: Prepare traced outlines for curve editing. Use: Select nodes in the current layer
to choose whole contours, or leave nodes unselected for all contours. The same contour
and endpoint indices apply only to layers with matching contour counts, node counts and
point types. Incompatible layers are listed as kept. Inspect the segment counts, then
press Apply. Benefit: Adds a master-wide preview to native segment conversion.

The non-modal panel previews the selected glyphs and chosen masters. A layer that has a shared, scaled or
rotated outline shape is kept as a whole. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Curve All Straights.py,
MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.

Run **Contours > Curve All Straights** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `c89c3ce42d661afee21dd8d65a859f6e6d830232f714020ba97ceacec79e5cdf`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Contours/Curve%20All%20Straights.py)
