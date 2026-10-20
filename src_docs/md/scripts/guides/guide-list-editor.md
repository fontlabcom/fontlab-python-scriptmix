---
this_file: src_docs/md/scripts/guides/guide-list-editor.md
tags: ["Guides"]
categories: ["Guides"]
---

# Guide List Editor

Edit glyph-guide coordinates, angles and names of the first selected glyph.

Choose current or all masters. Edit X, Y, angle in degrees and name; Add guide,
Delete selected and Revert change the proposal. Apply makes each editable master
match its rows in one Undo step. Unchanged guides retain their native properties;
hints are kept. Bad/non-finite cells and unknown masters refuse the whole write.
Unsafe automatic dependants are refused. Close releases signals and glyphs.

Run **Guides > Guide List Editor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/fdf1c8c18c9675a8895305d80a78435bb2f8b0681d97b4a4e531c5cf9222d984.py)
<!--/codeinclude-->
