---
this_file: src_docs/md/scripts/contours/optimize-start-points.md
tags: ["Contours"]
categories: ["Contours"]
---

# Optimize Start Points

Move the start node of every closed contour to its bottom-left on-curve
node.

What: For each selected glyph and master, the table lists every contour
whose start node moves, and the node that becomes the start. Optimize
applies the moves.

How: The bottom-left node is the lowest on-curve node; on a tie, the
leftmost one. "Match current master" finds it in the current master and uses
the same node number in every other master whose contour has the same node
count, so the masters stay compatible. "Bottom-left in each master" finds it
in each master on its own. FontLab's own flContour.setStartPoint turns the
node list round in place; this is meant to keep the node flags. See Safety
for VFJ reopen.

Why: A predictable start node makes masters easier to compare, helps
interpolation and keeps the order of points in exported fonts stable.

Use: Select glyphs. Run the script. Choose the rule and the masters. Press
Optimize. Press Reload selection after you change the selection.

Benefit: Sets consistent start points over many glyphs and masters in one
Undo step.

Safety: A status note reports only a newly introduced final off-curve with
raw Smooth (fl#8517), which FontLab may change on save. Check node types
after VFJ reopen. Open contours keep their start. These shapes are listed
and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (bottom-left in stored coordinates is
  not bottom-left on screen).

A new start renumbers the nodes, so the panel opens with All masters chosen.
With "Keep masters compatible" ticked, a glyph is kept when its masters
would get different start nodes, or when other masters need the move too but
are not chosen.

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
Every move is planned before the first one is written, so the current master
stays a valid reference. After the write, the script reads the start nodes
back. If FontLab fails part-way, the error says that native changes may
remain. The change is recorded as one Undo step. The one-step write, the
automatic-layer rule, the pending-update check and the panel are shared
(fly.ap.outline_writer, fly.ap.outline_panel); the planner belongs to this
script.

Source: the author's own FontLab sample outlines_optimize_start_points.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Optimize Start Points** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/cbbd0e5748218bd193b831e928fb2177093ca01b63ff5cdae6393d2824e095f3.py)
<!--/codeinclude-->
