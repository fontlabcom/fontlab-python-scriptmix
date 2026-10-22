---
this_file: src_docs/md/scripts/contours/autohint-selected-layers.md
tags: ["Contours"]
categories: ["Contours"]
---

# Autohint Selected Layers

Run FontLab's PostScript autohinter on the selected glyphs, in one or all masters.

What it does:
    For each selected glyph and chosen master, the script runs FontLab's own
    autohinter on the layer. It works from the font's hinting settings
    (alignment zones and standard stems). The table shows the horizontal and
    vertical hint counts before and after. FontLab's source does not touch
    TrueType instructions here.

How it works:
    A non-modal panel lists every glyph and master with its hint counts, or
    the reason why the layer is skipped. Apply reads the font again and
    calls the native flLayer.autohint() on every planned layer, all in one
    Undo step through the shared module fly.ap.history. Read-back reports
    a layer that has an outline but no PostScript hints after the call. The
    hint counts and the panel are shared (fly.ap.hints, fly.ap.selection_panel).

Native call caveat:
    FontLab's source shows that autohint switches the package master temporarily,
    writes hinting options and stored hinting data, and can attach hints as
    node links. These effects extend beyond the notified layers; the script
    does not check them. TrueType instructions are separate.

Why this design:
    - The hints come from FontLab's own autohinter, not from a script
      algorithm.
    - The script adds what the menu command does not: every master in one
      step, a count of hints before and after, and one Undo step.
    - Automatic layers and glyphs with automatic layers are never edited. A
      base of automatic composites is skipped unless you tick "Edit bases of
      auto glyphs anyway": the change notification makes FontLab rebuild
      those composites, which can drop their anchors and locks, and Undo
      does not restore them. Locked layers and layers without contours are
      skipped.
    - Apply is refused while FontLab has pending glyph updates. The script
      does not call UpdateAll (fl#8537).

How to use:
    Set the alignment zones and standard stems in Font Info first. Select
    glyphs in the Font window. Run the script. Choose the current master or
    all masters, check the table and press Autohint. Each Apply is recorded
    as one Undo step.

Benefit:
    A whole selection gets fresh PostScript hints in every master, with the
    counts in view, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (hints_autohint.py, "Autohint Selected Layers").

Run **Contours > Autohint Selected Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d5c722f0e7bc3aaaf7127594f9b539c3ad746546eeade07d6c05ead1feb49528.py)
<!--/codeinclude-->
