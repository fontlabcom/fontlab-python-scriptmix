# this_file: Scripts/Masters/Select Different Colour.py
# SPDX-License-Identifier: Apache-2.0
"""Add to the Font window selection all glyphs of a different mark colour.

What it does:
    Read the mark colours of the selected glyphs. Then select, in addition,
    every glyph whose mark colour is none of those colours. Unmarked glyphs
    count as one colour of their own.

How it works:
    The script reads the Font window selection, collects the mark values of
    the selected glyphs, and selects all other glyphs whose mark is not in that
    set. The old selection stays. It changes only the selection, never a glyph.

Why this design:
    - Pairs with "Select by Mark". That script picks colours from a list. This
      one derives the colours from the current selection: select a few glyphs
      of the colour to keep, run the script, then delete or move the rest.
    - It uses the shared selection helper, which refuses to write the selection
      while a Glyph window is active (FontLab bug fl#8528).
    - Difference to the Glyphs original: it works on all glyphs of the font. The
      Font window filter of FontLab is not readable from a script.

How to use:
    Open the Font window. Select glyphs of the colour(s) to keep apart. Run the
    script. Press Backspace or drag the selection as you need.

Benefit:
    Split a font by colour labels in two clicks.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Select different colour"
    (Apache-2.0), which is based on "Select Different Color" by Rainer Erich
    Scheichelbauer (mekkablue, Apache-2.0). Independent rewrite. No source code
    was copied.
"""

from collections.abc import Sequence

TITLE = "Select Different Colour"


def different_colour(marks: Sequence[tuple[str, int]], selected: Sequence[str]) -> list[str]:
    """Return names of glyphs whose mark differs from all selected glyphs.

    `marks` holds (glyph name, mark value) in font order. Mark 0 = no colour.
    Raise ValueError when no listed glyph is selected.
    """
    chosen = set(selected)
    kept = {mark for name, mark in marks if name in chosen}
    if not kept:
        raise ValueError("Select at least one glyph in the Font window first.")
    return [name for name, mark in marks if mark not in kept]


def run() -> str:
    """Read marks and selection, add the glyphs, return a message."""
    from fly import ap
    from fly.ap.scripting import (
        current_package,
        names_font_window_selection,
        select_glyphs,
    )

    package = current_package()
    font = ap.fontlab.CurrentFont()
    if package is None or font is None:
        raise ValueError("Open a font first.")
    marks = [(str(g.name), int(g.mark or 0)) for g in font.glyphs]
    names = different_colour(marks, names_font_window_selection())
    if not names:
        return "All glyphs have a colour of the selection; nothing to add."
    select_glyphs(names, package_id=int(package.id), add=True)
    return f"Added {len(names)} glyph(s) of a different colour."


def main() -> None:
    """Menu entry. Print the result or the reason for a refusal."""
    try:
        print(f"{TITLE}: {run()}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
