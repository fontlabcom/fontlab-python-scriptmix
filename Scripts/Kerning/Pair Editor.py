# this_file: Scripts/Kerning/Pair Editor.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Pair Editor
"""Edit every kerning pair that involves one glyph, with one column per master.

What it does:
    Rows are the pairs where the glyph, or a kerning class it belongs to, is on the left or right.
    Type a new value in any master's cell; clear a cell to delete that pair on that master. Edited
    cells turn the accent colour until Apply, which writes all of them as one Undo step. Add a row
    for a new partner with the field under the table.

How it works:
    Collect pairs involving the glyph or its applicable classes and stage
    editable master cells. Treat an empty cell as deletion and validate new
    side-specific partners.

Why this design:
    Staged cells let the user review several master changes before the shared
    writer checks and commits the complete batch.

How to use:
    Run Kerning > Pair Editor. Choose a glyph, edit values or add a partner
    row, inspect highlighted changes and press Apply. Clear a cell only when
    that stored pair should be deleted.

Benefit:
    Edit related explicit pairs together; Apply is recorded as one Undo step.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    kerning_edit_dialog_type,
    kerning_editor_api,
)
from fly.ap.scripting import (
    kerning_editor_apply as editor_apply,
)
from fly.ap.scripting import (
    kerning_editor_refresh as editor_refresh,
)
from fly.ap.scripting import (
    names_muted as muted,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
api = kerning_editor_api()
KerningEditDialog = kerning_edit_dialog_type()
native_side = api.native_side
current_package = ap.scripting.current_package
kerning_pairs = ap.scripting.kerning_pairs

TITLE = "Kerning Pair Editor"
KEY = "kerning_pair_editor"


def write_kerning(
    package: Any, edits: dict[str, dict[tuple[str, str], int | None]]
) -> None:
    """Apply a fully validated multi-master batch using the tool's native Undo label."""
    api.write_kerning(package, edits, TITLE)


class_sides, involving, parse_cell = api.class_sides, api.involving, api.parse_cell


def current_glyph_name(package: Any) -> str | None:
    """Keep the original Font-window selection, then current-glyph fallback."""
    names = ap.scripting.names_selected_names() if package is not None else []
    return names[0] if names else None


class PairEditor(KerningEditDialog):
    """Retain the complete original Pair Editor workflow with shared native safety."""

    def __init__(self, parent: Any = None) -> None:
        """Create all original controls on the shared snapshot-bound owned panel."""
        KerningEditDialog.__init__(self, parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(560)
        self.resize(600, 620)
        self.glyph = current_glyph_name(self.package) if self.package else None
        self.rows = {}
        self.order = []
        self.staged = {}
        self.filling = False
        self.table = QtGui.QTableWidget(0, len(self.masters) + 1)
        self.table.setHorizontalHeaderLabels(["Pair", *self.masters])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(260)
        root.addWidget(self.table, 1)
        add = QtGui.QHBoxLayout()
        add.setSpacing(8)
        self.side = QtGui.QComboBox()
        self.side.addItem(f"{self.glyph or '…'}  +  partner")
        self.side.addItem(f"partner  +  {self.glyph or '…'}")
        self.partner = QtGui.QLineEdit()
        self.partner.setPlaceholderText("Partner glyph or @class")
        self.add_button = QtGui.QPushButton("Add row")
        add.addWidget(QtGui.QLabel("New pair"))
        add.addWidget(self.side)
        add.addWidget(self.partner, 1)
        add.addWidget(self.add_button)
        root.addLayout(add)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.revert_button = QtGui.QPushButton("Revert")
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.revert_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)
        self.add_refresh(footer, self.load)
        self._connect(self.table.itemChanged, self.cell_edited)
        self._connect(self.add_button.clicked, lambda *a: self.add_row())
        self._connect(self.partner.returnPressed, lambda *a: self.add_row())
        self._connect(self.revert_button.clicked, lambda *a: self.load())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.load()

    @editor_refresh
    def load(self) -> None:
        """Discard staged cells and read the complete original-font pair table."""
        self.staged = {}
        self.errors = {}
        self.rows = (
            involving(self.package, self.masters, self.glyph)
            if self.package and self.glyph
            else {}
        )
        self.order = sorted(
            self.rows,
            key=lambda p: (p[0] != self.glyph and (not p[0].startswith("@")), p),
        )
        self.fill()

    def fill(self) -> None:
        """Rebuild the table (never called from inside its own itemChanged signal)."""
        self.filling = True
        self.table.setRowCount(len(self.order))
        for row, pair in enumerate(self.order):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}"))
            for column, master in enumerate(self.masters, 1):
                value = self.staged.get(
                    (pair, master), self.rows.get(pair, {}).get(master)
                )
                item = QtGui.QTableWidgetItem(
                    self.errors.get(
                        (pair, master), "" if value is None else f"{value:g}"
                    )
                )
                item.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                )
                self.table.setItem(row, column, item)
        self.filling = False
        self.refresh()

    def cell_edited(self, item: Any) -> None:
        """Stage valid cell input; keep invalid feedback without losing other edits."""
        if self.filling:
            return
        if item.column() == 0:
            self.filling = True
            pair = self.order[item.row()]
            item.setText(f"{pair[0]}  {pair[1]}")
            self.filling = False
            return
        (pair, master) = (self.order[item.row()], self.masters[item.column() - 1])
        self.ensure_edit_snapshot()
        error = self.stage_editor_cell(
            pair, master, item.text(), self.rows.get(pair, {}).get(master)
        )
        self.refresh()
        if error:
            self.status.setText(error)

    def set_cell(self, left: str, right: str, master: str, text: str) -> None:
        """Type into a cell, as a user would (used by tests and handy from the console)."""
        (row, column) = (
            self.order.index((left, right)),
            self.masters.index(master) + 1,
        )
        self.table.item(row, column).setText(text)

    def add_row(self) -> None:
        """Add a valid side-specific glyph/class partner without writing font data."""
        partner = self.partner.text.strip()
        if not partner or self.glyph is None:
            return
        self.ensure_edit_snapshot()
        pair = (
            (self.glyph, partner)
            if self.side.currentIndex == 0
            else (partner, self.glyph)
        )
        if not api.partner_exists(self.package, self.masters, pair):
            self.status.setText(f"No glyph or side-compatible class named “{partner}”")
            return
        if pair not in self.order:
            self.order.append(pair)
            self.fill()
        self.partner.setText("")

    def refresh(self) -> None:
        """Render preview values and counts; enable Apply only for actual staged edits."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif self.glyph is None:
            self.subtitle.setText(
                "Select a glyph in the Font window, then run this script again."
            )
        else:
            (left, right) = class_sides(self.package, self.masters[0], self.glyph)
            classes = ", ".join(c for c in (left, right) if c) or "no kerning class"
            self.subtitle.setText(
                f"Pairs with {self.glyph} ({classes}) on either side. Empty cell = no pair; clear a cell to delete that pair."
            )
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        plain = QtGui.QColor(self.palette.color(QtGui.QPalette.WindowText))
        self.filling = True
        for row, pair in enumerate(self.order):
            for column, master in enumerate(self.masters, 1):
                item = self.table.item(row, column)
                if item is None:
                    continue
                staged = (pair, master) in self.staged
                bold = item.font()
                bold.setBold(staged)
                item.setFont(bold)
                item.setForeground(QtGui.QBrush(accent if staged else plain))
        self.filling = False
        count = len(self.staged)
        self.status.setText(
            f"{count} edited cell{('s' if count != 1 else '')}"
            if count
            else f"{len(self.order)} pairs"
        )
        self.apply_button.setEnabled(bool(count))
        self.revert_button.setEnabled(bool(count or self.errors))
        if self.errors:
            self.status.setText(
                f"{count} valid edited cells; {len(self.errors)} invalid cells ignored. Correct them or Revert."
            )

    @editor_apply
    def apply(self) -> None:
        """Write the complete displayed batch, refresh its baseline and report counts."""
        edits = {}
        for (pair, master), value in self.staged.items():
            edits.setdefault(master, {})[pair] = value
        self.write_edits(edits, TITLE)
        self.last_result = {m: len(p) for (m, p) in edits.items()}
        fontlab.UpdateAll()
        self.refresh_after_apply(self.load)
        self.status.setText(
            f"Wrote {sum(self.last_result.values())} cells in {len(edits)} masters"
        )


def main() -> Any:
    """Replace only this tool's registry entry and show the owned modeless dialog."""
    return ap.scripting.show_script_dialog(PairEditor, KEY)


if __name__ == "__main__":
    main()
