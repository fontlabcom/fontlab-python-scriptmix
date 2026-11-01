---
this_file: src_docs/md/scripts/contours/correct-contour-direction.md
tags: ["Contours"]
categories: ["Contours"]
---

# Correct Contour Direction

Set the contour direction of the selected glyphs: outer and inner contours.

What: For each selected glyph and master, the table lists every closed
contour that runs the wrong way, with its current direction. Correct
reverses them.

How: Native flContour.clockwise gives the direction; contains tests all
segment start and mid points, as FontLab's own direction command does.
Nesting within the same shape decides each edit. If layer-wide nesting would
give a different answer, the contour is listed as "inside another shape,
direction left" and kept. Overlapping outer contours stay outer. Native
segments include TrueType implied on-curve points. PostScript outer contours
run counter-clockwise; TrueType uses the opposite convention. Native
flContour.reverse reverses in place.

Why: The result depends only on the shape, not on how the font was drawn, so
imports and pasted outlines get the right direction. A wrong direction makes
holes fill in some renderers and spoils overlap removal.

Use: Select glyphs. Run the script. Choose the masters. Press Correct. Press
Reload selection after you change the selection.

Benefit: Fixes many glyphs over many masters in one Undo step, and lists
each wrong contour before anything changes.

Safety: Open contours have no direction and are not counted. These shapes
are listed and kept, but count for the cross-shape safety check:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (a mirror in the transform turns the
  visible direction round).

After writing, a status note reports a newly introduced final off-curve with
raw Smooth (fl#8517), which FontLab may change on save. Existing conditions
are not reported as new. Check node types after VFJ reopen. A reversal
renumbers the nodes of that contour. The panel opens with All masters
chosen. When only one master has a wrong contour, check master compatibility
after the change: the other masters keep their node order.

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads every direction back. If FontLab fails part-way,
the error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_correct_direction.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Correct Contour Direction** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4c87a88043573f9d5eae7c3d5e313987844a0395acc0b0ad4ef87ef4af835515.py)
<!--/codeinclude-->
