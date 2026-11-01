# this_file: Scripts/Names/Select Different Mark Colours.py
# SPDX-License-Identifier: Apache-2.0
"""Add displayed glyphs with colours different from the initial selection.

Activate the Font window and select one or more glyphs. Run this command to add
its displayed glyphs whose stored mark hue is absent from those initial glyphs.
All initial selections stay selected. No selection means no change. The native
Font-window model keeps filtered-out glyphs untouched. Glyph data, Undo history,
preferences and Output contents are not cleared or edited.

Independently adapted from Pedro Arilla's Select different colour.py, based on
Rainer Erich Scheichelbauer's Select Different Color. See NOTICE and the exact
source identity in additional-tools.json. Requires Fly and App 0.2.26.dev332.
Native acceptance, including filtered/combined Font views, remains pending.
"""


def main() -> tuple[str, ...]:
    """Run the complete additive colour-selection action through Fly."""
    from fly.ap.mark_colour_selection import select_different_mark_colours

    return select_different_mark_colours()


if __name__ == "__main__":
    main()
