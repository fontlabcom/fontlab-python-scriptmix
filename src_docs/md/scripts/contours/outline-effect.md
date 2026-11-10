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
    step through the shared module fly.ap.core.history.glyphs: each old contour element is
    removed and the ring is added as one new element. Images and empty
    elements stay in the layer. After the write it
    counts the contours again and reports any difference. The path-to-contour
    step and the panel are shared (fly.ap.contours.copy,
    fly.ap.contours.selection.panel.model).

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
    - Apply discloses queued ids and their possible date changes. The script
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

## Source identity

SHA256: `15373391084f19e1f6851cc63d60d3dc8a496e2f75ec177ca7fc423318fc1a8a`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Contours/Outline%20Effect.py)
