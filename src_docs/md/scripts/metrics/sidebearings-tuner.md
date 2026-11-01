---
this_file: src_docs/md/scripts/metrics/sidebearings-tuner.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Sidebearings Tuner

Set, add to or scale the sidebearings of the selected glyphs.

What it does: changes the left sidebearing (LSB), the right sidebearing (RSB)
or both, on the current master or on all masters. "Add" adds a value to each
side; a negative value tightens. "Set to" gives each side a value. "Scale %"
multiplies each side by a percentage.

How it works: the sidebearings are read from the outline edges in whole units.
The new value of each ticked side is computed in whole units; a half unit
rounds up. An unticked side keeps its value. The outline moves in place by the
LSB change (anchors move with it) and the advance width becomes LSB + outline
width + RSB. A layer without outline is listed and skipped. A change that gives
a negative width is refused for that layer.

Why: spacing passes often need the same correction on many glyphs and in every
master, for example "+5 on both sides" or "RSB 40 on all round letters".

How to use: select glyphs in the Font window. Choose the operation. Tick the
sides to change and type their values. Choose the current master or all
masters. Check the table. Press Apply. The panel stays open. Press "Use
selection" to read the Font window selection again. The panel opens on "Add"
with 0, so the first preview changes nothing. Switching to "Scale %" turns a
value of 0 into 100 %, which also changes nothing; leaving "Scale %" turns
only that untouched 100 back into 0. A value that you typed is kept.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and
never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs anyway" to go
on. Apply discloses queued ids and their possible date changes. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: exact sidebearing corrections on many glyphs and masters in one step,
with a preview.

Credit: adapted from metrics_sidebearings_tuner.py, the author's own FontLab
sample, Apache-2.0.

Run **Metrics > Sidebearings Tuner** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/17a93adb15fdfb1e47e3e1f8bff1a4c0e27da5885f2f7d39d31669d19491a171.py)
<!--/codeinclude-->
