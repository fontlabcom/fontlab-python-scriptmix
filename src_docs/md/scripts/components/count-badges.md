---
this_file: src_docs/md/scripts/components/count-badges.md
tags: ["Components"]
categories: ["Components"]
---

# Count Badges

A painted card per selected glyph: its drawing plus component and contour counts for every master.

What it does:
    Accent badges count components, muted badges count the glyph's own contours; a
    master that differs from the first one is marked with a dot, and auto layers are
    labelled. A quick way to see which glyphs are composites, outlines or a mix.
    Nothing in the font is changed.

How it works:
    Use the shared component card view for the selected glyphs. Draw each
    glyph and count its own contours and components per master, marking
    differences from the first master.

Why this design:
    Counts beside the drawing make mixed outline/component construction easier
    to spot than names alone.

How to use:
    Select glyphs and run Components > Count Badges. Inspect each master's
    badges, mismatch dots and automatic-layer labels; scroll or resize to view
    more cards.

Benefit:
    Review construction differences without decomposing components or editing
    layer geometry.

Run **Components > Count Badges** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/16238d3703da6ce1126a8c20af2983b0e8ae5c1030b9460fad204771bf1a0c99.py)
<!--/codeinclude-->
