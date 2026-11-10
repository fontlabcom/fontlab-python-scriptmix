---
this_file: src_docs/md/scripts/metrics/round-advances.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Round Advances

Round advance widths to a step. Outlines stay where they are.

What it does: rounds the advance width of each target glyph to a multiple of
the step (1 to 100 units). Choose the nearest multiple, the next one up, or the
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
come from the App module fly.ap.metrics.panel.model. This script holds its own
maths, its planner and its controls.

Benefit: a whole font or a master gets tidy advances in one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_round_advances.py (Apache-2.0).

Run **Metrics > Round Advances** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `9b7e790969514bc1c5075e79f3bd10cd6fb5d6be3cc90b610a845b4a2651a7e8`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Metrics/Round%20Advances.py)
