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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/af0008b903366da7f3131f6daa35d3c8b4d69a78558094f406408523c06a44dd.py)
<!--/codeinclude-->
