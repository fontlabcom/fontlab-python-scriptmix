---
this_file: src_docs/md/scripts/names/batch-rename.md
tags: ["Names"]
categories: ["Names"]
---

# Batch Rename

Find and replace in glyph names, with a live preview and strict checks.

WHAT: A non-modal panel takes a Find text (plain or regular expression) and a
Replace text. It lists every glyph whose name would change, with the new name
and a check result. Rename applies all rows that pass.

HOW: The script scans the font on open and on Reload, and again before the
write. A row passes only when the new name is valid, does not exist, is not the
target of another row, and the glyph is not tied to an auto layer. The write is
one Undo step. The rename uses the font-owned FontGate record, never
flGlyph.fgGlyph. The scan, the refusal policy and the one-step write come from
the shared module fly.ap.names_edit. If a write fails part way, every planned
glyph is still notified and stamped, and the message asks you to use Edit >
Undo.

WHY: FontLab would replace an existing glyph that has the new name, so the
script refuses that. FontLab rebuilds auto layers when they are notified (it
turned ecircumflex into a lone "ee" after e was renamed). So the script REFUSES
glyphs that have auto layers and glyphs that are the base of an auto composite,
also through other composites. It never calls UpdateAll (fl#8537) and refuses
to write while native updates are pending. Kerning and features keep the old
names.

USE: Select glyphs in the Font window. Run the script. Type Find and Replace.
Use \1 for groups in regular-expression mode. Press Rename. Choose "All
glyphs" to rename across the font.

BENEFIT: Bulk renames (for example uniXXXX to AGL names) are safe, previewed
and reversible with one Edit > Undo.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. The edit is recorded as one Undo step.

Run **Names > Batch Rename** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/91f8c59445b9450ce64104052a687f5107f72f08595c869f2dc3ce53783a0ccb.py)
<!--/codeinclude-->
