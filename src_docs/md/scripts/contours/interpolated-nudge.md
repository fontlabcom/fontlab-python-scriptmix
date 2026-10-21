---
this_file: src_docs/md/scripts/contours/interpolated-nudge.md
tags: ["Contours"]
categories: ["Contours"]
---

# Interpolated Nudge

Move selected endpoints while keeping adjacent handle tension.

What: Move selected endpoints while keeping adjacent handle tension. How: Plan
simultaneous moves from original coordinates. The moved node's own handles also scale.
Clamp per-axis handle factors to 0 through 4; zero collapses a handle at its endpoint
instead of flipping it. Tiny axis spans use rigid movement. Read-back allows 0.5 unit
per axis for native rounding. Adjacent handles can lose collinearity at smooth nodes;
inspect these nodes after a move. Scale each neighbouring handle about its endpoint by
the changed endpoint distance in each axis. Keep ratios when an axis span is zero. Why:
Adjust outlines with less handle repair. Use: Select on-curve nodes in the glyph editor,
reload the panel, set X and Y, then Apply. Repeat as needed. Benefit: A repeatable non-
modal nudge with one history action per Apply.

The non-modal panel previews the selected glyphs and chosen masters. Shared, scaled and
rotated outline shapes are kept. Automatic-layer owners are kept. Bases of automatic
composites are kept unless the shared consent option is enabled. Each Apply is recorded
as one Undo step through the App history writer. Reload after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Interpolated Nudge.py,
MIT, copyright 2017 Simon Cozens. Repository:
https://github.com/simoncozens/GlyphsScripts . No source code was copied.

Run **Contours > Interpolated Nudge** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bc030cb1f0b01070518110c9abfce986c154a4844dc008082665e0ce9d5cb20c.py)
<!--/codeinclude-->
