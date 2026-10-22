---
this_file: src_docs/md/scripts/metrics/centre-in-advance.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Centre In Advance

Centre the outline of each selected glyph in its advance width.

What it does: moves the outline so that both sidebearings are equal. You can
also give the glyph a new advance width at the same time: keep it, set it, or
change it by an amount.

How it works: the white space is the new width minus the width of the ink.
The left sidebearing is half of it, in whole units. The right sidebearing
takes the odd unit. Anchors move with the outline. A glyph without outline is
listed and skipped. A negative new width is refused for that layer.

Why: symbols, figures, spaces with marks and accents must sit in the middle
of their box. Doing it by hand is slow and error prone.

How to use: select glyphs in the Font window. Choose the width mode and the
value. Choose the current master or all masters. Check the table. Press Apply.
The panel stays open. Press "Use selection" to read the Font window selection
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
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: exact centring in all masters in one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_center_in_advance.py (Apache-2.0).

Run **Metrics > Centre In Advance** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/43172cefe3e5a46a3e87b40a5576d536d642263bb88a887cda0fc4bcc79fa58b.py)
<!--/codeinclude-->
