---
this_file: src_docs/md/scripts/font-info/master-metrics-table.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Master Metrics Table

Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row.

What it does:
    Open with a font active. Double-click a metric value, check the selected row's
    diagram, then choose Apply. Every row is checked before any edit. Apply writes
    all changed masters as one Undo step and preserves glyph outlines. Keep this
    panel bound to its original font; reopen it after switching to another font.

How it works:
    Read each master's four vertical metrics while restoring the original
    current master. Validate finite, ordered, signed-16-bit proposals before
    writing metadata. Apply refuses when a value changed since the preview.
    It then writes and reads back each changed master. When one master fails,
    the written values are restored and nothing is added to Undo. When a
    restore also fails, the status names each failure (such as "master Bold
    was not restored") and says that values can remain; check every master
    before you save.

Why this design:
    A complete multi-row proposal prevents a later invalid cell from leaving
    an earlier master partially updated by normal validation.

How to use:
    Activate the font's Font window and run Font Info > Master Metrics Table.
    Edit metric cells, select a row to inspect its diagram and press Apply
    after reviewing every master. Use Edit > Undo in the Font window to revert
    the whole Apply. Reopen after changing fonts.

Benefit:
    Stage family-wide vertical metrics together while keeping glyph outlines
    unchanged.

Known issue:
    FontLab defect fl#8574: after Edit > Undo or Redo, the metric guides show
    3 of 9 lines until you reopen the font. The saved file is correct.

Run **Font Info > Master Metrics Table** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/08244e0ece2fd4c02315f5562c4cbf5c5351987c583eacbf9bf04fef72f3e1ac.py)
<!--/codeinclude-->
