---
this_file: src_docs/md/scripts/reports/nodes-near-zones.md
tags: ["Reports"]
categories: ["Reports"]
---

# Nodes Near Zones

Find on-curve nodes that sit within a few units of a vertical metric but not on it.

Near misses (y = 687 when the cap height is 688) are almost always slips
of the mouse; real overshoots are further away and pass. Checks baseline,
x-height, cap height, ascender and descender of every master. Select the
glyphs to fix them. Nothing in the font changes.

Run **Reports > Nodes Near Zones** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e5a80cd4148f4e58f55e0a6d1515dd3311fdcf646dd0d69673f46498ecf1217c.py)
<!--/codeinclude-->
