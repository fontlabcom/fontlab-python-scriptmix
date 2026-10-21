# this_file: tests/test_issue122_S8.py
# SPDX-License-Identifier: Apache-2.0
"""Six layer and master scripts, tested against owned fakes and the real App helpers.

Scripts: Masters/Copy Outline To Mask, Copy Layer Between Masters, Restore Backup
Layer, Layer Cleanup, Sync Sidebearings and Cleanup/Empty Layers.

The fakes replace FontLab layers, shapes, the `fontlab` module and Qt widgets.
The real App modules (`history`, `masters`, `metrics_panel`, `edit_guards`)
run over them as `fly.ap.<module>`, like inside FontLab. The tests prove the
planning numbers, the refusal paths, the clone repair and the Undo shape (one
notified list, no auto layer). They do not prove native FontLab behaviour.
"""

import ast
import dataclasses
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
SCRIPTS = {
    "Copy Outline To Mask": "Masters",
    "Copy Layer Between Masters": "Masters",
    "Restore Backup Layer": "Masters",
    "Layer Cleanup": "Masters",
    "Sync Sidebearings": "Masters",
    "Empty Layers": "Cleanup",
}
SOURCES = {
    "Copy Outline To Mask": "masters_copy_to_mask.py",
    "Copy Layer Between Masters": "masters_copy_layer.py",
    "Restore Backup Layer": "masters_restore_backup.py",
    "Layer Cleanup": "masters_layer_cleanup.py",
    "Sync Sidebearings": "masters_sync_metrics.py",
    "Empty Layers": "cleanup_empty_layers.py",
}
PANELS = ["Copy Outline To Mask", "Copy Layer Between Masters", "Restore Backup Layer", "Layer Cleanup"]
LOG: list[tuple[str, Any]] = []  # ordered ("init" | "edit" | "notify" | "stamp", detail)
STAMP = "UTC-stamp"
IDS = itertools.count(1000)
SELECTED = 0x0020


def path_of(title: str) -> Path:
    return ROOT / "Scripts" / SCRIPTS[title] / f"{title}.py"


def load(title: str) -> ModuleType:
    """Execute one script file as a fresh module; leave no .pyc and no sys.modules entry."""
    spec = importlib.util.spec_from_file_location("s8_" + title.replace(" ", "_"), path_of(title))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
        sys.modules.pop(spec.name, None)
    return module


# ---------------------------------------------------------------- Qt fakes
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

    SIGNALS = frozenset({"valueChanged", "currentIndexChanged", "toggled", "clicked", "finished", "itemChanged"})
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
        pass


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
        return [self.cells[row, c].text for c in sorted(c for r, c in self.cells if r == row)]

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
    def __init__(self, m11: float = 1, m12: float = 0, m21: float = 0, m22: float = 1, dx: float = 0, dy: float = 0):
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
            Node(x, y, names[i] if i < len(names) else "", states[i] if i < len(states) else 0)
            for i, (x, y) in enumerate(points)
        ]

    def nodes(self) -> list[Node]:
        return list(self._nodes)


def square(left: float, bottom: float, right: float, top: float, **kw: Any) -> Contour:
    return Contour([(left, bottom), (right, bottom), (right, top), (left, top)], **kw)


class Shape:
    """Fake flShape. clone() loses what FontLab's clone loses (fl#8516, fl#8538)."""

    def __init__(self, contours: Any = (), component: str | None = None, note: str = "", name: str = "") -> None:
        self.id = next(IDS)
        self.isComponent = component is not None
        self.shapeData = NS(note=note, name=name, componentGlyph=component or "", builder=NS(builds=component or ""))
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
    def __init__(self, name: str, glyph: Any = None, *, shapes: Any = (), anchors: Any = (), width: float = 500, **flags: Any):
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
        points = [(n.x, n.y) for s in self.shapes if not s.isComponent for c in s.contours for n in c.nodes()]
        if not points:
            return Box(0, 0, 0, 0)
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        return Box(min(xs), min(ys), max(xs), max(ys))

    def getMaskLayer(self, create: bool) -> Any:
        name = "mask." + self.name
        found = next((x for x in self.glyph.layers if x.name == name), None) if self.glyph else None
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
    def __init__(self, name: str, layers: dict[str, dict[str, Any]] | None = None) -> None:
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
    def __init__(self, glyphs: list[Glyph], masters: tuple[str, ...] = ("Light", "Bold"), ident: int = 7) -> None:
        self.id, self.masters, self.master = ident, list(masters), masters[0]
        self.glyphs = {g.name: g for g in glyphs}
        self.isNull = False

    def findName(self, name: str) -> Glyph | None:
        return self.glyphs.get(name)

    def records(self) -> tuple:
        return tuple(
            (g.name, bool(x.autoLayer), tuple(s.shapeData.componentGlyph for s in x.shapes if s.isComponent))
            for g in self.glyphs.values()
            for x in g.layers
        )


class World:
    def __init__(self) -> None:
        self.package: Package | None = None
        self.selection: list[str] = []
        self.history: list[tuple[str, list[Any]]] = []
        self.flags: list[tuple[Any, ...]] = []  # extra notify arguments (deep history flag)
        self.updates: list[Any] = []
        self.closed: list[str] = []
        self.shown: list[Any] = []

    def notifications(self) -> list[tuple[str, list[Any]]]:
        return list(self.history)

    def use(self, glyphs: list[Glyph], masters: tuple[str, ...] = ("Light", "Bold"), selection: list[str] | None = None) -> Package:
        self.package = Package(glyphs, masters)
        self.selection = [g.name for g in glyphs] if selection is None else selection
        return self.package

    def facts(self) -> Any:
        return self.app["history"].scan_auto_facts(self.package)


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch, real_app: Any) -> World:
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
    fontlab.flGlyph = NS(updatedFgGlyphs=lambda: list(state.updates))
    ap.fontlab = fontlab
    scripting.current_package = lambda expected_id=None: state.package
    scripting.names_selected_names = lambda: list(state.selection)
    scripting.names_font_glyphs = lambda: [(n, []) for n in (state.package.glyphs if state.package else [])]

    def connect_guarded(dialog: Any, signal: Any, callback: Any) -> None:
        def guarded(*args: Any) -> None:
            try:
                callback(*args)
            except Exception as error:  # noqa: BLE001
                dialog.status.setText("Error: " + repr(error))

        signal.connect(guarded)
        dialog._connections.append((signal, guarded))

    scripting.connect_guarded = connect_guarded
    scripting.close_script_dialog = lambda dialog, event, key, **kw: state.closed.append(key)

    def show_script_dialog(dialog_type: Any, key: str) -> Any:
        dialog = dialog_type(None)
        state.shown.append((key, dialog))
        return dialog

    scripting.show_script_dialog = show_script_dialog
    completion.install = lambda dialog, key: ("completion", key)
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
                "current_package", "names_selected_names", "names_font_glyphs",
                "connect_guarded", "close_script_dialog", "show_script_dialog",
            )
        },
        completion=completion.install,
        modules=["guides", "history", "masters", "edit_guards", "metrics_panel"],
    )
    monkeypatch.setattr(state.app["guides"], "dependency_values", lambda package: package.records())
    ap.scripting = state.app["scripting"]
    return state


def label(obj: Any) -> str:
    """Name a notified object: layers and glyphs by name, retained component objects by kind."""
    if isinstance(obj, Shape):
        return "shape:" + obj.shapeData.componentGlyph
    if hasattr(obj, "componentGlyph"):
        return "data:" + obj.componentGlyph
    if hasattr(obj, "builds"):
        return "builder:" + obj.builds
    return str(obj.name)


def notified_names(world: World) -> list[list[str]]:
    return [[label(x) for x in objects] for _, objects in world.notifications()]


def contours_of(layer: Layer) -> int:
    return sum(len(s.contours) for s in layer.shapes if not s.isComponent)


# ---------------------------------------------------------------- generic checks
@pytest.mark.parametrize("title", list(SCRIPTS))
def test_script_when_parsed_then_py311_typed_headed_and_documented(title: str) -> None:
    text = path_of(title).read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    folder = SCRIPTS[title]
    assert text.startswith(
        f"# this_file: Scripts/{folder}/{title}.py\n# SPDX-License-Identifier: Apache-2.0\n"
    ), "header"
    doc = ast.get_docstring(tree) or ""
    for part in ("What it does", "How it works", "Why this design", "How to use", "Benefit", "Credit"):
        assert part in doc, f"{title}: docstring lacks {part!r}"
    assert "the author's own FontLab sample, Apache-2.0" in doc, title
    for word in ("issue 122", "D22", "S8", "reviewed App", "fragment"):
        assert word not in text, f"{title}: internal wording {word!r}"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            assert node.returns is not None, f"{title}.{node.name}: return type"
            for arg in node.args.args + node.args.kwonlyargs:
                assert arg.arg in {"self", "cls"} or arg.annotation is not None, f"{title}.{node.name}.{arg.arg}"


@pytest.mark.parametrize("title", list(SCRIPTS))
def test_script_when_imported_then_no_fly_at_module_level_except_metrics_panel(title: str) -> None:
    tree = ast.parse(path_of(title).read_text())
    top = [n for n in tree.body if isinstance(n, ast.Import | ast.ImportFrom)]
    flies = [
        n for n in top
        if (isinstance(n, ast.ImportFrom) and (n.module or "").startswith("fly"))
        or (isinstance(n, ast.Import) and any(a.name.startswith("fly") for a in n.names))
    ]  # fmt: skip
    if title == "Sync Sidebearings":
        assert flies, "the metrics panel subclass binds fly at import"
    else:
        assert not flies, f"{title}: fly import must stay inside functions"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "fly.ap":
            raise AssertionError(f"{title}: use 'import fly.ap.<module> as <module>'")


@pytest.mark.parametrize("title", list(SCRIPTS))
def test_panel_attributes_when_assigned_then_never_shadow_native_members(title: str) -> None:
    tree = ast.parse(path_of(title).read_text())
    assigned = {
        n.attr for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
        and isinstance(n.value, ast.Name) and n.value.id == "self"
    }  # fmt: skip
    methods = {
        f.name for c in ast.walk(tree) if isinstance(c, ast.ClassDef) and "Panel" in c.name or (
            isinstance(c, ast.ClassDef) and c.name == "SyncSidebearings")
        for f in getattr(c, "body", []) if isinstance(f, ast.FunctionDef)
    }  # fmt: skip
    assert not (assigned | methods) & NATIVE_MEMBERS, (assigned | methods) & NATIVE_MEMBERS


def test_scripts_when_checked_then_real_app_names_exist() -> None:
    used = app_names_used([path_of(t) for t in SCRIPTS])
    assert "fly.ap.history" in used and {"commit", "scan_auto_facts", "refusal"} <= used["fly.ap.history"]
    assert "associated_master" in used["fly.ap.masters"]
    assert {"panel_type", "survey", "make_plan", "unit", "ink_edges"} <= used["fly.ap.metrics_panel"]
    check_real_app_names(used)


@pytest.mark.parametrize("title", list(SCRIPTS))
def test_import_when_loaded_then_nothing_opens_and_no_write(world: World, title: str) -> None:
    load(title)
    assert Widget.registry == [] and world.notifications() == [] and LOG == []


def test_back_up_master_layers_when_checked_then_not_ported_as_duplicate() -> None:
    assert not (ROOT / "Scripts/Masters/Back Up Master Layers.py").exists()
    assert (ROOT / "Scripts/Masters/Duplicate Current Layer.py").exists()
    assert not (ROOT / "Scripts/Guides/Suggest Zones From Overshoots.py").exists()


# ---------------------------------------------------------------- shared clone repair
@pytest.mark.parametrize("title", ["Copy Outline To Mask", "Copy Layer Between Masters", "Restore Backup Layer"])
def test_clone_shape_when_cloned_then_note_name_node_state_restored_selection_cleared(world: World, title: str) -> None:
    module = load(title)
    old = Shape([square(0, 0, 10, 10, names=["a", "", "", "d"], states=[SELECTED | 0x3, 0x1, 0, 0])],
                note="keep", name="bowl")
    new = module.clone_shape(old)
    assert (new.shapeData.note, new.shapeData.name) == ("keep", "bowl")
    nodes = new.contours[0].nodes()
    assert [n.name for n in nodes] == ["a", "", "", "d"]
    assert [n.nodeState for n in nodes] == [0x3, 0x1, 0, 0], "raw state kept, selection bit cleared"
    assert new is not old and nodes[0] is not old.contours[0].nodes()[0]


@pytest.mark.parametrize("title", ["Copy Outline To Mask", "Copy Layer Between Masters", "Restore Backup Layer"])
def test_clone_shape_when_fontlab_drops_a_contour_then_runtime_error(world: World, title: str) -> None:
    module = load(title)
    old = Shape([square(0, 0, 10, 10), square(20, 0, 30, 10)])
    old.drop_contour = True
    with pytest.raises(RuntimeError, match="contour count"):
        module.clone_shape(old)


# ---------------------------------------------------------------- Copy Outline To Mask
def mask_font(world: World) -> Package:
    a = Glyph("a", {
        "Light": {"shapes": [Shape([square(0, 0, 100, 100), square(10, 10, 20, 20)]), Shape(component="b")]},
        "Bold": {"shapes": [Shape([square(0, 0, 120, 100)])]},
        "mask.Light": {"shapes": [Shape([square(0, 0, 5, 5)])]},
    })
    b = Glyph("b", {"Light": {"shapes": [Shape(component="c")]}, "Bold": {}})
    c = Glyph("c", {"Light": {"shapes": [Shape([square(0, 0, 50, 50)])], "locked": True}, "Bold": {"auto": True}})
    return world.use([a, b, c])


def test_mask_survey_when_replace_then_counts_and_notes_exact(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    rows = module.survey(package, ["a", "b", "c"], ["Light", "Bold"], True, world.facts())
    table = [(r.glyph.name, r.master, r.outline, r.mask_now, r.mask_after, r.note) for r in rows]
    assert table == [
        ("a", "Light", 2, 1, 2, ""),
        ("a", "Bold", 1, 0, 1, ""),
        ("b", "Light", 0, 0, 0, "no outline (skipped)"),
        ("b", "Bold", 0, 0, 0, "no outline (skipped)"),
        ("c", "Light", 0, 0, 0, "has auto layers (skipped)"),
        ("c", "Bold", 0, 0, 0, "auto layer (skipped)"),
    ]


def test_mask_survey_when_add_then_after_adds_existing(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    rows = module.survey(package, ["a"], ["Light"], False, world.facts())
    assert (rows[0].outline, rows[0].mask_now, rows[0].mask_after) == (2, 1, 3)


def test_mask_survey_when_mask_holds_component_then_counted_and_shown(world: World) -> None:
    module = load("Copy Outline To Mask")
    g = Glyph("g", {
        "Light": {"shapes": [Shape([square(0, 0, 9, 9)])]},
        "mask.Light": {"shapes": [Shape([square(0, 0, 1, 1)]), Shape(component="h")]},
    })
    world.use([g], ("Light",))
    row = module.survey(world.package, ["g"], ["Light"], True, world.facts())[0]
    assert (row.mask_now, row.mask_components, row.mask_after) == (1, 1, 1)
    panel = module.panel_type()(None)
    assert panel.table.texts(0) == ["g · Light", "1", "1 + 1 component", "1"]


def test_mask_survey_when_locked_or_missing_then_note(world: World) -> None:
    module = load("Copy Outline To Mask")
    d = Glyph("d", {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])], "locked": True}})
    package = world.use([d])
    rows = module.survey(package, ["d", "zz"], ["Light", "Bold"], True, world.facts())
    assert [(r.glyph.name, r.master, r.note) for r in rows] == [
        ("d", "Light", "locked layer (skipped)"),
        ("d", "Bold", "no layer in this master"),
    ]


def test_copy_to_masks_when_applied_then_one_step_masks_created_and_read_back(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    facts = world.facts()
    rows = module.survey(package, ["a", "b"], ["Light", "Bold"], True, facts)
    result = module.copy_to_masks(rows, True, facts)
    a = package.findName("a")
    assert result == {"layers": 2, "glyphs": 1, "contours": 3, "created": 1, "mismatches": []}
    assert contours_of(a.layer("mask.Light")) == 2 and contours_of(a.layer("mask.Bold")) == 1
    assert notified_names(world) == [["mask.Light", "mask.Bold", "a"]], "existing mask, created mask, glyph"
    assert [e for e in LOG if e[0] == "notify"] == [("notify", "Copy Outline To Mask")]
    assert LOG.index(("init", "mask.Light")) < LOG.index(("edit", ("removeShape", "mask.Light")))
    assert not any(e[1][0] == "removeAllShapes" for e in LOG if e[0] == "edit"), "never removeAllShapes"
    assert world.flags == [()], "no mask component removed: the two-argument call"
    assert all(not s.isComponent for s in a.layer("mask.Light").shapes), "components are not copied"
    assert a.layer("Light").shapes[0].contours[0].nodes()[0].x == 0, "the body outline is untouched"


def test_copy_to_masks_when_replace_removes_mask_component_then_retained_first_and_deep(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    a = package.findName("a")
    accent = Shape(component="acute")
    a.layer("mask.Light").shapes.append(accent)
    facts = world.facts()
    rows = module.survey(package, ["a"], ["Light"], True, facts)
    result = module.copy_to_masks(rows, True, facts)
    assert result["mismatches"] == [] and a.layer("mask.Light").shapes[-1] is not accent
    assert notified_names(world) == [["shape:acute", "data:acute", "builder:acute", "mask.Light", "a"]]
    objects = world.notifications()[0][1]
    assert objects[:3] == [accent, accent.shapeData, accent.shapeData.builder], "the removed objects themselves"
    assert world.flags == [(True,)], "retained objects use the deep history call"
    removals = [i for i, e in enumerate(LOG) if e == ("edit", ("removeShape", "mask.Light"))]
    assert len(removals) == 2 and LOG.index(("init", "mask.Light")) < removals[0], "one removeShape per shape"


def test_copy_to_masks_when_mask_component_survives_then_mismatch(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    mask = package.findName("a").layer("mask.Light")
    mask.shapes.append(Shape(component="acute"))
    mask.keep_components = True
    facts = world.facts()
    rows = module.survey(package, ["a"], ["Light"], True, facts)
    result = module.copy_to_masks(rows, True, facts)
    assert result["mismatches"] == ["a · Light: mask still has 1 component(s), planned 0"]


def test_copy_to_masks_when_add_mode_then_existing_mask_kept(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    facts = world.facts()
    rows = module.survey(package, ["a"], ["Light"], False, facts)
    result = module.copy_to_masks(rows, False, facts)
    assert result["contours"] == 2 and result["created"] == 0
    assert contours_of(package.findName("a").layer("mask.Light")) == 3
    assert ("edit", ("removeShape", "mask.Light")) not in LOG


def test_copy_to_masks_when_nothing_to_do_then_no_history(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    facts = world.facts()
    rows = module.survey(package, ["b"], ["Light"], True, facts)
    assert module.copy_to_masks(rows, True, facts)["layers"] == 0
    assert world.notifications() == [] and LOG == []


def test_copy_to_masks_when_pending_updates_then_refused_before_history(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    facts = world.facts()
    rows = module.survey(package, ["a"], ["Light"], True, facts)
    world.updates = [1]
    with pytest.raises(ValueError, match="pending"):
        module.copy_to_masks(rows, True, facts)
    assert LOG == [] and world.notifications() == []


def test_copy_to_masks_when_mask_update_fails_then_partial_write_error_after_notify(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    package.findName("a").layer("mask.Light").update_ok = False
    facts = world.facts()
    rows = module.survey(package, ["a"], ["Light"], True, facts)
    with pytest.raises(RuntimeError, match="Edit > Undo"):
        module.copy_to_masks(rows, True, facts)
    assert len(world.notifications()) == 1


def test_copy_to_masks_when_fontlab_keeps_old_mask_then_mismatch_reported(world: World) -> None:
    module = load("Copy Outline To Mask")
    package = mask_font(world)
    package.findName("a").layer("mask.Light").stubborn = True
    facts = world.facts()
    rows = module.survey(package, ["a"], ["Light"], True, facts)
    result = module.copy_to_masks(rows, True, facts)
    assert result["mismatches"] == ["a · Light: mask has 0 contours, planned 2"]


def test_mask_panel_when_opened_then_preview_and_copy_runs_once(world: World) -> None:
    module = load("Copy Outline To Mask")
    mask_font(world)
    panel = module.panel_type()(None)
    assert panel.table.all_texts() == [
        ["a · Light", "2", "1", "2"],
        ["b · Light", "no outline (skipped)"],
        ["c · Light", "has auto layers (skipped)"],
    ], "current master only"
    panel.scope.pick(1)
    assert panel.table.texts(1) == ["a · Bold", "1", "0", "1"]
    assert panel.apply_button.isEnabled()
    panel.apply_button.press()
    assert panel.status.text.startswith("Copied 3 contours into 2 masks of 1 glyph")
    assert len(world.notifications()) == 1


def test_mask_panel_when_no_font_then_message_and_disabled(world: World) -> None:
    module = load("Copy Outline To Mask")
    panel = module.panel_type()(None)
    assert "Open a font" in panel.subtitle.text and not panel.apply_button.isEnabled()
    panel.close_button.press()
    assert world.closed == ["masters_copy_to_mask"]


def test_mask_panel_when_font_switched_then_apply_refused(world: World) -> None:
    module = load("Copy Outline To Mask")
    mask_font(world)
    panel = module.panel_type()(None)
    world.package.id = 99
    panel.apply_button.press()
    assert "font changed" in panel.status.text.lower() + panel.subtitle.text.lower()
    assert world.notifications() == []


# ---------------------------------------------------------------- Copy Layer Between Masters
def layer_font(world: World) -> Package:
    n = Glyph("n", {
        "Light": {"shapes": [Shape([square(10, 0, 90, 100)], note="stem"), Shape(component="acute")],
                  "anchors": [Pin("top", 50, 120), Pin("bottom", 50, 0)], "width": 100},
        "Bold": {"shapes": [Shape([square(5, 0, 115, 100), square(30, 20, 40, 30)]), Shape([]), Shape(component="acute")],
                 "anchors": [Pin("top", 60, 120)], "width": 120},
        "Black": {"shapes": [Shape([square(0, 0, 130, 100)])], "width": 130, "metricsLeft": "=o"},
    })
    acute = Glyph("acute", {"Light": {"shapes": [Shape([square(0, 0, 10, 10)])]}, "Bold": {}, "Black": {}})
    aacute = Glyph("aacute", {"Light": {"auto": True}, "Bold": {}, "Black": {}})
    aacute.layers[0].shapes = [Shape(component="acute")]
    return world.use([n, acute, aacute], ("Light", "Bold", "Black"))


def test_copy_layer_survey_when_all_targets_then_exact_preview_and_notes(world: World) -> None:
    module = load("Copy Layer Between Masters")
    package = layer_font(world)
    pairs = module.survey(package, ["n", "acute", "zz"], "Light", ["Bold", "Black"], True, True, world.facts())
    table = [(p.glyph.name, p.master, p.contours_now, p.contours_after, p.width_now, p.width_after, p.moves,
              p.missing, p.note) for p in pairs]
    assert table == [
        ("n", "Bold", 2, 1, 120, 100, (("top", 50.0, 120.0),), ("bottom",), ""),
        ("n", "Black", 1, 1, 130, 130, (), (), "metrics link or expression (skipped)"),
        ("acute", "Bold", 0, 0, 500, 500, (), (), "base of auto aacute (skipped)"),
        ("acute", "Black", 0, 0, 500, 500, (), (), "base of auto aacute (skipped)"),
    ]


def test_copy_layer_survey_when_options_off_then_width_and_anchors_kept(world: World) -> None:
    module = load("Copy Layer Between Masters")
    package = layer_font(world)
    pair = module.survey(package, ["n"], "Light", ["Bold"], False, False, world.facts())[0]
    assert (pair.width_after, pair.moves, pair.missing) == (120, (), ())


def test_copy_layer_survey_when_anchor_to_origin_or_duplicate_then_skipped(world: World) -> None:
    module = load("Copy Layer Between Masters")
    g = Glyph("g", {
        "Light": {"shapes": [Shape([square(0, 0, 9, 9)])], "anchors": [Pin("top", 0, 0)]},
        "Bold": {"shapes": [Shape([square(0, 0, 9, 9)])], "anchors": [Pin("top", 4, 4)]},
    })
    h = Glyph("h", {
        "Light": {"shapes": [Shape([square(0, 0, 9, 9)])], "anchors": [Pin("top", 1, 1), Pin("top", 2, 2)]},
        "Bold": {"shapes": [Shape([square(0, 0, 9, 9)])]},
    })
    e = Glyph("e", {"Light": {}, "Bold": {"shapes": [Shape([square(0, 0, 9, 9)])]}})
    package = world.use([g, h, e])
    notes = [p.note for p in module.survey(package, ["g", "h", "e"], "Light", ["Bold"], True, True, world.facts())]
    assert notes == [
        "anchor top would move to 0, 0; FontLab cannot redo it (fl#8527)",
        "several anchors named top (skipped)",
        "source has no outline (skipped)",
    ]


def test_copy_layer_when_applied_then_outline_replaced_anchor_width_one_step(world: World) -> None:
    module = load("Copy Layer Between Masters")
    package = layer_font(world)
    facts = world.facts()
    pairs = module.survey(package, ["n"], "Light", ["Bold"], True, True, facts)
    result = module.copy_pairs(pairs, facts)
    bold = package.findName("n").layer("Bold")
    assert result == {"layers": 1, "glyphs": 1, "contours": 1, "missing": ["bottom"], "mismatches": []}
    outline = [s for s in bold.shapes if not s.isComponent]
    assert len(outline) == 1 and outline[0].shapeData.note == "stem", "old outline shapes and the empty shape go"
    assert [(n.x, n.y) for n in outline[0].contours[0].nodes()][:2] == [(10, 0), (90, 0)]
    assert [s.shapeData.componentGlyph for s in bold.shapes if s.isComponent] == ["acute"], "components stay"
    assert bold.anchors[0].point == Point(50, 120) and bold.advanceWidth == 100
    assert notified_names(world) == [["Bold", "n"]]
    assert LOG.index(("init", "Bold")) < LOG.index(("edit", ("removeShape", "Bold")))
    light = package.findName("n").layer("Light")
    assert outline[0] is not light.shapes[0], "the target gets a copy, never the source shape"


def test_copy_layer_when_width_rejected_then_mismatch(world: World) -> None:
    module = load("Copy Layer Between Masters")
    package = layer_font(world)
    package.findName("n").layer("Bold").stubborn = True
    facts = world.facts()
    pairs = module.survey(package, ["n"], "Light", ["Bold"], True, True, facts)
    result = module.copy_pairs(pairs, facts)
    assert result["mismatches"] == ["n · Bold: 0 contours, planned 1", "n · Bold: width 120, planned 100"]


def test_copy_layer_when_base_forced_into_commit_then_value_error_and_no_history(world: World) -> None:
    module = load("Copy Layer Between Masters")
    package = layer_font(world)
    facts = world.facts()
    pair = module.survey(package, ["acute"], "Light", ["Bold"], True, True, facts)[0]
    forced = dataclasses.replace(pair, note="")
    with pytest.raises(ValueError, match="Refused"):
        module.copy_pairs([forced], facts)
    assert LOG == []


def test_copy_layer_panel_when_opened_then_targets_and_copy(world: World) -> None:
    module = load("Copy Layer Between Masters")
    layer_font(world)
    world.selection = ["n"]
    panel = module.panel_type()(None)
    assert panel.source.items == ["Light", "Bold", "Black"]
    assert panel.target.items == ["All other masters", "Bold", "Black"]
    assert panel.table.texts(0) == ["n · Bold", "2", "1", "120", "100"]
    assert panel.table.texts(1) == ["n · Black", "metrics link or expression (skipped)"]
    panel.source.pick(1)
    assert panel.target.items == ["All other masters", "Light", "Black"]
    panel.source.pick(0)
    panel.target.pick(1)
    assert len(panel.table.all_texts()) == 1
    panel.apply_button.press()
    assert panel.status.text.startswith("Replaced 1 layer in 1 glyph")
    assert "bottom" in panel.status.text


# ---------------------------------------------------------------- Restore Backup Layer
@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Light@ 10:00:00, 21/10/26", "Light"),
        ("Bold@", "Bold"),
        ("Light", None),
        ("Light#bracket", None),
        ("mask.Light@ x", None),
        ("|temp|Light@ x", None),
        ("Medium@ x", None),
        ("Light backup", None),
    ],
)
def test_backup_master_when_name_given_then_only_at_layers_of_a_master(world: World, name: str, expected: Any) -> None:
    module = load("Restore Backup Layer")
    assert module.backup_master(name, ["Light", "Bold"]) == expected


def backup_font(world: World) -> Package:
    stamp = "Light@ 10:00:00, 21/10/26"
    n = Glyph("n", {
        "Light": {"shapes": [Shape([square(0, 0, 50, 50)]), Shape(component="acute")], "anchors": [Pin("top", 9, 9)],
                  "width": 300},
        stamp: {"shapes": [Shape([square(0, 0, 60, 60), square(1, 1, 2, 2)])], "anchors": [Pin("top", 30, 70)],
                "width": 320},
        "mask." + stamp: {"shapes": [Shape([square(0, 0, 1, 1)])]},
        "Bold": {"width": 400},
    })
    o = Glyph("o", {"Light": {"locked": True}, stamp: {"shapes": [Shape([square(0, 0, 5, 5)])]},
                    "Bold@ old": {"shapes": [Shape([square(0, 0, 5, 5)])]}, "Bold": {}})
    v = Glyph("v", {"Light": {}, "Light#alt": {"shapes": [Shape([square(0, 0, 5, 5)])]}})
    return world.use([n, o, v])


def test_backup_names_when_listed_then_sorted_unique_at_layers_only(world: World) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    glyphs = [package.findName(x) for x in ("n", "o", "v")]
    assert module.backup_names(glyphs, package.masters) == ["Bold@ old", "Light@ 10:00:00, 21/10/26"]


def test_restore_survey_when_backup_chosen_then_exact_jobs(world: World) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    jobs = module.survey(package, ["n", "o", "v"], "Light@ 10:00:00, 21/10/26", world.facts())
    table = [(j.glyph.name, j.master, j.contours_now, j.contours_after, j.width_now, j.width_after, j.moves, j.note)
             for j in jobs]
    assert table == [
        ("n", "Light", 1, 2, 300, 320, (("top", 30.0, 70.0),), ""),
        ("o", "Light", 0, 0, 500, 500, (), "locked layer (skipped)"),
        ("v", "", 0, 0, 0, 0, (), "no layer with this name"),
    ]


def test_restore_when_applied_and_delete_then_master_restored_backup_and_its_mask_removed(world: World) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    facts = world.facts()
    stamp = "Light@ 10:00:00, 21/10/26"
    jobs = module.survey(package, ["n"], stamp, facts)
    result = module.restore(jobs, True, facts)
    n = package.findName("n")
    assert result == {"layers": 1, "glyphs": 1, "deleted": 2, "kept": 0, "mismatches": []}
    assert contours_of(n.layer("Light")) == 2 and n.layer("Light").advanceWidth == 320
    assert n.layer("Light").anchors[0].point == Point(30, 70)
    assert [x.name for x in n.layers] == ["Light", "Bold"]
    assert [s.shapeData.componentGlyph for s in n.layer("Light").shapes if s.isComponent] == ["acute"]
    assert notified_names(world) == [["Light", "n"]]
    assert world.flags == [()], "no component removed: the two-argument call"
    removed = [e[1][1] for e in LOG if e[0] == "edit" and e[1][0] == "removeLayer"]
    assert removed == ["mask." + stamp, stamp], "mask first, then the backup"


def test_restore_when_backup_is_shown_then_kept_and_counted(world: World) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    stamp = "Light@ 10:00:00, 21/10/26"
    n = package.findName("n")
    n.active = n.layer(stamp)
    facts = world.facts()
    result = module.restore(module.survey(package, ["n"], stamp, facts), True, facts)
    assert (result["deleted"], result["kept"]) == (0, 1)
    assert stamp in [x.name for x in n.layers]


@pytest.mark.parametrize("locked", ["backup", "mask"])
def test_restore_when_backup_or_its_mask_locked_then_kept_and_counted(world: World, locked: str) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    stamp = "Light@ 10:00:00, 21/10/26"
    n = package.findName("n")
    n.layer(stamp if locked == "backup" else "mask." + stamp).isLocked = True
    facts = world.facts()
    result = module.restore(module.survey(package, ["n"], stamp, facts), True, facts)
    assert (result["layers"], result["deleted"], result["kept"]) == (1, 0, 1)
    assert {stamp, "mask." + stamp} <= {x.name for x in n.layers}


def test_restore_when_deleted_backup_holds_component_then_retained_first_and_deep(world: World) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    stamp = "Light@ 10:00:00, 21/10/26"
    n = package.findName("n")
    accent = Shape(component="grave")
    n.layer(stamp).shapes.append(accent)
    facts = world.facts()
    result = module.restore(module.survey(package, ["n"], stamp, facts), True, facts)
    assert result["deleted"] == 2 and result["mismatches"] == []
    assert notified_names(world) == [["shape:grave", "data:grave", "builder:grave", "Light", "n"]]
    assert world.notifications()[0][1][0] is accent and world.flags == [(True,)]
    assert [s.shapeData.componentGlyph for s in n.layer("Light").shapes if s.isComponent] == ["acute"]


def test_restore_when_removal_ignored_then_mismatch(world: World) -> None:
    module = load("Restore Backup Layer")
    package = backup_font(world)
    package.findName("n").remove_fails = True
    facts = world.facts()
    stamp = "Light@ 10:00:00, 21/10/26"
    result = module.restore(module.survey(package, ["n"], stamp, facts), True, facts)
    assert result["mismatches"] == [f"n: layer '{stamp}' is still there", f"n: layer 'mask.{stamp}' is still there"]


def test_restore_panel_when_opened_then_backups_listed_and_restore_runs(world: World) -> None:
    module = load("Restore Backup Layer")
    backup_font(world)
    panel = module.panel_type()(None)
    assert panel.backup.items == ["Bold@ old", "Light@ 10:00:00, 21/10/26"]
    panel.backup.pick(1)
    assert panel.table.texts(0) == ["n", "Light", "1 → 2", "300 → 320"]
    panel.delete_after.tick(True)
    panel.apply_button.press()
    assert panel.status.text.startswith("Restored 1 master layer in 1 glyph · deleted 2 layers")
    assert panel.backup.items == ["Bold@ old", "Light@ 10:00:00, 21/10/26"], "o still has its backup"


def test_restore_panel_when_no_backup_then_hint(world: World) -> None:
    module = load("Restore Backup Layer")
    world.use([Glyph("x", {"Light": {}, "Bold": {}})])
    panel = module.panel_type()(None)
    assert "Duplicate Current Layer" in panel.status.text and not panel.apply_button.isEnabled()


# ---------------------------------------------------------------- Layer Cleanup
@pytest.mark.parametrize(
    ("name", "flags", "expected"),
    [
        ("Light", {}, None),
        ("light", {}, None),
        ("mask.Light", {}, "mask"),
        ("Light@ 10:00", {}, "backup"),
        ("Light#bracket", {}, "alternate"),
        ("Sketch", {}, "other"),
        ("Medium@ x", {}, "other"),
        ("|temp|Light", {}, None),
        ("svc", {"service": True}, None),
        ("pic", {"image": True}, None),
    ],
)
def test_kind_when_layer_given_then_class_or_none(world: World, name: str, flags: dict, expected: Any) -> None:
    module = load("Layer Cleanup")
    assert module.kind(Layer(name, **flags), ["Light", "Bold"]) == expected


def cleanup_font(world: World) -> Package:
    a = Glyph("a", {
        "Light": {}, "Bold": {}, "mask.Light": {"shapes": [Shape([square(0, 0, 1, 1)])]},
        "Light@ 1": {"shapes": [Shape([square(0, 0, 1, 1), square(2, 2, 3, 3)])]},
        "Sketch": {"locked": True}, "Light#alt": {},
    })
    b = Glyph("b", {"Light": {}, "Bold@ x": {}})
    b.active = b.layer("Bold@ x")
    c = Glyph("c", {"Light": {}, "Old": {}})
    cc = Glyph("ccedilla", {"Light": {"auto": True}})
    cc.layers[0].shapes = [Shape(component="c")]
    return world.use([a, b, c, cc])


def test_cleanup_survey_when_listed_then_kinds_counts_notes_exact(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    entries = module.survey(package, ["a", "b", "c", "ccedilla"], package.masters, world.facts())
    table = [(e.glyph.name, e.name, e.kind, e.contours, e.note) for e in entries]
    assert table == [
        ("a", "mask.Light", "mask", 1, ""),
        ("a", "Light@ 1", "backup", 2, ""),
        ("a", "Sketch", "other", 0, "locked layer (kept)"),
        ("a", "Light#alt", "alternate", 0, ""),
        ("b", "Bold@ x", "backup", 0, "shown layer (kept)"),
        ("c", "Old", "other", 0, "base of auto ccedilla (kept)"),
    ]


def test_delete_layers_when_applied_then_one_step_and_ids_gone(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    facts = world.facts()
    entries = module.survey(package, ["a"], package.masters, facts)
    doomed = [e for e in entries if e.kind in {"mask", "backup"}]
    result = module.delete_layers(doomed, package.masters, facts)
    assert result == {"layers": 2, "glyphs": 1, "deleted": ["a/mask.Light", "a/Light@ 1"], "mismatches": []}
    assert [x.name for x in package.findName("a").layers] == ["Light", "Bold", "Sketch", "Light#alt"]
    assert notified_names(world) == [["Light", "a"]], "a surviving body layer carries the Undo step"
    assert world.flags == [()], "no component removed: the two-argument call"
    assert LOG[:2] == [("init", "Light"), ("init", "a")]


def test_undo_layers_when_mask_or_plain_layer_deleted_then_foreground_else_first_master(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    a = package.findName("a")
    pick = module.undo_layers
    assert [x.name for x in pick(a, {int(a.layer("mask.Light").id)}, package.masters)] == ["Light"]
    assert [x.name for x in pick(a, {int(a.layer("Sketch").id)}, package.masters)] == ["Light"]
    assert [x.name for x in pick(a, {int(a.layer("Light").id)}, package.masters)] == ["Bold"]
    lone = Glyph("lone", {"Spare": {}})
    with pytest.raises(ValueError, match="no layer left"):
        pick(lone, {int(lone.layer("Spare").id)}, package.masters)


def test_delete_layers_when_a_kept_row_is_given_then_value_error_before_history(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    facts = world.facts()
    entries = module.survey(package, ["b"], package.masters, facts)
    with pytest.raises(ValueError, match="shown layer"):
        module.delete_layers(entries, package.masters, facts)
    assert LOG == []


def test_delete_layers_when_deleted_layer_holds_component_then_retained_first_and_deep(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    a = package.findName("a")
    accent = Shape(component="b")
    a.layer("Light@ 1").shapes.append(accent)
    facts = world.facts()
    entries = [e for e in module.survey(package, ["a"], package.masters, facts) if e.kind == "backup"]
    result = module.delete_layers(entries, package.masters, facts)
    assert result["deleted"] == ["a/Light@ 1"] and result["mismatches"] == []
    assert notified_names(world) == [["shape:b", "data:b", "builder:b", "Light", "a"]]
    assert world.notifications()[0][1][0] is accent and world.flags == [(True,)]


def test_delete_layers_when_removal_ignored_then_mismatch(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    package.findName("a").remove_fails = True
    facts = world.facts()
    entries = [e for e in module.survey(package, ["a"], package.masters, facts) if e.kind == "mask"]
    result = module.delete_layers(entries, package.masters, facts)
    assert result["mismatches"] == ["a: layer 'mask.Light' is still there"]


def test_cleanup_panel_when_kind_ticked_then_delete_ticked_only(world: World) -> None:
    module = load("Layer Cleanup")
    package = cleanup_font(world)
    panel = module.panel_type()(None)
    assert panel.table.texts(0) == ["a", "mask.Light", "mask", "1"]
    assert panel.table.texts(2) == ["a", "Sketch", "other", "locked layer (kept)"]
    assert not panel.apply_button.isEnabled()
    panel.kind_buttons["backup"].press()
    assert panel.status.text.startswith("6 extra layers · 1 ticked")
    panel.apply_button.press()
    assert "Light@ 1" not in [x.name for x in package.findName("a").layers]
    assert panel.status.text.startswith("Deleted 1 layer from 1 glyph")
    panel.kind_buttons["none"].press()
    assert not panel.apply_button.isEnabled()


# ---------------------------------------------------------------- Sync Sidebearings
def test_target_sidebearings_when_proportional_or_same_then_exact_half_up(world: World) -> None:
    module = load("Sync Sidebearings")
    assert module.target_sidebearings((100, 500), 600, (80, 680), True) == (150, 150)
    assert module.target_sidebearings((100, 500), 600, (80, 680), False) == (100, 100)
    assert module.target_sidebearings((35, 435), 470, (0, 600), True) == (53, 53), "52.5 rounds half up"


def sync_font(world: World) -> Package:
    n = Glyph("n", {"Light": {"shapes": [Shape([square(100, 0, 500, 100)])], "width": 600},
                    "Bold": {"shapes": [Shape([square(80, 0, 680, 100)])], "width": 700}})
    e = Glyph("e", {"Light": {}, "Bold": {"shapes": [Shape([square(0, 0, 10, 10)])]}})
    o = Glyph("o", {"Light": {"shapes": [Shape([square(35, 0, 435, 100)])], "width": 470},
                    "Bold": {"shapes": [Shape([square(0, 0, 600, 100)])], "width": 600}})
    return world.use([n, e, o])


def test_sync_panel_when_opened_then_all_other_masters_and_exact_preview(world: World) -> None:
    module = load("Sync Sidebearings")
    sync_font(world)
    panel = module.SyncSidebearings(None)
    assert panel.reference.items == ["Light", "Bold"] and panel.scope.currentIndex == 1
    assert panel.table.all_texts() == [
        ["n · Bold", "80", "20", "150", "150"],
        ["e · Bold", "reference has no outline"],
        ["o · Bold", "0", "0", "53", "53"],
    ]
    panel.rule.pick(1)
    assert panel.table.texts(0) == ["n · Bold", "80", "20", "100", "100"]


def test_sync_panel_when_applied_then_shift_and_width_one_step(world: World) -> None:
    module = load("Sync Sidebearings")
    package = sync_font(world)
    panel = module.SyncSidebearings(None)
    panel.apply_button.press()
    n, o = package.findName("n").layer("Bold"), package.findName("o").layer("Bold")
    assert (n.boundingBox.x(), n.advanceWidth) == (150, 900)
    assert (o.boundingBox.x(), o.advanceWidth) == (53, 706)
    assert notified_names(world) == [["Bold", "Bold", "n", "o"]]
    assert package.findName("n").layer("Light").advanceWidth == 600, "the reference stays"
    assert panel.status.text.startswith("Changed 2 layers in 2 glyphs")


def test_sync_panel_when_reference_is_the_only_target_then_nothing_to_change(world: World) -> None:
    module = load("Sync Sidebearings")
    sync_font(world)
    panel = module.SyncSidebearings(None)
    panel.scope.pick(0)
    assert "reference" in panel.subtitle.text.lower() and not panel.apply_button.isEnabled()


def test_sync_panel_when_reference_layer_missing_then_note(world: World) -> None:
    module = load("Sync Sidebearings")
    world.use([Glyph("z", {"Bold": {"shapes": [Shape([square(0, 0, 10, 10)])]}})])
    panel = module.SyncSidebearings(None)
    assert panel.table.all_texts() == [["z · Bold", "no layer in the reference master"]]


def test_sync_main_when_called_then_registry_gets_panel(world: World) -> None:
    module = load("Sync Sidebearings")
    sync_font(world)
    module.main()
    assert world.shown[0][0] == "masters_sync_metrics"


# ---------------------------------------------------------------- Empty Layers
def empty_font(world: World) -> Package:
    a = Glyph("a", {
        "Light": {}, "Bold": {}, "Spare": {}, "Kept": {"note": "idea"}, "Guide": {"guidelines": [1]},
        "mask.Light": {}, "Img": {"image": True}, "Light@ 1": {}, "WithMask": {},
    })
    a.layers.append(Layer("mask.WithMask", a, shapes=[Shape([square(0, 0, 1, 1)])]))
    b = Glyph("b", {"Light": {}, "Empty": {}})
    b.active = b.layer("Empty")
    c = Glyph("c", {"Light": {}, "Spare": {}})
    cc = Glyph("ccedilla", {"Light": {"auto": True}, "Spare": {}})
    cc.layers[0].shapes = [Shape(component="c")]
    return world.use([a, b, c, cc])


def test_is_empty_auxiliary_when_data_or_role_then_false(world: World) -> None:
    module = load("Empty Layers")
    package = empty_font(world)
    a = package.findName("a")
    result = {x.name: module.is_empty_auxiliary(x, package.masters) for x in a.layers}
    assert result == {
        "Light": False, "Bold": False, "Spare": True, "Kept": False, "Guide": False, "mask.Light": False,
        "Img": False, "Light@ 1": True, "WithMask": False, "mask.WithMask": False,
    }


@pytest.mark.parametrize("field", ["anchors", "guidelines", "note", "lib"])
def test_is_empty_auxiliary_when_mask_holds_data_then_layer_kept(world: World, field: str) -> None:
    module = load("Empty Layers")
    package = empty_font(world)
    a = package.findName("a")
    mask = Layer("mask.Spare", a)
    a.layers.append(mask)
    assert module.is_empty_auxiliary(a.layer("Spare"), package.masters), "an empty mask does not keep the layer"
    setattr(mask, field, [Pin("top", 1, 1)] if field == "anchors" else "x")
    assert not module.is_empty_auxiliary(a.layer("Spare"), package.masters), f"mask {field} is content"
    jobs, _ = module.plan(package, ["a"], world.facts())
    assert [x.name for _, x in jobs] == ["Light@ 1"]


def test_plan_when_selection_then_jobs_and_skips_exact(world: World) -> None:
    module = load("Empty Layers")
    package = empty_font(world)
    jobs, skipped = module.plan(package, ["a", "b", "c", "ccedilla"], world.facts())
    assert [(g.name, x.name) for g, x in jobs] == [("a", "Spare"), ("a", "Light@ 1")]
    assert skipped == ["b/Empty: shown layer", "c: base of auto ccedilla", "ccedilla: has auto layers"]


def test_run_when_called_then_one_step_and_message(world: World) -> None:
    module = load("Empty Layers")
    package = empty_font(world)
    world.selection = ["a", "c"]
    text = module.run()
    assert text == "Deleted 2 empty layers from 1 glyph: a/Spare, a/Light@ 1. Skipped 1: c: base of auto ccedilla."
    assert [x.name for x in package.findName("a").layers if x.name in {"Spare", "Light@ 1"}] == []
    assert notified_names(world) == [["Light", "a"]], "a surviving master layer carries the Undo step"
    assert world.flags == [()], "empty layers hold no component: the two-argument call"


def test_plan_when_layer_or_its_mask_locked_then_skipped(world: World) -> None:
    module = load("Empty Layers")
    package = empty_font(world)
    a = package.findName("a")
    a.layer("Spare").isLocked = True
    a.layers.append(Layer("mask.Light@ 1", a, locked=True))
    jobs, skipped = module.plan(package, ["a"], world.facts())
    assert jobs == []
    assert skipped == ["a/Spare: locked layer", "a/Light@ 1: locked layer"]


def test_remove_when_layer_has_empty_mask_then_mask_first_and_read_back(world: World) -> None:
    module = load("Empty Layers")
    package = empty_font(world)
    a = package.findName("a")
    a.layers.append(Layer("mask.Spare", a))
    facts = world.facts()
    jobs, _ = module.plan(package, ["a"], facts)
    assert [x.name for _, x in jobs] == ["Spare", "Light@ 1"], "the empty mask is not a job of its own"
    assert module.remove(jobs, package.masters, facts) == []
    removed = [e[1][1] for e in LOG if e[0] == "edit" and e[1][0] == "removeLayer"]
    assert removed == ["mask.Spare", "Spare", "Light@ 1"]
    assert not {"mask.Spare", "Spare", "Light@ 1"} & {x.name for x in a.layers}
    b = Glyph("b2", {"Light": {}, "Spare": {}})
    b.layers.append(Layer("mask.Spare", b))
    b.remove_fails = True
    package.glyphs["b2"] = b
    facts = world.facts()
    jobs, _ = module.plan(package, ["b2"], facts)
    assert module.remove(jobs, package.masters, facts) == [
        "b2: layer 'mask.Spare' is still there", "b2: layer 'Spare' is still there",
    ]


def test_run_when_many_deleted_then_first_ten_named(world: World) -> None:
    module = load("Empty Layers")
    names = [f"X{i:02}" for i in range(12)]
    world.use([Glyph("q", {"Light": {}, "Bold": {}, **{n: {} for n in names}})])
    text = module.run()
    shown = ", ".join(f"q/{n}" for n in names[:10])
    assert text == f"Deleted 12 empty layers from 1 glyph: {shown} and 2 more."


def test_run_when_nothing_or_no_font_then_value_error_and_main_prints(world: World, capsys: Any) -> None:
    module = load("Empty Layers")
    with pytest.raises(ValueError, match="Open a font"):
        module.run()
    world.use([Glyph("x", {"Light": {}, "Bold": {}})], selection=[])
    with pytest.raises(ValueError, match="Select glyphs"):
        module.run()
    world.selection = ["x"]
    with pytest.raises(ValueError, match="No empty layer"):
        module.run()
    module.main()
    assert capsys.readouterr().out == "Empty Layers: No empty layer in the selected glyphs.\n"
    assert world.notifications() == []


def test_run_when_pending_updates_then_refused(world: World) -> None:
    module = load("Empty Layers")
    empty_font(world)
    world.selection = ["a"]
    world.updates = [3]
    with pytest.raises(ValueError, match="pending"):
        module.run()
    assert LOG == []


# ---------------------------------------------------------------- main entries
@pytest.mark.parametrize("title", PANELS)
def test_main_when_called_then_panel_shown_under_key(world: World, title: str) -> None:
    module = load(title)
    world.use([Glyph("x", {"Light": {}, "Bold": {}})])
    module.main()
    assert world.shown and world.shown[0][0] == module.KEY


def test_sources_when_hashed_then_match_rescue_index() -> None:
    import json

    index = json.loads((ROOT / "rescue-index.json").read_text())
    rows = {row["target"]: row["target_sha256"] for row in index["menus"]}
    for title, stem in SOURCES.items():
        target = f"rescued/samples/{stem}"
        assert target in rows, target
        menu = next(r["menu"] for r in index["menus"] if r["target"] == target)
        assert menu == f"Scripts/{SCRIPTS[title]}/{title}.py", (menu, title)
        assert len(rows[target]) == 64
    assert "rescued/samples/masters_backup_layer.py" in rows
