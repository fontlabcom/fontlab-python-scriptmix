---
this_file: src_docs/md/scripts/reports/live-glyph-info.md
tags: ["Reports"]
categories: ["Reports"]
---

# Live Glyph Info

A live panel for the glyph you are working on: widths, side-bearings, bounds and counts per master.

What it does:
    It follows the first glyph selected in the Font window (or the glyph being
    edited) and re-reads it twice a second, so edits show up as you make them.
    Values that differ between masters stand out. Nothing in the font changes.

How it works:
    Poll the focused glyph and read width, sidebearings, bounds and object
    counts for its master layers. Highlight columns whose displayed values
    differ.

Why this design:
    Live values remove the need to reopen a static report after each drawing
    or spacing edit.

How to use:
    Run Reports > Live Glyph Info with a font open. Select a glyph in the Font
    window or edit a glyph and inspect the updated master rows. Close the
    panel when finished.

Benefit:
    Monitor the reported metrics and counts while leaving the font data
    unchanged.

Run **Reports > Live Glyph Info** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/099ae94f54c877799291208da323d96fd7d33ba942f2b7d5078a316a6e0df0bc.py)
<!--/codeinclude-->
