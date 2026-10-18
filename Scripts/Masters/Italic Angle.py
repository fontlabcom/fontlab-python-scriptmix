# this_file: Scripts/Masters/Italic Angle.py
# SPDX-License-Identifier: Apache-2.0
"""Stage each master's italic angle, preview its slant and Apply in one Undo.

The font remains unchanged until Apply. Reopen after changing fonts, masters or
their source angles. Close disconnects all owned signals and painter callbacks.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - Original public helper interface.
    master_angles_api,
    master_angles_dialog_type,
    master_angles_view_types,
    masters_make_table,
    masters_view_types,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Italic Angle", "masters_italic_angle"
_api, _views = master_angles_api(), master_angles_view_types()
read_angles, write_angles = _api.italic_angles, _api.write_angles
compact, readable, Gauge = _views.compact, _views.readable, _views.Gauge
make_table, series_colors = masters_make_table, masters_view_types().series_colors


class SampleDialog(master_angles_dialog_type()):
    """Preserve the original script-side shell and class interface."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent, TITLE, KEY)


class ItalicAngle(SampleDialog):
    """Complete original staged editor on the shared owned native lifecycle."""


def main() -> Any:
    """Replace and show only this script's owned panel."""
    return show_script_dialog(ItalicAngle, KEY)


if __name__ == "__main__":
    main()
