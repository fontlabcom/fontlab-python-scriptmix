---
this_file: src_docs/md/scripts/reports/glyph-table-csv.md
tags: ["Reports"]
categories: ["Reports"]
---

# Glyph Table CSV

A sortable table of glyphs (name, Unicode, width per master, contours, components) with CSV export.

Pick all glyphs or the selection, review the table, then export it as a
UTF-8 CSV file (choose the path first) or copy it to the clipboard for a
spreadsheet. Contours count everything drawn, components included, on the
current master. Nothing in the font changes.

Run **Reports > Glyph Table CSV** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/633627b3f2d375b2e67abf6cea0b0ae355178be4771c8a6a2380a45dd5fa8a16.py)
<!--/codeinclude-->
