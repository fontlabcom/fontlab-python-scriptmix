---
this_file: src_docs/md/scripts/reports/nodes-near-zones.md
tags: ["Reports"]
categories: ["Reports"]
---

# Nodes Near Zones

Find on-curve nodes that sit within a few units of a vertical metric but not on it.

What it does:
    Near misses (y = 687 when the cap height is 688) are almost always slips
    of the mouse; real overshoots are further away and pass. Checks baseline,
    x-height, cap height, ascender and descender of every master. Select the
    glyphs to fix them. Nothing in the font changes.

How it works:
    Transform own on-curve node positions into layer coordinates. Report
    points with a nonzero distance within the chosen tolerance of each
    master's vertical metrics.

Why this design:
    A near-miss report is a review aid; small offsets can be intentional and
    must not be snapped automatically.

How to use:
    Run Reports > Nodes Near Zones. Choose selection or whole font and a
    tolerance, inspect glyph/master/metric rows and select results to examine
    them in FontLab.

Benefit:
    Find nodes close to metric lines without moving nodes, handles, components
    or anchors.

Run **Reports > Nodes Near Zones** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/747edb4fb3133b6c8550b802b421c7e94cd48084723294fc06a94efd90cbdc0d.py)
<!--/codeinclude-->
