---
this_file: src_docs/md/scripts/names/mark-color-palette.md
tags: ["Names"]
categories: ["Names"]
---

# Mark Color Palette

Click a colour swatch to mark the selected glyphs with that colour.

WHAT: A non-modal panel shows ten swatches (none, eight hues, grey). Each
swatch shows how many glyphs in the font, and in the selection, carry that
mark. One click writes the mark to every selected glyph.

HOW: FontLab stores a mark as hue + 1 (1 to 360), grey as 1000 + level, and 0
for none. The script rescans the font, plans the change, and writes it as one
Undo step. It then reads each mark back and compares it with the plan. The
scan, the refusal policy and the one-step write come from the App helper
fly.ap.names_edit. If a write fails part way, every planned glyph is still
notified and stamped, and the message asks you to use Edit > Undo.

WHY: FontLab rebuilds all auto layers when an auto layer is notified. Undo
does not restore the rebuilt layers. So the script REFUSES glyphs that own an
auto layer and never puts an auto layer in the notify list. A base glyph of
an auto composite may be marked: its mark does not reach the composites
(native check pending). The script never reads flGlyph.fgGlyph, never calls
UpdateAll (fl#8537) and refuses to write when native updates are pending.
Swatch colours come from plain HLS arithmetic, so the colour logic works and
is testable without Qt.

USE: Select glyphs in the Font window. Run the script. Click a swatch. Press
Reload selection after you change the selection.

BENEFIT: Colour marks sort work (done, check, kerning needed) and show in the
Font window. One Edit > Undo reverts one click.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. Native acceptance pending.

Run **Names > Mark Color Palette** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d1c3f32a2e83290735e41241efd88513a3bcb2d19fe909a847219c0bc5e0e139.py)
<!--/codeinclude-->
