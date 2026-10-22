---
this_file: src_docs/md/scripts/anchors/cloud-view.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Cloud View

Overlay the selected glyphs faintly and show every anchor of one name as a cloud of dots, per master.

What it does:
    A tight cloud means marks will sit consistently; a stray dot is a glyph whose anchor
    is off. Hover-free and read-only: the list under each panel gives the extreme values.
    Nothing in the font is changed.

How it works:
    Read anchors of the chosen name from selected glyphs, grouped by master.
    Overlay faint glyph paths and plot positions with their extreme values.

Why this design:
    A cloud reveals a stray anchor position that can be difficult to see by
    opening glyphs one at a time.

How to use:
    Select glyphs in the Font window, run Anchors > Cloud View and choose an
    anchor name. Compare the master panels and the position ranges below them.

Benefit:
    Find candidates for anchor correction while retaining all stored anchor
    coordinates.

Run **Anchors > Cloud View** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ffc9c1f3171984b714df6033b8626daf0e8aa97d0efb19aa88680a3ac7ccd012.py)
<!--/codeinclude-->
