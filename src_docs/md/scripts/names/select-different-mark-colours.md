---
this_file: src_docs/md/scripts/names/select-different-mark-colours.md
tags: ["Names"]
categories: ["Names"]
---

# Select Different Mark Colours

Add displayed glyphs with colours different from the initial selection.

Activate the Font window and select one or more glyphs. Run this command to add
its displayed glyphs whose stored mark hue is absent from those initial glyphs.
All initial selections stay selected. No selection means no change. The native
Font-window model keeps filtered-out glyphs untouched. Glyph data, Undo history,
preferences and Output contents are not cleared or edited.

Independently adapted from Pedro Arilla's Select different colour.py, based on
Rainer Erich Scheichelbauer's Select Different Color. See NOTICE and the exact
source identity in additional-tools.json. Requires Fly and App 0.2.75.dev0.
Native acceptance, including filtered/combined Font views, remains pending.

Run **Names > Select Different Mark Colours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ba91bdca5cac1da02f583e06bd070c6c9b302b0aead23fcd23b2b6e16ea42a1d.py)
<!--/codeinclude-->
