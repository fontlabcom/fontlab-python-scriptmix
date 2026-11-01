---
this_file: src_docs/md/scripts/contours/remove-overlap.md
tags: ["Contours"]
categories: ["Contours"]
---

# Remove Overlap

Remove overlaps in the outline shapes of the selected glyphs.

What: For each selected glyph and master, the table lists every outline
shape whose contours overlap: the contour count now and after the merge.
Remove Overlap merges them. Shapes without overlap stay untouched. Overlaps
between separate shapes are not merged. This tool tests intersections
between contours; a single self-intersecting contour is kept.

How: Each shape goes through FontLab's FontGate engine: a copy is made with
flShape.convertToFgShape, fgShape.removeOverlap merges it (a shape has an
overlap when native contours intersect or same-direction contours nest), and
flShape.assign writes the result back into the same shape object. The start
node of each new contour moves back to an old start point when one survives
the merge, as FontLab's own command does. The preview runs the same merge on
a copy, so the numbers are exact.

Why: Overlapping contours print and render fine in many places, but fonts
for the web, variable fonts and many tools need clean outlines. With "Keep
masters compatible" ticked, a glyph is held back when the masters would get
different contours, or when only some masters are in scope: the merge would
break interpolation.

Use: Select glyphs. Run the script. Choose the masters. Press Remove
Overlap. Press Reload selection after you change the selection.

Benefit: Cleans many glyphs over many masters in one Undo step, and lists
each merge before anything changes.

Safety: A status note reports only a newly introduced final off-curve with
raw Smooth (fl#8517), which FontLab may change on save. Check node types
after VFJ reopen. The merge rebuilds the contours of a merged shape: node
names, node flags, contour names and corner_smooth (fl#8569) in that shape
are not kept. FontGate assign also replaces the shape appearance. No name,
note or appearance preservation is claimed for that round trip. These shapes
are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with a transform (FontGate would merge them in stored coordinates);
- shapes with an open contour (an open contour has no inside).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads the contour counts back. If FontLab fails
part-way, the error says that native changes may remain. The change is
recorded as one Undo step. The one-step write, the automatic-layer rule, the
pending-update check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_remove_overlap.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Remove Overlap** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e3d3597d1194e521e002dfe1d68f9f62d4e94fa8ae72893f18b99dd979397b3d.py)
<!--/codeinclude-->
