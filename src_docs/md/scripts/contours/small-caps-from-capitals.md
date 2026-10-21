---
this_file: src_docs/md/scripts/contours/small-caps-from-capitals.md
tags: ["Contours"]
categories: ["Contours"]
---

# Small Caps From Capitals

Create small-cap glyphs (h.sc, a.sc, ...) from the selected capitals.

What it does:
    For each selected capital the script creates a small-cap glyph on every
    master: H becomes h.sc, H.ss01 becomes h.sc.ss01. The outline is scaled
    by separate horizontal and vertical factors; the advance width is scaled
    horizontally. The capitals do not change.

How it works:
    A non-modal panel lists every selected glyph with its new name, or the
    reason why it is skipped. Create checks the font again. FontLab's own
    Add Glyph command makes each new glyph with its master layers and widths
    (rounded half up). Then one step through the shared module
    fly.ap.history adds the scaled copies to all new layers. The copy keeps
    node names and raw node flags, which a FontLab contour copy can drop
    (fl#8569). After the write the script reads every new layer back, and
    checks that no automatic glyph of the font changed. The creation, the
    contour copy and the panel are shared (fly.ap.glyph_copies,
    fly.ap.contour_copy).

Copy limits:
    Anchors are not copied. Add the required anchors to the new glyphs before
    building accented composites.
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - The name is the lowercase base plus ".sc", the usual naming for the
      smcp and c2sc features.
    - A larger horizontal than vertical factor keeps vertical stems
      relatively heavier, so the small caps do not look too light at once.
      The result is a starting point for drawing, not finished small caps.
    - A capital needs a layer with contours on every master, with no
      components and no automatic layer. Otherwise it is listed and skipped,
      so the new glyphs stay compatible across masters. Accented capitals
      are usually components: build their small caps from the new bases.
    - A target name that exists is never overwritten. Create is refused
      while FontLab has pending glyph updates. The script does not call
      UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names carry the
      new suffix (such as eacute.sc), the row shows "may rebuild auto ..."
      and is skipped unless you tick "Create even if FontLab may rebuild
      these auto glyphs". Use selection clears the tick.
    - Each new glyph is recorded as its own Undo step, and the outlines as
      one more Undo step.

How to use:
    Select capitals in the Font window. Run the script. Set the horizontal
    and vertical scale, check the table and press Create.

Benefit:
    A compatible set of small caps to refine, in every master, in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_small_caps.py, "Small Caps from Capitals").

Run **Contours > Small Caps From Capitals** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/cc2b7a13e8eafaec227c56c596f3cc95892abd80ab1bfd9a8d0f5551459ce762.py)
<!--/codeinclude-->
