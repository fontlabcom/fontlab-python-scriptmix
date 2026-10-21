# this_file: tests/test_issue122_S7.py
# SPDX-License-Identifier: Apache-2.0
"""Eight Contours generator and hint scripts, on owned fakes and the real App helpers.

Scripts: Contours/Placeholder Glyphs, Tabular Figure Copies, Superior & Inferior
Figures, Small Caps From Capitals (they make new glyphs), Shadow Copy, Outline
Effect, Autohint Selected Layers and Remove PostScript Hints (they edit the
selected layers).

The fakes replace FontLab glyphs, layers, shapes, contours, the `fontlab`,
`fontgate` and `fontpr` modules and Qt widgets. The real App modules
(`history`, `edit_guards`, `guides`, `layer_writer`, `hints`, `contour_copy`,
`glyph_creation`, `glyph_copies`, `selection_panel`) run over them as
`fly.ap.<module>`, like inside FontLab. The tests prove the planning numbers,
the refusal paths, the rebuild consent, the glyph creation through fontpr
`set_glyph` (never `addGlyph`) and the Undo shape (one notified list, no auto
layer). They do not prove native FontLab behaviour.
"""

import ast
import importlib.util
import itertools
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
FOLDER = "Contours"
SOURCES = {
    "Placeholder Glyphs": "generate_placeholder_glyphs.py",
    "Shadow Copy": "generate_shadow.py",
    "Tabular Figure Copies": "generate_tabular_copies.py",
    "Outline Effect": "generate_outline_effect.py",
    "Superior & Inferior Figures": "generate_superiors.py",
    "Small Caps From Capitals": "generate_small_caps.py",
    "Autohint Selected Layers": "hints_autohint.py",
    "Remove PostScript Hints": "hints_remove.py",
}
KEYS = {
    "Placeholder Glyphs": "generate_placeholder_glyphs",
    "Shadow Copy": "generate_shadow",
    "Tabular Figure Copies": "generate_tabular_copies",
    "Outline Effect": "generate_outline_effect",
    "Superior & Inferior Figures": "generate_superiors",
    "Small Caps From Capitals": "generate_small_caps",
    "Autohint Selected Layers": "hints_autohint",
    "Remove PostScript Hints": "hints_remove",
}
GENERATORS = [
    "Tabular Figure Copies",
    "Superior & Inferior Figures",
    "Small Caps From Capitals",
]
IN_PLACE = [
    "Shadow Copy",
    "Outline Effect",
    "Autohint Selected Layers",
    "Remove PostScript Hints",
]
# Names that live only in the App (fly.ap.layer_writer, hints, contour_copy,
# glyph_creation, glyph_copies, selection_panel), never in a script.
SHARED = {
    "SELECTED", "MAX_NAMES", "BASES_TEXT", "plural", "half_up", "outline_shapes",
    "contour_shapes", "repair_nodes", "copy_contours", "path_contours", "hint_counts",
    "source_problem", "survey_with", "layer_signature", "auto_signatures", "auto_changes",
    "auto_candidates", "rebuild_note", "REBUILD_LABEL", "Job",
}  # fmt: skip
# The panel scripts also leave the table limit, the row type and the writer to the App.
PANEL_SHARED = {"MAX_ROWS", "create"}
GENERATOR_UNDO = "Each new glyph is recorded as its own Undo step, and the outlines as one more Undo step."
APPLY_UNDO = "Each Apply is recorded as one Undo step."
LOG: list[
    tuple[str, Any]
] = []  # ordered ("init" | "edit" | "notify" | "stamp", detail)
STAMP = "UTC-stamp"
IDS = itertools.count(1000)
SELECTED = 0x0020


def path_of(title: str) -> Path:
    return ROOT / "Scripts" / FOLDER / f"{title}.py"


def load(title: str) -> ModuleType:
    """Execute one script file as a fresh module; leave no .pyc and no sys.modules entry."""
    stem = re.sub(r"\W+", "_", title)
    spec = importlib.util.spec_from_file_location("s7_" + stem, path_of(title))
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
    "render", "statusBar", "close", "scroll", "grab", "find", "event",
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
            "textChanged",
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

    def addItem(self, text: str) -> None:
        self.items.append(text)

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


class Spin(Widget):
    """Fake QSpinBox: `value` is a property in PythonQt."""

    def __init__(self, *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "_value", 0)

    @property
    def value(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        object.__setattr__(self, "_value", value)

    def turn(self, value: int) -> None:
        object.__setattr__(self, "_value", value)
        self.valueChanged.emit(value)


class TextEdit(Widget):
    def __init__(self, *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "_plain", "")

    def toPlainText(self) -> str:
        return self._plain

    def setPlainText(self, text: str) -> None:
        object.__setattr__(self, "_plain", text)
        self.textChanged.emit()


class Button(Widget):
    def __init__(self, text: str = "", *a: Any) -> None:
        super().__init__()
        object.__setattr__(self, "label", text)

    def press(self) -> None:
        self.clicked.emit(False)


class Item:
    def __init__(self, text: str = "") -> None:
        self.text = text

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

    def texts(self, row: int) -> list[str]:
        return [
            self.cells[row, c].text
            for c in sorted(c for r, c in self.cells if r == row)
        ]


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

    def m11(self) -> float:
        return self.m[0]

    def m12(self) -> float:
        return self.m[1]

    def m21(self) -> float:
        return self.m[2]

    def m22(self) -> float:
        return self.m[3]

    def dx(self) -> float:
        return self.m[4]

    def dy(self) -> float:
        return self.m[5]


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


class FakePath:
    """Fake QPainterPath: element list (type, x, y) and added sub-paths."""

    def __init__(self, elements: Any = ()) -> None:
        self.elements = [NS(type=t, x=x, y=y) for t, x, y in elements]
        self.parts: list[Any] = []

    def addPath(self, path: Any) -> None:
        self.parts.append(path)

    def elementCount(self) -> int:
        return len(self.elements)

    def elementAt(self, index: int) -> Any:
        return self.elements[index]


class Stroker:
    """Fake QPainterPathStroker: returns STROKE_RESULT, records its settings."""

    calls: ClassVar[list[Any]] = []
    result: ClassVar[Any] = None

    def __init__(self) -> None:
        pass

    def setWidth(self, width: float) -> None:
        Stroker.calls.append(("width", width))

    def setJoinStyle(self, style: Any) -> None:
        Stroker.calls.append(("join", style))

    def setCapStyle(self, style: Any) -> None:
        Stroker.calls.append(("cap", style))

    def createStroke(self, path: Any) -> Any:
        Stroker.calls.append(("stroke", len(path.parts)))
        return Stroker.result


def fake_qt() -> ModuleType:
    qt = ModuleType("fly.qt")
    gui, core = ModuleType("QtGui"), ModuleType("QtCore")
    gui.QDialog, gui.QLabel, gui.QComboBox, gui.QCheckBox = Dialog, Label, Combo, Check
    gui.QSpinBox = gui.QDoubleSpinBox = Spin
    gui.QPlainTextEdit = TextEdit
    gui.QPushButton, gui.QTableWidget, gui.QTableWidgetItem = Button, Table, Item
    gui.QVBoxLayout = gui.QHBoxLayout = gui.QGridLayout = Widget
    gui.QBrush = lambda color: color
    gui.QColor = FakeColor
    gui.QTransform = FakeTransform
    gui.QPainterPath = FakePath
    gui.QPainterPathStroker = Stroker
    for name in ("QPalette", "QAbstractItemView", "QHeaderView"):
        setattr(gui, name, Consts())
    core.Qt = Consts()
    core.QDateTime = DateTime
    core.QPointF = Point
    qt.QtGui, qt.QtCore = gui, core
    return qt


# ---------------------------------------------------------------- FontLab fakes
class Node:
    def __init__(
        self, x: float, y: float, name: str = "", state: int = 0, kind: str = "on"
    ) -> None:
        self.x, self.y, self.name, self.nodeState, self.type = x, y, name, state, kind


class Contour:
    """Fake flContour. cloneMapped() loses node names and raw state, as a node clone can (fl#8569)."""

    def __init__(
        self, points: Any, names: Any = (), states: Any = (), closed: bool = True
    ) -> None:
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
        self.closed = closed
        self.drop_node = False

    def nodes(self) -> list[Node]:
        return list(self._nodes)

    def points(self) -> list[tuple[float, float]]:
        return [(n.x, n.y) for n in self._nodes]

    def cloneMapped(self, transform: FakeTransform) -> "Contour":
        points = [transform.point(n.x, n.y) for n in self._nodes]
        if self.drop_node:
            points = points[:-1]
        copy = Contour(points)
        copy.drop_node = self.drop_node
        return copy

    def path(self) -> tuple:
        return ("path", tuple(self.points()))


def square(left: float, bottom: float, right: float, top: float, **kw: Any) -> Contour:
    return Contour([(left, bottom), (right, bottom), (right, top), (left, top)], **kw)


class Shape:
    def __init__(
        self, contours: Any = (), component: str | None = None, name: str = ""
    ) -> None:
        self.id = next(IDS)
        self.isComponent = component is not None
        self.shapeData = NS(componentGlyph=component or "", name=name, note="")
        self.contours = list(contours)
        self.name = name
        self.transform = FakeTransform()

    def addContours(self, contours: list[Any], closed: bool) -> None:
        assert isinstance(contours, list) and closed is True, (
            "addContours(list, True) only"
        )
        self.contours.extend(contours)

    @property
    def contoursCount(self) -> int:
        return len(self.contours)

    def convertToFgShape(self, fg: Any) -> None:
        fg.contours = list(self.contours)


class Pin:
    def __init__(self, name: str, x: float, y: float) -> None:
        self.name, self.point = name, Point(x, y)


class Guide:
    """Fake flGuideLine: the role is read with isVertical()/isHorizontal(), not by angle."""

    def __init__(
        self, hint: bool = True, vertical: bool = False, horizontal: bool | None = None
    ) -> None:
        self.isHint, self._vertical = hint, vertical
        self._horizontal = (not vertical) if horizontal is None else horizontal

    def isVertical(self) -> bool:
        return self._vertical

    def isHorizontal(self) -> bool:
        return self._horizontal


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
        self.autoLayer = flags.pop("auto", False)
        self.recipe = flags.pop("recipe", "")
        self.isLocked = flags.pop("locked", False)
        self.guidelines: list[Guide] = flags.pop("guides", [])
        self.hint_result: list[Guide] | None = flags.pop("autohint", None)
        self.isNull = False
        self.stubborn = False
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

    def checkInitHistoryState(self, level: int) -> None:
        LOG.append(("init", self.name))

    def removeShape(self, shape: Shape) -> None:
        LOG.append(("edit", ("removeShape", self.name)))
        if not self.stubborn:
            self.shapes.remove(shape)

    def addShape(self, shape: Shape) -> Shape:
        LOG.append(("edit", ("addShape", self.name)))
        if not self.stubborn:
            self.shapes.append(shape)
        return shape

    def insertShape(self, index: int, shape: Shape) -> Shape:
        LOG.append(("edit", ("insertShape", self.name, index)))
        if not self.stubborn:
            self.shapes.insert(index, shape)
        return shape

    def autohint(self) -> bool:
        LOG.append(("edit", ("autohint", self.name)))
        if self.hint_result is None:
            return True  # valid plain layers do not report native failure
        self.guidelines = [g for g in self.guidelines if not g.isHint] + list(
            self.hint_result
        )
        return True

    def removeHints(self, horizontal: bool, vertical: bool) -> bool:
        LOG.append(("edit", ("removeHints", self.name, horizontal, vertical)))
        if self.stubborn:
            return True

        def removed(g: Guide) -> bool:  # by role; a hint with no role always goes
            role = g.isVertical() or g.isHorizontal()
            return g.isHint and (
                not role
                or (vertical and g.isVertical())
                or (horizontal and g.isHorizontal())
            )

        self.guidelines = [g for g in self.guidelines if not removed(g)]
        return True


class Record:
    """Fake font-owned FontGate glyph record."""

    def __init__(self, ident: int, name: str, unicodes: Any = ()) -> None:
        self.id, self.name = ident, name
        self._unicodes = list(unicodes)
        self.ignore = False

    @property
    def unicodes(self) -> list[int]:
        return list(self._unicodes)

    @unicodes.setter
    def unicodes(self, value: list[int]) -> None:
        LOG.append(("edit", ("unicodes", self.name, tuple(value))))
        if not self.ignore:
            self._unicodes = list(value)


class Glyph:
    def __init__(
        self,
        name: str = "",
        layers: dict[str, dict[str, Any]] | None = None,
        unicodes: Any = (),
    ) -> None:
        self.id = next(IDS)
        self.fgGlyphId = next(IDS)
        self.name = name
        self.isNull = False
        self.layers: list[Layer] = []
        for layer_name, spec in (layers or {}).items():
            self.layers.append(Layer(layer_name, self, **spec))
        self.record = Record(self.fgGlyphId, name, unicodes)
        self._stamp: Any = None

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
        return next((x for x in self.layers if x.name == name), None)

    def findLayerCreate(self, name: str) -> Layer:
        found = self.findLayer(name)
        if found is None:
            LOG.append(("edit", ("createLayer", self.name, name)))
            found = Layer(name, self)
            self.layers.append(found)
        return found

    def checkInitHistoryState(self, level: int) -> None:
        LOG.append(("init", self.name))


class Package:
    def __init__(
        self,
        glyphs: list[Glyph],
        masters: tuple[str, ...] = ("Light", "Bold"),
        ident: int = 7,
    ) -> None:
        self.id, self.masters, self.master = ident, list(masters), masters[0]
        self.fgId = ident + 100  # the fontpr font_id; differs from the flPackage id
        self.glyphs = {g.name: g for g in glyphs}
        self.isNull = False
        self.on_add: Any = None

    def findName(self, name: str) -> Glyph | None:
        return self.glyphs.get(name)

    def addGlyph(self, glyph: Glyph) -> Glyph:
        raise AssertionError(
            "flPackage.addGlyph is a raw insert without history: never call it"
        )

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


class FgShape:
    def __init__(self) -> None:
        self.contours: list[Any] = []

    def removeOverlap(self) -> int:
        LOG.append(("edit", ("removeOverlap", len(self.contours))))
        self.contours = self.contours[
            :2
        ]  # the fake "cleans" join loops: keeps two rings
        return 0


class World:
    def __init__(self) -> None:
        self.package: Package | None = None
        self.selection: list[str] = []
        self.history: list[tuple[str, list[Any]]] = []
        self.updates: list[Any] = []
        self.closed: list[str] = []
        self.shown: list[Any] = []
        self.guards: list[Any] = []
        self.fontpr: list[dict[str, Any]] = []  # set_glyph calls, in order

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
def world(monkeypatch: pytest.MonkeyPatch, real_app: Any) -> World:
    state = World()
    LOG.clear()
    Widget.registry = []
    Stroker.calls = []
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    scripting = ModuleType("fly.ap.scripting")
    completion = ModuleType("fly.ap.script_completion")
    fontlab = ModuleType("fontlab")
    fontgate = ModuleType("fontgate")
    items = ModuleType("items")

    def notify(title: str, objects: list[Any], *deep: Any) -> None:
        assert not deep, "no retained objects in this batch"
        LOG.append(("notify", title))
        state.history.append((title, list(objects)))

    class FlGlyph(Glyph):
        @staticmethod
        def updatedFgGlyphs() -> list[Any]:
            return list(state.updates)

    def fl_shape(source: Any = None) -> Shape:
        return Shape(list(source.contours)) if source is not None else Shape()

    def fl_node(point: Point, nodeType: str = "on") -> Node:
        return Node(point.x(), point.y(), kind=nodeType)

    def fl_contour(nodes: list[Node], closed: bool = False) -> Contour:
        contour = Contour([(n.x, n.y) for n in nodes], closed=closed)
        for made, source in zip(contour.nodes(), nodes, strict=True):
            made.type = source.type
        return contour

    def fontpr_call(tool: str, **kw: Any) -> dict[str, Any]:
        """Fake fontpr set_glyph(create=True): FontLab's Add Glyph command makes the glyph."""
        assert tool == "set_glyph" and kw["create"] is True, (tool, kw)
        package = state.package
        assert kw["font_id"] == package.fgId, "fontpr finds fonts by fgId"
        data = kw["glyph_data"]
        assert kw["glyph_name"] == data["name"]
        state.fontpr.append(kw)
        LOG.append(("edit", ("set_glyph", data["name"])))
        layers = {x["name"]: {"width": x["advanceWidth"]} for x in data["layers"]}
        glyph = Glyph(data["name"], layers, unicodes=data.get("unicodes", ()))
        package.glyphs[glyph.name] = glyph
        if package.on_add is not None:
            package.on_add(glyph)
        return {"status": "ok", "created": True}  # mcptools_source.cpp toolSetGlyph

    fontpr = ModuleType("fontpr")
    fontpr.call = fontpr_call
    monkeypatch.setitem(sys.modules, "fontpr", fontpr)
    items.notifyChangesApplied = notify
    fontlab.flItems = lambda: items
    fontlab.flGlyph = FlGlyph
    fontlab.flShape = fl_shape
    fontlab.flNode = fl_node
    fontlab.flContour = fl_contour
    fontlab.CurrentFont = lambda: (
        NS(glyphs=[g.record for g in state.package.glyphs.values()])
        if state.package
        else None
    )
    fontgate.fgShape = FgShape
    ap.fontlab, ap.fontgate = fontlab, fontgate
    scripting.current_package = lambda expected_id=None: state.package
    scripting.names_selected_names = lambda: list(state.selection)

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
                "current_package",
                "names_selected_names",
                "connect_guarded",
                "close_script_dialog",
                "show_script_dialog",
            )
        },
        completion=completion.install,
        modules=[
            "guides",
            "history",
            "edit_guards",
            "layer_writer",
            "hints",
            "contour_copy",
            "glyph_creation",
            "glyph_copies",
            "selection_panel",
        ],
    )
    monkeypatch.setattr(
        state.app["guides"], "dependency_values", lambda package: package.records()
    )
    guards = state.app["edit_guards"]
    monkeypatch.setattr(
        guards,
        "require_selection_window",
        lambda package_id: state.guards.append(("window", package_id)),
    )
    monkeypatch.setattr(
        guards, "require_no_editors", lambda **kw: state.guards.append(("editors",))
    )
    ap.scripting = state.app["scripting"]
    return state


def app(world: World, name: str) -> ModuleType:
    """Return the real App module ``fontlabapp.<name>`` that the scripts see as fly.ap.<name>."""
    module = world.app[name]
    assert sys.modules[f"fly.ap.{name}"] is module
    return module


def notified_names(world: World) -> list[list[str]]:
    return [[str(x.name) for x in objects] for _, objects in world.notifications()]


def edits() -> list[Any]:
    return [detail for kind, detail in LOG if kind == "edit"]


# ---------------------------------------------------------------- generic checks
@pytest.mark.parametrize("title", list(SOURCES))
def test_script_when_parsed_then_py311_typed_headed_and_documented(title: str) -> None:
    text = path_of(title).read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    assert text.startswith(
        f"# this_file: Scripts/{FOLDER}/{title}.py\n# SPDX-License-Identifier: Apache-2.0\n"
    ), "header"
    doc = ast.get_docstring(tree) or ""
    for part in (
        "What it does",
        "How it works",
        "Why this design",
        "How to use",
        "Benefit",
        "Credit",
    ):
        assert part in doc, f"{title}: docstring lacks {part!r}"
    assert "the author's own FontLab sample, Apache-2.0" in doc, title
    assert SOURCES[title] in doc, f"{title}: credit names the sample file"
    for word in (
        "issue 122",
        "D22",
        "S7",
        "S-L4",
        "reviewed App",
        "fragment",
        "unverified",
        "not verified",
    ):
        assert word not in text, f"{title}: internal wording {word!r}"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            assert node.returns is not None, f"{title}.{node.name}: return type"
            for arg in node.args.args + node.args.kwonlyargs:
                assert arg.arg in {"self", "cls"} or arg.annotation is not None, (
                    f"{title}.{node.name}.{arg.arg}"
                )


@pytest.mark.parametrize("title", list(SOURCES))
def test_script_when_imported_then_fly_only_inside_functions(title: str) -> None:
    tree = ast.parse(path_of(title).read_text())
    top = [n for n in tree.body if isinstance(n, ast.Import | ast.ImportFrom)]
    for node in top:
        names = (
            [node.module or ""]
            if isinstance(node, ast.ImportFrom)
            else [a.name for a in node.names]
        )
        assert not any(
            n.startswith(("fly", "fontlab", "fontgate", "PythonQt", "FL"))
            for n in names
        ), (title, names)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "fly.ap":
            raise AssertionError(f"{title}: use 'import fly.ap.<module> as <module>'")


@pytest.mark.parametrize("title", list(SOURCES))
def test_script_when_scanned_then_no_unsafe_host_calls(title: str) -> None:
    text = path_of(title).read_text()
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    body = code.split('"""', 2)[2]  # skip the module docstring
    for pattern in (
        r"\bUpdateAll\(", r"notifyChangesApplied", r"\bFL\.fl\b", r"import FL\b", r"\.fgGlyph\b(?!Id)",
        r"removeAllShapes", r"\.clone\(\)", r"\bround\(", r"except Exception\b", r"\bglobal\b",
        r"\baddGlyph\b", r"\bflGlyph\(", r"findLayerCreate", r"\.unicodes\s*=",
    ):  # fmt: skip
        assert not re.search(pattern, body), f"{title}: {pattern}"


@pytest.mark.parametrize("title", list(SOURCES))
def test_script_when_documented_then_ruled_undo_text(title: str) -> None:
    """S7 I1/I3: the docstring states the recorded Undo steps and claims nothing Undo restores."""
    doc = " ".join(
        (ast.get_docstring(ast.parse(path_of(title).read_text())) or "").split()
    )
    for word in (
        "Edit > Undo restores",
        "Edit > Undo removes",
        "Edit > Undo can",
        "undoable",
        "notified step",
    ):
        assert word not in doc, f"{title}: {word!r}"
    if title in GENERATORS:
        assert GENERATOR_UNDO in doc, title
        assert "Create even if FontLab may rebuild these auto glyphs" in doc, title
    elif title == "Placeholder Glyphs":
        assert "Each new glyph is recorded as its own Undo step." in doc
        assert "Create even if FontLab may rebuild these auto glyphs" in doc
    else:
        assert APPLY_UNDO in doc, title
    benefit = doc.partition("Benefit:")[2].partition("Credit:")[0]
    assert (
        "in seconds" in benefit
        if title == "Placeholder Glyphs"
        else "in one step" in benefit
    ), (title, benefit)


@pytest.mark.parametrize("title", list(SOURCES))
def test_script_when_loaded_then_no_shared_name_defined_and_panel_from_app(
    world: World, title: str
) -> None:
    """Each script keeps only its own logic, its panel subclass and main (T14h)."""
    module = load(title)
    defined = set(vars(module))
    local = sorted(SHARED & defined)
    assert not local, f"{title}: shared names defined in the script: {local}"
    if title == "Placeholder Glyphs":  # own text panel: no selection to plan from
        return
    assert not PANEL_SHARED & defined, f"{title}: {sorted(PANEL_SHARED & defined)}"
    if title in GENERATORS:
        assert "Row" not in defined and "survey_with" not in defined, title
        base = app(world, "glyph_copies").panel_type()
    else:
        base = app(world, "selection_panel").panel_type()
    panel = module.panel_type()
    assert panel.__bases__ == (base,), (title, panel.__bases__)
    assert issubclass(base, app(world, "selection_panel").panel_type())


@pytest.mark.parametrize("title", list(SOURCES))
def test_panel_attributes_when_assigned_then_never_shadow_native_members(
    title: str,
) -> None:
    tree = ast.parse(path_of(title).read_text())
    assigned = {
        n.attr for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
        and isinstance(n.value, ast.Name) and n.value.id == "self"
    }  # fmt: skip
    methods = {
        f.name for c in ast.walk(tree) if isinstance(c, ast.ClassDef) and "Panel" in c.name
        for f in c.body if isinstance(f, ast.FunctionDef)
    }  # fmt: skip
    assert methods, f"{title}: a Panel class"
    assert not (assigned | methods) & NATIVE_MEMBERS, (
        assigned | methods
    ) & NATIVE_MEMBERS


def test_scripts_when_checked_then_real_app_names_exist() -> None:
    used = app_names_used([path_of(t) for t in SOURCES])
    assert {"commit", "scan_auto_facts", "refusal"} <= used["fly.ap.history"]
    assert used["fly.ap.scripting"] == {
        "current_package", "connect_guarded", "close_script_dialog", "show_script_dialog",
    }, "the selection and panel lifecycle live in fly.ap.selection_panel"  # fmt: skip
    assert {
        "NewGlyph",
        "create_glyphs",
        "auto_candidates",
        "rebuild_note",
        "REBUILD_LABEL",
    } <= used["fly.ap.glyph_creation"]
    assert {"survey_with", "half_up", "panel_type"} <= used["fly.ap.glyph_copies"]
    assert {"copy_contours", "contour_shapes", "path_contours"} <= used[
        "fly.ap.contour_copy"
    ]
    assert used["fly.ap.hints"] == {"hint_counts"}
    assert used["fly.ap.selection_panel"] == {"panel_type"}
    assert {"require_selection_window", "require_no_editors"} <= used[
        "fly.ap.edit_guards"
    ]
    check_real_app_names(used)


def test_real_app_package_when_native_names_read_then_served(
    monkeypatch: pytest.MonkeyPatch, real_app: Any
) -> None:
    """The scripts reach native modules as ap.fontlab and ap.fontgate: the real App serves both."""
    import importlib

    package = importlib.import_module("fontlabapp")
    for name in ("fontlab", "fontgate"):
        native = ModuleType(name)
        monkeypatch.setitem(sys.modules, name, native)
        monkeypatch.delitem(vars(package), name, raising=False)
        assert getattr(package, name) is native, name
    used = {
        node.attr
        for title in SOURCES
        for node in ast.walk(ast.parse(path_of(title).read_text()))
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "ap"
    }
    assert used == {"fontlab", "fontgate"}, used


@pytest.mark.parametrize("title", list(SOURCES))
def test_import_when_loaded_then_nothing_opens_and_no_write(
    world: World, title: str
) -> None:
    module = load(title)
    assert (module.TITLE, module.KEY) == (title, KEYS[title])
    assert Widget.registry == [] and world.notifications() == [] and LOG == []


@pytest.mark.parametrize("title", list(SOURCES))
def test_main_when_called_then_panel_shown_under_key(world: World, title: str) -> None:
    module = load(title)
    world.use([Glyph("one", {"Light": {}, "Bold": {}})])
    module.main()
    assert world.shown and world.shown[0][0] == module.KEY
    assert world.notifications() == []


@pytest.mark.parametrize("title", list(SOURCES))
def test_panel_when_no_font_then_message_and_action_disabled(
    world: World, title: str
) -> None:
    module = load(title)
    panel = module.panel_type()(None)
    assert "Open a font" in panel.subtitle.text
    assert not panel.apply_button.isEnabled()
    panel.apply_button.press()
    assert world.notifications() == []
    panel.close()
    assert world.closed == [module.KEY]


def test_sources_when_hashed_then_match_rescue_index() -> None:
    index = json.loads((ROOT / "rescue-index.json").read_text())
    rows = {row["target"]: row for row in index["menus"]}
    for title, stem in SOURCES.items():
        row = rows[f"rescued/samples/{stem}"]
        assert row["menu"] == f"Scripts/{FOLDER}/{title}.py", (row["menu"], title)
        assert len(row["target_sha256"]) == 64


# ---------------------------------------------------------------- Placeholder Glyphs
def test_placeholder_parse_when_mixed_then_names_codes_and_problems_exact(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    rows = module.parse("A.alt, Ω ₿\nA.alt 9bad 𝔸")
    assert [(e.token, e.name, e.problem) for e in rows] == [
        ("A.alt", "A.alt", ""),
        ("Ω", "uni03A9", ""),
        ("₿", "uni20BF", ""),
        ("A.alt", "A.alt", "repeated"),
        ("9bad", "9bad", "invalid name"),
        ("𝔸", "u1D538", ""),
    ]
    assert module.parse("  \n ,, ") == []


@pytest.mark.parametrize(
    ("text", "word"),
    [
        ("a\x00b", "NUL"),
        ("a b", "no-break space"),
        ("a b", "line separator"),
        ("a b", "paragraph separator"),
    ],
)
def test_placeholder_parse_when_lossy_character_then_refused(
    world: World, text: str, word: str
) -> None:
    module = load("Placeholder Glyphs")
    with pytest.raises(ValueError, match=word):
        module.parse(text)


def test_placeholder_code_of_when_names_given_then_code_or_none(world: World) -> None:
    module = load("Placeholder Glyphs")
    assert module.code_of("uni0041") == 0x41
    assert module.code_of("u1F600") == 0x1F600
    assert module.code_of("uni00e9") is None, "lowercase hex is not a uniXXXX name"
    assert module.code_of("uniD800") is None, "surrogates are not characters"
    assert module.code_of("u110000") is None, "beyond Unicode"
    assert module.code_of("A") is None


def test_placeholder_plan_when_exists_or_code_used_then_exact_rows(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    entries = module.parse("A uni0041 uni03A9 x.alt bad!")
    rows = module.plan(entries, {"x.alt"}.__contains__, {0x41: "A"})
    assert [(r.name, r.code, r.note, r.problem) for r in rows] == [
        ("A", None, "", ""),
        ("uni0041", None, "U+0041 is on A: not assigned", ""),
        ("uni03A9", 0x3A9, "U+03A9", ""),
        ("x.alt", None, "", "exists"),
        ("bad!", None, "", "invalid name"),
    ]


def test_placeholder_font_codes_when_records_then_code_map(world: World) -> None:
    module = load("Placeholder Glyphs")
    world.use([Glyph("A", unicodes=[0x41, 0x61]), Glyph("B", unicodes=[0x42])])
    assert module.font_codes() == {0x41: "A", 0x61: "A", 0x42: "B"}


def placeholder_rows(module: ModuleType, world: World, text: str) -> list[Any]:
    package = world.package
    return module.plan(
        module.parse(text),
        lambda n: package.findName(n) is not None,
        module.font_codes(),
    )


def test_placeholder_create_when_applied_then_fontpr_add_glyph_per_glyph(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}, "Bold": {}}, unicodes=[0x41])])
    rows = placeholder_rows(module, world, "Ω A.alt2 A")
    result = module.create(package, rows, 600, world.facts())
    assert result == {"glyphs": 2, "layers": 4, "codes": 1, "mismatches": []}
    layers = [
        {"name": "Light", "advanceWidth": 600},
        {"name": "Bold", "advanceWidth": 600},
    ]
    assert world.fontpr == [
        {"font_id": 107, "glyph_name": "uni03A9", "create": True,
         "glyph_data": {"name": "uni03A9", "layers": layers, "unicodes": [0x3A9]}},
        {"font_id": 107, "glyph_name": "A.alt2", "create": True,
         "glyph_data": {"name": "A.alt2", "layers": layers}},
    ]  # fmt: skip
    assert world.notifications() == [], (
        "FontLab's Add Glyph command records each glyph; no extra notify"
    )
    assert edits() == [("set_glyph", "uni03A9"), ("set_glyph", "A.alt2")], (
        "no FontGate record write"
    )
    omega = package.findName("uni03A9")
    assert [(x.name, x.advanceWidth, x.shapes) for x in omega.layers] == [
        ("Light", 600, []),
        ("Bold", 600, []),
    ]
    assert (
        omega.record.unicodes == [0x3A9]
        and package.findName("A.alt2").record.unicodes == []
    )
    assert world.guards == [("window", 7), ("editors",)], (
        "a code point write runs the Unicode guards"
    )


def test_placeholder_create_when_no_code_then_no_window_guard(world: World) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}, "Bold": {}})])
    result = module.create(
        package, placeholder_rows(module, world, "A.alt"), 500, world.facts()
    )
    assert result["codes"] == 0 and world.guards == []


def test_placeholder_create_when_nothing_ready_then_no_history(world: World) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}})])
    result = module.create(
        package, placeholder_rows(module, world, "A bad!"), 500, world.facts()
    )
    assert result == {"glyphs": 0, "layers": 0, "codes": 0, "mismatches": []}
    assert LOG == [] and world.notifications() == []


def test_placeholder_create_when_name_appeared_since_preview_then_refused_before_history(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}})])
    rows = placeholder_rows(module, world, "B")
    package.glyphs["B"] = Glyph("B", {"Light": {}})
    with pytest.raises(ValueError, match="B exists"):
        module.create(package, rows, 500, world.facts())
    assert LOG == [] and world.notifications() == []


def test_placeholder_create_when_pending_updates_then_refused_before_history(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}})])
    rows = placeholder_rows(module, world, "B")
    world.updates = [3]
    with pytest.raises(ValueError, match="pending"):
        module.create(package, rows, 500, world.facts())
    assert LOG == [] and world.notifications() == []


def test_placeholder_create_when_code_not_kept_then_mismatch(world: World) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}})])
    package.on_add = lambda glyph: setattr(glyph.record, "_unicodes", [])
    result = module.create(
        package, placeholder_rows(module, world, "Ω"), 500, world.facts()
    )
    assert result["mismatches"] == ["uni03A9: Unicode is [], planned U+03A9"]


def test_placeholder_create_when_width_not_kept_then_mismatch(world: World) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}})], ("Light",))
    package.on_add = lambda glyph: setattr(glyph.layer("Light"), "_width", 0)
    result = module.create(
        package, placeholder_rows(module, world, "B"), 500, world.facts()
    )
    assert result["mismatches"] == ["B · Light: width 0, planned 500"]


def test_placeholder_create_when_fontpr_fails_after_first_glyph_then_partial_error_names_it(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    package = world.use([Glyph("A", {"Light": {}})], ("Light",))
    real = sys.modules["fontpr"].call
    sys.modules["fontpr"].call = lambda tool, **kw: (
        real(tool, **kw)
        if kw["glyph_name"] == "B"
        else {"status": "error", "error": "no"}
    )
    with pytest.raises(RuntimeError, match="new glyphs that exist now: B"):
        module.create(
            package, placeholder_rows(module, world, "B C"), 500, world.facts()
        )


def auto_font(world: World, owner: str, **layer: Any) -> Package:
    """A font with A, H and one automatic glyph ``owner`` (no own recipe unless given)."""
    auto = Glyph(
        owner,
        {
            "Light": {"auto": True, "shapes": [Shape(component="A")], **layer},
            "Bold": {},
        },
    )
    outline = {"shapes": [Shape([square(0, 0, 90, 90)])]}
    return world.use([Glyph("A", {"Light": dict(outline), "Bold": dict(outline)}), Glyph("H", {
        "Light": {"shapes": [Shape([square(0, 0, 90, 90)])]}, "Bold": {"shapes": [Shape([square(0, 0, 99, 90)])]},
    }), auto], selection=["H"])  # fmt: skip


def test_placeholder_gate_when_auto_candidate_then_skipped_unless_consent(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    package = auto_font(world, "Aacute.alt")
    rows = placeholder_rows(module, world, "A.alt B")
    gated = module.gate(package, rows, world.facts(), False)
    assert [(r.name, r.problem, r.rebuild) for r in gated] == [
        ("A.alt", "may rebuild auto Aacute.alt", ("Aacute.alt",)),
        ("B", "", ()),
    ]
    allowed = module.gate(package, rows, world.facts(), True)
    first = allowed[0]
    assert (first.name, first.problem, first.rebuild) == ("A.alt", "", ("Aacute.alt",))
    with pytest.raises(ValueError, match="may rebuild auto Aacute.alt"):
        module.create(
            package, allowed, 500, world.facts()
        )  # without the consent the App refuses too
    assert world.fontpr == []
    assert module.create(package, allowed, 500, world.facts(), True)["glyphs"] == 2


def test_placeholder_gate_when_recipe_or_other_suffix_then_no_candidate(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    package = auto_font(world, "Aacute.alt", recipe="A+acute")
    assert (
        module.gate(
            package, placeholder_rows(module, world, "A.alt"), world.facts(), False
        )[0].problem
        == ""
    )
    package = auto_font(world, "Aacute.sc")
    assert (
        module.gate(
            package, placeholder_rows(module, world, "A.alt"), world.facts(), False
        )[0].problem
        == ""
    )


def test_placeholder_panel_when_candidate_then_consent_needed_and_text_clears_it(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    auto_font(world, "Aacute.alt")
    panel = module.panel_type()(None)
    panel.names.setPlainText("A.alt")
    assert panel.table.texts(0) == ["A.alt", "", "may rebuild auto Aacute.alt: skipped"]
    assert not panel.apply_button.isEnabled()
    panel.consent.tick(True)
    assert panel.table.texts(0) == [
        "A.alt",
        "",
        "create on 2 masters · may rebuild auto Aacute.alt",
    ]
    panel.names.setPlainText("A.alt ")
    assert not panel.consent.isChecked() and not panel.apply_button.isEnabled(), (
        "new text clears the tick"
    )
    panel.consent.tick(True)
    panel.apply_button.press()
    assert [c["glyph_name"] for c in world.fontpr] == ["A.alt"], panel.status.text
    assert "Created 1 glyph" in panel.status.text


def test_placeholder_panel_when_text_typed_then_preview_and_create_once(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    world.use([Glyph("A", {"Light": {}, "Bold": {}})])
    panel = module.panel_type()(None)
    panel.names.setPlainText("A Ω")
    assert [panel.table.texts(r) for r in range(panel.table.rowCount)] == [
        ["A", "", "exists: skipped"],
        ["uni03A9", "U+03A9", "create on 2 masters"],
    ]
    assert panel.apply_button.isEnabled()
    panel.apply_button.press()
    assert [c["glyph_name"] for c in world.fontpr] == [
        "uni03A9"
    ] and world.notifications() == []
    assert "Created 1 glyph" in panel.status.text
    panel.names.setPlainText("a b")
    assert (
        "no-break space" in panel.subtitle.text and not panel.apply_button.isEnabled()
    )


# ---------------------------------------------------------------- generator kernel (three scripts)
def test_copy_contours_when_copied_then_mapped_and_nodes_repaired(world: World) -> None:
    module = app(world, "contour_copy")
    shape = Shape(
        [
            square(
                0,
                0,
                10,
                20,
                names=["a", "", "", "d"],
                states=[SELECTED | 0x3, 0x1, 0, 0],
            )
        ]
    )
    shape.transform = FakeTransform(1, 0, 0, 1, 5, 0)
    layer = Layer("Light", shapes=[shape, Shape(component="x")])
    copies = module.copy_contours(layer, FakeTransform(2, 0, 0, 2, 0, 1))
    assert [c.points() for c in copies] == [[(10, 1), (30, 1), (30, 41), (10, 41)]]
    assert [n.name for n in copies[0].nodes()] == ["a", "", "", "d"]
    assert [n.nodeState for n in copies[0].nodes()] == [0x3, 0x1, 0, 0], (
        "raw state kept, selection cleared"
    )
    assert shape.contours[0].points() == [(0, 0), (10, 0), (10, 20), (0, 20)], (
        "source untouched"
    )


def test_copy_contours_when_node_count_changes_then_runtime_error(world: World) -> None:
    module = app(world, "contour_copy")
    contour = square(0, 0, 10, 10)
    contour.drop_node = True
    with pytest.raises(RuntimeError, match="node count"):
        module.copy_contours(Layer("Light", shapes=[Shape([contour])]), FakeTransform())


def figure_font(world: World, *extra: Glyph) -> Package:
    one = Glyph(
        "one",
        {
            "Light": {"shapes": [Shape([square(50, 0, 251, 700)])], "width": 300.4},
            "Bold": {"shapes": [Shape([square(40, 0, 300, 700)])], "width": 340},
        },
    )
    two = Glyph(
        "two",
        {
            "Light": {"shapes": [Shape([square(30, 0, 480, 700)])], "width": 520.6},
            "Bold": {"shapes": [Shape([square(30, 0, 500, 700)])], "width": 560},
        },
    )
    return world.use([one, two, *extra])


def test_tabular_survey_when_mixed_selection_then_exact_notes(world: World) -> None:
    module = load("Tabular Figure Copies")
    three = Glyph("three", {"Light": {"shapes": [Shape(component="two")]}, "Bold": {}})
    four = Glyph(
        "four",
        {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])]}, "Bold": {"auto": True}},
    )
    five = Glyph("five", {"Light": {}, "Bold": {}})
    six = Glyph("six", {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])]}})
    taken = Glyph("two.tf", {"Light": {}, "Bold": {}})
    package = figure_font(
        world,
        three,
        four,
        five,
        six,
        taken,
        Glyph("A"),
        Glyph(
            "one.osf",
            {
                "Light": {"shapes": [Shape([square(0, 0, 9, 9)])]},
                "Bold": {"shapes": [Shape([square(0, 0, 9, 9)])]},
            },
        ),
    )
    names = [
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "A",
        "one.osf",
        "one.tf",
        "one",
    ]
    rows = module.survey(package, names, world.facts())
    assert [(r.source, r.target, r.note) for r in rows] == [
        ("one", "one.tf", ""),
        ("two", "two.tf", "two.tf exists"),
        ("three", "three.tf", "Light: built from components"),
        ("four", "four.tf", "Bold: auto layer"),
        ("five", "five.tf", "Light: no outline"),
        ("six", "six.tf", "Bold: no layer"),
        ("A", "", "not a figure"),
        ("one.osf", "one.osf.tf", ""),
        ("one.tf", "", "already tabular"),
        ("one", "one.tf", "repeated"),
    ]


def test_tabular_widths_when_two_figures_then_widest_half_up_plus_extra(
    world: World,
) -> None:
    module = load("Tabular Figure Copies")
    package = figure_font(world)
    rows = module.survey(package, ["one", "two"], world.facts())
    assert module.tabular_widths(rows, 10) == {"Light": 531, "Bold": 570}


def test_tabular_centring_when_odd_space_then_extra_unit_right(world: World) -> None:
    module = load("Tabular Figure Copies")
    layer = Layer("Light", shapes=[Shape([square(50, 0, 251, 700)])])
    assert module.centring_shift(layer, 531) == 115, "(531 - 201) // 2 = 165; 165 - 50"
    assert module.centring_shift(layer, 532) == 115, "odd unit goes to the right side"


def create_copies(
    world: World, title: str, jobs: list[Any], allow_rebuild: bool = False
) -> dict[str, Any]:
    """Create the jobs the way the script's panel does (App glyph_copies.create)."""
    package = world.package
    return app(world, "glyph_copies").create(
        package, jobs, title, world.facts(), allow_rebuild=allow_rebuild
    )


def test_tabular_prepare_and_create_when_applied_then_add_glyph_then_one_outline_step(
    world: World,
) -> None:
    module = load("Tabular Figure Copies")
    package = figure_font(world)
    rows = module.survey(package, ["one", "two"], world.facts())
    jobs = module.prepare(rows, module.tabular_widths(rows, 10))
    result = create_copies(world, module.TITLE, jobs)
    assert result == {"glyphs": 2, "layers": 4, "mismatches": []}
    assert [(c["font_id"], c["glyph_name"], c["create"], c["glyph_data"]) for c in world.fontpr] == [
        (107, name, True, {"name": name, "layers": [
            {"name": "Light", "advanceWidth": 531}, {"name": "Bold", "advanceWidth": 570},
        ]})
        for name in ("one.tf", "two.tf")
    ], "widths are set by FontLab's Add Glyph command"  # fmt: skip
    assert notified_names(world) == [
        ["Light", "Bold", "Light", "Bold", "one.tf", "two.tf"]
    ]
    assert world.notifications()[0][0] == "Tabular Figure Copies"
    one = package.findName("one.tf")
    assert [x.advanceWidth for x in one.layers] == [531, 570]
    assert one.layer("Light").shapes[0].contours[0].points()[0] == (165, 0)
    assert one.layer("Bold").shapes[0].contours[0].points()[0] == (155, 0), (
        "(570-260)//2 = 155"
    )
    assert package.findName("one").layer("Light").shapes[0].contours[0].points()[0] == (
        50,
        0,
    ), "source untouched"
    created = LOG.index(("edit", ("set_glyph", "two.tf")))
    assert (
        created
        < LOG.index(("init", "one.tf"))
        < LOG.index(("edit", ("addShape", "Light")))
    )
    assert [d for k, d in LOG if k == "init"] == [
        "Light",
        "Bold",
        "Light",
        "Bold",
        "one.tf",
        "two.tf",
    ]
    assert ("width", "Light") not in edits(), "no width write after creation"


def single_source(world: World, title: str, **light: Any) -> tuple[Package, str]:
    package = world.use([
        Glyph("one", {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])], **light}}),
        Glyph("H", {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])], **light}}),
    ], ("Light",))  # fmt: skip
    return package, "H" if title == "Small Caps From Capitals" else "one"


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_create_when_target_appeared_then_refused_before_any_change(
    world: World, title: str
) -> None:
    module = load(title)
    package, source = single_source(world, title)
    rows = module.survey(package, [source], world.facts())
    jobs = generator_jobs(module, title, rows)
    package.glyphs[rows[0].target] = Glyph(rows[0].target, {"Light": {}})
    with pytest.raises(ValueError, match="exists"):
        create_copies(world, module.TITLE, jobs)
    assert LOG == [] and world.notifications() == [] and world.fontpr == []


def generator_jobs(module: ModuleType, title: str, rows: list[Any]) -> list[Any]:
    if title == "Tabular Figure Copies":
        return module.prepare(rows, module.tabular_widths(rows, 0))
    if title == "Superior & Inferior Figures":
        return module.prepare(rows, 60, 350)
    return module.prepare(rows, 75, 70)


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_create_when_pending_updates_then_refused(
    world: World, title: str
) -> None:
    module = load(title)
    package, source = single_source(world, title)
    jobs = generator_jobs(
        module, title, module.survey(package, [source], world.facts())
    )
    world.updates = [1]
    with pytest.raises(ValueError, match="pending"):
        create_copies(world, module.TITLE, jobs)
    assert LOG == [] and world.fontpr == []


def rebuild_font(world: World, title: str) -> tuple[Package, Glyph, str, str]:
    """A source glyph and an automatic glyph without a recipe that shares the new suffix."""
    suffix = {"Tabular Figure Copies": "tf", "Superior & Inferior Figures": "sups"}.get(
        title, "sc"
    )
    owner = f"eacute.{suffix}"
    auto = Glyph(
        owner,
        {
            "Light": {
                "auto": True,
                "shapes": [Shape(component="e")],
                "anchors": [Pin("top", 5, 9)],
            }
        },
    )
    package, source = single_source(world, title)
    package.glyphs.update({"e": Glyph("e", {"Light": {}}), owner: auto})
    return package, auto, source, owner


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_survey_when_auto_candidate_then_skipped_unless_consent(
    world: World, title: str
) -> None:
    """S7 I2: a new name that shares a suffix with a recipe-less auto glyph needs the consent tick."""
    module = load(title)
    package, _auto, source, owner = rebuild_font(world, title)
    (row,) = module.survey(package, [source], world.facts())
    assert (row.note, row.rebuild) == (f"may rebuild auto {owner}", (owner,))
    assert generator_jobs(module, title, [row]) == []
    (row,) = module.survey(package, [source], world.facts(), allow_rebuild=True)
    assert (row.note, row.rebuild) == ("", (owner,))
    with pytest.raises(ValueError, match="Create even if FontLab may rebuild"):
        create_copies(world, module.TITLE, generator_jobs(module, title, [row]))
    assert world.fontpr == [] and LOG == []


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_create_when_auto_glyph_changes_then_reported(
    world: World, title: str
) -> None:
    module = load(title)
    package, auto, source, owner = rebuild_font(world, title)

    def rebuild(
        glyph: Glyph,
    ) -> None:  # FontLab re-resolves the auto layer after a new name appears
        auto.layer("Light").shapes[0].transform = FakeTransform(1, 0, 0, 1, 12, 0)

    package.on_add = rebuild
    rows = module.survey(package, [source], world.facts(), allow_rebuild=True)
    result = create_copies(
        world, module.TITLE, generator_jobs(module, title, rows), allow_rebuild=True
    )
    assert result["mismatches"] == [
        (
            f"Auto glyph {owner} · Light changed after the write; "
            "FontLab rebuilt it. Check it."
        )
    ]
    assert all(
        not x.autoLayer
        for _, objects in world.notifications()
        for x in objects
        if isinstance(x, Layer)
    )
    assert ("init", owner) not in LOG, (
        "automatic glyphs are never initialised or notified"
    )


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_create_when_layer_ignores_width_then_mismatch(
    world: World, title: str
) -> None:
    module = load(title)
    package, source = single_source(world, title, width=400)
    package.on_add = lambda glyph: setattr(glyph.layer("Light"), "_width", 1)
    rows = module.survey(package, [source], world.facts())
    result = create_copies(world, module.TITLE, generator_jobs(module, title, rows))
    assert result["mismatches"] and "width 1; planned" in result["mismatches"][0], (
        result
    )


def test_superior_prepare_when_scaled_then_exact_points_and_half_up_advance(
    world: World,
) -> None:
    module = load("Superior & Inferior Figures")
    package = world.use(
        [
            Glyph(
                "one",
                {
                    "Light": {
                        "shapes": [Shape([square(100, 0, 300, 700)])],
                        "width": 501,
                    }
                },
            )
        ],
        ("Light",),
    )
    rows = module.survey(package, ["one"], world.facts(), ".sups")
    ((target, layers),) = module.prepare(rows, 50, 350)
    master, contours, advance = layers[0]
    assert (target, master, advance) == ("one.sups", "Light", 251), (
        "250.5 rounds half up"
    )
    assert contours[0].points() == [(50, 350), (150, 350), (150, 700), (50, 700)]


def test_superior_survey_when_inferior_then_subs_names(world: World) -> None:
    module = load("Superior & Inferior Figures")
    package = world.use(
        [
            Glyph("one", {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])]}}),
            Glyph("one.subs"),
        ],
        ("Light",),
    )
    rows = module.survey(package, ["one", "A", "one.subs"], world.facts(), ".subs")
    assert [(r.source, r.target, r.note) for r in rows] == [
        ("one", "one.subs", "one.subs exists"),
        ("A", "", "not a figure"),
        ("one.subs", "", "already superior or inferior"),
    ]
    assert module.KINDS == ((".sups", "Superior", 350), (".subs", "Inferior", -150))


def test_small_caps_names_when_capitals_then_lowercase_sc(world: World) -> None:
    module = load("Small Caps From Capitals")
    assert [module.target_name(n) for n in ("H", "H.ss01", "Aacute", "IJ")] == [
        "h.sc",
        "h.sc.ss01",
        "aacute.sc",
        "ij.sc",
    ]
    assert [module.is_capital(n) for n in ("H", "h", "H.ss01", "one", "h.sc", "Germandbls")] == [
        True, False, True, False, False, True,
    ]  # fmt: skip


def test_small_caps_prepare_when_scaled_then_exact_points_and_advance(
    world: World,
) -> None:
    module = load("Small Caps From Capitals")
    package = world.use(
        [
            Glyph(
                "H",
                {
                    "Light": {
                        "shapes": [Shape([square(100, 0, 500, 700)])],
                        "width": 601,
                    }
                },
            )
        ],
        ("Light",),
    )
    rows = module.survey(package, ["H", "h", "H"], world.facts())
    assert [(r.source, r.target, r.note) for r in rows] == [
        ("H", "h.sc", ""), ("h", "", "not a capital"), ("H", "h.sc", "repeated"),
    ]  # fmt: skip
    ((_target, layers),) = module.prepare(rows[:1], 75, 70)
    assert layers[0][2] == 451, "450.75 rounds to 451"
    points = [(round(x, 6), round(y, 6)) for x, y in layers[0][1][0].points()]
    assert points == [(75, 0), (375, 0), (375, 490), (75, 490)]


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_panel_when_opened_then_preview_and_create_once(
    world: World, title: str
) -> None:
    module = load(title)
    source = "H" if title == "Small Caps From Capitals" else "one"
    world.use(
        [
            Glyph(
                source,
                {
                    "Light": {"shapes": [Shape([square(0, 0, 90, 90)])]},
                    "Bold": {"shapes": [Shape([square(0, 0, 99, 90)])]},
                },
            ),
            Glyph("a"),
        ],
        selection=[source, "a"],
    )
    panel = module.panel_type()(None)
    texts = [panel.table.texts(r) for r in range(panel.table.rowCount)]
    assert texts[0][0] == source and texts[0][2] == "create on 2 masters"
    assert texts[1][0] == "a" and texts[1][2].startswith("not a")
    assert panel.scope is None, "copies are made on every master"
    assert panel.apply_button.isEnabled()
    panel.apply_button.press()
    assert len(world.fontpr) == 1 and len(world.notifications()) == 1, panel.status.text
    assert "Created 1 glyph" in panel.status.text
    panel.apply_button.press()
    assert len(world.fontpr) == 1 and len(world.notifications()) == 1, (
        "second press: the target exists now"
    )


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_panel_when_candidate_then_consent_needed_and_reselect_clears_it(
    world: World, title: str
) -> None:
    module = load(title)
    package, _auto, source, owner = rebuild_font(world, title)
    world.selection = [source]
    panel = module.panel_type()(None)
    assert (
        panel.table.texts(0)[2] == f"may rebuild auto {owner}"
        and not panel.apply_button.isEnabled()
    )
    panel.consent.tick(True)
    assert panel.table.texts(0)[2] == f"create on 1 masters · may rebuild auto {owner}"
    assert panel.apply_button.isEnabled()
    panel.selection_button.press()
    assert not panel.consent.isChecked() and not panel.apply_button.isEnabled(), (
        "Use selection clears the tick"
    )
    panel.consent.tick(True)
    panel.apply_button.press()
    assert [c["glyph_name"] for c in world.fontpr] == [
        module.survey(package, [source], world.facts())[0].target
    ]
    assert "Created 1 glyph" in panel.status.text, panel.status.text


def test_generator_panel_when_reselect_on_closed_font_then_status_not_raise(
    world: World,
) -> None:
    """S7 M6: Use selection shows a refusal in the status line instead of raising from the slot."""
    module = load("Small Caps From Capitals")
    figure_font(world)
    panel = module.panel_type()(None)
    world.package = None
    panel.selection_button.press()
    assert panel.status.text == "The font changed. Run this script again.", (
        panel.status.text
    )
    assert "Error" not in panel.status.text


# ---------------------------------------------------------------- in-place family
def o_font(world: World) -> Package:
    o = Glyph(
        "O",
        {
            "Light": {"shapes": [Shape([square(0, 0, 100, 100)])]},
            "Bold": {"shapes": [Shape([square(0, 0, 120, 100)])]},
        },
    )
    oacute = Glyph(
        "Oacute", {"Light": {"auto": True, "shapes": [Shape(component="O")]}}
    )
    h = Glyph(
        "H",
        {
            "Light": {
                "shapes": [Shape([square(0, 0, 50, 70), square(60, 0, 90, 70)])],
                "guides": [Guide(), Guide(vertical=True), Guide(False)],
            },
            "Bold": {"shapes": [Shape(component="I")]},
        },
    )
    s = Glyph(
        "S",
        {
            "Light": {"shapes": [Shape(name="shadow"), Shape([square(0, 0, 9, 9)])]},
            "Bold": {},
        },
    )
    e = Glyph(
        "E",
        {
            "Light": {},
            "Bold": {"locked": True, "shapes": [Shape([square(0, 0, 9, 9)])]},
        },
    )
    return world.use([o, oacute, h, s, e], selection=["O", "Oacute", "H", "S", "E"])


def test_shadow_survey_when_mixed_then_exact_notes_and_bases_opt_in(
    world: World,
) -> None:
    module = load("Shadow Copy")
    package = o_font(world)
    rows = module.survey(
        package, world.selection, ["Light", "Bold"], world.facts(), False
    )
    assert [(r.glyph.name, r.master, r.contours, r.note) for r in rows] == [
        ("O", "Light", 0, "base of auto Oacute (skipped)"),
        ("O", "Bold", 0, "base of auto Oacute (skipped)"),
        ("Oacute", "Light", 0, "auto layer (skipped)"),
        ("Oacute", "Bold", 0, "no layer in this master"),
        ("H", "Light", 2, ""),
        ("H", "Bold", 0, "built from components (skipped)"),
        ("S", "Light", 0, "has a shadow already (skipped)"),
        ("S", "Bold", 0, "no outline (skipped)"),
        ("E", "Light", 0, "no outline (skipped)"),
        ("E", "Bold", 0, "locked layer (skipped)"),
    ]
    opened = module.survey(package, ["O"], ["Light"], world.facts(), True)
    assert [(r.contours, r.note) for r in opened] == [(1, "")]


def test_shadow_when_applied_then_inserted_first_shifted_one_step(world: World) -> None:
    module = load("Shadow Copy")
    package = o_font(world)
    facts = world.facts()
    rows = module.survey(package, ["H", "O"], ["Light", "Bold"], facts, True)
    result = module.add_shadows(rows, 40, -40, facts, True)
    assert result == {"layers": 3, "glyphs": 2, "contours": 4, "mismatches": []}
    layer = package.findName("H").layer("Light")
    assert [s.name for s in layer.shapes] == ["shadow", ""]
    assert [c.points()[0] for c in layer.shapes[0].contours] == [(40, -40), (100, -40)]
    assert layer.shapes[1].contours[0].points()[0] == (0, 0), "original untouched"
    assert notified_names(world) == [["Light", "Light", "Bold", "H", "O"]]
    assert LOG.index(("init", "H")) < LOG.index(("edit", ("insertShape", "Light", 0)))


def test_shadow_when_base_without_opt_in_then_refused_before_history(
    world: World,
) -> None:
    module = load("Shadow Copy")
    package = o_font(world)
    facts = world.facts()
    rows = module.survey(package, ["O"], ["Light"], facts, True)
    with pytest.raises(ValueError, match="base of auto"):
        module.add_shadows(rows, 40, -40, facts, False)
    assert LOG == []


def test_shadow_when_layer_ignores_insert_then_mismatch(world: World) -> None:
    module = load("Shadow Copy")
    package = o_font(world)
    package.findName("H").layer("Light").stubborn = True
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light"], facts, False)
    assert module.add_shadows(rows, 1, 1, facts, False)["mismatches"] == [
        "H · Light: no shadow element after the write"
    ]


def stroke_path() -> FakePath:
    """Two rings: square 0..10 with a curve side, inner square; a stray 2-point stub."""
    return FakePath([
        (0, 0, 0), (1, 10, 0), (2, 10, 5), (3, 5, 10), (3, 0, 10), (1, 0, 0),
        (0, 2, 2), (1, 8, 2), (1, 8, 8), (1, 2, 2),
        (0, 50, 50), (1, 60, 50),
    ])  # fmt: skip


def test_path_contours_when_elements_then_closed_typed_nodes(world: World) -> None:
    module = app(world, "contour_copy")
    contours = module.path_contours(stroke_path())
    assert [c.points() for c in contours] == [
        [(0, 0), (10, 0), (10, 5), (5, 10), (0, 10)],
        [(2, 2), (8, 2), (8, 8)],
    ]
    assert [n.type for n in contours[0].nodes()] == ["on", "on", "curve", "curve", "on"]
    assert all(c.closed for c in contours)


def test_ring_shape_when_built_then_stroker_settings_and_overlap_removed(
    world: World,
) -> None:
    module = load("Outline Effect")
    Stroker.result = stroke_path()
    layer = Layer(
        "Light", shapes=[Shape([square(0, 0, 10, 10)]), Shape([square(20, 0, 30, 10)])]
    )
    ring = module.ring_shape(layer, 30)
    assert Stroker.calls[0] == ("width", 30) and Stroker.calls[-1] == ("stroke", 2)
    assert ("removeOverlap", 2) in edits()
    assert [c.points()[0] for c in ring.contours] == [(0, 0), (2, 2)]


def test_outline_when_applied_then_shapes_replaced_one_step(world: World) -> None:
    module = load("Outline Effect")
    Stroker.result = stroke_path()
    package = o_font(world)
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light", "Bold"], facts, False)
    assert [(r.master, r.contours, r.note) for r in rows] == [
        ("Light", 2, ""),
        ("Bold", 0, "built from components (skipped)"),
    ]
    result = module.outline(rows, 30, facts, False)
    assert result == {"layers": 1, "glyphs": 1, "contours": 2, "mismatches": []}
    layer = package.findName("H").layer("Light")
    assert len(layer.shapes) == 1 and layer.shapes[0].contoursCount == 2
    assert (
        edits().count(("removeShape", "Light")) == 1
        and ("addShape", "Light") in edits()
    )
    assert notified_names(world) == [["Light", "H"]]
    assert LOG.index(("edit", ("removeOverlap", 2))) < LOG.index(("init", "Light")), (
        "geometry is prepared first"
    )


def test_outline_when_nothing_to_do_then_no_history(world: World) -> None:
    module = load("Outline Effect")
    package = o_font(world)
    facts = world.facts()
    rows = module.survey(package, ["E"], ["Light"], facts, False)
    assert module.outline(rows, 30, facts, False)["layers"] == 0
    assert LOG == [] and world.notifications() == []


def test_hint_counts_when_guides_then_counted_by_role(world: World) -> None:
    """S7 M1: the App counts hints with isHorizontal()/isVertical(), plain guides not at all."""
    hints = app(world, "hints")
    layer = Layer("Light", guides=[
        Guide(), Guide(vertical=True), Guide(), Guide(False), Guide(False, True), Guide(horizontal=False),
    ])  # fmt: skip
    assert hints.hint_counts(layer) == (2, 1), "a hint with no role is in neither count"


def test_autohint_when_applied_then_counts_and_readback_one_step(world: World) -> None:
    module = load("Autohint Selected Layers")
    package = o_font(world)
    h = package.findName("H")
    h.layer("Light").hint_result = [
        Guide(),
        Guide(),
        Guide(vertical=True),
        Guide(vertical=True),
    ]
    h.layers[1] = Layer(
        "Bold", h, shapes=[Shape([square(0, 0, 9, 9)])]
    )  # native success can still leave an outlined layer without hints
    facts = world.facts()
    rows = module.survey(package, ["H", "Oacute", "S"], ["Light", "Bold"], facts, False)
    assert [(r.glyph.name, r.master, r.before, r.note) for r in rows] == [
        ("H", "Light", (1, 1), ""),
        ("H", "Bold", (0, 0), ""),
        ("Oacute", "Light", (0, 0), "auto layer (skipped)"),
        ("Oacute", "Bold", (0, 0), "no layer in this master"),
        ("S", "Light", (0, 0), ""),
        ("S", "Bold", (0, 0), "no outline (skipped)"),
    ]
    rows = [r for r in rows if r.glyph.name != "S"]
    result = module.autohint(rows, facts, False)
    assert result["after"] == {("H", "Light"): (2, 2), ("H", "Bold"): (0, 0)}
    assert result["mismatches"] == [
        "H · Bold: outline has no PostScript hints after autohint"
    ]
    assert (result["layers"], result["glyphs"]) == (2, 1)
    assert notified_names(world) == [["Light", "Bold", "H"]]
    assert h.layer("Light").guidelines[0].isHint is False, "non-hint guides kept"


def test_remove_hints_survey_when_direction_chosen_then_no_hints_note(
    world: World,
) -> None:
    module = load("Remove PostScript Hints")
    only_vertical = Glyph("I", {"Light": {"guides": [Guide(vertical=True)]}})
    package = world.use([only_vertical], ("Light",))
    rows = module.survey(package, ["I"], ["Light"], world.facts(), False, True, False)
    assert [(r.before, r.note) for r in rows] == [((0, 1), "no horizontal hints")]
    rows = module.survey(package, ["I"], ["Light"], world.facts(), False, True, True)
    assert [(r.before, r.note) for r in rows] == [((0, 1), "")]
    with pytest.raises(ValueError, match="direction"):
        module.survey(package, ["I"], ["Light"], world.facts(), False, False, False)


def test_remove_hints_when_applied_then_counts_zero_one_step(world: World) -> None:
    module = load("Remove PostScript Hints")
    package = o_font(world)
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light"], facts, False, True, False)
    result = module.remove_hints(rows, True, False, facts, False)
    assert result == {"layers": 1, "glyphs": 1, "removed": 1, "mismatches": []}
    assert app(world, "hints").hint_counts(package.findName("H").layer("Light")) == (
        0,
        1,
    )
    assert ("removeHints", "Light", True, False) in edits()
    assert notified_names(world) == [["Light", "H"]]


def test_remove_hints_when_layer_keeps_hints_then_mismatch(world: World) -> None:
    module = load("Remove PostScript Hints")
    package = o_font(world)
    package.findName("H").layer("Light").stubborn = True
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light"], facts, False, True, True)
    result = module.remove_hints(rows, True, True, facts, False)
    assert result["mismatches"] == [
        "H · Light: 1 horizontal and 1 vertical hints remain"
    ]


@pytest.mark.parametrize("title", IN_PLACE)
def test_in_place_panel_when_opened_then_preview_scope_bases_and_apply_once(
    world: World, title: str
) -> None:
    module = load(title)
    Stroker.result = stroke_path()
    package = o_font(world)
    package.findName("H").layer("Light").hint_result = [Guide()]
    package.findName("O").layer("Light").guidelines = [Guide()]
    world.selection = ["H", "O"]
    panel = module.panel_type()(None)
    names = [panel.table.texts(r)[0] for r in range(panel.table.rowCount)]
    assert names == ["H · Light", "O · Light"], "current master by default"
    assert "base of auto Oacute" in panel.table.texts(1)[-1]
    panel.scope.pick(1)
    assert panel.table.rowCount == 4
    assert (
        panel.CONSENT
        == "Edit bases of auto glyphs anyway (FontLab rebuilds those auto glyphs)"
    )
    panel.consent.tick(True)
    assert "base of auto" not in " ".join(panel.table.texts(3))
    panel.scope.pick(0)
    assert panel.apply_button.isEnabled()
    panel.apply_button.press()
    assert len(world.notifications()) == 1, panel.status.text
    assert notified_names(world)[0][-2:] == ["H", "O"]
    assert "Error" not in panel.status.text
    panel.selection_button.press()
    assert not panel.consent.isChecked(), "Use selection clears the bases opt-in"
    assert "base of auto Oacute" in panel.table.texts(1)[-1]


@pytest.mark.parametrize("title", IN_PLACE)
def test_in_place_panel_when_reselect_on_switched_font_then_status_not_raise(
    world: World, title: str
) -> None:
    """S7 M6: the Use selection slot shows the refusal in the status line, as Apply does."""
    module = load(title)
    o_font(world)
    world.selection = ["H"]
    panel = module.panel_type()(None)
    world.package = None
    panel.selection_button.press()
    assert panel.status.text == "The font changed. Run this script again.", (
        panel.status.text
    )


def test_in_place_panel_when_font_switched_then_apply_refused(world: World) -> None:
    module = load("Shadow Copy")
    o_font(world)
    world.selection = ["H"]
    panel = module.panel_type()(None)
    world.use([Glyph("H", {"Light": {"shapes": [Shape([square(0, 0, 9, 9)])]}})])
    world.package.id = 99
    panel.apply_button.press()
    assert world.notifications() == [] and "font changed" in panel.status.text


@pytest.mark.parametrize("hint_result", [[], [Guide(False)], [Guide(horizontal=False)]])
def test_autohint_when_native_succeeds_without_hints_then_readback_mismatch(
    world: World, hint_result: list[Guide]
) -> None:
    """A successful native return does not prove that the outline got hints."""
    module = load("Autohint Selected Layers")
    package = o_font(world)
    package.findName("H").layer("Light").hint_result = hint_result
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light"], facts, False)
    result = module.autohint(rows, facts, False)
    assert result["mismatches"] == [
        "H · Light: outline has no PostScript hints after autohint"
    ], result
    assert notified_names(world) == [["Light", "H"]]


def test_outline_when_other_elements_present_then_preserved_and_readback_clean(
    world: World,
) -> None:
    """Empty and image elements are not part of the outline being replaced."""
    module = load("Outline Effect")
    Stroker.result = stroke_path()
    package = o_font(world)
    layer = package.findName("H").layer("Light")
    empty, image = Shape(name="empty"), Shape(name="image")
    image.image = object()
    layer.shapes[:] = [empty, layer.shapes[0], image]
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light"], facts, False)
    result = module.outline(rows, 30, facts, False)
    assert layer.shapes[:2] == [empty, image], "non-outline elements must survive"
    assert len(layer.shapes) == 3 and not result["mismatches"], result


def test_outline_when_removal_ignored_then_readback_mismatch(world: World) -> None:
    module = load("Outline Effect")
    Stroker.result = stroke_path()
    package = o_font(world)
    layer = package.findName("H").layer("Light")
    layer.stubborn = True
    facts = world.facts()
    rows = module.survey(package, ["H"], ["Light"], facts, False)
    assert module.outline(rows, 30, facts, False)["mismatches"], (
        "an ignored write must be reported"
    )


@pytest.mark.parametrize("title", ["Shadow Copy", *GENERATORS])
def test_copy_docstring_when_metadata_omitted_then_discloses_limits(title: str) -> None:
    doc = " ".join(load(title).__doc__.split())
    assert "Only node names and raw node flags are repaired" in doc, title
    assert "Other node properties and contour names are not repaired" in doc, title
    assert "merged into one element" in doc, title
    assert "source element names and notes are not copied" in doc, title


@pytest.mark.parametrize("title", GENERATORS)
def test_generator_docstring_when_anchors_omitted_then_says_not_copied(
    title: str,
) -> None:
    assert "Anchors are not copied" in load(title).__doc__, title


def test_autohint_docstring_when_side_effects_source_only_then_no_preservation_claim() -> (
    None
):
    doc = " ".join(load("Autohint Selected Layers").__doc__.split())
    assert "FontLab's source shows" in doc
    assert "master temporarily" in doc and "hinting options" in doc
    assert "node links" in doc
    assert "same as FontLab's menu command" not in doc
    assert "reports failure" not in doc


def test_placeholder_docstring_when_single_ascii_then_describes_actual_mapping(
    world: World,
) -> None:
    module = load("Placeholder Glyphs")
    doc = " ".join(module.__doc__.split())
    assert "single non-ASCII character" in doc
    assert [(e.name, e.problem) for e in module.parse("A & 1")] == [
        ("A", ""),
        ("&", "invalid name"),
        ("1", "invalid name"),
    ]
    text = path_of("Placeholder Glyphs").read_text()
    assert all(char not in text for char in ("\u00a0", "\u2028", "\u2029")), (
        "use visible Unicode escapes"
    )


def test_autohint_panel_when_no_hints_after_success_then_status_reports_mismatch(
    world: World,
) -> None:
    module = load("Autohint Selected Layers")
    package = o_font(world)
    package.findName("H").layer("Light").hint_result = []
    world.selection = ["H"]
    panel = module.panel_type()(None)
    panel.apply_button.press()
    assert (
        "H · Light: outline has no PostScript hints after autohint" in panel.status.text
    ), panel.status.text


def test_autohint_when_no_planned_layers_then_no_history(world: World) -> None:
    world.use([])
    module = load("Autohint Selected Layers")
    assert module.autohint([], world.facts(), False) == {
        "layers": 0,
        "glyphs": 0,
        "after": {},
        "mismatches": [],
    }
    assert not LOG and not world.notifications(), "empty plans must not start history"
