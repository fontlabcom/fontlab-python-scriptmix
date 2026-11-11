---
this_file: src_docs/md/scripts/font-info/paste-glyph-order-encoding.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Paste Glyph Order Encoding

Insert pasted names into the current font's order and save a FontLab encoding.

Select a glyph, run the tool, and paste space-separated glyph names. Preview
moves known names before the selected glyph, keeping pasted order and removing
repetitions. Unknown names are listed. The insertion position stays defined
even when the selected glyph is among the pasted names.

Save a new .enc file anywhere, then use File > Import > Encoding. Choose the
encoding in the Font window; use the encoding chooser's Refresh button as needed. This produces an
ordered Encoding view; it does not change the font's stored glyph indices.
FontLab's File > Export > Encoding saves a visible order; this tool adds
insertion by pasted names. Existing files are kept. No font edit or Undo step
is made. The preview shows up to 200 rows; the file contains every supported glyph.
Non-ASCII or unsafe glyph names get named kept rows and stay out of the file.
Why: Glyphs glyphOrder has no bound FontLab glyph-reorder API. An encoding
provides a persistent order that FontLab can import without changing glyph indices.
Benefit: Move a pasted sequence in one action and reuse its order in FontLab.

Independent behaviour rewrite after Alex Slobzheninov, Glyphs-Scripts,
Font Info/glyphOrder - Paste.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts .
No upstream code, private identifiers or comments are used.

Run **Font Info > Paste Glyph Order Encoding** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `58dd0938d020cc42eb18d3c5c246e26414b97beda26ed3e2247042ef8d370317`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Font%20Info/Paste%20Glyph%20Order%20Encoding.py)
