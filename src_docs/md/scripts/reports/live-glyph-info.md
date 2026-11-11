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
    A line under the glyph name shows the active font, glyph and layer.
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

## Source identity

SHA256: `cff55f51dc0905472bcb3edb342be32c0f128e44ab0e880572e7f6fb92c40ad7`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Reports/Live%20Glyph%20Info.py)
