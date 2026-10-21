---
this_file: src_docs/md/scripts/anchors/snap-to-metrics.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Snap To Metrics

Move named anchors vertically onto a font metric, plus an offset.

What: Sets the y value of the named anchors to baseline, x-height, cap height,
ascender or descender, plus an offset. The x value stays as stored.

How: Each master uses its own metric. A Bold with a taller x-height gets its
own anchor height. The panel shows the metric of every chosen master.

Why: Anchor heights follow the design instead of a number typed once. The
script reads the metric of a master without switching to that master.

Use: Select glyphs. Run the script. Type the anchor names. Choose the metric
and the offset. Check the table. Press Snap.

Benefit: Top and bottom anchors line up across glyphs and masters in one step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The one-step write, the automatic-layer rule
and the pending-update check are shared with other scripts (fly.ap.history,
fly.ap.edit_guards); the planner and the panel belong to this script.

Source: the author's own FontLab sample
anchors_snap_to_metrics.py, Apache-2.0.
Independent rewrite for the current FontLab 9 API.

Run **Anchors > Snap To Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9c0fe26475f0716f249b227e01cade82520e7e5e23e91a56cd7fdf33353487c0.py)
<!--/codeinclude-->
