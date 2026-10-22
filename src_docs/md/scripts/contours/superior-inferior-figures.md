---
this_file: src_docs/md/scripts/contours/superior-inferior-figures.md
tags: ["Contours"]
categories: ["Contours"]
---

# Superior & Inferior Figures

Create superior (.sups) or inferior (.subs) copies of the selected figures.

What it does:
    For each selected figure (zero to nine, also with a suffix) the script
    creates a new glyph with ".sups" or ".subs" added to the name, on every
    master. The outline is scaled by one factor and moved up or down; the
    advance width is scaled by the same factor. The source figures do not
    change.

How it works:
    A non-modal panel lists every selected glyph with its new name, or the
    reason why it is skipped. Choose Superior or Inferior: the vertical shift
    takes the usual preset (350 or -150 units), which you can change. Create
    checks the font again. FontLab's own Add Glyph command makes each new
    glyph with its master layers and widths (rounded half up). Then one step
    through the shared module fly.ap.history adds the scaled copies to all
    new layers. The copy keeps node names and raw node flags, which a
    FontLab contour copy can drop (fl#8569). After the write the script
    reads every new layer back, and checks that no automatic glyph of the
    font changed. The creation, the contour copy and the panel are shared
    (fly.ap.glyph_copies, fly.ap.contour_copy).

Copy limits:
    Anchors are not copied. Add the required anchors to the new glyphs before
    building accented composites.
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - Scaling about the baseline origin, then one vertical shift, keeps all
      new figures on one common baseline, as the sups and subs features
      expect.
    - Scaled figures come out lighter than the originals. The result is a
      starting point for drawing, not finished superiors.
    - A figure needs a layer with contours on every master, with no
      components and no automatic layer. Otherwise the figure is listed and
      skipped, so the new glyphs stay compatible across masters.
    - A target name that exists is never overwritten. Create discloses queued
      ids and their possible date changes. The script does not call
      UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names carry the
      new suffix, the row shows "may rebuild auto ..." and is skipped unless
      you tick "Create even if FontLab may rebuild these auto glyphs". Use
      selection clears the tick.
    - Each new glyph is recorded as its own Undo step, and the outlines as
      one more Undo step.

How to use:
    Select the figures in the Font window. Run the script. Choose Superior or
    Inferior, set the scale and the shift, check the table and press Create.

Benefit:
    A compatible set of superior or inferior figures to refine, in every
    master, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_superiors.py, "Superior & Inferior Figures").

Run **Contours > Superior & Inferior Figures** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/08c5bfa009f53b847cd39283d2322eb04a6df63af7d80f0cfa614c3553b59fe2.py)
<!--/codeinclude-->
