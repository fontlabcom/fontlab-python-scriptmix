---
this_file: src_docs/md/scripts/names/glyph-notes.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Notes

Read and edit the note of one glyph. Browse every glyph that has a note.

WHAT: A non-modal panel shows the note of the first glyph selected in the Font
window in an editor. Save writes it. A list below shows all glyphs that have a
note. A click loads that note into the editor. A double-click also selects the
glyph in the Font window.

HOW: The script scans the whole font. Save rescans, then writes one note as one
Undo step: layers and glyph in one notify list (a glyph alone adds no Undo
step). It then reads the note back and compares it with the text. Double-click
selection goes through the App selection helper, which checks that a regular
Font window is active (fl#8528). The scan, the refusal policy and the one-step
write come from the shared module fly.ap.names_edit. If a write fails part way,
every planned glyph is still notified and stamped, and the message asks you to
use Edit > Undo.

WHY: FontLab rebuilds all auto layers when an auto layer is notified, and Undo
does not restore them. So the script REFUSES to save a note on a glyph that
owns an auto layer, says why, and never puts an auto layer in the notify list.
A base glyph of an auto composite may get a note (native check pending). The
script never reads flGlyph.fgGlyph (that getter can clear a fresh note mirror
on build 9784), never calls UpdateAll (fl#8537), and discloses queued ids and
their possible date changes.

USE: Select a glyph in the Font window. Run the script. Edit the note. Press
Save note. Pick a row in the list to edit another glyph.

BENEFIT: Notes travel with the glyph in .vfc and .vfj files. The list gives an
overview of all remarks in the font. One Edit > Undo reverts one save.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. The edit is recorded as one Undo step.

Run **Names > Glyph Notes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/2e5636a4e20af47818dcde26c0ffce22ca1a18a16859f20b50ed632a00fc6de4.py)
<!--/codeinclude-->
