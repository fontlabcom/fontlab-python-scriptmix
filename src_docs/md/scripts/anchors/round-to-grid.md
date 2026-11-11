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
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
The edit is recorded as one Undo step. The plan, the safety checks, the
one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchors.writer, fly.ap.anchors.panel.model); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_round_to_grid.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Round To Grid** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d4d3a6448900e471ec5a905a96338c0c6fd2d491693cbb5315fb2366f0b1a39c`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Anchors/Round%20To%20Grid.py)
