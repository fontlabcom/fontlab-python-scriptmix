---
this_file: src_docs/md/scripts/names/suffix-tool.md
tags: ["Names"]
categories: ["Names"]
---

# Suffix Tool

Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt) on the selected
glyphs.

WHAT: A non-modal panel offers three operations. Add puts a suffix on each
selected name. Remove strips one suffix (or the last suffix when the field is
empty). Replace swaps one suffix for another. A table previews every new name
and a check result. Apply renames all rows that pass.

HOW: The script rescans the font before the write. A row passes only when the
new name is valid, does not exist, is not the target of another row, and the
glyph is not tied to an auto layer. The write is one Undo step. The rename and
the optional Unicode removal use the font-owned FontGate record, never
flGlyph.fgGlyph. After clearing Unicode the script reads the list back and
compares it with the plan. The scan, the refusal policy and the one-step write
come from the shared module fly.ap.glyphs.names.model. If a write fails part way, every
planned glyph is still notified and stamped, and the message asks you to use
Edit > Undo.

WHY: Suffixed alternates are normally unencoded, so the panel can clear their
Unicode in the same step. FontLab would replace an existing glyph that has the
new name, so the script refuses that. FontLab rebuilds auto layers when they
are notified, so the script REFUSES glyphs that have auto layers and glyphs
that are the base of an auto composite, also through other composites. It never
calls UpdateAll (fl#8537) and discloses queued ids and their possible date
changes. Before it removes Unicode, the script applies the guards of the App
Unicode writer: a regular Font window must be active and no Glyph editor may be
open.

USE: Select glyphs in the Font window. Run the script. Choose the operation,
type or pick a suffix (a missing leading dot is added), then press Apply.

BENEFIT: Alternate sets (.ss01, .sc, .case) get consistent names in one
previewed, undoable step.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. The edit is recorded as one Undo step.

Run **Names > Suffix Tool** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `67fab137c995d22a14bbb0b5d2a961f40af914581f6a88eadee65fb9d1492855`

[Python source at `1fddaa75b7e6`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/1fddaa75b7e644ddcb3764909f3dd231cc78528e/Scripts/Names/Suffix%20Tool.py)
