---
this_file: src_docs/md/scripts/font-ui-lab/unicode-and-glyph-order-explorer.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Unicode and Glyph Order Explorer

Explore Unicode assignments and glyph order with a linked name sequence.

Use: Open this window with a font available and browse or filter its glyph names.
The initial sequence follows the font's catalogue order. Selecting glyphs in the
browser builds a sequence of those names; the sequence field also accepts repeated
slash-prefixed names such as /A /A /V. Click a sequence occurrence or use its
navigation keys to inspect that occurrence without renaming or reordering glyphs.

The detail table shows the glyph name, its sequence occurrence index, its positions
in the catalogue and all Unicode values assigned to the glyph. Code points are
shown together with their characters, including characters outside the Basic
Multilingual Plane. Unencoded glyphs are labelled explicitly. Selecting a repeated
name reports the selected occurrence, rather than collapsing all matching names
into one sequence position. The linked preview follows that occurrence.

Safety: This is a read-only inspection of the current borrowed font. It does not
write Unicode assignments, glyph order or sequence text back into the font, save a
file, or close the font. Missing fonts, unreadable sequence data and failed refreshes
clear occurrence details and the linked preview. Close the window when finished.

Run **Font UI Lab > Unicode and Glyph Order Explorer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d4715f1721dc5d9b1401ba0b2ee0ef1ae671be242409c649c7733495c976a4fa`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Font%20UI%20Lab/Unicode%20and%20Glyph%20Order%20Explorer.py)
