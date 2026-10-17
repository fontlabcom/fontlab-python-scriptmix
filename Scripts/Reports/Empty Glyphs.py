# this_file: Scripts/Reports/Empty Glyphs.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Empty Glyphs
"""List glyphs that have no outlines and no components on some or all masters, and select them.

A glyph empty on one master but drawn on others is usually a mistake;
spaces are empty on purpose and can be hidden. Each master is a column.
Select puts the listed glyphs (or the rows you pick) into the Font window
selection. Nothing in the font changes.
"""

import contextlib
import unicodedata
from collections.abc import Callable
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package, select_glyphs

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Empty Glyphs"
KEY = "report_empty_glyphs"


# ---------------------------------------------------------------- font access
# ---------------------------------------------------------------- core
def is_empty(layer: Any) -> bool:
    """Nothing drawn: no contours, counting the contours of its components."""
    return not layer.getContours()


def is_whitespace(name: str, codes: list[int]) -> bool:
    """Recognise intentional empty glyphs by Unicode category and conventional names."""
    if any(
        unicodedata.category(chr(c)) in {"Zs", "Zl", "Zp", "Cc", "Cf"} for c in codes
    ):
        return True
    return name in {
        ".notdef",
        ".null",
        "nbspace",
        "space",
        "CR",
        "nonmarkingreturn",
    } or name.endswith("space")


def scan(package: Any, skip_whitespace: bool) -> list[tuple]:
    """[(glyph name, [master, ...] where empty)] in font order."""
    font = fontlab.CurrentFont()
    masters = list(package.masters)
    out = []
    for fg in font.glyphs:
        if skip_whitespace and is_whitespace(fg.name, list(fg.unicodes)):
            continue
        glyph = package.findName(fg.name)
        if glyph is None:
            continue
        empty = []
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None or is_empty(layer):
                empty.append(master)
        if empty:
            out.append((fg.name, empty))
    return out


# ---------------------------------------------------------------- GUI
def muted(widget: Any) -> str:
    """Return a translucent text colour matching the current native palette."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class EmptyGlyphs(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the modeless report with native Qt controls and guarded signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(520)
        self.resize(560, 460)
        self._connections = []
        self.rows = []
        self.package_id: int | None = None

        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.skip_whitespace = QtGui.QCheckBox(
            "Hide space-like glyphs (empty on purpose)",
        )
        self.skip_whitespace.setChecked(True)
        root.addWidget(self.skip_whitespace)

        self.table = QtGui.QTableWidget(0, 1)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.rescan_button = QtGui.QPushButton("Rescan")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select in Font window")
        self.select_button.setDefault(True)
        footer.addWidget(self.rescan_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.skip_whitespace.toggled, lambda *a: self.rescan())
        self._connect(self.rescan_button.clicked, lambda *a: self.rescan())
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(
            self.table.cellDoubleClicked,
            lambda row, *a: self.select_rows([row]),
        )
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.rescan()

    def _connect(self, signal: Any, slot: Callable[..., Any]) -> None:
        """Connect through the shared guarded native lifecycle."""
        ap.scripting.connect_guarded(self, signal, slot)

    def rescan(self) -> None:
        """Publish selectable rows only after the complete scan and display succeed.

        Invalidate the previous snapshot before native access. Any scan or Qt
        failure clears partial results and leaves explicit selection refused.
        """
        self.package_id = None
        self.rows = []
        try:
            self.select_button.setEnabled(False)
            package = current_package()
            if package is None:
                self.rows = []
                self.package_id = None
                self.table.setRowCount(0)
                self.status.setText("No font open.")
                self.subtitle.setText("Open a font first.")
                self.select_button.setEnabled(False)
                return
            masters = list(package.masters)
            rows = scan(package, self.skip_whitespace.isChecked())
            partial = sum(1 for _, empty in rows if len(empty) < len(masters))
            self.subtitle.setText(
                f"{len(rows)} glyph{'s' if len(rows) != 1 else ''} without outlines on at "
                f"least one of {len(masters)} masters; {partial} only on some (likely mistakes).",
            )
            self.table.clear()
            self.table.setColumnCount(1 + len(masters))
            self.table.setHorizontalHeaderLabels(["Glyph", *masters])
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            alert = QtGui.QColor("#d33")
            soft = QtGui.QColor(muted(self))
            self.table.setRowCount(len(rows))
            for row, (name, empty) in enumerate(rows):
                self.table.setItem(row, 0, QtGui.QTableWidgetItem(name))
                for column, master in enumerate(masters, start=1):
                    item = QtGui.QTableWidgetItem("empty" if master in empty else "✓")
                    item.setTextAlignment(int(QtCore.Qt.AlignCenter))
                    item.setForeground(QtGui.QBrush(alert if master in empty else soft))
                    self.table.setItem(row, column, item)
            self.status.setText("Double-click a row to select it.")
            self.rows = rows
            self.package_id = package.id
            self.select_button.setEnabled(bool(rows))
        except Exception:  # Invalidate on any native or Qt failure, then propagate.
            self.package_id = None
            self.rows = []
            with contextlib.suppress(Exception):
                self.select_button.setEnabled(False)
            with contextlib.suppress(Exception):
                self.table.setRowCount(0)
            raise

    def select_rows(self, rows: list[int] | None = None) -> None:
        """Select chosen report rows, or all rows, only in the scanned font."""
        if rows is None:
            rows = sorted(
                {index.row() for index in self.table.selectionModel().selectedRows()},
            )
            rows = rows or list(range(len(self.rows)))
        names = [self.rows[r][0] for r in rows if 0 <= r < len(self.rows)]
        if self.package_id is None:
            raise ValueError("Refresh the report with an open font first.")
        selected = select_glyphs(names, package_id=self.package_id)
        self.last_result = {"selected": selected}
        self.status.setText(
            f"Selected {len(selected)} glyph{'s' if len(selected) != 1 else ''}",
        )

    def closeEvent(self, event: Any) -> None:
        """Release the owned report and its connections."""
        ap.scripting.close_script_dialog(self, event, KEY)


def main() -> EmptyGlyphs:
    """Show the persistent modeless report."""
    return ap.scripting.show_script_dialog(EmptyGlyphs, KEY)


if __name__ == "__main__":
    main()
