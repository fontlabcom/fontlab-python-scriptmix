---
this_file: src_docs/md/scripts/components/replace-reference.md
tags: ["Components"]
categories: ["Components"]
---

# Replace Reference

Replace the base glyph of matching components, and keep their placement.

What: Every component that refers to glyph X now refers to glyph Y. Offset,
scale, slant, name, note and lock of each component stay. Works on the
selected glyphs or on the whole font, on one or all masters. The table lists
every component that changes.

How: The script sets the base glyph name of the existing component in place,
then lets FontLab rebuild the component. It does not delete and re-create
the component, so nothing that a re-created element would lose is lost.

Why: Swapping a mark or a figure variant in many composites by hand is slow
and easy to get wrong. This keeps every placement exactly where it was.

Use: Run the script. Type the glyph to replace and the new glyph (both fields
complete names). Choose the glyphs and masters. Press Replace. Press Reload
selection after you change the selection.

Benefit: Changes a component in the whole font in one Undo step.

Safety: Auto layers are listed and never edited (change their recipe). A
component is blocked, with the reason in red, when:

- the new glyph has no layer for that master;
- the new glyph uses the edited glyph, directly or through other components
  (the result would refer to itself);
- the component shares its element data with other elements (the change
  would reach them too).

The script refuses the whole batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the components back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_replace_reference.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Components > Replace Reference** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/288f524dbe612d719a13e143d2568d6e6f4bd714ab79e9692cac5fb7151557b0.py)
<!--/codeinclude-->
