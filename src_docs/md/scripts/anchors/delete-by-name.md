---
this_file: src_docs/md/scripts/anchors/delete-by-name.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Delete By Name

Delete anchors by name from the selected glyphs.

What: Shows every anchor name found on the selected glyphs, with the number of
layers that carry it. Tick the names to delete. Choose the masters.

How: Delete removes every anchor with a ticked name from every editable layer
in scope. Layers with an auto role are counted, shown and kept.

Why: The checklist is the preview: you see which names exist before you delete.
Nothing else changes: contours, components and other anchors stay.

Use: Select glyphs. Run the script. Tick names. Press Delete. Press Reload
selection after you change the selection.

Benefit: Removes stray or obsolete anchors in many glyphs and masters in one step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the result back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The one-step write, the automatic-layer rule
and the pending-update check are shared with other scripts (fly.ap.history,
fly.ap.edit_guards); the planner and the panel belong to this script.

Source: the author's own FontLab sample
anchors_delete_by_name.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Delete By Name** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6980991efcb150b1da4eacb7f017055990227f42d576f9f5eaf8a3247a3f86db.py)
<!--/codeinclude-->
