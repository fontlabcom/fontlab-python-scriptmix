---
this_file: src_docs/md/scripts/reports/open-contours.md
tags: ["Reports"]
categories: ["Reports"]
---

# Open Contours

Find open contours on every master and select the glyphs that have them.

What it does:
    Open paths are usually unintended in a font for filling: they render
    unpredictably and break overlap removal. Each row is one open contour with
    its master, node count and the gap between its end points. Nothing in the
    font changes.

How it works:
    Scan glyph layers on every declared master. For each open contour, list
    its node count and the distance between its end points; keep source
    identity for selection.

Why this design:
    An open contour can be intentional, so the report identifies it for review
    rather than closing paths automatically.

How to use:
    Run Reports > Open Contours. Inspect the glyph, master and gap columns.
    Select report rows to locate their glyphs in the Font window, then review
    the actual paths.

Benefit:
    Find open-path candidates across masters without changing their topology
    or geometry.

Run **Reports > Open Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/10540577d3d96859b8e3e3a2c8cf930ff6bbfbb2ee25a3efb7c59ddd054d4b84.py)
<!--/codeinclude-->
