---
this_file: src_docs/md/scripts/contours/outline-effect.md
tags: ["Contours"]
categories: ["Contours"]
---

# Outline Effect

Turn the selected glyphs into outlined (hollow) letters of a chosen line width.

What it does:
    For each selected glyph and chosen master, the script replaces the
    contours of the layer with a ring of the chosen line width, centred on the
    old outline. The advance width does not change.

How it works:
    A non-modal panel lists every glyph and master with its contour count, or
    the reason why the layer is skipped. Apply first builds every ring: Qt's
    path stroker draws the contours with round joins and caps, the script
    turns the stroke into closed FontLab contours (cubic handles stay
    cubic), and FontGate's Remove Overlap cleans the small loops that the
    stroker leaves inside corners. Then it writes all layers in one Undo
    step through the shared module fly.ap.history: each old contour element is
    removed and the ring is added as one new element. Images and empty
    elements stay in the layer. After the write it
    counts the contours again and reports any difference. The path-to-contour
    step and the panel are shared (fly.ap.contour_copy, fly.ap.selection_panel).

Why this design:
    - FontLab has no Python call that strokes an outline, so the script uses
      the Qt stroker and FontLab's own overlap removal. FontGate puts the
      result on the integer grid.
    - The geometry is built before history starts, so a failed stroke never
      leaves a half-edited layer.
    - Layers with components are skipped: the components would stay filled.
      Locked layers are skipped too. Element names and notes of the old
      outline do not carry over to the ring.
    - Automatic layers and glyphs with automatic layers are never edited. A
      base of automatic composites is skipped unless you tick "Edit bases of
      auto glyphs anyway": FontLab then rebuilds those composites, can drop
      their anchors and locks, and Undo does not restore them.
    - Apply is refused while FontLab has pending glyph updates. The script
      does not call UpdateAll (fl#8537).

How to use:
    Select glyphs in the Font window. Run the script. Set the line width,
    choose the current master or all masters, check the table and press
    Outline. Each Apply is recorded as one Undo step.

Benefit:
    An inline or outline style starts from the real drawing, in every master,
    in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_outline_effect.py, "Outline Effect").

Run **Contours > Outline Effect** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5d9b76d2c2dc3e8a415c7082255a251a699fd9615787b491f8473ee31525370e.py)
<!--/codeinclude-->
