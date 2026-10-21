---
this_file: src_docs/md/scripts/contours/sansomatic.md
tags: ["Contours"]
categories: ["Contours"]
---

# Sansomatic

Construct geometric sans capitals in empty selected master layers.

What: Build A, E, F, H, I, L, N, O, S, T, V, X, Y and Z from explicit
height, width, vertical stroke, horizontal stroke and side space dimensions.
How: Compose rectangles, diagonal strips, an elliptical ring or a cubic S.
Union the filled pieces with Qt, then use the shared contour converter and
outline writer. Existing outlines, components, locked layers and linked metrics
are kept and named in the preview. No glyph or layer is created.
Why: FontLab's Rectangle and Ellipse tools draw individual pieces. This panel
constructs complete letter skeletons across selected glyphs and masters. Explicit
dimensions replace the Glyphs Dimension palette; no host callbacks are installed.
Use: Select empty capital glyphs in the Font window. Set the five dimensions,
inspect the non-modal preview and choose current or all masters. Press Build.
To give each master its own dimensions, untick Keep masters compatible, choose
Current master, and set that master's dimensions before Build.
Each changing action is recorded as one Undo step. Clear an outline with native
FontLab tools before building that glyph again. Unsupported capitals are kept.
Benefit: Start a consistent geometric alphabet without overwriting existing work.
Diagonal ends are horizontal at the baseline and cap height. S spans both levels.
The common dimensions are a construction model; per-letter source sliders and
the source's continuous destructive redraw are replaced by explicit Build.

Independent behaviour rewrite after Simon Cozens, Sansomatic.py, MIT.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.

Run **Contours > Sansomatic** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/55748f9f4f5f4b01fe342eb46af154ab6851dded9098acd550cf0e122faf38ad.py)
<!--/codeinclude-->
