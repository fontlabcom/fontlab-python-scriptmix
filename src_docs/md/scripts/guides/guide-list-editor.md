---
this_file: src_docs/md/scripts/guides/guide-list-editor.md
tags: ["Guides"]
categories: ["Guides"]
---

# Guide List Editor

Edit glyph-guide coordinates, angles and names of the first selected glyph.

What it does:
    Choose current or all masters. Edit X, Y, angle in degrees and name; Add guide,
    Delete selected and Revert change the proposal. Apply makes each editable master
    match its rows in one Undo step. Unchanged guides retain their native properties;
    hints are kept. Bad/non-finite cells and unknown masters refuse the whole write.
    Unsafe automatic dependants are refused. Close releases signals and glyphs.

How it works:
    Stage guide rows for the first selected glyph across the chosen master
    scope. Validate names, coordinates and angles before replacing editable
    master guide sets.

Why this design:
    Retaining unchanged native guides keeps their properties, while a proposal
    table makes added and deleted records explicit.

How to use:
    Run Guides > Guide List Editor after selecting a glyph. Edit rows or use
    Add, Delete and Revert, inspect each master's proposal and press Apply to
    write it.

Benefit:
    Edit glyph construction guides in one recorded Undo step while preserving
    hints and retained guide properties.

Run **Guides > Guide List Editor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `7d706fa180e98dfbf5b64177f501fb0cbe121b722ca1039f489f384d4c893a89`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Guides/Guide%20List%20Editor.py)
