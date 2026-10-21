---
this_file: src_docs/md/scripts/anchors/round-to-grid.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Round To Grid

Round anchor positions to a grid step.

What: Moves anchors to the nearest multiple of a grid step. Halves round up:
15 becomes 20 and -15 becomes -10 for step 10. You choose the step, the
axes and, if you want, the anchor names.

How: The table lists each anchor that moves. A fractional position moves too,
even for step 1. Name, style and expressions of the anchors stay.

Why: A grid step is a simple, predictable rule. It keeps all marks on one
lattice, so values are easy to compare and to edit by hand.

Use: Select glyphs. Run the script. Set the step and the axes. Leave the names
empty for all anchors. Check the table. Press Round.

Benefit: Clean anchor values in all masters, in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph is the base of an automatic composite (FontLab rebuilds the
  composite and Undo does not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font.

Source: the author's own FontLab sample
anchors_round_to_grid.py, Apache-2.0.
Independent rewrite for the current FontLab 9 API.

Run **Anchors > Round To Grid** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c13e524b66cc2e95e81d6b6efdf3d875603922346a182174a9332e8464ff6d51.py)
<!--/codeinclude-->
