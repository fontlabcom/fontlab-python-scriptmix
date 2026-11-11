---
this_file: src_docs/md/scripts/names/glyph-metadata-tree.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Metadata Tree

Browse every glyph of the current font as an expandable metadata tree.

What: Opens a modeless panel with one top-level row per glyph, in font order.
Expand a glyph to see each Unicode value assigned to it and the local date
when the glyph was last modified. Glyphs without a Unicode value say
"Not encoded"; glyphs without a recorded date say "Not recorded". A glyph with
several Unicode values lists every one of them.

Use: Open a font. Run Names > Glyph Metadata Tree. Expand the glyphs you want
to inspect. Press Refresh after you change the font; the panel does not follow
edits by itself. Close the panel when you are done. If no font is open, or the
font changes while the panel reads it, the panel status line says so and shows
no partial tree.

Safety: Read-only. The tool reads glyph names, Unicode values and modification
dates once per refresh. It writes no font data, selection, history,
preference, clipboard or Output text. Closing the panel releases only the
widgets that the panel created.

Source: Original workflow built on the shared App glyph tree
(fly.ap.glyphs.tree.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Names > Glyph Metadata Tree** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b79472aaf93c41ac1d5d2bc252fc2e1b58a697438c0204b7f3fb80603018fb39`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Names/Glyph%20Metadata%20Tree.py)
