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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7cb67c7d78be7697eb88ea55440fbe3e9576a1221a1f4718a1e622601ce7511d.py)
<!--/codeinclude-->
