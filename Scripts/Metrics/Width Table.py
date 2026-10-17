# this_file: Scripts/Metrics/Width Table.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Metrics · Width Table
"""Advance widths of the selected glyphs across all masters, sortable, with odd progressions flagged.

In a weight family the widths usually grow (or shrink) steadily from master to master. A glyph
whose width goes up and then down again is flagged: often a spacing slip. Click a column header
to sort; "Select flagged" selects those glyphs in the Font window. Nothing is edited."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package as current_package,  # noqa: PLC0414 - original public helper
)
from fly.ap.scripting import (
    inspectors_api,
    inspectors_dialog_type,
    inspectors_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = inspectors_api()
muted = _api.muted
selected_glyphs = _api.selected_glyphs
widths = _api.widths
progression = _api.progression
report = _api.report
TITLE = "Width Table"
KEY = "metrics_width_table"


class SampleDialog(inspectors_dialog_type()):
    """Original menu shell on the existing owned Proof/Names/Masters lifecycle."""

    def __init__(self, parent: Any = None) -> None:
        """Finish controls/status/Close before fallible font reads."""
        super().__init__(parent, TITLE, KEY)


def select_in_font(names: list[str]) -> None:
    """Select through the active panel's complete source and identity preflight."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


class WidthTable(SampleDialog):
    """Complete original inspector with complete snapshots and owned cleanup."""

    ACTION = "Select flagged"

    def build(self) -> None:
        """Retain every original control/default before reading native data."""
        self.setMinimumWidth(560)
        options = QtGui.QHBoxLayout()
        self.only_flagged = QtGui.QCheckBox("Show only mixed progressions")
        options.addWidget(self.only_flagged)
        options.addStretch(1)
        self.root.addLayout(options)

        headers = ["Glyph", *self.masters, "Progression"]
        self.table = QtGui.QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(240)
        self.root.addWidget(self.table, 1)

        self._connect(self.only_flagged.toggled, lambda *a: self.fill())

    def flagged(self) -> Any:
        """Return mixed progressions in captured glyph order."""
        return [name for name, _, trend in self.rows if trend == "mixed"]

    @inspectors_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete original report under the shared font/master snapshot guard."""
        self.glyphs = (
            [self.package.findName(name) for name in self.names] if self.package else []
        )
        if any(g is None or g.isNull for g in self.glyphs):
            raise ValueError("Selected glyph source changed; reopen this tool.")
        self.table.setColumnCount(len(self.masters) + 2)
        self.table.setHorizontalHeaderLabels(["Glyph", *self.masters, "Progression"])
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again.",
            )
        else:
            self.subtitle.setText(
                f"{count} glyph{'s' if count != 1 else ''} × {len(self.masters)} masters, "
                f"masters in font order: {' → '.join(self.masters)}",
            )
        self.rows = report(self.glyphs, self.masters)
        self.fill()

    def fill(self) -> None:
        """Render all original numeric cells, warning labels and exact mixed filter."""
        if self._snapshot_valid:
            self.ensure_snapshot()
        warn = QtGui.QColor("#d33")
        shown = [
            r for r in self.rows if not self.only_flagged.isChecked() or r[2] == "mixed"
        ]
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(shown))
        for row, (name, values, trend) in enumerate(shown):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(name))
            for column, value in enumerate(values, 1):
                item = QtGui.QTableWidgetItem("–")
                if value is not None:
                    item.setData(
                        QtCore.Qt.DisplayRole,
                        value,
                    )  # an int sorts numerically
                item.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                )
                self.table.setItem(row, column, item)
            flag = QtGui.QTableWidgetItem("⚠ mixed" if trend == "mixed" else trend)
            flag.setTextAlignment(int(QtCore.Qt.AlignCenter))
            if trend == "mixed":
                bold = flag.font()
                bold.setBold(True)
                flag.setFont(bold)
                flag.setForeground(QtGui.QBrush(warn))
            self.table.setItem(row, len(values) + 1, flag)
        self.table.setSortingEnabled(True)
        flagged = self.flagged()
        self.status.setText(
            f"{len(flagged)} of {len(self.rows)} glyphs with a mixed progression",
        )
        self.select_button.setEnabled(bool(flagged))

    def table_values(self) -> Any:
        """{glyph: [widths]} as shown (used by tests and handy for copying)."""
        out = {}
        for row in range(self.table.rowCount):
            name = self.table.item(row, 0).text()
            out[name] = [
                self.table.item(row, c).data(QtCore.Qt.DisplayRole)
                for c in range(1, len(self.masters) + 1)
            ]
        return out

    def select_flagged(self) -> None:
        """Preflight displayed widths before selecting exactly the mixed glyphs."""
        self.ensure_snapshot()
        flagged = self.flagged()
        self.select_names(flagged)
        fontlab.UpdateAll()
        self.status.setText(
            f"Selected {len(flagged)} glyph{'s' if len(flagged) != 1 else ''} in the Font window",
        )


def main() -> Any:
    """Replace and show the complete original owned inspector."""
    return show_script_dialog(WidthTable, KEY)


if __name__ == "__main__":
    main()
