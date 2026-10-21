---
this_file: src_docs/md/scripts/metrics/vertical-metrics-diagram.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Vertical Metrics Diagram

Compare the vertical metrics of every master with real outlines, side by side.

What it does: shows one column per master. Each column draws the outlines of
H, x, b and p from that master against its baseline, ascender, cap height,
x-height and descender lines. A cap height that misses the H, or an x-height
that cuts the x, shows at a glance. The panel only reads the font; it never
changes it.

How it works: the metric values come from FontMetrics(package, master) for
each master, the same reader as Masters > Overview, so the current master is
never switched. The outlines are read in place from each layer's contours,
with component transforms applied, into one QPainterPath per glyph. One scale
fits the tallest and the lowest metric of all masters and the widest sample
line, so the columns compare directly. Line names stand in the left margin.
A sample glyph that the font lacks, or that has no layer in a master, is
listed below the diagram and left out; it never stops the panel. Drawing
errors are kept in the panel and the painter always ends.

Why: wrong vertical metrics are easy to miss in a table of numbers and costly
to find late, in proofs or after export. A picture of all masters with their
own outlines makes the error visible before it spreads.

How to use: open a font and run the script. The panel stays open. Press
Reload after you change the metrics or the sample glyphs. To change the
values, use Font Info > Master Metrics Table (or FontLab's Font Info); this
diagram does not edit.

Benefit: a quick visual check of ascender, cap height, x-height and descender
against real letters in every master, without a risk to the font.

Credit: adapted from metrics_vertical_metrics_diagram.py, the author's own
FontLab sample, Apache-2.0. The editing part of that sample is left to Font
Info > Master Metrics Table.

Run **Metrics > Vertical Metrics Diagram** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/dbea9be50c738984fda958312ec855303c5ff4d339c9f709d60dc674081ebafa.py)
<!--/codeinclude-->
