# this_file: tests/test_issue122_G9.py
# SPDX-License-Identifier: Apache-2.0
"""Behaviour checks for three Resistenza rewrites; no native acceptance claim."""

import ast
import copy
import importlib.util
import itertools
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "Master Twins": ROOT / "Scripts/Masters/Master Twins.py",
    "Deliver Glyphs": ROOT / "Scripts/Masters/Deliver Glyphs.py",
    "Style Linker": ROOT / "Scripts/Names/Style Linker.py",
}


def load(title: str) -> Any:
    """Load one menu without starting its UI."""
    spec = importlib.util.spec_from_file_location(title.replace(" ", "_"), PATHS[title])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


@pytest.mark.parametrize("title", PATHS)
def test_public_contract(title: str) -> None:
    source = PATHS[title].read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    assert source.startswith(f"# this_file: {PATHS[title].relative_to(ROOT)}\n")
    doc = ast.get_docstring(tree)
    for text in (
        "What:",
        "How:",
        "Why:",
        "Use:",
        "Benefit:",
        "Giuseppe Salerno",
        "Apache-2.0",
        "https://github.com/rsztype/Scripts",
    ):
        assert text in doc, text
    for text in ("archived", "unresolved", "issue 122", "native acceptance", "draft"):
        assert text not in source.lower(), text
    forbidden = {
        "render",
        "size",
        "layout",
        "update",
        "font",
        "move",
        "statusBar",
        "name",
        "result",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert (
                not {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                & forbidden
            )
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        ):
            assert node.attr not in forbidden


def test_real_app_names() -> None:
    check_real_app_names(app_names_used(PATHS.values()))


@pytest.mark.parametrize(
    "source,target,fallback,expected",
    [
        (
            ["Regular", "Bold"],
            [" bold ", "Black"],
            "Regular",
            [(" bold ", "Bold", False), ("Black", "Regular", True)],
        ),
        (["Light"], ["Light"], "Light", [("Light", "Light", False)]),
    ],
)
def test_delivery_master_pairing(
    source: list[str], target: list[str], fallback: str, expected: list[Any]
) -> None:
    assert load("Deliver Glyphs").master_pairs(source, target, fallback) == expected


@pytest.mark.parametrize(
    "source,target,fallback",
    [
        ([], ["A"], "A"),
        (["A", " a "], ["B"], "A"),
        (["A"], [], "A"),
        (["A"], ["B"], "X"),
    ],
)
def test_delivery_refuses_ambiguous_masters(
    source: list[str], target: list[str], fallback: str
) -> None:
    with pytest.raises(ValueError):
        load("Deliver Glyphs").master_pairs(source, target, fallback)


def instance(style: str, group: str = "", active: bool = True) -> Any:
    class Instance:
        def setSLV(self, bold: bool, italic: bool) -> None:
            self.slv = int(italic) | (int(bold) << 1)

        def autoSGN(self, family: str) -> str:
            return family if self.tsn == "Regular" else family + " " + self.tsn

    value = Instance()
    value.name = style
    value.tsn = style
    value.sgn = group
    value.slv = 0
    value.exportable = active
    value.location = {}
    value.weight, value.width, value.weightValue = "Regular", "Normal", 400
    return value


def test_style_proposals_use_native_style_group_and_whole_words() -> None:
    tool = load("Style Linker")
    values = [
        instance("Regular", "Family"),
        instance("Bold"),
        instance("Bold Italic"),
        instance("ExtraBold"),
        instance("Condensed", "Family Condensed"),
        instance("Condensed Bold Italic"),
        instance("Italic", active=False),
    ]
    assert tool.link_plan(values) == [
        (1, "Family", 2),
        (2, "Family", 3),
        (5, "Family Condensed", 3),
    ]
    assert values[1].sgn == ""


def test_style_fallback_and_duplicate_refusal() -> None:
    tool = load("Style Linker")
    assert tool.link_plan(
        [instance("Bold", "Family Bold"), instance("Bold Italic")]
    ) == [(1, "Family Bold", 1)]
    with pytest.raises(ValueError, match="Duplicate"):
        tool.link_plan([instance("Regular"), instance("Regular")])
    assert tool.link_plan([]) == []


LOG: list[tuple[str, Any]] = []
STAMP = "UTC-stamp"
IDS = itertools.count(1000)

NATIVE_MEMBERS = {
    "metric", "update", "layout", "font", "palette", "parent", "style", "size",
    "pos", "width", "height", "geometry", "show", "hide", "open", "done", "accept",
    "reject", "exec", "repaint", "move", "resize", "rect", "title", "name",
    "windowTitle", "objectName", "children", "focus", "enabled", "visible", "result",
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


class Consts:
    """Any attribute is a distinct small integer, like a Qt enum."""

    def __getattr__(self, name: str) -> int:
        return sum(map(ord, name)) % 997


class FakeColor:
    HexArgb = 2

    def __init__(self, *args: Any) -> None:
        pass

    def name(self, *args: Any) -> str:
        return "#000000"

    def setAlpha(self, alpha: int) -> None:
        pass


class FakePalette:
    def color(self, *args: Any) -> FakeColor:
        return FakeColor()

    def setColor(self, *args: Any) -> None:
        pass


class FakeFont:
    def pointSizeF(self) -> float:
        return 10.0

    def __getattr__(self, name: str) -> Any:
        return lambda *a, **k: None


class Widget:
    """Accept layout calls; reject Python attributes that shadow native members."""

    SIGNALS = frozenset(
        {
            "valueChanged",
            "currentIndexChanged",
            "toggled",
            "clicked",
            "finished",
            "itemChanged",
        }
    )
    registry: ClassVar[list[Any]] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        object.__setattr__(self, "_signals", {})
        object.__setattr__(self, "_enabled", True)
        object.__setattr__(self, "args", args)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in NATIVE_MEMBERS:
            raise AttributeError(f"Slot '{name}' can not be overwritten")
        object.__setattr__(self, name, value)

    @property
    def palette(self) -> FakePalette:
        return FakePalette()

    @property
    def font(self) -> FakeFont:
        return FakeFont()

    def __getattr__(self, name: str) -> Any:
        if name == "timer":
            return None
        if name.startswith("__"):
            raise AttributeError(name)
        if name in Widget.SIGNALS:
            return self._signals.setdefault(name, Signal())
        return lambda *a, **k: None

    def setEnabled(self, flag: bool) -> None:
        object.__setattr__(self, "_enabled", bool(flag))

    def isEnabled(self) -> bool:
        return self._enabled


class Dialog(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        Widget.registry.append(self)

    def close(self) -> bool:
        self.closeEvent(NS())
        return True

    def closeEvent(self, event: Any) -> None:
        LOG.append(("close", True))


class Label(Widget):
    def __init__(self, text: str = "", *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "_text", text)

    @property
    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        object.__setattr__(self, "_text", text)


class Combo(Widget):
    def __init__(self, *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "items", [])
        object.__setattr__(self, "_index", 0)

    @property
    def currentIndex(self) -> int:
        return self._index

    @property
    def currentText(self) -> str:
        return self.items[self._index] if self.items else ""

    @property
    def count(self) -> int:
        return len(self.items)

    def addItem(self, text: str) -> None:
        self.items.append(text)

    def clear(self) -> None:
        self.items.clear()
        object.__setattr__(self, "_index", 0)

    def setCurrentIndex(self, index: int) -> None:
        object.__setattr__(self, "_index", index)

    def pick(self, index: int) -> None:
        object.__setattr__(self, "_index", index)
        self.currentIndexChanged.emit(index)


class Check(Widget):
    def __init__(self, *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "_checked", False)

    def setChecked(self, flag: bool) -> None:
        object.__setattr__(self, "_checked", bool(flag))

    def isChecked(self) -> bool:
        return self._checked

    def tick(self, flag: bool) -> None:
        object.__setattr__(self, "_checked", flag)
        self.toggled.emit(flag)


class Button(Widget):
    def __init__(self, text: str = "", *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "label", text)

    def press(self) -> None:
        self.clicked.emit(False)


class Item:
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.state = None
        self.item_flags = 0

    def font(self) -> FakeFont:
        return FakeFont()

    def flags(self) -> int:
        return self.item_flags

    def setFlags(self, value: int) -> None:
        self.item_flags = value

    def setCheckState(self, state: Any) -> None:
        self.state = state

    def checkState(self) -> Any:
        return self.state

    def __getattr__(self, name: str) -> Any:
        return lambda *a, **k: None


class Table(Widget):
    def __init__(self, rows: int = 0, columns: int = 0) -> None:
        super().__init__()
        object.__setattr__(self, "cells", {})
        object.__setattr__(self, "row_count", rows)

    def horizontalHeader(self) -> Widget:
        return Widget()

    def verticalHeader(self) -> Widget:
        return Widget()

    def setRowCount(self, count: int) -> None:
        object.__setattr__(self, "row_count", count)
        object.__setattr__(self, "cells", {})

    @property
    def rowCount(self) -> int:
        return self.row_count

    def setItem(self, row: int, column: int, item: Item) -> None:
        self.cells[row, column] = item

    def item(self, row: int, column: int) -> Item | None:
        return self.cells.get((row, column))

    def texts(self, row: int) -> list[str]:
        return [
            self.cells[row, c].text
            for c in sorted(c for r, c in self.cells if r == row)
        ]

    def all_texts(self) -> list[list[str]]:
        return [self.texts(row) for row in range(self.row_count)]


class Box:
    def __init__(self, left: float, bottom: float, right: float, top: float) -> None:
        self._v = (left, bottom, right - left, top - bottom)

    def x(self) -> float:
        return self._v[0]

    def y(self) -> float:
        return self._v[1]

    def width(self) -> float:
        return self._v[2]

    def height(self) -> float:
        return self._v[3]


class FakeTransform:
    def __init__(
        self,
        m11: float = 1,
        m12: float = 0,
        m21: float = 0,
        m22: float = 1,
        dx: float = 0,
        dy: float = 0,
    ):
        self.m = (m11, m12, m21, m22, dx, dy)

    def point(self, x: float, y: float) -> tuple[float, float]:
        m11, m12, m21, m22, dx, dy = self.m
        return m11 * x + m21 * y + dx, m12 * x + m22 * y + dy


class Point:
    """Fake QPointF."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self._x, self._y = float(x), float(y)

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Point) and (self._x, self._y) == (other._x, other._y)


class DateTime:
    @staticmethod
    def currentDateTimeUtc() -> str:
        return STAMP


def fake_qt() -> ModuleType:
    qt = ModuleType("fly.qt")
    gui, core = ModuleType("QtGui"), ModuleType("QtCore")
    gui.QDialog, gui.QLabel, gui.QComboBox, gui.QCheckBox = Dialog, Label, Combo, Check
    gui.QSpinBox = gui.QDoubleSpinBox = Widget
    gui.QPushButton, gui.QTableWidget, gui.QTableWidgetItem = Button, Table, Item
    gui.QVBoxLayout = gui.QHBoxLayout = gui.QGridLayout = Widget
    gui.QBrush = lambda color: color
    gui.QColor = FakeColor
    gui.QTransform = FakeTransform
    for name in ("QPalette", "QAbstractItemView", "QHeaderView"):
        setattr(gui, name, Consts())
    core.Qt = Consts()
    core.QDateTime = DateTime
    core.QPointF = Point
    qt.QtGui, qt.QtCore = gui, core
    return qt


# ---------------------------------------------------------------- FontLab fakes
class Node:
    def __init__(self, x: float, y: float, name: str = "", state: int = 0) -> None:
        self.x, self.y, self.name, self.nodeState = x, y, name, state


class Contour:
    def __init__(self, points: Any, names: Any = (), states: Any = ()) -> None:
        names, states = list(names), list(states)
        self._nodes = [
            Node(
                x,
                y,
                names[i] if i < len(names) else "",
                states[i] if i < len(states) else 0,
            )
            for i, (x, y) in enumerate(points)
        ]

    def nodes(self) -> list[Node]:
        return list(self._nodes)


def square(left: float, bottom: float, right: float, top: float, **kw: Any) -> Contour:
    return Contour([(left, bottom), (right, bottom), (right, top), (left, top)], **kw)


class Shape:
    """Fake flShape. clone() loses what FontLab's clone loses (fl#8516, fl#8538)."""

    def __init__(
        self,
        contours: Any = (),
        component: str | None = None,
        note: str = "",
        name: str = "",
    ) -> None:
        self.id = next(IDS)
        self.isComponent = component is not None
        self.shapeData = NS(
            note=note,
            name=name,
            componentGlyph=component or "",
            builder=NS(builds=component or ""),
        )
        self.contours = list(contours)
        self.active = self.selected = False
        self.drop_contour = False

    def clone(self) -> "Shape":
        copies = [Contour([(n.x, n.y) for n in c.nodes()]) for c in self.contours]
        if self.drop_contour:
            copies = copies[:-1]
        return Shape(copies)


class Pin:
    def __init__(self, name: str, x: float, y: float) -> None:
        self.name, self.point = name, Point(x, y)


class Layer:
    def __init__(
        self,
        name: str,
        glyph: Any = None,
        *,
        shapes: Any = (),
        anchors: Any = (),
        width: float = 500,
        **flags: Any,
    ):
        self.id = next(IDS)
        self.name, self.glyph = name, glyph
        self.shapes = list(shapes)
        self.anchors = list(anchors)
        self._width = width
        self.isMaskLayer = flags.pop("mask", name.startswith("mask."))
        self.isService = flags.pop("service", self.isMaskLayer)
        self.isImgLayer = flags.pop("image", False)
        self.autoLayer = flags.pop("auto", False)
        self.isLocked = flags.pop("locked", False)
        self.metricsLeft = flags.pop("metricsLeft", "")
        self.metricsRight = self.metricsWidth = ""
        self.guidelines: list[Any] = flags.pop("guidelines", [])
        self.note = flags.pop("note", "")
        self.recipe = self.lib = ""
        self.hasTTH = self.hasTTData = False
        self.isNull, self.isValid = False, True
        self.update_ok = True
        self.stubborn = False
        self.keep_components = False  # removeShape ignores components (read-back tests)
        assert not flags, flags

    @property
    def advanceWidth(self) -> float:
        return self._width

    @advanceWidth.setter
    def advanceWidth(self, value: float) -> None:
        LOG.append(("edit", ("width", self.name)))
        if not self.stubborn:
            self._width = value

    @property
    def boundingBox(self) -> Box:
        points = [
            (n.x, n.y)
            for s in self.shapes
            if not s.isComponent
            for c in s.contours
            for n in c.nodes()
        ]
        if not points:
            return Box(0, 0, 0, 0)
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        return Box(min(xs), min(ys), max(xs), max(ys))

    def getMaskLayer(self, create: bool) -> Any:
        name = "mask." + self.name
        found = (
            next((x for x in self.glyph.layers if x.name == name), None)
            if self.glyph
            else None
        )
        if found is None and create:
            LOG.append(("edit", ("create mask", name)))
            found = Layer(name, self.glyph)
            self.glyph.layers.append(found)
        return found

    def checkInitHistoryState(self, level: int) -> None:
        LOG.append(("init", self.name))

    def removeShape(self, shape: Shape) -> None:
        LOG.append(("edit", ("removeShape", self.name)))
        if not (self.keep_components and shape.isComponent):
            self.shapes.remove(shape)

    def addShape(self, shape: Shape) -> Shape:
        LOG.append(("edit", ("addShape", self.name)))
        if not self.stubborn:
            self.shapes.append(shape)
        return shape

    def removeAllShapes(self) -> None:
        LOG.append(("edit", ("removeAllShapes", self.name)))
        self.shapes = []

    def applyTransform(self, transform: FakeTransform) -> None:
        LOG.append(("edit", ("move", self.name)))
        for shape in self.shapes:
            for contour in shape.contours:
                for node in contour.nodes():
                    node.x, node.y = transform.point(node.x, node.y)
        for pin in self.anchors:
            pin.point = Point(*transform.point(pin.point.x(), pin.point.y()))

    def changed(self) -> None:
        LOG.append(("edit", ("changed", self.name)))

    def update(self) -> bool:
        return self.update_ok


class Glyph:
    def __init__(
        self, name: str, layers: dict[str, dict[str, Any]] | None = None
    ) -> None:
        self.id = next(IDS)
        self.name = name
        self.isNull = False
        self.layers: list[Layer] = []
        for layer_name, spec in (layers or {}).items():
            self.layers.append(Layer(layer_name, self, **spec))
        self.active = self.layers[0] if self.layers else None
        self._stamp: Any = None
        self.remove_fails = False

    @property
    def lastModified(self) -> Any:
        return self._stamp

    @lastModified.setter
    def lastModified(self, value: Any) -> None:
        LOG.append(("stamp", self.name))
        self._stamp = value

    def layer(self, name: str) -> Layer:
        return next(x for x in self.layers if x.name == name)

    def findLayer(self, name: str) -> Layer | None:
        return next((x for x in self.layers if x.name.lower() == name.lower()), None)

    def removeLayer(self, layer: Layer) -> None:
        LOG.append(("edit", ("removeLayer", layer.name)))
        if self.remove_fails:
            return
        self.layers = [x for x in self.layers if x is not layer]

    def updateActiveLayer(self, assign: bool) -> Layer | None:
        assert assign is False
        return self.active

    def checkInitHistoryState(self, level: int) -> None:
        LOG.append(("init", self.name))


class Package:
    def __init__(
        self,
        glyphs: list[Glyph],
        masters: tuple[str, ...] = ("Light", "Bold"),
        ident: int = 7,
    ) -> None:
        self.id, self.fgId, self.masters, self.master = (
            ident,
            ident + 7000,
            list(masters),
            masters[0],
        )
        self.glyphs = {g.name: g for g in glyphs}
        self.isNull = False

    @property
    def instances(self) -> list[Any]:
        return copy.deepcopy(getattr(self, "_instances", []))

    @instances.setter
    def instances(self, values: list[Any]) -> None:
        self._instances = copy.deepcopy(values)

    def findName(self, name: str) -> Glyph | None:
        return self.glyphs.get(name)

    def records(self) -> tuple:
        return tuple(
            (
                g.name,
                bool(x.autoLayer),
                tuple(s.shapeData.componentGlyph for s in x.shapes if s.isComponent),
            )
            for g in self.glyphs.values()
            for x in g.layers
        )


class World:
    def __init__(self) -> None:
        self.package: Package | None = None
        self.selection: list[str] = []
        self.history: list[tuple[str, list[Any]]] = []
        self.flags: list[
            tuple[Any, ...]
        ] = []  # extra notify arguments (deep history flag)
        self.updates: list[Any] = []
        self.closed: list[str] = []
        self.shown: list[Any] = []

    def notifications(self) -> list[tuple[str, list[Any]]]:
        return list(self.history)

    def use(
        self,
        glyphs: list[Glyph],
        masters: tuple[str, ...] = ("Light", "Bold"),
        selection: list[str] | None = None,
    ) -> Package:
        self.package = Package(glyphs, masters)
        self.selection = [g.name for g in glyphs] if selection is None else selection
        return self.package

    def facts(self) -> Any:
        return self.app["history"].scan_auto_facts(self.package)


@pytest.fixture
def native_world(monkeypatch: pytest.MonkeyPatch, real_app: Any) -> World:
    state = World()
    LOG.clear()
    Widget.registry = []
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    scripting = ModuleType("fly.ap.scripting")
    completion = ModuleType("fly.ap.script_completion")
    fontlab = ModuleType("fontlab")
    items = ModuleType("items")

    def notify(title: str, objects: list[Any], *flags: Any) -> None:
        LOG.append(("notify", title))
        state.history.append((title, list(objects)))
        state.flags.append(flags)

    items.notifyChangesApplied = notify
    fontlab.flItems = lambda: items
    fontlab.flItems.notifyChangesApplied = notify
    fontlab.UpdateAll = lambda: LOG.append(("UpdateAll", True))
    fontlab.flGlyph = NS(updatedFgGlyphs=lambda: list(state.updates))
    ap.fontlab = fontlab
    scripting.current_package = lambda expected_id=None: state.package
    scripting.names_selected_names = lambda: list(state.selection)
    scripting.names_font_glyphs = lambda: [
        (n, []) for n in (state.package.glyphs if state.package else [])
    ]

    def connect_guarded(dialog: Any, signal: Any, callback: Any) -> None:
        def guarded(*args: Any) -> None:
            try:
                callback(*args)
            except Exception as error:  # noqa: BLE001
                dialog.status.setText("Error: " + repr(error))

        signal.connect(guarded)
        dialog._connections.append((signal, guarded))

    scripting.connect_guarded = connect_guarded
    scripting.close_script_dialog = lambda dialog, event, key, **kw: (
        state.closed.append(key)
    )

    def show_script_dialog(dialog_type: Any, key: str) -> Any:
        dialog = dialog_type(None)
        state.shown.append((key, dialog))
        return dialog

    scripting.show_script_dialog = show_script_dialog
    completion.install = lambda dialog, key: NS(stop=lambda: None)
    qt = fake_qt()
    fly.ap, fly.qt = ap, qt
    for name, module in {
        "fly": fly, "fly.ap": ap, "fly.qt": qt,
        "fly.ap.scripting": scripting, "fly.ap.script_completion": completion,
    }.items():  # fmt: skip
        monkeypatch.setitem(sys.modules, name, module)
    state.app = real_app(
        qt=qt,
        fontlab=fontlab,
        scripting={
            name: getattr(scripting, name)
            for name in (
                "current_package",
                "names_selected_names",
                "names_font_glyphs",
                "connect_guarded",
                "show_script_dialog",
            )
        },
        completion=completion.install,
        modules=["guides", "history", "masters", "edit_guards", "metrics_panel"],
    )
    monkeypatch.setattr(
        state.app["guides"], "dependency_values", lambda package: package.records()
    )
    ap.scripting = state.app["scripting"]
    return state


fakes = NS(
    FakeColor=FakeColor,
    Glyph=Glyph,
    LOG=LOG,
    Layer=Layer,
    Package=Package,
    Pin=Pin,
    Point=Point,
    Shape=Shape,
    square=square,
)


@pytest.fixture
def world(native_world: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Use real App writer kernels over strict native/Qt doubles."""
    import importlib

    state = native_world
    for name in (
        "anchor_writer",
        "outline_writer",
        "instance_style_names",
        "glyph_catalog",
        "layer_selection",
        "glyph_creation",
        "glyph_copies",
        "contour_copy",
    ):
        module = importlib.import_module(f"fontlabapp.{name}")
        monkeypatch.setitem(sys.modules, f"fly.ap.{name}", module)
        state.app[name] = module
    qt = sys.modules["PythonQt"]
    native = sys.modules["fontlab"]

    def new_pin(point: Any) -> Any:
        return NS(name="", point=point, anchor=False, appearance=0)

    native.flPinPoint = new_pin
    monkeypatch.setattr(
        Node,
        "getProperties",
        lambda node: [],
        raising=False,
    )
    monkeypatch.setattr(
        Node,
        "getProperty",
        lambda node, key: getattr(node, "properties", {}).get(key),
        raising=False,
    )
    monkeypatch.setattr(Contour, "name", "", raising=False)
    monkeypatch.setattr(
        Contour,
        "getProperties",
        lambda contour: [],
        raising=False,
    )

    monkeypatch.setattr(
        fakes.Layer,
        "addAnchor",
        lambda layer, pin: layer.anchors.append(pin),
        raising=False,
    )
    monkeypatch.setattr(
        fakes.Layer,
        "removeAnchor",
        lambda layer, pin: layer.anchors.remove(pin),
        raising=False,
    )
    monkeypatch.setattr(fakes.Layer, "hasHints", False, raising=False)
    monkeypatch.setattr(fakes.Shape, "name", "", raising=False)
    monkeypatch.setattr(fakes.Shape, "transform", NS(marker="identity"), raising=False)
    # Match native clone's component identity; its lossy notes/nodes stay lossy.
    original_init = Shape.__init__

    def init_shape(shape: Any, *args: Any, **kwargs: Any) -> None:
        original_init(shape, *args, **kwargs)
        shape.shapeData.referenceCount = 1

    monkeypatch.setattr(Shape, "__init__", init_shape)
    original_clone = fakes.Shape.clone

    def clone(shape: Any) -> Any:
        value = original_clone(shape)
        value.isComponent = shape.isComponent
        value.shapeData.componentGlyph = shape.shapeData.componentGlyph
        value.shapeData.referenceCount = 1
        return value

    monkeypatch.setattr(fakes.Shape, "clone", clone)
    native.MainWindow = lambda: None
    workspace = NS(findPackageId=lambda ident: state.fonts.get(ident))
    native.flWorkspace = NS(instance=lambda: workspace)
    fly = sys.modules["fly"]
    monkeypatch.setattr(fly, "fl", native, raising=False)
    tools = NS(call=lambda *a, **k: None)
    monkeypatch.setattr(fly, "pr", tools, raising=False)
    monkeypatch.setitem(sys.modules, "fontpr", tools)
    state.fonts = {}
    state.qt = qt
    state.native = native
    state.selection_window_ids = []

    def require_window(ident: int) -> None:
        assert ident == state.package.id
        assert ident != state.package.fgId
        state.selection_window_ids.append(ident)

    monkeypatch.setattr(
        state.app["edit_guards"], "require_selection_window", require_window
    )
    monkeypatch.setattr(state.app["edit_guards"], "require_no_editors", lambda: None)
    monkeypatch.setattr(
        state.app["layer_selection"],
        "capture",
        lambda deadline: NS(occurrences=[NS(glyph_name=n) for n in state.selection]),
    )
    monkeypatch.setattr(
        state.app["glyph_catalog"],
        "capture",
        lambda: NS(rows=[(n, "", "") for n in state.package.glyphs]),
    )
    return state


def seed(world: Any) -> tuple[Any, Any, Any]:
    """Create an asymmetric two-master font with explicit source metadata."""
    shape = fakes.Shape(
        [fakes.square(0, 0, 50, 80, names=["a", "b", "c", "d"], states=[32, 7, 9, 0])],
        note="keep",
        name="outline",
    )
    glyph = fakes.Glyph(
        "A",
        {
            "Light": {"shapes": [shape], "width": 480},
            "Bold": {
                "shapes": [fakes.Shape([fakes.square(0, 0, 90, 100)])],
                "width": 650,
            },
        },
    )
    package = world.use([glyph])
    package.info = NS(
        familyName="Family", openTypeNamePreferredFamilyName="", unitsPerEm=1000
    )
    package.fgPackage = [NS(name="A", unicodes=[65])]
    package.instances = []
    package._masters = NS(name="masters")
    package.mastersContainer = lambda: package._masters
    package.checkInitHistoryState = lambda index: fakes.LOG.append(("init", "package"))
    glyph.metricsLeft = glyph.metricsRight = glyph.metricsWidth = ""
    world.fonts[package.fgId] = package
    return package, glyph, shape


def test_master_copy_restores_names_flags_and_has_one_notification(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, shape = seed(world)
    before = copy.deepcopy([(n.name, n.nodeState) for n in shape.contours[0].nodes()])
    facts = world.facts()
    work = tool.copy_work(package, ["A", "A"], "Light", "Bold", tool.Content(), facts)
    assert len(work) == 1
    result = world.app["outline_writer"].apply_work(
        work, "Copy", facts, tool.editor_type()()
    )
    target = glyph.findLayer("Bold")
    assert result == {"edits": 1, "layers": 1}
    assert target.advanceWidth == 480
    cloned = target.shapes[0]
    assert cloned is not shape and cloned.shapeData.note == "keep"
    assert [(n.name, n.nodeState) for n in cloned.contours[0].nodes()] == [
        (n, s & ~32) for n, s in before
    ]
    assert [(n.name, n.nodeState) for n in shape.contours[0].nodes()] == before
    assert world.history == [("Copy", [target, glyph])]
    assert glyph.findLayer("Light").advanceWidth == 480


def test_component_only_copy_keeps_target_contours_and_retains_removed_components(
    world: Any,
) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    base = fakes.Glyph("B", {"Light": {}, "Bold": {}})
    package.glyphs["B"] = base
    source, target = glyph.findLayer("Light"), glyph.findLayer("Bold")
    source.shapes.append(fakes.Shape(component="B"))
    old = fakes.Shape(component="B")
    target.shapes.append(old)
    outline = target.shapes[0]
    facts = world.facts()
    work = tool.copy_work(
        package, ["A"], "Light", "Bold", tool.Content(False, True, False, False), facts
    )
    world.app["outline_writer"].apply_work(
        work, "Components", facts, tool.editor_type()()
    )
    assert target.shapes[0] is outline
    assert target.shapes[1].isComponent
    assert target.shapes[1].shapeData.componentLayer == "Bold"
    assert world.history[0][1] == [
        old,
        old.shapeData,
        old.shapeData.builder,
        target,
        glyph,
    ]
    assert world.flags == [(True,)]
    assert target.advanceWidth == 650


def test_empty_source_clears_only_chosen_content(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    glyph.findLayer("Light").shapes.clear()
    facts = world.facts()
    work = tool.copy_work(
        package, ["A"], "Light", "Bold", tool.Content(True, False, False, False), facts
    )
    world.app["outline_writer"].apply_work(work, "Clear", facts, tool.editor_type()())
    assert glyph.findLayer("Bold").shapes == []
    assert glyph.findLayer("Bold").advanceWidth == 650


@pytest.mark.parametrize(
    "flag", ["isLocked", "autoLayer", "isMaskLayer", "isService", "hasHints", "hasTTH"]
)
def test_master_copy_refuses_unsupported_layers_before_history(
    world: Any, flag: str
) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    setattr(glyph.findLayer("Bold"), flag, True)
    kept = []
    assert (
        tool.copy_work(
            package, ["A"], "Light", "Bold", tool.Content(), world.facts(), kept
        )
        == []
    )
    assert len(kept) == 1 and kept[0][0] == "A" and kept[0][1]
    assert not world.history


@pytest.mark.parametrize(
    "names,source,target,options",
    [
        ([], "Light", "Bold", (True, True, True, True)),
        (["A"], "Light", "Light", (True, True, True, True)),
        (["A"], "X", "Bold", (True, True, True, True)),
        (["A"], "Light", "Bold", (False, False, False, False)),
    ],
)
def test_master_copy_refuses_invalid_requests(
    world: Any, names: list[str], source: str, target: str, options: tuple[bool, ...]
) -> None:
    tool = load("Master Twins")
    package, _, _ = seed(world)
    with pytest.raises(ValueError):
        tool.copy_work(
            package, names, source, target, tool.Content(*options), world.facts()
        )
    assert not world.history


def test_anchor_copy_add_remove_move_and_origin_refusal(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    source, target = glyph.findLayer("Light"), glyph.findLayer("Bold")
    source.anchors = [fakes.Pin("top", 20, 80), fakes.Pin("bottom", 0, 0)]
    target.anchors = [fakes.Pin("top", 10, 60), fakes.Pin("old", 8, 9)]
    facts = world.facts()
    work = tool.copy_work(
        package, ["A"], "Light", "Bold", tool.Content(False, False, True, False), facts
    )
    world.app["outline_writer"].apply_work(work, "Anchors", facts, tool.editor_type()())
    assert world.app["anchor_writer"].anchor_points(target) == {
        "top": (20, 80),
        "bottom": (0, 0),
    }
    assert next(p for p in target.anchors if p.name == "top").point == fakes.Point(
        20, 80
    )
    source.anchors = [fakes.Pin("top", 0, 0)]
    with pytest.raises(ValueError, match="origin"):
        tool.anchor_edits(source, target)


def test_master_write_failure_has_undo_hint(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    glyph.findLayer("Bold").update_ok = False
    facts = world.facts()
    work = tool.copy_work(package, ["A"], "Light", "Bold", tool.Content(), facts)
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        world.app["outline_writer"].apply_work(
            work, "Copy", facts, tool.editor_type()()
        )
    assert len(world.history) == 1


def test_style_write_uses_real_history_and_package_value_list(world: Any) -> None:
    tool = load("Style Linker")
    package, _, _ = seed(world)
    package.instances = [
        instance("Regular", "Family"),
        instance("Bold"),
        instance("Italic"),
        instance("ExtraBold"),
    ]
    expected = tool.instance_state(package.instances)
    plan = tool.link_plan(package.instances)
    assert tool.apply_links(package.fgId, expected, plan) == 2
    assert [(i.sgn, i.slv) for i in package.instances] == [
        ("Family", 0),
        ("Family", 2),
        ("Family", 1),
        ("", 0),
    ]
    assert world.history == [("Style Linker", [package, package._masters])] * 2
    assert ("init", "package") in fakes.LOG
    assert (
        tool.apply_links(package.fgId, tool.instance_state(package.instances), plan)
        == 0
    )
    assert len(world.history) == 2


def test_style_write_refuses_stale_switched_and_pending(world: Any) -> None:
    tool = load("Style Linker")
    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    expected = tool.instance_state(package.instances)
    plan = tool.link_plan(package.instances)
    with pytest.raises(ValueError, match="font changed"):
        tool.apply_links(-1, expected, plan)
    values = package.instances
    values[1].sgn = "changed"
    package.instances = values
    with pytest.raises(ValueError, match="Instances changed"):
        tool.apply_links(package.fgId, expected, plan)
    world.updates.append(1)
    with pytest.raises(ValueError):
        tool.apply_links(package.fgId, tool.instance_state(package.instances), plan)
    assert not world.history


def target_font(world: Any) -> Any:
    package = fakes.Package([], ("Light", "Black"), 100)
    package.fgPackage = []
    package.info = NS(familyName="Destination", unitsPerEm=1000)
    world.fonts[package.fgId] = package
    return package


def test_delivery_new_glyph_creation_and_one_outline_action(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load("Deliver Glyphs")
    source, glyph, _ = seed(world)
    target = target_font(world)
    jobs = tool.delivery_plan(source, target, ["A", "A"], "Light", False)
    assert [(m, s, guessed) for m, s, guessed, _, _ in jobs[0]["layers"]] == [
        ("Light", "Light", False),
        ("Black", "Light", True),
    ]
    world.package = target
    calls = []

    def add(command: str, **kwargs: Any) -> dict[str, Any]:
        calls.append((command, kwargs))
        data = kwargs["glyph_data"]
        made = fakes.Glyph(
            data["name"],
            {l["name"]: {"width": l["advanceWidth"]} for l in data["layers"]},
        )
        made.metricsLeft = made.metricsRight = made.metricsWidth = ""
        target.glyphs[data["name"]] = made
        target.fgPackage.append(NS(name=data["name"], unicodes=list(data["unicodes"])))
        return {"status": "ok", "created": True}

    monkeypatch.setattr(sys.modules["fly"].pr, "call", add)
    result = tool.deliver(target, jobs, False)
    assert result == {"created": 1, "glyphs": 1, "layers": 2, "unicode_changes": ["A"]}
    assert calls == [
        (
            "set_glyph",
            {
                "font_id": target.fgId,
                "glyph_name": "A",
                "create": True,
                "glyph_data": {
                    "name": "A",
                    "layers": [
                        {"name": "Light", "advanceWidth": 480},
                        {"name": "Black", "advanceWidth": 480},
                    ],
                    "unicodes": [65],
                },
            },
        )
    ]
    added = target.findName("A")
    assert world.history == [
        ("Deliver Glyphs", [added.findLayer("Light"), added.findLayer("Black"), added])
    ]
    assert len(glyph.findLayer("Light").shapes) == 1


def test_delivery_preserves_existing_by_default_and_replaces_explicitly(
    world: Any,
) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    target = target_font(world)
    target.glyphs["A"] = fakes.Glyph("A", {"Light": {}, "Black": {}})
    target.fgPackage = [NS(name="A", unicodes=[66])]
    assert (
        "Replace is off"
        in tool.delivery_plan(source, target, ["A"], "Light", False)[0]["note"]
    )
    jobs = tool.delivery_plan(source, target, ["A"], "Light", True)
    world.package = target
    assert tool.deliver(target, jobs, False) == {
        "created": 0,
        "glyphs": 1,
        "layers": 2,
        "unicode_changes": [],
    }
    assert target.fgPackage[0].unicodes == [66], "Existing destination Unicode is kept"
    assert len(world.history) == 1


def test_delivery_auto_warning_requires_consent_before_creation(world: Any) -> None:
    tool = load("Deliver Glyphs")
    source, glyph, _ = seed(world)
    source.glyphs = {"A.sc": glyph}
    glyph.name = "A.sc"
    source.fgPackage[0].name = "A.sc"
    target = target_font(world)
    target.glyphs["Aacute.sc"] = Glyph("Aacute.sc", {"Light": {"auto": True}})
    target.fgPackage = [NS(name="Aacute.sc", unicodes=[])]
    jobs = tool.delivery_plan(source, target, ["A.sc"], "Light", False)
    assert tool.rebuild_rows(target, jobs) == {"A.sc": ("Aacute.sc",)}
    world.package = target
    with pytest.raises(ValueError, match="Tick"):
        tool.deliver(target, jobs, False)
    assert not world.history and target.findName("A.sc") is None


@pytest.mark.parametrize(
    "kind", ["component", "hint", "auto", "locked", "missing", "nonfinite"]
)
def test_delivery_refuses_unsupported_source_content(world: Any, kind: str) -> None:
    tool = load("Deliver Glyphs")
    source, glyph, _ = seed(world)
    layer = glyph.findLayer("Light")
    if kind == "component":
        layer.shapes.append(Shape(component="B"))
    elif kind == "missing":
        glyph.layers.remove(layer)
    elif kind == "nonfinite":
        layer._width = float("nan")
    else:
        setattr(
            layer,
            {"hint": "hasHints", "auto": "autoLayer", "locked": "isLocked"}[kind],
            True,
        )
    jobs = tool.delivery_plan(source, target_font(world), ["A"], "Light", False)
    assert jobs[0]["note"] and not world.history
    assert tool.preview_rows(jobs)[0][-1].startswith("kept:")


@pytest.mark.parametrize("title", PATHS)
def test_panels_are_nonmodal_use_owned_signals_and_close(
    world: Any, title: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    # The real common shell is used; only its fake colour enum needs one member.
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)
    panel = load(title).panel_type()(None)
    assert panel._connections, "Every panel owns its signals"
    assert not world.history, "Opening a panel must not edit the font"
    panel.close_button.press()
    assert ("close", True) in LOG, "Close uses the common lifecycle"


def test_panel_reports_capture_timeout(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world)
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)

    def timeout(deadline: float) -> Any:
        raise TimeoutError("capture timed out")

    monkeypatch.setattr(world.app["layer_selection"], "capture", timeout)
    panel = load("Master Twins").panel_type()(None)
    assert "capture timed out" in panel.status.text
    assert not panel.apply_button.isEnabled()


def test_master_refuses_duplicate_anchors(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    glyph.findLayer("Light").anchors = [Pin("top", 1, 2), Pin("top", 3, 4)]
    kept = []
    assert (
        tool.copy_work(
            package, ["A"], "Light", "Bold", tool.Content(), world.facts(), kept
        )
        == []
    )
    assert "Duplicate anchor" in kept[0][1] and not world.history


def test_master_refuses_new_indirect_component_cycle(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    glyph.findLayer("Light").shapes = [Shape(component="B")]
    package.glyphs["B"] = Glyph(
        "B", {"Light": {}, "Bold": {"shapes": [Shape(component="A")]}}
    )
    kept = []
    assert (
        tool.copy_work(
            package, ["A"], "Light", "Bold", tool.Content(), world.facts(), kept
        )
        == []
    )
    assert "cycle" in kept[0][1] and not world.history


def test_delivery_refuses_duplicate_anchors(world: Any) -> None:
    tool = load("Deliver Glyphs")
    source, glyph, _ = seed(world)
    glyph.findLayer("Light").anchors = [Pin("top", 1, 2), Pin("top", 3, 4)]
    jobs = tool.delivery_plan(source, target_font(world), ["A"], "Light", False)
    assert "Duplicate anchor" in jobs[0]["note"] and not world.history


def test_delivery_add_command_failure_has_undo_hint(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    target = target_font(world)
    jobs = tool.delivery_plan(source, target, ["A"], "Light", False)
    world.package = target

    def failure(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Add Glyph failed after dispatch")

    monkeypatch.setattr(sys.modules["fly"].pr, "call", failure)
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        tool.deliver(target, jobs, False)


@pytest.mark.parametrize("title", PATHS)
def test_main_routes_to_shared_owned_registry(
    world: Any, title: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)
    menu = load(title)
    assert menu.main() is world.shown[-1][1]
    assert world.shown[-1][0] == menu.KEY


def test_master_panel_copy_and_font_switch_refusal(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, glyph, _ = seed(world)
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)
    panel = load("Master Twins").panel_type()(None)
    assert panel.apply_button.isEnabled()
    assert panel.table.all_texts() == [["A", "Light", "Bold", "copy"]]
    panel.apply_button.press()
    assert glyph.findLayer("Bold").advanceWidth == 480
    assert len(world.history) == 1
    world.package = None
    panel.apply_button.press()
    assert "font changed" in panel.status.text
    assert len(world.history) == 1
    world.package = package
    panel.all_glyphs.tick(True)
    assert panel.apply_button.isEnabled()


def test_style_panel_apply_and_empty_font_feedback(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)
    panel = load("Style Linker").panel_type()(None)
    assert panel.table.all_texts()[1] == ["Bold", "Family", "✓", "", "link"]
    panel.apply_button.press()
    assert package.instances[1].slv == 2 and package.instances[1].sgn == "Family"
    assert len(world.history) == 2
    world.package = None
    panel.refresh_button.press()
    assert "Open a font" in panel.status.text
    assert not panel.apply_button.isEnabled()


def test_delivery_panel_checks_source_lifetime_and_preview_identity(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, _, _ = seed(world)
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)
    panel = load("Deliver Glyphs").panel_type()(None)
    target = target_font(world)
    world.package = target
    panel.preview_button.press()
    assert panel.table.all_texts() == [
        ["A", "Light", "Light", "add; Unicode assigned on creation"],
        ["A", "Black", "Light", "add; Unicode assigned on creation; fallback"],
    ]
    assert panel.apply_button.isEnabled()
    target.masters = ["Light"]
    panel.apply_button.press()
    assert "delivery changed" in panel.status.text
    assert not world.history
    world.fonts.pop(source.fgId)
    panel.preview_button.press()
    assert "closed" in panel.status.text
    assert not panel.apply_button.isEnabled()


@pytest.mark.parametrize("title", PATHS)
def test_close_disconnects_all_owned_signals_before_deletion(
    world: Any, title: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run the actual App cleanup, rather than accepting a close-recording fake."""
    import inspect

    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    monkeypatch.setattr(fakes.FakeColor, "HexArgb", 1, raising=False)
    scripting = world.app["scripting"]
    import importlib

    assert (
        scripting.close_script_dialog
        is importlib.import_module("fontlabapp.scripting").close_script_dialog
    )
    assert inspect.isfunction(scripting.close_script_dialog)
    menu = load(title)
    panel = menu.panel_type()(None)
    panel.timer = None
    stopped: list[bool] = []
    panel._completion_lifetime = NS(stop=lambda: stopped.append(True))
    owned = list(panel._connections)
    assert all(slot in signal.slots for signal, slot in owned)
    panel.close_button.press()
    assert stopped == [True]
    assert panel._connections == []
    assert all(slot not in signal.slots for signal, slot in owned)


def test_editor_check_returns_mismatch_texts(world: Any) -> None:
    tool = load("Master Twins")
    _package, glyph, _ = seed(world)
    target = glyph.findLayer("Bold")
    target.stubborn = True
    editor = tool.editor_type()()
    steps = editor.prepare(target, [(glyph.findLayer("Light"), tool.Content())])
    editor.write(target, steps)
    assert editor.check([(target, steps)]) == [
        "Bold: shape replacement",
        "Bold: metrics",
    ]


def test_clone_topology_loss_refuses_before_history(world: Any) -> None:
    tool = load("Master Twins")
    package, _, shape = seed(world)
    shape.drop_contour = True
    facts = world.facts()
    work = tool.copy_work(package, ["A"], "Light", "Bold", tool.Content(), facts)
    with pytest.raises(ValueError):
        world.app["outline_writer"].apply_work(
            work, "Copy", facts, tool.editor_type()()
        )
    assert not world.history


def test_style_keeps_automatic_base_groups_instead_of_guessing_family(
    world: Any,
) -> None:
    tool = load("Style Linker")
    package, _, _ = seed(world)
    package.instances = [instance("Regular"), instance("Bold")]
    rows = tool.link_rows(package.instances)
    assert "automatic" in rows[1][-1]
    assert tool.link_plan(package.instances) == []
    package.info.familyName = "Different from instance tfn"
    assert (
        tool.apply_links(package.fgId, tool.instance_state(package.instances), []) == 0
    )
    assert not world.history


def test_delivery_refuses_changed_font_and_source_equals_target(world: Any) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    with pytest.raises(ValueError, match="different destination"):
        tool.delivery_plan(source, source, ["A"], "Light", False)
    target = target_font(world)
    jobs = tool.delivery_plan(source, target, ["A"], "Light", False)
    with pytest.raises(ValueError, match="destination Font window"):
        tool.deliver(target, jobs, False)
    assert not world.history


def test_creation_never_targets_the_active_destination_glyph(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    target = target_font(world)
    source.fgId, target.fgId = 7007, 8100
    active = fakes.Glyph(
        "untouched", {"Light": {"width": 999}, "Black": {"width": 999}}
    )
    target.glyphs[active.name] = active
    world.native.flWorkspace.instance().activeGlyph = lambda: active
    jobs = tool.delivery_plan(source, target, ["A"], "Light", False)
    world.package = target
    calls = []

    def strict(command: str, **kwargs: Any) -> dict[str, Any]:
        assert kwargs.get("glyph_name") == "A", (
            "An unnamed request targets the active glyph"
        )
        assert kwargs["font_id"] == target.fgId, "fontpr uses fgId, not object id"
        calls.append(kwargs)
        data = kwargs["glyph_data"]
        made = fakes.Glyph(
            "A", {x["name"]: {"width": x["advanceWidth"]} for x in data["layers"]}
        )
        made.metricsLeft = made.metricsRight = made.metricsWidth = ""
        target.glyphs["A"] = made
        target.fgPackage.append(NS(name="A", unicodes=[65]))
        return {"status": "ok", "created": True}

    monkeypatch.setattr(sys.modules["fly"].pr, "call", strict)
    monkeypatch.setitem(sys.modules, "fontpr", NS(call=strict))
    tool.deliver(target, jobs, False)
    assert calls and active.findLayer("Light").advanceWidth == 999


@pytest.mark.parametrize("hint", ["hasHints", "hasTTH"])
@pytest.mark.parametrize("kind", ["anchors", "metrics", "components"])
def test_hints_do_not_keep_non_outline_master_operations(
    world: Any, hint: str, kind: str
) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    for layer in glyph.layers:
        setattr(layer, hint, True)
    choices = {
        "contours": False,
        "components": False,
        "anchors": False,
        "metrics": False,
    }
    choices[kind] = True
    kept = []
    work = tool.copy_work(
        package, ["A"], "Light", "Bold", tool.Content(**choices), world.facts(), kept
    )
    assert len(work) == 1 and kept == []
    world.app["outline_writer"].apply_work(
        work, "Copy", world.facts(), tool.editor_type()()
    )
    assert len(world.history) == 1
    assert all(getattr(layer, hint) for layer in glyph.layers)


def test_master_kept_glyph_does_not_stop_eligible_glyph(world: Any) -> None:
    tool = load("Master Twins")
    package, glyph, _ = seed(world)
    blocked = Glyph("locked", {"Light": {}, "Bold": {"locked": True}})
    package.glyphs[blocked.name] = blocked
    kept = []
    work = tool.copy_work(
        package, ["locked", "A"], "Light", "Bold", tool.Content(), world.facts(), kept
    )
    assert [(g.name, layer.name) for g, layer, _ in work] == [("A", "Bold")]
    assert kept == [("locked", "locked layer")]
    world.app["outline_writer"].apply_work(
        work, "Copy", world.facts(), tool.editor_type()()
    )
    assert world.history == [("Copy", [glyph.findLayer("Bold"), glyph])]


@pytest.mark.parametrize("title", ["Master Twins", "Deliver Glyphs"])
@pytest.mark.parametrize(
    "extra",
    [
        "shared",
        "corner_zero",
        "corner_fraction",
        "contour_name",
    ],
)
def test_extra_copy_state_is_a_kept_row(world: Any, title: str, extra: str) -> None:
    source, _glyph, shape = seed(world)
    node, contour = shape.contours[0].nodes()[0], shape.contours[0]
    if extra == "shared":
        shape.shapeData.referenceCount = 2
    elif extra.startswith("corner"):
        node.properties = {"corner_smooth": 0 if extra == "corner_zero" else 0.125}
    elif extra == "contour_name":
        contour.name = "named"
    tool = load(title)
    if title == "Master Twins":
        kept = []
        assert (
            tool.copy_work(
                source, ["A"], "Light", "Bold", tool.Content(), world.facts(), kept
            )
            == []
        )
        assert len(kept) == 1
    else:
        jobs = tool.delivery_plan(source, target_font(world), ["A"], "Light", False)
        assert jobs[0]["note"]
    assert not world.history


def test_delivery_unicode_collision_is_kept_while_other_glyph_copies(
    world: Any,
) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    source.glyphs["B"] = Glyph("B", {"Light": {"width": 410}, "Bold": {"width": 430}})
    source.glyphs["B"].metricsLeft = source.glyphs["B"].metricsRight = source.glyphs[
        "B"
    ].metricsWidth = ""
    source.fgPackage.append(NS(name="B", unicodes=[66]))
    target = target_font(world)
    target.glyphs["A"] = Glyph("A", {"Light": {}, "Black": {}})
    target.glyphs["B"] = Glyph("B", {"Light": {}, "Black": {}})
    target.glyphs["owner"] = Glyph("owner", {"Light": {}, "Black": {}})
    target.fgPackage = [
        NS(name="A", unicodes=[67]),
        NS(name="B", unicodes=[]),
        NS(name="owner", unicodes=[65]),
    ]
    jobs = tool.delivery_plan(source, target, ["A", "B"], "Light", True)
    assert "U+0041" in jobs[0]["note"] and not jobs[1]["note"]
    world.package = target
    result = tool.deliver(target, jobs, False)
    assert result == {"created": 0, "glyphs": 1, "layers": 2, "unicode_changes": []}
    assert target.fgPackage[0].unicodes == [67] and target.fgPackage[1].unicodes == []
    assert target.findName("A").findLayer("Light").advanceWidth == 500
    assert target.findName("B").findLayer("Light").advanceWidth == 410
    assert world.history[0][1][-1].name == "B"


def test_creation_duplicate_unicode_in_source_selection_keeps_later_glyph(
    world: Any,
) -> None:
    tool = load("Deliver Glyphs")
    source, _glyph, _ = seed(world)
    source.glyphs["B"] = Glyph("B", {"Light": {}, "Bold": {}})
    source.glyphs["B"].metricsLeft = source.glyphs["B"].metricsRight = source.glyphs[
        "B"
    ].metricsWidth = ""
    source.fgPackage.append(NS(name="B", unicodes=[65]))
    jobs = tool.delivery_plan(source, target_font(world), ["A", "B"], "Light", False)
    assert not jobs[0]["note"] and "U+0041" in jobs[1]["note"]
    assert [job["name"] for job in jobs if job["unicode_changes"]] == ["A"]


def test_creation_checks_fontpr_status_before_filling(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    target = target_font(world)
    jobs = tool.delivery_plan(source, target, ["A"], "Light", False)
    world.package = target
    monkeypatch.setattr(
        sys.modules["fontpr"],
        "call",
        lambda *a, **k: {"status": "error", "error": "creation refused"},
    )
    with pytest.raises(
        RuntimeError,
        match="did not start: creation refused No glyph was added",
    ):
        tool.deliver(target, jobs, False)
    assert not world.history and target.findName("A") is None


def test_units_per_em_mismatch_refuses_before_delivery(world: Any) -> None:
    source, _, _ = seed(world)
    target = target_font(world)
    target.info.unitsPerEm = 2048
    with pytest.raises(ValueError, match="units per em differ"):
        load("Deliver Glyphs").delivery_plan(source, target, ["A"], "Light", False)
    assert not world.history


def test_no_suffix_does_not_warn_about_unrelated_auto_glyphs(world: Any) -> None:
    source, _, _ = seed(world)
    target = target_font(world)
    target.glyphs["eacute.sc"] = Glyph("eacute.sc", {"Light": {"auto": True}})
    tool = load("Deliver Glyphs")
    jobs = tool.delivery_plan(source, target, ["A"], "Light", False)
    assert tool.rebuild_rows(target, jobs) == {}


def test_master_toggles_reuse_catalogue_and_auto_facts(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed(world)
    counts = {"facts": 0, "catalogue": 0}
    old_scan = world.app["history"].scan_auto_facts

    def scan(package: Any) -> Any:
        counts["facts"] += 1
        return old_scan(package)

    def catalogue() -> Any:
        counts["catalogue"] += 1
        return NS(rows=[("A", "", "")])

    monkeypatch.setattr(world.app["history"], "scan_auto_facts", scan)
    monkeypatch.setattr(world.app["glyph_catalog"], "capture", catalogue)
    panel = load("Master Twins").panel_type()(None)
    assert counts == {"facts": 1, "catalogue": 1}
    panel.all_glyphs.tick(True)
    panel.switches[2].tick(False)
    panel.switches[3].tick(False)
    assert counts == {"facts": 1, "catalogue": 1}
    panel.apply_button.press()
    assert counts["facts"] == counts["catalogue"] == 2


def test_style_empty_tsn_is_visible_and_per_instance_family_is_retained(
    world: Any,
) -> None:
    package, _, _ = seed(world)
    base, bold = instance("Regular", "Separate Family"), instance("Bold")
    base.tfn = bold.tfn = "Per-instance family"
    unnamed = instance("BoldItalic")
    unnamed.tsn = ""
    package.instances = [base, bold, unnamed]
    tool = load("Style Linker")
    rows = tool.link_rows(package.instances)
    assert "missing typographic style" in rows[2][-1]
    assert (
        tool.apply_links(
            package.fgId,
            tool.instance_state(package.instances),
            tool.link_plan(package.instances),
        )
        == 1
    )
    assert [i.tfn for i in package.instances[:2]] == ["Per-instance family"] * 2
    assert [i.sgn for i in package.instances[:2]] == ["Separate Family"] * 2


def test_style_notifies_before_and_after_instance_assignment(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    states = []

    def notify(title: str, objects: list[Any]) -> None:
        assert objects == [package, package.mastersContainer()]
        states.append([(i.sgn, i.slv) for i in package.instances])

    monkeypatch.setattr(world.native.flItems, "notifyChangesApplied", notify)
    tool = load("Style Linker")
    tool.apply_links(
        package.fgId,
        tool.instance_state(package.instances),
        tool.link_plan(package.instances),
    )
    assert states == [[("Family", 0), ("", 0)], [("Family", 0), ("Family", 2)]]
    assert ("UpdateAll", True) in LOG


def test_style_failure_retains_original_values_and_finishes_notifications(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    package, _, _ = seed(world)
    package.instances = [instance("Regular", "Family"), instance("Bold")]
    tool = load("Style Linker")
    before = tool.instance_state(package.instances)
    proposals = tool.link_plan(package.instances)

    def fail(value: Any, bold: bool, italic: bool) -> None:
        raise RuntimeError("instance setter failed")

    monkeypatch.setattr(type(package.instances[1]), "setSLV", fail)
    with pytest.raises(
        RuntimeError,
        match="instance setter failed.*Native changes may remain; use Edit > Undo",
    ):
        tool.apply_links(package.fgId, before, proposals)
    assert tool.instance_state(package.instances) == before
    assert (
        world.history == [("Style Linker", [package, package.mastersContainer()])] * 2
    )


@pytest.mark.parametrize("title", ["Master Twins", "Deliver Glyphs"])
def test_native_copy_fields_are_properties_and_empty_lists(world: Any, title: str) -> None:
    _, _, shape = seed(world)
    contour = shape.contours[0]
    node = contour.nodes()[0]
    node.properties = {"custom": 3.25}
    contour.properties = {"custom": 0}
    assert type(shape.shapeData.referenceCount) is int
    assert not callable(shape.shapeData.referenceCount)
    assert node.getProperties() == contour.getProperties() == []
    tool = load(title)
    if title == "Master Twins":
        assert tool.shape_problem(shape) == ""
    else:
        tool.usable_layer(world.package.findName("A").findLayer("Light"))


def test_delivery_partial_write_has_one_undo_hint(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load("Deliver Glyphs")
    source, _, _ = seed(world)
    target = target_font(world)
    target.glyphs["A"] = Glyph("A", {"Light": {}, "Black": {}})
    target.fgPackage = [NS(name="A", unicodes=[])]
    jobs = tool.delivery_plan(source, target, ["A"], "Light", True)
    world.package = target

    def failure(*args: Any, **kwargs: Any) -> Any:
        raise world.app["history"].PartialWriteError("Deliver Glyphs", [RuntimeError("write failed")])

    monkeypatch.setattr(world.app["outline_writer"], "apply_work", failure)
    with pytest.raises(RuntimeError) as caught:
        tool.deliver(target, jobs, False)
    assert str(caught.value).count("use Edit > Undo") == 1
    assert world.selection_window_ids == [target.id]
