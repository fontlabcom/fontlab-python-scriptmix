#FLM: Reports · Compare Open Font Revisions
# this_file: Scripts/Reports/Compare Open Font Revisions.py
# SPDX-License-Identifier: Apache-2.0
"""Compare named glyph fields in two explicitly chosen open font revisions.

What it does:
    Open both fonts, choose each font and master, then Compare and inspect the
    changed-field details. Geometry, advances, anchors and components are read only;
    raw node flags are listed separately. This does not claim complete font equality.

How it works:
    Use the shared App comparison panel for two chosen open fonts and masters.
    Compare named geometry, advance, anchor and component fields; show raw
    flags separately.

Why this design:
    Separate field differences help distinguish a spacing revision from a
    drawing change without claiming complete font equality.

How to use:
    Open both revisions and run Reports > Compare Open Font Revisions. Choose
    each font and master, press Compare and inspect the changed-field details.

Benefit:
    Review the reported differences between revisions without copying data
    between fonts.
"""

from typing import Any

from fly.ap.scripting import revision_compare_dialog_type, show_script_dialog

KEY = "compare_open_font_revisions"


def main() -> Any:
    """Show the shared App comparison using its owned replacement and Close lifecycle."""
    return show_script_dialog(revision_compare_dialog_type(), KEY)


if __name__ == "__main__":
    main()
