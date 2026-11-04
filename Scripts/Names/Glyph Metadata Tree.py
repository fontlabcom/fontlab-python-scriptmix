# this_file: Scripts/Names/Glyph Metadata Tree.py
# SPDX-License-Identifier: Apache-2.0
"""Browse every glyph of the current font as an expandable metadata tree.

What: Opens a modeless panel with one top-level row per glyph, in font order.
Expand a glyph to see each Unicode value assigned to it and the local date
when the glyph was last modified. Glyphs without a Unicode value say
"Not encoded"; glyphs without a recorded date say "Not recorded". A glyph with
several Unicode values lists every one of them.

Use: Open a font. Run Names > Glyph Metadata Tree. Expand the glyphs you want
to inspect. Press Refresh after you change the font; the panel does not follow
edits by itself. Close the panel when you are done. If no font is open, or the
font changes while the panel reads it, the panel status line says so and shows
no partial tree.

Safety: Read-only. The tool reads glyph names, Unicode values and modification
dates once per refresh. It writes no font data, selection, history,
preference, clipboard or Output text. Closing the panel releases only the
widgets that the panel created.

Source: Original workflow built on the shared App glyph tree
(fly.ap.glyphs.tree.model), Apache-2.0.
Requires App>=1.2.0 and fontlab-fly in FontLab 9 Python 3.11.
"""

from typing import Any


def main() -> Any:
    """Open the shared glyph tree panel, or replace the one already open."""
    from fly.ap.glyphs.tree.model import show_tree

    return show_tree()


if __name__ == "__main__":
    main()
