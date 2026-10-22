---
this_file: src_docs/md/scripts/guides/font-guides-panel.md
tags: ["Guides"]
categories: ["Guides"]
---

# Font Guides Panel

List font-guide names and add named horizontal or vertical glyph guides.

What it does:
    Select glyphs, run the script, name a guide and choose its position and master
    scope. Inspect every planned row, then use Add glyph guide. Existing matching
    guides and automatic layers are kept. Fonts whose automatic dependants cannot
    be restored by Undo are refused before editing. Close releases owned signals.
    This panel adds glyph guides; it does not add font-wide guides.

How it works:
    Read font-guide names for reference, then plan one named horizontal or
    vertical glyph guide per chosen layer. Keep matching guides and automatic
    layers.

Why this design:
    Listing font guides provides context without implying that this panel
    edits font-wide guide objects.

How to use:
    Select glyphs and run Guides > Font Guides Panel. Enter a guide name,
    direction and position, choose the master scope, inspect rows and press
    Add glyph guide.

Benefit:
    Add a consistent named glyph reference while preserving existing guide
    records and outlines.

Run **Guides > Font Guides Panel** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/638d03dda5be391c0a3559e1b7daf2381400abac5fa4945d94061dcfcee7f6d7.py)
<!--/codeinclude-->
