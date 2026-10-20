---
this_file: src_docs/md/scripts/reports/unicode-coverage.md
tags: ["Reports"]
categories: ["Reports"]
---

# Unicode Coverage

Unicode coverage of the current font, block by block, with progress bars.

For every Unicode block that the font touches, shows how many of the
block's assigned characters (per Python's unicodedata) have a glyph.
Double-click a block to select its glyphs in the Font window. Block ranges
are embedded (planes 0 and 1). Nothing in the font changes.

Run **Reports > Unicode Coverage** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/abadcdc25b285677df5922c92c1ba2b60a1463e327f124fe45d7a473a0a245ab.py)
<!--/codeinclude-->
