# this_file: Scripts/Components/Report.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Components Report
"""List every composite layer in the font: base and mark names, offsets and auto-layer status.

The table covers the current master or all masters, filters as you type and can
be copied to the clipboard as CSV for a spreadsheet. Double-click a row to make
that glyph current in FontLab. Nothing in the font is changed."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    components_api,
    components_dialog_type,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = components_api()
current_package = _api.current_package
font_glyph_names = _api.font_glyph_names
component_rows = _api.component_rows
report = _api.report
to_csv = _api.to_csv
item_ink = _api.item_ink
muted = _api.muted

TITLE = "Components Report"
KEY = "components_report"
COLUMNS = ["Glyph", "Master", "Components", "Offsets", "Layer"]


class ComponentsReport(components_dialog_type()):
    """Complete original component inspector with owned read-only source guards."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control and Close before reading native sources."""
        super().__init__(parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(680)
        bar = QtGui.QHBoxLayout()
        bar.setSpacing(10)
        self.filter = QtGui.QLineEdit()
        self.filter.setPlaceholderText("Filter by glyph, component or “auto”")
        self.filter.setClearButtonEnabled(True)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        bar.addWidget(self.filter, 1)
        bar.addWidget(self.scope)
        root.addLayout(bar)
        self.table = QtGui.QTableWidget(len(self.rows), len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        for column in (0, 1, 4):
            header.setSectionResizeMode(column, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(320)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.copy_button = QtGui.QPushButton("Copy CSV")
        self.copy_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.copy_button)
        root.addLayout(footer)
        self._connect(self.filter.textChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
        self._connect(
            self.table.cellDoubleClicked, lambda row, column: self.open_glyph(row)
        )
        self._connect(self.copy_button.clicked, lambda *a: self.copy_csv())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def matches(self, values: Any) -> Any:
        """Preserve the original matches calculation and native interface."""
        needle = self.filter.text.strip().lower()
        if self.scope.currentIndex == 0 and values[1] != self.current_master:
            return False
        return not needle or any(needle in str(v).lower() for v in values)

    def visible_rows(self) -> Any:
        """Preserve the original visible rows calculation and native interface."""
        return [values for values in self.rows if self.matches(values)]

    @components_action
    def refresh(self) -> None:
        """Preserve the original refresh calculation and native interface."""
        if self._scanning and self.package is not None:
            self.rows = report(self.package, self.names, self.masters)
        self.table.setRowCount(len(self.rows))
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        dim = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        dim.setAlpha(140)
        for row, values in enumerate(self.rows):
            for column, text in enumerate(values):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(item_ink())
                if column == 4:
                    item.setForeground(QtGui.QBrush(dim if text == "auto" else accent))
                self.table.setItem(row, column, item)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            glyphs = len({r[0] for r in self.rows})
            auto = sum(1 for r in self.rows if r[4] == "auto")
            self.subtitle.setText(
                f"{glyphs} composite glyphs · {len(self.rows)} layers with components, {auto} of them auto layers. Double-click a row to open the glyph."
            )
        shown = 0
        for row, values in enumerate(self.rows):
            hide = not self.matches(values)
            self.table.setRowHidden(row, hide)
            shown += not hide
        self.copy_button.setEnabled(shown > 0)
        self.status.setText(f"{shown} of {len(self.rows)} rows shown")

    def csv_text(self) -> Any:
        """Preserve the original csv text calculation and native interface."""
        return to_csv(self.visible_rows())

    @components_action
    def copy_csv(self) -> None:
        """Preserve the original copy csv calculation and native interface."""
        QtGui.QApplication.clipboard().setText(self.csv_text())
        self.status.setText(f"Copied {len(self.visible_rows())} rows as CSV")

    @components_action
    def open_glyph(self, row: Any) -> None:
        """Preserve the original open glyph calculation and native interface."""
        glyph = self.package.findName(self.rows[row][0]) if self.package else None
        if glyph is not None:
            self.package.activateGlyph(glyph)
            fontlab.UpdateAll()


def select_in_font(names: list[str]) -> None:
    """Route the original helper alias through the active panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


def main() -> Any:
    """Replace and display the complete original owned component inspector."""
    return show_script_dialog(ComponentsReport, KEY)


if __name__ == "__main__":
    main()
