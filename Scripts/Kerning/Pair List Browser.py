# this_file: Scripts/Kerning/Pair List Browser.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Pair List
"""Browse every kerning pair of a master: filter, sort by any column, export to CSV.

What it does:
    Type in the filter to keep pairs whose left or right side contains the text (glyph or @class
    name); "=" anchors a whole side, so "=T" shows pairs with exactly T on one side. Click a header
    to sort; values sort numerically. Export writes the pairs shown to a CSV file. Read-only.

How it works:
    Read explicit pairs on the chosen master and filter either side by
    substring or exact equals-prefixed name. Export rows in the table's
    displayed order.

Why this design:
    Numeric value sorting and exact-side filtering help isolate a pair set
    without changing its stored values.

How to use:
    Run Kerning > Pair List Browser. Choose a master, enter a filter, sort by
    a header and use Export to save the shown rows as CSV.

Benefit:
    Inspect and share an explicit kerning subset while retaining all glyph and
    class pairs.
"""

import csv
import pathlib
from typing import Any

from fly import ap, qt

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
# The tiny facade stays lazy until a native menu script asks for its panel.
from fly.ap.scripting import (
    kerning_dialog_type,
    kerning_pairs,
)
from fly.ap.scripting import (
    kerning_snapshot_refresh as snapshot_refresh,
)
from fly.ap.scripting import (
    names_muted as muted,
)

KerningDialog = kerning_dialog_type()

TITLE = "Kerning Pairs"
KEY = "kerning_list_browser"


# ---------------------------------------------------------------- core
def matches(pair: tuple[str, str], text: str) -> bool:
    """Filter rule: substring of either side; '=name' must equal a whole side."""
    text = text.strip()
    if not text:
        return True
    if text.startswith("="):
        return text[1:] in pair
    return any(text in side for side in pair)


def filtered(
    pairs: dict[tuple[str, str], float], text: str
) -> list[tuple[str, str, float]]:
    """Return matching explicit pairs in stable name order."""
    return sorted((l, r, v) for (l, r), v in pairs.items() if matches((l, r), text))


def export_csv(
    rows: list[tuple[str, str, float]], master: str, path: str | pathlib.Path
) -> int:
    """Write left,right,value,master rows; returns the number of pairs written."""
    with pathlib.Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["left", "right", "value", "master"])
        for left, right, value in rows:
            writer.writerow([left, right, f"{value:g}", master])
    return len(rows)


# ---------------------------------------------------------------- GUI


class PairList(KerningDialog):
    """Retain the original Pair List Browser controls on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize owned controls without changing the font."""
        KerningDialog.__init__(self, parent, TITLE, KEY)

        self.pairs, self.rows = {}, []
        root = self.root

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        self.filter = QtGui.QLineEdit()
        self.filter.setPlaceholderText("Filter: T, @L_A, =V …")
        self.filter.setClearButtonEnabled(True)
        form.addWidget(QtGui.QLabel("Master"), 0, 0)
        form.addWidget(self.master, 0, 1)
        form.addWidget(QtGui.QLabel("Filter"), 1, 0)
        form.addWidget(self.filter, 1, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Left", "Right", "Value"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(260)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        self.status.setWordWrap(True)
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.export_button = QtGui.QPushButton("Export CSV…")
        self.export_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.export_button)
        root.addLayout(footer)

        self._connect(self.master.currentIndexChanged, lambda *a: self.load())
        self._connect(self.filter.textChanged, lambda *a: self.fill())
        self._connect(self.export_button.clicked, lambda *a: self.ask_path())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.load()

    def chosen_master(self) -> str:
        """Return the master named by the original combo box."""
        return self.masters[self.master.currentIndex] if self.masters else ""

    @snapshot_refresh
    def load(self) -> None:
        """Read explicit pairs on the chosen master and refresh the table."""
        self.pairs = (
            kerning_pairs(self.package, self.chosen_master()) if self.package else {}
        )
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            classes = sum(
                1 for l, r in self.pairs if l.startswith("@") or r.startswith("@")
            )
            self.subtitle.setText(
                f"{self.chosen_master()}: {len(self.pairs)} pairs, {classes} of them with a class side",
            )
        self.fill()

    @snapshot_refresh
    def fill(self) -> None:
        """Render the complete filtered rows from the current snapshot."""
        self.rows = filtered(self.pairs, self.filter.text)
        accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.rows))
        for row, (left, right, value) in enumerate(self.rows):
            for column, text in enumerate((left, right)):
                item = QtGui.QTableWidgetItem(text)
                if text.startswith("@"):
                    item.setForeground(QtGui.QBrush(accent))
                self.table.setItem(row, column, item)
            item = QtGui.QTableWidgetItem()
            item.setData(
                QtCore.Qt.DisplayRole,
                int(value) if value == int(value) else value,
            )
            item.setTextAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
            self.table.setItem(row, 2, item)
        self.table.setSortingEnabled(True)
        shown = (
            f"{len(self.rows)} of {len(self.pairs)} pairs"
            if self.filter.text.strip()
            else f"{len(self.rows)} pairs"
        )
        self.status.setText(shown)
        self.export_button.setEnabled(bool(self.rows))

    def shown_rows(self) -> Any:
        """Rows in the table's current (possibly sorted) order."""
        return [
            (
                self.table.item(row, 0).text(),
                self.table.item(row, 1).text(),
                float(self.table.item(row, 2).data(QtCore.Qt.DisplayRole)),
            )
            for row in range(self.table.rowCount)
        ]

    def ask_path(self) -> None:
        """Non-modal save dialog (open(), never a blocking modal loop): FontLab keeps running."""
        self.ensure_snapshot()
        if self.file_dialog is None:
            dialog = QtGui.QFileDialog(self, "Export kerning pairs")
            dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            dialog.setNameFilter("CSV files (*.csv)")
            dialog.setDefaultSuffix("csv")
            dialog.setOption(QtGui.QFileDialog.DontUseNativeDialog, True)
            self._connect(dialog.fileSelected, self.export)
            self.file_dialog = dialog
        self.file_dialog.selectFile(f"kerning-{self.chosen_master()}.csv")
        self.file_dialog.open()

    def export(self, path: str) -> int:
        """Export actual shown table order after checking the complete snapshot."""
        self.ensure_snapshot()
        count = export_csv(self.shown_rows(), self.chosen_master(), path)
        self.last_export = {"path": path, "pairs": count}
        self.status.setText(f"Exported {count} pairs to {pathlib.Path(path).name}")
        return count


def main() -> Any:
    """Replace the original registry window and show this owned modeless panel."""
    return ap.scripting.show_script_dialog(PairList, KEY)


if __name__ == "__main__":
    main()
