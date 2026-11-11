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
source identity in additional-tools.json. Requires Fly and App 1.2.0.
Native acceptance, including filtered/combined Font views, remains pending.

Run **Names > Select Different Mark Colours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `42fe45daf79850eb223950e6b440f86773a9849a8f4e622d6177caa422842770`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Names/Select%20Different%20Mark%20Colours.py)
