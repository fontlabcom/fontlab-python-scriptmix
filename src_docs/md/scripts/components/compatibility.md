---
this_file: src_docs/md/scripts/components/compatibility.md
tags: ["Components"]
categories: ["Components"]
---

# Compatibility

Compare component names and order across masters; glyphs that differ cannot interpolate their components.

What it does:
    One row per composite glyph, one column per master. Masters whose component list
    differs from the first master are shown in red, and mismatching glyphs are listed
    first. Double-click a row to select the glyph in the Font window. Nothing is changed.

How it works:
    Read ordered component base lists for each composite and master. Compare
    each list with the first master's list and display mismatching master
    cells in red.

Why this design:
    Matching component counts alone cannot show an order or base-name
    mismatch; explicit lists make that difference visible.

How to use:
    Run Components > Compatibility. Inspect the mismatches first and double-
    click a row to select its glyph in the Font window for manual review.

Benefit:
    Locate component-name and order differences without changing decomposition
    or master drawings.

Run **Components > Compatibility** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/597d05621e7f7716484f94bcd39fbf8b04e400a737a4d9366be7d0c42bdf644d.py)
<!--/codeinclude-->
