---
this_file: src_docs/md/scripts/masters/glyph-weight-chart.md
tags: ["Masters"]
categories: ["Masters"]
---

# Glyph Weight Chart

Bar chart of the ink area of the selected glyphs in every master.

What it does:
    Ink area is the filled area of the outline: contour areas from the flattened curves, counters
    subtracted by nesting. Overlapping contours are counted twice, so remove overlaps first for exact
    numbers. Each glyph gets one bar per master in axis order, labelled in thousands of square units.
    Read-only.

How it works:
    Use the shared Masters chart and flattened outline areas, subtracting
    counters by nesting. Draw one labelled bar per glyph and master in axis
    order.

Why this design:
    Area bars expose weight differences, but overlapping contours can count
    twice and must be reviewed before treating values as exact filled areas.

How to use:
    Select glyphs and run Masters > Glyph Weight Chart. Compare bars between
    masters; inspect overlap in the source outlines when a value looks
    unexpectedly large.

Benefit:
    Compare the reported ink-area trend without changing outlines or removing
    overlaps.

Run **Masters > Glyph Weight Chart** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/caa919742c2ca9277144d697d243f9688614c39fe6e6406f0cc9d99288b969e1.py)
<!--/codeinclude-->
