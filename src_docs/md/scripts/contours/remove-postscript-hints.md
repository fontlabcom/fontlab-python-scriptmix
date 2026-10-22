---
this_file: src_docs/md/scripts/contours/remove-postscript-hints.md
tags: ["Contours"]
categories: ["Contours"]
---

# Remove PostScript Hints

Remove PostScript stem hints from the selected glyphs, horizontal and/or vertical.

What it does:
    For each selected glyph and chosen master, the script removes the
    horizontal hints, the vertical hints or both from the layer. FontLab's
    source does not touch plain guidelines or TrueType instructions here. The
    table shows the hint counts before and after.

How it works:
    A non-modal panel lists every glyph and master with its hint counts, or
    the reason why the layer is skipped. A layer without hints in the chosen
    directions is listed and skipped. Apply reads the font again and calls
    the native flLayer.removeHints(horizontal, vertical) on every planned
    layer, all in one Undo step through the shared module fly.ap.history.
    After the write it counts the hints again and reports any layer that
    still has hints in a chosen direction. The hint counts and the panel are
    shared (fly.ap.hints, fly.ap.selection_panel).

Why this design:
    - The removal is FontLab's own call, so hints are removed exactly as the
      menu command removes them.
    - The script adds what the menu command does not: every master in one
      step, one direction only, the counts in view and one Undo step.
    - Automatic layers and glyphs with automatic layers are never edited. A
      base of automatic composites is skipped unless you tick "Edit bases of
      auto glyphs anyway": the change notification makes FontLab rebuild
      those composites, which can drop their anchors and locks, and Undo
      does not restore them. Locked layers are skipped.
    - Apply is refused while FontLab has pending glyph updates. The script
      does not call UpdateAll (fl#8537).

How to use:
    Select glyphs in the Font window. Run the script. Tick the directions,
    choose the current master or all masters, check the table and press
    Remove Hints. Each Apply is recorded as one Undo step.

Benefit:
    Clean hint-free layers before a new autohint pass or a TrueType-only
    export, in every master, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (hints_remove.py, "Remove PostScript Hints").

Run **Contours > Remove PostScript Hints** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ddd8b1de182672250649a8272e535f4f3353e7c8286a6b2ade24f65877ac7cdf.py)
<!--/codeinclude-->
