---
this_file: src_docs/md/scripts/font-info/trial-font-maker.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Trial Font Maker

Make prefixed trial copies of static fonts exported from the current font.

What: Keep selected FontLab glyphs in each matching exported OTF or TTF. Keep
.notdef and component dependencies. Ligature expansion is off by default;
tick Also keep ligatures to include the extra glyphs listed in the preview.
Keep kerning and positioning unless Remove kerning and positioning is ticked.
Keep the existing liga substitutions that survive this keep set. Prefix family,
full, unique and PostScript names, including CFF names. Preserve copyright and
licence records.
How: Read exported binaries with fontTools, subset detached copies and save new
files. Inspect the saved copies by reopening them in FontLab. No source font or
source binary is edited. There is no font edit and no Undo step.
Why: File > Export Font As produces the source binaries. This panel adds a selected
glyph keep set and consistent trial names across those static exports. It avoids
changing a live font or relying on Glyphs export-only custom parameters.
Usage: Export static OTF/TTF instances to a folder first. Select the trial glyphs
in FontLab. Open this panel, enter that folder, a different output folder and a
prefix. Inspect the per-file preview, then press Make Trial Copies. Use selection
reads the glyph selection again. Family name and UPM must match the current font;
other files get named kept rows. Existing destinations are kept. Variable fonts
are kept: export static instances before using this tool.
Benefit: Repeatable trial binaries without deleting work from the design source.
The keep set uses exported glyph names. Preserve glyph names in the export
profile; renamed or absent glyphs are reported instead of silently dropped.
Substitution features are limited to liga and the retained positioning feature
tags; ligatures are not invented.
Requires user-installed fontTools in FontLab's Python site-packages, such as
the dependency installed with fontlab-fontport. FontLab's private copy is not
used. Install it through Settings > Python if it is missing.
Source inspection is cached until the folder or selection changes, or Refresh
Exports is pressed. Prefix edits update destination names without opening fonts.

Independent behaviour rewrite of Fernando Díaz / Reset Type Studio,
Glyphs-Scripts/Exports/Trial Font Maker.py.
https://github.com/Reset-Type-Studio/Glyphs-Scripts
Apache-2.0, declared in the repository README; no separate LICENSE file.
No source code was copied.

Run **Font Info > Trial Font Maker** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `4a3f416df2e51d3f77d514681c0b86e5029817d8156015a6626b4ce78602ce0f`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Font%20Info/Trial%20Font%20Maker.py)
