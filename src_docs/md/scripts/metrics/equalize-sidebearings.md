---
this_file: src_docs/md/scripts/metrics/equalize-sidebearings.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Equalize Sidebearings

Make the left and right sidebearings of each selected glyph equal.

What it does: gives both sidebearings the same value, on the current master or
on all masters. Five rules are available. "Average of both" keeps the advance
width and splits the white space. "Both = LSB", "Both = RSB", "Both = the
smaller" and "Both = the larger" copy one value to the other side, so the
advance width changes.

How it works: the sidebearings are read from the outline edges in whole units.
For "Average of both", the left side gets half of the white space, rounded
down; the right side takes the odd unit. The outline moves in place (anchors
move with it) and the advance gets the new width. A layer without outline is
listed and skipped. A rule that gives a negative width is refused for that
layer.

Why: symmetric letters such as O, H, o and n, and many symbols, start with equal
sidebearings. Setting both sides by hand in each master is slow and error prone.

How to use: select glyphs in the Font window. Choose the rule. Choose the
current master or all masters. Check the table. Press Apply. The panel stays
open. Press "Use selection" to read the Font window selection again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). Tick "Edit bases of auto glyphs anyway" to go
on. Apply is refused while FontLab has pending glyph updates. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537).

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
rules, its planner and its controls.

Benefit: symmetric spacing in all masters in one step, with a preview.

Credit: adapted from metrics_equalize_sidebearings.py, the author's own
FontLab sample, Apache-2.0.

Run **Metrics > Equalize Sidebearings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e8a377435c152ccccca56491ffecd8b1f646ef52eed6fdc9a1d7c0e8710f55ae.py)
<!--/codeinclude-->
