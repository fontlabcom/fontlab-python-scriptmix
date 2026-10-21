---
this_file: src_docs/md/scripts/names/suffix-tool.md
tags: ["Names"]
categories: ["Names"]
---

# Suffix Tool

Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt) on the selected glyphs.

WHAT: A non-modal panel offers three operations. Add puts a suffix on each
selected name. Remove strips one suffix (or the last suffix when the field is
empty). Replace swaps one suffix for another. A table previews every new name
and a check result. Apply renames all rows that pass.

HOW: The script rescans the font before the write. A row passes only when the
new name is valid, does not exist, is not the target of another row, and the
glyph is not tied to an auto layer. The write is one Undo step with the App
history order (see commit). The rename and the optional Unicode removal use the
font-owned FontGate record, never flGlyph.fgGlyph. After clearing Unicode the
script reads the list back and compares it with the plan.

WHY: Suffixed alternates are normally unencoded, so the panel can clear their
Unicode in the same step. FontLab would replace an existing glyph that has the
new name, so the script refuses that. FontLab rebuilds auto layers when they
are notified, so the script REFUSES glyphs that have auto layers and glyphs
that are the base of an auto composite. It never calls UpdateAll (fl#8537) and
refuses to write while native updates are pending.
Before it removes Unicode, the script applies the guards of the App Unicode
writer: a regular Font window must be active and no Glyph editor may be open.

USE: Select glyphs in the Font window. Run the script. Choose the operation,
type or pick a suffix (a missing leading dot is added), then press Apply.

BENEFIT: Alternate sets (.ss01, .sc, .case) get consistent names in one
previewed, undoable step.

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.

Run **Names > Suffix Tool** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/e86eb2bf9d65a2834917630528cf4a14a0138a6edc4a8388cc32c84381018c0e.py)
<!--/codeinclude-->
