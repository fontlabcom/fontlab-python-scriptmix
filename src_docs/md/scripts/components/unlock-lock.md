---
this_file: src_docs/md/scripts/components/unlock-lock.md
tags: ["Components"]
categories: ["Components"]
---

# Unlock Lock

Show which components of the selected glyphs are locked; lock or unlock them.

What: Lists every component of the selected glyphs on the chosen masters,
with its lock state now and after the action. Lock or Unlock sets the state
of every component that differs.

How: A locked component cannot be selected or moved by accident in the Glyph
window. FontLab's Python property reports every component as locked, because
component data is always locked. So the script reads each element's own lock
flag from FontLab's glyph data (the same data that a .vfj file stores). It
trusts that data only when its elements match the layer's shapes one to one,
with the same component names. Otherwise the state shows as "unknown" and
the component is not changed. The lock is set on the existing component in
place.

Why: Locking protects finished composites while you edit their outlines.
Unlocking many components at once is tedious in the Glyph window.

Use: Select composite glyphs. Run the script. Choose Lock or Unlock and the
masters. Press Apply. Press Reload selection after you change the selection.

Benefit: Sets component locks in many glyphs and masters in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);

After the write, the script reads the lock flags again and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_unlock_lock.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Components > Unlock Lock** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/12b7ca216a88c0c30bf0d116baa46138dfcbd9084757b57507489eee02df77e8.py)
<!--/codeinclude-->
