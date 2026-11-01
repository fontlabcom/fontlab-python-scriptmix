# this_file: Scripts/Contours/Contour Order View.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Contour Order View
"""Show every master of a glyph side by side with numbered contours, start points and directions.

What it does:
    Each contour carries its index at the start node, a dot on the start node and an arrow along
    its first segment, so start-point and order mismatches between masters are visible at a glance
    before interpolation surprises you. Read-only: nothing in the font changes.

How it works:
    Use the shared contour-order view to draw each master and label contour
    indices, start nodes and first-segment directions at their native
    positions.

Why this design:
    A structural count cannot reveal a different start point or contour order;
    the drawing exposes those differences directly.

How to use:
    Select a glyph and run Contours > Contour Order View. Compare matching
    contour numbers and direction arrows between the master panels before
    editing compatibility.

Benefit:
    Review contour order and starts without reversing paths or changing
    interpolation structure.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package as current_package,  # noqa: PLC0414 - original public helper
)
from fly.ap.scripting import (
    inspectors_api,
    inspectors_dialog_type,
    inspectors_snapshot_refresh,
    inspectors_view_types,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = inspectors_api()
muted = _api.muted
selected_names = _api.selected_names
master_layers = _api.master_layers
own_contours = _api.own_contours
node_points = _api.node_points
signed_area = _api.signed_area
contour_info = _api.contour_info
OrderView = inspectors_view_types().OrderView
outline_path = inspectors_view_types().outline_path
fit_transform = inspectors_view_types().fit_transform
TITLE = "Contour Order View"
KEY = "outlines_contour_order_view"


class SampleDialog(inspectors_dialog_type()):
    """Original menu shell on the existing owned Proof/Names/Masters lifecycle."""

    def __init__(self, parent: Any = None) -> None:
        """Finish controls/status/Close before fallible font reads."""
        super().__init__(parent, TITLE, KEY)


class ContourOrder(SampleDialog):
    """Complete original inspector with complete snapshots and owned cleanup."""

    ACTION = None

    def build(self) -> None:
        """Create every original control and guarded signal before native reads."""
        self.setMinimumWidth(640)
        grid = self.form()
        self.glyph_combo = QtGui.QComboBox()
        for name in self.names:
            self.glyph_combo.addItem(name)
        self._connect(self.glyph_combo.currentIndexChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyph"), 0, 0)
        grid.addWidget(self.glyph_combo, 0, 1)
        grid.setColumnStretch(1, 1)
        self.view = OrderView()
        self.view.report = self.paint_report
        self.root.addWidget(self.view, 1)
        legend = QtGui.QLabel(
            "● start node · number = contour order · arrow = direction of the first segment",
        )
        legend.setStyleSheet(f"color: {muted(self)};")
        self.root.addWidget(legend)

    @inspectors_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete original report under the shared font/master snapshot guard."""
        self.sync_controls()
        self.info = {}
        if not self.describe_selection():
            self.view.columns = []
            self.view.update()
            return
        glyph = self.package.findName(self.glyph_combo.currentText)
        columns = []
        for master, layer in master_layers(glyph, self.masters).items():
            info = [] if layer.autoLayer else contour_info(layer)
            self.info[master] = [
                (i, start, direction, len(points))
                for i, points, start, _, direction in info
            ]
            columns.append((master + (" (auto)" if layer.autoLayer else ""), info))
        self.view.columns = columns
        self.view.update()
        counts = {len(v) for v in self.info.values()}
        note = (
            "contour counts match"
            if len(counts) == 1
            else "contour counts differ between masters"
        )
        self.status.setText(f"{glyph.name}: {len(columns)} masters · {note}")


def main() -> Any:
    """Replace and show the complete original owned inspector."""
    return show_script_dialog(ContourOrder, KEY)


if __name__ == "__main__":
    main()
