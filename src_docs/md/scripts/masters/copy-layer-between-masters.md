---
this_file: src_docs/md/scripts/masters/copy-layer-between-masters.md
tags: ["Masters"]
categories: ["Masters"]
---

# Copy Layer Between Masters

Copy the outline, anchors and advance width from one master to others.

What it does:
    For each selected glyph, replace the contours of the target master
    layers with copies of the contours of the source master layer.
    Optionally move same-named anchors to the source positions and set the
    source advance width. Components of the targets stay; components of
    the source are not copied.

How it works:
    A non-modal panel has a "From" master, a "To" choice (all other masters
    or one master), and two options: Anchors and Advance width. The table
    shows, per target layer, contours now and after, width now and after.
    Copy reads the font again and writes every target in one Undo step
    through the shared module fly.ap.history. The old outline shapes of a
    target are removed (empty ones too) and repaired clones of the source
    outline shapes are added. After the write the script reads contour
    counts, widths and anchor positions back and reports any difference.

Why this design:
    - The target loses its outline shapes, it never edits them. A shape that
      other glyphs share stays intact for them.
    - FontLab clone() drops shape notes and names and the raw state and name
      of nodes (fl#8516, fl#8538). The script copies them back, clears
      selection bits, and stops when a clone has another contour count.
    - Only same-named anchors move; missing anchors are listed, never added.
      Two anchors with one name make the layer ambiguous: it is skipped. An
      existing anchor that would move to 0, 0 is skipped too: FontLab does
      not Redo that move (fl#8527).
    - Skipped and listed: automatic layers, glyphs with automatic layers,
      bases of automatic composites (also through manual composites),
      locked layers, layers with a metrics link or expression, and a source
      without outline. Apply is refused while FontLab has pending glyph
      updates. The panel binds to the font that was current when it opened.

How to use:
    Select glyphs in the Font window. Run the script. Pick the source master
    and the targets. Check the table. Press Copy. Then check the masters for
    compatibility: the targets now have the point structure of the source.

Benefit:
    Start the outlines of a new master from an existing one, or resync the
    outlines of a broken master, in
    one step and one Undo.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (masters_copy_layer.py, "Copy Layer Between Masters").
    Known limit: node.clone loses explicit corner smoothness and other
    scalar node properties (fl#8569); a shape clone may lose them too.

Run **Masters > Copy Layer Between Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7cc747978719a26e7af9c71143d4cd51db8ef07dbaded367ef018c0a5566373a.py)
<!--/codeinclude-->
