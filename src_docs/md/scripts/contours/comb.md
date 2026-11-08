---
this_file: src_docs/md/scripts/contours/comb.md
tags: ["Contours"]
categories: ["Contours"]
---

# Comb

Split ribbon contours into evenly spaced strips.

What: Split ribbon contours into evenly spaced strips. How: The shortest opposing
compatible line segments form caps. Pair the intervening edges in opposite directions
and interpolate their coordinates. Equal segment types are required. New contours
replace the ribbon. Read-back allows 0.5 unit per axis for native rounding. Why: Make a
striped outline while retaining cubic edge geometry. Use: Set strip count and filled
percentage. Inspect the contour counts, then Apply. Benefit: Generates editable strips
over selected glyphs and masters. Rebuilt contours have new node identities.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Comb.py, MIT, copyright
2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts . No source
code was copied.

Run **Contours > Comb** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5b04d1c4f70cf7e4378c4a90219af93997abd2182e76a9b60d55f10208fc2229`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Contours/Comb.py)
