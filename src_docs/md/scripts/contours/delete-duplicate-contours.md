---
this_file: src_docs/md/scripts/contours/delete-duplicate-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Delete Duplicate Contours

Find contours drawn twice in the same layer and keep only the first copy.

What: For each selected glyph and master, the table lists every contour that
repeats an earlier contour of the same layer. Delete removes the copies.

How: Two contours are duplicates when they have the same nodes in the same
cyclic order, from any start node in the same direction, and each node pair
lies within the tolerance (in glyph coordinates, so moved shapes compare
where you see them). On-curve and off-curve nodes must match. The first
contour of a group stays; FontLab's own flShape.removeContour removes the
others.

Reversed duplicate groups are listed as "reversed duplicate, kept". Every
member stays, including further copies: their winding can cancel. Open
contours are kept; cyclic rotation changes their open endpoints.

Why: Same-direction duplicates are invisible in a filled preview, but they
break overlap removal, double the ink in some renderers and confuse contour
order tools. With "Keep masters compatible" ticked, a glyph is held back
when the masters would lose different contours, or when only some masters
are in scope.

Use: Select glyphs. Run the script. Set the tolerance and the masters. Press
Delete. Press Reload selection after you change the selection.

Benefit: Removes hidden copies over many glyphs and masters in one Undo
step, and names the contour each copy repeats.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored nodes are not visible nodes).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads the contour counts back. If FontLab fails
part-way, the error says that native changes may remain. The change is
recorded as one Undo step. The one-step write, the automatic-layer rule, the
pending-update check and the panel are shared (fly.ap.contours.writer,
fly.ap.contours.panel.model); the planner belongs to this script.

Source: the author's own FontLab sample
outlines_delete_duplicate_contours.py, Apache-2.0. Adapted for the current
FontLab 9 API.

Run **Contours > Delete Duplicate Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d2efd700219d2d771343353d26695553e2809d364818e055cbe8003f83aa4aff`

[Python source at `83142fd0a0ef`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/83142fd0a0efad5aec2ed5ca10642beb376d3f0f/Scripts/Contours/Delete%20Duplicate%20Contours.py)
