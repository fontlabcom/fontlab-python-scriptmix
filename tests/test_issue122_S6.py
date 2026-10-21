# this_file: tests/test_issue122_S6.py
# SPDX-License-Identifier: Apache-2.0
"""Eleven Contours scripts on owned FontLab/Qt fakes.

The scripts run unchanged. Only the native modules `fontlab`, `fontgate`,
`FL` and `PythonQt` are fakes; `fly` and the App modules
(`fontlabapp.scripting`, `history`, `edit_guards`, `affine`,
`contour_selection`) are the real packages.
Offline results never prove native FontLab behaviour.
"""

import ast
import itertools
import math
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
ISOLATED = ("fly", "fontlabapp", "echopy")  # packages this file re-imports for itself
FOLDER = ROOT / "Scripts/Contours"
STEMS = {
    "Round Coordinates": "outlines_round_coordinates",
    "Remove Overlap": "outlines_remove_overlap",
    "Add Extremes": "outlines_add_extremes",
    "Correct Contour Direction": "outlines_correct_direction",
    "Straighten Short Curves": "outlines_straighten_short_curves",
    "Optimize Start Points": "outlines_optimize_start_points",
    "Delete Small Contours": "outlines_delete_small_contours",
    "Fix Zero Handles": "outlines_fix_zero_handles",
    "Delete Duplicate Contours": "outlines_delete_duplicate_contours",
    "Transform": "outlines_transform_dialog",
    "Slant": "outlines_slant",
}
NAMES = list(STEMS)
TRANSFORMS = {"Transform", "Slant"}
# App modules a script may hold; load() checks that each is the real one.
APP_MODULES = (
    "history",
    "edit_guards",
    "affine",
    "contour_selection",
    "outline_writer",
    "outline_panel",
    "outline_transform",
)
# Kernel, panel and transform-writer names that live only in the App
# (fly.ap.outline_writer, outline_panel, outline_transform), never in a script.
SHARED = {
    "Work", "Point", "MAX_ROWS", "EPSILON", "COMPATIBLE_LABEL", "BASES_LABEL", "Change",
    "Plan", "Planner", "plural", "fmt", "layer_of", "shown", "node_points", "translation",
    "outline_shapes", "note_rows", "held_back", "collect", "require_safe", "settle",
    "Editor", "apply_work", "ERROR_COLOR", "ink", "muted", "readable_palette",
    "OutlinePanel", "Affine", "ORIGIN_NEAR", "FIT_MARGIN", "bakes", "transform_changes",
    "TransformEditor", "layer_outline", "mapped", "outline_path", "fit", "OutlinePreview",
    "TransformPanel",
}  # fmt: skip
STRUCTURAL = [
    "Remove Overlap",
    "Add Extremes",
    "Straighten Short Curves",
    "Delete Small Contours",
    "Fix Zero Handles",
    "Delete Duplicate Contours",
]
# Members of QWidget/QDialog/QPaintDevice that a Python subclass must not shadow:
# PythonQt raises "Slot ... can not be overwritten".
NATIVE_MEMBERS = {
    "metric", "update", "layout", "font", "palette", "parent", "style", "size",
    "pos", "width", "height", "geometry", "show", "hide", "open", "done", "accept",
    "reject", "exec", "repaint", "move", "resize", "rect", "title", "name",
    "windowTitle", "objectName", "children", "focus", "enabled", "visible",
    "actions", "cursor", "locale", "mask", "scroll", "find", "close", "render",
    "statusBar", "grab", "lower", "raise_", "x", "y", "frameGeometry",
}  # fmt: skip


# ---------------------------------------------------------------- Qt fakes
class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


SIGNALS = {"clicked", "toggled", "valueChanged", "currentIndexChanged", "timeout"}


class Widget:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.enabled = True
        self.text = ""

    def __getattr__(self, name: str) -> Any:
        if name in SIGNALS:
            signal = Signal()
            setattr(self, name, signal)
            return signal
        if name.startswith(
            ("set", "add", "insert", "block", "show", "raise", "resize", "vertical")
        ):
            return lambda *args, **kwargs: Widget()
        raise AttributeError(name)

    def setEnabled(self, flag: bool) -> None:
        self.enabled = flag

    def setText(self, text: str) -> None:
        self.text = text

    def horizontalHeader(self) -> "Widget":
        return Widget()


class Guarded(Widget):
    """Base of fakes that a script subclasses: native member names are refused."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in NATIVE_MEMBERS and type(self).__module__ != __name__:
            raise AttributeError(f"Slot '{name}' can not be overwritten")
        object.__setattr__(self, name, value)


class Font:
    def pointSizeF(self) -> float:
        return 10.0

    def __getattr__(self, name: str) -> Any:
        return lambda *args: None


class Color:
    HexArgb = 1

    def __init__(self, value: Any = 0) -> None:
        self.value = value.value if isinstance(value, Color) else value

    def lightness(self) -> int:
        return 128 if not isinstance(self.value, int) else self.value

    def name(self, fmt: Any = None) -> str:
        return "#808080" if not isinstance(self.value, str) else self.value

    def setAlpha(self, value: int) -> None:
        pass


class Palette:
    Active, Inactive, Base, Text, WindowText, Link = range(6)

    def color(self, *args: Any) -> Color:
        return Color(100)

    def setColor(self, *args: Any) -> None:
        pass


class Label(Widget):
    def __init__(self, text: str = "", *args: Any) -> None:
        super().__init__()
        self.text = text
        self.font = Font()


class CheckBox(Widget):
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.label, self.checked = text, False

    def setChecked(self, flag: bool) -> None:
        self.checked = flag
        self.toggled.emit(flag)

    def isChecked(self) -> bool:
        return self.checked


class Combo(Widget):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[str] = []
        self.currentIndex = -1

    def addItem(self, text: str) -> None:
        self.items.append(text)
        self.currentIndex = max(self.currentIndex, 0)

    def setItemText(self, index: int, text: str) -> None:
        self.items[index] = text

    def setCurrentIndex(self, index: int) -> None:
        self.currentIndex = index
        self.currentIndexChanged.emit(index)


class Spin(Widget):
    """QSpinBox: `value` is a property in PythonQt; setRange checks the type."""

    INTEGER = True

    def __init__(self) -> None:
        super().__init__()
        self.value, self.low, self.high = 0, 0, 99

    def setRange(self, low: Any, high: Any) -> None:
        if self.INTEGER and not (isinstance(low, int) and isinstance(high, int)):
            raise TypeError("QSpinBox.setRange wants int")
        self.low, self.high = low, high

    def setValue(self, value: Any) -> None:
        if self.INTEGER and not isinstance(value, int):
            raise TypeError("QSpinBox.setValue wants int")
        self.value = min(max(value, self.low), self.high)
        self.valueChanged.emit(self.value)


class DoubleSpin(Spin):
    INTEGER = False


class Button(Widget):
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.text = text


class Item:
    def __init__(self, text: str = "") -> None:
        self._text = text
        self.foreground: Any = None

    def setForeground(self, brush: Any) -> None:
        self.foreground = brush

    def text(self) -> str:
        return self._text


class Table(Widget):
    def __init__(self, rows: int = 0, columns: int = 0) -> None:
        super().__init__()
        self.cells: dict[tuple[int, int], Item] = {}
        self.rows = rows

    def setRowCount(self, rows: int) -> None:
        self.rows = rows
        self.cells = {k: v for k, v in self.cells.items() if k[0] < rows}

    def setItem(self, row: int, column: int, item: Item) -> None:
        self.cells[(row, column)] = item

    def row_texts(self) -> list[list[str]]:
        columns = max((c for _, c in self.cells), default=-1) + 1
        return [
            [self.cells[(r, c)].text() for c in range(columns) if (r, c) in self.cells]
            for r in range(self.rows)
        ]

    def colors(self) -> list[Any]:
        """Foreground colour value of the last cell of each row."""
        columns = max((c for _, c in self.cells), default=-1) + 1
        return [
            self.cells[(r, columns - 1)].foreground.color().value
            for r in range(self.rows)
        ]


class Dialog(Guarded):
    registry: ClassVar[list[Any]] = []
    palette = Palette()

    def __init__(self, parent: Any = None) -> None:
        object.__setattr__(self, "deleted", False)
        object.__setattr__(self, "shown", False)
        object.__setattr__(self, "core_closed", 0)
        object.__setattr__(self, "enabled", True)
        object.__setattr__(self, "text", "")
        Dialog.registry.append(self)

    def closeEvent(self, event: Any) -> None:
        object.__setattr__(self, "core_closed", self.core_closed + 1)

    def close(self) -> bool:
        self.closeEvent(object())
        return True

    def show(self) -> None:
        object.__setattr__(self, "shown", True)

    def deleteLater(self) -> None:
        object.__setattr__(self, "deleted", True)


class QWidget(Guarded):
    """QWidget base of the preview: width/height are read-only properties."""

    palette = Palette()
    width = 400
    height = 300

    def __init__(self, parent: Any = None) -> None:
        object.__setattr__(self, "repaints", 0)

    def update(self) -> None:
        object.__setattr__(self, "repaints", self.repaints + 1)


class Point:
    def __init__(self, x: float, y: float) -> None:
        self._x, self._y = float(x), float(y)

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y


class Transform:
    """QTransform(m11, m12, m21, m22, dx, dy), row-vector convention like Qt."""

    def __init__(
        self,
        m11: float = 1.0,
        m12: float = 0.0,
        m21: float = 0.0,
        m22: float = 1.0,
        dx: float = 0.0,
        dy: float = 0.0,
    ) -> None:
        self.values = (m11, m12, m21, m22, dx, dy)

    def m11(self) -> float:
        return self.values[0]

    def m12(self) -> float:
        return self.values[1]

    def m21(self) -> float:
        return self.values[2]

    def m22(self) -> float:
        return self.values[3]

    def dx(self) -> float:
        return self.values[4]

    def dy(self) -> float:
        return self.values[5]

    def apply(self, x: float, y: float) -> tuple[float, float]:
        a, b, c, d, e, f = self.values
        return x * a + y * c + e, x * b + y * d + f

    def inverted(self) -> "Transform":
        """PythonQt returns QTransform alone, unlike PySide's tuple."""
        a, b, c, d, e, f = self.values
        det = a * d - b * c
        if abs(det) < 1e-12:
            return Transform()
        return Transform(
            d / det,
            -b / det,
            -c / det,
            a / det,
            (c * f - d * e) / det,
            (b * e - a * f) / det,
        )

    def map(self, point: Point) -> Point:
        return Point(*self.apply(point.x(), point.y()))


class Rect:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.box = (x, y, w, h)

    def x(self) -> float:
        return self.box[0]

    def y(self) -> float:
        return self.box[1]

    def width(self) -> float:
        return self.box[2]

    def height(self) -> float:
        return self.box[3]

    def united(self, other: "Rect") -> "Rect":
        if not self.box[2] and not self.box[3]:
            return other
        x0 = min(self.x(), other.x())
        y0 = min(self.y(), other.y())
        x1 = max(self.x() + self.width(), other.x() + other.width())
        y1 = max(self.y() + self.height(), other.y() + other.height())
        return Rect(x0, y0, x1 - x0, y1 - y0)


def bounds(points: list[tuple[float, float]]) -> Rect:
    if not points:
        return Rect(0, 0, 0, 0)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


class PainterPath:
    def __init__(self) -> None:
        self.calls: list[tuple] = []
        self.points: list[tuple[float, float]] = []

    def _add(self, name: str, *values: float) -> None:
        self.calls.append((name, *values))
        self.points += list(zip(values[::2], values[1::2], strict=True))

    def moveTo(self, *v: float) -> None:
        self._add("move", *v)

    def lineTo(self, *v: float) -> None:
        self._add("line", *v)

    def cubicTo(self, *v: float) -> None:
        self._add("cubic", *v)

    def quadTo(self, *v: float) -> None:
        self._add("quad", *v)

    def closeSubpath(self) -> None:
        self.calls.append(("close",))

    def boundingRect(self) -> Rect:
        return bounds(self.points)


class Painter:
    Antialiasing = 1
    log: ClassVar[list[Any]] = []
    fail = False

    def __init__(self, widget: Any) -> None:
        self.ended = False
        Painter.log.append(self)
        self.paths: list[PainterPath] = []

    def drawPath(self, path: PainterPath) -> None:
        if Painter.fail:
            raise RuntimeError("paint boom")
        self.paths.append(path)

    def end(self) -> None:
        self.ended = True

    def __getattr__(self, name: str) -> Any:
        return lambda *args, **kwargs: None


def make_qt() -> ModuleType:
    qt = ModuleType("PythonQt")
    core = NS(
        QPointF=Point,
        QDateTime=NS(currentDateTimeUtc=lambda: "UTC stamp"),
        Qt=NS(AlignRight=2, ScrollBarAlwaysOff=3, DashLine=4, NoPen=0),
    )
    gui = NS(
        QDialog=Dialog,
        QWidget=QWidget,
        QLabel=Label,
        QCheckBox=CheckBox,
        QComboBox=Combo,
        QSpinBox=Spin,
        QDoubleSpinBox=DoubleSpin,
        QPushButton=Button,
        QTableWidget=Table,
        QTableWidgetItem=Item,
        QVBoxLayout=Widget,
        QHBoxLayout=Widget,
        QGridLayout=Widget,
        QPalette=Palette,
        QColor=Color,
        QBrush=lambda color: NS(color=lambda: color),
        QPen=lambda color: Widget(),
        QTransform=Transform,
        QPainter=Painter,
        QPainterPath=PainterPath,
        QAbstractItemView=NS(NoEditTriggers=0, NoSelection=0),
        QHeaderView=NS(Stretch=0, ResizeToContents=1),
    )
    qt.QtCore, qt.QtGui = core, gui
    return qt


# ---------------------------------------------------------------- font fakes
IDS = itertools.count(1)
Spec = list[tuple[float, float, int]]  # (x, y, on) per node


class Node:
    def __init__(self, contour: "Contour", x: float, y: float, on: bool) -> None:
        self.contour, self._x, self._y, self.on = contour, float(x), float(y), bool(on)
        self.smooth = False

    def _write(self, name: str, value: float) -> None:
        world = self.contour.world
        if world.fail_write:
            raise RuntimeError("boom write")
        if world.round_writes:
            value = math.floor(float(value) + 0.5)
        if not world.ignore_writes:
            setattr(self, name, float(value))

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._write("_x", value)

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._write("_y", value)

    def isOn(self) -> bool:
        return self.on

    def convertToLine(self) -> bool:
        return self.contour.convert_to_line(self)


class Contour:
    def __init__(
        self, world: "World", points: Spec, closed: bool = True, tt: bool = False
    ) -> None:
        self.world, self.closed, self.isTT = world, closed, tt
        self._nodes = [Node(self, x, y, on) for x, y, on in points]

    def _segments(self) -> list[list[tuple[float, float]]]:
        points = self.xy()
        if not points:
            return []
        on = next((i for i, p in enumerate(points) if p[2]), None)
        if on is None:
            if not self.isTT:
                return []
            first, last = points[0], points[-1]
            points = [
                ((first[0] + last[0]) / 2, (first[1] + last[1]) / 2, True),
                *points,
            ]
            on = 0
        ring = points[on:] + points[:on]
        current, controls, result = ring[0][:2], [], []
        for x, y, is_on in ring[1:] + ring[:1]:
            if not is_on:
                controls.append((x, y))
                continue
            end = (x, y)
            if self.isTT and controls:
                for left, right in itertools.pairwise(controls):
                    mid = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)
                    result.append([current, left, mid])
                    current = mid
                result.append([current, controls[-1], end])
            else:
                result.append([current, *controls, end])
            current, controls = end, []
        return result

    def segments(self) -> list[Any]:
        return [NS(p0=Point(*part[0])) for part in self._segments()]

    def calculate(self, t: float) -> Point:
        parts = self._segments()
        points = parts[int(t) % len(parts)]
        u = t - math.floor(t)
        while len(points) > 1:
            points = [
                (a[0] * (1 - u) + b[0] * u, a[1] * (1 - u) + b[1] * u)
                for a, b in itertools.pairwise(points)
            ]
        return Point(*points[0])

    def _polygon(self) -> list[tuple[float, float]]:
        return [
            (p.x(), p.y())
            for k, part in enumerate(self._segments())
            for count in [1 if len(part) == 2 else 64]
            for j in range(count)
            for p in [self.calculate(k + j / count)]
        ]

    def getSquare(self) -> float:
        points = self._polygon()
        return (
            sum(
                a[0] * b[1] - a[1] * b[0]
                for a, b in zip(points, points[1:] + points[:1], strict=True)
            )
            / 2
        )

    @property
    def clockwise(self) -> bool:
        return self.getSquare() < 0

    def contains(self, point: Any) -> bool:
        if isinstance(point, Contour):
            return all(self.contains(Point(x, y)) for x, y in point._polygon())
        x, y, hit = point.x(), point.y(), False
        points = self._polygon()
        for a, b in zip(points, points[1:] + points[:1], strict=True):
            if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (
                b[1] - a[1]
            ):
                hit = not hit
        return hit

    def hasIntersPoints(self, other: "Contour") -> bool:
        def cross(a: tuple, b: tuple, c: tuple) -> float:
            return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

        a, b = self._polygon(), other._polygon()
        return any(
            cross(p, q, r) * cross(p, q, s) < 0 and cross(r, s, p) * cross(r, s, q) < 0
            for p, q in zip(a, a[1:] + a[:1], strict=True)
            for r, s in zip(b, b[1:] + b[:1], strict=True)
        )

    def nodes(self) -> list[Node]:
        return list(self._nodes)

    @property
    def nodesCount(self) -> int:
        return len(self._nodes)

    def xy(self) -> list[tuple[float, float, bool]]:
        return [(n.x, n.y, n.on) for n in self._nodes]

    def _guard(self) -> bool:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        return not self.world.ignore_writes

    def reverse(self) -> None:
        if self._guard():
            self._nodes = self._nodes[:1] + self._nodes[1:][::-1]

    def setStartPoint(self, index: int) -> bool:
        if not self.closed or not 0 < index < len(self._nodes):
            return False
        if not self._nodes[index].on:
            return False
        if self._guard():
            self._nodes = self._nodes[index:] + self._nodes[:index]
        return True

    def insertNodeTo(self, t: float) -> Node:
        """Split segment int(t) at t - int(t), as FontLab does (de Casteljau)."""
        self._guard()
        k, u = int(t), t - int(t)
        on = [i for i, n in enumerate(self._nodes) if n.on]
        start, end = on[k], on[(k + 1) % len(on)]
        span = (end - start) % len(self._nodes) or len(self._nodes)
        between = [(start + j) % len(self._nodes) for j in range(1, span)]
        p = [(self._nodes[i].x, self._nodes[i].y) for i in (start, *between, end)]

        def lerp(a: tuple, b: tuple) -> tuple:
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)

        assert len(p) == 4, "the fake splits cubic curves only"
        p01, p12, p23 = lerp(p[0], p[1]), lerp(p[1], p[2]), lerp(p[2], p[3])
        p012, p123 = lerp(p01, p12), lerp(p12, p23)
        mid = lerp(p012, p123)
        fresh = [
            Node(self, *p01, False),
            Node(self, *p012, False),
            Node(self, *mid, True),
            Node(self, *p123, False),
            Node(self, *p23, False),
        ]
        if self.world.ignore_writes:
            return fresh[2]
        first = between[0]
        assert between == [first, first + 1], "the fake needs an unwrapped curve"
        self._nodes[first : first + 2] = fresh
        return fresh[2]

    def convert_to_line(self, node: Node) -> bool:
        if not self._guard():
            return True
        index = self._nodes.index(node)
        count = len(self._nodes)
        prev = next(
            (index - j) % count
            for j in range(1, count)
            if self._nodes[(index - j) % count].on
        )
        doomed = {(prev + j) % count for j in range(1, (index - prev) % count)}
        self._nodes = [n for i, n in enumerate(self._nodes) if i not in doomed]
        self.world.events.append(("to-line", len(doomed)))
        return True


class ShapeData:
    def __init__(self, base: str, refs: int) -> None:
        self.componentGlyph, self.referenceCount = base, refs


class Shape:
    def __init__(
        self,
        world: "World",
        contours: list[Any] | None = None,
        base: str | None = None,
        dx: float = 0.0,
        dy: float = 0.0,
        matrix: tuple[float, float, float, float] = (1, 0, 0, 1),
        refs: int = 1,
    ) -> None:
        self.world, self.id = world, next(IDS)
        self.isComponent = base is not None
        self.shapeData = ShapeData(base or "", refs)
        self._transform = Transform(*matrix, dx, dy)
        self._contours = [
            c if isinstance(c, Contour) else Contour(world, c) for c in (contours or [])
        ]
        self.name, self.note = f"shape-{self.id}", "keep me"

    @property
    def contours(self) -> list[Contour]:
        return list(self._contours)

    @property
    def includesList(self) -> list[Any]:
        return []

    @property
    def transform(self) -> Transform:
        return self._transform

    @transform.setter
    def transform(self, value: Transform) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._transform = value

    def removeContour(self, contour: Contour) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._contours = [c for c in self._contours if c is not contour]

    def convertToFgShape(self, target: "FgShape") -> None:
        target.contours = [FgContour(c.xy()) for c in self._contours]

    def assign(self, source: "FgShape") -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._contours = [Contour(self.world, c.points) for c in source.contours]
        self.world.events.append(("assign", self.name))

    def applyTransform(self) -> None:
        """Bake the shape transform into the nodes and reset it (FontLab rounds)."""
        if self.world.ignore_writes:
            return
        for contour in self._contours:
            for node in contour.nodes():
                x, y = self._transform.apply(node.x, node.y)
                node._x, node._y = float(round(x)), float(round(y))
        self._transform = Transform()
        self.world.events.append(("bake", self.name))

    def changed(self) -> None:
        pass


class FgContour:
    def __init__(self, points: list[tuple[float, float, bool]]) -> None:
        self.points = list(points)

    def countNodes(self) -> int:
        return len(self.points)


class FgShape:
    """fontgate.fgShape: removeOverlap merges contours whose boxes overlap.

    A merged group becomes its bounding rectangle, started at the top-left.
    """

    def __init__(self) -> None:
        self.contours: list[FgContour] = []

    def removeOverlap(self) -> int:
        groups: list[list[FgContour]] = []
        for contour in self.contours:
            box = bounds([p[:2] for p in contour.points])
            for group in groups:
                if any(overlap(box, bounds([p[:2] for p in g.points])) for g in group):
                    group.append(contour)
                    break
            else:
                groups.append([contour])
        result = []
        for group in groups:
            if len(group) == 1:
                result.append(group[0])
                continue
            box = bounds([p[:2] for c in group for p in c.points])
            x0, y0 = box.x(), box.y()
            x1, y1 = x0 + box.width(), y0 + box.height()
            corners = [(x0, y1, True), (x1, y1, True), (x1, y0, True), (x0, y0, True)]
            result.append(FgContour(corners))
        self.contours = result
        return 0


def overlap(a: Rect, b: Rect) -> bool:
    return (
        a.x() < b.x() + b.width()
        and b.x() < a.x() + a.width()
        and a.y() < b.y() + b.height()
        and b.y() < a.y() + a.height()
    )


class Pin:
    def __init__(self, world: "World", name: str, x: float, y: float) -> None:
        self.world, self.name, self._point = world, name, Point(x, y)

    @property
    def point(self) -> Point:
        return self._point

    @point.setter
    def point(self, value: Point) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._point = value


class Layer:
    isNull = False

    def __init__(
        self, world: "World", glyph: str, master: str, advance: float, auto: bool
    ) -> None:
        self.world, self.glyph, self.master, self.name = world, glyph, master, master
        self.marker = f"{glyph}/{master}"
        self.advanceWidth, self.autoLayer = advance, auto
        self.anchors: list[Pin] = []
        self._shapes: list[Shape] = []

    @property
    def shapes(self) -> list[Shape]:
        return list(self._shapes)

    @property
    def boundingBox(self) -> Rect:
        return bounds(
            [
                shape.transform.apply(n.x, n.y)
                for shape in self._shapes
                for c in shape.contours
                for n in c.nodes()
            ]
        )

    def changed(self) -> None:
        self.world.events.append(("changed", self.marker))

    def update(self) -> bool:
        return self.world.update_ok

    def checkInitHistoryState(self, index: int) -> None:
        self.world.events.append(("init", self.marker))


class Glyph:
    isNull = False

    def __init__(self, world: "World", name: str) -> None:
        self.world, self.name = world, name
        self.by_master: dict[str, Layer] = {}
        self._modified = "before"

    @property
    def layers(self) -> list[Layer]:
        return list(self.by_master.values())

    def findLayer(self, master: str) -> Layer | None:
        return self.by_master.get(master)

    def checkInitHistoryState(self, index: int) -> None:
        self.world.events.append(("init", self.name))

    @property
    def lastModified(self) -> Any:
        return self._modified

    @lastModified.setter
    def lastModified(self, value: Any) -> None:
        self._modified = value
        self.world.events.append(("stamp", self.name))


class World:
    """One owned font: masters, glyphs, selection, history log."""

    def __init__(self, masters: tuple[str, ...] = ("Light", "Bold")) -> None:
        self.masters, self.master = list(masters), masters[0]
        self.glyphs: dict[str, Glyph] = {}
        self.selected: list[str] = []
        self.events: list[Any] = []
        self.ignore_writes = self.fail_write = self.fail_notify = False
        self.round_writes = False  # FontLab's strong-rounding preference
        self.no_font = False
        self.update_ok = True
        self.pending: list[int] = []  # flGlyph.updatedFgGlyphs()
        self.x_height = 500.0
        self.package = NS(
            id=7,
            isNull=False,
            masters=self.masters,
            master=self.master,
            italicAngle_value=-12.0,
            findName=lambda name: self.glyphs.get(name),
        )

    def glyph(
        self,
        name: str,
        shapes: dict[str, list[Shape]] | None = None,
        anchors: dict[str, list[tuple[str, float, float]]] | None = None,
        auto: tuple[str, ...] = (),
        select: bool = True,
    ) -> Glyph:
        glyph = self.glyphs.setdefault(name, Glyph(self, name))
        for master in self.masters:
            layer = Layer(self, name, master, 600, master in auto)
            for pin in (anchors or {}).get(master, []):
                layer.anchors.append(Pin(self, *pin))
            for shape in (shapes or {}).get(master, []):
                layer._shapes.append(shape)
            glyph.by_master[master] = layer
        if select:
            self.selected.append(name)
        return glyph

    def outline(self, *contours: Any, **options: Any) -> Shape:
        return Shape(self, list(contours), **options)

    def same(self, name: str, *contours: Spec, **options: Any) -> Glyph:
        """A glyph whose every master holds the same outline shape."""
        shapes = {m: [self.outline(*contours, **options)] for m in self.masters}
        return self.glyph(name, shapes)

    def layer(self, glyph: str, master: str | None = None) -> Layer:
        return self.glyphs[glyph].by_master[master or self.master]

    def points(self, glyph: str, master: str | None = None) -> list[list[tuple]]:
        return [c.xy() for s in self.layer(glyph, master).shapes for c in s.contours]

    def notifications(self) -> list[Any]:
        return [e for e in self.events if e[0] == "notify"]

    def history(self) -> list[Any]:
        """The history-relevant events only: init, stamp, notify (markers)."""
        return [
            e[:3] if e[0] == "notify" else e
            for e in self.events
            if e[0] in {"init", "stamp", "notify"}
        ]


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> World:
    """Install fake native modules; reset fly, fontlabapp and echopy around the test."""
    w = World()
    qt = make_qt()
    fontlab = ModuleType("fontlab")
    fontlab.flWorkspace = NS(
        instance=lambda: NS(currentPackage=None if w.no_font else w.package)
    )

    def notify(title: str, items: list) -> None:
        if w.fail_notify:
            raise RuntimeError("boom notify")
        w.events.append(
            (
                "notify",
                title,
                [getattr(i, "marker", None) or i.name for i in items],
                items,
            )
        )

    fontlab.flItems = lambda: NS(notifyChangesApplied=notify)
    fontlab.CurrentGlyph = lambda: w.glyphs[w.selected[0]] if w.selected else None
    fontlab.CurrentFont = lambda: NS(glyphs=[NS(name=n, unicodes=[]) for n in w.glyphs])
    fontlab.MainWindow = lambda: NS(palette=Palette())
    fontlab.UpdateAll = lambda: w.events.append(("update-all",))
    fontlab.flGlyph = NS(updatedFgGlyphs=lambda: tuple(w.pending))
    fontlab.FontMetrics = lambda package, master: NS(xHeight=w.x_height)
    fontgate = ModuleType("fontgate")
    fontgate.fgShape = FgShape
    names = lambda: list(w.glyphs)
    fl = NS(Selected=lambda index: names()[index] in w.selected)

    class FLFont:
        def __len__(self) -> int:
            return len(w.glyphs)

        def __getitem__(self, index: int) -> Any:
            return NS(name=names()[index])

    fl.font = FLFont()
    native = ModuleType("FL")
    native.fl = fl
    # Isolate from other test files in the same run: snapshot, import the real
    # packages afresh, put the snapshot back afterwards (monkeypatch restores).
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
        monkeypatch.delitem(sys.modules, key)
    for name, module in (
        ("PythonQt", qt),
        ("fontlab", fontlab),
        ("fontgate", fontgate),
        ("FL", native),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(
        sys,
        "meta_path",
        [f for f in sys.meta_path if not getattr(f, "_fontlab_fly_alias", False)],
    )
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    Dialog.registry.clear()
    Painter.log.clear()
    Painter.fail = False
    yield w
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
        del sys.modules[key]


def load(name: str) -> dict[str, Any]:
    namespace = runpy.run_path(str(FOLDER / f"{name}.py"), run_name="inspection")
    scripting = namespace["scripting"]
    assert scripting.__name__ == "fontlabapp.scripting", "the real App helper"
    assert scripting.__file__.endswith("fontlabapp/scripting.py")
    for module in APP_MODULES:
        if module in namespace:
            found = namespace[module]
            assert found.__name__ == f"fontlabapp.{module}", f"the real App {module}"
            assert found.__file__.endswith(f"fontlabapp/{module}.py")
    return namespace


def app(name: str) -> Any:
    """The real App module (fly.ap.<name>) that the scripts of this run use."""
    return sys.modules[f"fontlabapp.{name}"]


def panel_of(name: str) -> tuple[Any, dict[str, Any]]:
    namespace = load(name)
    return namespace["main"](), namespace


def texts(panel: Any) -> list[list[str]]:
    return panel.table.row_texts()


def light(panel: Any) -> list[list[str]]:
    """Preview rows of the Light master only."""
    return [row for row in texts(panel) if row[0].endswith("· Light")]


def press(panel: Any) -> None:
    """Click Apply the way Qt does: through the guarded slot."""
    panel.apply_button.clicked.emit()


def one_step(world: World, title: str, layers: list[str], glyphs: list[str]) -> None:
    """Assert the one-Undo event shape: init layers+glyphs, stamp, ONE notify, stamp."""
    assert world.history() == [
        *(("init", m) for m in layers),
        *(("init", g) for g in glyphs),
        *(("stamp", g) for g in glyphs),
        ("notify", title, [*layers, *glyphs]),
        *(("stamp", g) for g in glyphs),
    ], world.history()


def square(x: float, y: float, size: float, clockwise: bool = False) -> Spec:
    """Closed square from (x, y); counter-clockwise (y up) unless `clockwise`."""
    ccw = [(x, y, 1), (x + size, y, 1), (x + size, y + size, 1), (x, y + size, 1)]
    return ccw[:1] + ccw[1:][::-1] if clockwise else ccw


ARCH: Spec = [(0, 0, 1), (0, 100, 0), (100, 100, 0), (100, 0, 1)]  # y extreme at t=0.5


def fixture_glyph(world: World, name: str) -> None:
    """One glyph with work for the given script, in both masters."""
    if name == "Round Coordinates":
        world.same("A", [(0.4, 0, 1), (10, 0, 1), (10, 10, 1)])
    elif name == "Remove Overlap":
        world.same("A", square(0, 0, 10), square(5, 5, 10))
    elif name == "Add Extremes":
        world.same("A", ARCH)
    elif name == "Correct Contour Direction":
        world.same("A", square(0, 0, 100, clockwise=True))
    elif name == "Straighten Short Curves":
        world.same(
            "A", [(0, 0, 1), (10, 0.5, 0), (20, 0.5, 0), (30, 0, 1), (15, -40, 1)]
        )
    elif name == "Optimize Start Points":
        world.same("A", [(10, 10, 1), (0, 10, 1), (0, 0, 1), (10, 0, 1)])
    elif name == "Delete Small Contours":
        world.same("A", square(0, 0, 100), square(200, 0, 10))
    elif name == "Fix Zero Handles":
        world.same("A", [(0, 0, 1), (0, 0, 0), (30, 0, 0), (30, 0, 1), (15, 40, 1)])
    elif name == "Delete Duplicate Contours":
        world.same("A", square(0, 0, 10), square(0, 0, 10))
    else:  # Transform, Slant
        world.same("A", square(0, 0, 100))


def make_work(panel: Any, name: str) -> None:
    """Set controls so that Apply has something to do on fixture_glyph.

    All masters: structure edits on one master only are held for compatibility.
    """
    panel.scope.setCurrentIndex(1)
    if name == "Transform":
        panel.move_x.setValue(10.0)


# ---------------------------------------------------------------- all eleven: shape
JARGON = [
    "issue 122",
    "issue122",
    "S6",
    "D22",
    "D11",
    "S-L4",
    "reviewed App",
    "see fragment",
    "fragment",
    "Batch S",
    "AGENTS.md",
    "landmine",
    "unverified",
]


@pytest.mark.parametrize("name", NAMES)
def test_script_when_parsed_then_python311_syntax_header_and_sections(
    name: str,
) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    lines = source.splitlines()
    assert lines[0] == f"# this_file: Scripts/Contours/{name}.py", "this_file header"
    assert lines[1] == "# SPDX-License-Identifier: Apache-2.0"
    assert lines[2] == f"# FLM: Contours · {name}"
    doc = ast.get_docstring(tree) or ""
    for section in ("What", "How", "Why", "Use", "Benefit", "Safety", "Source"):
        assert f"\n\n{section}: " in doc, f"{name}: docstring lacks paragraph {section}"
    assert "\n\n- " in doc, "Markdown needs a blank line before the Safety list"
    assert f"{STEMS[name]}.py" in doc, "credit names the rescued sample"
    assert "the author's own FontLab sample" in doc and "Apache-2.0" in doc
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    untyped = [
        f.name
        for f in functions
        if (f.returns is None and f.name != "__init__")
        or any(a.annotation is None for a in f.args.args if a.arg != "self")
    ]
    assert not untyped, f"{name}: functions without full type hints: {untyped}"
    calls = {
        getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)
    }
    assert "UpdateAll" not in calls, "no UpdateAll after writes (fl#8537)"
    assert not calls & {"clone", "cloneCustom", "removeAllShapes"}, "no shape clones"
    imports = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not [n for n in imports if n.module == "fly.ap"], (
        "import App modules as `import fly.ap.x as x`"
    )


@pytest.mark.parametrize("name", NAMES)
def test_public_text_when_read_then_has_no_internal_process_wording(name: str) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    found = [word for word in JARGON if word in source]
    assert not found, f"{name}: internal wording {found}"
    assert "fl#" not in source.replace("fl#8527", "").replace("fl#8537", "").replace(
        "fl#8517", ""
    ).replace("fl#8569", ""), "cite only the public FontLab issues this file relies on"


@pytest.mark.parametrize("name", NAMES)
def test_panel_attributes_when_assigned_then_never_shadow_native_members(
    name: str,
) -> None:
    tree = ast.parse((FOLDER / f"{name}.py").read_text())
    widgets = [
        cls
        for cls in ast.walk(tree)
        if isinstance(cls, ast.ClassDef)
        and (
            cls.name.endswith(("Panel", "Preview"))
            or (
                cls.bases
                and ast.unparse(cls.bases[0])
                in {"outline_panel.panel_type()", "outline_transform.panel_type()"}
            )
        )
    ]
    assert widgets, "the panel classes are found"
    assigned = {
        node.attr
        for cls in widgets
        for node in ast.walk(cls)
        if isinstance(node, ast.Attribute)
        and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    }
    defined = {
        node.name
        for cls in widgets
        for node in cls.body
        if isinstance(node, ast.FunctionDef)
    }
    clash = (assigned | defined) & NATIVE_MEMBERS
    assert not clash, clash


@pytest.mark.parametrize("name", NAMES)
def test_import_when_loaded_then_nothing_opens_until_main(
    world: World, name: str
) -> None:
    load(name)
    assert Dialog.registry == [], "import must not create a window"


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_no_font_then_diagnoses_and_blocks_apply(
    world: World, name: str
) -> None:
    world.no_font = True
    panel, _ = panel_of(name)
    assert panel.subtitle.text == "Open a font first."
    assert not panel.apply_button.enabled and panel.close_button.enabled
    assert world.notifications() == []


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_nothing_selected_then_asks_for_selection(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    world.selected.clear()
    panel, _ = panel_of(name)
    assert "Select glyphs" in panel.subtitle.text
    assert not panel.apply_button.enabled


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_closed_then_disconnects_deletes_and_unregisters(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, namespace = panel_of(name)
    assert sys._fontlab_samples[namespace["KEY"]] is panel and panel.shown
    assert panel._connections, "signals must be tracked for disconnect"
    again = namespace["main"]()
    assert again is not panel and panel.deleted, "second main replaces the first panel"
    panel = again
    signals = [s for s, _ in panel._connections]
    panel.close_button.clicked.emit()
    assert panel.deleted and not panel._connections
    assert all(s.slots == [] for s in signals), "every owned slot disconnected"
    assert namespace["KEY"] not in sys._fontlab_samples


def test_real_app_names_when_imported_from_installed_app_then_all_exist() -> None:
    used = app_names_used([FOLDER / f"{name}.py" for name in NAMES])
    kernel = {"Change", "Editor", "Planner", "outline_shapes", "note_rows", "fmt"}
    assert kernel <= used["fly.ap.outline_writer"]
    assert {"node_points", "translation", "plural", "Point"} <= used[
        "fly.ap.outline_writer"
    ]
    assert used["fly.ap.outline_panel"] == {"panel_type"}
    assert {"panel_type", "transform_changes", "TransformEditor"} <= used[
        "fly.ap.outline_transform"
    ]
    assert "unsigned_area" in used["fly.ap.contour_selection"]
    assert {"concat", "rotation", "IDENTITY"} <= used["fly.ap.affine"]
    # The panel and the kernel write through these App names: they must exist too.
    used["fly.ap.outline_writer"] |= {"collect", "apply_work", "require_safe"}
    used["fly.ap.outline_transform"] |= {"bakes", "layer_outline", "outline_path"}
    used.setdefault("fly.ap.history", set()).update(
        {"commit", "scan_auto_facts", "refusal", "auto_facts"}
    )
    used.setdefault("fly.ap.layer_writer", set()).update({"apply_work", "Editor"})
    check_real_app_names(used)


@pytest.mark.parametrize("name", NAMES)
def test_script_when_loaded_then_kernel_and_panel_are_the_app_outline_modules(
    world: World, name: str
) -> None:
    namespace = load(name)
    writer, panel_module = app("outline_writer"), app("outline_panel")
    assert namespace["outline_writer"] is writer
    local = sorted(SHARED & set(namespace))
    assert not local, f"{name}: shared names defined in the script: {local}"
    panel = namespace["main"]()
    base = panel_module.panel_type()
    if name in TRANSFORMS:
        assert namespace["outline_transform"] is app("outline_transform")
        base = app("outline_transform").panel_type()
        assert issubclass(base, panel_module.panel_type())
    assert isinstance(panel, base), "the panel subclasses the App base"
    assert type(panel).__module__ != base.__module__, "only the subclass is local"
    assert type(panel).__bases__ == (base,)


# ---------------------------------------------------------------- all eleven: write
@pytest.mark.parametrize("name", NAMES)
def test_apply_when_planned_then_one_undo_step_for_layers_and_glyph(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, namespace = panel_of(name)
    panel.scope.setCurrentIndex(1)  # all masters
    make_work(panel, name)
    assert panel.apply_button.enabled, (panel.status.text, texts(panel))
    press(panel)
    assert panel.status.text.startswith(panel.DONE), panel.status.text
    one_step(world, namespace["TITLE"], ["A/Light", "A/Bold"], ["A"])


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_write_fails_then_partial_error_says_use_undo(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, _ = panel_of(name)
    make_work(panel, name)
    world.fail_write = True
    press(panel)
    assert "Native changes may remain; use Edit > Undo." in panel.status.text
    assert len(world.notifications()) == 1, "history still closes with one notify"


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_font_ignores_write_then_read_back_reports(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, _ = panel_of(name)
    make_work(panel, name)
    world.ignore_writes = True
    press(panel)
    assert "did not store" in panel.status.text, panel.status.text
    assert "Check those layers before you save." in panel.status.text
    assert "Undo restores" not in panel.status.text


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_updates_queued_then_refuses_before_history(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, _ = panel_of(name)
    make_work(panel, name)
    world.pending.append(42)
    panel.refresh()
    assert not panel.apply_button.enabled
    assert "pending" in panel.status.text
    press(panel)
    assert world.history() == [] and world.pending == [42], "queue never cleared"


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_glyph_is_auto_base_then_skipped_unless_allowed(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    world.glyph(
        "Aacute",
        {m: [Shape(world, base="A")] for m in world.masters},
        auto=tuple(world.masters),
        select=False,
    )
    panel, _ = panel_of(name)
    make_work(panel, name)
    assert ["A", "glyph", "skipped: base of auto Aacute"] in [
        [row[0], row[1], row[-1]] for row in texts(panel)
    ], texts(panel)
    assert not panel.apply_button.enabled
    panel.bases.setChecked(True)
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert len(world.notifications()) == 1
    assert world.notifications()[0][2] == ["A/Light", "A/Bold", "A"], (
        "the auto glyph is never notified"
    )


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_glyph_has_auto_layer_then_skipped_and_other_glyphs_written(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    world.glyph(
        "B",
        {m: [world.outline(square(0, 0, 10))] for m in world.masters},
        auto=("Bold",),
    )
    panel, _ = panel_of(name)
    make_work(panel, name)
    assert ["B", "glyph", "skipped: has auto layers"] in [
        [row[0], row[1], row[-1]] for row in texts(panel)
    ]
    assert panel.apply_button.enabled
    press(panel)
    assert world.notifications()[0][2] == ["A/Light", "A/Bold", "A"]
    assert "1 skipped" in panel.status.text


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_font_switched_then_refuses_with_reload_hint(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, _ = panel_of(name)
    make_work(panel, name)
    world.no_font = True
    press(panel)
    assert "Reload selection" in panel.status.text
    assert world.history() == []


@pytest.mark.parametrize("name", [n for n in NAMES if n not in {"Transform", "Slant"}])
def test_planner_when_shape_is_shared_or_scaled_then_kept_with_note(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    spec = [c.xy() for c in world.layer("A").shapes[0].contours]
    shared = world.outline(*spec, refs=2)
    scaled = world.outline(*spec, matrix=(2, 0, 0, 2))
    world.glyph("B", {m: [shared, scaled] for m in world.masters})
    world.selected[:] = ["B"]
    panel, _ = panel_of(name)
    rows = texts(panel)
    assert ["B · Light", "1 shape", "", "shared outline, kept"] in rows or [
        "B · Light",
        "1 shape",
        "shared outline, kept",
    ] in rows, rows
    assert any("scaled or rotated shape, kept" in row for row in rows), rows
    assert not panel.apply_button.enabled


def test_preview_rows_when_many_glyphs_then_capped_but_edit_complete(
    world: World,
) -> None:
    for index in range(260):
        world.same(f"g{index}", square(0, 0, 100, clockwise=True))
    panel, _ = panel_of("Correct Contour Direction")
    panel.scope.setCurrentIndex(1)
    assert panel.rows == app("outline_panel").MAX_ROWS == 500
    press(panel)
    assert panel.status.text == "Reversed 520 contours on 520 layers"


# ---------------------------------------------------------------- Round Coordinates
def test_snap_when_halves_and_grids_then_rounds_half_up(world: World) -> None:
    snap = load("Round Coordinates")["snap"]
    assert [snap(v, 1) for v in (2.5, -2.5, 0.4, -0.6, 3.0)] == [3, -2, 0, -1, 3]
    assert (snap(12, 5), snap(12.5, 5), snap(-7.5, 5)) == (10, 15, -5)
    assert math.copysign(1, snap(-0.2, 1)) == 1, "no negative zero"


def test_round_when_shape_moved_then_rounds_visible_position(world: World) -> None:
    moved = world.outline([(10.2, 3, 1), (20, 3, 1), (20.6, 9, 1)], dx=2)
    world.glyph("A", {m: [moved] for m in world.masters})
    panel, _ = panel_of("Round Coordinates")
    assert texts(panel)[0] == ["A · Light", "nodes", "2 off grid", "on grid 1"]
    world.round_writes = True
    press(panel)
    xs = [n.x for n in moved.contours[0].nodes()]
    assert xs == [10, 20, 21], "x + 2 lands on the grid, also under strong rounding"
    assert "Error" not in panel.status.text, panel.status.text


def test_round_when_shape_moved_by_fraction_then_kept(world: World) -> None:
    moved = world.outline([(10.2, 3, 1), (20, 3, 1), (20, 9, 1)], dx=0.5)
    world.glyph("A", {m: [moved] for m in world.masters})
    panel, _ = panel_of("Round Coordinates")
    assert light(panel) == [
        ["A · Light", "1 shape", "", "fractional shape offset, kept"]
    ]
    assert not panel.apply_button.enabled, "nothing to write"


def test_round_when_components_then_offsets_rounded_matrix_kept(world: World) -> None:
    mark = Shape(world, base="acute", dx=10.4, dy=-2.5, matrix=(1, 0, 0.2, 1))
    world.glyph("A", {m: [mark] for m in world.masters})
    panel, _ = panel_of("Round Coordinates")
    assert texts(panel) == [["A · Light", "acute", "10.4, -2.5", "10, -2"]]
    press(panel)
    assert mark.transform.values == (1, 0, 0.2, 1, 10, -2)
    panel.offsets.setChecked(False)
    assert texts(panel) == []


def test_round_when_grid_five_then_counts_and_moves(world: World) -> None:
    world.same("A", [(12, 0, 1), (20, 7.5, 1), (0, 0, 1)])
    panel, _ = panel_of("Round Coordinates")
    panel.grid.setValue(5)
    assert texts(panel)[0][2:] == ["2 off grid", "on grid 5"]
    press(panel)
    assert world.points("A")[0] == [(10, 0, True), (20, 10, True), (0, 0, True)]
    assert world.points("A", "Bold")[0][0] == (12, 0, True), "current master only"


# ---------------------------------------------------------------- Remove Overlap
def test_overlap_when_merged_then_rows_write_and_start_point_restored(
    world: World,
) -> None:
    world.same("A", square(0, 0, 10), square(5, 5, 10))
    panel, _ = panel_of("Remove Overlap")
    panel.scope.setCurrentIndex(1)
    assert light(panel) == [["A · Light", "shape 1", "2 contours", "1 contour"]]
    panel.scope.setCurrentIndex(1)
    press(panel)
    contour = world.layer("A").shapes[0].contours[0]
    assert contour.xy()[0] == (0, 0, True), "start moved back to the old start (0, 0)"
    assert len(contour.xy()) == 4
    assert world.layer("A").shapes[0].note == "keep me", "same shape object"


def test_overlap_when_no_overlap_or_open_or_moved_then_kept(world: World) -> None:
    open_shape = Shape(world, [Contour(world, square(0, 0, 10), closed=False)])
    moved = world.outline(square(0, 0, 10), square(5, 5, 10), dx=3)
    plain = world.outline(square(0, 0, 10), square(50, 50, 10))
    world.glyph("A", {m: [open_shape, moved, plain] for m in world.masters})
    panel, _ = panel_of("Remove Overlap")
    panel.scope.setCurrentIndex(1)
    notes = [row[-1] for row in light(panel)]
    assert notes == ["open contour, kept", "moved shape, kept"], texts(panel)
    assert not panel.apply_button.enabled


def test_overlap_when_masters_differ_then_held_unless_allowed(world: World) -> None:
    world.glyph(
        "A",
        {
            "Light": [world.outline(square(0, 0, 10), square(5, 5, 10))],
            "Bold": [world.outline(square(0, 0, 10), square(50, 50, 10))],
        },
    )
    panel, _ = panel_of("Remove Overlap")
    panel.scope.setCurrentIndex(1)
    assert texts(panel)[0][-1] == "masters would differ, kept"
    assert "held for compatibility" in panel.status.text
    assert not panel.apply_button.enabled
    panel.compatible.setChecked(False)
    assert panel.apply_button.enabled


def test_overlap_when_current_master_only_then_held_for_other_masters(
    world: World,
) -> None:
    world.same("A", square(0, 0, 10), square(5, 5, 10))
    panel, _ = panel_of("Remove Overlap")
    panel.scope.setCurrentIndex(0)
    assert texts(panel)[0][-1] == "other masters need it too; choose All masters"
    assert not panel.apply_button.enabled
    panel.scope.setCurrentIndex(1)
    assert texts(panel)[0][-1] == "1 contour" and panel.apply_button.enabled
    panel.scope.setCurrentIndex(0)
    panel.compatible.setChecked(False)
    assert texts(panel) == [["A · Light", "shape 1", "2 contours", "1 contour"]]


# ---------------------------------------------------------------- Add Extremes
def test_extremes_when_arch_then_solves_t_half_and_splits(world: World) -> None:
    ns = load("Add Extremes")
    assert ns["extremes"]((0, 0), (0, 100), (100, 100), (100, 0)) == [0.5]
    assert ns["roots"](0, 0, 1) == [] and ns["roots"](1, 0, 1) == []
    world.same("A", ARCH)
    panel, _ = panel_of("Add Extremes")
    panel.scope.setCurrentIndex(1)
    assert light(panel) == [["A · Light", "contour 1", "4 nodes", "+1 extreme"]]
    panel.scope.setCurrentIndex(1)
    press(panel)
    assert world.points("A")[0] == [
        (0, 0, True),
        (0, 50, False),
        (25, 75, False),
        (50, 75, True),
        (75, 75, False),
        (100, 50, False),
        (100, 0, True),
    ]


def test_extremes_when_two_in_one_curve_then_reparametrised(world: World) -> None:
    ns = load("Add Extremes")
    calls: list[float] = []
    ns["insert_extremes"](NS(insertNodeTo=calls.append), [(2, [0.25, 0.75])])
    assert calls == [2.75, 2 + 0.25 / 0.75]


def test_extremes_when_masters_differ_then_held(world: World) -> None:
    world.glyph(
        "A",
        {
            "Light": [world.outline(ARCH)],
            "Bold": [world.outline([(0, 0, 1), (30, 0, 0), (70, 0, 0), (100, 0, 1)])],
        },
    )
    panel, _ = panel_of("Add Extremes")
    panel.scope.setCurrentIndex(1)
    assert texts(panel)[0][-1] == "masters would differ, kept"
    assert not panel.apply_button.enabled


def test_extremes_when_truetype_or_open_then_left_alone(world: World) -> None:
    tt = Shape(world, [Contour(world, ARCH, tt=True)])
    world.glyph("A", {m: [tt] for m in world.masters})
    panel, _ = panel_of("Add Extremes")
    panel.scope.setCurrentIndex(1)
    assert texts(panel) == []


# ---------------------------------------------------------------- Direction
def test_direction_when_outer_cw_and_counter_ccw_then_both_wrong(world: World) -> None:
    ns = load("Correct Contour Direction")
    outer = Contour(world, square(0, 0, 100, clockwise=True))
    counter = Contour(world, square(25, 25, 50))
    contours = [(outer, Transform()), (counter, Transform())]
    assert ns["wrong_contours"](contours) == [0, 1]
    outer.isTT = counter.isTT = True
    assert ns["wrong_contours"](contours) == [], "TrueType uses opposite winding"
    good = Contour(world, square(0, 0, 100))
    assert ns["wrong_contours"]([(good, Transform())]) == []


def test_direction_when_corrected_then_reverse_keeps_start(world: World) -> None:
    world.same("A", square(0, 0, 100, clockwise=True))
    panel, _ = panel_of("Correct Contour Direction")
    assert panel.scope.currentIndex == 1, "a reversal renumbers nodes: all masters"
    assert light(panel) == [
        ["A · Light", "contour 1", "clockwise", "counter-clockwise"]
    ]
    press(panel)
    assert world.points("A")[0] == [
        (0, 0, True), (100, 0, True), (100, 100, True), (0, 100, True)
    ]  # fmt: skip
    assert texts(panel) == []


# ---------------------------------------------------------------- Straighten
def test_straighten_when_short_flat_curve_then_line(world: World) -> None:
    ns = load("Straighten Short Curves")
    points = [(0, 0, True), (10, 0.5, False), (20, 0.5, False), (30, 0, True)]
    assert ns["straight_segments"](points, 60, 2) == [(0, 3, 0.5)]
    assert ns["straight_segments"](points, 20, 2) == [], "chord 30 > 20"
    assert ns["straight_segments"](points, 60, 0.4) == [], "deviation 0.5 > 0.4"
    world.same("A", [(0, 0, 1), (10, 0.5, 0), (20, 0.5, 0), (30, 0, 1), (15, -40, 1)])
    panel, _ = panel_of("Straighten Short Curves")
    panel.scope.setCurrentIndex(1)
    assert light(panel) == [
        ["A · Light", "contour 1", "1 curve", "1 to lines (max 0.5)"]
    ]
    panel.scope.setCurrentIndex(1)
    press(panel)
    assert world.points("A")[0] == [(0, 0, True), (30, 0, True), (15, -40, True)]
    assert ("to-line", 2) in world.events, "FontLab's convertToLine on the end node"


# ---------------------------------------------------------------- Start points
def test_start_when_bottom_left_then_moves_and_matches_masters(world: World) -> None:
    ns = load("Optimize Start Points")
    assert ns["bottom_left"]([(5, 0, True), (0, 0, True), (0, 0, False)]) == 1
    assert ns["bottom_left"]([(0, 0, False)]) is None
    world.glyph(
        "A",
        {
            "Light": [world.outline([(10, 10, 1), (0, 10, 1), (0, 0, 1), (10, 0, 1)])],
            "Bold": [world.outline([(10, 10, 1), (10, -5, 1), (0, 0, 1), (0, 10, 1)])],
        },
    )
    panel, _ = panel_of("Optimize Start Points")
    panel.scope.setCurrentIndex(1)
    rows = texts(panel)
    assert rows == [
        ["A · Light", "contour 1", "node 0 at 10, 10", "node 2 at 0, 0"],
        ["A · Bold", "contour 1", "node 0 at 10, 10", "node 2 at 0, 0"],
    ], "Bold follows the current master's node number"
    panel.rule.setCurrentIndex(1)
    assert texts(panel)[0][-1] == "masters would differ, kept", "each master on its own"
    assert not panel.apply_button.enabled
    panel.rule.setCurrentIndex(0)
    panel.scope.setCurrentIndex(0)
    assert texts(panel)[0][-1] == "other masters need it too; choose All masters"
    panel.scope.setCurrentIndex(1)
    press(panel)
    assert world.points("A", "Bold")[0][0] == (0, 0, True), "Bold node 2 starts"
    assert world.points("A")[0][0] == (0, 0, True)


# ---------------------------------------------------------------- Delete small
def test_small_when_area_below_threshold_then_deleted(world: World) -> None:
    ns = load("Delete Small Contours")
    parts = ns["segments_of"]([(0, 0, True), (10, 0, True), (10, 10, True)], False)
    assert parts == (((0, 0), (10, 0)), ((10, 0), (10, 10)), ((10, 10), (0, 0)))
    world.same("A", square(0, 0, 100), square(200, 0, 10))
    panel, _ = panel_of("Delete Small Contours")
    panel.scope.setCurrentIndex(1)
    assert light(panel) == [["A · Light", "contour 2", "area 100", "delete at 200, 0"]]
    panel.threshold.setValue(100)
    assert texts(panel) == [], (
        "strictly below the threshold, like Select Small Contours"
    )
    panel.threshold.setValue(101)
    panel.scope.setCurrentIndex(1)
    press(panel)
    assert len(world.points("A")) == len(world.points("A", "Bold")) == 1


def test_small_when_truetype_spline_then_implied_points(world: World) -> None:
    ns = load("Delete Small Contours")
    parts = ns["segments_of"](
        [(0, 0, True), (0, 10, False), (10, 10, False), (10, 0, True)], True
    )
    assert parts == (
        ((0, 0), (0, 10), (5.0, 10.0)),
        ((5.0, 10.0), (10, 10), (10, 0)),
        ((10, 0), (0, 0)),
    )
    assert ns["segments_of"]([(0, 0, False)], True) == ()


# ---------------------------------------------------------------- Zero handles
def test_zero_when_both_retracted_then_line_single_kept_or_pulled(world: World) -> None:
    ns = load("Fix Zero Handles")
    points = [(0, 0, True), (0, 0, False), (30, 0, False), (30, 0, True)]
    assert ns["zero_handles"](points) == ([(0, 3)], [])
    single = [(0, 0, True), (0, 0.2, False), (20, 30, False), (30, 0, True)]
    assert ns["zero_handles"](single) == ([], [(1, 0, 2)])
    world.same("A", [(0, 0, 1), (0, 0.2, 0), (21, 30, 0), (30, 0, 1), (15, -40, 1)])
    panel, _ = panel_of("Fix Zero Handles")
    panel.scope.setCurrentIndex(1)
    assert light(panel) == [
        ["A · Light", "contour 1", "0 lines, 1 single", "single handles kept"]
    ]
    assert not panel.apply_button.enabled
    panel.pull.setChecked(True)
    assert texts(panel)[0][-1] == "1 pulled"
    press(panel)
    assert world.points("A")[0][1] == (7, 10, False), "a third of the way to (21, 30)"


def test_zero_when_pull_fractional_then_whole_unit_and_no_false_alarm(
    world: World,
) -> None:
    assert load("Fix Zero Handles")["third"](0, 20) == 7, "6.67 rounds half up"
    world.same("A", [(0, 0, 1), (0, 0.2, 0), (20, 31, 0), (30, 0, 1), (15, -40, 1)])
    panel, _ = panel_of("Fix Zero Handles")
    panel.pull.setChecked(True)
    world.round_writes = True
    press(panel)
    assert "Error" not in panel.status.text, panel.status.text
    assert world.points("A")[0][1] == (7, 10, False), "(6.67, 10.33) as whole units"


def test_zero_when_pull_rounds_back_onto_node_then_kept(world: World) -> None:
    world.same("A", [(0, 0, 1), (0, 0.2, 0), (1, 1, 0), (1, 0, 1), (15, -40, 1)])
    panel, _ = panel_of("Fix Zero Handles")
    panel.pull.setChecked(True)
    assert light(panel) == [
        ["A · Light", "contour 1", "0 lines, 1 single", "single handles kept"]
    ], "a third of 1 unit rounds to 0: no pull"


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_strong_rounding_then_no_false_alarm(
    world: World, name: str
) -> None:
    fixture_glyph(world, name)
    panel, _ = panel_of(name)
    make_work(panel, name)
    assert panel.apply_button.enabled, (name, texts(panel))
    world.round_writes = True
    press(panel)
    assert "Error" not in panel.status.text, (name, panel.status.text)


def test_panel_when_structural_then_opens_with_all_masters(world: World) -> None:
    for name in NAMES:
        panel, _ = panel_of(name)
        renumbers = panel.STRUCTURAL or name == "Correct Contour Direction"
        assert panel.scope.currentIndex == (1 if renumbers else 0), name
        panel.close()


def test_bases_when_reloaded_then_consent_cleared(world: World) -> None:
    world.same("A", square(0, 0, 10))
    panel, _ = panel_of("Optimize Start Points")
    panel.bases.setChecked(True)
    panel.reload_button.clicked.emit()
    assert not panel.bases.isChecked(), "consent belongs to the glyphs the user saw"


def test_zero_when_line_then_handles_removed(world: World) -> None:
    world.same("A", [(0, 0, 1), (0, 0, 0), (30, 0, 0), (30, 0, 1), (15, 40, 1)])
    panel, _ = panel_of("Fix Zero Handles")
    panel.scope.setCurrentIndex(1)
    assert texts(panel)[0][-2:] == ["1 line, 0 singles", "1 to lines"]
    press(panel)
    assert world.points("A")[0] == [(0, 0, True), (30, 0, True), (15, 40, True)]


# ---------------------------------------------------------------- Duplicates
def test_duplicates_when_rotated_reversed_or_moved_then_found(world: World) -> None:
    ns = load("Delete Duplicate Contours")
    a = [(0, 0, True), (10, 0, True), (10, 10, True), (0, 10, True)]
    assert ns["same_cycle"](a, a[2:] + a[:2], 0)
    assert not ns["same_cycle"](a, a[::-1], 0)
    assert not ns["same_cycle"](a, [(0, 0, True), (10, 0, True), (10, 10, True)], 0)
    near = [(0.4, 0, True), *a[1:]]
    assert ns["same_cycle"](a, near, 0.5) and not ns["same_cycle"](a, near, 0.3)
    first = world.outline(square(0, 0, 10))
    moved = world.outline(square(-5, 0, 10), dx=5)
    world.glyph("A", {m: [first, moved] for m in world.masters})
    panel, _ = panel_of("Delete Duplicate Contours")
    panel.scope.setCurrentIndex(1)
    assert light(panel) == [["A · Light", "contour 2", "same as contour 1", "delete"]]
    press(panel)
    assert moved.contours == [] and len(first.contours) == 1


# ---------------------------------------------------------------- Transform
def test_mapper_when_scale_skew_turn_move_then_exact_matrix(world: World) -> None:
    ns = load("Transform")
    apply = ns["affine"].apply
    m = ns["mapper"]((200, 50, 0, 0, 10, -5), (100, 100))
    assert apply(m, 150, 300) == (210.0, 195.0), "scale about (100, 100), then move"
    turn = ns["mapper"]((100, 100, 0, 90, 0, 0), (0, 0))
    x, y = apply(turn, 10, 0)
    assert (round(x, 9), round(y, 9)) == (0, 10)
    skew = ns["mapper"]((100, 100, 45, 0, 0, 0), (0, 0))
    assert apply(skew, 0, 100) == pytest.approx((100, 100))
    with pytest.raises(ValueError):
        ns["mapper"]((0, 100, 0, 0, 0, 0), (0, 0))


def test_transform_when_applied_then_bakes_plain_composes_component_moves_anchors(
    world: World,
) -> None:
    plain = world.outline(square(0, 0, 100))
    shared = world.outline(square(0, 0, 100), refs=2)
    mark = Shape(world, base="acute", dx=10)
    world.glyph(
        "A",
        {m: [plain, shared, mark] for m in world.masters},
        anchors={"Light": [("top", 50, 100)]},
    )
    panel, _ = panel_of("Transform")
    panel.origin.setCurrentIndex(2)
    panel.scale_x.setValue(200.0)
    assert texts(panel) == [
        ["A · Light", "outline", "8 nodes", "0, 0"],
        ["A · Light", "anchors", "1 anchor", "move"],
    ]
    press(panel)
    assert (
        plain.contours[0].xy()[1] == (200, 0, True) and plain.transform.values[0] == 1
    )
    assert ("bake", plain.name) in world.events
    assert shared.transform.values == (2, 0, 0, 1, 0, 0), "shared data: composed"
    assert shared.contours[0].xy()[1] == (100, 0, True)
    assert mark.transform.values == (2, 0, 0, 1, 20, 0), "component: composed"
    pin = world.layer("A").anchors[0]
    assert (pin.point.x(), pin.point.y()) == (100, 100)


def test_transform_when_anchor_lands_on_origin_then_blocked(world: World) -> None:
    world.glyph(
        "A",
        {m: [world.outline(square(0, 0, 100))] for m in world.masters},
        anchors={"Light": [("bottom", 10, 0)]},
    )
    panel, _ = panel_of("Transform")
    panel.move_x.setValue(-10.0)
    assert not panel.apply_button.enabled
    assert (
        "bottom would move to 0, 0" in panel.status.text
        and "fl#8527" in panel.status.text
    )
    panel.anchors.setChecked(False)
    assert panel.apply_button.enabled


def test_transform_preview_when_painted_then_paths_and_painter_ends(
    world: World,
) -> None:
    world.same("A", square(0, 0, 100))
    panel, _ = panel_of("Transform")
    panel.move_x.setValue(50.0)
    assert panel.preview.after[0][0] == (50, 0, True)
    panel.preview.paintEvent(None)
    painter = Painter.log[-1]
    assert painter.ended and len(painter.paths) == 2
    assert painter.paths[1].calls[0] == ("move", 50, 0)
    Painter.fail = True
    panel.preview.paintEvent(None)
    assert Painter.log[-1].ended, "the painter always ends"
    assert panel.status.text.startswith("Preview failed")
    panel.close_button.clicked.emit()
    assert panel.preview.report is None, "callback dropped on close"


# ---------------------------------------------------------------- Slant
def test_slant_when_half_x_height_then_pivot_and_italic_button(world: World) -> None:
    ns = load("Slant")
    apply = app("affine").apply
    assert apply(ns["slant_matrix"](45, 0), 0, 100) == pytest.approx((100, 100))
    assert apply(ns["slant_matrix"](45, 250), 0, 250) == pytest.approx((0, 250))
    with pytest.raises(ValueError):
        ns["slant_matrix"](90, 0)
    world.same("A", square(0, 0, 100))
    panel, _ = panel_of("Slant")
    assert panel.italic.text == "Current master’s italic angle (-12°)"
    assert texts(panel)[0] == ["A · Light", "outline", "4 nodes", "250"]
    assert panel.preview.guide_y == 250
    panel.italic.clicked.emit()
    assert panel.angle.value == 12.0
    panel.pivots.setCurrentIndex(0)
    panel.angle.setValue(45.0)
    press(panel)
    assert world.points("A")[0][3] == (100, 100, True), "(0, 100) leans right by 100"
    assert world.points("A", "Bold")[0][3] == (0, 100, True), "current master only"


# ---------------------------------------------------------------- review regressions
@pytest.mark.parametrize("rotation", range(4))
def test_direction_when_outers_overlap_then_kept_for_every_start(
    world: World, rotation: int
) -> None:
    stem = [(0, 0, 1), (100, 0, 1), (100, 700, 1), (0, 700, 1)]
    bar = [(20, 300, 1), (300, 300, 1), (300, 380, 1), (20, 380, 1)]
    world.same("A", stem, bar[rotation:] + bar[:rotation])
    ns = load("Correct Contour Direction")
    assert not [r for r in ns["direction_changes"](world.layer("A")) if r.edit], (
        "overlapping outers stay outer"
    )


def test_direction_when_outer_is_shared_scaled_then_counter_still_nested(
    world: World,
) -> None:
    outer = world.outline(square(0, 0, 100), refs=2, matrix=(2, 0, 0, 2))
    inner = world.outline(square(25, 25, 50, clockwise=True))
    world.glyph("A", {m: [outer, inner] for m in world.masters})
    ns = load("Correct Contour Direction")
    rows = ns["direction_changes"](world.layer("A"))
    assert not [r for r in rows if r.edit], "cross-shape ambiguity must not edit"
    assert any(r.new == "inside another shape, direction left" for r in rows)


def test_small_when_long_open_stroke_then_kept_without_area(
    world: World, monkeypatch: Any
) -> None:
    contour = Contour(world, [(0, 0, 1), (10000, 0, 1)], closed=False)
    world.glyph("A", {m: [Shape(world, [contour])] for m in world.masters})
    ns = load("Delete Small Contours")

    def no_area(parts: Any) -> float:
        raise AssertionError("open contour must not be measured by area")

    monkeypatch.setattr(ns["contour_selection"], "unsigned_area", no_area)
    rows = ns["small_changes"](world.layer("A"), 400)
    assert all(r.edit is None for r in rows)
    assert any("open contour, kept" in r.new for r in rows)


@pytest.mark.parametrize("copies", [2, 3])
def test_duplicates_when_reversed_pair_then_every_member_kept(
    world: World, copies: int
) -> None:
    a = square(0, 0, 10)
    world.same("A", a, a[::-1], *([a] if copies == 3 else []))
    ns = load("Delete Duplicate Contours")
    rows = ns["duplicate_changes"](world.layer("A"), 0)
    assert not [r for r in rows if r.edit], (
        "a third copy must also keep cancelling winding"
    )
    assert any("reversed duplicate, kept" in r.new for r in rows)


def test_duplicates_when_open_paths_different_start_then_kept(world: World) -> None:
    a = square(0, 0, 10)
    contours = [
        Contour(world, a, closed=False),
        Contour(world, a[1:] + a[:1], closed=False),
    ]
    world.glyph("A", {m: [Shape(world, contours)] for m in world.masters})
    ns = load("Delete Duplicate Contours")
    assert not [r for r in ns["duplicate_changes"](world.layer("A"), 0) if r.edit]


def test_extremes_when_cut_near_endpoint_then_not_offered(world: World) -> None:
    ns = load("Add Extremes")
    tiny = [(x / 10000, y / 10000, bool(on)) for x, y, on in ARCH]
    assert ns["contour_plan"](tiny) == [], (
        "native reuses a node within 0.1 Manhattan units"
    )


def test_overlap_when_scan_revisits_shape_then_merge_cached(
    world: World, monkeypatch: Any
) -> None:
    world.same("A", square(0, 0, 10), square(5, 5, 10))
    panel, _ = panel_of("Remove Overlap")
    calls: list[Any] = []
    original = FgShape.removeOverlap

    def counted(self: FgShape) -> int:
        calls.append(self)
        return original(self)

    monkeypatch.setattr(FgShape, "removeOverlap", counted)
    plan = panel.planner()
    glyph = world.glyphs["A"]
    plan(glyph, "Light", world.layer("A"))
    plan(glyph, "Light", world.layer("A"))
    assert len(calls) == 1, "cache is limited to this scan/planner"
    panel.planner()(glyph, "Light", world.layer("A"))
    assert len(calls) == 2, "fresh Apply/scan recomputes"


def test_overlap_when_disjoint_normalisation_then_no_merge(
    world: World, monkeypatch: Any
) -> None:
    world.same("A", square(0, 0, 10), square(50, 50, 10))
    ns = load("Remove Overlap")

    def forbidden(self: FgShape) -> int:
        raise AssertionError("no real intersection: no destructive merge")

    monkeypatch.setattr(FgShape, "removeOverlap", forbidden)
    assert not [r for r in ns["overlap_changes"](world.layer("A")) if r.edit]


@pytest.mark.parametrize(
    "name,editor",
    [
        ("Correct Contour Direction", "ReverseEditor"),
        ("Optimize Start Points", "StartEditor"),
        ("Remove Overlap", "MergeEditor"),
    ],
)
@pytest.mark.parametrize("preexisting", [False, True])
def test_readback_when_final_smooth_introduced_then_advice_not_store_failure(
    world: World, name: str, editor: str, preexisting: bool
) -> None:
    contour = Contour(world, [(0, 0, 1), (100, 0, 1), (100, 50, 0), (0, 50, 0)])
    contour.nodes()[-1].smooth = preexisting
    shape = Shape(world, [contour])
    world.glyph("A", {m: [shape] for m in world.masters})
    ns = load(name)
    steps = {
        "ReverseEditor": [(contour, True)],
        "StartEditor": [(contour, 0, (0, 0))],
        "MergeEditor": [(shape, None, set(), 1)],
    }[editor]
    writer = ns[editor]()
    prepared = writer.prepare(world.layer("A"), steps)
    contour.nodes()[-1].smooth = True  # native write introduces the condition
    missed = writer.check([(world.layer("A"), prepared)])
    assert not any("fl#8517" in text for text in missed), (
        "a stored edit is not a mismatch"
    )
    assert bool(writer.advice) != preexisting, (
        "only a newly introduced final Smooth control is reported"
    )
    if writer.advice:
        assert "final off-curve with raw Smooth" in writer.advice[0]
        assert "FontLab may change on save" in writer.advice[0]


def test_direction_when_separate_element_inside_then_left_with_note(
    world: World,
) -> None:
    outer = world.outline(square(0, 0, 100))
    element = world.outline(square(25, 25, 50))
    world.glyph("A", {m: [outer, element] for m in world.masters})
    ns = load("Correct Contour Direction")
    rows = ns["direction_changes"](world.layer("A"))
    assert not [r for r in rows if r.edit], (
        "nesting within each shape decides direction"
    )
    assert any(r.new == "inside another shape, direction left" for r in rows)


@pytest.mark.parametrize("name", NAMES)
def test_docstrings_when_reflowed_then_within_eighty_columns(name: str) -> None:
    tree = ast.parse((FOLDER / f"{name}.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                assert all(len(line) <= 80 for line in doc.splitlines()), name


@pytest.mark.parametrize("name", ["Transform", "Slant"])
def test_transform_when_anchor_moves_from_near_origin_to_origin_then_app_refuses(
    world: World, name: str
) -> None:
    ns = load(name)
    layer = NS(shapes=[], anchors=[NS(name="top", point=Point(0.3, 0))])
    rows = ns["outline_transform"].transform_changes(
        layer, (1, 0, 0, 1, -0.3, 0), True, ""
    )
    assert any("fl#8527" in r.problem for r in rows), "already fixed by App"


@pytest.mark.parametrize(
    "name,phrases",
    [
        ("Remove Overlap", ["separate shapes", "corner_smooth", "appearance"]),
        ("Add Extremes", ["parameter t", "rounding"]),
        ("Straighten Short Curves", ["recomputes the smooth flags at both ends"]),
        ("Round Coordinates", ["meant to keep node names and flags", "not measured"]),
        (
            "Optimize Start Points",
            ["meant to keep the node flags", "See Safety for VFJ reopen"],
        ),
        ("Fix Zero Handles", ["Smooth base", "non-collinear"]),
        ("Slant", ["Tools > Actions > Slant", "current master"]),
    ],
)
def test_safety_text_when_reviewed_then_states_native_limits(
    name: str, phrases: list[str]
) -> None:
    doc = " ".join(
        ast.get_docstring(ast.parse((FOLDER / f"{name}.py").read_text())).split()
    )
    assert all(p in doc for p in phrases), f"{name}: missing native safety rule"


def test_direction_when_vertices_inside_but_midpoint_outside_then_not_nested(
    world: World,
) -> None:
    # U-shaped outer, with a gap through the top half. The triangle spans the gap.
    outer = [
        (0, 0, 1),
        (100, 0, 1),
        (100, 100, 1),
        (70, 100, 1),
        (70, 30, 1),
        (30, 30, 1),
        (30, 100, 1),
        (0, 100, 1),
    ]
    triangle = [(10, 80, 1), (10, 10, 1), (90, 80, 1)]
    world.same("A", outer, triangle)
    ns = load("Correct Contour Direction")
    assert not [r for r in ns["direction_changes"](world.layer("A")) if r.edit], (
        "every midpoint must also be inside"
    )


@pytest.mark.parametrize(
    "points",
    [
        [(0, 0, 1), (100, 0, 0), (100, 100, 0), (0, 100, 1)],
        [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0)],
    ],
)
def test_direction_when_truetype_implied_nodes_then_native_segments_used(
    world: World, points: Spec, monkeypatch: Any
) -> None:
    contour = Contour(world, points, tt=True)
    world.glyph("A", {m: [Shape(world, [contour])] for m in world.masters})
    ns = load("Correct Contour Direction")
    calls: list[float] = []
    original = contour.calculate

    def calculate(t: float) -> Point:
        calls.append(t)
        return original(t)

    monkeypatch.setattr(contour, "calculate", calculate)
    rows = ns["direction_changes"](world.layer("A"))
    assert any(r.edit for r in rows), "CCW TrueType outer must reverse"
    assert all(k + 0.5 in calls for k in range(len(contour.segments()))), (
        "native implied segments supply midpoint tests"
    )


@pytest.mark.parametrize("name", NAMES)
def test_undo_text_when_read_then_no_unmeasured_restoration_claim(name: str) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    assert "recorded as one" in source
    assert "Undo restores" not in source and "Undo brings back" not in source


def test_small_dependency_when_documented_then_fontui_named() -> None:
    source = (FOLDER / "Delete Small Contours.py").read_text()
    assert "fontlab-fontlabapp[fontui]" in source, "M8 already documents the dependency"


def test_app_writer_when_read_then_preservation_is_strategy_specific(
    world: World,
) -> None:
    load("Round Coordinates")
    writer = sys.modules["fontlabapp.layer_writer"]
    assert "write strategy decides what is kept" in writer.apply_work.__doc__
    assert "names, notes and node flags stay" not in writer.apply_work.__doc__


@pytest.mark.parametrize(
    "name,editor",
    [
        ("Correct Contour Direction", "ReverseEditor"),
        ("Optimize Start Points", "StartEditor"),
        ("Remove Overlap", "MergeEditor"),
    ],
)
def test_apply_when_save_risk_advice_then_success_status_keeps_truthful_note(
    world: World, monkeypatch: Any, name: str, editor: str
) -> None:
    fixture_glyph(world, name)
    panel, ns = panel_of(name)
    make_work(panel, name)
    message = "a final off-curve with raw Smooth; FontLab may change on save (fl#8517)"

    def check(writer: Any, prepared: Any) -> list[str]:
        writer.advice = [message]
        return []

    monkeypatch.setattr(ns[editor], "check", check)
    press(panel)
    assert panel.status.text.startswith(panel.DONE), panel.status.text
    assert message in panel.status.text, "successful writes must show save-risk advice"
    assert "did not store" not in panel.status.text
