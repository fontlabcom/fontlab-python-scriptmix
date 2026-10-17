# this_file: Scripts/Reports/Nodes Near Zones.py
# SPDX-License-Identifier: Apache-2.0
"""Find on-curve nodes that sit within a few units of a vertical metric but not on it.

Near misses (y = 687 when the cap height is 688) are almost always slips
of the mouse; real overshoots are further away and pass. Checks baseline,
x-height, cap height, ascender and descender of every master. Select the
glyphs to fix them. Nothing in the font changes.
"""

import contextlib
import sys
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package, select_glyphs

fontlab = ap.fontlab
(QtCore, QtGui) = (qt.QtCore, qt.QtGui)
TITLE = "Nodes Near Zones"
KEY = "report_nodes_near_zones"


def selected_names() -> Any:
    """Return selected Font window glyph names in font order."""
    try:
        FL = ap.FL
        font = FL.fl.font
        return [font[i].name for i in range(len(font)) if FL.fl.Selected(i)]
    except (AttributeError, RuntimeError, TypeError):
        return []


def master_metrics(package: Any, master: Any) -> Any:
    """[(label, y)] vertical metrics of one master."""
    m = fontlab.FontMetrics(package, master)
    return [
        ("baseline", 0.0),
        ("x-height", m.xHeight),
        ("cap height", m.capsHeight),
        ("ascender", m.ascender),
        ("descender", m.descender),
    ]


def on_curve_points(layer: Any) -> Any:
    """[(x, y)] of the layer's own on-curve nodes with each shape's transform applied."""
    points = []
    for shape in layer.shapes:
        if shape.shapeData is not None and shape.shapeData.componentGlyph:
            continue
        transform = shape.transform
        for contour in shape.getContours():
            for node in contour.nodes():
                if node.isOn():
                    p = transform.map(QtCore.QPointF(node.x, node.y))
                    points.append((p.x(), p.y()))
    return points


def near_misses(points: Any, metrics: Any, tolerance: Any) -> Any:
    """[(label, metric y, node x, node y)] for points with 0 < |y - metric| <= tolerance."""
    out = []
    for x, y in points:
        for label, value in metrics:
            delta = y - value
            if 0 < abs(delta) <= tolerance:
                out.append((label, value, x, y))
    return out


def scan(package: Any, names: Any, tolerance: Any) -> Any:
    """[(glyph, master, metric label, metric y, node x, node y)]."""
    masters = list(package.masters)
    metrics = {m: master_metrics(package, m) for m in masters}
    rows = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None:
            continue
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None:
                continue
            rows.extend(
                (name, master, *hit)
                for hit in near_misses(
                    on_curve_points(layer), metrics[master], tolerance
                )
            )
    return rows


def muted(widget: Any) -> Any:
    """Muted."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class NodesNearZones(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the original modeless report controls and connect owned signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(560)
        self.resize(600, 500)
        self._connections = []
        self.rows = []
        self.package = current_package()
        self.selection = selected_names() if self.package else []
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
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Selected glyphs ({len(self.selection)})")
        self.scope.addItem("All glyphs")
        self.tolerance = QtGui.QSpinBox()
        self.tolerance.setRange(1, 30)
        self.tolerance.setValue(4)
        self.tolerance.setSuffix(" units")
        self.tolerance.setAlignment(QtCore.Qt.AlignRight)
        form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        form.addWidget(self.scope, 0, 1)
        form.addWidget(QtGui.QLabel("Within"), 0, 2)
        form.addWidget(self.tolerance, 0, 3)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.table = QtGui.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Glyph · master", "Metric", "Node", "y", "Off by"]
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
        self._connect(self.scope.currentIndexChanged, lambda *a: self.rescan())
        self._connect(self.tolerance.valueChanged, lambda *a: self.rescan())
        self._connect(self.rescan_button.clicked, lambda *a: self.rescan())
        self._connect(self.select_button.clicked, lambda *a: self.select_rows())
        self._connect(
            self.table.cellDoubleClicked, lambda row, *a: self.select_rows([row])
        )
        self._connect(self.close_button.clicked, lambda *a: self.close())
        if not self.selection:
            self.scope.setCurrentIndex(1)
        self.rescan()

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

    def rescan(self) -> None:
        """Scan the current font and publish results only after display succeeds."""
        self.package_id = None
        self.rows = []
        self.select_button.setEnabled(False)
        self.table.setRowCount(0)
        try:
            self.package = current_package()
            self.selection = selected_names() if self.package else []
            if self.package is None:
                self.subtitle.setText("Open a font first.")
                self.select_button.setEnabled(False)
                return
            font = fontlab.CurrentFont()
            names = (
                self.selection
                if self.scope.currentIndex == 0
                else [g.name for g in font.glyphs]
            )
            tolerance = self.tolerance.value
            result_rows = scan(self.package, names, tolerance)
            glyphs = sorted({r[0] for r in result_rows})
            self.subtitle.setText(
                f"{len(names)} glyphs × {len(self.package.masters)} masters checked: on-curve nodes 1–{tolerance} units off baseline, x-height, cap height, ascender or descender."
            )
            alert = QtGui.QColor("#d33")
            self.table.setRowCount(len(result_rows))
            for row, (name, master, label, value, x, y) in enumerate(result_rows):
                cells = [
                    f"{name} · {master}",
                    f"{label} {value:g}",
                    f"{x:g}, {y:g}",
                    f"{y:g}",
                    f"{y - value:+g}",
                ]
                for column, text in enumerate(cells):
                    item = QtGui.QTableWidgetItem(text)
                    if column >= 2:
                        item.setTextAlignment(
                            int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                        )
                    if column == 4:
                        item.setForeground(QtGui.QBrush(alert))
                    self.table.setItem(row, column, item)
            self.select_button.setEnabled(bool(result_rows))
            self.status.setText(
                f"{len(result_rows)} near miss{('es' if len(result_rows) != 1 else '')} in {len(glyphs)} glyph{('s' if len(glyphs) != 1 else '')}"
            )
            self.rows = result_rows
            self.package_id = self.package.id
        except Exception:
            self.package_id = None
            self.rows = []
            self.select_button.setEnabled(False)
            self.table.setRowCount(0)
            raise

    def select_rows(self, rows: Any = None) -> None:
        """Select requested report rows only in the font that produced them."""
        if self.package_id is None:
            raise ValueError("Refresh the report before selecting glyphs.")
        package = current_package()
        if package is None or package.id != self.package_id:
            raise ValueError("stale font: Refresh the report.")
        if rows is None:
            rows = sorted(
                {index.row() for index in self.table.selectionModel().selectedRows()}
            )
            rows = rows or list(range(len(self.rows)))
        names = [self.rows[r][0] for r in rows if 0 <= r < len(self.rows)]
        selected = select_glyphs(names, package_id=self.package_id)
        self.last_result = {"selected": selected}
        self.status.setText(
            f"Selected {len(selected)} glyph{('s' if len(selected) != 1 else '')}"
        )

    def closeEvent(self, event: Any) -> None:
        """Disconnect owned signals and release this modeless window."""
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
    dialog = NodesNearZones(fontlab.MainWindow())
    windows[KEY] = dialog
    dialog.show()
    dialog.raise_()
    return dialog


if __name__ == "__main__":
    main()
