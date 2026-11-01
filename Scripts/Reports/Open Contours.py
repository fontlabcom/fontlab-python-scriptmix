# this_file: Scripts/Reports/Open Contours.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Reports · Open Contours
"""Find open contours on every master and select the glyphs that have them.

What it does:
    Open paths are usually unintended in a font for filling: they render
    unpredictably and break overlap removal. Each row is one open contour with
    its master, node count and the gap between its end points. Nothing in the
    font changes.

How it works:
    Scan glyph layers on every declared master. For each open contour, list
    its node count and the distance between its end points; keep source
    identity for selection.

Why this design:
    An open contour can be intentional, so the report identifies it for review
    rather than closing paths automatically.

How to use:
    Run Reports > Open Contours. Inspect the glyph, master and gap columns.
    Select report rows to locate their glyphs in the Font window, then review
    the actual paths.

Benefit:
    Find open-path candidates across masters without changing their topology
    or geometry.
"""

import contextlib
import math
from collections.abc import Callable
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package, select_glyphs

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Open Contours"
KEY = "report_open_contours"


# ---------------------------------------------------------------- font access
# ---------------------------------------------------------------- core
def scan(package: Any) -> list[tuple]:
    """[(glyph, master, contour index, node count, gap)] for every open contour, font order."""
    font = fontlab.CurrentFont()
    masters = list(package.masters)
    out = []
    for fg in font.glyphs:
        glyph = package.findName(fg.name)
        if glyph is None:
            continue
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None:
                continue
            for index, contour in enumerate(layer.getContours()):
                if contour.closed:
                    continue
                nodes = contour.nodes()
                gap = 0.0
                if len(nodes) > 1:
                    first, last = nodes[0], nodes[len(nodes) - 1]
                    gap = math.hypot(last.x - first.x, last.y - first.y)
                out.append((fg.name, master, index, len(nodes), round(gap, 1)))
    return out


# ---------------------------------------------------------------- GUI
def muted(widget: Any) -> str:
    """Return a translucent text colour matching the current native palette."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class OpenContours(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the modeless report with native Qt controls and guarded signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette  # FontLab can pair a light Base with a light Text (seen in dark mode): use WindowText
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(500)
        self.resize(540, 440)
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

        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Glyph", "Master", "Contour", "Nodes", "End gap"],
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.rescan_button = QtGui.QPushButton("Rescan")
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select glyphs")
        self.select_button.setDefault(True)
        footer.addWidget(self.rescan_button)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

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
            rows = scan(package)
            glyphs = sorted({r[0] for r in rows})
            if rows:
                self.subtitle.setText(
                    f"{len(rows)} open contour{'s' if len(rows) != 1 else ''} in "
                    f"{len(glyphs)} glyph{'s' if len(glyphs) != 1 else ''} across "
                    f"{len(package.masters)} masters.",
                )
            else:
                self.subtitle.setText(
                    f"No open contours on any of {len(package.masters)} masters.",
                )
            alert = QtGui.QColor("#d33")
            self.table.setRowCount(len(rows))
            for row, values in enumerate(rows):
                for column, value in enumerate(values):
                    item = QtGui.QTableWidgetItem(
                        str(value) if column != 2 else f"#{value + 1}",
                    )
                    if column >= 2:
                        item.setTextAlignment(
                            int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                        )
                    if column == 4 and value > 0:
                        item.setForeground(QtGui.QBrush(alert))
                    self.table.setItem(row, column, item)
            self.status.setText(
                "Double-click a row to select that glyph." if rows else "",
            )
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


def main() -> OpenContours:
    """Show the persistent modeless report."""
    return ap.scripting.show_script_dialog(OpenContours, KEY)


if __name__ == "__main__":
    main()
