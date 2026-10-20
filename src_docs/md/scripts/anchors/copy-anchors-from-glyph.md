---
this_file: src_docs/md/scripts/anchors/copy-anchors-from-glyph.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Copy Anchors From Glyph

Copy a source glyph's anchors to selected glyphs, master by master.

Type a source name with fontwide completion; choose merge/replace, width scaling
and current/all masters. Automatic layers are skipped. Unsafe automatic
dependants and stale source previews refuse the complete write before history.
One Copy is one native Undo. Close disconnects every owned callback.

Run **Anchors > Copy Anchors From Glyph** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/046dbf5a680c87aa722a527da700231dcdf126d0c4a4c95e4d24f21259397f89.py)
<!--/codeinclude-->
