# this_file: Scripts/Names/Duplicate Unicodes.py
# SPDX-License-Identifier: Apache-2.0
"""Find shared Unicode assignments across the whole current font and remove chosen pairs.

Expanded codepoint groups preserve font order and prefer the first primary owner
as keeper. Untick any row to keep its code, or tick the keeper too. Rescan resets
the preview; Remove ticked writes only the checked assignments and refreshes.
Requires Fly and App0.2.121.dev0. No glyph geometry or selection is edited.

Close all Glyph editors and activate the Font window before applying. Changed sources, pending native glyph
updates, automatic targets/dependants or surviving repeated-code lists that the
native setter would collapse refuse before history. One final history batch is
used; a partial failure diagnoses Edit > Undo. Full native history/font/reopen
preservation remains unqualified; no UpdateAll or fgGlyph conversion is used.
"""

from typing import Any


def main() -> Any:
    """Open the complete owned editor lazily through the shared App utility."""
    from fly.ap.duplicate_unicodes import show

    return show()


if __name__ == "__main__":
    main()
