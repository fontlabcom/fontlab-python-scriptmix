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

## Source identity

SHA256: `669f80b1f2513054216347fb76f39bc6db71fd4077810ed8378aaa436711fb6d`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Masters/Glyph%20Weight%20Chart.py)
