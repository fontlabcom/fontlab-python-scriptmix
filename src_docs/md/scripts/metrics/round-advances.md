---
this_file: src_docs/md/scripts/metrics/round-advances.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Round Advances

Round advance widths to a step. Outlines stay where they are.

What it does: rounds the advance width of each target glyph to a multiple of
the step (2 to 100 units). Choose the nearest multiple, the next one up, or the
next one down. A half step goes up for "nearest".

How it works: the right sidebearing takes the whole change. The left
sidebearing, the outline and the anchors do not move. The table lists only the
layers that change. Each Apply plans again from the live font.

Why: interpolation and scaling leave fractional or odd advances. A rounded
advance keeps the spacing on a clean grid. The left edge that you already set
stays fixed.

How to use: select glyphs in the Font window, or choose all glyphs. Choose the
current master or all masters. Set the step. Check the table. Press Apply. The
panel stays open. Press "Use selection" to read the Font window selection
again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited.
Layers with a metrics link or expression are listed and skipped. A base of
auto glyphs is refused, because FontLab rebuilds the auto glyphs and may lose
their anchors and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs
anyway" to go on. After the write the script reads advance and outline back
and reports any mismatch. It does not call UpdateAll (FontLab issue 8537).
Native Undo/Redo/reopen is pending.

Benefit: a whole font or a master gets tidy advances in one step.

Credit: independent rewrite of the author's own rescued FontLab sample
metrics_round_advances.py (Apache-2.0).

Run **Metrics > Round Advances** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/44e40e55015f7e0f31f9f939592cec25a7c344e5c8c6d1aa7007b812c204b400.py)
<!--/codeinclude-->
