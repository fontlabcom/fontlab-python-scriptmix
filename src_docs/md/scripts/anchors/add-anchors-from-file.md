---
this_file: src_docs/md/scripts/anchors/add-anchors-from-file.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Add Anchors From File

Import named anchor coordinates from a UTF-8 CSV file.

What: Add or move named anchors on the current master for every CSV glyph row.
How: Use name or glyph plus paired anchor_x,anchor_y columns. Strip header
whitespace; refuse unknown columns, missing glyphs and malformed rows. Two
empty coordinate cells leave that anchor unchanged. Coordinates round half up
to font units before preview and writing. Report BOM and newline conversions
only when they occur. Existing pins keep their appearance and expressions.
Why: A checked table avoids repeated manual entry and preference-dependent
fractional writes. Automatic layers are kept; unsafe writes are refused.
Use: Browse for a CSV, click Load, inspect the non-modal preview, then Import.
Benefit: Apply a complete coordinate table consistently. Each application
is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.

Run **Anchors > Add Anchors From File** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f7ccec055b1886d4d2950dc2987765532f3ef0f98451d4e9e21d7eb4e7b818e7.py)
<!--/codeinclude-->
