---
this_file: src_docs/md/scripts/reports/empty-glyphs.md
tags: ["Reports"]
categories: ["Reports"]
---

# Empty Glyphs

List glyphs that have no outlines and no components on some or all masters, and select them.

What it does:
    A glyph empty on one master but drawn on others is usually a mistake;
    spaces are empty on purpose and can be hidden. Each master is a column.
    Select puts the listed glyphs (or the rows you pick) into the Font window
    selection. Nothing in the font changes.

How it works:
    Read whether each glyph layer draws contours, including component
    contours. Record empty masters and optionally hide whitespace-like glyphs
    and conventional empty names.

Why this design:
    Some empty glyphs are intentional; a report with a whitespace filter
    supports review without deleting data.

How to use:
    Run Reports > Empty Glyphs. Choose whether to hide whitespace, inspect the
    per-master columns and select chosen rows or all listed glyphs in the Font
    window.

Benefit:
    Find incomplete master drawings while preserving empty glyphs and their
    advances.

Run **Reports > Empty Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `dad6b49302f0ee0d76d663b83bd0769e61f4b5ffd999a5e5094065b815674581`

[Python source at `dc797fffaa31`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/dc797fffaa31fa6c47959870966e2642fe1df6f7/Scripts/Reports/Empty%20Glyphs.py)
