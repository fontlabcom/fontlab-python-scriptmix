---
this_file: src_docs/md/scripts/metrics/tabular-width.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Tabular Width

Give figures one shared advance width. Each outline is centred.

What it does: sets the same advance width on a group of glyphs and centres
every outline in it. The group is the figures zero to nine, the figures with
currency signs, or the selected glyphs. The width is the widest glyph of the
group on each master, or a fixed value.

How it works: the table shows old width, new width, old and new left
sidebearing. The widest width is found for each master separately. The white
space is split in two; the right sidebearing takes an odd unit. A glyph without
outline is listed and skipped. Anchors move with the outline.

Why: tabular figures line up in columns of numbers. This script does the
spacing half of that job. The preset groups use the plain names zero to nine.
For figures with suffix names, such as one.tf, select them and use "Selected
glyphs".

How to use: choose the group. Choose "Widest in set" or enter a fixed width.
Choose the current master or all masters. Check the table. Press Apply. The
panel stays open. Press "Use selection" to read the Font window selection
again.

Safety: one Apply is one Undo step. Auto layers are listed and never edited. A
glyph that owns an auto layer is listed and skipped as a whole. Layers with a
metrics link or expression are listed and skipped. A base of auto glyphs is
refused, because FontLab rebuilds the auto glyphs and may lose their anchors
and locks (FontLab issue 8512). This includes a base that reaches an auto
glyph through other composites. Tick "Edit bases of auto glyphs anyway" to go
on. Apply is refused while FontLab has pending glyph updates. After the write
the script reads advance and outline back and reports any mismatch. A failure
after the write started says so and asks you to use Edit > Undo. It does not
call UpdateAll (FontLab issue 8537). Native Undo/Redo/reopen of in-place moves
is pending.

Shared parts: the panel, the plan model, the one-step write and the read-back
come from the App module fly.ap.metrics_panel. This script holds its own
maths, its planner and its controls.

Benefit: columns of figures align in every master after one step.

Credit: adapted from the author's own rescued FontLab sample
metrics_tabular_width.py (Apache-2.0).

Run **Metrics > Tabular Width** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1fa694eef6bdb79b421622879be2b8669ca496af56f0a06ec0dec96b6fdfa5b0.py)
<!--/codeinclude-->
