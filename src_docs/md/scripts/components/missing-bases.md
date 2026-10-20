---
this_file: src_docs/md/scripts/components/missing-bases.md
tags: ["Components"]
categories: ["Components"]
---

# Missing Bases

Find components that point to glyphs which do not exist, or to a base glyph without that master.

Such components draw nothing and break exports. The tree groups the problems by
the missing base glyph; expand a group to see the composites and masters affected.
Select affected glyphs puts them in the Font window selection. Nothing is changed.

Run **Components > Missing Bases** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a6ab4aa6160b8cf9ac2d5bd851b47dbe07399f59f8f429c5b30e40cbd4a0fe4c.py)
<!--/codeinclude-->
