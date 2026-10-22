# this_file: tests/test_issue122_G15.py
# SPDX-License-Identifier: Apache-2.0
"""Alignment maths and real App history/panel wiring on owned native fakes."""

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
from unittest.mock import create_autospec

import pytest

try:
    from .conftest import app_names_used, check_real_app_names
except ImportError:
    from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "Scripts/Contours/Align And Distribute.py"
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
        self, world: "World", points: Spec, *, closed: bool = True, tt: bool = False
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
    for key in [
        k for k in sys.modules if k.split(".")[0] in ("fly", "fontlabapp", "echopy")
    ]:
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
    for key in [
        k for k in sys.modules if k.split(".")[0] in ("fly", "fontlabapp", "echopy")
    ]:
        del sys.modules[key]


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


@pytest.fixture
def world(native_world: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Keep real App modules; provide only native selection and drawing objects."""
    import fly.ap.layer_selection as selection

    def capture(deadline: float) -> Any:
        if native_world.no_font:
            return NS(occurrences=())
        return NS(
            occurrences=tuple(
                NS(
                    package=native_world.package,
                    glyph=native_world.glyphs[name],
                    layer=native_world.layer(name),
                )
                for name in native_world.selected
            )
        )

    replacement = create_autospec(selection.capture, side_effect=capture)
    assert inspect.signature(replacement) == inspect.signature(selection.capture)
    monkeypatch.setattr(selection, "capture", replacement)
    return native_world


def load() -> dict[str, Any]:
    """Load the menu without executing main."""
    return runpy.run_path(str(SCRIPT), run_name="inspection")


def write_rows(module: dict[str, Any], layer: Any, rows: list[Any]) -> None:
    """Exercise the same editor prepare/write contract as the App kernel."""
    editor = module["GeometryEditor"]()
    editor.write(
        layer, editor.prepare(layer, [r.edit for r in rows if r.edit is not None])
    )


def seed(world: Any, full: bool = False) -> list[Any]:
    """Install asymmetric coordinates and explicit native selection flags."""
    world.same("A", [(0, 0, 1), (20, 30, 1), (100, 90, 1), (80, 60, 1)])
    for glyph in world.glyphs.values():
        for layer in glyph.layers:
            layer.isLocked = layer.isMaskLayer = layer.isService = False
            for shape in layer.shapes:
                shape.selected = shape.contentLocked = False
                for contour in shape.contours:
                    contour.transform = Transform()
                    for index, node in enumerate(contour.nodes()):
                        node.selected = full or index < 3
                        node.smooth = False
    return world.layer("A").shapes[0].contours[0].nodes()


def test_real_app_names() -> None:
    check_real_app_names(app_names_used([SCRIPT]))


def test_public_contract() -> None:
    text = SCRIPT.read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    assert text.startswith("# this_file: Scripts/Contours/Align And Distribute.py\n")
    for word in (
        "What:",
        "How:",
        "Why:",
        "Use:",
        "Benefit:",
        "Apache-2.0",
        "mekkablue",
        "Contour > Align Points",
        "Element > Align / Distribute Shapes",
    ):
        assert word in ast.get_docstring(tree), word
    for word in ("archived", "unresolved", "draft", "issue 122", "Undo restores"):
        assert word not in text, word
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, node.name
        if isinstance(node, ast.ClassDef):
            members = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
            assigned = {
                n.attr
                for n in ast.walk(node)
                if isinstance(n, ast.Attribute)
                and isinstance(n.ctx, ast.Store)
                and isinstance(n.value, ast.Name)
                and n.value.id == "self"
            }
            assert not (members | assigned) & NATIVE_MEMBERS, (
                members | assigned
            ) & NATIVE_MEMBERS


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("left", [0, 0, 0]),
        ("right", [100, 100, 100]),
        ("horizontal", [50, 50, 50]),
        ("bottom", [0, 0, 0]),
        ("top", [90, 90, 90]),
        ("vertical", [45, 45, 45]),
        ("distribute_x", [0, 50, 100]),
        ("distribute_y", [0, 45, 90]),
    ],
)
def test_exact_node_results(world: Any, mode: str, expected: list[float]) -> None:
    nodes = seed(world)
    module = load()
    rows = module["plan_layer"](world.layer("A"), mode)
    write_rows(module, world.layer("A"), rows)
    axis = "x" if mode in ("left", "right", "horizontal", "distribute_x") else "y"
    assert [getattr(n, axis) for n in nodes[:3]] == expected, mode
    assert (nodes[3].x, nodes[3].y) == (80, 60), "unselected node stays"


@pytest.mark.parametrize("mode", range(8))
def test_panel_one_undo_and_cleanup(world: Any, mode: int) -> None:
    seed(world)
    panel = load()["main"]()
    panel.operation_box.setCurrentIndex(mode)
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert "Error" not in panel.status.text, panel.status.text
    one_step(world, "Align And Distribute", ["A/Light"], ["A"])
    assert not any(e[0] == "update-all" for e in world.events)
    panel.close_button.clicked.emit()
    assert panel.deleted


def test_batch_all_masters_and_live_replan(world: Any) -> None:
    nodes = seed(world)
    panel = load()["main"]()
    panel.scope.setCurrentIndex(1)
    nodes[0].selected = False
    press(panel)
    assert nodes[1].x == nodes[2].x == 20, "Apply uses the live selection"
    assert nodes[0].x == 0
    one_step(world, "Align And Distribute", ["A/Light", "A/Bold"], ["A"])


def test_complete_contours_translate_as_units(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    second = Contour(world, [(200, 10, 1), (240, 20, 1), (250, 40, 1)])
    second.transform = Transform()
    layer.shapes[0]._contours.append(second)
    for contour in layer.shapes[0].contours:
        for node in contour.nodes():
            node.selected = True
    module = load()
    rows = module["plan_layer"](layer, "right")
    write_rows(module, layer, rows)
    first = layer.shapes[0].contours[0].nodes()
    assert [(n.x, n.y) for n in first] == [(150, 0), (170, 30), (250, 90), (230, 60)]
    assert [n.x for n in second.nodes()] == [200, 240, 250]


def test_transformed_nodes_use_visible_coordinates(world: Any) -> None:
    nodes = seed(world)
    shape = world.layer("A").shapes[0]
    shape.transform = Transform(2, 0, 0, 3, 10, 50)
    module = load()
    rows = module["plan_layer"](world.layer("A"), "right", coordinate=250)
    write_rows(module, world.layer("A"), rows)
    assert [n.x for n in nodes[:3]] == [120, 120, 120]


@pytest.mark.parametrize(
    "fault",
    [
        "no font",
        "no glyph",
        "no nodes",
        "locked",
        "shared",
        "auto",
        "base",
        "pending",
        "contour matrix",
        "singular",
        "nan",
    ],
)
def test_refusal_creates_no_history(world: Any, fault: str) -> None:
    nodes = seed(world)
    layer = world.layer("A")
    if fault == "no font":
        world.no_font = True
    elif fault == "no glyph":
        world.selected.clear()
    elif fault == "no nodes":
        for node in nodes:
            node.selected = False
    elif fault == "locked":
        layer.isLocked = True
    elif fault == "shared":
        layer.shapes[0].shapeData.referenceCount = 2
    elif fault == "auto":
        layer.autoLayer = True
    elif fault == "base":
        world.glyph(
            "Aacute",
            {"Light": [Shape(world, base="A")]},
            auto=("Light",),
            select=False,
        )
    elif fault == "pending":
        world.pending.append(123)
    elif fault == "contour matrix":
        layer.shapes[0].contours[0].transform = Transform(dx=10)
    elif fault == "singular":
        layer.shapes[0].transform = Transform(0, 0, 0, 0)
    else:
        nodes[0]._x = math.nan
    panel = load()["main"]()
    if fault == "pending":
        before = tuple(world.pending)
        assert panel.apply_button.enabled
        press(panel)
        assert world.history() and tuple(world.pending) == before
        assert panel.last_result["pending_updates"] == before and "8537" in panel.status.text and panel.last_result["pending_note"] in panel.status.text
        return
    assert not panel.apply_button.enabled, (fault, panel.status.text)
    press(panel)
    assert not world.history(), (fault, world.history())


@pytest.mark.parametrize("fault", ["fail_write", "ignore_writes", "fail_notify"])
def test_partial_failure_names_undo(world: Any, fault: str) -> None:
    seed(world)
    panel = load()["main"]()
    setattr(world, fault, True)
    press(panel)
    assert "use Edit > Undo" in panel.status.text, panel.status.text


def test_timeout_is_contained(world: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    seed(world)
    module = load()
    panel = module["main"]()

    def fail(deadline: float) -> Any:
        raise TimeoutError("selection took too long")

    monkeypatch.setattr(module["layer_selection"], "capture", fail)
    panel.reload()
    assert not panel.apply_button.enabled
    assert "selection took too long" in panel.status.text
    assert not world.history()


def test_distribution_requires_three_nodes_and_keeps_endpoints(world: Any) -> None:
    nodes = seed(world)
    module = load()
    nodes[2].selected = False
    rows = module["plan_layer"](world.layer("A"), "distribute_x")
    assert not any(r.edit for r in rows) and "three" in str(rows)
    nodes[2].selected = True
    rows = module["plan_layer"](world.layer("A"), "distribute_x")
    write_rows(module, world.layer("A"), rows)
    assert [n.x for n in nodes[:3]] == [0, 50, 100]


def test_noop_and_bad_operation(world: Any) -> None:
    seed(world)
    module = load()
    with pytest.raises(ValueError):
        module["plan_layer"](world.layer("A"), "invalid")
    with pytest.raises(ValueError):
        module["plan_layer"](world.layer("A"), "left", coordinate=math.inf)
    for n in world.layer("A").shapes[0].contours[0].nodes():
        n._x = 0
    assert not module["plan_layer"](world.layer("A"), "left")


def test_component_alignment_composes_without_editing_base(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    component = Shape(world, base="base", dx=40, dy=20, matrix=(2, 0, 0, 3))
    component.selected, component.contentLocked = True, False
    component.boundingBox = Rect(10, 0, 20, 30)
    layer._shapes.append(component)
    panel = load()["main"]()
    panel.operation_box.setCurrentIndex(1)
    # Component right edge already equals 100; move all items to explicit 150.
    panel.reference_box.setCurrentIndex(1)
    panel.target_value.setValue(150)
    press(panel)
    assert component.transform.values == (2, 0, 0, 3, 90, 20)
    assert component.shapeData.componentGlyph == "base"
    one_step(world, "Align And Distribute", ["A/Light"], ["A"])


def test_anchors_outside_bounds_and_duplicate_names_are_ignored(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    layer.anchors = [Pin(world, "top", 0, 700), Pin(world, "top", 100, 900)]
    panel = load()["main"]()
    assert not hasattr(panel, "anchor_tick"), "Anchor alignment was removed"
    panel.operation_box.setCurrentIndex(4)
    assert not any("anchor" in str(row) for row in panel.table.row_texts()), (
        panel.table.row_texts()
    )
    press(panel)
    assert [n.y for n in layer.shapes[0].contours[0].nodes()][:3] == [90, 90, 90]
    assert [(p.point.x(), p.point.y()) for p in layer.anchors] == [(0, 700), (100, 900)]


def test_selected_nodes_distribute_across_two_glyphs_and_masters(world: Any) -> None:
    seed(world)
    world.same("B", [(10, 10, 1), (20, 50, 1), (100, 100, 1), (40, 80, 1)])
    for glyph in world.glyphs.values():
        for layer in glyph.layers:
            layer.isLocked = layer.isMaskLayer = layer.isService = False
            for shape in layer.shapes:
                shape.contentLocked = shape.selected = False
                for contour in shape.contours:
                    contour.transform = Transform()
                    for n in contour.nodes():
                        n.selected = True
    panel = load()["main"]()
    panel.operation_box.setCurrentIndex(6)
    panel.scope.setCurrentIndex(1)
    press(panel)
    assert "Error" not in panel.status.text, panel.status.text
    assert sorted(
        n.x for n in world.layer("A").shapes[0].contours[0].nodes()
    ) == pytest.approx([0, 100 / 3, 200 / 3, 100])
    assert sorted(
        n.x for n in world.layer("B", "Bold").shapes[0].contours[0].nodes()
    ) == pytest.approx([10, 40, 70, 100])
    one_step(
        world,
        "Align And Distribute",
        ["A/Light", "A/Bold", "B/Light", "B/Bold"],
        ["A", "B"],
    )


def test_equal_coordinate_ties_keep_stable_node_order(world: Any) -> None:
    nodes = seed(world)
    nodes[1]._x = 0
    module = load()
    rows = module["plan_layer"](world.layer("A"), "distribute_x")
    write_rows(module, world.layer("A"), rows)
    assert [n.x for n in nodes[:3]] == [0, 50, 100]


def test_font_switch_and_cross_font_capture_refuse(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world)
    module = load()
    panel = module["main"]()
    world.package.id = 99
    press(panel)
    assert "Error" in panel.status.text
    assert not world.history()
    world.package.id = 7
    monkeypatch.setattr(
        module["layer_selection"],
        "capture",
        lambda deadline: NS(
            occurrences=(
                NS(package=NS(id=99), glyph=world.glyphs["A"], layer=world.layer("A")),
            )
        ),
    )
    panel.reload()
    assert "another font" in panel.status.text
    assert not panel.apply_button.enabled


def test_grid_rounding_is_checked_with_half_unit_tolerance(world: Any) -> None:
    seed(world)
    world.round_writes = True
    panel = load()["main"]()
    panel.operation_box.setCurrentIndex(6)
    for node in world.layer("A").shapes[0].contours[0].nodes():
        node.selected = True
    press(panel)
    assert "Error" not in panel.status.text, panel.status.text
    assert sorted(n.x for n in world.layer("A").shapes[0].contours[0].nodes()) == [
        0,
        33,
        67,
        100,
    ]


def test_component_readback_failure_names_undo(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    component = Shape(world, base="base", dx=10)
    component.selected, component.contentLocked = True, False
    component.boundingBox = Rect(0, 0, 10, 10)
    layer._shapes = [component]
    panel = load()["main"]()
    panel.reference_box.setCurrentIndex(1)
    panel.target_value.setValue(70)
    world.ignore_writes = True
    press(panel)
    assert "Light" in panel.status.text, panel.status.text
    assert "use Edit > Undo" in panel.status.text, panel.status.text


@pytest.mark.parametrize("flag", ["isMaskLayer", "isService"])
def test_mask_and_service_layers_refuse(world: Any, flag: str) -> None:
    seed(world)
    setattr(world.layer("A"), flag, True)
    panel = load()["main"]()
    assert not panel.apply_button.enabled
    press(panel)
    assert not world.history()


def test_negative_coordinates_and_empty_outline(world: Any) -> None:
    nodes = seed(world)
    for node in nodes:
        node._x -= 100
    module = load()
    rows = module["plan_layer"](world.layer("A"), "distribute_x")
    write_rows(module, world.layer("A"), rows)
    assert [n.x for n in nodes[:3]] == [-100, -50, 0]
    world.layer("A")._shapes.clear()
    assert not module["plan_layer"](world.layer("A"), "right")


@pytest.mark.parametrize("smooth", [False, True])
@pytest.mark.parametrize("mode,delta", [("left", (-30, 0)), ("top", (0, 80))])
def test_oncurve_own_handles_follow_exactly(
    world: Any, smooth: bool, mode: str, delta: tuple[float, float]
) -> None:
    seed(world)
    layer = world.layer("A")
    contour = Contour(
        world, [(0, 0, 1), (20, 10, 0), (40, 30, 1), (60, 50, 0), (100, 100, 1)]
    )
    contour.transform = Transform()
    layer.shapes[0]._contours = [contour]
    nodes = contour.nodes()
    for index, node in enumerate(nodes):
        node.selected = index == 2
        node.smooth = smooth if index == 2 else False
    before = [(n.x, n.y) for n in nodes]
    module = load()
    coordinate = 10 if mode == "left" else 110
    rows = module["plan_layer"](layer, mode, coordinate=coordinate)
    write_rows(module, layer, rows)
    for index in (1, 2, 3):
        assert (nodes[index].x, nodes[index].y) == (
            before[index][0] + delta[0],
            before[index][1] + delta[1],
        ), "Own handles must retain their node offsets"
    a = (nodes[1].x - nodes[2].x, nodes[1].y - nodes[2].y)
    b = (nodes[3].x - nodes[2].x, nodes[3].y - nodes[2].y)
    assert abs(a[0] * b[1] - a[1] * b[0]) <= 1e-6, "Smooth tangency is retained"
    assert nodes[2].smooth == smooth


def test_all_nodes_distribution_is_disabled_with_status(world: Any) -> None:
    seed(world)
    panel = load()["main"]()
    panel.node_scope.setCurrentIndex(1)
    panel.operation_box.setCurrentIndex(6)
    assert not panel.apply_button.enabled
    assert "selected nodes" in panel.status.text
    press(panel)
    assert not world.history()


@pytest.mark.parametrize("fault", ["layer", "shape", "shared", "contour"])
def test_kept_item_does_not_block_other_master(world: Any, fault: str) -> None:
    seed(world)
    layer = world.layer("A")
    if fault == "layer":
        layer.isLocked = True
    elif fault == "shape":
        layer.shapes[0].contentLocked = True
    elif fault == "shared":
        layer.shapes[0].shapeData.referenceCount = 2
    else:
        layer.shapes[0].contours[0].transform = Transform(dx=10)
    panel = load()["main"]()
    panel.scope.setCurrentIndex(1)
    assert panel.apply_button.enabled, panel.status.text
    assert any(
        "kept" in str(row) and "A · Light" in str(row)
        for row in panel.table.row_texts()
    )
    press(panel)
    one_step(world, "Align And Distribute", ["A/Bold"], ["A"])


def test_capture_once_per_scan_and_not_on_controls(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world)
    module = load()
    calls = []
    original = module["layer_selection"].capture

    def capture(deadline: float) -> Any:
        calls.append(deadline)
        return original(deadline)

    monkeypatch.setattr(module["layer_selection"], "capture", capture)
    panel = module["main"]()
    assert len(calls) == 1
    panel.target_value.setValue(30)
    panel.operation_box.setCurrentIndex(1)
    assert len(calls) == 1
    panel.reload()
    assert len(calls) == 2
    press(panel)
    assert len(calls) == 3


def test_native_constructor_optional_arguments_are_keyword_only(world: Any) -> None:
    with pytest.raises(TypeError):
        Contour(world, [(0, 0, 1)], False)
    contour = Contour(world, [(0, 0, 1)], closed=False)
    assert not contour.closed


def test_locked_shape_kept_but_other_shape_same_layer_writes(world: Any) -> None:
    nodes = seed(world)
    layer = world.layer("A")
    layer.shapes[0].contentLocked = True
    other = Shape(world, [[(200, 10, 1), (240, 50, 1), (300, 100, 1)]])
    other.contentLocked = other.selected = False
    for contour in other.contours:
        contour.transform = Transform()
        for index, node in enumerate(contour.nodes()):
            node.selected = index < 2
    layer._shapes.append(other)
    panel = load()["main"]()
    assert panel.apply_button.enabled
    press(panel)
    assert [n.x for n in nodes] == [0, 20, 100, 80]
    assert [n.x for n in other.contours[0].nodes()] == [200, 200, 300]
    one_step(world, "Align And Distribute", ["A/Light"], ["A"])


def test_unselected_locked_master_emits_no_kept_row(world: Any) -> None:
    seed(world)
    layer = world.layer("A", "Bold")
    layer.isLocked = True
    for node in layer.shapes[0].contours[0].nodes():
        node.selected = False
    panel = load()["main"]()
    panel.scope.setCurrentIndex(1)
    assert not any("Bold" in str(row) for row in panel.table.row_texts())
    press(panel)
    one_step(world, "Align And Distribute", ["A/Light"], ["A"])


def test_auxiliary_editor_layer_and_live_layer_change(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world)
    glyph = world.glyphs["A"]
    auxiliary = Layer(world, "A", "Light@ sketch", 600, False)
    auxiliary.isLocked = auxiliary.isMaskLayer = auxiliary.isService = False
    auxiliary._shapes = [Shape(world, [[(0, 10, 1), (20, 50, 1), (100, 90, 1)]])]
    for shape in auxiliary.shapes:
        shape.contentLocked = shape.selected = False
        for contour in shape.contours:
            contour.transform = Transform()
            for index, node in enumerate(contour.nodes()):
                node.selected = index < 2
    glyph.by_master[auxiliary.name] = auxiliary
    module = load()
    active = [world.layer("A")]
    monkeypatch.setattr(
        module["layer_selection"],
        "capture",
        lambda deadline: NS(
            occurrences=(NS(package=world.package, glyph=glyph, layer=active[0]),)
        ),
    )
    panel = module["main"]()
    active[0] = auxiliary
    press(panel)
    assert [n.x for n in auxiliary.shapes[0].contours[0].nodes()] == [0, 0, 100]
    one_step(world, "Align And Distribute", ["A/Light@ sketch"], ["A"])


def test_rotated_component_uses_transformed_local_bounds(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    component = Shape(world, base="base", dx=40, dy=20, matrix=(0, 1, -1, 0))
    component.selected, component.contentLocked = True, False
    component.boundingBox = Rect(10, 0, 20, 30)
    layer._shapes = [component]
    panel = load()["main"]()
    panel.operation_box.setCurrentIndex(1)
    panel.reference_box.setCurrentIndex(1)
    panel.target_value.setValue(150)
    press(panel)
    assert component.transform.values == (0, 1, -1, 0, 150, 20)
    assert component.shapeData.componentGlyph == "base"


def test_explicitly_selected_handle_has_only_its_own_move(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    contour = Contour(
        world, [(0, 0, 1), (20, 10, 0), (40, 30, 1), (60, 50, 0), (100, 100, 1)]
    )
    contour.transform = Transform()
    layer.shapes[0]._contours = [contour]
    nodes = contour.nodes()
    for index, node in enumerate(nodes):
        node.selected = index in (1, 2)
    module = load()
    rows = module["plan_layer"](layer, "left", coordinate=10)
    write_rows(module, layer, rows)
    assert [(n.x, n.y) for n in nodes] == [
        (0, 0),
        (10, 10),
        (10, 30),
        (30, 50),
        (100, 100),
    ]


def test_editor_check_returns_all_layer_labelled_misses(world: Any) -> None:
    seed(world)
    module = load()
    editor = module["GeometryEditor"]()
    prepared = []
    for master in ("Light", "Bold"):
        layer = world.layer("A", master)
        rows = module["plan_layer"](layer, "left")
        prepared.append(
            (layer, editor.prepare(layer, [row.edit for row in rows if row.edit]))
        )
    misses = editor.check(prepared)
    assert any("Light" in text for text in misses), misses
    assert any("Bold" in text for text in misses), misses


def test_empty_selection_hint_names_glyph_window(world: Any) -> None:
    seed(world)
    world.selected.clear()
    panel = load()["main"]()
    assert "Glyph window" in panel.subtitle.text
    assert "Font window" not in panel.subtitle.text


@pytest.mark.parametrize("closed", [False, True])
def test_handle_following_wraps_only_closed_contours(world: Any, closed: bool) -> None:
    seed(world)
    layer = world.layer("A")
    contour = Contour(
        world,
        [(0, 0, 1), (10, 10, 0), (100, 100, 1), (90, 90, 0), (-10, -10, 0)],
        closed=closed,
    )
    contour.transform = Transform()
    layer.shapes[0]._contours = [contour]
    for index, node in enumerate(contour.nodes()):
        node.selected = index == 0
    module = load()
    rows = module["plan_layer"](layer, "top", coordinate=50)
    write_rows(module, layer, rows)
    nodes = contour.nodes()
    assert (nodes[1].x, nodes[1].y) == (10, 60)
    assert (nodes[-1].x, nodes[-1].y) == (-10, 40 if closed else -10)


def test_scaled_curve_keeps_handle_vectors_in_glyph_space(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    contour = Contour(
        world, [(0, 0, 1), (20, 10, 0), (40, 30, 1), (60, 50, 0), (100, 100, 1)]
    )
    contour.transform = Transform()
    shape = layer.shapes[0]
    shape._contours = [contour]
    shape.transform = Transform(0, 2, -3, 0, 10, 50)
    for index, node in enumerate(contour.nodes()):
        node.selected = index == 2
    before = [shape.transform.apply(n.x, n.y) for n in contour.nodes()]
    module = load()
    rows = module["plan_layer"](layer, "top", coordinate=180)
    write_rows(module, layer, rows)
    after = [shape.transform.apply(n.x, n.y) for n in contour.nodes()]
    for index in (1, 2, 3):
        assert after[index] == pytest.approx(
            (before[index][0], before[index][1] + 50)
        ), "Same glyph-space offset for the node and both handles"


def test_mixed_editor_layers_do_not_form_cross_product(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world)
    world.same("B", [(0, 0, 1), (20, 30, 1), (100, 90, 1), (80, 60, 1)])
    for layer in world.glyphs["B"].layers:
        layer.isLocked = layer.isMaskLayer = layer.isService = False
        for shape in layer.shapes:
            shape.selected = shape.contentLocked = False
            for contour in shape.contours:
                contour.transform = Transform()
                for index, node in enumerate(contour.nodes()):
                    node.selected = index < 3
    module = load()
    monkeypatch.setattr(
        module["layer_selection"],
        "capture",
        lambda deadline: NS(
            occurrences=tuple(
                NS(
                    package=world.package,
                    glyph=world.glyphs[name],
                    layer=world.layer(name, master),
                )
                for name, master in (("A", "Light"), ("B", "Bold"))
            )
        ),
    )
    panel = module["main"]()
    press(panel)
    one_step(world, "Align And Distribute", ["A/Light", "B/Bold"], ["A", "B"])
    assert [n.x for n in world.layer("A", "Bold").shapes[0].contours[0].nodes()] == [
        0,
        20,
        100,
        80,
    ]
    assert [n.x for n in world.layer("B", "Light").shapes[0].contours[0].nodes()] == [
        0,
        20,
        100,
        80,
    ]


def test_two_node_closed_contour_has_one_handle_owner(world: Any) -> None:
    seed(world)
    layer = world.layer("A")
    contour = Contour(world, [(0, 0, 1), (10, 10, 0)])
    contour.transform = Transform()
    layer.shapes[0]._contours = [contour]
    for index, node in enumerate(contour.nodes()):
        node.selected = index == 0
    module = load()
    rows = module["plan_layer"](layer, "left", coordinate=30)
    assert not any("kept" in row.new for row in rows), rows
    assert len(rows[0].edit[0]) == 2, (
        "One node and one handle, without duplicate writes"
    )
    write_rows(module, layer, rows)
    assert [(n.x, n.y) for n in contour.nodes()] == [(30, 0), (40, 10)]


@pytest.mark.parametrize("scope", ["layer", "group"])
def test_position_error_keeps_named_item_and_allows_other_edits(
    world: Any, monkeypatch: pytest.MonkeyPatch, scope: str
) -> None:
    seed(world)
    module = load()
    original = module["position"]

    def position(
        points: list[tuple[float, float]], axis: int, fraction: float
    ) -> float:
        if scope == "layer" and len(points) > 1 and points[0][0] == 0:
            raise ValueError("non-finite position result")
        if scope == "group" and len(points) == 1 and points[0][0] == 20:
            raise ValueError("non-finite position result")
        return original(points, axis, fraction)

    monkeypatch.setitem(module["plan_layer"].__globals__, "position", position)
    if scope == "layer":
        for node in world.layer("A", "Bold").shapes[0].contours[0].nodes():
            node._x += 10
    panel = module["main"]()
    panel.scope.setCurrentIndex(1)
    assert panel.apply_button.enabled, panel.status.text
    assert any(
        "A · Light" in str(row)
        and "non-finite position" in str(row)
        and "kept" in str(row)
        for row in panel.table.row_texts()
    ), panel.table.row_texts()
    press(panel)
    layers = ["A/Bold"] if scope == "layer" else ["A/Light", "A/Bold"]
    one_step(world, "Align And Distribute", layers, ["A"])


def test_scripts_use_only_public_app_names() -> None:
    """Forbid private module imports and attributes through every App alias."""
    used = app_names_used([SCRIPT])
    assert all(
        not part.startswith("_") for module in used for part in module.split(".")
    ), used
    assert all(not name.startswith("_") for names in used.values() for name in names), used


def test_panel_overrides_match_installed_public_hooks(world: Any) -> None:
    """Compare subclass calls with the installed base, using only native fakes."""
    import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
    import fly.ap.outline_panel as outline_panel  # noqa: PLR0402

    with pytest.raises(TypeError):
        layer_selection.capture()
    panel = load()["GeometryPanel"]
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
    for node in ast.walk(ast.parse((SCRIPT).read_text())):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            assert not (node.value.id == "self" and node.attr.startswith("_")), node.attr


def test_explicit_fly_app_paths_have_no_private_names() -> None:
    """Also catch full fly.ap.module._member paths without import aliases."""
    for path in [SCRIPT]:
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
