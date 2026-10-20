---
this_file: src_docs/md/scripts/kerning/pair-list-browser.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Pair List Browser

Browse every kerning pair of a master: filter, sort by any column, export to CSV.

Type in the filter to keep pairs whose left or right side contains the text (glyph or @class
name); "=" anchors a whole side, so "=T" shows pairs with exactly T on one side. Click a header
to sort; values sort numerically. Export writes the pairs shown to a CSV file. Read-only.

Run **Kerning > Pair List Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/925c5ac9178477b00f4c133d54982116ba63175959ae4a0e2ebcd95b1f9e3ae0.py)
<!--/codeinclude-->
