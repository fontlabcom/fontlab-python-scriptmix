---
this_file: src_docs/md/scripts/contours/node-coordinates-panel.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Coordinates Panel

Follow selected nodes as you edit; inspect coordinates, offsets and distances.

What it does:
    Open a glyph, run this script and select nodes. Both tables update every 400 ms.
    Copy exports the displayed node coordinates as tab-separated lines. Contour
    numbers start at one; node indices start at zero. Component contours are excluded.
    The modeless panel reads the bound font only. Switching or closing that font
    stops polling; reopen the tool to bind another font. No font data is written.

How it works:
    Read selected own nodes on the bound glyph layer and publish both tables
    from the same snapshot. Poll every 400 ms and recheck that snapshot before
    Copy.

Why this design:
    Live coordinates support measurement while a stale-font refusal prevents
    copying values from a different document under the old panel title.

How to use:
    Open a glyph and run Contours > Node Coordinates Panel. Select nodes,
    inspect positions and distances, then use Copy for the displayed tab-
    separated coordinates.

Benefit:
    Measure selected nodes without moving them; Close stops polling and
    releases owned connections.

Run **Contours > Node Coordinates Panel** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3dc045bd4ecec623478b084e2a901fa961c677fccfa7ae57fa5ccf260d71639b.py)
<!--/codeinclude-->
