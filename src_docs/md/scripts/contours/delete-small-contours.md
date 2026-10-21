---
this_file: src_docs/md/scripts/contours/delete-small-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Delete Small Contours

Delete contours whose area is below a threshold: specks from drawing or
tracing.

What: For each selected glyph and master, the table lists every contour
smaller than the threshold, with its area and position. Delete removes them.

How: The area is the exact area of the curves in square font units, measured
by fly.ap.contour_selection.unsigned_area (FontTools' area pen). Open
contours are listed as "open contour, kept" and are never deleted. A contour
counts as small when its area is strictly below the threshold. This is the
same rule as Contours > Select Small Contours, so you can select first and
look, then delete with the same number. FontLab's own flShape.removeContour
removes each contour.

Why: Specks are hard to see in a filled preview but end up in the font. With
"Keep masters compatible" ticked, a glyph is held back when the masters
would lose different contours, or when only some masters are in scope:
different contour counts break interpolation.

Use: Select glyphs. Run the script. Set the threshold and the masters. Press
Delete. Press Reload selection after you change the selection.

Benefit: Removes specks over many glyphs and masters in one Undo step, and
shows each one first.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored areas are not visible areas).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
refuses before any history exists when FontLab holds queued glyph updates.
The area needs FontTools (fontlab-fontlabapp[fontui]); without it the status
line says so and nothing changes. After the write, the script reads the
contour counts back. If FontLab fails part-way, the error says that native
changes may remain. The change is recorded as one Undo step. The one-step
write, the automatic-layer rule, the pending-update check and the panel are
shared (fly.ap.outline_writer, fly.ap.outline_panel); the planner belongs to
this script.

Source: the author's own FontLab sample outlines_delete_small_contours.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Delete Small Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a68dd311ce836325f1eab174a6c568b17ae86f1cc44740acf37261b3d3ad47df.py)
<!--/codeinclude-->
