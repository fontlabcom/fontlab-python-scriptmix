---
this_file: src_docs/md/scripts/contours/fix-zero-handles.md
tags: ["Contours"]
categories: ["Contours"]
---

# Fix Zero Handles

Find curve handles that sit on their own node, and clean them up.

What: For each selected glyph and master, the table lists every contour with
retracted handles: curves whose two handles both sit on their nodes, and
curves with one such handle. Fix turns the first kind into lines and, when
you ask for it, pulls single handles out.

How: A handle counts as retracted when it is closer than half a unit to its
own node. A curve with two retracted handles is a straight line in disguise:
FontLab's own flNode.convertToLine, called on the end node, removes the
handles and resets the smooth flags. With "Pull single handles out to ⅓", a
lone retracted handle moves a third of the way towards the other handle: the
curve then has a real tangent at that node, but its shape changes slightly.
TrueType (quadratic) contours are left alone.

Why: Retracted handles give a zero tangent: hinting, offsetting, stroke
expansion and some rasterisers handle them badly. With "Keep masters
compatible" ticked, a glyph is held back when the masters would get
different curves, or when only some masters are in scope.

Use: Select glyphs. Run the script. Choose the option and the masters. Press
Fix. Press Reload selection after you change the selection.

Benefit: Finds and fixes a common outline fault over many glyphs and masters
in one Undo step.

Safety: Pulling a single handle on a Smooth base can leave the handles
non-collinear. FontLab may later align them again. Converting a curve to a
line recomputes the smooth flags at both ends. These shapes are listed and
kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored distances are not visible
  distances).

A pulled handle lands on a whole unit, a third of the way to the other
handle, so FontLab's rounding preference cannot move it again.

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
After the write, it reads node counts and handle positions back. If FontLab
fails part-way, the error says that native changes may remain. The change is
recorded as one Undo step. The one-step write, the automatic-layer rule, the
pending-update check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_fix_zero_handles.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Fix Zero Handles** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3c1d65808eaf40328fe5f758061a03f70bbe867370c4e5c3823a09c19cd2ce45.py)
<!--/codeinclude-->
