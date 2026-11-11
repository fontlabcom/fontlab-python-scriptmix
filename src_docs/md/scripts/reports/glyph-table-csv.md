---
this_file: src_docs/md/scripts/reports/glyph-table-csv.md
tags: ["Reports"]
categories: ["Reports"]
---

# Glyph Table CSV

A sortable table of glyphs (name, Unicode, width per master, contours, components) with CSV export.

What it does:
    Pick all glyphs or the selection, review the table, then export it as a
    UTF-8 CSV file (choose the path first) or copy it to the clipboard for a
    spreadsheet. Contours count everything drawn, components included, on the
    current master. Nothing in the font changes.

How it works:
    Capture glyph names, encodings, master advances and current-master
    contour/component counts. Encode rows with CSV quoting for clipboard or
    UTF-8 file export.

Why this design:
    A spreadsheet-friendly snapshot supports external review while keeping the
    font as the source of the measured values.

How to use:
    Run Reports > Glyph Table CSV. Choose all glyphs or selection, review the
    columns and choose a path before Export, or use Copy for the computed CSV
    text.

Benefit:
    Share a glyph inventory with widths across masters without writing any
    font data.

Run **Reports > Glyph Table CSV** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `7e5642249b14d7cdb4d17088ee8789585f91a471fe143eb6aefd05948982adec`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Reports/Glyph%20Table%20CSV.py)
