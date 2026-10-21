# this_file: tests/test_issue122_S5.py
# SPDX-License-Identifier: Apache-2.0
"""Issue 122 batch S5: seven Anchors scripts on owned FontLab/Qt fakes.

The scripts run unchanged. Only the native modules `fontlab`, `FL` and
`PythonQt` are fakes; `fly` and `fontlabapp.scripting` are the real packages.
Offline results never prove native FontLab behaviour.
"""

import ast
import math
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest

ROOT = Path(__file__).parents[1]
ISOLATED = ("fly", "fontlabapp")  # top-level packages this file re-imports for itself
FOLDER = ROOT / "Scripts/Anchors"
NAMES = [
    "Rename Bulk",
    "Center Horizontally",
    "Place From Bounds",
    "Snap To Metrics",
    "Round To Grid",
    "Delete By Name",
    "Mirror Across Masters",
]
HEADER_STEMS = {
    "Rename Bulk": "anchors_rename_bulk",
    "Center Horizontally": "anchors_center_horizontally",
    "Place From Bounds": "anchors_place_from_bounds",
    "Snap To Metrics": "anchors_snap_to_metrics",
    "Round To Grid": "anchors_round_to_grid",
    "Delete By Name": "anchors_delete_by_name",
    "Mirror Across Masters": "anchors_mirror_across_masters",
}


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
        return "#808080"

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


class Spin(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.value = 0
        self.range = (0, 99)

    def setRange(self, low: float, high: float) -> None:
        self.range = (low, high)

    def setValue(self, value: float) -> None:
        self.value = value
        self.valueChanged.emit(value)


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

    def blockSignals(self, flag: bool) -> bool:
        return False


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
        ),
    )
    gui = NS(
        QDialog=Dialog,
        QLabel=Label,
        QLineEdit=LineEdit,
        QCheckBox=CheckBox,
        QComboBox=Combo,
        QSpinBox=Spin,
        QDoubleSpinBox=Spin,
        QSlider=Spin,
        QPushButton=Button,
        QTableWidget=Table,
        QTableWidgetItem=Item,
        QListWidget=ListWidget,
        QListWidgetItem=Item,
        QVBoxLayout=Widget,
        QHBoxLayout=Widget,
        QGridLayout=Widget,
        QPalette=Palette,
        QColor=Color,
        QBrush=lambda color: NS(color=lambda: color),
        QAbstractItemView=NS(NoEditTriggers=0, NoSelection=0),
        QHeaderView=NS(Stretch=0, ResizeToContents=1),
    )
    qt.QtCore, qt.QtGui = core, gui
    return qt


# ---------------------------------------------------------------- font fakes
class Pin:
    def __init__(
        self, world: "World", name: str, x: float, y: float, appearance: int = 0
    ) -> None:
        self.world, self.name, self.appearance, self.anchor = (
            world,
            name,
            appearance,
            True,
        )
        self._point = (x, y)
        self.marker = f"pin-{name}"

    @property
    def point(self) -> Any:
        x, y = self._point
        return NS(x=lambda: x, y=lambda: y)

    @point.setter
    def point(self, value: Any) -> None:
        if self.world.fail_write:
            raise RuntimeError("boom write")
        if self.world.ignore_writes:
            return
        x, y = value.x(), value.y()
        if self.world.strong_rounding:
            x, y = float(round(x)), float(round(y))
        self._point = (x, y)


class Layer:
    isNull = False

    def __init__(
        self,
        world: "World",
        glyph: str,
        master: str,
        advance: float,
        box: tuple,
        auto: bool,
    ) -> None:
        self.world, self.glyph, self.master = world, glyph, master
        self.marker = f"{glyph}/{master}"
        self.advanceWidth, self.autoLayer = advance, auto
        self.box = box
        self.anchors: list[Pin] = []
        self.shapes: list[Any] = []

    @property
    def boundingBox(self) -> Any:
        x, y, w, h = self.box
        return NS(x=lambda: x, y=lambda: y, width=lambda: w, height=lambda: h)

    def addAnchor(self, pin: Pin) -> None:
        self.anchors.append(pin)

    def removeAnchor(self, pin: Pin) -> None:
        self.anchors = [p for p in self.anchors if p is not pin]

    def checkInitHistoryState(self, index: int) -> None:
        self.world.events.append(("init", f"{self.glyph}/{self.master}"))


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
        self.ignore_writes = self.strong_rounding = False
        self.fail_write = self.fail_notify = False
        self.no_font = False
        self.pending: list[int] = []  # flGlyph.updatedFgGlyphs()
        self.metrics = {
            "Light": NS(xHeight=480.4, capsHeight=700, ascender=720, descender=-200),
            "Bold": NS(xHeight=520, capsHeight=710, ascender=730, descender=-210),
        }
        self.package = NS(
            id=7,
            isNull=False,
            masters=self.masters,
            master=self.master,
            italicAngle_value=-10.0,
            findName=lambda name: self.glyphs.get(name),
        )

    def glyph(
        self,
        name: str,
        advance: float = 500,
        box: tuple = (50, 0, 400, 700),
        anchors: dict[str, list[tuple]] | None = None,
        auto: tuple[str, ...] = (),
        components: dict[str, str] | None = None,
        select: bool = True,
        advances: dict[str, float] | None = None,
    ) -> Glyph:
        glyph = self.glyphs.setdefault(name, Glyph(self, name))
        for master in self.masters:
            layer = Layer(
                self,
                name,
                master,
                (advances or {}).get(master, advance),
                box,
                master in auto,
            )
            for pin in (anchors or {}).get(master, []):
                layer.anchors.append(Pin(self, *pin))
            if components and master in components:
                layer.shapes = [
                    NS(
                        isComponent=True,
                        shapeData=NS(componentGlyph=components[master]),
                    )
                ]
            glyph.by_master[master] = layer
        if select:
            self.selected.append(name)
        return glyph

    def layer(self, glyph: str, master: str | None = None) -> Layer:
        return self.glyphs[glyph].by_master[master or self.master]

    def points(self, glyph: str, master: str | None = None) -> dict[str, tuple]:
        return {p.name: p._point for p in self.layer(glyph, master).anchors}

    def notifications(self) -> list[Any]:
        return [e for e in self.events if e[0] == "notify"]


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> World:
    """Install fake native modules; reset fly and fontlabapp caches around the test."""
    w = World()
    qt = make_qt()
    fontlab = ModuleType("fontlab")
    fontlab.flWorkspace = NS(
        instance=lambda: NS(currentPackage=None if w.no_font else w.package)
    )
    fontlab.flPinPoint = lambda point: Pin(w, "", point.x(), point.y())

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
    fontlab.FontMetrics = lambda package, master: w.metrics[master]
    fontlab.MainWindow = lambda: NS(palette=Palette())
    fontlab.UpdateAll = lambda: w.events.append(("update-all",))
    fontlab.flGlyph = NS(updatedFgGlyphs=lambda: tuple(w.pending))
    names = lambda: list(w.glyphs)
    fl = NS(
        font=NS(),
        Selected=lambda index: names()[index] in w.selected,
    )

    class FLFont:
        def __len__(self) -> int:
            return len(w.glyphs)

        def __getitem__(self, index: int) -> Any:
            return NS(name=names()[index])

    fl.font = FLFont()
    native = ModuleType("FL")
    native.fl = fl
    for name, module in (("PythonQt", qt), ("fontlab", fontlab), ("FL", native)):
        monkeypatch.setitem(sys.modules, name, module)
    # Isolate from other test files in the same run: they may have left spec-copied
    # `fontlabapp.*` modules or fakes behind. Snapshot, import the real packages afresh,
    # and put the snapshot back afterwards (monkeypatch restores what it deleted).
    for key in [k for k in sys.modules if k.split(".")[0] in ISOLATED]:
        monkeypatch.delitem(sys.modules, key)
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
    return namespace


def panel_of(name: str) -> Any:
    namespace = load(name)
    return namespace["main"](), namespace


def texts(panel: Any) -> list[list[str]]:
    return panel.table.row_texts()


def tick(widget: Any, row: int, state: int) -> None:
    """Set a checklist state the way Qt does: the list then reports itemChanged."""
    item = widget.item(row)
    item.setCheckState(state)
    widget.itemChanged.emit(item)


# ---------------------------------------------------------------- all seven: shape
@pytest.mark.parametrize("name", NAMES)
def test_script_when_parsed_then_python311_syntax_header_and_sections(
    name: str,
) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    tree = ast.parse(source, feature_version=(3, 11))
    lines = source.splitlines()
    assert lines[0] == f"# this_file: Scripts/Anchors/{name}.py", "this_file header"
    assert lines[1] == "# SPDX-License-Identifier: Apache-2.0"
    assert lines[2] == f"# FLM: Anchors · {name}"
    doc = ast.get_docstring(tree) or ""
    for section in ("What", "How", "Why", "Use", "Benefit", "Safety", "Source"):
        assert f"\n\n{section}: " in doc, f"{name}: docstring lacks paragraph {section}"
    assert "\n\n- " in doc, "Markdown needs a blank line before the Safety list"
    assert f"{HEADER_STEMS[name]}.py" in doc and "Apache-2.0" in doc, "own-code credit"
    assert "D22" not in doc
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    untyped = [
        f.name
        for f in functions
        if f.returns is None
        and f.name != "__init__"
        or any(a.annotation is None for a in f.args.args if a.arg != "self")
    ]
    assert not untyped, f"{name}: functions without full type hints: {untyped}"
    assert not any(
        isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "UpdateAll"
        for n in ast.walk(tree)
    )


# Members of QWidget/QDialog/QPaintDevice that a Python subclass must not shadow:
# PythonQt raises "Slot ... can not be overwritten" (AGENTS.md host landmines).
NATIVE_MEMBERS = {
    "metric", "update", "layout", "font", "palette", "parent", "style", "size",
    "pos", "width", "height", "geometry", "show", "hide", "open", "done", "accept",
    "reject", "exec", "repaint", "move", "resize", "rect", "title", "name",
    "windowTitle", "objectName", "children", "focus", "enabled", "visible",
}  # fmt: skip


@pytest.mark.parametrize("name", NAMES)
def test_panel_attributes_when_assigned_then_never_shadow_native_members(
    name: str,
) -> None:
    tree = ast.parse((FOLDER / f"{name}.py").read_text())
    assigned = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    }
    defined = {
        node.name
        for cls in ast.walk(tree)
        if isinstance(cls, ast.ClassDef) and cls.name != "Plan"
        for node in cls.body
        if isinstance(node, ast.FunctionDef)
    }
    assert not (assigned | defined) & NATIVE_MEMBERS, (
        assigned | defined
    ) & NATIVE_MEMBERS


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
    world.glyph("a", anchors={"Light": [("top", 250, 700)]}, select=False)
    panel, _ = panel_of(name)
    assert "Select glyphs" in panel.subtitle.text
    assert not panel.apply_button.enabled


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_closed_then_disconnects_deletes_and_unregisters(
    world: World, name: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 250, 700)]})
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


# ---------------------------------------------------------------- shared safety rules
MOVERS = [
    "Center Horizontally",
    "Place From Bounds",
    "Snap To Metrics",
    "Round To Grid",
    "Mirror Across Masters",
]


@pytest.mark.parametrize("name", MOVERS)
def test_require_safe_when_existing_anchor_moves_to_origin_then_refuses(
    world: World, name: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 5, 5)]})
    ns = load(name)
    layer = world.layer("a")
    with pytest.raises(ValueError, match="Redo"):
        ns["require_safe"](
            [(world.glyphs["a"], layer, [("set", "top", (0, 0))])],
            ns["dependency_records"](world.package),
        )
    # A NEW anchor at 0, 0 and a move that stays off the origin are fine.
    ns["require_safe"](
        [(world.glyphs["a"], layer, [("set", "new", (0, 0)), ("set", "top", (0, 1))])],
        ns["dependency_records"](world.package),
    )


@pytest.mark.parametrize("name", NAMES)
def test_require_safe_when_glyph_is_base_of_auto_composite_then_refuses_with_names(
    world: World, name: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 250, 700)]})
    world.glyph("agrave", components={"Light": "a"}, select=False)
    world.glyph(
        "agravedot", auto=("Light",), components={"Light": "agrave"}, select=False
    )
    ns = load(name)
    work = [(world.glyphs["a"], world.layer("a"), [("remove", "top", None)])]
    with pytest.raises(ValueError, match="agravedot"):
        ns["require_safe"](work, ns["dependency_records"](world.package))
    other = [(world.glyphs["agrave"], world.layer("agrave"), [("remove", "top", None)])]
    with pytest.raises(ValueError, match="agravedot"):
        ns["require_safe"](other, ns["dependency_records"](world.package))
    world.glyph("b", select=False)
    ok = [(world.glyphs["b"], world.layer("b"), [("remove", "top", None)])]
    ns["require_safe"](ok, ns["dependency_records"](world.package))


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_glyph_updates_are_queued_then_refuses_and_never_clears_them(
    world: World, name: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698), ("bottom", 251, 4)]})
    panel, _ = panel_of(name)
    world.pending.append(41)
    with pytest.raises(ValueError, match="pending glyph updates"):
        panel.apply()
    assert world.events == [] and world.pending == [41], "queue untouched, no history"


@pytest.mark.parametrize("name", NAMES)
def test_collect_when_layer_is_auto_then_listed_skipped_and_never_written(
    world: World, name: str
) -> None:
    glyph = world.glyph(
        "a",
        anchors={"Light": [("top", 250, 700)], "Bold": [("top", 260, 700)]},
        auto=("Bold",),
    )
    ns = load(name)

    def planner(g: Any, master: str, layer: Any) -> list:
        return [ns["Change"]("top", "old", "new", ("remove", "top", None))]

    plan = ns["collect"]([glyph], ["Light", "Bold"], planner)
    assert plan.skipped == ["a/Bold"]
    assert [l.master for _, l, _ in plan.work] == ["Light"], (
        "auto layer must not enter the write list"
    )
    assert ("a · Bold" in [label for label, _ in plan.rows]) and plan.rows[-1][
        1
    ].new == "auto layer, skipped"


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_font_changed_since_scan_then_refuses_before_history(
    world: World, name: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698), ("bottom", 251, 4)]})
    panel, _ = panel_of(name)
    world.package.id = 99
    with pytest.raises(ValueError, match="font changed"):
        panel.apply()
    assert world.events == []


# ---------------------------------------------------------------- Round To Grid
def test_snap_when_halves_and_negatives_then_round_half_up(world: World) -> None:
    snap = load("Round To Grid")["snap"]
    assert [snap(v, 10) for v in (15, -15, -5, 5, 4, 14.5)] == [20, -10, 0, 10, 0, 10]
    assert snap(14.5, 1) == 15 and snap(-14.5, 1) == -14, (
        "halves round up, also with step 1"
    )


def test_round_panel_when_applied_then_exact_values_and_one_undo_step(
    world: World,
) -> None:
    world.glyph(
        "a",
        anchors={
            "Light": [("top", 203, 698.4), ("bottom", 251, -4)],
            "Bold": [("top", 210, 702)],
        },
    )
    world.glyph("b", anchors={"Light": [("top", 300, 700)]})
    panel, _ = panel_of("Round To Grid")
    assert texts(panel) == [
        ["a · Light", "top", "203, 698.4", "200, 700"],
        ["a · Light", "bottom", "251, -4", "250, 0"],
    ]
    assert (
        panel.status.text == "2 anchor changes on 1 layer"
        and panel.apply_button.enabled
    )
    panel.apply_button.clicked.emit()
    assert world.points("a") == {"top": (200, 700), "bottom": (250, 0)}
    assert world.points("a", "Bold") == {"top": (210, 702)}, "other master untouched"
    assert world.points("b") == {"top": (300, 700)}
    assert [e[0] for e in world.events] == [
        "init",
        "init",
        "stamp",
        "notify",
        "stamp",
    ], "one history step"
    assert world.events[0][1:] == ("a/Light",) and world.events[1][1:] == ("a",)
    assert world.notifications()[0][1:3] == ("Round Anchors to Grid", ["a/Light", "a"])
    assert panel.status.text == "Changed 2 anchors on 1 layer"
    assert texts(panel) == [] and not panel.apply_button.enabled
    assert ("update-all",) not in world.events, "UpdateAll queues cache ids (fl#8537)"


def test_round_panel_when_names_and_axes_set_then_only_those_move(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698.4), ("bottom", 251, -4)]})
    panel, _ = panel_of("Round To Grid")
    panel.names.setText("top")
    panel.do_y.setChecked(False)
    assert texts(panel) == [["a · Light", "top", "203, 698.4", "200, 698.4"]]
    panel.apply()
    assert world.points("a") == {"top": (200, 698.4), "bottom": (251, -4)}


def test_round_panel_when_scope_all_masters_then_every_layer_listed(
    world: World,
) -> None:
    world.glyph(
        "a", anchors={"Light": [("top", 203, 700)], "Bold": [("top", 214, 700)]}
    )
    panel, _ = panel_of("Round To Grid")
    panel.scope.setCurrentIndex(1)
    assert [r[0] for r in texts(panel)] == ["a · Light", "a · Bold"]
    assert panel.scope.items == ["Current master (Light)", "All masters (2)"]
    panel.apply()
    assert world.points("a", "Bold") == {"top": (210, 700)}
    assert world.notifications()[0][2] == ["a/Light", "a/Bold", "a"]


def test_round_panel_when_move_reaches_origin_then_refuses_before_history(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 3, -2)]})
    panel, _ = panel_of("Round To Grid")
    assert texts(panel) == [["a · Light", "top", "3, -2", "0, 0"]]
    assert not panel.apply_button.enabled and "Redo" in panel.status.text
    with pytest.raises(ValueError, match="Redo"):
        panel.apply()
    panel.apply_button.clicked.emit()
    assert panel.status.text.startswith("Error:") and world.events == [], (
        "no history, no write"
    )
    assert world.points("a") == {"top": (3, -2)}


def test_round_panel_when_glyph_is_base_of_auto_composite_then_refuses(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    world.glyph(
        "aacute",
        auto=("Light", "Bold"),
        components={"Light": "a", "Bold": "a"},
        select=False,
    )
    panel, _ = panel_of("Round To Grid")
    assert not panel.apply_button.enabled and "aacute" in panel.status.text
    with pytest.raises(ValueError, match="aacute"):
        panel.apply()
    assert world.events == [] and world.points("a") == {"top": (203, 698)}


def test_round_panel_when_names_repeat_on_layer_then_blocks_as_ambiguous(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698), ("top", 100, 100)]})
    panel, _ = panel_of("Round To Grid")
    assert (
        "several anchors named top" in panel.status.text
        and not panel.apply_button.enabled
    )


def test_round_panel_when_step_zero_or_no_axis_then_explains(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    panel, _ = panel_of("Round To Grid")
    panel.step.setValue(0)
    assert "at least 1" in panel.status.text and not panel.apply_button.enabled
    panel.step.setValue(10)
    panel.do_x.setChecked(False)
    panel.do_y.setChecked(False)
    assert "Tick x, y or both" in panel.status.text


def test_round_panel_when_scope_has_auto_layer_then_listed_and_apply_blocked(
    world: World,
) -> None:
    world.glyph(
        "a",
        anchors={"Light": [("top", 203, 698)], "Bold": [("top", 203, 698)]},
        auto=("Bold",),
    )
    panel, _ = panel_of("Round To Grid")
    panel.scope.setCurrentIndex(1)
    assert texts(panel)[-1] == ["a · Bold", "1 anchor", "", "auto layer, skipped"]
    assert (
        not panel.apply_button.enabled and "automatic composites" in panel.status.text
    )


def test_apply_when_font_ignores_writes_then_error_names_gap_after_history(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    panel, _ = panel_of("Round To Grid")
    world.ignore_writes = True
    with pytest.raises(RuntimeError, match=r"did not store 1 change.*a/top.*Undo"):
        panel.apply()
    assert len(world.notifications()) == 1, (
        "partial writes stay recoverable through Edit > Undo"
    )
    assert world.events[-1] == ("stamp", "a")


def test_apply_when_strong_rounding_alters_untouched_axis_then_no_false_alarm(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698.4)]})
    world.strong_rounding = True
    panel, _ = panel_of("Round To Grid")
    panel.do_y.setChecked(False)
    panel.apply()
    assert world.points("a") == {"top": (200.0, 698.0)}


def test_round_panel_when_updates_are_queued_then_preview_blocks_until_reload(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    world.pending.append(41)
    panel, _ = panel_of("Round To Grid")
    assert (
        "pending glyph updates" in panel.status.text and not panel.apply_button.enabled
    )
    world.pending.clear()
    panel.reload_button.clicked.emit()
    assert (
        panel.apply_button.enabled and panel.status.text == "1 anchor change on 1 layer"
    )


def test_round_panel_when_selection_changes_then_reload_button_rescans(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]}, select=False)
    panel, _ = panel_of("Round To Grid")
    assert texts(panel) == [] and "Select glyphs" in panel.subtitle.text
    world.selected.append("a")
    panel.reload_button.clicked.emit()
    assert texts(panel) == [["a · Light", "top", "203, 698", "200, 700"]]
    assert panel.subtitle.text == "1 glyph: a"


def test_round_panel_when_many_rows_then_preview_is_capped_but_edit_is_complete(
    world: World,
) -> None:
    pins = [(f"p{i}", 10 * i + 3, 7) for i in range(600)]
    world.glyph("a", anchors={"Light": pins})
    panel, _ = panel_of("Round To Grid")
    assert (
        panel.table.rows == 500 and panel.status.text == "600 anchor changes on 1 layer"
    )
    panel.apply()
    assert panel.status.text == "Changed 600 anchors on 1 layer"
    assert world.points("a")["p599"] == (5990, 10) and world.points("a")["p0"] == (
        0,
        10,
    )


# ---------------------------------------------------------------- Snap To Metrics
def test_metric_value_when_attribute_then_master_value_rounded_half_up(
    world: World,
) -> None:
    ns = load("Snap To Metrics")
    assert ns["metric_value"](world.package, "Light", "xHeight") == 480
    assert ns["metric_value"](world.package, "Bold", "xHeight") == 520
    assert ns["metric_value"](world.package, "Bold", None) == 0, "baseline"


def test_snap_changes_when_heights_differ_then_only_y_changes(world: World) -> None:
    world.glyph(
        "a", anchors={"Light": [("top", 250.5, 700), ("bottom", 250, 0), ("x", 1, 490)]}
    )
    ns = load("Snap To Metrics")
    changes = ns["snap_changes"](world.layer("a"), ["top", "x"], 490)
    assert [(c.name, c.old, c.new, c.edit) for c in changes] == [
        ("top", "250.5, 700", "250.5, 490", ("set", "top", (250.5, 490))),
    ], "x kept as stored; anchors already at the height produce no row"


def test_snap_panel_when_metric_and_offset_then_each_master_uses_its_own_value(
    world: World,
) -> None:
    world.glyph(
        "a", anchors={"Light": [("top", 250, 700)], "Bold": [("top", 260, 710)]}
    )
    panel, _ = panel_of("Snap To Metrics")
    panel.offset.setValue(10)
    assert texts(panel) == [["a · Light", "top", "250, 700", "250, 490"]]
    panel.scope.setCurrentIndex(1)
    assert panel.values.text == "x-height: Light 490, Bold 530"
    assert texts(panel)[1] == ["a · Bold", "top", "260, 710", "260, 530"]
    panel.apply()
    assert world.points("a") == {"top": (250, 490)} and world.points("a", "Bold") == {
        "top": (260, 530)
    }
    assert [e[0] for e in world.events] == ["init"] * 3 + ["stamp", "notify", "stamp"]
    assert world.notifications()[0][2] == ["a/Light", "a/Bold", "a"]


def test_snap_panel_when_baseline_would_put_anchor_on_origin_then_refuses(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 0, 15)]})
    panel, _ = panel_of("Snap To Metrics")
    panel.metric_box.setCurrentIndex(0)
    assert "Redo" in panel.status.text and not panel.apply_button.enabled
    panel.names.setText("")
    assert "Type the anchor names" in panel.status.text


# ---------------------------------------------------------------- Center Horizontally
def test_target_x_when_italic_advance_then_slanted_line_through_baseline_point(
    world: World,
) -> None:
    world.glyph("a", advance=500)
    ns = load("Center Horizontally")
    layer = world.layer("a")
    assert round(ns["target_x"](layer, "advance", 0.5, -10, 700), 2) == 373.43
    assert ns["half_up"](ns["target_x"](layer, "advance", 0.5, -10, 700)) == 373
    assert (
        ns["target_x"](layer, "advance", 0.0, 0, 700) == 0
        and ns["target_x"](layer, "advance", 1.0, 0, 0) == 500
    )
    assert ns["target_x"](layer, "advance", 0.5, 10, 700) == pytest.approx(
        250 - math.tan(math.radians(10)) * 700
    )


def test_target_x_when_ink_box_then_centre_line_and_none_for_empty(
    world: World,
) -> None:
    world.glyph("a", box=(50, 0, 400, 700))
    world.glyph("e", box=(0, 0, 0, 0))
    ns = load("Center Horizontally")
    assert ns["target_x"](world.layer("a"), "ink", 0.5, 0, 700) == 250
    assert ns["half_up"](ns["target_x"](world.layer("a"), "ink", 0.5, -10, 700)) == 312
    assert ns["target_x"](world.layer("e"), "ink", 0.5, 0, 700) is None


def test_center_panel_when_applied_then_x_moves_y_stays_and_angle_starts_from_font(
    world: World,
) -> None:
    world.glyph(
        "a",
        anchors={"Light": [("top", 250, 700), ("bottom", 250, 0), ("ogonek", 9, 9)]},
    )
    panel, _ = panel_of("Center Horizontally")
    assert panel.angle.value == -10.0, "starts from the font italic angle"
    assert texts(panel) == [["a · Light", "top", "250, 700", "373, 700"]]
    panel.apply_button.clicked.emit()
    assert world.points("a") == {
        "top": (373, 700),
        "bottom": (250, 0),
        "ogonek": (9, 9),
    }
    assert world.notifications()[0][1:3] == (
        "Center Anchors Horizontally",
        ["a/Light", "a"],
    )


def test_center_panel_when_slider_and_reference_change_then_table_follows(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 250, 700)]}, box=(50, 0, 400, 700))
    panel, _ = panel_of("Center Horizontally")
    panel.angle.setValue(0)
    assert texts(panel) == [] and panel.status.text == "0 anchor changes on 0 layers", (
        "already centred"
    )
    panel.position.setValue(100)
    assert panel.position_label.text == "100 %" and texts(panel) == [
        ["a · Light", "top", "250, 700", "500, 700"]
    ]
    panel.reference.setCurrentIndex(1)
    assert texts(panel) == [["a · Light", "top", "250, 700", "450, 700"]]
    panel.names.setText("")
    assert "Type the anchor names" in panel.status.text


# ---------------------------------------------------------------- Place From Bounds
def test_target_point_when_edges_and_offsets_then_exact_integers(world: World) -> None:
    ns = load("Place From Bounds")
    box = (50, 0, 450, 700)
    assert ns["target_point"](box, "top", 20) == (250, 720)
    assert ns["target_point"](box, "bottom", 10) == (250, -10)
    assert ns["target_point"]((50, 0, 451, 700), "top", 0) == (251, 700), (
        "centre rounds half up"
    )


def test_bounds_changes_when_layer_empty_then_nothing(world: World) -> None:
    world.glyph("e", box=(0, 0, 0, 0))
    ns = load("Place From Bounds")
    assert ns["bounds_changes"](world.layer("e"), [("top", "top", 0)]) == []


def test_place_panel_when_applied_then_new_pins_get_name_derived_appearance(
    world: World,
) -> None:
    world.glyph("a")
    panel, _ = panel_of("Place From Bounds")
    for name in ("_top", "_bottom"):
        panel.checks[name].setChecked(True)
    panel.offsets["top"].setValue(20)
    assert texts(panel) == [
        ["a · Light", "top", "–", "250, 720"],
        ["a · Light", "bottom", "–", "250, 0"],
        ["a · Light", "_top", "–", "250, 0"],
        ["a · Light", "_bottom", "–", "250, 700"],
    ]
    panel.apply()
    pins = {p.name: p for p in world.layer("a").anchors}
    assert {n: p._point for n, p in pins.items()} == {
        "top": (250, 720),
        "bottom": (250, 0),
        "_top": (250, 0),
        "_bottom": (250, 700),
    }
    assert {n: p.appearance for n, p in pins.items()} == {
        "top": 5,
        "bottom": 6,
        "_top": 6,
        "_bottom": 5,
    }
    assert all(p.anchor for p in pins.values())
    assert [e[0] for e in world.events] == ["init", "init", "stamp", "notify", "stamp"]


def test_place_panel_when_anchor_exists_then_moved_with_own_style_kept(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 100, 100, 9)]})
    panel, _ = panel_of("Place From Bounds")
    panel.checks["bottom"].setChecked(False)
    assert texts(panel) == [["a · Light", "top", "100, 100", "250, 700"]]
    panel.apply()
    pin = world.layer("a").anchors[0]
    assert pin._point == (250, 700) and pin.appearance == 9, (
        "existing appearance is native data"
    )


def test_place_panel_when_nothing_ticked_or_layer_empty_then_explains(
    world: World,
) -> None:
    world.glyph("e", box=(0, 0, 0, 0))
    panel, _ = panel_of("Place From Bounds")
    assert texts(panel) == [] and not panel.apply_button.enabled
    for name in ("top", "bottom"):
        panel.checks[name].setChecked(False)
    assert "Tick at least one anchor" in panel.status.text


# ---------------------------------------------------------------- Mirror Across Masters
def test_mirror_changes_when_scaled_then_x_follows_advance_ratio_half_up(
    world: World,
) -> None:
    world.glyph(
        "a",
        advances={"Light": 500, "Bold": 750},
        anchors={"Light": [("top", 125, 700), ("bottom", 250, 0)]},
    )
    ns = load("Mirror Across Masters")
    source, target = world.layer("a", "Light"), world.layer("a", "Bold")
    rows = ns["mirror_changes"](source, target, True, False)
    assert [(c.name, c.old, c.new) for c in rows] == [
        ("top", "–", "188, 700"),
        ("bottom", "–", "375, 0"),
    ]
    plain = ns["mirror_changes"](source, target, False, False)
    assert [c.new for c in plain] == ["125, 700", "250, 0"]


def test_mirror_changes_when_only_missing_or_equal_then_skips(world: World) -> None:
    world.glyph(
        "a",
        advances={"Light": 500, "Bold": 500},
        anchors={
            "Light": [("top", 125, 700), ("bottom", 250, 0)],
            "Bold": [("top", 1, 1), ("bottom", 250, 0)],
        },
    )
    ns = load("Mirror Across Masters")
    source, target = world.layer("a", "Light"), world.layer("a", "Bold")
    assert [
        (c.name, c.old, c.new)
        for c in ns["mirror_changes"](source, target, True, False)
    ] == [("top", "1, 1", "125, 700")]
    assert ns["mirror_changes"](source, target, True, True) == [], (
        "only-missing leaves existing anchors alone"
    )


def test_mirror_changes_when_source_names_repeat_then_blocked(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1), ("top", 2, 2)]})
    ns = load("Mirror Across Masters")
    rows = ns["mirror_changes"](
        world.layer("a", "Light"), world.layer("a", "Bold"), True, False
    )
    assert rows and rows[0].problem.startswith("several anchors named top")


def test_mirror_panel_when_applied_then_target_master_gets_scaled_anchors_once(
    world: World,
) -> None:
    world.glyph(
        "a",
        advances={"Light": 500, "Bold": 750},
        anchors={"Light": [("top", 125, 700), ("ogonek", 10, -5)]},
    )
    panel, _ = panel_of("Mirror Across Masters")
    assert panel.source.currentText == "Light"
    assert [(i.text(), i.checkState()) for i in panel.targets.items] == [
        ("Light", 0),
        ("Bold", 2),
    ]
    assert texts(panel) == [
        ["a · Bold", "top", "–", "188, 700"],
        ["a · Bold", "ogonek", "–", "15, -5"],
    ]
    panel.apply_button.clicked.emit()
    pins = {p.name: p for p in world.layer("a", "Bold").anchors}
    assert {n: p._point for n, p in pins.items()} == {
        "top": (188, 700),
        "ogonek": (15, -5),
    }
    assert {n: p.appearance for n, p in pins.items()} == {"top": 5, "ogonek": 0}
    assert world.points("a", "Light") == {"top": (125, 700), "ogonek": (10, -5)}, (
        "source untouched"
    )
    assert [e[0] for e in world.events] == ["init", "init", "stamp", "notify", "stamp"]
    assert world.notifications()[0][1:3] == (
        "Mirror Anchors Across Masters",
        ["a/Bold", "a"],
    )


def test_mirror_panel_when_single_master_or_no_target_then_explains(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 125, 700)]})
    panel, _ = panel_of("Mirror Across Masters")
    tick(panel.targets, 1, 0)
    assert "Tick the masters" in panel.status.text and not panel.apply_button.enabled
    world.masters.pop()
    solo, _ = panel_of("Mirror Across Masters")
    assert "one master" in solo.status.text


def test_mirror_panel_when_source_changes_then_it_is_excluded_from_targets(
    world: World,
) -> None:
    world.glyph("a", anchors={"Bold": [("top", 300, 700)]})
    panel, _ = panel_of("Mirror Across Masters")
    panel.source.setCurrentIndex(1)
    tick(panel.targets, 0, 2)
    tick(panel.targets, 1, 2)
    assert panel.chosen_masters() == ["Light"]
    assert texts(panel) == [["a · Light", "top", "–", "300, 700"]]


# ---------------------------------------------------------------- Rename Bulk
def test_renamer_when_plain_regex_empty_or_bad_then_expected(world: World) -> None:
    renamer = load("Rename Bulk")["renamer"]
    assert renamer("top", "up", False)("top_top") == "up_up"
    assert renamer("^(top|bottom)$", r"\1_alt", True)("bottom") == "bottom_alt"
    assert renamer("", "x", False)("top") == "top"
    with pytest.raises(ValueError, match="Pattern error"):
        renamer("(", "x", True)


def test_rename_changes_when_clash_empty_or_merge_then_rows_carry_problems(
    world: World,
) -> None:
    world.glyph(
        "a",
        anchors={
            "Light": [("top", 1, 1), ("bottom", 2, 2), ("a1", 3, 3), ("a2", 4, 4)]
        },
    )
    ns = load("Rename Bulk")
    layer = world.layer("a")
    plain = ns["rename_changes"](layer, ns["renamer"]("bottom", "top", False))
    assert [(c.name, c.edit, c.problem) for c in plain] == [
        ("bottom", None, "top is already used on this layer")
    ]
    empty = ns["rename_changes"](layer, ns["renamer"]("^top$", "", True))
    assert empty[0].problem == "the new name is empty" and empty[0].edit is None
    merge = ns["rename_changes"](layer, ns["renamer"](r"\d", "", True))
    assert sorted(c.problem for c in merge) == ["several anchors would become a"] * 2
    fine = ns["rename_changes"](layer, ns["renamer"]("top", "upper", False))
    assert [(c.name, c.new, c.edit, c.problem) for c in fine] == [
        ("top", "upper", ("rename", "top", "upper"), "")
    ]


def test_rename_panel_when_applied_then_names_change_nothing_else_and_one_undo(
    world: World,
) -> None:
    world.glyph(
        "a",
        anchors={
            "Light": [("top", 250, 700, 5), ("bottom", 250, 0, 6)],
            "Bold": [("top", 260, 700, 5)],
        },
    )
    panel, _ = panel_of("Rename Bulk")
    assert panel.apply_button.label == "Rename" and not panel.apply_button.enabled
    panel.find.setText("top")
    panel.replace.setText("upper")
    assert texts(panel) == [["a · Light", "top", "upper"]]
    panel.scope.setCurrentIndex(1)
    assert [r[0] for r in texts(panel)] == ["a · Light", "a · Bold"]
    panel.apply_button.clicked.emit()
    assert world.points("a") == {"upper": (250, 700), "bottom": (250, 0)}
    assert world.points("a", "Bold") == {"upper": (260, 700)}
    assert [p.appearance for p in world.layer("a").anchors] == [5, 6], (
        "appearance untouched"
    )
    assert [e[0] for e in world.events] == ["init"] * 3 + ["stamp", "notify", "stamp"]
    assert world.notifications()[0][1:3] == (
        "Rename Anchors in Bulk",
        ["a/Light", "a/Bold", "a"],
    )


def test_rename_panel_when_whole_font_scope_then_unselected_glyphs_included(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)]})
    world.glyph("b", anchors={"Light": [("top", 2, 2)]}, select=False)
    panel, _ = panel_of("Rename Bulk")
    panel.find.setText("top")
    panel.replace.setText("t")
    assert [r[0] for r in texts(panel)] == ["a · Light"]
    panel.glyph_scope.setCurrentIndex(1)
    assert [r[0] for r in texts(panel)] == ["a · Light", "b · Light"]


def test_rename_panel_when_bad_pattern_or_clash_then_nothing_applies(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1), ("bottom", 2, 2)]})
    panel, _ = panel_of("Rename Bulk")
    panel.regex.setChecked(True)
    panel.find.setText("(")
    assert (
        panel.status.text.startswith("Pattern error")
        and texts(panel) == []
        and not panel.apply_button.enabled
    )
    panel.regex.setChecked(False)
    panel.find.setText("bottom")
    panel.replace.setText("top")
    assert texts(panel) == [
        ["a · Light", "bottom", "top is already used on this layer"]
    ]
    assert not panel.apply_button.enabled and panel.status.text.startswith(
        "a · Light: top is already used"
    )
    with pytest.raises(ValueError, match="already used"):
        panel.apply()
    assert world.events == []


# ---------------------------------------------------------------- Delete By Name
def test_census_when_masters_and_auto_layers_then_counts_per_name(world: World) -> None:
    world.glyph(
        "a",
        anchors={"Light": [("top", 1, 1), ("bottom", 2, 2)], "Bold": [("top", 3, 3)]},
        auto=("Bold",),
    )
    world.glyph("b", anchors={"Light": [("top", 1, 1)]})
    census = load("Delete By Name")["census"]
    glyphs = [world.glyphs["a"], world.glyphs["b"]]
    assert census(glyphs, ["Light", "Bold"]) == {"bottom": [1, 0], "top": [2, 1]}
    assert census(glyphs, ["Light"]) == {"bottom": [1, 0], "top": [2, 0]}


def test_delete_panel_when_names_ticked_then_all_pins_with_that_name_go_in_one_step(
    world: World,
) -> None:
    world.glyph(
        "a", anchors={"Light": [("top", 1, 1), ("top", 5, 5), ("bottom", 2, 2)]}
    )
    world.glyph("b", anchors={"Light": [("top", 1, 1)]})
    panel, _ = panel_of("Delete By Name")
    assert [i.text() for i in panel.list.items] == [
        "bottom    -  1 layer",
        "top    -  2 layers",
    ]
    assert not panel.apply_button.enabled and "Tick the names" in panel.status.text
    tick(panel.list, 1, 2)
    assert texts(panel) == [
        ["a · Light", "top", "delete"],
        ["b · Light", "top", "delete"],
    ]
    panel.apply_button.clicked.emit()
    assert world.points("a") == {"bottom": (2, 2)} and world.points("b") == {}
    assert [e[0] for e in world.events] == ["init"] * 4 + [
        "stamp",
        "stamp",
        "notify",
        "stamp",
        "stamp",
    ]
    assert world.notifications()[0][2] == ["a/Light", "b/Light", "a", "b"]
    assert panel.status.text == "Changed 3 anchors on 2 layers", (
        "counts pins, also duplicates"
    )
    assert [i.text() for i in panel.list.items] == ["bottom    -  1 layer"]


def test_delete_panel_when_scope_changes_then_checklist_counts_follow(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)], "Bold": [("top", 3, 3)]})
    panel, _ = panel_of("Delete By Name")
    assert [i.text() for i in panel.list.items] == ["top    -  1 layer"]
    panel.scope.setCurrentIndex(1)
    assert [i.text() for i in panel.list.items] == ["top    -  2 layers"]


def test_delete_changes_when_name_absent_then_no_row(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)]})
    delete_changes = load("Delete By Name")["delete_changes"]
    assert delete_changes(world.layer("a"), {"nope"}) == []


# ---------------------------------------------------------------- review fix round 1
JARGON = (
    "D22",
    "S-L4",
    "batch S5",
    "fragment",
    "AGENTS.md",
    "landmine",
    "reviewed anchor",
    "reviewed write",
    "App helper",
)


@pytest.mark.parametrize("name", NAMES)
def test_public_script_when_read_then_no_internal_jargon(name: str) -> None:
    source = (FOLDER / f"{name}.py").read_text()
    found = [word for word in JARGON if word in source]
    assert not found, f"{name}: internal jargon in a public script: {found}"
    doc = ast.get_docstring(ast.parse(source)) or ""
    assert "the author's own FontLab sample" in doc and "Apache-2.0" in doc


@pytest.mark.parametrize("name", NAMES)
def test_docstring_when_script_adds_no_pins_then_never_claims_pin_appearance(
    name: str,
) -> None:
    doc = ast.get_docstring(ast.parse((FOLDER / f"{name}.py").read_text())) or ""
    adds = name in ("Place From Bounds", "Mirror Across Masters")
    assert ("appearance" in doc) == adds, (
        f"{name}: appearance claim must match behaviour"
    )


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("stage", ["write", "notify"])
def test_apply_when_native_step_fails_after_history_started_then_undo_hint_chained(
    world: World, name: str, stage: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698), ("bottom", 251, 4)]})
    panel, namespace = panel_of(name)
    if name == "Delete By Name":
        tick(panel.list, 1, 2)
    elif name == "Rename Bulk":
        panel.find.setText("top")
        panel.replace.setText("up")
    elif name == "Place From Bounds":
        world.layer("a").anchors.clear()
        panel.refresh()
    assert panel.apply_button.enabled, name

    def broken(*args: Any) -> None:
        raise RuntimeError("boom write")

    if stage == "write":
        namespace["apply_work"].__globals__["write"] = broken
    else:
        world.fail_notify = True
    with pytest.raises(
        RuntimeError, match=r"Native changes may remain; use Edit > Undo"
    ) as raised:
        panel.apply()
    assert isinstance(raised.value.__cause__, RuntimeError) and "boom" in str(
        raised.value.__cause__
    )


def test_rename_when_replacement_template_is_bad_then_table_and_apply_agree(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)]})
    panel, _ = panel_of("Rename Bulk")
    panel.regex.setChecked(True)
    panel.find.setText("(top)")
    panel.replace.setText("\\2")
    assert texts(panel) == [] and not panel.apply_button.enabled
    assert panel.status.text.startswith("Pattern error")
    with pytest.raises(ValueError, match="Pattern error"):
        panel.apply()
    assert world.events == []


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_first_load_raises_then_opens_with_error_and_no_apply(
    world: World, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    namespace = load(name)

    def broken() -> list[str]:
        raise OSError("selection unreadable")

    monkeypatch.setattr(namespace["scripting"], "names_selected_names", broken)
    panel = namespace["main"]()
    assert (
        panel.status.text.startswith("Error:")
        and "selection unreadable" in panel.status.text
    )
    assert not panel.apply_button.enabled and panel.close_button.enabled


def test_center_when_reloaded_then_user_angle_is_kept_and_all_masters_warns(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 250, 700)]})
    panel, _ = panel_of("Center Horizontally")
    assert panel.angle.value == -10.0
    panel.angle.setValue(-5)
    panel.reload_button.clicked.emit()
    assert panel.angle.value == -5, "Reload selection must not undo the user's angle"
    assert panel.warning.text == ""
    panel.scope.setCurrentIndex(1)
    assert "every chosen master" in panel.warning.text
    panel.scope.setCurrentIndex(0)
    assert panel.warning.text == ""


def test_apply_when_current_master_changed_since_scan_then_refuses(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    panel, _ = panel_of("Round To Grid")
    world.package.master = "Bold"
    with pytest.raises(ValueError, match="Master changed; Reload"):
        panel.apply()
    assert world.events == []


def test_apply_when_a_glyph_vanished_since_scan_then_refuses(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 203, 698)]})
    panel, _ = panel_of("Round To Grid")
    del world.glyphs["a"]
    with pytest.raises(ValueError, match="Glyphs changed; Reload"):
        panel.apply()
    assert world.events == []


def test_table_when_rows_are_skipped_or_blocked_then_skipped_is_muted_not_error_red(
    world: World,
) -> None:
    world.glyph(
        "a",
        anchors={"Light": [("top", 203.4, 698.4)], "Bold": [("top", 203.4, 698.4)]},
        auto=("Bold",),
    )
    panel, _ = panel_of("Round To Grid")
    panel.scope.setCurrentIndex(1)

    def last(row: int) -> Any:
        return panel.table.cells[(row, 3)].foreground.color().value

    rows = texts(panel)
    skipped = [i for i, row in enumerate(rows) if row[3] == "auto layer, skipped"]
    live = [i for i, row in enumerate(rows) if row[3] == "200, 700"]
    assert skipped and live, rows
    assert {last(i) for i in skipped} == {"#808080"}, "skip rows use the muted colour"
    assert last(live[0]) not in ("#808080", "#d33"), "a live change keeps the accent"
    world.glyph("b", anchors={"Light": [("top", 1, 1), ("top", 2, 2)]}, select=False)
    world.selected[:] = ["b"]
    panel.reload_button.clicked.emit()
    assert last(0) == "#d33", "blocked row stays error red"


def test_rename_whole_font_when_bases_of_auto_composites_then_blocked_glyphs_are_rows(
    world: World,
) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)]})
    world.glyph("b", anchors={"Light": [("top", 2, 2)]}, select=False)
    world.glyph("aacute", auto=("Light",), components={"Light": "a"}, select=False)
    panel, _ = panel_of("Rename Bulk")
    panel.glyph_scope.setCurrentIndex(1)
    panel.timer.starts = 0
    panel.find.setText("top")
    panel.replace.setText("t")
    assert panel.timer.starts == 2 and panel.timer.active, (
        "whole-font typing is debounced"
    )
    assert texts(panel) == [], "no replanning per keystroke"
    panel.timer.timeout.emit()
    rows = texts(panel)
    assert ["a", "blocked", "base of automatic composite aacute"] in rows
    assert ["b · Light", "top", "t"] in rows and ["a · Light", "top", "t"] in rows
    assert rows[0][1] == "blocked", (
        "blocked rows come first, so the row limit never hides them"
    )
    assert not panel.apply_button.enabled and "aacute" in panel.status.text


def test_rename_selected_scope_when_typing_then_still_immediate(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)]})
    panel, _ = panel_of("Rename Bulk")
    panel.find.setText("top")
    panel.replace.setText("t")
    assert texts(panel) == [["a · Light", "top", "t"]] and panel.timer.starts == 0


def test_timer_when_panel_closes_then_it_is_stopped(world: World) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 1)]})
    panel, _ = panel_of("Rename Bulk")
    panel.glyph_scope.setCurrentIndex(1)
    panel.find.setText("top")
    assert panel.timer.active
    panel.close_button.clicked.emit()
    assert not panel.timer.active
