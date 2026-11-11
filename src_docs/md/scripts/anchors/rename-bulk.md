---
this_file: src_docs/md/scripts/anchors/rename-bulk.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Rename Bulk

Find and replace anchor names across glyphs and masters.

What: Renames anchors by plain text or by regular expression. Scope: the
selected glyphs or the whole font; the current master or all masters.
Example: find "^(top|bottom)$", replace "\1_alt".

How: The table updates with each key press. It lists every rename and flags
a blocked row in red. Rename writes all renames as one Undo step.
Position, style and expressions of each anchor stay as they are.

Why: A rename is blocked, not guessed, when the new name is empty, already in
use on the layer, or the target of two old names. This avoids silent
merges of anchors. A bad pattern shows its error and changes nothing.

Use: Select glyphs. Run the script. Type Find and Replace. Check the table.
Press Rename. Press Reload selection after you change the selection.

Benefit: One consistent anchor vocabulary in all masters, in one step, with a
complete preview.

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
anchors_rename_bulk.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Rename Bulk** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `8a1d87b5e40323e00a6ca2872bae7ccc88faf4cb4a7aa9f1b832ca1ea4c2ac1a`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Anchors/Rename%20Bulk.py)
