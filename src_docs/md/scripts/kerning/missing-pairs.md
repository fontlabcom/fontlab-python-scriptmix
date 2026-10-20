---
this_file: src_docs/md/scripts/kerning/missing-pairs.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Missing Pairs

List the combinations of two glyph groups that no kerning pair covers on a master.

Enter left and right glyphs: names separated by spaces, plain characters (“AVT”), or @class
tokens that stand for all their members. Every left + right combination that neither a glyph
pair nor a class pair reaches is listed, ready to proof or to kern. "Copy list" puts the
missing pairs on the clipboard, one "left right" per line. Nothing is edited.

Run **Kerning > Missing Pairs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/eb9a0ee1b2763280639fc9e1810a2f92528a9b4fc58fb8c293ed21026d5d3680.py)
<!--/codeinclude-->
