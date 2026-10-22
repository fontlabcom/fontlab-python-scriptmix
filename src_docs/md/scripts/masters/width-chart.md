---
this_file: src_docs/md/scripts/masters/width-chart.md
tags: ["Masters"]
categories: ["Masters"]
---

# Width Chart

Line chart of the advance widths of the selected glyphs across masters.

What it does:
    Masters run left to right in axis order; each glyph is one line with its widths labelled, so a
    master that breaks the progression stands out at once. Read-only.

How it works:
    Read selected glyph widths in master axis order. Draw one labelled series
    per glyph through the shared Masters chart, with a limit on displayed
    series.

Why this design:
    A chart makes a reversed width progression easier to see than a table of
    individual values.

How to use:
    Select glyphs in the Font window. Run Masters > Width Chart. Compare each
    line and its labels; select fewer glyphs if the series limit hides a
    glyph.

Benefit:
    Find masters that need spacing review without changing advance widths or
    outlines.

Run **Masters > Width Chart** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/23e832186bde7fa4d5ad850e772d44cc334ed0d4c0c7d5b9ba30bd86f3926e57.py)
<!--/codeinclude-->
