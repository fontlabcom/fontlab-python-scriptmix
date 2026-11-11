---
this_file: src_docs/md/scripts/names/select-by-mark.md
tags: ["Names"]
categories: ["Names"]
---

# Select by Mark

Select glyphs in the Font window by their mark colour.

What it does:
    Lists every mark colour used in the font (and unmarked glyphs) with a
    swatch and a count. Pick one or more rows and click Select, or double-click
    a row. Optionally add to the current selection. Nothing in the font changes.

How it works:
    Group the current font's glyphs by native mark value, then draw swatches
    and counts. Selection goes through the shared Names panel source guard.

Why this design:
    Colour groups can identify a work batch without requiring a persistent
    naming convention.

How to use:
    Run Names > Select by Mark. Pick one or more rows and press Select, or
    double-click a row. Enable Add to the current selection when the old
    selection must remain.

Benefit:
    Turn existing mark colours into a Font-window selection while keeping the
    stored marks unchanged.

Run **Names > Select by Mark** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `917a1b23e4f71791d0ed508c91470c1bfb9fd42549440070d32395d70916e8f8`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Names/Select%20by%20Mark.py)
