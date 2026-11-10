# this_file: Scripts/Font UI Lab/Tabular Width Audit.py
# SPDX-License-Identifier: Apache-2.0
"""Choose an open font and compare selected glyph advances without changing them.

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
change the glyph selected in a FontLab editing window."""


def main():
    """Retain one world and return its nonmodal tabular audit controller."""
    from fly.ap.fontui.tabular_audit import show
    from fly.fp.world import FontWorld

    world = FontWorld()
    return show(world)


if __name__ == "__main__":
    main()
