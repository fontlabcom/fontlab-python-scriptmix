---
this_file: src_docs/md/scripts/anchors/center-horizontally.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Center Horizontally

Put named anchors on the horizontal centre of the advance or of the ink box.

What: Moves the named anchors sideways. A slider sets the target between the
left edge (0 %) and the right edge (100 %) of the advance width or of
the ink box. The y value never changes.

How: With an italic angle the target is a slanted line. For the advance it
passes through the baseline point; for the ink box it passes through the
centre of the box. So a top anchor of an italic glyph moves right as its
height grows. FontLab angle convention: a negative angle leans right.
Example: advance 500, centre, angle -10 degrees, y 700: x = 373.

Why: One rule for upright and italic glyphs. The panel starts with the font
italic angle of the current master and lets you override it. Reload
selection keeps your value. With all masters, one angle serves every
master and the panel says so.

Use: Select glyphs. Run the script. Type the anchor names. Choose advance or
ink box. Move the slider. Check the table. Press Centre.

Benefit: Mark anchors sit on the optical centre in every master, in one step.

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
anchors_center_horizontally.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Center Horizontally** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d56a67a6cca4c6a9d168fe93cba394e8a925d520a1c17d83c27a858003a11183`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Anchors/Center%20Horizontally.py)
