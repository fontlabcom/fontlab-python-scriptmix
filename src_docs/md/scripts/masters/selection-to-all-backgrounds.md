---
this_file: src_docs/md/scripts/masters/selection-to-all-backgrounds.md
tags: ["Masters"]
categories: ["Masters"]
---

# Selection To All Backgrounds

Copy the selected contours into the background of every glyph.

What it does:
    Take the selected contours of the shown glyph layer. Replace the background
    (mask layer) of the current-master layer of EVERY glyph in the font with
    copies of them. Use it to put one guide shape, such as a grid or a
    reference
    skeleton, behind all glyphs.

How it works:
    A contour counts as selected when all its nodes are selected (select a
    contour with a double click, or drag a box around it). A panel first
    shows what will happen: contour count, glyph count, backgrounds to be
    replaced and glyphs to be skipped. "Replace backgrounds" checks again that
    nothing changed, then removes the old background shapes, creates missing
    backgrounds, and adds clones of the selected contours. One notification
    covers
    the whole font: one Undo step. The shared module fly.ap.history decides
    which glyphs are skipped and does the one-step write. Read-back checks
    every target background for the planned contour count and no components.
    A mismatch is reported with the Edit > Undo hint.

Why this design:
    - The change spans the whole font and overwrites backgrounds. So there is a
      preview and an explicit button; there is no silent run.
    - The panel works only on the current master. Other masters keep their
      backgrounds.
    - Glyphs with an automatic layer, glyphs that are a base of one (also
      through manual composites), glyphs with a locked master layer and glyphs
      without a layer for the current master are skipped and counted. An
      automatic layer must never be notified: it would rebuild every automatic
      glyph. In a font with many recipes, most base letters are skipped.
    - FontLab clone() drops shape notes and names and the raw state and name of
      nodes. The script copies them back, except selection bits.
    - Only contours move. Components in the selection are not copied.

How to use:
    Open a Glyph window. Select the contours. Run the script. Read the summary.
    Click "Replace backgrounds". Use Edit > Undo to revert.

Benefit:
    One reference shape behind the whole font in one step.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Selection to all the
    backgrounds" (Apache-2.0). Independent rewrite. No source code was copied.
    Known limit: clone() recalculates smooth flags (fl#8516); the script
    restores node states.

Run **Masters > Selection To All Backgrounds** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/32e438fe8cb8e3ab6dcce174ddd6c9ccf74e0643a6bfb8a83aa77a46d0fd4d82.py)
<!--/codeinclude-->
