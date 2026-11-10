# this_file: Scripts/Font UI Lab/Unicode and Glyph Order Explorer.py
# SPDX-License-Identifier: Apache-2.0
"""Explore Unicode assignments and glyph order with a linked name sequence.

Use: Open this window with a font available and browse or filter its glyph names.
The initial sequence follows the font's catalogue order. Selecting glyphs in the
browser builds a sequence of those names; the sequence field also accepts repeated
slash-prefixed names such as /A /A /V. Click a sequence occurrence or use its
navigation keys to inspect that occurrence without renaming or reordering glyphs.

The detail table shows the glyph name, its sequence occurrence index, its positions
in the catalogue and all Unicode values assigned to the glyph. Code points are
shown together with their characters, including characters outside the Basic
Multilingual Plane. Unencoded glyphs are labelled explicitly. Selecting a repeated
name reports the selected occurrence, rather than collapsing all matching names
into one sequence position. The linked preview follows that occurrence.

Safety: This is a read-only inspection of the current borrowed font. It does not
write Unicode assignments, glyph order or sequence text back into the font, save a
file, or close the font. Missing fonts, unreadable sequence data and failed refreshes
clear occurrence details and the linked preview. Close the window when finished."""


def main():
    """Open the inspection window for the current borrowed font."""
    from fly.ap.fontui.unicode_order import show
    from fly.fp.world import FontWorld

    world = FontWorld()
    return show(world.CurrentFont())


if __name__ == "__main__":
    main()
