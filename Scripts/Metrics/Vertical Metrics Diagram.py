# this_file: Scripts/Metrics/Vertical Metrics Diagram.py
# SPDX-License-Identifier: Apache-2.0
"""Compare the vertical metrics of every master with real outlines, side by side.

What it does: shows one column per master. Each column draws the outlines of
H, x, b and p from that master against its baseline, ascender, cap height,
x-height and descender lines. A cap height that misses the H, or an x-height
that cuts the x, shows at a glance. The panel only reads the font; it never
changes it.

How it works: the metric values come from FontMetrics(package, master) for
each master, the same reader as Masters > Overview, so the current master is
never switched. The outlines are read in place from each layer's contours,
with component transforms applied, into one QPainterPath per glyph. One scale
fits the tallest and the lowest metric of all masters and the widest sample
line, so the columns compare directly. Line names stand in the left margin.
A sample glyph that the font lacks, or that has no layer in a master, is
listed below the diagram and left out; it never stops the panel. Drawing
errors are kept in the panel and the painter always ends.

Why: wrong vertical metrics are easy to miss in a table of numbers and costly
to find late, in proofs or after export. A picture of all masters with their
own outlines makes the error visible before it spreads.

How to use: open a font and run the script. The panel stays open. Press
Reload after you change the metrics or the sample glyphs. To change the
values, use Font Info > Master Metrics Table (or FontLab's Font Info); this
diagram does not edit.

Benefit: a quick visual check of ascender, cap height, x-height and descender
against real letters in every master, without a risk to the font.

Credit: adapted from metrics_vertical_metrics_diagram.py, the author's own
FontLab sample, Apache-2.0. The editing part of that sample is left to Font
Info > Master Metrics Table.
"""

from dataclasses import dataclass
from typing import Any

import fly.ap.metrics_panel as metrics_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.script_completion as script_completion  # noqa: PLR0402 - same reason
from fly import ap, qt
from fly.ap.scripting import (
    close_script_dialog,
    connect_guarded,
    current_package,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Vertical Metrics Diagram"
KEY = "metrics_vertical_metrics_diagram"
#: (line name, FontMetrics attribute); the attributes are documented in the
#: Echopy stub fontlab.pyi (class FontMetrics) and used by fontlabapp.masters.
FIELDS = [
    ("Ascender", "ascender"),
    ("Cap height", "capsHeight"),
    ("x-height", "xHeight"),
    ("Descender", "descender"),
]
SAMPLE = ("H", "x", "b", "p")
LABEL_WIDTH = 84  # px: margin for the line names.
RIGHT_PAD = 16  # px after the last column.
HEAD = 22  # px: row for the master names.
FOOT = 12  # px below the lowest line.
TOP_MARGIN = 60  # units above the highest metric.
BOTTOM_MARGIN = 40  # units below the lowest metric.
FILL = 0.9  # Part of a column that the widest sample line may use.
LABEL_GAP = 16  # px between two line names in the margin.


# ---------------------------------------------------------------- core
@dataclass(frozen=True)
class Frame:
    """Map font units to widget pixels. y grows down in the widget."""

    left: float  # px: x of the first column.
    column: float  # px: width of one master column.
    scale: float  # px per unit.
    baseline: float  # px: y of the baseline.

    def x(self, index: int, units: float) -> float:
        """Pixel x of a unit offset inside column ``index``."""
        return self.left + index * self.column + units * self.scale

    def y(self, units: float) -> float:
        """Pixel y of a height in units."""
        return self.baseline - units * self.scale


def frame(
    width: float, height: float, metrics: list[dict[str, float]], sample_width: float
) -> Frame:
    """Fit all masters' metrics and the widest sample line into the widget.

    The scale is the smaller of the height fit (all lines, the baseline and
    the margins) and the width fit (``FILL`` of a column for the widest line).
    Vertical slack is split above and below.
    """
    top = max(max(values.values()) for values in metrics) + TOP_MARGIN
    bottom = min(0, *(min(values.values()) for values in metrics)) - BOTTOM_MARGIN
    column = (width - LABEL_WIDTH - RIGHT_PAD) / len(metrics)
    room = height - HEAD - FOOT
    scale = min(room / (top - bottom), column * FILL / max(sample_width, 1))
    baseline = HEAD + max(room - (top - bottom) * scale, 0) / 2 + top * scale
    return Frame(LABEL_WIDTH, column, scale, baseline)


def line_start(area: Frame, line_width: float) -> float:
    """Unit offset that centres a sample line of ``line_width`` units in a column."""
    return (area.column / area.scale - line_width) / 2


def read_metrics(package: Any, masters: list[str]) -> dict[str, dict[str, float]]:
    """{master: {attribute: value}} from FontMetrics; never switches the master."""
    found = {}
    for master in masters:
        values = ap.fontlab.FontMetrics(package, master)
        found[master] = {key: float(getattr(values, key)) for _, key in FIELDS}
    return found


def outline(layer: Any) -> Any:
    """The layer outline as one QPainterPath in font units; read in place."""
    path = QtGui.QPainterPath()
    path.setFillRule(QtCore.Qt.WindingFill)
    for shape in layer.shapes:
        part = QtGui.QPainterPath()
        for contour in shape.getContours():
            part.addPath(contour.path())
        path.addPath(shape.transform.map(part))
    return path


def collect(
    package: Any, masters: list[str]
) -> tuple[dict[str, list[tuple[str, Any, float]]], float, list[str]]:
    """Read the sample glyphs: ({master: [(name, path, advance)]}, widest line, notes)."""
    samples: dict[str, list[tuple[str, Any, float]]] = {m: [] for m in masters}
    notes: list[str] = []
    for name in SAMPLE:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            notes.append(f"{name}: not in this font")
            continue
        for master in masters:
            layer = glyph.findLayer(master)
            if layer is None or layer.isNull:
                notes.append(f"{name}: no layer in {master}")
                continue
            samples[master].append((name, outline(layer), float(layer.advanceWidth)))
    widest = max((sum(a for _, _, a in line) for line in samples.values()), default=0)
    return samples, widest, notes


# ---------------------------------------------------------------- panel
class Diagram(QtGui.QWidget):
    """One column per master: sample outlines plus labelled metric lines."""

    def __init__(self, owner: Any) -> None:
        """Keep the owner panel, which holds the data to draw."""
        QtGui.QWidget.__init__(self)
        self.owner = owner
        self.paint_error = ""
        self.setMinimumSize(560, 260)

    def paintEvent(self, event: Any) -> None:
        """Draw. An error is kept, never raised; the painter always ends."""
        painter = QtGui.QPainter(self)
        try:
            self.draw(painter, self.width, self.height)
            self.paint_error = ""
        except Exception as error:  # noqa: BLE001 - an error escaping paint can crash FontLab
            self.paint_error = repr(error)
        finally:
            painter.end()

    def draw(self, painter: Any, width: float, height: float) -> None:
        """Paint the background, then every master column."""
        owner = self.owner
        palette = self.palette
        painter.fillRect(
            QtCore.QRectF(0, 0, width, height), palette.color(QtGui.QPalette.Base)
        )
        masters = [m for m in owner.masters if m in owner.metrics]
        if not masters:
            painter.setPen(QtGui.QColor(metrics_panel.muted(self)))
            painter.drawText(
                QtCore.QRectF(0, 0, width, height),
                int(QtCore.Qt.AlignCenter),
                "No metrics to show.",
            )
            return
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        area = frame(
            width, height, [owner.metrics[m] for m in masters], owner.sample_width
        )
        ink = QtGui.QColor(palette.color(QtGui.QPalette.WindowText))
        guide = QtGui.QColor(palette.color(QtGui.QPalette.Mid))
        small = painter.font()
        small.setPointSizeF(max(small.pointSizeF() * 0.85, 8))
        painter.setFont(small)
        for index, master in enumerate(masters):
            self.draw_column(painter, area, index, master, ink, guide)

    def draw_column(
        self, painter: Any, area: Frame, index: int, master: str, ink: Any, guide: Any
    ) -> None:
        """Master name, metric lines, the sample outlines; line names in column 0."""
        values = self.owner.metrics[master]
        left = area.x(index, 0)
        painter.setPen(ink)
        painter.drawText(
            QtCore.QRectF(left, 0, area.column, HEAD),
            int(QtCore.Qt.AlignCenter),
            master,
        )
        lines = [("Baseline", 0.0)] + [(label, values[key]) for label, key in FIELDS]
        painter.setPen(QtGui.QPen(QtGui.QBrush(guide), 1.0))
        for _, units in lines:
            painter.drawLine(
                QtCore.QPointF(left + 6, area.y(units)),
                QtCore.QPointF(left + area.column - 6, area.y(units)),
            )
        if index == 0:
            self.draw_labels(painter, [(area.y(u), label) for label, u in lines])
        line = self.owner.samples.get(master, [])
        pen = line_start(area, sum(advance for _, _, advance in line))
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(ink))
        for _, path, advance in line:
            painter.save()
            painter.translate(area.x(index, pen), area.baseline)
            painter.scale(area.scale, -area.scale)
            painter.drawPath(path)
            painter.restore()
            pen += advance

    def draw_labels(self, painter: Any, labels: list[tuple[float, str]]) -> None:
        """Line names right-aligned in the margin, pushed apart when lines are close."""
        painter.setPen(QtGui.QColor(metrics_panel.muted(self)))
        last = None
        for y, label in sorted(labels):
            if last is not None and y < last + LABEL_GAP:
                y = last + LABEL_GAP
            painter.drawText(
                QtCore.QRectF(0, y - 9, LABEL_WIDTH - 6, 18),
                int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                label,
            )
            last = y


class VerticalMetricsDiagram(QtGui.QDialog):
    """Read-only, non-modal panel: the diagram, notes, Reload and Close."""

    def __init__(self, parent: Any = None) -> None:
        """Build all widgets first, then read the font."""
        QtGui.QDialog.__init__(self, parent)
        self._connections: list[Any] = []
        self._completion_lifetime = script_completion.install(self, KEY)
        self.masters: list[str] = []
        self.metrics: dict[str, dict[str, float]] = {}
        self.samples: dict[str, list[tuple[str, Any, float]]] = {}
        self.sample_width = 0.0
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(640)
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
        self.subtitle.setStyleSheet(f"color: {metrics_panel.muted(self)};")
        root.addWidget(self.subtitle)
        self.diagram = Diagram(self)
        root.addWidget(self.diagram, 1)
        self.notes_label = QtGui.QLabel()
        self.notes_label.setWordWrap(True)
        self.notes_label.setStyleSheet(f"color: {metrics_panel.muted(self)};")
        root.addWidget(self.notes_label)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {metrics_panel.muted(self)};")
        footer.addWidget(self.status, 1)
        self.reload_button = QtGui.QPushButton("Reload")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.reload_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        connect_guarded(self, self.reload_button.clicked, lambda *a: self.reload())
        connect_guarded(self, self.close_button.clicked, lambda *a: self.close())
        self.reload()

    def reload(self) -> None:
        """Read metrics and sample outlines of the current font again."""
        self.masters, self.metrics, self.samples, self.sample_width = [], {}, {}, 0.0
        self.notes_label.setText("")
        try:
            package = current_package()
            if package is None:
                self.subtitle.setText("Open a font. Then press Reload.")
                self.status.setText("")
                return
            self.masters = list(package.masters)
            self.metrics = read_metrics(package, self.masters)
            self.samples, self.sample_width, notes = collect(package, self.masters)
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.metrics = {}
            self.status.setText(f"Error: {error}")
            return
        finally:
            self.diagram.update()
        self.subtitle.setText(
            f"{' '.join(SAMPLE)} from each master against its own lines. "
            "Read only: edit the values in Font Info > Master Metrics Table."
        )
        self.notes_label.setText(" · ".join(notes))
        found = sum(
            1 for name in SAMPLE if not any(n.startswith(f"{name}: not") for n in notes)
        )
        count = len(self.masters)
        self.status.setText(
            f"{count} master{'s' if count != 1 else ''} · {found} of {len(SAMPLE)} sample glyphs"
        )

    def closeEvent(self, event: Any) -> None:
        """Disconnect owned signals, drop the outlines, then delete the panel."""
        self.samples = {}
        close_script_dialog(self, event, KEY)


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    return show_script_dialog(VerticalMetricsDiagram, KEY)


if __name__ == "__main__":
    main()
