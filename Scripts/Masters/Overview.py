# this_file: Scripts/Masters/Overview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Masters · Masters Overview
"""One table of all masters: axis location, vertical metrics and italic angle.

Rows follow the font's master order; the current master is bold. Vertical metrics come from
``fontlab.FontMetrics(package, master)``; FontLab has no per-master italic-angle accessor, so each
master is made current for the read and the original master is restored. Double-click a row to
make that master current. Read-only otherwise.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - original public interface
    masters_api,
    masters_dialog_type,
    masters_snapshot_refresh,
    show_script_dialog,
)
from fly.ap.scripting import (
    masters_fill_table as fill_table,
)
from fly.ap.scripting import (
    masters_make_table as make_table,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = masters_api()
muted = _api.muted
selected_names = _api.selected_names
location_text = _api.location_text
italic_angles = _api.italic_angles
overview = _api.overview
TITLE = "Masters Overview"
KEY = "masters_overview"
METRICS = [
    ("Ascender", "ascender"),
    ("Cap height", "capsHeight"),
    ("x-height", "xHeight"),
    ("Descender", "descender"),
]


class SampleDialog(masters_dialog_type()):
    """Keep the original per-menu shell interface on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Build every control before initial binding or native reads."""
        super().__init__(parent, TITLE, KEY)


class Overview(SampleDialog):
    """Complete original read-only Masters tool with guarded native actions."""

    ACTION = None

    def build(self) -> None:
        """Build every original chart/table/tree control and guarded action connection."""
        self.setMinimumWidth(680)
        headers = (
            ["Master", "Location"]
            + [label for (label, _) in METRICS]
            + ["Italic angle"]
        )
        self.table = make_table(headers, 200)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QtGui.QHeaderView.ResizeToContents
        )
        self.root.addWidget(self.table, 1)
        self._connect(
            self.table.cellDoubleClicked, lambda row, column, *a: self.make_current(row)
        )
        hint = QtGui.QLabel(
            "Double-click a master to make it current. Values that differ between masters are highlighted."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(hint)

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Read and render complete results from the original bound font and selection."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            self.rows = []
            return
        self.rows = overview(self.package)
        axes = ", ".join(f"{a.name} ({a.tag})" for a in self.package.axes) or "no axes"
        self.subtitle.setText(f"{len(self.rows)} masters · {axes}")
        varies = {c for c in range(2, 7) if len({row[c] for row in self.rows}) > 1}
        cells = [
            (r[0], r[1], *tuple(f"{v:g}" for v in r[2:6]), f"{r[6]:g}°")
            for r in self.rows
        ]
        fill_table(self.table, cells, lambda r, c, text: c in varies)
        current = self.package.master
        for row, cells_row in enumerate(cells):
            if cells_row[0] == current:
                item = self.table.item(row, 0)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setText(cells_row[0] + "  (current)")
        self.status.setText(f"Current master: {current}")

    def make_current(self, row: Any) -> None:
        """Refuse changed displayed source before the original explicit UI action."""
        self.ensure_snapshot()
        master = self.rows[row][0]
        self.package.setMaster(master, True)
        fontlab.UpdateAll()
        self.refresh()


def main() -> Any:
    """Replace and show this owned original Masters tool."""
    return show_script_dialog(Overview, KEY)


if __name__ == "__main__":
    main()
