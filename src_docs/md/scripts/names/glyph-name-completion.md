---
this_file: src_docs/md/scripts/names/glyph-name-completion.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Name Completion

Draft text with completions taken from the glyph names of the current font.

What: Opens a modeless panel with a text area. As you type, the panel offers
the exact glyph names of the current font as completions, so you can write
lists of glyph names (for a class, a test string or a note) without typos.
Typing at least three characters, or pressing Ctrl+E, opens the completion
list. The vocabulary is the complete glyph-name list in font order.

Use: Open a font. Run Names > Glyph Name Completion. Type a draft and pick
names from the list. Press Refresh to reload the vocabulary after the font
changed; your draft stays. Select and copy the text with the normal text
shortcuts. Close the panel when you are done. The draft is not saved anywhere.

Safety: The panel only reads glyph names. Your draft lives in the panel and is
lost when the panel closes. The tool writes no font data, selection, history,
preference, file or Output text, and it never copies text by itself.
Standard text selection and copy stay under your control.

Source: Original workflow built on the shared App completion panel
(fly.ap.glyphs.completion.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.

Run **Names > Glyph Name Completion** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b9a5198a8063ce7b4536ad9717538375dc9f14900cd5a93b7105a1041963ae72`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Names/Glyph%20Name%20Completion.py)
