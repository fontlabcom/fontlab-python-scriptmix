---
this_file: src_docs/md/scripts/contours/contour-order-view.md
tags: ["Contours"]
categories: ["Contours"]
---

# Contour Order View

Show every master of a glyph side by side with numbered contours, start points and directions.

What it does:
    Each contour carries its index at the start node, a dot on the start node and an arrow along
    its first segment, so start-point and order mismatches between masters are visible at a glance
    before interpolation surprises you. Read-only: nothing in the font changes.

How it works:
    Use the shared contour-order view to draw each master and label contour
    indices, start nodes and first-segment directions at their native
    positions.

Why this design:
    A structural count cannot reveal a different start point or contour order;
    the drawing exposes those differences directly.

How to use:
    Select a glyph and run Contours > Contour Order View. Compare matching
    contour numbers and direction arrows between the master panels before
    editing compatibility.

Benefit:
    Review contour order and starts without reversing paths or changing
    interpolation structure.

Run **Contours > Contour Order View** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a6631d3cb8e2a3aec56ca5ea5c7b0103447f9cc0b4c4491dab95d84c842331a9.py)
<!--/codeinclude-->
