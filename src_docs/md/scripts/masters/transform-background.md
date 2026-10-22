---
this_file: src_docs/md/scripts/masters/transform-background.md
tags: ["Masters"]
categories: ["Masters"]
---

# Transform Background

Scale or shift the background of the selected glyph layers.

What it does:
    Open a small floating panel with two actions. "Scale" multiplies the
    background of every selected glyph layer by a percentage, around the origin
    (0, 0). "Shift" moves the background horizontally by a number of units.
    Positive units move right, negative units move left.

How it works:
    The background of a FontLab layer is its mask layer. The script finds it
    with getMaskLayer(False), so it never creates a background. Layers without
    one are skipped. It then applies one transform to the mask layer: contours,
    components and anchors move together. Metrics and guides of the mask stay.
    FontLab rounds the result as set in the preferences. One notification
    covers
    all backgrounds: one Undo step per click.

Why this design:
    - One panel replaces the two Glyphs scripts. It stays open, so you can
      scale, shift and repeat while you compare with the foreground.
    - The Glyphs scripts read a number from a text box once per run and close.
      They break on invalid input. This panel checks the number and shows the
      reason in the status line.
    - The Glyphs scale script ignores components. This script moves them too.
    - A glyph that has an automatic layer, or is a base of one (also through
      manual composites), is refused: FontLab cannot undo an edit that reaches
      an automatic layer. So is a click while FontLab has pending glyph
      updates. The shared module fly.ap.history does these checks and the
      one-step write.
    - Zero, negative, empty and non-finite scale values are refused. A scale of
      0 would destroy the background; a negative scale would mirror it.

How to use:
    Select glyphs in the Font window, or open a Glyph window. Type a number.
    Press Return or click the button. Use Edit > Undo to revert.

Benefit:
    Fit a traced or imported background to your drawing without redrawing it.

Credit:
    Behaviour after Pedro Arilla's Glyphs scripts "Scale background in selected
    glyphs" and "Shift background in selected glyphs" (Apache-2.0). Independent
    rewrite. No source code was copied.

Run **Masters > Transform Background** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/f4b0b7028ce3f29b6a294f1b61a13e99b64d280945147356ba9bfc1c97f46bca.py)
<!--/codeinclude-->
