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

Safety: each Apply is recorded as one Undo step. Auto layers are listed and
never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). This includes a base that reaches an auto
glyph through other composites. Tick "Edit bases of auto glyphs anyway" to go
on. Apply discloses queued ids and their possible date changes. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: open or tighten the spacing of many glyphs in one step. The
balance of each glyph is kept.

Credit: adapted from the author's own rescued FontLab sample
metrics_scale_advances.py (Apache-2.0).

Run **Metrics > Scale Advances** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9fc0523887ce763a409b4c820a2762690a7d03cea9336cfdcd82481043817d17.py)
<!--/codeinclude-->
