---
this_file: src_docs/md/scripts/contours/node-statistics.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Statistics

Contours and nodes per glyph and master in one table, with incompatible glyphs flagged.

What it does:
    Each cell reads "contours / nodes" for a master; a glyph is flagged when its masters differ,
    which breaks interpolation. Work on the selection or the whole font, then select the flagged
    glyphs in the Font window with one click. Read-only: nothing in the font changes.

How it works:
    Read contour and node counts on the selection or whole font, grouped by
    master. Flag differing counts and keep the source snapshot for the
    selection action.

Why this design:
    Count differences can rule out compatibility, but matching counts alone do
    not prove matching contour structure.

How to use:
    Run Contours > Node Statistics. Choose the source scope, inspect each
    contours/nodes cell and use the action button to select flagged glyphs in
    the Font window.

Benefit:
    Find count mismatches quickly while preserving node positions, topology
    and layer data.

Run **Contours > Node Statistics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/dcc972723a148c263d9fba99267508d7c518d48c95733367590323141b425eea.py)
<!--/codeinclude-->
