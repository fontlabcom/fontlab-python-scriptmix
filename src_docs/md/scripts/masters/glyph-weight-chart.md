---
this_file: src_docs/md/scripts/masters/glyph-weight-chart.md
tags: ["Masters"]
categories: ["Masters"]
---

# Glyph Weight Chart

Bar chart of the ink area of the selected glyphs in every master.

Ink area is the filled area of the outline: contour areas from the flattened curves, counters
subtracted by nesting. Overlapping contours are counted twice, so remove overlaps first for exact
numbers. Each glyph gets one bar per master in axis order, labelled in thousands of square units.
Read-only.

Run **Masters > Glyph Weight Chart** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/065db5fbb8727be35506317f30d3c7c997928aa0ff3af1a89b4cf6ca7c29ca36.py)
<!--/codeinclude-->
