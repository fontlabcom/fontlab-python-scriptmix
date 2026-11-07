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

Benefit: Removes stray or obsolete anchors in many glyphs and masters in one
step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);

After the write, the script reads the result back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
The edit is recorded as one Undo step. The plan, the safety checks, the
one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchors.writer, fly.ap.anchors.panel.model); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_delete_by_name.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Delete By Name** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d9d16c3aa0992f1a2b9136173e82f68a87e75895b3a7cd3f88116efb77e6e103`

[Python source at `c2b34988556c`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/c2b34988556c9214a67f800f68565b7a32df832a/Scripts/Anchors/Delete%20By%20Name.py)
