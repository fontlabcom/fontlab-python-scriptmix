---
this_file: src_docs/md/scripts/metrics/scale-advances.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Scale Advances

Scale advance widths by a percentage. Each outline stays centred.

What it does: multiplies the advance width of each selected glyph by a
percentage (10 to 400 percent). The new width is a whole number of units.

How it works: the change in width is split between both sidebearings. The
outline moves by half of the change. The right sidebearing takes the odd unit.
Anchors move with the outline. The table lists the old width, the new width and
the shift for each layer.

Why: loosening a Bold master or tightening a Display master is a common job.
Splitting the change keeps the balance of every glyph. A plain scale of the
advance alone would push the ink to one side.

How to use: select glyphs in the Font window. Choose the current master or all
masters. Enter the percentage. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited.
Layers with a metrics link or expression are listed and skipped. A base of
auto glyphs is refused, because FontLab rebuilds the auto glyphs and may lose
their anchors and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs
anyway" to go on. After the write the script reads advance and outline back
and reports any mismatch. It does not call UpdateAll (FontLab issue 8537).
Native Undo/Redo/reopen of in-place moves is pending.

Benefit: open or tighten the spacing of many glyphs in one step. The
balance of each glyph is kept.

Credit: independent rewrite of the author's own rescued FontLab sample
metrics_scale_advances.py (Apache-2.0).

Run **Metrics > Scale Advances** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bbef3d5a5b321fdf22170c692ec5f0a87bca753a3384d2a53a27c4e2481b4c56.py)
<!--/codeinclude-->
