# this_file: Scripts/Components/Where Used.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Where Used
"""Find every glyph that uses a given glyph as a component, on any master.

What it does:
    Type a glyph name (the field completes as you type). The table lists the composites,
    the masters where the component appears and whether those layers are auto layers.
    Click a row to select that glyph in the Font window; "Select all" selects them all.

How it works:
    Search component references on all masters through App and list the owning
    composite glyphs. Keep the captured source guarded when selecting results.

Why this design:
    Reverse lookup shows which composites need review after a base glyph
    changes, without rewriting those composites.

How to use:
    Run Components > Where Used. Enter a base glyph name, inspect the
    composites and master columns, then click a row or use Select all to
    select the results.

Benefit:
    Trace component use across masters while leaving references, transforms
    and outlines intact.
"""

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
current_name = _api.current_name
usage_index = _api.usage_index
item_ink = _api.item_ink
muted = _api.muted
frame = _api.frame

TITLE = "Where Is It Used?"
KEY = "components_where_used"


class WhereUsed(components_dialog_type()):
    """Complete original component inspector with owned read-only source guards."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control and Close before reading native sources."""
        super().__init__(parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(520)
        self.search = QtGui.QLineEdit(current_name() if self.package else "")
        self.search.setPlaceholderText("glyph name, e.g. period")
        self.search.setClearButtonEnabled(True)
        completer = QtGui.QCompleter(sorted(self.index), self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setFilterMode(QtCore.Qt.MatchContains)
        self.search.setCompleter(completer)
        root.addWidget(self.search)
        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Composite", "Masters", "Layers"])
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
        header.setSectionResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(280)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select all")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)
        self._connect(self.search.textChanged, lambda *a: self.refresh())
        self._connect(self.table.cellClicked, lambda row, column: self.pick(row))
        self._connect(self.select_button.clicked, lambda *a: self.select_all())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    @components_action
    def refresh(self) -> None:
        """Preserve the original refresh calculation and native interface."""
        if self._scanning and self.package is not None:
            self.index = usage_index(self.package, self.names, self.masters)
            completer = QtGui.QCompleter(sorted(self.index), self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setFilterMode(QtCore.Qt.MatchContains)
            self.search.setCompleter(completer)
        name = self.search.text.strip()
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            self.subtitle.setText(
                f"{len(self.index)} glyphs are used as components in this font. Click a row to select that composite in the Font window."
            )
        users = self.index.get(name, {})
        self.rows = [n for n in self.names if n in users]
        dim = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        dim.setAlpha(140)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setRowCount(len(self.rows))
        for row, composite in enumerate(self.rows):
            entries = users[composite]
            auto = sum(1 for (_, a) in entries if a)
            kind = "auto" if auto == len(entries) else "mixed" if auto else "components"
            for column, text in enumerate(
                (composite, ", ".join(m for (m, _) in entries), kind)
            ):
                item = QtGui.QTableWidgetItem(text)
                item.setForeground(item_ink())
                if column == 2:
                    item.setForeground(QtGui.QBrush(dim if kind == "auto" else accent))
                self.table.setItem(row, column, item)
        self.select_button.setEnabled(bool(self.rows))
        if not name:
            self.status.setText("Type a glyph name")
        elif self.package is not None and self.package.findName(name) is None:
            self.status.setText(f"No glyph named “{name}”")
        else:
            self.status.setText(
                f"{name} is used by {len(self.rows)} glyph{('s' if len(self.rows) != 1 else '')}"
            )

    @components_action
    def pick(self, row: Any) -> None:
        """Preserve the original pick calculation and native interface."""
        self.select_names([self.rows[row]])
        self.status.setText(f"Selected {self.rows[row]} in the Font window")

    @components_action
    def select_all(self) -> None:
        """Preserve the original select all calculation and native interface."""
        self.select_names(self.rows)
        self.status.setText(f"Selected {len(self.rows)} glyphs in the Font window")


def select_in_font(names: list[str]) -> None:
    """Route the original helper alias through the active panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


def main() -> Any:
    """Replace and display the complete original owned component inspector."""
    return show_script_dialog(WhereUsed, KEY)


if __name__ == "__main__":
    main()
