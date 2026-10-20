---
this_file: src_docs/md/scripts/font-info/master-metrics-table.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Master Metrics Table

Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row.

Open with a font active. Double-click a metric value, check the selected row's
diagram, then choose Apply. Every row is checked before any edit. Apply records
one undoable metadata operation and preserves glyph outlines. Keep this panel
bound to its original font; reopen it after switching to another font.

Run **Font Info > Master Metrics Table** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4455e14f52b4db43cd372c2d5218af04e5f4afcf7c925f7f5a75de61402b8be1.py)
<!--/codeinclude-->
