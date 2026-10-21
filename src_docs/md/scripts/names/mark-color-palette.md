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
Undo step with the App history order (see commit). It then reads each mark
back and compares it with the plan.

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

Credit: archived Apache-2.0 FontLab samples. Native acceptance pending.

Run **Names > Mark Color Palette** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/14c7938afc4c9f48ccf7e7f95c2d5692f0fcac4d69686c0572ccfddaa11fafdb.py)
<!--/codeinclude-->
