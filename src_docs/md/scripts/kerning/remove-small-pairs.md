---
this_file: src_docs/md/scripts/kerning/remove-small-pairs.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Remove Small Pairs

Delete kerning pairs whose value is smaller than a threshold, on one or all masters.

Tiny pairs (±1 … ±5 units) are invisible in print, bloat the kern feature and often come from
auto-kerning or interpolation. The preview lists every pair that would go, with the count per
master; zero pairs are included. Class pairs (@name) count like glyph pairs. One Apply is one
Undo step for all masters.

Run **Kerning > Remove Small Pairs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/de4b6244375ea09af774a8bd4effeaf7f67be65c2b15ad05a328c23048f269cd.py)
<!--/codeinclude-->
