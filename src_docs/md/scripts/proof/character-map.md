---
this_file: src_docs/md/scripts/proof/character-map.md
tags: ["Proof"]
categories: ["Proof"]
---

# Character Map

Pick characters from an installed reference font and see what your font covers.

What: Opens a modeless character map. A grid shows the characters of the Basic
Multilingual Plane in a reference font that you choose from the fonts
installed on your system, with a style and a size. Click a character to add
it to a proof text. The tool then reports, for each character of that text,
the Unicode value and the glyphs of the current FontLab font that encode it.
Glyphs with several Unicode values and characters beyond the Basic
Multilingual Plane are reported too.

Use: Open a font. Run Proof > Character Map. Choose the reference font, style
and size, then click characters to build a proof string. Read the coverage
report. Press Refresh to re-read the font after you change it. Press Copy
selected text when you want the proof string on the clipboard. Close the panel
when you are done. Without a font the panel says that coverage is unavailable
and the reference font choice still works.

Safety: The tool reads the Unicode assignments of the current font and the
list of installed fonts, and it writes nothing to the font: no font data,
selection, history, preference or Output text. The one write is the clipboard:
the copy button puts the proof text on the clipboard, and only when you press
it. The script itself never copies anything on launch.

Source: Original workflow built on the shared App character map
(fly.ap.glyphs.character_map.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Proof > Character Map** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `d0b7b74b0f88902a0b6191f7fb9fa4d89cc62df906905bd44dc7a6d9734fde2e`

[Python source at `168b57cbfbaf`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/168b57cbfbaf1b00b43f4aa06ba26d2e01ba12e1/Scripts/Proof/Character%20Map.py)
