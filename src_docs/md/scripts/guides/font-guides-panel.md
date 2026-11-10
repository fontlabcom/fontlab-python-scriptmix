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

## Source identity

SHA256: `5ebf7188897e7bd285f3a2408a486d1bb9fd2bbbc1d7e540b45b05f3dc11e09a`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Guides/Font%20Guides%20Panel.py)
