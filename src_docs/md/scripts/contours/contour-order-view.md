---
this_file: src_docs/md/scripts/contours/contour-order-view.md
tags: ["Contours"]
categories: ["Contours"]
---

# Contour Order View

Show every master of a glyph side by side with numbered contours, start points and directions.

Each contour carries its index at the start node, a dot on the start node and an arrow along
its first segment, so start-point and order mismatches between masters are visible at a glance
before interpolation surprises you. Read-only: nothing in the font changes.

Run **Contours > Contour Order View** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ca39b81fa0a200b048ce1a18ec888717a8b4fb4ed8cab59d4bfc470e3b2739d4.py)
<!--/codeinclude-->
