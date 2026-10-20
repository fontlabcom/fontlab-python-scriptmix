---
this_file: src_docs/md/scripts/contours/node-statistics.md
tags: ["Contours"]
categories: ["Contours"]
---

# Node Statistics

Contours and nodes per glyph and master in one table, with incompatible glyphs flagged.

Each cell reads "contours / nodes" for a master; a glyph is flagged when its masters differ,
which breaks interpolation. Work on the selection or the whole font, then select the flagged
glyphs in the Font window with one click. Read-only: nothing in the font changes.

Run **Contours > Node Statistics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7eff97dfbb7b7c2ea5e080dd3e413be96987aaf8cd64ae2961372252ba28b8ca.py)
<!--/codeinclude-->
