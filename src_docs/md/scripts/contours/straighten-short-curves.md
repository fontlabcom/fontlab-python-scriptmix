---
this_file: src_docs/md/scripts/contours/straighten-short-curves.md
tags: ["Contours"]
categories: ["Contours"]
---

# Straighten Short Curves

Turn short, flat curves into straight lines.

What: For each selected glyph and master, the table lists every contour with
curves that are short and flat: the number of curves now, how many become
lines, and the largest handle deviation. Straighten converts them.

How: A cubic curve qualifies when its chord is no longer than "Chord up to"
and both handles lie within "Handles within" of the chord, between its ends.
FontLab's own flNode.convertToLine, called on the end node of the curve,
removes the two handles and recomputes the smooth flags at both ends.
TrueType (quadratic) contours are left alone.

Why: Autotracing and format conversion leave tiny curves that are really
lines. As lines they hint better, interpolate more safely and take less
space. With "Keep masters compatible" ticked, a glyph is held back when the
masters would get different curves, or when only some masters are in scope.

Use: Select glyphs. Run the script. Set the two limits and the masters.
Press Straighten. Press Reload selection after you change the selection.

Benefit: Cleans many glyphs over many masters in one Undo step, with the
worst deviation shown before anything changes.

Safety: These shapes are listed and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (stored lengths are not visible
  lengths).

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
After the write, it reads the node counts back. If FontLab fails part-way,
the error says that native changes may remain. The change is recorded as one
Undo step. The one-step write, the automatic-layer rule, the pending-update
check and the panel are shared (fly.ap.outline_writer,
fly.ap.outline_panel); the planner belongs to this script.

Source: the author's own FontLab sample outlines_straighten_short_curves.py,
Apache-2.0. Adapted for the current FontLab 9 API.

Run **Contours > Straighten Short Curves** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8cb89dc50a822132028d989d49846fc2f8857cc361ac7c40d44bf7b51caedada.py)
<!--/codeinclude-->
