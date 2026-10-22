---
this_file: src_docs/md/scripts/font-info/master-metrics-table.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Master Metrics Table

Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row.

What it does:
    Open with a font active. Double-click a metric value, check the selected row's
    diagram, then choose Apply. Every row is checked before any edit. Apply records
    one undoable metadata operation and preserves glyph outlines. Keep this panel
    bound to its original font; reopen it after switching to another font.

How it works:
    Read each master's four vertical metrics while restoring the original
    current master. Validate finite, ordered, signed-16-bit proposals before
    writing metadata.

Why this design:
    A complete multi-row proposal prevents a later invalid cell from leaving
    an earlier master partially updated by normal validation.

How to use:
    Run Font Info > Master Metrics Table. Edit metric cells, select a row to
    inspect its diagram and press Apply after reviewing every master. Reopen
    after changing fonts.

Benefit:
    Stage family-wide vertical metrics together while keeping glyph outlines
    unchanged.

Run **Font Info > Master Metrics Table** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9e0c582b5d576c0bb9ac1203c613a803ca6c2343331fec24b9481fb43b040233.py)
<!--/codeinclude-->
