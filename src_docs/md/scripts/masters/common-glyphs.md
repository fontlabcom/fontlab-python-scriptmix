---
this_file: src_docs/md/scripts/masters/common-glyphs.md
tags: ["Masters"]
categories: ["Masters"]
---

# Common Glyphs

Report glyph names common to every open font, including unencoded glyphs.

What: Intersect exact glyph names across the registered open fonts. Show the
sorted names, reusable slash text and each font's complete Unicode assignments.
How: Read the registered fonts twice within a deadline. Refuse changed data.
Map AllFonts() FontGate fonts to registered workspace packages by font ID,
then read each canonical font.glyphs list. Errors print a short diagnosis.
Use: Open the fonts to compare, make one current, then run the script. Select
and copy the report text for proofing. Run again to replace the report with a
fresh snapshot. With one font open, all its glyph names are reported.
Why: Exact names keep alternates and unencoded glyphs. Per-font Unicode lists
expose different encodings of a shared name. FontLab has no verified equivalent
of Glyphs' productionGlyphName conversion; the report uses stored FontLab names.
Over FontLab's Glyph-window multi-master text views and Text By Master, this
adds an exact-name proof set shared by every open font, with per-font encodings.
Benefit: Copy shared glyph names or the current font's encoded proof text.

Credit: Luke Prowse (LukeProwse), NaN-xyz/GlyphsApp-Scripts, CommonGlyphs.py,
MIT (root LICENSE), copyright 2019 LukeProwse. The README also declares Apache-2.0.
https://github.com/NaN-xyz/GlyphsApp-Scripts
Independent rewrite of behaviour. No source code was copied.

Run **Masters > Common Glyphs** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ed5a35144920f6dfe8d819d77bd2ca8d02818eb4d48d379d3a82d09ae06f4a0b.py)
<!--/codeinclude-->
