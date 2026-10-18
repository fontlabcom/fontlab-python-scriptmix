#FLM: Reports · Compare Open Font Revisions
# this_file: Scripts/Reports/Compare Open Font Revisions.py
# SPDX-License-Identifier: Apache-2.0
"""Compare named glyph fields in two explicitly chosen open font revisions.

Open both fonts, choose each font and master, then Compare and inspect the
changed-field details. Geometry, advances, anchors and components are read only;
raw node flags are listed separately. This does not claim complete font equality.
"""

from typing import Any

from fly.ap.scripting import revision_compare_dialog_type, show_script_dialog

KEY = "compare_open_font_revisions"


def main() -> Any:
    """Show the shared App comparison using its owned replacement and Close lifecycle."""
    return show_script_dialog(revision_compare_dialog_type(), KEY)


if __name__ == "__main__":
    main()
