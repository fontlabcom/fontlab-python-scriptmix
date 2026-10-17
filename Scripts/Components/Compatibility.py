# this_file: Scripts/Components/Compatibility.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Compatibility
"""Compare component names and order across masters; glyphs that differ cannot interpolate their components.

One row per composite glyph, one column per master. Masters whose component list
differs from the first master are shown in red, and mismatching glyphs are listed
first. Double-click a row to select the glyph in the Font window. Nothing is changed."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    components_api,
    components_dialog_type,
    components_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = components_api()
current_package = _api.current_package
font_glyph_names = _api.font_glyph_names
selected_names = _api.selected_names
component_lists = _api.component_lists
odd_masters = _api.odd_masters
item_ink = _api.item_ink
muted = _api.muted
frame = _api.frame

TITLE = "Component Compatibility"
KEY = "components_compatibility"
ERROR = "#d33"


class Compatibility(components_dialog_type()):
    """Complete original component inspector with owned read-only source guards."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control and Close before reading native sources."""
        super().__init__(parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(680)
        bar = QtGui.QHBoxLayout()
        bar.setSpacing(10)
        self.scope = QtGui.QComboBox()
        self.scope.addItem("Whole font")
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.only_bad = QtGui.QCheckBox("Only mismatches")
        bar.addWidget(QtGui.QLabel("Glyphs"))
        bar.addWidget(self.scope)
        bar.addStretch(1)
        bar.addWidget(self.only_bad)
        root.addLayout(bar)
        self.table = QtGui.QTableWidget(0, len(self.masters) + 1)
        self.table.setHorizontalHeaderLabels(["Glyph", *self.masters])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(320)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select mismatches")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)
        self._connect(self.scope.currentIndexChanged, lambda *a: self.rescan())
        self._connect(self.only_bad.toggled, lambda *a: self.refresh())
        self._connect(
            self.table.cellDoubleClicked, lambda row, column: self.open_row(row)
        )
        self._connect(
            self.select_button.clicked, lambda *a: self.select_names(self.mismatches())
        )
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    @components_snapshot_refresh
    def rescan(self) -> None:
        """Preserve the original rescan calculation and native interface."""
        self.table.setColumnCount(len(self.masters) + 1)
        self.table.setHorizontalHeaderLabels(["Glyph", *self.masters])
        names = font_glyph_names() if self.scope.currentIndex == 0 else self.selection
        self.rows = (
            component_lists(self.package, names, self.masters) if self.package else []
        )
        self.refresh()

    def mismatches(self) -> Any:
        """Preserve the original mismatches calculation and native interface."""
        return [name for (name, lists) in self.rows if odd_masters(lists, self.masters)]

    @components_action
    def refresh(self) -> None:
        """Preserve the original refresh calculation and native interface."""
        bad = set(self.mismatches())
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText(
                f"{len(self.rows)} composite glyphs compared across {len(self.masters)} masters. Red cells differ from the first master."
            )
        error = QtGui.QColor(ERROR)
        self.shown = [
            r
            for r in sorted(self.rows, key=lambda r: r[0] not in bad)
            if not self.only_bad.isChecked() or r[0] in bad
        ]
        self.table.setRowCount(len(self.shown))
        for row, (name, lists) in enumerate(self.shown):
            odd = set(odd_masters(lists, self.masters))
            item = QtGui.QTableWidgetItem(name)
            item.setForeground(item_ink())
            if name in bad:
                bold = item.font()
                bold.setBold(True)
                item.setFont(bold)
            self.table.setItem(row, 0, item)
            for column, master in enumerate(self.masters, 1):
                cell = QtGui.QTableWidgetItem(" + ".join(lists.get(master, [])) or "–")
                cell.setForeground(item_ink())
                if master in odd:
                    cell.setForeground(QtGui.QBrush(error))
                self.table.setItem(row, column, cell)
        self.select_button.setEnabled(bool(bad))
        self.status.setText(
            f"{len(bad)} glyph{('s' if len(bad) != 1 else '')} with incompatible components"
            if bad
            else "All composites have the same components on every master"
        )

    @components_action
    def open_row(self, row: Any) -> None:
        """Preserve the original open row calculation and native interface."""
        name = self.shown[row][0]
        self.select_names([name])
        self.status.setText(f"Selected {name} in the Font window")


def select_in_font(names: list[str]) -> None:
    """Route the original helper alias through the active panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


def main() -> Any:
    """Replace and display the complete original owned component inspector."""
    return show_script_dialog(Compatibility, KEY)


if __name__ == "__main__":
    main()
