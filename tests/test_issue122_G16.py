# this_file: tests/test_issue122_G16.py
# SPDX-License-Identifier: Apache-2.0
"""Selected geometry rewrites with real App helpers and self-contained native fakes."""

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
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
FOLDER = ROOT / "Scripts/Contours"
NAMES = (
    "Rotate Selection",
    "Reflect Horizontally",
    "Reflect Vertically",
    "Overlap Nodes",
)


def load(title: str) -> dict[str, Any]:
    """Load one menu without running main."""
    return runpy.run_path(str(FOLDER / f"{title}.py"), run_name="inspection")


ISOLATED = ("fly", "fontlabapp", "echopy")  # packages this file re-imports for itself


NATIVE_MEMBERS = {
    "metric", "update", "layout", "font", "palette", "parent", "style", "size",
    "pos", "width", "height", "geometry", "show", "hide", "open", "done", "accept",
    "reject", "exec", "repaint", "move", "resize", "rect", "title", "name",
    "windowTitle", "objectName", "children", "focus", "enabled", "visible",
    "actions", "cursor", "locale", "mask", "scroll", "find", "close", "render",
    "statusBar", "grab", "lower", "raise_", "x", "y", "frameGeometry",
}  # fmt: skip


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
    registry: ClassVar[list[Any]] = []

    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.text = text
        self.registry.append(self)


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


def make_qt() -> ModuleType:
    qt = ModuleType("PythonQt")
    core = NS(
        QPointF=Point,
        QDateTime=NS(currentDateTimeUtc=lambda: "UTC stamp"),
        Qt=NS(AlignRight=2, ScrollBarAlwaysOff=3, DashLine=4, NoPen=0),
    )
    gui = NS(
        QDialog=Dialog,
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
        QAbstractItemView=NS(NoEditTriggers=0, NoSelection=0),
        QHeaderView=NS(Stretch=0, ResizeToContents=1),
    )
    qt.QtCore, qt.QtGui = core, gui
    return qt


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

    def changed(self) -> None:
        pass


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
        self.package = Package(self)

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
    Button.registry.clear()
    yield w
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
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


class Package:
    """Native current-master angle property with explicit master switches."""

    def __init__(self, owner: "World") -> None:
        self.owner, self.id, self.isNull = owner, 7, False
        self.masters, self.master = owner.masters, owner.master
        self.angles = {name: -12.0 for name in self.masters}
        self.switches: list[str] = []

    @property
    def italicAngle_value(self) -> float:
        return self.angles[self.master]

    @italicAngle_value.setter
    def italicAngle_value(self, angle: float) -> None:
        self.angles[self.master] = float(angle)

    def setMaster(self, name: str) -> None:
        assert name in self.masters, "Switch only to a declared master"
        self.switches.append(name)
        self.master = name

    def findName(self, name: str) -> Any:
        return self.owner.glyphs.get(name)


@pytest.fixture
def world(native_world: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Install selected-layer capture over the local native fakes."""
    import fly.ap.layer_selection as selection

    def capture(deadline: float) -> Any:
        rows = [
            NS(
                package=native_world.package,
                glyph=glyph,
                layer=glyph.findLayer(native_world.package.master),
            )
            for name, glyph in native_world.glyphs.items()
            if name in native_world.selected
        ]
        return NS(occurrences=tuple(rows))

    replacement = create_autospec(selection.capture, side_effect=capture)
    assert inspect.signature(replacement) == inspect.signature(selection.capture)
    monkeypatch.setattr(selection, "capture", replacement)
    return native_world


def seed(world: Any, title: str) -> list[Any]:
    """Install an eligible, asymmetric fixture for a menu."""
    if title == "Overlap Nodes":
        points = [(20, 30, 1), (40, 10, 1), (50, 50, 0), (80, 60, 0), (100, 20, 1)]
        chosen = {0}
    else:
        points = [(0, 0, 1), (100, 0, 1), (100, 50, 1), (0, 50, 1)]
        chosen = {0, 1, 2}
    world.same("A", points)
    for glyph in world.glyphs.values():
        for layer in glyph.layers:
            layer.isLocked = False
            for shape in layer.shapes:
                shape.selected = shape.contentLocked = False
                for contour in shape.contours:
                    contour.transform = Transform()
                    for index, node in enumerate(contour.nodes()):
                        node.selected = layer.name == "Light" and index in chosen
                        node.smooth = True
    return world.layer("A").shapes[0].contours[0].nodes()


@pytest.mark.parametrize("title", NAMES)
def test_public_contract(title: str) -> None:
    source = (FOLDER / f"{title}.py").read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    assert source.startswith(f"# this_file: Scripts/Contours/{title}.py\n")
    doc = ast.get_docstring(tree)
    assert "Glyph · layer" in source, "column heading includes auxiliary layers"
    assert "Bake contour-level transforms" not in source
    if title != "Overlap Nodes":
        assert "What:" not in doc, "summary already describes the action"
        assert (
            "native Rotate" in doc
            if title == "Rotate Selection"
            else "Tools > Flip" in doc
        )
        assert "Each action is recorded as one Undo step." in doc
    for term in (
        "How:",
        "Why:",
        "Use:",
        "Benefit:",
        "Source:",
        "Apache-2.0",
        "slobzheninov/Glyphs-Scripts",
    ):
        assert term in doc, (title, term)
    for term in (
        "archived",
        "unresolved",
        "draft",
        "issue 122",
        "native acceptance",
        "Undo restores",
    ):
        assert term not in source, (title, term)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, (title, node.name)
        if isinstance(node, ast.ClassDef):
            names = {x.name for x in node.body if isinstance(x, ast.FunctionDef)}
            assert not names & NATIVE_MEMBERS, (title, names & NATIVE_MEMBERS)


def test_real_app_import_names() -> None:
    check_real_app_names(app_names_used([FOLDER / f"{name}.py" for name in NAMES]))


@pytest.mark.parametrize("title", NAMES)
def test_panel_action_and_one_history_step(world: Any, title: str) -> None:
    nodes = seed(world, title)
    before = [(n.x, n.y, n.smooth) for n in nodes]
    panel = load(title)["main"]()
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert "Error" not in panel.status.text, panel.status.text
    assert [(n.x, n.y, n.smooth) for n in nodes] != before, "real node edit"
    one_step(world, title, ["A/Light"], ["A"])
    assert not any(x[0] == "update-all" for x in world.events)
    panel.close_button.clicked.emit()
    assert panel.deleted, "panel closes and releases signals"


@pytest.mark.parametrize("title", NAMES)
@pytest.mark.parametrize(
    "fault",
    ("no font", "no glyph", "no nodes", "auto", "pending", "locked", "shared", "base"),
)
def test_refusals_write_nothing(world: Any, title: str, fault: str) -> None:
    nodes = seed(world, title)
    layer = world.layer("A")
    if fault == "no font":
        world.no_font = True
    elif fault == "no glyph":
        world.selected.clear()
    elif fault == "no nodes":
        for node in nodes:
            node.selected = False
    elif fault == "auto":
        layer.autoLayer = True
    elif fault == "pending":
        world.pending.append(42)
    elif fault == "locked":
        layer.isLocked = True
    elif fault == "shared":
        layer.shapes[0].shapeData.referenceCount = 2
    else:
        world.glyph(
            "Aacute", {"Light": [Shape(world, base="A")]}, auto=("Light",), select=False
        )
    panel = load(title)["main"]()
    if fault == "pending":
        before = tuple(world.pending)
        assert panel.apply_button.enabled
        press(panel)
        assert world.history() and tuple(world.pending) == before
        assert panel.last_result["pending_updates"] == before and "8537" in panel.status.text and panel.last_result["pending_note"] in panel.status.text
        return
    assert not panel.apply_button.enabled, (title, fault, panel.status.text)
    press(panel)
    assert not world.history(), (title, fault, world.history())


@pytest.mark.parametrize("title", NAMES)
def test_partial_native_failure_has_undo_hint(world: Any, title: str) -> None:
    seed(world, title)
    panel = load(title)["main"]()
    world.fail_write = True
    press(panel)
    assert "Native changes may remain; use Edit > Undo" in panel.status.text
    assert len(world.notifications()) == 1


@pytest.mark.parametrize("title", NAMES)
def test_readback_failure_has_undo_hint(world: Any, title: str) -> None:
    seed(world, title)
    panel = load(title)["main"]()
    world.ignore_writes = True
    press(panel)
    assert "use Edit > Undo" in panel.status.text


@pytest.mark.parametrize("title", NAMES)
def test_live_node_selection_is_replanned(world: Any, title: str) -> None:
    nodes = seed(world, title)
    panel = load(title)["main"]()
    for node in nodes:
        node.selected = False
    press(panel)
    assert not world.history(), "no write from an old selection preview"


@pytest.mark.parametrize("title", NAMES[:3])
def test_transform_exact_coordinates(world: Any, title: str) -> None:
    nodes = seed(world, title)
    panel = load(title)["main"]()
    if title == "Rotate Selection":
        panel.degrees.setValue(90)
        want = [(75, -25), (75, 75), (25, 75)]
    elif title == "Reflect Horizontally":
        want = [(100, 0), (0, 0), (0, 50)]
    else:
        want = [(0, 50), (100, 50), (100, 0)]
    press(panel)
    for node, expected in zip(nodes[:3], want, strict=True):
        assert (node.x, node.y) == pytest.approx(expected)
    assert (nodes[3].x, nodes[3].y) == (0, 50), "unselected stays"


def test_overlap_exact_italic_handle_and_corner(world: Any) -> None:
    nodes = seed(world, "Overlap Nodes")
    panel = load("Overlap Nodes")["main"]()
    press(panel)
    assert (nodes[1].x, nodes[1].y, nodes[1].smooth) == (20, 30, False)
    expected = math.trunc(20 - math.tan(math.radians(-12)) * 20)
    assert (nodes[2].x, nodes[2].y) == (expected, 50)
    assert (nodes[0].x, nodes[0].y) == (20, 30)


def test_clockwise_presets_and_invalid_angles(world: Any) -> None:
    seed(world, "Rotate Selection")
    ns = load("Rotate Selection")
    for angle in (1, 10, 45, -1, -10, -45):
        matrix = ns["selection_matrix"](angle, (0, 0))
        x, y = ns["affine"].apply(matrix, 100, 0)
        assert (x, y) == pytest.approx(
            (100 * math.cos(math.radians(angle)), 100 * math.sin(math.radians(angle)))
        )
    for bad in (float("nan"), float("inf")):
        with pytest.raises(ValueError):
            ns["selection_matrix"](bad, (0, 0))


@pytest.mark.parametrize("title", NAMES[:3])
def test_component_transform_uses_placed_bounds_and_selected_flag(
    world: Any, title: str
) -> None:
    nodes = seed(world, title)
    for node in nodes:
        node.selected = False
    component = Shape(world, base="acute", dx=200, dy=50, matrix=(2, 0, 0, 1))
    component.selected, component.contentLocked = True, False

    component.boundingBox = Rect(0, 0, 40, 20)
    world.layer("A")._shapes.append(component)
    panel = load(title)["main"]()
    if title == "Rotate Selection":
        panel.degrees.setValue(90)
        expected = (0, 2, -1, 0, 250, 20)
    elif title == "Reflect Horizontally":
        expected = (-2, 0, 0, 1, 280, 50)
    else:
        expected = (2, 0, 0, -1, 200, 70)
    press(panel)
    assert component.transform.values == pytest.approx(expected)
    assert len(world.notifications()) == 1
    component.selected = False
    component.active = True
    press(panel)
    assert len(world.notifications()) == 1, "active alone is not selection"


@pytest.mark.parametrize("title", NAMES[:3])
def test_shape_space_roundtrip_and_all_master_scope(world: Any, title: str) -> None:
    seed(world, title)
    for layer in world.glyphs["A"].layers:
        shape = layer.shapes[0]
        shape.transform = Transform(2, 0, 0, 3, 20, -10)
        for index, node in enumerate(shape.contours[0].nodes()):
            node.selected = index < 3
    panel = load(title)["main"]()
    panel.scope.setCurrentIndex(1)
    if title == "Rotate Selection":
        panel.degrees.setValue(90)
        expected = (87.5, -25 / 3)
    elif title == "Reflect Horizontally":
        expected = (100, 0)
    else:
        expected = (0, 50)
    press(panel)
    first = world.layer("A").shapes[0].contours[0].nodes()[0]
    assert (first.x, first.y) == pytest.approx(expected)
    assert world.notifications()[0][2] == ["A/Light", "A/Bold", "A"]
    press(panel)
    assert len(world.notifications()) == 2, "one step on each repeated click"


@pytest.mark.parametrize("title", NAMES)
@pytest.mark.parametrize(
    "fault", ("shape lock", "contour transform", "stale master", "timeout")
)
def test_additional_refusals(
    world: Any, title: str, fault: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world, title)
    panel = load(title)["main"]()
    shape = world.layer("A").shapes[0]
    if fault == "shape lock":
        shape.contentLocked = True
    elif fault == "contour transform":
        shape.contours[0].transform = Transform(2, 0, 0, 1, 0, 0)
    elif fault == "stale master":
        world.package.master = "Bold"
    else:
        import sys

        def timeout(*args: Any, **kwargs: Any) -> Any:
            raise TimeoutError("Selection deadline exceeded")

        monkeypatch.setattr(
            sys.modules["fontlabapp.history"], "scan_auto_facts", timeout
        )
    press(panel)
    assert "Error" in panel.status.text
    assert not world.history()


@pytest.mark.parametrize("title", ("Overlap Nodes",))
def test_open_endpoints_and_quadratic_contours_stay(world: Any, title: str) -> None:
    nodes = seed(world, title)
    contour = world.layer("A").shapes[0].contours[0]
    contour.closed = False
    for node in nodes:
        node.selected = False
    nodes[-1].selected = True
    # Last endpoint has no suitable preceding corner in this fixture.
    assert not load(title)["tip_changes"](world.layer("A"), 0)
    contour.isTT = True
    panel = load(title)["main"]()
    assert not panel.apply_button.enabled
    assert "quadratic" in str(panel.table.row_texts())


def test_overlap_previous_side_translation_and_zero_angle(world: Any) -> None:
    nodes = seed(world, "Overlap Nodes")
    # Select the far endpoint: its previous neighbour is now a corner with a handle.
    nodes[-1].on = True
    nodes[-2].on = True
    nodes[-3].on = False
    nodes[0].selected, nodes[-1].selected = False, True
    shape = world.layer("A").shapes[0]
    shape.transform = Transform(1, 0, 0, 1, 0.25, 10)
    world.package.italicAngle_value = 0
    panel = load("Overlap Nodes")["main"]()
    press(panel)
    assert (nodes[-2].x, nodes[-2].y, nodes[-2].smooth) == (100, 20, False)
    assert nodes[-3].x == 99.75, "integer handle x is computed in glyph space"


@pytest.mark.parametrize("title", NAMES)
def test_fresh_main_guard_and_close_releases_signals(world: Any, title: str) -> None:
    seed(world, title)
    ns = runpy.run_path(str(FOLDER / f"{title}.py"), run_name="__main__")
    import sys

    panel = sys._fontlab_samples[ns["KEY"]]
    panel.close_button.clicked.emit()
    assert panel.deleted and ns["KEY"] not in sys._fontlab_samples


@pytest.mark.parametrize("title", NAMES)
def test_auxiliary_editor_layer_uses_exact_selected_occurrence(
    world: Any, title: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world, title)
    import fly.ap.layer_selection as selection

    glyph = world.glyphs["A"]
    layer = glyph.by_master.pop("Light")
    layer.name, layer.marker = "Light@Alternate", "A/Light@Alternate"
    glyph.by_master[layer.name] = layer
    monkeypatch.setattr(
        selection,
        "capture",
        lambda deadline: NS(
            occurrences=(NS(package=world.package, glyph=glyph, layer=layer),)
        ),
    )
    panel = load(title)["main"]()
    assert panel.apply_button.enabled, panel.status.text
    press(panel)
    assert world.notifications()[0][2] == ["A/Light@Alternate", "A"]


@pytest.mark.parametrize("title", NAMES)
def test_nonfinite_nodes_refused_before_history(world: Any, title: str) -> None:
    nodes = seed(world, title)
    nodes[0]._x = float("inf")
    panel = load(title)["main"]()
    assert not panel.apply_button.enabled
    press(panel)
    assert not world.history()


def test_mixed_editor_layers_do_not_edit_cross_product(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world, "Reflect Horizontally")
    original = world.layer("A").shapes[0].contours[0].xy()
    world.same("B", [(x, y, int(on)) for x, y, on in original])
    for glyph in world.glyphs.values():
        for layer in glyph.layers:
            layer.isLocked = False
            shape = layer.shapes[0]
            shape.selected = shape.contentLocked = False
            contour = shape.contours[0]
            contour.transform = Transform()
            for node in contour.nodes():
                node.selected, node.smooth = True, True
    import fly.ap.layer_selection as selection

    rows = tuple(
        NS(
            package=world.package,
            glyph=world.glyphs[name],
            layer=world.layer(name, master),
        )
        for name, master in (("A", "Light"), ("B", "Bold"))
    )
    monkeypatch.setattr(selection, "capture", lambda deadline: NS(occurrences=rows))
    panel = load("Reflect Horizontally")["main"]()
    press(panel)
    assert world.notifications()[0][2] == ["A/Light", "B/Bold", "A", "B"]
    assert world.points("A", "Bold")[0] == original
    assert world.points("B", "Light")[0] == original


@pytest.mark.parametrize("title", NAMES)
def test_host_whole_unit_rounding_passes_readback(world: Any, title: str) -> None:
    seed(world, title)
    panel = load(title)["main"]()
    world.round_writes = True
    press(panel)
    assert "Error" not in panel.status.text, panel.status.text
    assert len(world.notifications()) == 1


def test_overlap_conflicting_tip_targets_refused(world: Any) -> None:
    nodes = seed(world, "Overlap Nodes")
    nodes[3].on = True
    nodes[4].selected = True
    panel = load("Overlap Nodes")["main"]()
    assert not panel.apply_button.enabled
    press(panel)
    assert "conflicting targets" in panel.status.text
    assert not world.history()


def test_overlap_uses_each_layers_own_master_angle(world: Any) -> None:
    seed(world, "Overlap Nodes")
    world.package.angles.update(Light=0, Bold=-12)
    world.layer("A", "Bold").shapes[0].contours[0].nodes()[0].selected = True
    panel = load("Overlap Nodes")["main"]()
    panel.scope.setCurrentIndex(1)
    rows = panel.table.row_texts()
    assert "italic 0°" in str(rows[0]), rows
    assert "italic -12°" in str(rows[1]), rows
    press(panel)
    upright = world.layer("A", "Light").shapes[0].contours[0].nodes()[2]
    italic = world.layer("A", "Bold").shapes[0].contours[0].nodes()[2]
    assert upright.x == 20, "Light uses its own upright angle"
    assert italic.x == 24, "Bold uses its own -12 degree angle"
    assert world.package.master == "Light", "angle read restores the current master"
    one_step(world, "Overlap Nodes", ["A/Light", "A/Bold"], ["A"])


@pytest.mark.parametrize("suffix", ("@Alternate", "#Bracket"))
def test_overlap_auxiliary_own_master_angle(
    world: Any, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    seed(world, "Overlap Nodes")
    world.package.angles.update(Light=0, Bold=-12)
    glyph = world.glyphs["A"]
    layer = glyph.by_master.pop("Bold")
    layer.name = "Bold" + suffix
    layer.marker = "A/" + layer.name
    glyph.by_master[layer.name] = layer
    layer.shapes[0].contours[0].nodes()[0].selected = True
    import fly.ap.layer_selection as selection

    monkeypatch.setattr(
        selection,
        "capture",
        lambda deadline: NS(
            occurrences=(NS(package=world.package, glyph=glyph, layer=layer),)
        ),
    )
    panel = load("Overlap Nodes")["main"]()
    assert "italic -12°" in str(panel.table.row_texts())
    press(panel)
    assert layer.shapes[0].contours[0].nodes()[2].x == 24
    assert world.package.master == "Light"


def test_overlap_unassociated_layer_is_refused(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world, "Overlap Nodes")
    glyph = world.glyphs["A"]
    layer = glyph.by_master.pop("Light")
    layer.name = "Drawing"
    glyph.by_master[layer.name] = layer
    import fly.ap.layer_selection as selection

    monkeypatch.setattr(
        selection,
        "capture",
        lambda deadline: NS(
            occurrences=(NS(package=world.package, glyph=glyph, layer=layer),)
        ),
    )
    panel = load("Overlap Nodes")["main"]()
    assert not panel.apply_button.enabled
    press(panel)
    assert "master" in panel.status.text.lower()
    assert not world.history()


@pytest.mark.parametrize("amount", (1, 10, 45))
@pytest.mark.parametrize("direction,sign", (("CW", -1), ("CCW", 1)))
def test_rotate_preset_applies_in_one_click(
    world: Any, amount: int, direction: str, sign: int
) -> None:
    nodes = seed(world, "Rotate Selection")
    panel = load("Rotate Selection")["main"]()
    button = next(
        button for button in Button.registry if button.text == f"{amount}° {direction}"
    )
    button.clicked.emit(True)
    assert panel.degrees.value == sign * amount
    angle = math.radians(sign * amount)
    assert (nodes[0].x, nodes[0].y) == pytest.approx(
        (
            50 - 50 * math.cos(angle) + 25 * math.sin(angle),
            25 - 50 * math.sin(angle) - 25 * math.cos(angle),
        )
    )
    assert len(world.notifications()) == 1, "preset click writes exactly once"


def test_scripts_use_only_public_app_names() -> None:
    """Forbid private module imports and attributes through every App alias."""
    used = app_names_used([FOLDER / f"{title}.py" for title in NAMES])
    assert all(
        not part.startswith("_") for module in used for part in module.split(".")
    ), used
    assert all(not name.startswith("_") for names in used.values() for name in names), used


@pytest.mark.parametrize("title", NAMES)
def test_panel_overrides_match_installed_public_hooks(world: Any, title: str) -> None:
    """Compare subclass calls with the installed base, using only native fakes."""
    import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
    import fly.ap.outline_panel as outline_panel  # noqa: PLR0402

    with pytest.raises(TypeError):
        layer_selection.capture()
    panel = load(title)["SelectionPanel"]
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
    for node in ast.walk(ast.parse((FOLDER / f"{title}.py").read_text())):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            assert not (node.value.id == "self" and node.attr.startswith("_")), node.attr


def test_explicit_fly_app_paths_have_no_private_names() -> None:
    """Also catch full fly.ap.module._member paths without import aliases."""
    for path in [FOLDER / f"{title}.py" for title in NAMES]:
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
