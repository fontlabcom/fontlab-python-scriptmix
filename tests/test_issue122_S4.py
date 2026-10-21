# this_file: tests/test_issue122_S4.py
# SPDX-License-Identifier: Apache-2.0
"""Seven Components scripts on owned FontLab/Qt fakes.

The scripts run unchanged. Only the native modules `fontlab`, `FL`,
`PythonQt` and FontLab's data tools (`echopy.fontpr`, reached as `fly.pr`)
are fakes; `fly` and the App modules (`fontlabapp.scripting`, `history`,
`edit_guards`) are the real packages.
Offline results never prove native FontLab behaviour.
"""

import ast
import importlib
import itertools
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
FOLDER = ROOT / "Scripts/Components"
STEMS = {
    "Build From Recipes": "components_build_from_recipes",
    "Align By Anchor": "components_align_by_anchor",
    "Decompose": "components_decompose",
    "Replace Reference": "components_replace_reference",
    "Copy Offsets Between Masters": "components_copy_offsets_between_masters",
    "Unlock Lock": "components_unlock_lock",
    "Nested Finder": "components_nested_finder",
}
NAMES = list(STEMS)
WRITERS = [n for n in NAMES if n != "Build From Recipes"]  # one-step history writers
EJECTORS = ["Decompose", "Nested Finder"]  # remove a component: Undo not yet verified
SMOOTH = 0x30  # fake flNode.NodeKind["SmoothMask"]


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


SIGNALS = {
    "clicked",
    "textChanged",
    "toggled",
    "valueChanged",
    "currentIndexChanged",
    "itemChanged",
    "timeout",
}


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
            ("set", "add", "insert", "block", "show", "raise", "resize")
        ):
            return lambda *args, **kwargs: None
        raise AttributeError(name)

    def setEnabled(self, flag: bool) -> None:
        self.enabled = flag

    def setText(self, text: str) -> None:
        self.text = text

    def verticalHeader(self) -> "Widget":
        return Widget()

    def horizontalHeader(self) -> "Widget":
        return Widget()


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


class LineEdit(Widget):
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.text = text

    def setText(self, text: str) -> None:
        self.text = text
        self.textChanged.emit(text)


class PlainText(Widget):
    def __init__(self) -> None:
        super().__init__()
        self.plain = ""

    def setPlainText(self, text: str) -> None:
        self.plain = text
        self.textChanged.emit()

    def toPlainText(self) -> str:
        return self.plain


class CheckBox(Widget):
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.checked = False

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

    @property
    def currentText(self) -> str:
        return self.items[self.currentIndex] if self.items else ""

    def addItem(self, text: str) -> None:
        self.items.append(text)
        self.currentIndex = max(self.currentIndex, 0)

    def addItems(self, texts: list[str]) -> None:
        for text in texts:
            self.addItem(text)

    def clear(self) -> None:
        self.items, self.currentIndex = [], -1

    def setItemText(self, index: int, text: str) -> None:
        self.items[index] = text

    def setCurrentIndex(self, index: int) -> None:
        self.currentIndex = index
        self.currentIndexChanged.emit(index)


class Button(Widget):
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self.label = text


class Item:
    def __init__(self, text: str = "") -> None:
        self._text, self._data, self._state = text, None, 0
        self.foreground = None

    def setForeground(self, brush: Any) -> None:
        self.foreground = brush

    def text(self) -> str:
        return self._text

    def setData(self, role: int, value: Any) -> None:
        self._data = value

    def data(self, role: int) -> Any:
        return self._data

    def setCheckState(self, state: int) -> None:
        self._state = state

    def checkState(self) -> int:
        return self._state

    def __getattr__(self, name: str) -> Any:
        return lambda *args, **kwargs: None


class ListWidget(Widget):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[Item] = []

    @property
    def count(self) -> int:
        return len(self.items)

    def item(self, row: int) -> Item:
        return self.items[row]

    def addItem(self, item: Item) -> None:
        self.items.append(item)

    def clear(self) -> None:
        self.items = []


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
            [self.cells[(r, c)].text() for c in range(columns)]
            for r in range(self.rows)
        ]

    def colors(self) -> list[Any]:
        """Foreground colour value of the last cell of each row."""
        columns = max((c for _, c in self.cells), default=-1) + 1
        return [
            self.cells[(r, columns - 1)].foreground.color().value
            for r in range(self.rows)
        ]


class Timer(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.starts, self.active = 0, False

    def start(self, *args: Any) -> None:
        self.starts += 1
        self.active = True

    def stop(self) -> None:
        self.active = False


class Dialog(Widget):
    registry: ClassVar[list[Any]] = []

    def __init__(self, parent: Any = None) -> None:
        super().__init__()
        self.deleted = self.shown = False
        self.palette = Palette()
        self.core_closed = 0
        Dialog.registry.append(self)

    def closeEvent(self, event: Any) -> None:
        self.core_closed += 1

    def close(self) -> bool:
        self.closeEvent(object())
        return True

    def show(self) -> None:
        self.shown = True

    def deleteLater(self) -> None:
        self.deleted = True


class Transform:
    """QTransform(m11, m12, m21, m22, dx, dy)."""

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
        self.affine = True  # False: a perspective transform

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

    def isAffine(self) -> bool:
        return self.affine


def make_qt() -> ModuleType:
    qt = ModuleType("PythonQt")
    core = NS(
        QPointF=lambda x, y: NS(x=lambda: x, y=lambda: y),
        QDateTime=NS(currentDateTimeUtc=lambda: "UTC stamp"),
        QTimer=Timer,
        Qt=NS(
            Horizontal=1,
            AlignRight=2,
            ScrollBarAlwaysOff=3,
            ItemIsEnabled=4,
            ItemIsUserCheckable=8,
            UserRole=32,
            Checked=2,
            Unchecked=0,
            CaseInsensitive=0,
            MatchContains=1,
        ),
    )
    gui = NS(
        QDialog=Dialog,
        QLabel=Label,
        QLineEdit=LineEdit,
        QPlainTextEdit=PlainText,
        QCheckBox=CheckBox,
        QComboBox=Combo,
        QPushButton=Button,
        QTableWidget=Table,
        QTableWidgetItem=Item,
        QListWidget=ListWidget,
        QListWidgetItem=Item,
        QVBoxLayout=Widget,
        QHBoxLayout=Widget,
        QGridLayout=Widget,
        QCompleter=Widget,
        QFontDatabase=NS(FixedFont=0, systemFont=lambda kind: Font()),
        QPalette=Palette,
        QColor=Color,
        QBrush=lambda color: NS(color=lambda: color),
        QTransform=Transform,
        QAbstractItemView=NS(NoEditTriggers=0, NoSelection=0),
        QHeaderView=NS(Stretch=0, ResizeToContents=1),
    )
    qt.QtCore, qt.QtGui = core, gui
    return qt


# ---------------------------------------------------------------- font fakes
IDS = itertools.count(1)


class Node:
    def __init__(self, x: float, y: float, state: int) -> None:
        self.x, self.y, self.nodeState = x, y, state


class Contour:
    def __init__(self, nodes: list[Node]) -> None:
        self._nodes = nodes

    def nodes(self) -> list[Node]:
        return list(self._nodes)


class Builder:
    def __init__(self, world: "World") -> None:
        self.world = world

    def update(self) -> bool:
        self.world.events.append(("builder-update",))
        return self.world.builder_ok


class ShapeData:
    def __init__(self, world: "World", base: str, note: str) -> None:
        self.world, self._base, self._note = world, base, note
        self.referenceCount, self.componentLayer = 1, ""
        self.builder = Builder(world)

    @property
    def componentGlyph(self) -> str:
        return self._base

    @componentGlyph.setter
    def componentGlyph(self, name: str) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._base = name

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, text: str) -> None:
        self._note = text


class Shape:
    def __init__(
        self,
        world: "World",
        base: str | None = None,
        dx: float = 0.0,
        dy: float = 0.0,
        contours: list[list[tuple[float, float, int]]] | None = None,
        note: str = "",
        locked: bool = False,
        matrix: tuple[float, float, float, float] = (1, 0, 0, 1),
    ) -> None:
        self.world, self.id, self.owner = world, next(IDS), None
        self.isComponent = base is not None
        self.shapeData = ShapeData(world, base or "", note)
        self._transform = Transform(*matrix, dx, dy)
        self.contours = [Contour([Node(*n) for n in c]) for c in (contours or [])]
        self._locked = locked
        self.marker = f"shape-{self.id}"
        self.shapeData.marker = f"data-{self.id}"
        self.shapeData.builder.marker = f"builder-{self.id}"
        self.name = ""  # element name; ejectTo copies drop it
        self.other_composite = False  # a composite shape that is not a component

    @property
    def isComposite(self) -> bool:
        return self.isComponent or self.other_composite

    @property
    def transform(self) -> Transform:
        return self._transform

    @transform.setter
    def transform(self, value: Transform) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._transform = value

    @property
    def contentLocked(self) -> bool:
        # Like FontLab: the getter ORs in the always-locked component data.
        return self._locked or self.isComponent

    @contentLocked.setter
    def contentLocked(self, flag: bool) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if not self.world.ignore_writes:
            self._locked = flag

    def changed(self) -> None:
        pass

    @property
    def includesList(self) -> list["Shape"]:
        return self.world.layer(self.shapeData.componentGlyph, self.owner.master).shapes

    def ejectTo(self) -> list["Shape"]:
        """Copies with the transform applied; like FontLab, they lose raw flags and notes."""
        dx, dy = self._transform.dx(), self._transform.dy()
        copies = []
        for part in self.includesList:
            if part.isComponent:
                copy = Shape(
                    self.world,
                    part.shapeData.componentGlyph,
                    part.transform.dx() + dx,
                    part.transform.dy() + dy,
                )
            else:
                copy = Shape(
                    self.world,
                    contours=[
                        [(n.x + dx, n.y + dy, n.nodeState & ~SMOOTH) for n in c.nodes()]
                        for c in part.contours
                    ],
                )
                copy._locked = part._locked
            copies.append(copy)
        return copies


class Layer:
    isNull = False

    def __init__(
        self, world: "World", glyph: str, master: str, advance: float, auto: bool
    ) -> None:
        self.world, self.glyph, self.master, self.name = world, glyph, master, master
        self.marker = f"{glyph}/{master}"
        self.advanceWidth, self.autoLayer = advance, auto
        self.anchors: list[Any] = []
        self._shapes: list[Shape] = []

    @property
    def shapes(self) -> list[Shape]:
        return list(self._shapes)

    def add(self, shape: Shape) -> Shape:
        shape.owner = self
        self._shapes.append(shape)
        return shape

    def removeShape(self, shape: Shape) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        self._shapes = [s for s in self._shapes if s.id != shape.id]

    def insertShape(self, index: int, shape: Shape) -> Shape:
        shape.owner = self
        self._shapes.insert(index, shape)
        return shape

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

    def findLayerCreate(self, master: str) -> Layer:
        layer = Layer(self.world, self.name, master, 0, False)
        self.by_master[master] = layer
        self.world.events.append(("layer-created", f"{self.name}/{master}"))
        return layer

    def checkInitHistoryState(self, index: int) -> None:
        self.world.events.append(("init", self.name))

    @property
    def lastModified(self) -> Any:
        return self._modified

    @lastModified.setter
    def lastModified(self, value: Any) -> None:
        self._modified = value
        self.world.events.append(("stamp", self.name))


Spec = tuple  # ("c", base, dx, dy) component or ("o", [[(x, y, state)...]]) outline


class World:
    """One owned font: masters, glyphs, selection, history log, data tools."""

    def __init__(self, masters: tuple[str, ...] = ("Light", "Bold")) -> None:
        self.masters, self.master = list(masters), masters[0]
        self.glyphs: dict[str, Glyph] = {}
        self.selected: list[str] = []
        self.events: list[Any] = []
        self.calls: list[Any] = []
        self.ignore_writes = self.fail_write = self.fail_notify = False
        self.no_font = False
        self.builder_ok = self.update_ok = True
        self.pending: list[int] = []  # flGlyph.updatedFgGlyphs()
        self.stored: dict[str, Any] = {}  # get_glyph answers that replace the default
        self.build_errors: dict[tuple[str, str], Any] = {}
        self.package = NS(
            id=7,
            fgId=70,  # the fontpr font_id; differs from the flPackage id
            isNull=False,
            masters=self.masters,
            master=self.master,
            findName=lambda name: self.glyphs.get(name),
        )

    def glyph(
        self,
        name: str,
        shapes: dict[str, list[Spec]] | None = None,
        anchors: dict[str, list[tuple]] | None = None,
        auto: tuple[str, ...] = (),
        select: bool = True,
        advances: dict[str, float] | None = None,
        masters: tuple[str, ...] | None = None,
    ) -> Glyph:
        glyph = self.glyphs.setdefault(name, Glyph(self, name))
        for master in masters or self.masters:
            layer = Layer(
                self, name, master, (advances or {}).get(master, 500), master in auto
            )
            for pin in (anchors or {}).get(master, []):
                layer.anchors.append(
                    NS(
                        name=pin[0],
                        point=NS(x=lambda v=pin[1]: v, y=lambda v=pin[2]: v),
                    )
                )
            for spec in (shapes or {}).get(master, []):
                layer.add(self.make(spec))
            glyph.by_master[master] = layer
        if select:
            self.selected.append(name)
        return glyph

    def make(self, spec: Spec) -> Shape:
        if spec[0] == "c":
            _, base, dx, dy, *rest = spec
            options = rest[0] if rest else {}
            return Shape(self, base, dx, dy, **options)
        _, contours, *rest = spec
        return Shape(self, contours=contours, **(rest[0] if rest else {}))

    def layer(self, glyph: str, master: str | None = None) -> Layer:
        return self.glyphs[glyph].by_master[master or self.master]

    def notifications(self) -> list[Any]:
        return [e for e in self.events if e[0] == "notify"]

    def history(self) -> list[Any]:
        """The history-relevant events only: init, stamp, notify (markers)."""
        return [
            e[:3] if e[0] == "notify" else e
            for e in self.events
            if e[0] in {"init", "stamp", "notify"}
        ]

    # -- data tools (fontpr)
    def call(self, tool: str, **args: Any) -> Any:
        self.calls.append((tool, args))
        if tool == "get_glyph":
            return self.stored.get(args["glyph_name"]) or self.vfj(args["glyph_name"])
        if tool == "build_glyph":
            return self.build(args)
        raise AssertionError(tool)

    def vfj(self, name: str) -> dict:
        layers = []
        for master, layer in self.glyphs[name].by_master.items():
            elements = []
            for shape in layer.shapes:
                element: dict[str, Any] = (
                    {"component": {"glyphName": shape.shapeData.componentGlyph}}
                    if shape.isComponent
                    else {"elementData": {"contours": []}}
                )
                if shape._locked:
                    element["locked"] = True
                elements.append(element)
            layers.append({"name": master, "elements": elements})
        return {"name": name, "layers": layers}

    def build(self, args: dict) -> Any:
        key = (args["glyph_name"], args["layer_name"])
        if key in self.build_errors and not args["dry_run"]:
            error = self.build_errors[key]
            if isinstance(error, Exception):
                raise error
            return error
        glyph = self.glyphs.get(args["glyph_name"])
        if glyph is not None and glyph.findLayer(args["layer_name"]) is None:
            raise RuntimeError("Target layer not found.")
        parts = [
            p.split("@")[0] for p in args["recipe"][1:].replace("&", "+").split("+")
        ]
        resolved = [{"glyph_name": p} for p in parts]
        if args["dry_run"]:
            return {"status": "validated", "resolved_components": resolved}
        created = glyph is None
        if created:
            glyph = self.glyph(
                args["glyph_name"], masters=(args["layer_name"],), select=False
            )
        self.events.append(("build", args["glyph_name"], args["layer_name"]))
        return {"status": "ok", "created": created, "resolved_components": resolved}


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> World:
    """Install fake native modules; reset fly, fontlabapp and echopy around the test."""
    w = World()
    qt = make_qt()
    fontlab = ModuleType("fontlab")
    fontlab.flWorkspace = NS(
        instance=lambda: NS(currentPackage=None if w.no_font else w.package)
    )

    def notify(title: str, items: list, *flags: bool) -> None:
        if w.fail_notify:
            raise RuntimeError("boom notify")
        w.events.append(
            (
                "notify",
                title,
                [getattr(i, "marker", None) or i.name for i in items],
                items,
                flags,  # (True,) asks for deep history
            )
        )

    fontlab.flItems = lambda: NS(notifyChangesApplied=notify)
    fontlab.flNode = NS(NodeKind={"SmoothMask": SMOOTH})
    fontlab.CurrentGlyph = lambda: w.glyphs[w.selected[0]] if w.selected else None
    fontlab.CurrentFont = lambda: NS(glyphs=[NS(name=n, unicodes=[]) for n in w.glyphs])
    fontlab.MainWindow = lambda: NS(palette=Palette())
    fontlab.UpdateAll = lambda: w.events.append(("update-all",))
    fontlab.flGlyph = NS(updatedFgGlyphs=lambda: tuple(w.pending))
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
    # Isolate from other test files in the same run: they may have left spec-copied
    # `fontlabapp.*` modules or fakes behind. Snapshot, import the real packages afresh,
    # and put the snapshot back afterwards (monkeypatch restores what it deleted).
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
        monkeypatch.delitem(sys.modules, key)
    echopy = ModuleType("echopy")
    echopy.__path__ = []  # a package, so `echopy.fontpr` resolves from sys.modules
    fontpr = ModuleType("echopy.fontpr")
    fontpr.call = w.call
    echopy.fontpr = fontpr
    for name, module in (
        ("PythonQt", qt),
        ("fontlab", fontlab),
        ("FL", native),
        ("echopy", echopy),
        ("echopy.fontpr", fontpr),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(
        sys,
        "meta_path",
        [f for f in sys.meta_path if not getattr(f, "_fontlab_fly_alias", False)],
    )
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    Dialog.registry.clear()
    yield w
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
        del sys.modules[key]


def load(name: str) -> dict[str, Any]:
    namespace = runpy.run_path(str(FOLDER / f"{name}.py"), run_name="inspection")
    scripting = namespace["scripting"]
    assert scripting.__name__ == "fontlabapp.scripting", (
        "the real App helper, not a copy"
    )
    assert scripting._native.__module__ == "fontlabapp", "unpatched native loader"
    assert scripting.__file__.endswith("fontlabapp/scripting.py")
    for module in ("history", "edit_guards", "component_writer", "component_panel"):
        if module in namespace:  # only the App module, never a copy
            assert namespace[module] is app(module), module
    assert namespace["component_writer"] is app("component_writer")
    return namespace


def app(module: str) -> Any:
    """The real App module that the scripts of this test use (fresh per test)."""
    return importlib.import_module(f"fontlabapp.{module}")


def kernel(ns: dict[str, Any], key: str) -> Any:
    """A kernel name from fly.ap.component_writer.

    A script must not keep a private copy of a name that the App holds.
    """
    assert key not in ns, f"{key} must come from fly.ap.component_writer"
    return getattr(ns["component_writer"], key)


def panel_of(name: str) -> tuple[Any, dict[str, Any]]:
    namespace = load(name)
    return namespace["main"](), namespace


def texts(panel: Any) -> list[list[str]]:
    return panel.table.row_texts()


def press(panel: Any) -> None:
    """Click Apply the way Qt does: through the guarded slot."""
    panel.apply_button.clicked.emit()


def one_step(
    world: World,
    title: str,
    layers: list[str],
    glyphs: list[str],
    retained: list[str] | None = None,
) -> None:
    """Assert the one-Undo event shape: init layers+glyphs, stamp, ONE notify, stamp.

    `retained`: removed component, data and builder markers. They come first in
    the notify list, are never initialised, and ask for deep history (fl#7641).
    """
    assert world.history() == [
        *(("init", m) for m in layers),
        *(("init", g) for g in glyphs),
        *(("stamp", g) for g in glyphs),
        ("notify", title, [*(retained or []), *layers, *glyphs]),
        *(("stamp", g) for g in glyphs),
    ], world.history()
    flags = world.notifications()[0][4]
    assert flags == ((True,) if retained else ()), flags


def retained_of(shapes: list[Any]) -> list[str]:
    """Markers of (component, its data, its builder) per removed component."""
    return [f"{kind}-{s.id}" for s in shapes for kind in ("shape", "data", "builder")]


# ---------------------------------------------------------------- all seven: shape
JARGON = [
    "issue 122",
    "issue122",
    "S4",
    "D22",
    "D11",
    "S-L4",
    "reviewed App",
    "see fragment",
    "fragment",
    "Batch S",
    "AGENTS.md",
    "landmine",
]


@pytest.mark.parametrize("name", NAMES)
def test_script_when_parsed_then_python311_syntax_header_and_sections(
    name: str,
) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    lines = source.splitlines()
    assert lines[0] == f"# this_file: Scripts/Components/{name}.py", "this_file header"
    assert lines[1] == "# SPDX-License-Identifier: Apache-2.0"
    assert lines[2] == f"# FLM: Components · {name}"
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
        if f.returns is None
        and f.name != "__init__"
        or any(a.annotation is None for a in f.args.args if a.arg != "self")
    ]
    assert not untyped, f"{name}: functions without full type hints: {untyped}"
    calls = {
        getattr(n.func, "attr", "") for n in ast.walk(tree) if isinstance(n, ast.Call)
    }
    assert "UpdateAll" not in calls, "no UpdateAll after writes (fl#8537)"
    assert not calls & {"clone", "cloneCustom", "removeAllShapes"}, (
        "no shape clones and no removeAllShapes"
    )


@pytest.mark.parametrize("name", NAMES)
def test_public_text_when_read_then_has_no_internal_process_wording(name: str) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    found = [word for word in JARGON if word in source]
    assert not found, f"{name}: internal wording {found}"
    cited = ("fl#8516", "fl#8537", "fl#8538", "fl#7641")
    for issue in cited:
        source = source.replace(issue, "")
    assert "fl#" not in source, (
        "cite only the public FontLab issues this file relies on"
    )


BUILD_UNDO = (
    "FontLab's builder writes each layer itself, so Edit > Undo of a rebuilt "
    "existing layer depends on FontLab; Undo of a new glyph is FontLab's Add Glyph step."
)


@pytest.mark.parametrize("name", NAMES)
def test_public_text_when_read_then_promises_no_unmeasured_undo(name: str) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    doc = " ".join((ast.get_docstring(ast.parse(source)) or "").split())
    assert "Edit > Undo restores" not in source, "no unmeasured Undo promise"
    assert "not yet verified" not in doc, "no acceptance-status line"
    assert "bring it back" not in doc, "no unmeasured Undo promise"
    if name in EJECTORS:
        assert "recorded as one Undo step" in doc, "the design intent, not a promise"
        assert "Edit > Undo of removed components depends on FontLab (fl#7641)." in doc
        assert "not yet copied back" in doc, "say what a native copy still drops"
    if name == "Build From Recipes":
        assert BUILD_UNDO in doc, doc
        assert "PER BUILT LAYER" not in source and 'auto layers"' not in source


# Members of QWidget/QDialog/QPaintDevice that a Python subclass must not shadow:
# PythonQt raises "Slot ... can not be overwritten".
NATIVE_MEMBERS = {
    "metric", "update", "layout", "font", "palette", "parent", "style", "size",
    "pos", "width", "height", "geometry", "show", "hide", "open", "done", "accept",
    "reject", "exec", "repaint", "move", "resize", "rect", "title", "name",
    "windowTitle", "objectName", "children", "focus", "enabled", "visible",
    "actions", "cursor", "locale", "mask", "scroll", "find", "close",
}  # fmt: skip
PANEL_ONLY = {"close"}  # inherited, never redefined


@pytest.mark.parametrize("name", NAMES)
def test_panel_attributes_when_assigned_then_never_shadow_native_members(
    name: str,
) -> None:
    tree = ast.parse((FOLDER / f"{name}.py").read_text())
    panels = [
        cls
        for cls in ast.walk(tree)
        if isinstance(cls, ast.ClassDef)
        and cls.name not in {"Change", "Plan", "Line", "Result"}
        and not cls.name.endswith("Editor")
    ]
    assigned = {
        node.attr
        for cls in panels
        for node in ast.walk(cls)
        if isinstance(node, ast.Attribute)
        and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    }
    defined = {
        node.name
        for cls in panels
        for node in cls.body
        if isinstance(node, ast.FunctionDef)
    }
    clash = (assigned | defined) & (NATIVE_MEMBERS - PANEL_ONLY)
    assert not clash, clash


@pytest.mark.parametrize("name", NAMES)
def test_import_when_loaded_then_nothing_opens_until_main(
    world: World, name: str
) -> None:
    load(name)
    assert Dialog.registry == [], "import must not create a window"
    assert world.calls == [], "import must not call FontLab's data tools"


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_no_font_then_diagnoses_and_blocks_apply(
    world: World, name: str
) -> None:
    world.no_font = True
    panel, _ = panel_of(name)
    assert panel.subtitle.text == "Open a font first."
    assert not panel.apply_button.enabled and panel.close_button.enabled
    assert world.notifications() == []


@pytest.mark.parametrize("name", [n for n in WRITERS if n != "Nested Finder"])
def test_panel_when_nothing_selected_then_asks_for_selection(
    world: World, name: str
) -> None:
    world.glyph("A", shapes={"Light": [("o", [[(0, 0, 0)]])]}, select=False)
    panel, _ = panel_of(name)
    assert "Select glyphs" in panel.subtitle.text
    assert not panel.apply_button.enabled


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_closed_then_disconnects_deletes_and_unregisters(
    world: World, name: str
) -> None:
    world.glyph("A", shapes={"Light": [("o", [[(0, 0, 0)]])]})
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
    assert {"commit", "scan_auto_facts", "refusal"} <= used["fly.ap.history"]
    assert used["fly.ap.edit_guards"] == {"require_settled"}
    assert {
        "EjectEditor",
        "MoveEditor",
        "plain_move",
        "copy_problem",
        "Editor",
    } <= used["fly.ap.component_writer"]
    assert "panel_type" in used["fly.ap.component_panel"]
    check_real_app_names(used)


#: Names that live in the App; no script may hold a private copy.
SHARED = {
    "Change", "Plan", "Planner", "Work", "Editor", "EjectEditor", "MoveEditor",
    "collect", "require_safe", "blocked_rows", "apply_work", "settle", "shown",
    "refreshed", "keep_raw_state", "eject", "copy_problem", "part_counts",
    "parts_text", "MAX_DEPTH", "EPSILON", "plain_move", "half_up", "plural",
    "fmt", "layer_of", "components", "base_of", "offset", "offset_text",
    "shape_index", "ComponentPanel", "ink", "muted", "readable_palette",
    "ERROR_COLOR", "MAX_ROWS",
}  # fmt: skip


@pytest.mark.parametrize("name", NAMES)
def test_script_when_loaded_then_kernel_and_panel_are_the_app_modules(
    world: World, name: str
) -> None:
    ns = load(name)
    assert ns["component_writer"].__name__ == "fontlabapp.component_writer"
    assert ns["component_writer"].__file__.endswith("fontlabapp/component_writer.py")
    assert ns["component_panel"].__name__ == "fontlabapp.component_panel"
    panel = ns["main"]()
    base = ns["component_panel"].panel_type()
    assert isinstance(panel, base) and base.__module__ == "fontlabapp._component_panel"
    assert not SHARED & set(ns), f"private copies left: {SHARED & set(ns)}"


# ---------------------------------------------------------------- fixtures
def accented(world: World, select: bool = True) -> Glyph:
    """A (base, top 250/700) + acute (_top 100/500) -> Aacute = A + acute@(10, 10)."""
    world.glyph(
        "A",
        shapes={m: [("o", [[(0, 0, 0), (500, 0, SMOOTH)]])] for m in world.masters},
        anchors={"Light": [("top", 250, 700)], "Bold": [("top", 260, 720)]},
        select=False,
    )
    world.glyph(
        "acute",
        shapes={m: [("o", [[(0, 0, 0)], [(10, 10, SMOOTH)]])] for m in world.masters},
        anchors={"Light": [("_top", 100, 500)], "Bold": [("_top", 100, 500)]},
        select=False,
    )
    return world.glyph(
        "Aacute",
        shapes={m: [("c", "A", 0, 0), ("c", "acute", 10, 10)] for m in world.masters},
        select=select,
    )


# ---------------------------------------------------------------- shared write rules
def plan_for(name: str, ns: dict, world: World, glyph: str = "Aacute") -> Any:
    """The work list that each writer plans for the accented fixture (Light only)."""
    shapes = world.layer(glyph).shapes
    edits = {
        "Align By Anchor": [(shapes[1].id, (150.0, 200.0))],
        "Copy Offsets Between Masters": [(shapes[1].id, (12.0, 12.0))],
        "Decompose": [shapes[0].id],
        "Nested Finder": [shapes[0].id],
        "Replace Reference": [(shapes[1].id, "A")],
        "Unlock Lock": [(shapes[1].id, True, glyph)],
    }[name]
    return [(world.glyphs[glyph], world.layer(glyph), edits)]


def editor_for(name: str, ns: dict, world: World) -> Any:
    panel_class = {
        "Align By Anchor": "MoveEditor",
        "Copy Offsets Between Masters": "MoveEditor",
        "Decompose": "EjectEditor",
        "Nested Finder": "EjectEditor",
        "Replace Reference": "ReplaceEditor",
        "Unlock Lock": "LockEditor",
    }[name]
    if panel_class == "EjectEditor":
        return kernel(ns, panel_class)(unlock=False)
    if panel_class == "MoveEditor":
        return kernel(ns, panel_class)()
    if panel_class == "LockEditor":
        return ns[panel_class](world.package)
    return ns[panel_class]()


@pytest.mark.parametrize("name", WRITERS)
def test_apply_work_when_written_then_one_undo_step_of_layer_and_glyph(
    world: World, name: str
) -> None:
    accented(world)
    ns = load(name)
    facts = app("history").scan_auto_facts(world.package)
    work = plan_for(name, ns, world)
    removed = [world.layer("Aacute").shapes[0]] if name in EJECTORS else []
    result = kernel(ns, "apply_work")(
        work, ns["TITLE"], facts, editor_for(name, ns, world)
    )
    assert result == {"edits": 1, "layers": 1}
    one_step(world, ns["TITLE"], ["Aacute/Light"], ["Aacute"], retained_of(removed))
    assert ("changed", "Aacute/Light") in world.events, "layer settled inside history"
    assert "update-all" not in [e[0] for e in world.events]


@pytest.mark.parametrize("name", WRITERS)
def test_apply_work_when_write_fails_then_undo_hint_and_history_closed(
    world: World, name: str
) -> None:
    accented(world)
    ns = load(name)
    facts = app("history").scan_auto_facts(world.package)
    work = plan_for(name, ns, world)
    editor = editor_for(name, ns, world)
    steps = [(layer, editor.prepare(layer, edits)) for _, layer, edits in work]
    editor.prepare = lambda layer, edits: steps[0][1]
    world.fail_write = True
    with pytest.raises(app("history").PartialWriteError, match="use Edit > Undo"):
        kernel(ns, "apply_work")(work, ns["TITLE"], facts, editor)
    assert len(world.notifications()) == 1, "the partial edit stays one Undo step"


@pytest.mark.parametrize("name", WRITERS)
def test_apply_work_when_font_ignores_write_then_read_back_reports(
    world: World, name: str
) -> None:
    accented(world)
    ns = load(name)
    facts = app("history").scan_auto_facts(world.package)
    work = plan_for(name, ns, world)
    editor = editor_for(name, ns, world)
    if name in {"Decompose", "Nested Finder"}:
        editor.write = lambda layer, steps: None  # FontLab kept the component
    else:
        world.ignore_writes = True
    with pytest.raises(RuntimeError, match="did not store 1 change"):
        kernel(ns, "apply_work")(work, ns["TITLE"], facts, editor)


@pytest.mark.parametrize("name", WRITERS)
def test_require_safe_when_glyph_is_base_of_auto_composite_then_refuses(
    world: World, name: str
) -> None:
    accented(world)
    world.glyph("Aacutedot", shapes={"Light": [("c", "Aacute", 0, 0)]},
                auto=("Light",), select=False)  # fmt: skip
    ns = load(name)
    facts = app("history").scan_auto_facts(world.package)
    with pytest.raises(ValueError, match="Aacutedot"):
        kernel(ns, "require_safe")(plan_for(name, ns, world), facts)
    assert world.history() == []


@pytest.mark.parametrize("name", WRITERS)
def test_panel_when_glyph_updates_are_queued_then_refuses_and_never_clears_them(
    world: World, name: str
) -> None:
    accented(world)
    panel, _ = panel_of(name)
    world.pending.append(41)
    press(panel)
    assert "updates are pending" in panel.status.text
    assert world.history() == [] and world.pending == [41], "queue untouched"


@pytest.mark.parametrize("name", WRITERS)
def test_collect_when_layer_is_auto_then_listed_skipped_and_never_written(
    world: World, name: str
) -> None:
    accented(world)
    ns = load(name)
    world.layer("Aacute", "Bold").autoLayer = True
    glyph = world.glyphs["Aacute"]

    def planner(g: Any, master: str, layer: Any) -> list:
        return [kernel(ns, "Change")("acute", "old", "new", "edit")]

    plan = kernel(ns, "collect")([glyph], ["Light", "Bold"], planner)
    assert plan.skipped == ["Aacute/Bold"]
    assert [layer.master for _, layer, _ in plan.work] == ["Light"]
    assert (
        "Aacute · Bold",
        kernel(ns, "Change")("1 row", "", "auto layer, skipped"),
    ) in plan.rows


@pytest.mark.parametrize("name", WRITERS)
def test_apply_when_font_changed_since_scan_then_refuses_without_history(
    world: World, name: str
) -> None:
    accented(world)
    panel, _ = panel_of(name)
    world.package.id = 8
    press(panel)
    assert "font changed" in panel.status.text
    assert world.history() == []


# ---------------------------------------------------------------- Align By Anchor
def test_align_changes_when_anchors_differ_then_mark_lands_on_base_anchor(
    world: World,
) -> None:
    accented(world)
    ns = load("Align By Anchor")
    rows = ns["align_changes"](world.package, world.layer("Aacute"), "Light", None)
    # base (0, 0) + top (250, 700) - _top (100, 500) = (150, 200)
    assert [(r.name, r.old, r.new) for r in rows] == [
        ("acute @ top", "10, 10", "150, 200")
    ]
    bold = ns["align_changes"](
        world.package, world.layer("Aacute", "Bold"), "Bold", "top"
    )
    assert bold[0].new == "160, 220"
    assert ns["families"](world.package, [world.glyphs["Aacute"]], "Light") == ["top"]


def test_align_changes_when_half_unit_then_rounds_half_up_and_keeps_scaled(
    world: World,
) -> None:
    accented(world)
    world.layer("A").anchors[0] = NS(
        name="top", point=NS(x=lambda: 250.5, y=lambda: 700)
    )
    ns = load("Align By Anchor")
    rows = ns["align_changes"](world.package, world.layer("Aacute"), "Light", None)
    assert rows[0].new == "151, 200", "150.5 rounds half up"
    world.layer("Aacute").shapes[1]._transform = Transform(1.2, 0, 0, 1, 10, 10)
    rows = ns["align_changes"](world.package, world.layer("Aacute"), "Light", None)
    assert rows[0].new == "scaled or slanted, kept" and rows[0].edit is None
    rows = ns["align_changes"](world.package, world.layer("Aacute"), "Light", "bottom")
    assert rows[0].new == "no matching anchors"


def test_align_panel_when_applied_then_moves_offset_only_in_one_step(
    world: World,
) -> None:
    glyph = accented(world)
    mark = world.layer("Aacute").shapes[1]
    mark.shapeData.note = "keep me"
    panel, _ = panel_of("Align By Anchor")
    assert texts(panel) == [["Aacute · Light", "acute @ top", "10, 10", "150, 200"]]
    assert panel.apply_button.enabled
    press(panel)
    assert panel.status.text == "Moved 1 component on 1 layer", panel.status.text
    after = world.layer("Aacute").shapes[1]
    assert after is mark, "the original shape is edited in place, not copied"
    assert (after.transform.dx(), after.transform.dy()) == (150, 200)
    assert after.shapeData.note == "keep me"
    one_step(world, "Align Components by Anchor", ["Aacute/Light"], [glyph.name])
    assert texts(panel)[0][-1] == "in place"


# ---------------------------------------------------------------- Copy Offsets
def test_offset_changes_when_scaled_then_x_follows_width_ratio(world: World) -> None:
    accented(world)
    ns = load("Copy Offsets Between Masters")
    world.layer("Aacute", "Light").shapes[1]._transform = Transform(dx=40, dy=-12)
    world.layer("Aacute", "Bold").advanceWidth = 600
    source, target = world.layer("Aacute", "Light"), world.layer("Aacute", "Bold")
    plain = ns["offset_changes"](source, target, False)
    assert [(r.name, r.new) for r in plain] == [("A", "same"), ("acute", "40, -12")]
    scaled = ns["offset_changes"](source, target, True)
    assert scaled[1].new == "48, -12" and scaled[1].edit[1] == (48.0, -12.0)
    target.add(world.make(("c", "grave", 0, 0)))
    mismatch = ns["offset_changes"](source, target, False)
    assert [(r.new, r.edit) for r in mismatch] == [("different components, kept", None)]


def test_copy_panel_when_applied_then_targets_get_source_offsets(
    world: World,
) -> None:
    accented(world)
    world.layer("Aacute", "Light").shapes[1]._transform = Transform(dx=40, dy=-12)
    panel, _ = panel_of("Copy Offsets Between Masters")
    assert panel.chosen_masters() == ["Bold"]
    assert texts(panel) == [
        ["Aacute · Bold", "A", "0, 0", "same"],
        ["Aacute · Bold", "acute", "10, 10", "40, -12"],
    ]
    press(panel)
    bold = world.layer("Aacute", "Bold").shapes[1]
    assert (bold.transform.dx(), bold.transform.dy()) == (40, -12)
    one_step(world, "Copy Component Offsets", ["Aacute/Bold"], ["Aacute"])


def test_copy_panel_when_no_target_ticked_then_explains_and_blocks(
    world: World,
) -> None:
    accented(world)
    panel, _ = panel_of("Copy Offsets Between Masters")
    item = panel.target_list.item(0)
    item.setCheckState(0)
    panel.target_list.itemChanged.emit(item)
    assert panel.status.text == "Tick at least one target master."
    assert not panel.apply_button.enabled


# ---------------------------------------------------------------- Decompose
def test_decompose_panel_when_applied_then_parts_replace_component_in_place(
    world: World,
) -> None:
    accented(world)
    world.layer("A").shapes[0].shapeData.note = "stem note"
    world.layer("A").shapes[0].name = "stem"
    panel, _ = panel_of("Decompose")
    removed = world.layer("Aacute").shapes
    assert texts(panel) == [
        ["Aacute · Light", "A", "1 contour"],
        ["Aacute · Light", "acute", "2 contours"],
    ]
    press(panel)
    assert panel.status.text == "Decomposed 2 components on 1 layer", panel.status.text
    layer = world.layer("Aacute")
    assert [s.isComponent for s in layer.shapes] == [False, False]
    first, second = layer.shapes
    assert [(n.x, n.y, n.nodeState) for n in first.contours[0].nodes()] == [
        (0, 0, 0),
        (500, 0, SMOOTH),
    ], "raw Smooth bits copied back after the native copy"
    assert first.shapeData.note == "stem note", "element note copied back"
    assert first.name == "stem", "element name copied back"
    assert [(n.x, n.y) for n in second.contours[1].nodes()] == [(20, 20)], "placed"
    assert not first._locked and not second._locked, "decomposed parts are unlocked"
    assert ("builder-update",) in world.events, "component cache refreshed first"
    one_step(world, "Decompose Components", ["Aacute/Light"], ["Aacute"],
             retained_of(removed))  # fmt: skip
    assert world.layer("A").shapes[0].contours[0].nodes()[1].nodeState == SMOOTH


def test_decompose_when_base_is_composite_then_one_level_and_says_press_again(
    world: World,
) -> None:
    accented(world, select=False)
    world.glyph("Aacutedot", shapes={m: [("c", "Aacute", 5, 0)] for m in world.masters})
    panel, _ = panel_of("Decompose")
    assert texts(panel) == [
        [
            "Aacutedot · Light",
            "Aacute",
            "0 contours + 2 components (nested: press again)",
        ]
    ]
    press(panel)
    inner = world.layer("Aacutedot").shapes
    assert [(s.shapeData.componentGlyph, s.transform.dx()) for s in inner] == [
        ("A", 5),
        ("acute", 15),
    ]


def test_decompose_when_builder_refuses_then_error_before_history(
    world: World,
) -> None:
    accented(world)
    world.builder_ok = False
    panel, _ = panel_of("Decompose")
    press(panel)
    assert "could not refresh component" in panel.status.text
    assert world.history() == []


def nested_chain(world: World, case: str) -> str:
    """X uses B; B uses C plus an outline; C is an outline. Break it per `case`."""
    outline = ("o", [[(0, 0, 0)]])
    world.glyph("C", shapes={m: [outline] for m in world.masters}, select=False)
    world.glyph("B", shapes={m: [("c", "C", 0, 0), outline] for m in world.masters},
                select=False)  # fmt: skip
    world.glyph("X", shapes={m: [("c", "B", 5, 0)] for m in world.masters})
    if case == "auto base":
        world.layer("B").autoLayer = True
        return "base B has no plain layer Light"
    if case == "perspective":
        world.layer("C").shapes[0].transform.affine = False
        return "base C holds a shape that cannot be copied"
    if case == "other composite":
        world.layer("B").shapes[1].other_composite = True
        return "base B holds a shape that cannot be copied"
    if case == "cycle":
        world.layer("C").add(world.make(("c", "X", 0, 0)))
        return "components loop through X"
    if case == "plain":
        return ""
    chain = [f"g{index}" for index in range(70)]
    for name, inner in itertools.pairwise(chain):
        world.glyph(name, shapes={m: [("c", inner, 0, 0)] for m in world.masters},
                    select=False)  # fmt: skip
    world.glyph(chain[-1], shapes={m: [outline] for m in world.masters}, select=False)
    world.layer("C").add(world.make(("c", chain[0], 0, 0)))
    return "components nest more than 64 levels"


@pytest.mark.parametrize("name", EJECTORS)
@pytest.mark.parametrize(
    "case", ["auto base", "perspective", "other composite", "cycle", "deep"]
)
def test_eject_when_base_cannot_be_copied_then_row_blocked_before_history(
    world: World, name: str, case: str
) -> None:
    expected = nested_chain(world, case)
    panel, _ = panel_of(name)
    panel.scope.setCurrentIndex(0)  # current master only
    assert texts(panel)[0][-1] == expected, texts(panel)
    assert not panel.apply_button.enabled
    press(panel)
    assert expected in panel.status.text, panel.status.text
    assert world.history() == [] and ("builder-update",) not in world.events


@pytest.mark.parametrize("name", EJECTORS)
def test_eject_when_chain_is_plain_then_not_blocked(world: World, name: str) -> None:
    nested_chain(world, "plain")
    panel, _ = panel_of(name)
    panel.scope.setCurrentIndex(0)
    assert texts(panel) == [
        (["X · Light", "B", "C", "1 contour + 1 component"] if name == "Nested Finder"
         else ["X · Light", "B", "1 contour + 1 component (nested: press again)"])
    ]  # fmt: skip
    assert panel.apply_button.enabled


# ---------------------------------------------------------------- Nested Finder
def test_nested_panel_when_whole_font_chosen_then_lists_and_unnests_one_level(
    world: World,
) -> None:
    accented(world, select=False)
    world.glyph(
        "Aacutedot",
        shapes={
            m: [("c", "Aacute", 5, 0), ("o", [[(1, 1, 0)]])] for m in world.masters
        },
        select=False,
    )
    panel, _ = panel_of("Nested Finder")
    # Selected glyphs by default: a whole-font batch is refused as soon as any
    # glyph is an auto owner or base. All masters by default, like the sample.
    assert panel.glyph_scope.currentIndex == 0
    assert texts(panel) == [], "Selected glyphs: nothing is selected"
    panel.glyph_scope.setCurrentIndex(1)
    removed = [world.layer("Aacutedot", m).shapes[0] for m in world.masters]
    assert texts(panel) == [
        ["Aacutedot · Light", "Aacute", "A + acute", "0 contours + 2 components"],
        ["Aacutedot · Bold", "Aacute", "A + acute", "0 contours + 2 components"],
    ]
    press(panel)
    for master in world.masters:
        shapes = world.layer("Aacutedot", master).shapes
        assert [(s.isComponent, s.shapeData.componentGlyph) for s in shapes] == [
            (True, "A"),
            (True, "acute"),
            (False, ""),
        ], "inner components keep following their bases; own outline stays last"
        assert shapes[1].transform.dx() == 15
    one_step(
        world,
        "Nested Components",
        ["Aacutedot/Light", "Aacutedot/Bold"],
        ["Aacutedot"],
        retained_of(removed),
    )
    assert panel.status.text == "Unnested 2 components on 2 layers"


# ---------------------------------------------------------------- Replace Reference
def test_replace_panel_when_applied_then_base_changes_and_placement_stays(
    world: World,
) -> None:
    accented(world)
    world.glyph(
        "acute.case",
        shapes={m: [("o", [[(0, 0, 0)]])] for m in world.masters},
        select=False,
    )
    mark = world.layer("Aacute").shapes[1]
    panel, _ = panel_of("Replace Reference")
    assert panel.status.text == "Type both glyph names."
    panel.old_edit.setText("acute")
    panel.new_edit.setText("acute.case")
    assert not panel.apply_button.enabled and panel.timer.active, "debounced"
    panel.timer.timeout.emit()
    assert texts(panel) == [["Aacute · Light", "acute", "10, 10", "acute.case"]]
    press(panel)
    assert world.layer("Aacute").shapes[1] is mark, "same element, edited in place"
    assert mark.shapeData.componentGlyph == "acute.case"
    assert (mark.transform.dx(), mark.transform.dy()) == (10, 10)
    assert ("builder-update",) in world.events
    one_step(world, "Replace Component Reference", ["Aacute/Light"], ["Aacute"])


def test_replace_changes_when_unsafe_then_blocked_with_reason(world: World) -> None:
    accented(world)
    world.glyph("acute.cap", shapes={"Light": [("c", "Aacute", 0, 0)]},
                masters=("Light",), select=False)  # fmt: skip
    ns = load("Replace Reference")
    facts = app("history").scan_auto_facts(world.package)
    glyph, light = world.glyphs["Aacute"], world.layer("Aacute")
    cycle = ns["replace_changes"](
        world.package, glyph, light, "Light", ("acute", "acute.cap"), facts
    )
    assert "uses Aacute" in cycle[0].problem
    bold = world.layer("Aacute", "Bold")
    missing = ns["replace_changes"](
        world.package, glyph, bold, "Bold", ("acute", "acute.cap"), facts
    )
    assert missing[0].problem == "acute.cap has no layer Bold"
    light.shapes[1].shapeData.referenceCount = 2
    shared = ns["replace_changes"](
        world.package, glyph, light, "Light", ("acute", "A"), facts
    )
    assert shared[0].problem.startswith("shared element data")
    assert shared[0].edit is None


def test_replace_changes_when_component_names_its_layer_then_checks_that_layer(
    world: World,
) -> None:
    accented(world)
    world.glyph("acute.case", shapes={"Light": [("o", [[(0, 0, 0)]])]},
                masters=("Light",), select=False)  # fmt: skip
    ns = load("Replace Reference")
    facts = app("history").scan_auto_facts(world.package)
    bold = world.layer("Aacute", "Bold")
    bold.shapes[1].shapeData.componentLayer = "Light"
    rows = ns["replace_changes"](
        world.package, world.glyphs["Aacute"], bold, "Bold", ("acute", "acute.case"),
        facts,
    )  # fmt: skip
    assert [(r.problem, r.new) for r in rows] == [("", "acute.case")]


def test_replace_panel_when_cycle_appears_after_scan_then_apply_refuses(
    world: World,
) -> None:
    accented(world)
    world.glyph("acute.cap", shapes={m: [("o", [[(0, 0, 0)]])] for m in world.masters},
                select=False)  # fmt: skip
    panel, _ = panel_of("Replace Reference")
    panel.old_edit.setText("acute")
    panel.new_edit.setText("acute.cap")
    panel.timer.timeout.emit()
    assert panel.apply_button.enabled
    world.layer("acute.cap").add(world.make(("c", "Aacute", 0, 0)))
    press(panel)
    assert "uses Aacute" in panel.status.text, panel.status.text
    assert world.history() == [], "fresh component data before planning the write"


def test_replace_panel_when_new_glyph_missing_then_explains(world: World) -> None:
    accented(world)
    panel, _ = panel_of("Replace Reference")
    panel.old_edit.setText("acute")
    panel.new_edit.setText("nothing")
    panel.timer.timeout.emit()
    assert panel.status.text == "No glyph named nothing."
    assert not panel.apply_button.enabled


# ---------------------------------------------------------------- Unlock Lock
def test_lock_states_when_data_matches_then_own_flags_else_unknown(
    world: World,
) -> None:
    accented(world)
    ns = load("Unlock Lock")
    layer = world.layer("Aacute")
    layer.shapes[1]._locked = True
    stored = ns["explicit_locks"](world.package, "Aacute")
    assert world.calls[-1] == ("get_glyph", {"font_id": 70, "glyph_name": "Aacute"})
    assert ns["lock_states"](layer, stored["Light"]) == [False, True]
    swapped = [("acute", False), ("A", True)]
    assert ns["lock_states"](layer, swapped) == [None, None], "names must match"
    assert ns["lock_states"](layer, [("A", False)]) == [None, None], "count must match"
    assert ns["lock_states"](layer, None) == [None, None]


def test_lock_panel_when_applied_then_sets_own_flag_and_reads_back(
    world: World,
) -> None:
    accented(world)
    panel, _ = panel_of("Unlock Lock")
    assert texts(panel) == [
        ["Aacute · Light", "A", "unlocked", "locked"],
        ["Aacute · Light", "acute", "unlocked", "locked"],
    ], "the getter says locked for every component; the stored flags say otherwise"
    press(panel)
    assert panel.status.text == "Changed 2 components on 1 layer", panel.status.text
    assert [s._locked for s in world.layer("Aacute").shapes] == [True, True]
    assert world.layer("Aacute", "Bold").shapes[0]._locked is False, (
        "current master only"
    )
    one_step(world, "Lock and Unlock Components", ["Aacute/Light"], ["Aacute"])
    assert texts(panel)[0][-1] == "already locked"
    panel.action.setCurrentIndex(1)
    assert texts(panel)[0][2:] == ["locked", "unlocked"]


def test_lock_panel_when_data_does_not_match_then_unknown_and_no_write(
    world: World,
) -> None:
    accented(world)
    world.stored["Aacute"] = {"layers": [{"name": "Light", "elements": []}]}
    panel, _ = panel_of("Unlock Lock")
    assert [row[2:] for row in texts(panel)] == [
        ["unknown", "unknown, kept"],
        ["unknown", "unknown, kept"],
    ]
    assert not panel.apply_button.enabled
    assert panel.status.text == "Nothing to change"


def test_lock_panel_when_data_tool_fails_then_error_and_apply_off(world: World) -> None:
    accented(world)
    world.stored["Aacute"] = {"status": "error", "error": "no such glyph"}
    panel, _ = panel_of("Unlock Lock")
    assert panel.status.text == "Error: no such glyph"
    assert not panel.apply_button.enabled


# ---------------------------------------------------------------- Build From Recipes
def test_parse_when_lines_given_then_names_both_anchors_and_flags_problems(
    world: World,
) -> None:
    ns = load("Build From Recipes")
    lines = ns["parse"](
        "Aacute.alt = A + acute@acute  # comment\n"
        "\n"
        "fi = f & i\n"
        "bad line\n"
        "x y = A\n"
        "Adot = A + dot@top[_top]\n"
        "nb = A\xa0+ acute\n"
    )
    assert [(l.number, l.target, l.recipe, l.problem) for l in lines] == [
        (1, "Aacute.alt", "=A+acute@acute[_acute]", ""),
        (3, "fi", "=f&i", ""),
        (4, "bad line", "", "use: target = base + mark@anchor"),
        (5, "x y", "=A", "x y is not a valid glyph name"),
        (6, "Adot", "=A+dot@top[_top]", ""),
        (7, "nb = A\xa0+ acute", "", "remove the no-break space"),
    ]


def test_build_panel_when_checked_then_dry_run_with_package_id_and_options(
    world: World,
) -> None:
    accented(world, select=False)
    panel, _ = panel_of("Build From Recipes")
    # Opening never reaches the builder: its dry run can refresh glyph data.
    assert world.calls == [] and panel.status.text == "Press Check"
    assert not panel.apply_button.enabled
    assert not hasattr(panel, "auto"), "no auto-layer option (FontLab notifies it)"
    panel.reload_button.clicked.emit()
    assert world.calls == [
        (
            "build_glyph",
            {
                "font_id": 70,
                "glyph_name": "Aacute.alt",
                "recipe": "=A+acute@acute[_acute]",
                "layer_name": "Light",
                "replace": False,
                "auto_layer": False,
                "dry_run": True,
            },
        )
    ]
    assert texts(panel) == [
        ["Aacute.alt · Light", "=A+acute@acute[_acute]", "valid: A + acute"]
    ]
    assert panel.apply_button.enabled and panel.status.text == "1 of 1 layers ready"
    panel.recipes.setPlainText("Aacute.alt = A + acute@acute\nbroken\n")
    assert not panel.apply_button.enabled
    assert panel.status.text == "Recipes changed: press Check"
    panel.reload_button.clicked.emit()
    assert panel.status.text == "1 of 2 layers ready · fix the red lines"
    assert panel.table.colors()[1] == "#d33"


def test_build_panel_when_built_then_reports_layers_and_masters_still_to_build(
    world: World,
) -> None:
    accented(world, select=False)
    world.glyph("Agrave", masters=("Light",), select=False)
    panel, _ = panel_of("Build From Recipes")
    panel.scope.setCurrentIndex(1)
    panel.replace.setChecked(True)
    panel.recipes.setPlainText("Agrave = A + acute@top\nNew = A\n")
    panel.reload_button.clicked.emit()
    assert [row[-1] for row in texts(panel)] == [
        "valid: A + acute",
        "valid: adds layer Bold first",
        "valid: A",
        "new glyph: press Build again for Bold",
    ]
    world.events.clear()
    press(panel)
    assert [e for e in world.events if e[0] in {"build", "layer-created"}] == [
        ("layer-created", "Agrave/Bold"),
        ("build", "Agrave", "Light"),
        ("build", "Agrave", "Bold"),
        ("build", "New", "Light"),
    ]
    assert [n[1] for n in world.notifications()] == ["Add Master Layers"], (
        "the added layers are one Undo step; the builds are FontLab's own steps"
    )
    builds = [args for tool, args in world.calls if tool == "build_glyph"]
    assert builds and all(args["auto_layer"] is False for args in builds), (
        "never ask FontLab for an auto layer: it would notify an auto owner"
    )
    assert panel.status.text == (
        "Built 3 layers · added 1 empty layer · "
        "1 master still to build: press Build again"
    ), panel.status.text


def test_build_panel_when_target_is_base_of_auto_then_refused_before_any_build(
    world: World,
) -> None:
    accented(world, select=False)
    world.glyph(
        "Adot", shapes={"Light": [("c", "A", 0, 0)]}, auto=("Light",), select=False
    )
    panel, _ = panel_of("Build From Recipes")
    panel.recipes.setPlainText("A = acute\n")
    panel.reload_button.clicked.emit()
    assert texts(panel) == [["A", "=acute", "base of auto Adot"]]
    assert not panel.apply_button.enabled
    assert [c for c in world.calls if c[1]["glyph_name"] == "A"] == []


def test_build_panel_when_fontlab_fails_later_then_reports_and_keeps_others(
    world: World,
) -> None:
    accented(world, select=False)
    panel, _ = panel_of("Build From Recipes")
    world.build_errors[("Aacute.alt", "Light")] = {
        "status": "error",
        "error": "no anchor",
    }
    panel.reload_button.clicked.emit()
    press(panel)
    assert panel.status.text.endswith("1 failed: no anchor"), panel.status.text
    assert panel.table.colors() == ["#d33"]


def test_build_panel_when_updates_are_queued_then_refuses_before_any_build(
    world: World,
) -> None:
    accented(world, select=False)
    panel, _ = panel_of("Build From Recipes")
    world.pending.append(3)
    world.calls.clear()
    press(panel)
    assert "updates are pending" in panel.status.text
    assert world.calls == [] and world.pending == [3]
