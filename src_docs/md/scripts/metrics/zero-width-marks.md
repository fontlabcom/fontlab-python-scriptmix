---
this_file: src_docs/md/scripts/metrics/zero-width-marks.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Zero-Width Marks

Set the advance width of combining marks to zero.

What it does: gives each selected combining mark an advance width of 0. A
combining mark is a glyph with a Unicode category of Mn or Me, or a name that
ends in "comb". Other glyphs are ignored unless you clear the filter.

How it works: you choose where the outline goes. "Keep" leaves the outline
in place. "Hang left" moves it left by the old width, so it sits over the
preceding glyph. "Centre" puts the middle of the ink on x = 0. Anchors move
with the outline.

Why: a combining mark must not move the pen. A mark with a width pushes the
base letter and the next letter apart. Marks that attach by anchor need
the zero width and a known place for the ink.

How to use: select the marks in the Font window. Choose the placement and the
masters. Check the table. Press Apply. The panel stays open. Press "Use
selection" to read the Font window selection again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited.
Layers with a metrics link or expression are listed and skipped. A base of
auto glyphs is refused, because FontLab rebuilds the auto glyphs and may lose
their anchors and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs
anyway" to go on. After the write the script reads advance and outline back
and reports any mismatch. It does not call UpdateAll (FontLab issue 8537).
Native Undo/Redo/reopen of in-place moves is pending.

Benefit: all marks in all masters get a correct zero width in one step.

Credit: independent rewrite of the author's own rescued FontLab sample
metrics_zero_width_marks.py (Apache-2.0).

Run **Metrics > Zero-Width Marks** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8f242ce282c5883edb8aa0b8f56bba4311b0f3e75be09b42f728b805904c5153.py)
<!--/codeinclude-->
