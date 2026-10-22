# this_file: tests/test_issue122_G12.py
# SPDX-License-Identifier: Apache-2.0
"""Contour behaviour rewrites on the real App kernel and owned native fakes."""

import ast
import inspect
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

ISOLATED = ("fly", "fontlabapp", "echopy")

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
    echopy = ModuleType("echopy")
    echopy.__path__ = []
    monkeypatch.setitem(sys.modules, "echopy", echopy)
    monkeypatch.setitem(sys.modules, "echopy.fontlab", fontlab)
    yield w
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
        del sys.modules[key]


def press(panel: Any) -> None:
    """Invoke the owned button signal."""
    panel.apply_button.clicked.emit()


def square(x: float, y: float, size: float) -> Spec:
    """Counterclockwise rectangle fixture."""
    return [(x, y, 1), (x + size, y, 1), (x + size, y + size, 1), (x, y + size, 1)]


ROOT = Path(__file__).parents[1]
TITLES = (
    "Comb",
    "Curve All Straights",
    "Delete Close Points",
    "Make Compatible",
    "Sandblast",
    "Straighten All Curves",
    "Superaligner",
    "Interpolated Nudge",
)


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts" / "Contours" / f"{title}.py"))


@pytest.mark.parametrize("title", TITLES)
def test_script_contract(title: str, world: Any) -> None:
    path = ROOT / "Scripts" / "Contours" / f"{title}.py"
    text = path.read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    doc = ast.get_docstring(tree)
    assert all(
        word in doc
        for word in ("What:", "How:", "Why:", "Use:", "Benefit:", "Simon Cozens", "MIT")
    )
    assert "# this_file: " + str(path.relative_to(ROOT)) in text
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ToolPanel":
            assert (
                not {x.name for x in node.body if isinstance(x, ast.FunctionDef)}
                & NATIVE_MEMBERS
            )
    ns = load(title)
    panel = ns["main"]()
    assert not panel.apply_button.enabled
    panel.close()
    assert not world.notifications()


def test_real_app_imports() -> None:
    used = app_names_used([ROOT / "Scripts" / "Contours" / f"{t}.py" for t in TITLES])
    used.setdefault("fly.ap.history", set()).update({"commit", "scan_auto_facts"})
    check_real_app_names(used)


@pytest.fixture(autouse=True)
def native_extensions(world: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Extend the shared owned fakes with the exact native methods used here."""
    import sys

    monkeypatch.setattr(Node, "selected", False, raising=False)
    monkeypatch.setattr(Node, "smooth", False, raising=False)
    monkeypatch.setattr(Layer, "advanceHeight", 1000.0, raising=False)
    monkeypatch.setattr(Layer, "guidelines", (), raising=False)

    def convert(node: Any, smooth: bool = False) -> bool:
        contour = node.contour
        nodes = contour._nodes
        index = nodes.index(node)
        previous = nodes[index - 1]
        assert previous.isOn(), "conversion must address a line endpoint"
        if contour._guard():
            controls = [
                Node(
                    contour,
                    previous.x + (node.x - previous.x) * t,
                    previous.y + (node.y - previous.y) * t,
                    False,
                )
                for t in (0.33, 0.67)
            ]
            if index:
                nodes[index:index] = controls
            else:
                nodes.extend(controls)
        return True

    def remove(contour: Any, index: int) -> None:
        if contour._guard():
            contour._nodes.pop(index)

    def add(shape: Any, contour: Any) -> None:
        if world.fail_write:
            raise RuntimeError("boom write")
        if not world.ignore_writes:
            shape._contours.append(contour)

    def make_node(point: Any, *, nodeType: str = "on") -> Any:
        from types import SimpleNamespace

        assert nodeType in {"on", "curve"}, (
            "cubic controls must use the native Curve type"
        )
        return SimpleNamespace(x=point.x(), y=point.y(), on=nodeType == "on")

    def make_contour(nodes: list[Any], *, closed: bool = False) -> Any:
        return Contour(world, [(n.x, n.y, n.on) for n in nodes], closed)

    monkeypatch.setattr(Node, "convertToCurve", convert, raising=False)
    monkeypatch.setattr(Contour, "removeAt", remove, raising=False)
    monkeypatch.setattr(Shape, "addContour", add, raising=False)

    def clockwise(contour: Any) -> bool:
        points = [(n.x, n.y) for n in contour.nodes() if n.isOn()]
        return (
            sum(
                a[0] * b[1] - b[0] * a[1]
                for a, b in zip(points, points[1:] + points[:1])
            )
            < 0
        )

    monkeypatch.setattr(Contour, "clockwise", property(clockwise), raising=False)
    monkeypatch.setattr(
        Contour, "path", lambda self: Containment(self.xy()), raising=False
    )
    monkeypatch.setattr(
        Shape,
        "closedPath",
        property(
            lambda self: Containment(
                self.contours[0].xy(), [c.xy() for c in self.contours[1:]]
            )
        ),
        raising=False,
    )
    import importlib

    selection = importlib.import_module("fly.ap.layer_selection")
    monkeypatch.setattr(
        selection,
        "capture",
        lambda deadline: NS(
            occurrences=[
                NS(glyph=world.glyphs[n], layer=world.layer(n)) for n in world.selected
            ]
        ),
    )
    monkeypatch.setattr(sys.modules["fontlab"], "flNode", make_node, raising=False)
    monkeypatch.setattr(
        sys.modules["fontlab"], "flContour", make_contour, raising=False
    )
    monkeypatch.setattr(
        PainterPath, "contains", lambda self, other: False, raising=False
    )


class Containment:
    """Rectangle containment fixture, including rectangular counters."""

    def __init__(
        self, points: list | None = None, counters: list | None = None
    ) -> None:
        self.points = points or square(0, 0, 100)
        self.counters = counters or []

    def boundingRect(self) -> Rect:
        return bounds([(p[0], p[1]) for p in self.points])

    def contains(self, path: Any) -> bool:
        points = path.points if hasattr(path, "points") else [(path.x(), path.y())]

        def inside(x: float, y: float, polygon: list) -> bool:
            return min(p[0] for p in polygon) < x < max(p[0] for p in polygon) and min(
                p[1] for p in polygon
            ) < y < max(p[1] for p in polygon)

        return all(
            inside(x, y, self.points)
            and not any(inside(x, y, c) for c in self.counters)
            for x, y in points
        )


CUBIC = [
    (0, 0, True),
    (33, 40, False),
    (67, 40, False),
    (100, 0, True),
    (100, 100, True),
    (0, 100, True),
]


def ready(world: Any, title: str) -> tuple[Any, dict[str, Any]]:
    if title == "Make Compatible":
        world.glyph(
            "a",
            {
                "Light": [world.outline(square(0, 0, 100))],
                "Bold": [world.outline(CUBIC)],
            },
        )
    elif title == "Superaligner":
        world.glyph(
            "a",
            {
                "Light": [world.outline(CUBIC)],
                "Bold": [world.outline(CUBIC[3:] + CUBIC[:3])],
            },
        )
    elif title == "Delete Close Points":
        world.same(
            "a",
            [
                (0, 0, True),
                (2, 0, True),
                (100, 0, True),
                (100, 100, True),
                (0, 100, True),
            ],
        )
    elif title in ("Straighten All Curves", "Interpolated Nudge"):
        world.same("a", CUBIC)
    else:
        world.same("a", square(0, 0, 100))
    if title == "Interpolated Nudge":
        world.layer("a").shapes[0].contours[0].nodes()[0].selected = True
    ns = load(title)
    panel = ns["main"]()
    panel.refresh()
    return panel, ns


@pytest.mark.parametrize("title", TITLES)
def test_apply_when_valid_then_one_notification_with_layers_and_glyph(
    title: str, world: Any
) -> None:
    panel, ns = ready(world, title)
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert not panel.slot_error, panel.status.text
    assert len(world.notifications()) == 1, world.events
    notify = world.notifications()[0]
    assert notify[1] == title
    assert notify[2][-1] == "a", notify
    assert all("/" in marker for marker in notify[2][:-1]), notify
    assert ns["writer"].__name__ == "fontlabapp.outline_writer"


@pytest.mark.parametrize("title", TITLES)
def test_refusals_when_queued_or_auto_then_no_history(title: str, world: Any) -> None:
    panel, _ = ready(world, title)
    world.pending = [44]
    press(panel)
    assert world.notifications() and world.pending == [44]
    assert panel.last_result["pending_updates"] == (44,) and "8537" in panel.status.text and panel.last_result["pending_note"] in panel.status.text
    world.events.clear()
    world.pending = []
    world.layer("a").autoLayer = True
    panel.reload()
    assert not panel.apply_button.enabled
    press(panel)
    assert not world.notifications()


@pytest.mark.parametrize("title", TITLES)
def test_partial_failure_when_native_write_raises_then_one_notification_and_undo_hint(
    title: str, world: Any
) -> None:
    panel, _ = ready(world, title)
    world.fail_write = True
    press(panel)
    assert "Native changes may remain; use Edit > Undo" in panel.status.text
    assert len(world.notifications()) == 1


@pytest.mark.parametrize("title", TITLES)
def test_read_back_when_native_ignores_write_then_error(title: str, world: Any) -> None:
    panel, _ = ready(world, title)
    world.ignore_writes = True
    press(panel)
    assert "Error" in panel.status.text, panel.status.text
    assert "Use Edit > Undo" in panel.status.text
    assert len(world.notifications()) == 1


@pytest.mark.parametrize("title", TITLES)
def test_panel_when_font_missing_then_no_edits_and_close_disconnects(
    title: str, world: Any
) -> None:
    world.no_font = True
    ns = load(title)
    panel = ns["main"]()
    assert not panel.apply_button.enabled
    panel.close()
    assert not world.notifications()
    assert not panel._connections


def test_curve_conversion_when_square_then_eight_new_controls(world: Any) -> None:
    panel, _ = ready(world, "Curve All Straights")
    press(panel)
    points = world.points("a")[0]
    assert len(points) == 12
    assert sum(not p[2] for p in points) == 8
    assert points[1][:2] == (33, 0)
    assert points[2][:2] == (67, 0)


def test_straighten_when_cubic_then_only_endpoints(world: Any) -> None:
    panel, _ = ready(world, "Straighten All Curves")
    press(panel)
    assert world.points("a")[0] == [
        (0, 0, True),
        (100, 0, True),
        (100, 100, True),
        (0, 100, True),
    ]


def test_delete_when_short_line_then_merge_and_keep_three_endpoints(world: Any) -> None:
    panel, ns = ready(world, "Delete Close Points")
    press(panel)
    assert world.points("a")[0] == square(0, 0, 100)
    assert ns["arc_length"](world.layer("a").shapes[0].contours[0].nodes()[:2]) == 100
    with pytest.raises(ValueError):
        ns["changes"](world.layer("a"), float("nan"))


def test_compatible_when_one_master_has_curve_then_only_line_master_changes(
    world: Any,
) -> None:
    panel, _ = ready(world, "Make Compatible")
    press(panel)
    assert len(world.points("a", "Light")[0]) == 6
    assert world.points("a", "Bold")[0] == CUBIC
    assert world.notifications()[0][2] == ["a/Light", "a"]


def test_align_when_shifted_types_then_rotates_to_reference(world: Any) -> None:
    panel, ns = ready(world, "Superaligner")
    press(panel)
    assert world.points("a", "Bold")[0] == CUBIC
    assert ns["alignment"](CUBIC, CUBIC[3:] + CUBIC[:3]) == (False, 3)
    with pytest.raises(ValueError):
        ns["alignment"](CUBIC, CUBIC[:1])


def test_comb_when_rectangle_then_exact_strips(world: Any) -> None:
    ns = load("Comb")
    points = square(0, 0, 100)
    edges = [[points[i], points[(i + 1) % 4]] for i in range(4)]
    assert ns["striped"](edges, 2, 0.5) == [
        [(100, 0, 1), (100, 100, 1), (75, 100, 1), (75, 0, 1)],
        [(50, 0, 1), (50, 100, 1), (25, 100, 1), (25, 0, 1)],
    ]
    with pytest.raises(ValueError):
        ns["striped"](edges, 0, 0.5)


def test_holes_when_seeded_then_reproducible_bounded_and_disjoint(world: Any) -> None:
    ns = load("Sandblast")
    a = ns["holes"](Containment(), (0, 0, 100, 100), 20, 2, 3)
    assert a == ns["holes"](Containment(), (0, 0, 100, 100), 20, 2, 3)
    assert len(a) == 20 and all(len(p) == 12 for p in a)
    assert all(0 < x < 100 and 0 < y < 100 for polygon in a for x, y in polygon)

    class Empty:
        def contains(self, path: Any) -> bool:
            return False

    assert ns["holes"](Empty(), (0, 0, 1, 1), 1, 1, 0) == []
    with pytest.raises(ValueError):
        ns["holes"](Containment(), (0, 0, 1, 1), 1, float("nan"), 0)


def test_nudge_when_one_endpoint_moves_then_handle_ratios_stay(world: Any) -> None:
    ns = load("Interpolated Nudge")
    result = ns["nudged"](CUBIC, {0}, 10, 0)
    assert result[:4] == [(10, 0), (39.7, 40), (70.3, 40), (100, 0)]
    result = ns["nudged"](CUBIC, {0, 3}, 10, 5)
    assert result[:4] == [(10, 5), (43, 45), (77, 45), (110, 5)]
    with pytest.raises(ValueError):
        ns["nudged"](CUBIC, {1}, 10, 0)


def test_hole_editor_direct_write(world: Any) -> None:
    panel, ns = ready(world, "Sandblast")
    layer = world.layer("a")
    edits = [row.edit for row in ns["changes"](layer, 2, 3, 1) if row.edit is not None]
    editor = panel.editor()
    steps = editor.prepare(layer, edits)
    editor.write(layer, steps)
    assert not editor.check([(layer, steps)])


@pytest.mark.parametrize("title", TITLES)
def test_timeout_when_capture_fails_then_visible_and_apply_disabled(
    title: str, world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, _ = ready(world, title)

    def timeout() -> None:
        raise TimeoutError("Selection deadline reached")

    monkeypatch.setattr(panel, "scan", timeout)
    panel.reload()
    assert "Selection deadline" in panel.status.text
    assert not panel.apply_button.enabled


@pytest.mark.parametrize("title", ["Make Compatible", "Superaligner"])
def test_mismatched_master_contours_when_planned_then_no_history(
    title: str, world: Any
) -> None:
    panel, _ = ready(world, title)
    world.layer("a", "Bold")._shapes.append(world.outline(square(0, 0, 50)))
    panel.refresh()
    assert not panel.apply_button.enabled
    assert "contour counts differ" in panel.table.row_texts()[0][3]
    press(panel)
    assert not world.notifications()


@pytest.mark.parametrize(
    "title",
    [
        "Curve All Straights",
        "Straighten All Curves",
        "Delete Close Points",
        "Interpolated Nudge",
    ],
)
def test_open_and_quadratic_when_planned_then_kept(title: str, world: Any) -> None:
    panel, _ = ready(world, title)
    for glyph in world.glyphs.values():
        for layer in glyph.layers:
            for shape in layer.shapes:
                for contour in shape.contours:
                    contour.isTT = True
                    contour.closed = False
    panel.refresh()
    assert not panel.apply_button.enabled
    assert not world.notifications()


def test_compatibility_when_counts_differ_then_no_truncation(world: Any) -> None:
    panel, _ = ready(world, "Make Compatible")

    contour = world.layer("a", "Bold").shapes[0].contours[0]
    contour._nodes.append(Node(contour, 10, 10, True))
    panel.refresh()
    assert any(
        "segment counts differ" in cell
        for row in panel.table.row_texts()
        for cell in row
    )
    assert not panel.apply_button.enabled


def test_delete_when_wrapped_short_curve_then_first_survivor_is_oncurve(
    world: Any,
) -> None:
    world.same(
        "a",
        [
            (0, 0, True),
            (20, 10, False),
            (80, 10, False),
            (100, 0, True),
            (100, 100, True),
            (0, 100, True),
            (0, 2, True),
        ],
    )
    ns = load("Delete Close Points")
    rows = ns["changes"](world.layer("a"), 5)
    editor = ns["MergeEditor"]()
    edits = [r.edit for r in rows if r.edit is not None]
    editor.write(world.layer("a"), edits)
    assert world.points("a")[0][0][2]
    assert not editor.check([(world.layer("a"), edits)])


def test_alignment_when_reversal_required_then_reports_reverse(world: Any) -> None:
    ns = load("Superaligner")
    reference = [(0, 0, True), (80, 10, True), (100, 90, True), (5, 120, True)]
    candidate = reference[:1] + reference[:0:-1]
    assert ns["alignment"](reference, candidate) == (True, 0)
    world.glyph(
        "a", {"Light": [world.outline(reference)], "Bold": [world.outline(candidate)]}
    )
    contour = world.layer("a", "Bold").shapes[0].contours[0]
    before = contour.clockwise
    panel = ns["main"]()
    press(panel)
    assert contour.clockwise is not before, "a direction reversal must actually happen"
    assert world.points("a", "Bold")[0] == reference


@pytest.mark.parametrize("title", ["Comb", "Make Compatible", "Superaligner"])
def test_mixed_selection_when_one_glyph_unsuitable_then_write_only_valid(
    title: str, world: Any
) -> None:
    panel, _ = ready(world, title)
    if title == "Comb":
        world.same("bad", [(0, 0, True), (50, 70, True), (100, 0, True)])
    else:
        world.glyph(
            "bad",
            {
                "Light": [world.outline(square(0, 0, 100))],
                "Bold": [world.outline(square(0, 0, 100), square(20, 20, 20))],
            },
        )
    before = world.points("bad")
    valid_before = {master: world.points("a", master) for master in world.masters}
    panel.reload()
    assert panel.apply_button.enabled, panel.status.text
    assert any("kept" in text for row in panel.table.row_texts() for text in row)
    press(panel)
    assert not panel.slot_error, panel.status.text
    assert all("bad" not in marker for marker in world.notifications()[0][2])
    assert "a" in world.notifications()[0][2], "the valid glyph must be notified"
    assert any(
        world.points("a", master) != valid_before[master] for master in world.masters
    ), "the valid glyph's points must change"
    assert world.points("bad") == before


@pytest.mark.parametrize("title", ["Curve All Straights", "Straighten All Curves"])
def test_selection_when_only_current_layer_selected_then_map_same_contours(
    title: str, world: Any
) -> None:
    first = square(0, 0, 100) if title == "Curve All Straights" else CUBIC
    second = (
        square(200, 0, 100)
        if title == "Curve All Straights"
        else [(x + 200, y, on) for x, y, on in CUBIC]
    )
    world.same("a", first, second)
    world.layer("a").shapes[0].contours[0].nodes()[0].selected = True
    # Deliberately conflicting selection in the other master must be ignored.
    world.layer("a", "Bold").shapes[0].contours[1].nodes()[0].selected = True
    ns = load(title)
    panel = ns["main"]()
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert not panel.slot_error, panel.status.text
    count = 12 if title == "Curve All Straights" else 4
    for master in world.masters:
        assert len(world.points("a", master)[0]) == count
        assert world.points("a", master)[1] == second


@pytest.mark.parametrize("title", ["Curve All Straights", "Straighten All Curves"])
def test_conversion_when_other_layer_incompatible_then_kept_and_current_written(
    title: str, world: Any
) -> None:
    panel, _ = ready(world, title)
    contour = world.layer("a", "Bold").shapes[0].contours[0]
    contour._nodes.append(Node(contour, 20, 30, True))
    before = world.points("a", "Bold")
    panel.refresh()
    assert panel.apply_button.enabled, panel.status.text
    assert any(
        "incompatible" in cell and "kept" in cell
        for row in panel.table.row_texts()
        for cell in row
    )
    press(panel)
    assert world.notifications()[0][2] == ["a/Light", "a"]
    assert world.points("a", "Bold") == before


def test_native_constructors_when_positional_optional_then_rejected(world: Any) -> None:
    native = sys.modules["fontlab"]
    point = Point(1, 2)
    with pytest.raises(TypeError):
        native.flNode(point, "curve")
    with pytest.raises(TypeError):
        native.flContour([], True)
    node = native.flNode(point, nodeType="curve")
    assert not node.on
    assert native.flContour([node], closed=True).closed


@pytest.mark.parametrize("title", TITLES)
def test_retry_when_previous_readback_failed_then_success_clears_hint(
    title: str, world: Any
) -> None:
    panel, _ = ready(world, title)
    world.ignore_writes = True
    press(panel)
    assert "Use Edit > Undo" in panel.status.text
    world.ignore_writes = False
    press(panel)
    assert not panel.slot_error, panel.status.text
    assert "Undo" not in panel.status.text, panel.status.text
    assert len(world.notifications()) == 2


def test_geometric_match_when_all_lines_then_start_decided_by_geometry(
    world: Any,
) -> None:
    ns = load("Superaligner")
    points = square(0, 0, 100)
    assert ns["alignment"](points, points[2:] + points[:2]) == (False, 2)
    with pytest.raises(ValueError, match="ambiguous start"):
        ns["alignment"]([(0, 0, True)] * 3, [(0, 0, True)] * 3)


def test_alignment_readback_when_wrong_start_has_same_types_then_detected(
    world: Any,
) -> None:
    world.glyph(
        "a",
        {
            "Light": [world.outline(square(0, 0, 100))],
            "Bold": [world.outline(square(0, 0, 100)[2:] + square(0, 0, 100)[:2])],
        },
    )
    ns = load("Superaligner")
    layer = world.layer("a", "Bold")
    edits = [
        r.edit
        for r in ns["changes"](world.glyphs["a"], "Bold", layer, world.masters)
        if r.edit is not None
    ]
    assert edits
    assert ns["AlignEditor"]().check([(layer, edits)]), (
        "unchanged all-line pattern must fail geometric read-back"
    )


def test_nudge_when_factor_would_flip_or_explode_then_nonnegative_and_bounded(
    world: Any,
) -> None:
    ns = load("Interpolated Nudge")
    points = [
        (0, 0, True),
        (0.66, 1, False),
        (1.34, 1, False),
        (2, 0, True),
        (2, 5, True),
        (0, 5, True),
    ]
    expanded = ns["nudged"](points, {3}, 10, 0)
    assert expanded[1][0] == pytest.approx(0.66 * 4), "factor must clamp to four"
    assert expanded[2][0] == pytest.approx(12 - (2 - 1.34) * 4)
    crossed = ns["nudged"](points, {0}, 10, 0)
    assert crossed[1][0] == 10 and crossed[2][0] == 2, (
        "crossed handles must collapse at their own endpoints"
    )
    tiny = [(x * 1e-12, y, on) for x, y, on in points]
    result = ns["nudged"](tiny, {0}, 10, 0)
    assert all(math.isfinite(x) and math.isfinite(y) for x, y in result)
    assert result[1][0] == pytest.approx(10 + 0.66e-12)


def test_sandblast_when_existing_counter_then_holes_stay_in_fill_and_cache_reused(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.same("a", square(0, 0, 100), square(30, 30, 40)[::-1])
    ns = load("Sandblast")
    layer = world.layer("a")
    cache = {}
    rows = ns["changes"](layer, 20, 2, 3, cache)
    result = rows[0].edit[1]
    assert result and all(
        not (30 < x < 70 and 30 < y < 70) for polygon in result for x, y in polygon
    )

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("placement should use the cache")

    monkeypatch.setitem(ns["changes"].__globals__, "holes", unexpected)
    assert ns["changes"](layer, 20, 2, 3, cache)[0].edit[1] == result


def test_make_compatible_when_components_present_then_outline_pairs_still_work(
    world: Any,
) -> None:
    panel, _ = ready(world, "Make Compatible")
    for master in world.masters:
        world.layer("a", master)._shapes.append(world.outline(base="base"))
    panel.refresh()
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert not panel.slot_error, panel.status.text


def test_panel_instance_assignments_when_parsed_then_no_native_member_collisions(
    world: Any,
) -> None:
    for title in TITLES:
        tree = ast.parse((ROOT / "Scripts/Contours" / f"{title}.py").read_text())
        attributes = {
            n.attr
            for n in ast.walk(tree)
            if isinstance(n, ast.Attribute)
            and isinstance(n.ctx, ast.Store)
            and isinstance(n.value, ast.Name)
            and n.value.id == "self"
        }
        assert not attributes & NATIVE_MEMBERS, (title, attributes & NATIVE_MEMBERS)


def test_delete_snapshot_when_node_equality_unsupported_then_plan_uses_indices(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.same(
        "a",
        [(0, 0, True), (2, 0, True), (100, 0, True), (100, 100, True), (0, 100, True)],
    )
    ns = load("Delete Close Points")

    def no_equal(self: Any, other: Any) -> bool:
        raise AssertionError("node wrapper equality must not be used")

    monkeypatch.setattr(Node, "__eq__", no_equal, raising=False)
    rows = ns["changes"](world.layer("a"), 5)
    assert rows[0].edit[1] == [1]


def test_curve_readback_when_smooth_flag_not_stored_then_detected(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, _ = ready(world, "Curve All Straights")
    monkeypatch.setattr(
        Node, "smooth", property(lambda self: False, lambda self, value: None)
    )
    press(panel)
    assert "Use Edit > Undo" in panel.status.text


def test_align_when_final_control_smooth_then_glyph_kept(world: Any) -> None:
    # The matching target order would leave its last two controls at the end.
    points = [
        (0, 0, True),
        (100, 0, True),
        (100, 100, True),
        (30, 90, False),
        (0, 30, False),
    ]
    target = points[1:] + points[:1]
    world.glyph(
        "a", {"Light": [world.outline(points)], "Bold": [world.outline(target)]}
    )
    # Last control in the desired order is target node 3.
    world.layer("a", "Bold").shapes[0].contours[0].nodes()[3].smooth = True
    ns = load("Superaligner")
    panel = ns["main"]()
    assert not panel.apply_button.enabled
    assert any("fl#8517" in cell for row in panel.table.row_texts() for cell in row)


def test_created_node_rounding_when_enabled_then_comb_readback_within_half_unit(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, _ns = ready(world, "Comb")
    original = sys.modules["fontlab"].flNode

    def rounded(point: Any, *, nodeType: str = "on") -> Any:
        return original(
            Point(math.floor(point.x() + 0.5), math.floor(point.y() + 0.5)),
            nodeType=nodeType,
        )

    monkeypatch.setattr(sys.modules["fontlab"], "flNode", rounded)
    press(panel)
    assert not panel.slot_error, panel.status.text


@pytest.mark.parametrize("title", ["Curve All Straights", "Straighten All Curves"])
@pytest.mark.parametrize("kind", ["shared", "scaled"])
def test_conversion_when_shape_omitted_then_distinct_kept_message(
    title: str, kind: str, world: Any
) -> None:
    _panel, ns = ready(world, title)
    shape = world.layer("a").shapes[0]
    if kind == "shared":
        shape.shapeData.referenceCount = 2
    else:
        shape._transform = Transform(2, 0, 0, 2, 0, 0)
    rows = ns["changes"](world.layer("a"))
    assert [row.new for row in rows] == ["shared or scaled shape, kept"]


@pytest.mark.parametrize("title", ["Comb", "Sandblast"])
def test_readback_when_host_copies_contours_and_equality_raises_then_geometry_passes(
    title: str, world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, _ = ready(world, title)

    def copied(shape: Any, contour: Any) -> None:
        shape._contours.append(Contour(world, contour.xy(), closed=contour.closed))

    def no_equal(self: Any, other: Any) -> bool:
        raise AssertionError("contour wrapper equality must not be used")

    monkeypatch.setattr(Shape, "addContour", copied)
    monkeypatch.setattr(Contour, "__eq__", no_equal, raising=False)
    press(panel)
    assert not panel.slot_error, panel.status.text
    assert len(world.notifications()) == 1


@pytest.mark.parametrize("title", ["Comb", "Sandblast"])
def test_readback_when_copied_contour_has_wrong_point_then_detected(
    title: str, world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, _ = ready(world, title)

    def wrong(shape: Any, contour: Any) -> None:
        points = contour.xy()
        points[0] = (points[0][0] + 10, points[0][1], points[0][2])
        shape._contours.append(Contour(world, points, closed=contour.closed))

    monkeypatch.setattr(Shape, "addContour", wrong)
    press(panel)
    assert "Use Edit > Undo" in panel.status.text


def test_straighten_docstring_when_read_then_states_current_layer_selection_rule(
    world: Any,
) -> None:
    doc = ast.get_docstring(
        ast.parse((ROOT / "Scripts/Contours/Straighten All Curves.py").read_text())
    )
    assert (
        "Select nodes in the current layer to choose whole contours, or leave nodes unselected for all contours."
        in " ".join(doc.split())
    )


@pytest.mark.parametrize("title", ["Comb", "Make Compatible", "Superaligner"])
def test_kept_message_when_error_has_trailing_punctuation_then_one_comma(
    title: str, world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _panel, ns = ready(world, title)

    def invalid(*args: Any) -> Any:
        raise ValueError("Example.,")

    monkeypatch.setitem(ns["changes"].__globals__, "plan_content", invalid)
    layer = world.layer("a")
    rows = (
        ns["changes"](layer, 7, 0.5)
        if title == "Comb"
        else ns["changes"](world.glyphs["a"], "Light", layer, world.masters)
    )
    assert rows[0].new == "Example, kept"


def test_comb_readback_when_multiple_ribbons_in_one_shape_then_complete_output_checked(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.same("a", square(0, 0, 100), square(200, 0, 100))
    ns = load("Comb")

    def copied(shape: Any, contour: Any) -> None:
        shape._contours.append(Contour(world, contour.xy(), closed=contour.closed))

    monkeypatch.setattr(Shape, "addContour", copied)
    panel = ns["main"]()
    press(panel)
    assert not panel.slot_error, panel.status.text
    assert len(world.points("a")) == 14


def test_scripts_use_only_public_app_names() -> None:
    """Forbid private module imports and attributes through every App alias."""
    used = app_names_used([ROOT / "Scripts/Contours" / f"{title}.py" for title in TITLES])
    assert all(
        not part.startswith("_") for module in used for part in module.split(".")
    ), used
    assert all(not name.startswith("_") for names in used.values() for name in names), used


@pytest.mark.parametrize("title", TITLES)
def test_panel_overrides_match_installed_public_hooks(world: Any, title: str) -> None:
    """Compare subclass calls with the installed base, using only native fakes."""
    import fly.ap.outline_panel as outline_panel  # noqa: PLR0402

    panel = load(title)["ToolPanel"]
    base = outline_panel.panel_type()
    public = set(outline_panel.HOOKS) | set(outline_panel.MEMBERS)
    inherited = set(panel.__dict__) & set(base.__dict__)
    overrides = {name for name in inherited if callable(getattr(panel, name))}
    assert overrides <= public, overrides - public
    for name in overrides:
        actual = inspect.signature(getattr(panel, name))
        expected = inspect.signature(getattr(base, name))
        assert [
            (p.name, p.kind, p.default) for p in actual.parameters.values()
        ] == [
            (p.name, p.kind, p.default) for p in expected.parameters.values()
        ], (name, actual, expected)
    for node in ast.walk(ast.parse((ROOT / "Scripts/Contours" / f"{title}.py").read_text())):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            assert not (node.value.id == "self" and node.attr.startswith("_")), node.attr


def test_explicit_fly_app_paths_have_no_private_names() -> None:
    """Also catch full fly.ap.module._member paths without import aliases."""
    for path in [ROOT / "Scripts/Contours" / f"{title}.py" for title in TITLES]:
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Attribute):
                continue
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name) and current.id == "fly" and parts[0] == "ap":
                assert all(not part.startswith("_") for part in parts), (path, parts)
