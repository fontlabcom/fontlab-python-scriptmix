---
this_file: src_docs/md/scripts/names/batch-glyph-notes.md
tags: ["Names"]
categories: ["Names"]
---

# Batch Glyph Notes

Set or append one note on every selected glyph at once.

WHAT: A non-modal panel takes a note text and an operation. Set replaces each
glyph note (an empty Set clears the notes). Append adds the text on a new line
after the existing note. A table shows every note before and after. Apply
writes only the glyphs whose note changes.

HOW: The script reads the selection through the App helper and scans the whole
font. For the write it rescans, plans, and writes as one Undo step with the App
history order: layers and glyph in one notify list (a glyph alone adds no Undo
step). After the write it reads each note back and compares it with the plan.

WHY: A glyph note belongs to the glyph, not to a master. FontLab rebuilds
all auto layers when an auto layer is notified, and Undo does not restore
them. So the script REFUSES glyphs that own an auto layer, shows the reason in
the table, and never puts an auto layer in the notify list. A base glyph of an
auto composite may get a note (native check pending). The script never reads
flGlyph.fgGlyph (that getter can clear a fresh note mirror on build 9784),
never calls UpdateAll (fl#8537), and refuses to write while native updates are
pending.

USE: Select glyphs in the Font window. Run the script. Choose Set or Append,
type the note, check the table, press Apply. Press Reload selection after you
change the selection.

BENEFIT: Review comments or to-do remarks reach many glyphs in one undoable
step, with a preview.

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.

Run **Names > Batch Glyph Notes** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6139d081f75ce8d577f39a008d1d92dd3c6ef5454290c1575fe330cc9bdf0d2f.py)
<!--/codeinclude-->
