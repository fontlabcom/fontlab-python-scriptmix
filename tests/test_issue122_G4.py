# this_file: tests/test_issue122_G4.py
# SPDX-License-Identifier: Apache-2.0
"""Self-contained native fakes with the real installed Fly/App kernels."""

import ast
import itertools
import math
import runpy
import sys
from pathlib import Path
from time import monotonic
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Node Duplicator", "Smart Slant")

ISOLATED = ("fly", "fontlabapp", "echopy")

NATIVE_MEMBERS = {
    "metric",
    "update",
    "layout",
    "font",
    "palette",
    "parent",
    "style",
    "size",
    "pos",
    "width",
    "height",
    "geometry",
    "show",
    "hide",
    "open",
    "done",
    "accept",
    "reject",
    "exec",
    "repaint",
    "move",
    "resize",
    "rect",
    "title",
    "name",
    "windowTitle",
    "objectName",
    "children",
    "focus",
    "enabled",
    "visible",
    "actions",
    "cursor",
    "locale",
    "mask",
    "scroll",
    "find",
    "close",
    "render",
    "statusBar",
    "grab",
    "lower",
    "raise_",
    "x",
    "y",
    "frameGeometry",
}


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
        self.label, self.checked = (text, False)

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
        self.value, self.low, self.high = (0, 0, 99)

    def setRange(self, low: Any, high: Any) -> None:
        if self.INTEGER and (not (isinstance(low, int) and isinstance(high, int))):
            raise TypeError("QSpinBox.setRange wants int")
        self.low, self.high = (low, high)

    def setValue(self, value: Any) -> None:
        if self.INTEGER and (not isinstance(value, int)):
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
        self.cells[row, column] = item

    def row_texts(self) -> list[list[str]]:
        columns = max((c for _, c in self.cells), default=-1) + 1
        return [
            [self.cells[r, c].text() for c in range(columns) if (r, c) in self.cells]
            for r in range(self.rows)
        ]

    def colors(self) -> list[Any]:
        """Foreground colour value of the last cell of each row."""
        columns = max((c for _, c in self.cells), default=-1) + 1
        return [
            self.cells[r, columns - 1].foreground.color().value
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
        self._x, self._y = (float(x), float(y))

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
        return (x * a + y * c + e, x * b + y * d + f)

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
        if not self.box[2] and (not self.box[3]):
            return other
        x0 = min(self.x(), other.x())
        y0 = min(self.y(), other.y())
        x1 = max(self.x() + self.width(), other.x() + other.width())
        y1 = max(self.y() + self.height(), other.y() + other.height())
        return Rect(x0, y0, x1 - x0, y1 - y0)


def bounds(points: list[tuple[float, float]]) -> Rect:
    if not points:
        return Rect(0, 0, 0, 0)
    xs, ys = ([p[0] for p in points], [p[1] for p in points])
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
    qt.QtCore, qt.QtGui = (core, gui)
    return qt


IDS = itertools.count(1)

Spec = list[tuple[float, float, int]]


class Node:
    def __init__(self, contour: "Contour", x: float, y: float, on: bool) -> None:
        self.contour, self._x, self._y, self.on = (
            contour,
            float(x),
            float(y),
            bool(on),
        )

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


class Contour:
    def __init__(
        self, world: "World", points: Spec, closed: bool = True, tt: bool = False
    ) -> None:
        self.world, self.closed, self.isTT = (world, closed, tt)
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


class ShapeData:
    def __init__(self, base: str, refs: int) -> None:
        self.componentGlyph, self.referenceCount = (base, refs)


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
        self.world, self.id = (world, next(IDS))
        self.isComponent = base is not None
        self.shapeData = ShapeData(base or "", refs)
        self._transform = Transform(*matrix, dx, dy)
        self._contours = [
            c if isinstance(c, Contour) else Contour(world, c) for c in contours or []
        ]
        self.name, self.note = (f"shape-{self.id}", "keep me")

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

    def applyTransform(self) -> None:
        """Bake the shape transform into the nodes and reset it (FontLab rounds)."""
        if self.world.ignore_writes:
            return
        for contour in self._contours:
            for node in contour.nodes():
                x, y = self._transform.apply(node.x, node.y)
                node._x, node._y = (float(round(x)), float(round(y)))
        self._transform = Transform()
        self.world.events.append(("bake", self.name))

    def changed(self) -> None:
        pass


class Pin:
    def __init__(self, world: "World", name: str, x: float, y: float) -> None:
        self.world, self.name, self._point = (world, name, Point(x, y))

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
        self.world, self.glyph, self.master, self.name = (world, glyph, master, master)
        self.marker = f"{glyph}/{master}"
        self.advanceWidth, self.autoLayer = (advance, auto)
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
        self.world, self.name = (world, name)
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
        self.masters, self.master = (list(masters), masters[0])
        self.glyphs: dict[str, Glyph] = {}
        self.selected: list[str] = []
        self.events: list[Any] = []
        self.ignore_writes = self.fail_write = self.fail_notify = False
        self.round_writes = False
        self.no_font = False
        self.update_ok = True
        self.pending: list[int] = []
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
def native_world(monkeypatch: pytest.MonkeyPatch) -> World:
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


@pytest.mark.parametrize("title", TITLES)
def test_menu_file_exists(title: str) -> None:
    assert (ROOT / "Scripts" / "Contours" / f"{title}.py").is_file()


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(
        str(ROOT / "Scripts/Contours" / f"{title}.py"), run_name="inspection"
    )


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch, native_world: Any) -> Any:
    w = native_world
    monkeypatch.setattr(Shape, "contentLocked", False, raising=False)
    monkeypatch.setattr(Contour, "transform", Transform(), raising=False)
    monkeypatch.setattr(Node, "selected", False, raising=False)
    monkeypatch.setattr(Node, "smooth", False, raising=False)
    monkeypatch.setattr(Layer, "isLocked", False, raising=False)
    monkeypatch.setattr(Layer, "isNull", False, raising=False)

    def insert(contour: Any, index: int, nodes: list[Any]) -> None:
        if contour._guard():
            for node in nodes:
                node.contour = contour
            contour._nodes[index:index] = nodes

    def remove(contour: Any, index: int) -> None:
        if contour._guard():
            contour._nodes.pop(index)

    monkeypatch.setattr(Contour, "insert", insert, raising=False)
    monkeypatch.setattr(Contour, "removeAt", remove, raising=False)
    fontlab = sys.modules["fontlab"]
    echopy = ModuleType("echopy")
    echopy.__path__ = []
    echopy.fontlab = fontlab
    monkeypatch.setitem(sys.modules, "echopy", echopy)
    monkeypatch.setitem(sys.modules, "echopy.fontlab", fontlab)
    fontlab.flNode = lambda point, *, nodeType: Node(
        NS(world=w), point.x(), point.y(), nodeType == "on"
    )

    def contour(nodes: list[Any], *, closed: bool) -> Any:
        c = Contour(w, [], closed=closed)
        c._nodes = list(nodes)
        for n in nodes:
            n.contour = c
        return c

    fontlab.flContour = contour
    fontlab.flShape = lambda: Shape(w, [])
    monkeypatch.setattr(
        Shape, "addContours", lambda s, cs, flag: s._contours.extend(cs), raising=False
    )
    qt = sys.modules["PythonQt"]
    qt.QtGui.QMessageBox = NS(
        warning=lambda *args: w.events.append(("warning", str(args[-1])))
    )
    import fly.ap.layer_selection as selection

    def capture(deadline: float) -> Any:
        assert isinstance(deadline, float) and deadline > monotonic()
        w.captures.append(deadline)
        rows = [
            NS(glyph=w.glyphs[name], layer=w.glyphs[name].findLayer(w.master))
            for name in w.selected
        ]
        return NS(occurrences=rows)

    monkeypatch.setattr(selection, "capture", capture)
    w.captures = []
    yield w


def drawing(world: Any, title: str) -> Any:
    world.same("A", square(20, 10, 100))
    glyph = world.glyphs["A"]
    for layer in glyph.layers:
        layer.shapes[0].contours[0].nodes()[0].selected = True
    return glyph


def panel(title: str) -> Any:
    return load(title)["main"]()


@pytest.mark.parametrize("title", TITLES)
def test_real_fly_app_names(title: str) -> None:
    check_real_app_names(app_names_used([ROOT / "Scripts/Contours" / f"{title}.py"]))


@pytest.mark.parametrize("title", TITLES)
def test_panel_applies_one_shared_geometry_history_step(world: Any, title: str) -> None:
    glyph = drawing(world, title)
    ui = panel(title)
    ui.scope.setCurrentIndex(1)
    world.events.clear()
    ui.apply_button.clicked.emit()
    assert ui.last_result.get("layers") == 2, (title, ui.status.text)
    one_step(world, title, ["A/Light", "A/Bold"], ["A"])
    assert glyph.layers[0].shapes[0].note == "keep me"


@pytest.mark.parametrize("title", TITLES)
def test_panel_closes_and_replaces_without_live_slots(world: Any, title: str) -> None:
    drawing(world, title)
    ns = load(title)
    ui = ns["main"]()
    other = ns["main"]()
    assert other is not ui and ui.deleted
    signals = [signal for signal, _ in other._connections]
    other.close_button.clicked.emit()
    assert other.deleted and (not other._connections)
    assert all(not signal.slots for signal in signals)


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "failure", ["no_font", "pending", "auto", "locked", "switched"]
)
def test_refusals_do_not_open_history(world: Any, title: str, failure: str) -> None:
    glyph = drawing(world, title)
    if failure == "no_font":
        world.no_font = True
    if failure == "pending":
        world.pending = [4242]
    if failure == "auto":
        glyph.layers[0].autoLayer = True
    if failure == "locked":
        glyph.layers[0].isLocked = True
    ui = panel(title)
    if failure == "switched":
        world.package.id += 1
    world.events.clear()
    ui.apply_button.clicked.emit()
    assert not world.notifications(), (title, failure, ui.status.text)
    assert not any(event[0] == "init" for event in world.events)


@pytest.mark.parametrize("title", TITLES)
def test_partial_write_reports_undo(world: Any, title: str) -> None:
    drawing(world, title)
    ui = panel(title)
    world.fail_write = True
    ui.apply_button.clicked.emit()
    assert "Undo" in ui.status.text, ui.status.text


@pytest.mark.parametrize("title", TITLES)
def test_ignored_native_write_is_detected(world: Any, title: str) -> None:
    drawing(world, title)
    ui = panel(title)
    world.ignore_writes = True
    ui.apply_button.clicked.emit()
    assert "Error" in ui.status.text, ui.status.text


@pytest.mark.parametrize("title", TITLES)
def test_public_text_and_native_member_names(title: str) -> None:
    text = (ROOT / "Scripts/Contours" / f"{title}.py").read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert (
                not {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                & NATIVE_MEMBERS
            )
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.value, ast.Name)
            and (node.value.id == "self")
        ):
            assert node.attr not in NATIVE_MEMBERS
    doc = ast.get_docstring(tree)
    assert all(
        word not in doc.lower()
        for word in ("issue 122", "archived", "unresolved", "draft", "batch g4")
    )
    assert "Apache-2.0" in doc and "Reset Type Studio" in doc


def test_duplicate_selected_indices_and_handle_types(world: Any) -> None:
    glyph = drawing(world, "Node Duplicator")
    c = glyph.layers[0].shapes[0].contours[0]
    c.nodes()[2].selected = True
    ns = load("Node Duplicator")
    rows = ns["duplicate_changes"](glyph, glyph.layers[0], "Light", True)
    editor = ns["DuplicateEditor"]()
    prepared = editor.prepare(glyph.layers[0], [r.edit for r in rows])
    editor.write(glyph.layers[0], prepared)
    assert [(n.x, n.y, n.isOn()) for n in c.nodes()] == [
        (20, 10, True),
        (20, 10, False),
        (20, 10, False),
        (20, 10, True),
        (120, 10, True),
        (120, 110, True),
        (120, 110, False),
        (120, 110, False),
        (120, 110, True),
        (20, 110, True),
    ]
    assert editor.check([(glyph.layers[0], prepared)]) == []


def test_duplicate_mismatched_master_is_kept(world: Any) -> None:
    glyph = drawing(world, "Node Duplicator")
    glyph.layers[1].shapes[0].contours[0]._nodes.pop()
    rows = load("Node Duplicator")["duplicate_changes"](
        glyph, glyph.layers[1], "Light", False
    )
    assert rows and all(row.edit is None for row in rows)
    assert "masters differ" in rows[0].new


def test_duplicate_no_selection_has_no_edits(world: Any) -> None:
    glyph = drawing(world, "Node Duplicator")
    glyph.layers[0].shapes[0].contours[0].nodes()[0].selected = False
    rows = load("Node Duplicator")["duplicate_changes"](
        glyph, glyph.layers[0], "Light", False
    )
    assert not any(r.edit is not None for r in rows)


def test_smart_compensation_exact_matrix(world: Any) -> None:
    fn = load("Smart Slant")["compensated_matrix"]
    angle = math.degrees(math.atan(0.5))
    before, after = ((10.0, 0.0, 100.0, 300.0), (-40.0, 0.0, 250.0, 300.0))
    assert fn(angle, before, after, True) == pytest.approx((1, 0, 0.5, 1, 0, 0))
    assert fn(angle, before, after, False) == pytest.approx((1, 0, 0.5, 1, -75, 0))
    with pytest.raises(ValueError):
        fn(float("nan"), before, after, True)


def test_smart_rect_preserves_sidebearings_or_ink_centre(world: Any) -> None:
    glyph = drawing(world, "Smart Slant")
    ns = load("Smart Slant")
    layer = glyph.layers[0]
    old_width = layer.advanceWidth
    rows = ns["slant_plan"](layer, 45, True, False)
    advance = next(r.edit[1] for r in rows if r.edit[0] == "advance")
    assert advance == pytest.approx(old_width + 100)
    matrix = rows[0].edit[1][0][1]
    assert matrix == pytest.approx((1, 0, 1, 1, -10, 0))
    rows = ns["slant_plan"](layer, 45, False, False)
    assert rows[0].edit[1][0][1] == pytest.approx((1, 0, 1, 1, -60, 0))
    assert not any(r.edit[0] == "advance" for r in rows)


@pytest.mark.parametrize("title", TITLES)
def test_empty_selection_is_explained_without_history(world: Any, title: str) -> None:
    drawing(world, title)
    world.selected = []
    ui = panel(title)
    world.events.clear()
    ui.apply_button.clicked.emit()
    assert not world.notifications()
    assert "Select" in ui.subtitle.text or "Nothing" in ui.status.text


@pytest.mark.parametrize("title", TITLES)
def test_timeout_is_reported_by_main(
    world: Any, monkeypatch: pytest.MonkeyPatch, title: str
) -> None:
    namespace = load(title)

    def failure(*args: Any) -> None:
        raise TimeoutError("selection capture deadline")

    monkeypatch.setattr(namespace["scripting"], "show_script_dialog", failure)
    assert namespace["main"]() is None
    assert world.events[-1] == ("warning", "selection capture deadline")


@pytest.mark.parametrize("title", ["Node Duplicator"])
@pytest.mark.parametrize("flag", ["shared", "transform", "shape_locked", "quadratic"])
def test_unsafe_geometry_is_kept_or_refused_before_history(
    world: Any, title: str, flag: str
) -> None:
    glyph = drawing(world, title)
    for layer in glyph.layers:
        shape = layer.shapes[0]
        if flag == "shared":
            shape.shapeData.referenceCount = 2
        elif flag == "transform":
            shape._transform = Transform(2, 0, 0, 1, 0, 0)
        elif flag == "shape_locked":
            shape.contentLocked = True
        else:
            shape.contours[0].isTT = True
    ui = panel(title)
    world.events.clear()
    ui.apply_button.clicked.emit()
    assert not world.notifications(), ui.status.text


def test_duplicate_current_auxiliary_layer_and_per_glyph_reference(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    glyph = drawing(world, "Node Duplicator")
    aux = Layer(world, "A", "Sketch", 600, False)
    aux._shapes = [Shape(world, [square(10, 20, 40)])]
    aux.shapes[0].contours[0].nodes()[1].selected = True
    glyph.by_master["Sketch"] = aux
    namespace = load("Node Duplicator")

    def capture_aux(deadline: float) -> Any:
        assert isinstance(deadline, float) and deadline > monotonic()
        return NS(occurrences=[NS(glyph=glyph, layer=aux)])

    monkeypatch.setattr(namespace["layer_selection"], "capture", capture_aux)
    ui = namespace["main"]()
    ui.editor_layers.setChecked(True)
    assert not ui.scope.enabled and (not ui.compatible.enabled)
    assert not ui.compatible.isChecked()
    world.events.clear()
    ui.apply_button.clicked.emit()
    assert ui.last_result["layers"] == 1, ui.status.text
    assert len(aux.shapes[0].contours[0].nodes()) == 5
    assert len(glyph.layers[0].shapes[0].contours[0].nodes()) == 4
    one_step(world, "Node Duplicator", ["A/Sketch"], ["A"])


def test_duplicate_uses_each_glyph_own_indices(world: Any) -> None:
    first = drawing(world, "Node Duplicator")
    world.same("B", square(0, 0, 30))
    second = world.glyphs["B"]
    second.layers[0].shapes[0].contours[0].nodes()[2].selected = True
    ui = panel("Node Duplicator")
    ui.apply_button.clicked.emit()
    a = first.layers[1].shapes[0].contours[0].nodes()
    b = second.layers[1].shapes[0].contours[0].nodes()
    assert (a[0].x, a[0].y) == (a[1].x, a[1].y) == (20, 10)
    assert (b[2].x, b[2].y) == (b[3].x, b[3].y) == (30, 30)


def test_smart_anchor_origin_blocks_plan(world: Any) -> None:
    glyph = drawing(world, "Smart Slant")
    layer = glyph.layers[0]
    layer.anchors = [Pin(world, "bottom", 10, 0)]
    rows = load("Smart Slant")["slant_plan"](layer, 45, True, True)
    assert rows and all(row.edit is None for row in rows)
    assert "fl#8527" in rows[0].new


@pytest.mark.parametrize("title", TITLES)
def test_mixed_selection_keeps_invalid_glyph_and_writes_valid_glyph(
    world: Any, title: str
) -> None:
    drawing(world, title)
    bad = world.same("B", square(0, 0, 40))
    for layer in bad.layers:
        layer.isLocked = True
    ui = panel(title)
    ui.scope.setCurrentIndex(1)
    assert ui.apply_button.enabled, ui.status.text
    assert any("kept" in row[-1] for row in ui.table.row_texts()), ui.table.row_texts()
    world.events.clear()
    ui.apply_button.clicked.emit()
    assert ui.last_result["layers"] == 2, ui.status.text
    one_step(world, title, ["A/Light", "A/Bold"], ["A"])


@pytest.mark.parametrize("error_type", [ValueError, TimeoutError])
@pytest.mark.parametrize("action", ["refresh", "apply"])
def test_capture_failure_reaches_panel_status(
    world: Any,
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[Exception],
    action: str,
) -> None:
    drawing(world, "Node Duplicator")
    ns = load("Node Duplicator")
    ui = ns["main"]()

    def failure(deadline: float) -> Any:
        assert isinstance(deadline, float) and deadline > monotonic()
        raise error_type("capture cannot settle")

    monkeypatch.setattr(ns["layer_selection"], "capture", failure)
    world.events.clear()
    getattr(ui, action)()
    assert "capture cannot settle" in ui.status.text, ui.status.text
    assert not ui.apply_button.enabled
    assert not world.notifications()


def test_capture_is_once_per_plan_and_shared_between_scope_and_planner(
    world: Any,
) -> None:
    drawing(world, "Node Duplicator")
    ui = panel("Node Duplicator")
    ui.editor_layers.setChecked(True)
    world.captures.clear()
    ui.refresh()
    assert len(world.captures) == 1, world.captures
    world.captures.clear()
    ui.apply()
    assert len(world.captures) == 2, "one Apply plan, one post-write refresh plan"


@pytest.mark.parametrize("title", TITLES)
def test_menu_header_is_present(title: str) -> None:
    source = (ROOT / "Scripts/Contours" / f"{title}.py").read_text()
    assert source.splitlines()[2] == f"# FLM: Contours · {title}"


@pytest.mark.parametrize(
    "kind", ["component", "open", "contour_transform", "origin_anchor"]
)
def test_smart_content_note_does_not_disable_other_glyphs(
    world: Any, kind: str
) -> None:
    drawing(world, "Smart Slant")
    bad = world.same("B", square(20, 10, 100))
    for layer in bad.layers:
        shape = layer.shapes[0]
        if kind == "component":
            shape.isComponent = True
        elif kind == "open":
            shape.contours[0].closed = False
        elif kind == "contour_transform":
            shape.contours[0].transform = Transform(2, 0, 0, 1, 0, 0)
        else:
            layer.anchors = [Pin(world, "bottom", 10 * math.tan(math.radians(10)), 0)]
    ui = panel("Smart Slant")
    ui.scope.setCurrentIndex(1)
    assert ui.apply_button.enabled, ui.status.text
    assert any(
        row[0].startswith("B") and "kept" in row[-1] for row in ui.table.row_texts()
    )
    world.events.clear()
    ui.apply()
    one_step(world, "Smart Slant", ["A/Light", "A/Bold"], ["A"])


def test_duplicate_mismatch_holds_glyph_and_edits_other_glyph(world: Any) -> None:
    drawing(world, "Node Duplicator")
    bad = world.same("B", square(0, 0, 30))
    bad.layers[0].shapes[0].contours[0].nodes()[0].selected = True
    bad.layers[1].shapes[0].contours[0]._nodes.pop()
    ui = panel("Node Duplicator")
    assert ui.apply_button.enabled, ui.status.text
    assert "held" in ui.status.text, ui.status.text
    world.events.clear()
    ui.apply()
    one_step(world, "Node Duplicator", ["A/Light", "A/Bold"], ["A"])


def test_invalid_slant_control_blocks_the_action(world: Any) -> None:
    drawing(world, "Smart Slant")
    ui = panel("Smart Slant")
    ui.slant_degrees.setValue(float("nan"))
    world.events.clear()
    ui.apply()
    assert not world.notifications()
    assert not ui.apply_button.enabled
    assert "angle" in ui.status.text


def test_native_constructor_fakes_require_keyword_optional_arguments(
    world: Any,
) -> None:
    native = sys.modules["fontlab"]
    with pytest.raises(TypeError):
        native.flNode(Point(1, 2), "on")
    with pytest.raises(TypeError):
        native.flContour([], True)
