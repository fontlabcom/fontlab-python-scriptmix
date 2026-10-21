---
this_file: src_docs/md/scripts/components/align-by-anchor.md
tags: ["Components"]
categories: ["Components"]
---

# Align By Anchor

Align mark components on their base component by anchors.

What: In each selected composite, the first component is the base. Every
later component (a mark) moves so that its "_name" anchor lands on the base's
"name" anchor. The table shows the anchor pair, the current offset and the new
offset per master.

How: New offset = base offset + base anchor - mark anchor, rounded half up to
whole units. The anchors come from the base and mark glyphs on the same master.
"Automatic" takes the first pair the two glyphs share; or choose one anchor
name. Only the offset changes: the component itself stays in place in the
layer, with its name, note and lock.

Why: Marks drift when anchors move after a composite was built. This puts
them back without a rebuild, and keeps manual composites manual. Components
with scale, slant or rotation are listed and kept: the anchor sum is exact
only for a plain move.

Use: Select composite glyphs. Run the script. Choose the anchor and the
masters. Press Align. Press Reload selection after you change the selection.

Benefit: Re-aligns many marks over many masters in one Undo step.

Safety: Auto layers are listed and never edited (FontLab aligns them itself).
The script refuses the whole batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the offsets back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_align_by_anchor.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Components > Align By Anchor** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7f268de54fbea93e1b54bd9a3ee063251dc0993aecf12c1878418aa5303244ee.py)
<!--/codeinclude-->
