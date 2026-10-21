---
this_file: src_docs/md/scripts/cleaning/delete-stickers.md
tags: ["Cleaning"]
categories: ["Cleaning"]
---

# Delete Stickers

Remove FontLab stickers from all layers or master layers.

What: Delete text, arrow and symbol stickers from selected glyphs or the whole
font. Choose every stored layer, including backgrounds, or master layers only.
How: Preview each layer's sticker count, then remove only ShapeSticker shapes.
Contours, components, anchors, image shapes and layer notes stay.
Why: Stickers are FontLab's equivalent of the source tools' layer annotations.
Use: Choose the glyph and layer scope. For the whole font, press Preview, then
Delete and confirm the font and counts. Other scopes use the live table.
Benefit: Clear annotations over many layers in one action. The deletion is
recorded as one Undo step. Glyphs with automatic layers are listed and kept.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Cleaning/Delete annotations in all layers.py and Delete annotations in all
master layers.py, Apache-2.0. Repository:
https://github.com/pedroarilla/glyphs-scripts . No source code copied.

Run **Cleaning > Delete Stickers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3838ff1c11912384b76988a9f22359a0a367efe5ac94c1d3402d3593ca38f0c7.py)
<!--/codeinclude-->
