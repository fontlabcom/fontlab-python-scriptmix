---
this_file: src_docs/md/scripts/contours/superaligner.md
tags: ["Contours"]
categories: ["Contours"]
---

# Superaligner

Align contour start nodes and directions to the first declared master.

What: Align contour start nodes and directions to the first declared master. How:
Compare normalized point geometry among cyclic point-type matches in both directions.
Choose the unique closest order; keep a glyph when scores tie. Read back the actual
point coordinates, start and winding after each write. Why: Repair master point ordering
before interpolation. Use: Choose All masters, inspect the start and direction changes,
then Apply. Benefit: Adds a batch preview to start-node and direction commands.

The non-modal panel previews the selected glyphs and chosen masters. A glyph with
shared, scaled or rotated outline shapes is kept as a whole. Automatic-layer owners are
kept. Bases of automatic composites are kept unless the shared consent option is
enabled. Each Apply is recorded as one Undo step through the App history writer. Reload
after changing the selection.

Independent behaviour rewrite after Simon Cozens, GlyphsScripts/Superaligner.py, MIT,
copyright 2017 Simon Cozens. Repository: https://github.com/simoncozens/GlyphsScripts .
No source code was copied.

Run **Contours > Superaligner** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `f43e31cb5d62486e9c7362ea41febc982c0ab830f213c2232aa8365e4b503e05`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Contours/Superaligner.py)
