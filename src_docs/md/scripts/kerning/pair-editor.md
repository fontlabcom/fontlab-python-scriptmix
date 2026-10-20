---
this_file: src_docs/md/scripts/kerning/pair-editor.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Pair Editor

Edit every kerning pair that involves one glyph, with one column per master.

Rows are the pairs where the glyph, or a kerning class it belongs to, is on the left or right.
Type a new value in any master's cell; clear a cell to delete that pair on that master. Edited
cells turn the accent colour until Apply, which writes all of them as one Undo step. Add a row
for a new partner with the field under the table.

Run **Kerning > Pair Editor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2e31e1278e5de1606eea877ecbed5d6ee93e433440acd934f0de8cb762a66dfc.py)
<!--/codeinclude-->
