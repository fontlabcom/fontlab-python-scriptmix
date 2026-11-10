---
this_file: src_docs/md/scripts/contours/remove-postscript-hints.md
tags: ["Contours"]
categories: ["Contours"]
---

# Remove PostScript Hints

Remove PostScript stem hints from the selected glyphs, horizontal and/or
vertical.

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
    layer, all in one Undo step through the shared module fly.ap.core.history.glyphs.
    After the write it counts the hints again and reports any layer that
    still has hints in a chosen direction. The hint counts and the panel are
    shared (fly.ap.hints.postscript, fly.ap.contours.selection.panel.model).

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
    - Apply discloses queued ids and their possible date changes. The script
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

## Source identity

SHA256: `e92210f7977e3625b41ab274c00e131a6046ec377c824c179d413b5cd9e13ce4`

[Python source at `1e4c2b2dd9bc`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1e4c2b2dd9bccfd04b38e70ed3dcaaa52242835d/Scripts/Contours/Remove%20PostScript%20Hints.py)
