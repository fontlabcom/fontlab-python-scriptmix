---
this_file: src_docs/md/scripts/font-ui-lab/tabular-width-audit.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Tabular Width Audit

Choose an open font and compare selected glyph advances without changing them.

Use: Choose a font in the window, filter its glyph names and select several
rows. Every selected glyph is compared with the first selected row in browser
order, regardless of the order in which you clicked the rows. The report shows
exact fractional advances, so nearby unequal widths remain visible. Blank and
component glyphs participate using their actual advances.

Refresh open fonts to discover newly opened documents and reacquire their
current data. Changing fonts clears the previous selection and report. Empty,
closed or unreadable fonts and invalid widths show a reason instead of an old
successful result. Fonts with identical labels remain separate choices.

Safety: This window borrows fonts. It does not change widths, outlines, host
selection, masters or font history, save files, or close any font. Close the
audit window when finished. The preview follows the selected row; it does not
change the glyph selected in a FontLab editing window.

Run **Font UI Lab > Tabular Width Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `58fca5c31786f1ab0d95e83c7066964f1889ebf96635ce7844212dd7869a99d2`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Font%20UI%20Lab/Tabular%20Width%20Audit.py)
