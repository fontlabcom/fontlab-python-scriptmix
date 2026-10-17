# this_file: Scripts/Reports/Live Glyph Info.py
# SPDX-License-Identifier: Apache-2.0
"""A live panel for the glyph you are working on: widths, side-bearings, bounds and counts per master.

It follows the first glyph selected in the Font window (or the glyph being
edited) and re-reads it twice a second, so edits show up as you make them.
Values that differ between masters stand out. Nothing in the font changes.
"""

import contextlib
import sys
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package

fontlab = ap.fontlab
(QtCore, QtGui) = (qt.QtCore, qt.QtGui)
TITLE = "Glyph Info Live"
KEY = "report_glyph_info_live"
POLL_MS = 500
COLUMNS = [
    "Master",
    "Width",
    "LSB",
    "RSB",
    "Bounds (x, y, w, h)",
    "Contours",
    "Nodes",
    "Components",
    "Anchors",
]


def focused_name() -> Any:
    """First glyph selected in the Font window, else the current glyph."""
    try:
        FL = ap.FL
        font = FL.fl.font
        for i in range(len(font)):
            if FL.fl.Selected(i):
                return font[i].name
    except (AttributeError, RuntimeError, TypeError):
        pass
    glyph = fontlab.CurrentGlyph()
    return glyph.name if glyph is not None else None


def component_names(layer: Any) -> Any:
    """Return component base names in the layer shape order."""
    names = []
    for shape in layer.shapes:
        base = shape.shapeData.componentGlyph if shape.shapeData is not None else ""
        if base:
            names.append(base)
    return names


def layer_info(layer: Any) -> Any:
    """[width, lsb, rsb, bounds, contours, nodes, components, anchors] for one layer (display strings)."""
    box = layer.boundingBox
    width = layer.advanceWidth
    contours = layer.getContours()
    drawn = box.width() > 0 or box.height() > 0
    lsb = f"{box.x():g}" if drawn else "–"
    rsb = f"{width - box.x() - box.width():g}" if drawn else "–"
    bounds = (
        f"{box.x():g}, {box.y():g}, {box.width():g}, {box.height():g}"
        if drawn
        else "empty"
    )
    nodes = sum(len(c.nodes()) for c in contours)
    components = ", ".join(component_names(layer)) or "–"
    return [
        f"{width:g}",
        lsb,
        rsb,
        bounds,
        str(len(contours)),
        str(nodes),
        components,
        str(len(layer.anchors)),
    ]


def glyph_info(package: Any, name: Any) -> Any:
    """[(master, values)] for every master of the glyph."""
    glyph = package.findName(name)
    if glyph is None:
        return []
    rows = []
    for master in package.masters:
        layer = glyph.findLayer(master)
        if layer is not None:
            rows.append((master, layer_info(layer)))
    return rows


def muted(widget: Any) -> Any:
    """Muted."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class GlyphInfoLive(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the original modeless report controls and connect owned signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(680)
        self.resize(760, 300)
        self._connections = []
        (self.shown_name, self.rows) = (None, [])
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
        self.glyph_label = QtGui.QLabel()
        big = self.glyph_label.font
        big.setPointSizeF(big.pointSizeF() * 1.6)
        big.setBold(True)
        self.glyph_label.setFont(big)
        self.glyph_label.setStyleSheet(
            f"color: {self.palette.color(QtGui.QPalette.Link).name()};"
        )
        root.addWidget(self.glyph_label)
        self.table = QtGui.QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(7, QtGui.QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.pause = QtGui.QCheckBox("Pause")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.pause)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(POLL_MS)
        self._connect(self.timer.timeout, lambda *a: self.poll())
        self._connect(
            self.pause.toggled,
            lambda checked, *a: self.timer.stop() if checked else self.timer.start(),
        )
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()
        self.timer.start()

    def _connect(self, signal: Any, slot: Any) -> None:
        """Guard and retain a signal connection for deterministic teardown."""

        def guarded(*args) -> None:
            """Guarded."""
            try:
                slot(*args)
            except Exception as error:  # noqa: BLE001 - PythonQt slots must contain all errors
                self.slot_error = repr(error)
                label = getattr(self, "status", None)
                if label is not None:
                    label.setText("Error: " + self.slot_error)

        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def poll(self) -> None:
        """Refresh from the current font on each timer tick."""
        self.refresh()

    def refresh(self, name: Any = None) -> None:
        """Rebuild the current snapshot and publish it only after display succeeds."""
        self.package_id = None
        self.shown_name = None
        self.rows = []
        self.glyph_label.setText("–")
        self.table.setRowCount(0)
        try:
            package = current_package()
            name = name or (focused_name() if package else None)
            rows = glyph_info(package, name) if package and name else []
            (result_shown_name, result_rows) = (name, rows)
            if package is None or not rows:
                self.glyph_label.setText("–")
                self.subtitle.setText(
                    "Open a font and select a glyph."
                    if package is None
                    else "Select a glyph in the Font window."
                )
                self.table.setRowCount(0)
                return
            codes = " ".join(
                f"U+{c:04X}" for c in package.findName(name).fgGlyph.unicodes
            )
            self.glyph_label.setText(f"{name}  {codes}")
            self.subtitle.setText(
                f"Follows the Font window selection · refreshes every {POLL_MS} ms · values that differ between masters are highlighted."
            )
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            self.table.setRowCount(len(rows))
            for row, (master, values) in enumerate(rows):
                self.table.setItem(row, 0, QtGui.QTableWidgetItem(master))
                for column, text in enumerate(values, start=1):
                    item = QtGui.QTableWidgetItem(text)
                    if column in {1, 2, 3, 5, 6, 8}:
                        item.setTextAlignment(
                            int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                        )
                    if (
                        column in {5, 6, 7}
                        and len({v[column - 1] for (_, v) in rows}) > 1
                    ):
                        item.setForeground(QtGui.QBrush(accent))
                    self.table.setItem(row, column, item)
            self.status.setText(
                f"Updated {QtCore.QTime.currentTime().toString('HH:mm:ss')}"
            )
            self.shown_name = result_shown_name
            self.rows = result_rows
            self.package_id = package.id
        except Exception:
            self.package_id = None
            self.shown_name = None
            self.rows = []
            self.glyph_label.setText("–")
            self.table.setRowCount(0)
            raise

    def closeEvent(self, event: Any) -> None:
        """Disconnect owned signals and release this modeless window."""
        self.timer.stop()
        for signal, slot in self._connections:
            with contextlib.suppress(Exception):
                signal.disconnect(slot)
        self._connections = []
        getattr(sys, "_fontlab_samples", {}).pop(KEY, None)
        QtGui.QDialog.closeEvent(self, event)


def main() -> Any:
    """Replace the previous owned report window and show a modeless instance."""
    windows = sys.__dict__.setdefault("_fontlab_samples", {})
    old = windows.pop(KEY, None)
    if old is not None:
        old.close()
    dialog = GlyphInfoLive(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
