---
this_file: src_docs/md/scripts/kerning/unbundle-punctuation-kerning.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Unbundle Punctuation Kerning

Materialize glyph-pair exceptions for selected punctuation across masters.

What: Turn inherited values involving the selection into explicit glyph pairs.
How: Expand affected class records, resolve existing exceptions, and keep every
explicit glyph pair, including zero. Class definitions and class pairs remain.
This preserves other members and permits subsequent independent punctuation
edits. No membership is removed. Unicode punctuation is the default filter;
untick it for unencoded punctuation, Greek letters or other selected glyphs.
Unencoded alternates use the Unicode values of their base-name glyph. An
ambiguous partner keeps only that pair. Each master is checked with FontLab's
shared pair validator; a master with invalid class members is named and kept,
while other valid masters can still write.
Whole-number values and the twice-UPM limit are checked too. Invalid numeric
data on any master, including one outside the chosen scope, keeps the entire
font unchanged: the shared writer validates numeric history font-wide.
Why: FontLab's Flatten Class Kerning expands the whole current-master table.
This tool limits expansion to selected glyphs and offers all-master scope.
Use: Select glyphs in the Font window. Inspect the non-modal preview, choose
masters, and press Add Exceptions. Each changing action is recorded as one Undo
step by the shared kerning writer. Refresh the selection for another pass.
Benefit: Isolate punctuation without discarding class data or existing overrides.

Independent behaviour rewrite after Simon Cozens, Unbundle Punctuation Kerning.py,
MIT. Repository: https://github.com/simoncozens/GlyphsScripts . No code copied.

Run **Kerning > Unbundle Punctuation Kerning** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `97894e162ebee70d9fbdbb5843d323f7af99e806b4fcfcad9a775c72a3d7ec93`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Kerning/Unbundle%20Punctuation%20Kerning.py)
