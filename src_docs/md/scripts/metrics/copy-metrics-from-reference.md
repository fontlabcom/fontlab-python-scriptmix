---
this_file: src_docs/md/scripts/metrics/copy-metrics-from-reference.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Copy Metrics From Reference

Give the selected glyphs the sidebearings or the advance width of a reference glyph.

What it does: copies the metrics of one reference glyph to the selected glyphs,
on the current master or on all masters. Four modes are available: "LSB and
RSB", "LSB only", "RSB only" and "Advance width (centred)". An optional offset
is added to each copied value.

How it works: each master takes the reference values of the same master, so a
multi-master family keeps its progression. Sidebearings are read from the
outline edges in whole units. In the sidebearing modes the outline moves in
place by the LSB change (anchors move with it) and the advance width becomes
LSB + outline width + RSB. In "Advance width (centred)" the advance becomes
the reference advance plus the offset; the change is shared by both sides, and
the right side takes the odd unit. The reference glyph itself is never edited.
A master without a reference layer, a reference without outline (sidebearing
modes) and a layer without outline are listed and skipped. A result with a
negative width is refused for that layer.

Why: related glyphs share their spacing: n, m, h and u take the sidebearings of
n; H, I and N take those of H; figures take one tabular width. Copying values by
hand in every master is slow and error prone.

How to use: select the glyphs to change in the Font window. Type the reference
glyph name; the completer lists the glyphs of the font. Choose the mode, the
offset and the current master or all masters. Check the table. Press Apply. The
panel stays open. Press "Use selection" to read the Font window selection and
the glyph list again.

Safety: each Apply is recorded as one Undo step. Auto layers are listed and never edited. A
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
maths, its planner and its controls.

Benefit: consistent spacing groups in all masters in one step, with a preview.

Credit: adapted from metrics_copy_from_reference.py, the author's own FontLab
sample, Apache-2.0.

Run **Metrics > Copy Metrics From Reference** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/212ab42d323539a1c1c811baf328a5dd18599098e4800bc858a39caa10bb786e.py)
<!--/codeinclude-->
