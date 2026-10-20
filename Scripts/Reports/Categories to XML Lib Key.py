# this_file: Scripts/Reports/Categories to XML Lib Key.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
"""Export a complete ordered public.openTypeCategories UFO lib fragment.

Open a font and run this command. The read-only modeless panel includes every
native glyph in font order. Select the XML for manual insertion into a UFO's
lib dictionary. Mark becomes mark; every other category becomes base, including
ligatures and unknown glyphs, exactly as in Simon Cozens' MIT source. Glyph names
are XML-escaped. Empty fonts produce an empty dictionary. No file is written.

Glyport's GSGlyph.category policy supplies categories from maintained glyphsLib
GlyphData: names first, Unicode fallback for unknown names. Explicit GDEF class
is not a substitute. This command requires fontlab-glyport and its declared
glyphsLib dependency as well as matching App and Fly, in FontLab9 Python3.11.
Refresh rebuilds the full snapshot; a changing source or missing dependency
clears the report and shows the failure. Close releases the owned callbacks.
No clipboard, preferences, Output, selection, history or font writers are used.
Native getter preservation and actual panel behavior await native acceptance.
Adapted from Simon Cozens' Categories to XML lib key.py; see NOTICE.
"""


def main() -> None:
    """Use Fly for shared UI and the existing foreign category policy."""
    from fly.ap.category_xml import show
    from fly.gp.glyphsapp.glyph_info import glyph_categories

    show(glyph_categories)


if __name__ == "__main__":
    main()
