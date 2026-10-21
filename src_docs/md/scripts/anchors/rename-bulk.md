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
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the result back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_rename_bulk.py, Apache-2.0.
Adapted for the current FontLab 9 API.

Run **Anchors > Rename Bulk** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/88a65a46fb92d0121677d441e43a5a4e794395e205a8b3da57e1194c9e579dce.py)
<!--/codeinclude-->
