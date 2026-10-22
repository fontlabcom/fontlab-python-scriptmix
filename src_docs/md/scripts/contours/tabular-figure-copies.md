---
this_file: src_docs/md/scripts/contours/tabular-figure-copies.md
tags: ["Contours"]
categories: ["Contours"]
---

# Tabular Figure Copies

Create tabular (.tf) copies of the selected figures, with one shared width per
master.

What it does:
    For each selected figure (zero to nine, also with a suffix such as
    one.osf) the script creates a new glyph with ".tf" added to the name, on
    every master. In each master all new glyphs get one advance width: the
    widest selected figure of that master plus an extra amount. The figure
    outline is copied and centred in that width. The source figures do not
    change.

How it works:
    A non-modal panel lists every selected glyph with its new name, or the
    reason why it is skipped. Create checks the font again. FontLab's own
    Add Glyph command makes each new glyph with its master layers and the
    shared widths. Then one step through the shared module fly.ap.history
    adds the centred copies to all new layers. The centring keeps the
    outline on whole units; an odd unit of white space goes to the right
    side. The copy keeps node names and raw node flags, which a FontLab
    contour copy can drop (fl#8569). After the write the script reads every
    new layer back, and checks that no automatic glyph of the font changed.
    The creation, the contour copy and the panel are shared
    (fly.ap.glyph_copies, fly.ap.contour_copy).

Copy limits:
    Anchors are not copied. Add the required anchors to the new glyphs before
    building accented composites.
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - New glyphs, not changed figures: proportional and tabular figures can
      then live side by side, as the OpenType tnum feature expects. To make
      the existing figures tabular in place, use Metrics > Tabular Width.
    - A figure needs a layer with contours on every master, with no
      components and no automatic layer. Otherwise the figure is listed and
      skipped, so the new glyphs stay compatible across masters.
    - A target name that exists is never overwritten.
    - Create discloses queued ids and their possible date changes. The script
      does not call UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names carry the
      new suffix, the row shows "may rebuild auto ..." and is skipped unless
      you tick "Create even if FontLab may rebuild these auto glyphs". Use
      selection clears the tick.
    - Each new glyph is recorded as its own Undo step, and the outlines as
      one more Undo step.

How to use:
    Select the figures in the Font window. Run the script. Set the extra
    width, check the table and press Create. Narrow figures such as one can
    then need redrawing in their wider space.

Benefit:
    A complete, compatible set of tabular figures to refine, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_tabular_copies.py, "Tabular Figure Copies").

Run **Contours > Tabular Figure Copies** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/70daeec319fa71e210a609881da85239977f59430c187a6ff0edea39f483226b.py)
<!--/codeinclude-->
