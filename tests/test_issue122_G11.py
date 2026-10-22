# this_file: tests/test_issue122_G11.py
# SPDX-License-Identifier: Apache-2.0
"""Independent anchor tools on real App helpers and owned native fakes."""

import ast
import math
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest
from conftest import app_names_used, check_real_app_names

ISOLATED = ("fly", "fontlabapp")


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
    "returnPressed",
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


ROOT = Path(__file__).parents[1]
FOLDER = ROOT / "Scripts" / "Anchors"
TITLES = [
    "Add Anchors From File",
    "Copy Myanmar Anchors",
    "Derive Anchors From Components",
    "Optical Center",
    "Remove Extraneous Mark Anchors",
    "Auto Cursive Attachment Add Anchors",
    "Auto Cursive Attachment Get Sample",
]


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(FOLDER / (title + ".py")), run_name="inspection")


@pytest.mark.parametrize("title", TITLES)
def test_import_and_public_header(world: Any, title: str) -> None:
    code = (FOLDER / (title + ".py")).read_text()
    tool = load(title)
    assert callable(tool["main"])
    assert "Simon Cozens" in tool["__doc__"] and "MIT" in tool["__doc__"]
    assert "this_file: Scripts/Anchors/" + title + ".py" in code
    assert code.splitlines()[2] == f"# FLM: Anchors · {title}"
    assert all(
        label in tool["__doc__"]
        for label in ("What:", "How:", "Why:", "Use:", "Benefit:")
    )
    forbidden = {"render", "size", "layout", "update", "font", "move", "statusBar"}
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.ClassDef):
            assert not (
                {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                & forbidden
            )
    assert "Undo restores" not in code


def test_real_app_names() -> None:
    check_real_app_names(app_names_used([FOLDER / (n + ".py") for n in TITLES]))


def test_csv_exact_values_and_blank_cells(world: Any) -> None:
    read = load(TITLES[0])["parse_table"]
    assert read("name,top_x,top_y,bottom_x,bottom_y\na,12,600,,\n") == {
        "a": {"top": (12, 600)}
    }
    assert read("glyph,top_x,top_y\na,-2.5,600.25\n") == {"a": {"top": (-2, 600)}}


@pytest.mark.parametrize(
    "text",
    [
        "name,top_x\na,2\n",
        "name,top_x,top_y\na,nan,2\n",
        "name,top_x,top_y\na,2,\n",
        "name,top_x,top_y\na,1,2\na,2,3\n",
        "name,top_x,top_y\na\u00a0,1,2\n",
        "x,y\n1,2\n",
    ],
)
def test_csv_refuses_malformed_input(world: Any, text: str) -> None:
    with pytest.raises(ValueError):
        load(TITLES[0])["parse_table"](text)


def test_mark_removals_are_conditional_and_all_master_one_step(world: Any) -> None:
    world.glyph(
        "acute",
        anchors={
            "Light": [("_top", 20, 0), ("bottom", 20, -10), ("top", 20, 100)],
            "Bold": [("_bottom", 30, 100), ("top", 30, 200)],
        },
    )
    panel = load(TITLES[4])["main"]()
    panel.apply()
    assert set(world.points("acute")) == {"_top", "top"}
    assert set(world.points("acute", "Bold")) == {"_bottom"}
    assert len(world.notifications()) == 1
    assert world.notifications()[0][2] == ["acute/Light", "acute/Bold", "acute"]


@pytest.mark.parametrize("bad", ["auto", "pending", "partial"])
def test_writer_refusals_and_partial_failure(
    world: Any, bad: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.glyph(
        "mark",
        anchors={"Light": [("_top", 1, 2), ("bottom", 4, 5)]},
        auto=("Bold",) if bad == "auto" else (),
    )
    panel = load(TITLES[4])["main"]()
    if bad == "pending":
        world.pending = [123]
    if bad == "partial":

        def fail(pin: Any) -> None:
            raise RuntimeError("injected anchor removal failure")

        monkeypatch.setattr(world.layer("mark"), "removeAnchor", fail)
    message = {
        "auto": "has auto layers",
        "pending": "pending",
        "partial": "Native changes may remain; use Edit > Undo",
    }[bad]
    if bad == "pending":
        panel.apply()
        assert world.pending == [123] and world.notifications()
        assert panel.last_result["pending_updates"] == (123,)
        assert "8537" in panel.last_result["pending_note"] and panel.last_result["pending_note"] in panel.status.text
        return
    with pytest.raises((ValueError, RuntimeError), match=message):
        panel.apply()
    assert len(world.notifications()) == (1 if bad == "partial" else 0)


def test_no_font_panel_refuses_write(world: Any) -> None:
    world.no_font = True
    panel = load(TITLES[4])["main"]()
    assert not panel.apply_button.enabled
    with pytest.raises(ValueError):
        panel.apply()


def test_myanmar_routing_uses_unicode_not_names(world: Any) -> None:
    route = load(TITLES[1])["route_names"]
    rows = [
        ("round", "U+101D", ""),
        ("angular", "U+1000", ""),
        ("target", "U+1001", ""),
        ("other", "U+1003", ""),
    ]
    assert route(rows) == {"target": "round", "other": "angular"}
    with pytest.raises(ValueError, match="source"):
        route(rows[1:])


def test_component_affine_inverse(world: Any) -> None:
    project = load(TITLES[2])["attachment_in_base"]
    assert project((10, 20), (2, 0, 0, 3, 5, 7), (1, 0, 0, 1, 8, 12)) == (17, 55)
    assert project((10, 20), (1, 0, 0, 1, 100, 200), (2, 0, 0, 2, 10, 20)) == (50, 100)
    with pytest.raises(ValueError):
        project((1, 2), (1, 0, 0, 1, 0, 0), (0, 0, 0, 0, 0, 0))


def test_optical_median_uses_absolute_origin(world: Any) -> None:
    calc = load(TITLES[3])["optical_position"]
    assert calc([(100, 1), (110, 3), (120, 1)], 100, 140) == pytest.approx(
        116.6666666667
    )
    with pytest.raises(ValueError):
        calc([], 0, 10)


@pytest.mark.parametrize("title", TITLES[-2:])
def test_cursive_strip_edges_and_tangents(world: Any, title: str) -> None:
    tool = load(title)
    rings = [[(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)]]
    assert tool["vertical_spans"](rings, 50) == [(0, 40, 0, 0)]
    assert tool["vertical_spans"](rings, 110) == []
    profile = tool["measure_sample"](rings, [(50, 10)])
    assert profile == {"below": 10, "above": 30, "lower_angle": 0, "upper_angle": 0}
    with pytest.raises(ValueError):
        tool["measure_sample"](rings, [(50, 100)])


def test_cursive_exact_zero_score_and_form_routing(world: Any) -> None:
    tool = load(TITLES[-2])
    rings = [[(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)]]
    profile = {"below": 10, "above": 30, "lower_angle": 0, "upper_angle": 0}
    assert tool["choose_attachment"](rings, profile, [10, 20]) == (10, 10)
    assert tool["needed_connections"]("beh.medi") == ["exit", "entry"]
    assert tool["needed_connections"]("beh.isol") == []


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"below": -1, "above": 3, "lower_angle": 0, "upper_angle": 0},
        {"below": 0, "above": 0, "lower_angle": 0, "upper_angle": 0},
        {"below": 1, "above": 2, "lower_angle": math.nan, "upper_angle": 0},
    ],
)
def test_cursive_bad_profile(world: Any, data: dict) -> None:
    with pytest.raises(ValueError):
        load(TITLES[-2])["validate_profile"](data)


@pytest.fixture(autouse=True)
def reject_native_member_assignments(monkeypatch: pytest.MonkeyPatch) -> None:
    forbidden = {"render", "size", "layout", "update", "font", "move", "statusBar"}

    def checked_setattr(self: Any, name: str, value: Any) -> None:
        if name in forbidden:
            raise AssertionError("Native widget member collision: " + name)
        object.__setattr__(self, name, value)

    monkeypatch.setattr(Dialog, "__setattr__", checked_setattr)


def catalogue(monkeypatch: pytest.MonkeyPatch, rows: list) -> None:
    import fly.ap.glyph_catalog as glyph_catalog  # noqa: PLR0402

    monkeypatch.setattr(glyph_catalog, "capture", lambda: NS(rows=rows))


def test_csv_panel_reads_replaced_file_before_apply(world: Any, tmp_path: Path) -> None:
    world.glyph("a")
    path = tmp_path / "anchors.csv"
    path.write_text("name,top_x,top_y\na,12,600\n")
    panel = load(TITLES[0])["main"]()
    panel.csv_path.text = str(path)
    panel.reload()
    assert panel.apply_button.enabled
    path.write_text("name,top_x,top_y\na,14,610\n")
    panel.apply()
    assert world.points("a") == {"top": (14, 610)}
    assert world.points("a", "Bold") == {}
    assert world.notifications()[0][2] == ["a/Light", "a"]


def test_csv_unknown_glyph_disables_import(world: Any, tmp_path: Path) -> None:
    world.glyph("a")
    path = tmp_path / "anchors.csv"
    path.write_text("name,top_x,top_y\nmissing,12,600\n")
    panel = load(TITLES[0])["main"]()
    panel.csv_path.text = str(path)
    panel.reload()
    assert not panel.apply_button.enabled
    assert "Missing glyphs" in panel.status.text
    assert not world.notifications()


def test_myanmar_copies_by_named_master_in_one_step(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.glyph(
        "round", anchors={"Light": [("top", 12, 600)], "Bold": [("top", 20, 700)]}
    )
    world.glyph(
        "angular", anchors={"Light": [("top", 30, 500)], "Bold": [("top", 40, 550)]}
    )
    world.glyph("recipient")
    catalogue(
        monkeypatch,
        [
            ("round", "U+101D", ""),
            ("angular", "U+1000", ""),
            ("recipient", "U+1001", ""),
        ],
    )
    panel = load(TITLES[1])["main"]()
    panel.apply()
    assert world.points("recipient") == {"top": (12, 600)}
    assert world.points("recipient", "Bold") == {"top": (20, 700)}
    assert world.notifications()[0][2] == [
        "recipient/Light",
        "recipient/Bold",
        "recipient",
    ]


def matrix(values: tuple = (1, 0, 0, 1, 0, 0)) -> Any:
    return NS(
        isAffine=lambda: True,
        **{
            name: lambda v=value: v
            for name, value in zip(("m11", "m12", "m21", "m22", "dx", "dy"), values)
        },
    )


def composite_fixture(world: Any) -> None:
    world.glyph("base")
    world.glyph(
        "mark", anchors={"Light": [("_top", 10, 20)], "Bold": [("_top", 15, 25)]}
    )
    world.glyph("composite")
    for master in world.masters:
        world.layer("composite", master).shapes = [
            NS(
                isComponent=True,
                shapeData=NS(componentGlyph="base", componentLayer=""),
                transform=matrix(),
            ),
            NS(
                isComponent=True,
                shapeData=NS(componentGlyph="mark", componentLayer=""),
                transform=matrix((1, 0, 0, 1, 100, 200)),
            ),
        ]


def test_component_evidence_writes_only_base_layers(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    composite_fixture(world)
    catalogue(monkeypatch, [(name, "", "") for name in world.glyphs])
    panel = load(TITLES[2])["main"]()
    panel.apply()
    assert world.points("base") == {"top": (110, 220)}
    assert world.points("base", "Bold") == {"top": (115, 225)}
    assert world.notifications()[0][2] == ["base/Light", "base/Bold", "base"]
    assert world.points("composite") == {}


def test_component_conflicts_refuse_before_history(world: Any) -> None:
    composite_fixture(world)
    world.glyph("other")
    shapes = list(world.layer("composite").shapes)
    world.layer("other").shapes = [
        shapes[0],
        NS(
            isComponent=True,
            shapeData=NS(componentGlyph="mark", componentLayer=""),
            transform=matrix((1, 0, 0, 1, 200, 300)),
        ),
    ]
    notes = {}
    result = load(TITLES[2])["derived_points"](
        world.package, list(world.glyphs), world.masters, notes
    )
    assert result["base", "Light"] == {}
    assert result["base", "Bold"] == {"top": (115, 225)}
    assert any(
        "conflicting evidence" in row.new and row.edit is None and not row.problem
        for row in notes["base", "Light"]
    )

    assert not world.notifications()


def test_optical_alignment_keeps_y_and_reports_without_top(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load(TITLES[3])
    monkeypatch.setitem(
        tool["optical_changes"].__globals__, "layer_estimate", lambda layer: 120
    )
    world.glyph("a", anchors={"Light": [("top", 100, 600)]})
    panel = tool["main"]()
    panel.apply()
    assert world.points("a") == {"top": (120, 600)}
    assert world.notifications()[0][2] == ["a/Light", "a"]
    world.glyph("b")
    row = tool["optical_changes"](world.layer("b"))[0]
    assert row.new == "120" and row.edit is None


def test_cursive_profile_file_roundtrip_and_no_overwrite(
    world: Any, tmp_path: Path
) -> None:
    sample, fit = load(TITLES[-1]), load(TITLES[-2])
    path = tmp_path / "profile.json"
    profile = {"below": 10, "above": 30, "lower_angle": 0, "upper_angle": 0}
    document = {
        "format": "fontlab-cursive-sample-1",
        "master": "Light",
        "profile": profile,
    }
    sample["save_document"](str(path), document)
    assert fit["read_sample"](str(path), "Light") == profile
    with pytest.raises(ValueError, match="Choose a new file name"):
        sample["save_document"](str(path), document)
    with pytest.raises(ValueError, match="master"):
        fit["read_sample"](str(path), "Bold")


def test_cursive_plans_missing_connections_and_one_notification(
    world: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tool = load(TITLES[-2])
    rings = [[(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)]]
    monkeypatch.setitem(
        tool["cursive_changes"].__globals__, "outline_rings", lambda layer: rings
    )
    world.glyph("beh.medi", anchors={"Light": [("entry", 90, 10)]})
    path = tmp_path / "profile.json"
    load(TITLES[-1])["save_document"](
        str(path),
        {
            "format": "fontlab-cursive-sample-1",
            "master": "Light",
            "profile": {"below": 10, "above": 30, "lower_angle": 0, "upper_angle": 0},
        },
    )
    panel = tool["main"]()
    panel.sample_path.setText(str(path))
    panel.apply()
    assert world.points("beh.medi") == {"entry": (90, 10), "exit": (1, 10)}
    assert world.notifications()[0][2] == ["beh.medi/Light", "beh.medi"]
    assert world.points("beh.medi", "Bold") == {}


def test_sample_captures_existing_pins_and_rejects_missing(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load(TITLES[-1])
    rings = [[(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)]]
    monkeypatch.setitem(
        tool["sample_document"].__globals__, "outline_rings", lambda layer: rings
    )
    world.glyph("sample", anchors={"Light": [("entry", 50, 10)]})
    assert (
        tool["sample_document"](world.layer("sample"), "Light")["profile"]["below"]
        == 10
    )
    with pytest.raises(ValueError, match="entry or exit"):
        tool["sample_document"](world.layer("sample", "Bold"), "Bold")


@pytest.mark.parametrize("title", TITLES[-2:])
def test_cursive_winding_holes_and_overlaps(world: Any, title: str) -> None:
    tool = load(title)
    outer = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]
    counter = [(20, 20), (20, 80), (80, 80), (80, 20), (20, 20)]
    assert [
        (low, high) for low, high, _, _ in tool["vertical_spans"]([outer, counter], 50)
    ] == [(0, 20), (80, 100)]
    assert [
        (low, high) for low, high, _, _ in tool["vertical_spans"]([outer, outer], 50)
    ] == [(0, 100)]


@pytest.mark.parametrize("title", TITLES[:-1])
def test_preview_close_disconnects_and_deletes_owned_panel(
    world: Any, title: str
) -> None:
    panel = load(title)["main"]()
    assert panel._connections
    panel.close()
    assert panel.deleted and not panel._connections


def test_sample_main_saves_selected_layer_without_font_write(
    world: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
    import fly.ap.qt_dialogs as qt_dialogs  # noqa: PLR0402

    tool = load(TITLES[-1])
    world.glyph("sample", anchors={"Light": [("entry", 50, 10)]})
    layer = world.layer("sample")
    layer.name, layer.isMaskLayer, layer.isService = "Light", False, False
    rings = [[(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)]]
    monkeypatch.setitem(
        tool["sample_document"].__globals__, "outline_rings", lambda layer: rings
    )
    monkeypatch.setattr(
        layer_selection, "capture", lambda deadline: NS(occurrences=[NS(layer=layer)])
    )
    path = tmp_path / "profile.json"
    monkeypatch.setattr(qt_dialogs, "run_file_dialog", lambda *args: [str(path)])
    result = tool["main"]()
    assert result["master"] == "Light" and path.is_file()
    assert not world.events


def test_optical_scanline_weights_from_real_rings(world: Any) -> None:
    tool = load(TITLES[3])
    outer = [(100, 0), (140, 0), (140, 40), (100, 40), (100, 0)]
    counter = [(110, 10), (110, 30), (130, 30), (130, 10), (110, 10)]
    assert tool["column_weight"]([outer, counter], 120) == 20
    assert tool["column_weight"]([outer, counter], 105) == 40
    assert tool["column_weight"]([outer, outer], 120) == 40
    assert tool["estimate_rings"]([outer], math.inf) == 120


def test_csv_new_anchor_appearance_and_origin_refusal(
    world: Any, tmp_path: Path
) -> None:
    world.glyph("a", anchors={"Light": [("bottom", 10, 20)]})
    path = tmp_path / "anchors.csv"
    path.write_text("name,top_x,top_y\na,12,600\n")
    panel = load(TITLES[0])["main"]()
    panel.csv_path.text = str(path)
    panel.reload()
    panel.apply()
    top = next(pin for pin in world.layer("a").anchors if pin.name == "top")
    assert top.appearance == 5
    path.write_text("name,bottom_x,bottom_y\na,0,0\n")
    panel.reload()
    assert not panel.apply_button.enabled
    with pytest.raises(ValueError, match="0, 0"):
        panel.apply()
    assert len(world.notifications()) == 1


@pytest.mark.parametrize(
    "title",
    [
        "Derive Anchors From Components",
        "Optical Center",
        "Auto Cursive Attachment Add Anchors",
    ],
)
def test_scan_timeout_disables_action_inside_panel(
    world: Any, monkeypatch: pytest.MonkeyPatch, title: str
) -> None:
    tool = load(title)
    panel = tool["main"]()

    def fail() -> Any:
        raise TimeoutError("injected scan deadline")

    monkeypatch.setattr(panel, "planner", fail)
    world.glyph("a")
    panel.glyphs = [world.glyphs["a"]]
    panel.refresh()
    assert not panel.apply_button.enabled
    assert "deadline" in panel.status.text


def test_component_keeps_existing_anchor(world: Any) -> None:
    composite_fixture(world)
    world.layer("base").anchors = [Pin(world, "top", 1, 2)]
    result = load(TITLES[2])["derived_points"](
        world.package, list(world.glyphs), world.masters
    )
    assert result["base", "Light"] == {}
    assert result["base", "Bold"] == {"top": (115, 225)}


def test_cursive_empty_candidate_search_refuses(world: Any) -> None:
    profile = {"below": 10, "above": 30, "lower_angle": 0, "upper_angle": 0}
    with pytest.raises(ValueError, match="No suitable"):
        load(TITLES[-2])["choose_attachment"]([], profile, [1, 2])


def test_myanmar_ambiguous_encoding_refuses(world: Any) -> None:
    with pytest.raises(ValueError, match="Several glyphs"):
        load(TITLES[1])["route_names"]([("a", "U+101D", ""), ("b", "U+101D", "")])


def test_csv_duplicate_target_names_refuse_before_history(
    world: Any, tmp_path: Path
) -> None:
    world.glyph("a", anchors={"Light": [("top", 1, 2), ("top", 3, 4)]})
    path = tmp_path / "anchors.csv"
    path.write_text("name,top_x,top_y\na,12,600\n")
    panel = load(TITLES[0])["main"]()
    panel.csv_path.text = str(path)
    panel.reload()
    assert not panel.apply_button.enabled
    with pytest.raises(ValueError, match="several anchors"):
        panel.apply()
    assert not world.notifications()


@pytest.mark.parametrize(
    "title,method,field",
    [
        (TITLES[0], "choose_csv", "csv_path"),
        (TITLES[-2], "choose_profile", "sample_path"),
    ],
)
def test_owned_file_picker_sets_path(
    world: Any, monkeypatch: pytest.MonkeyPatch, title: str, method: str, field: str
) -> None:
    import fly.ap.qt_dialogs as qt_dialogs  # noqa: PLR0402

    panel = load(title)["main"]()
    monkeypatch.setattr(qt_dialogs, "run_file_dialog", lambda *args: ["/chosen/file"])
    getattr(panel, method)()
    assert getattr(panel, field).text == "/chosen/file"


# Regression: a stack contributes its first mark for each attachment label.
def test_stacked_marks_derive_first_attachment(world: Any) -> None:
    composite_fixture(world)
    world.glyph("upper", anchors={"Light": [("_top", 0, 0)], "Bold": [("_top", 0, 0)]})
    for master in world.masters:
        world.layer("composite", master).shapes.append(
            NS(
                isComponent=True,
                shapeData=NS(componentGlyph="upper", componentLayer=""),
                transform=matrix((1, 0, 0, 1, 100, 400)),
            )
        )
    result = load(TITLES[2])["derived_points"](
        world.package, list(world.glyphs), world.masters
    )
    assert result["base", "Light"] == {"top": (110, 220)}, (
        "Stack must keep the first mark next to the base"
    )


def test_fractional_csv_rounds_before_strong_rounding_write(
    world: Any, tmp_path: Path
) -> None:
    world.glyph("a", anchors={"Light": [("top", 10, 500)]})
    world.strong_rounding = True
    path = tmp_path / "fractional.csv"
    path.write_text("name,top_x,top_y\na,-2.5,600.5\n")
    panel = load(TITLES[0])["main"]()
    panel.csv_path.text = str(path)
    panel.reload()
    panel.apply()
    assert world.points("a") == {"top": (-2, 601)}, (
        "CSV must plan half-up integer coordinates"
    )


@pytest.mark.parametrize("fault", ["missing", "auto", "ambiguous", "nonmaster"])
def test_doubtful_component_evidence_is_a_note_not_a_font_refusal(
    world: Any, fault: str
) -> None:
    composite_fixture(world)
    world.glyph("broken")
    base, mark = world.layer("composite").shapes
    if fault == "missing":
        mark = NS(
            isComponent=True,
            shapeData=NS(componentGlyph="absent", componentLayer=""),
            transform=matrix(),
        )
    elif fault == "auto":
        world.glyph("automatic", anchors={"Light": [("_top", 0, 0)]}, auto=("Light",))
        mark = NS(
            isComponent=True,
            shapeData=NS(componentGlyph="automatic", componentLayer=""),
            transform=matrix(),
        )
    elif fault == "ambiguous":
        world.glyph(
            "ambiguous", anchors={"Light": [("_top", 0, 0), ("_bottom", 0, 10)]}
        )
        mark = NS(
            isComponent=True,
            shapeData=NS(componentGlyph="ambiguous", componentLayer=""),
            transform=matrix(),
        )
    else:
        world.glyphs["base"].by_master["Light@copy"] = world.layer("base")
        base = NS(
            isComponent=True,
            shapeData=NS(componentGlyph="base", componentLayer="Light@copy"),
            transform=matrix(),
        )
    world.layer("broken").shapes = [base, mark]
    notes = {}
    result = load(TITLES[2])["derived_points"](
        world.package, list(world.glyphs), world.masters, notes
    )
    assert result["base", "Light"] == {"top": (110, 220)}, (
        "Clean evidence must survive a doubtful composite"
    )
    assert notes["broken", "Light"]
    assert all(row.edit is None and not row.problem for row in notes["broken", "Light"])


def test_one_conflicting_base_does_not_remove_another_clean_base(world: Any) -> None:
    composite_fixture(world)
    world.glyph("secondbase")
    world.glyph("clean")
    base, mark = world.layer("composite").shapes
    world.layer("clean").shapes = [
        NS(
            isComponent=True,
            shapeData=NS(componentGlyph="secondbase", componentLayer=""),
            transform=matrix(),
        ),
        mark,
    ]
    world.glyph("conflict")
    world.layer("conflict").shapes = [
        base,
        NS(
            isComponent=True,
            shapeData=NS(componentGlyph="mark", componentLayer=""),
            transform=matrix((1, 0, 0, 1, 200, 300)),
        ),
    ]
    notes = {}
    result = load(TITLES[2])["derived_points"](
        world.package, list(world.glyphs), world.masters, notes
    )
    assert result["base", "Light"] == {}
    assert result["secondbase", "Light"] == {"top": (110, 220)}
    assert "conflicting evidence" in notes["base", "Light"][0].new


@pytest.mark.parametrize("title", [TITLES[1], TITLES[2]])
def test_catalogue_is_captured_once_per_scan(
    world: Any, monkeypatch: pytest.MonkeyPatch, title: str
) -> None:
    import fly.ap.glyph_catalog as glyph_catalog  # noqa: PLR0402

    rows = [
        ("round", "U+101D", ""),
        ("angular", "U+1000", ""),
        ("recipient", "U+1001", ""),
    ]
    for name, _, _ in rows:
        world.glyph(name)
    calls = []

    def capture() -> Any:
        calls.append(1)
        return NS(rows=rows)

    monkeypatch.setattr(glyph_catalog, "capture", capture)
    panel = load(title)["main"]()
    assert len(calls) == 1, "One catalogue capture on opening scan"
    panel.refresh()
    assert len(calls) == 1, "Refresh must reuse the routing/name capture"
    panel.reload()
    assert len(calls) == 2, "An explicit scan captures once again"


def test_derive_budgets_are_per_layer(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load(TITLES[2])
    composite_fixture(world)
    for i in range(20):
        world.glyph(f"copy{i}")
        world.layer(f"copy{i}").shapes = list(world.layer("composite").shapes)
    clock = iter(i * 0.1 for i in range(1000))
    monkeypatch.setitem(
        tool["derived_points"].__globals__, "monotonic", lambda: next(clock)
    )
    notes = {}
    result = tool["derived_points"](
        world.package, list(world.glyphs), world.masters, notes
    )
    assert result["base", "Light"] == {"top": (110, 220)}
    assert not notes, "Cumulative font work must not exhaust a single shared deadline"


def test_optical_layer_timeout_becomes_note_and_other_layer_writes(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = load(TITLES[3])
    world.glyph("slow", anchors={"Light": [("top", 10, 500)]})
    world.glyph("clean", anchors={"Light": [("top", 20, 500)]})

    def estimate(layer: Any) -> int:
        if layer.glyph == "slow":
            raise TimeoutError("layer time budget exceeded")
        return 30

    monkeypatch.setitem(tool["optical_changes"].__globals__, "layer_estimate", estimate)
    row = tool["optical_changes"](world.layer("slow"))[0]
    assert row.edit is None and not row.problem and "skipped" in row.new
    panel = tool["main"]()
    assert panel.apply_button.enabled
    panel.apply()
    assert world.points("slow")["top"] == (10, 500)
    assert world.points("clean")["top"] == (30, 500)
    assert world.notifications()[0][2] == ["clean/Light", "clean"]


def test_optical_flattens_placed_components_once(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    import fly.ap.proof as proof  # noqa: PLR0402

    tool = load(TITLES[3])
    ring = [(100, 0), (140, 0), (140, 40), (100, 40), (100, 0)]
    points = [NS(x=lambda x=x: x, y=lambda y=y: y) for x, y in ring]
    calls = []

    def placed(layer: Any) -> Any:
        calls.append(layer)
        return NS(toSubpathPolygons=lambda: [points])

    monkeypatch.setattr(proof, "layer_path", placed)
    layer = NS(shapes=[NS(isComponent=True)])
    assert tool["layer_estimate"](layer) == 120
    assert calls == [layer]


@pytest.mark.parametrize("converted", [False, True])
def test_csv_conversion_report_matches_bytes(
    world: Any, tmp_path: Path, converted: bool
) -> None:
    path = tmp_path / "table.csv"
    text = "name, top_x , top_y \na,1.5,600.5\n"
    path.write_bytes(
        (b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode())
        if converted
        else text.encode()
    )
    records, report = load(TITLES[0])["load_table"](str(path))
    assert records == {"a": {"top": (2, 601)}}
    assert ("BOM removed" in report) == converted
    assert ("CR/CRLF" in report) == converted
    assert "round half up" in report


def test_unknown_csv_column_has_clear_message(world: Any) -> None:
    with pytest.raises(ValueError, match="Unknown CSV columns: top_X"):
        load(TITLES[0])["parse_table"]("name,top_x,top_y,top_X\na,1,2,3\n")


@pytest.mark.parametrize("converted", [False, True])
def test_sample_conversion_report_matches_bytes(
    world: Any, tmp_path: Path, converted: bool
) -> None:
    import json

    data = {
        "format": "fontlab-cursive-sample-1",
        "master": "Light",
        "profile": {"below": 10, "above": 30, "lower_angle": 0, "upper_angle": 0},
    }
    text = json.dumps(data, indent=2) + "\n"
    path = tmp_path / "sample.json"
    path.write_bytes(
        (b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode())
        if converted
        else text.encode()
    )
    notes = []
    load(TITLES[-2])["read_sample"](str(path), "Light", notes)
    assert ("BOM removed" in notes) == converted
    assert ("CR/CRLF read as LF" in notes) == converted


def test_empty_cursive_path_requests_sample(world: Any) -> None:
    with pytest.raises(ValueError, match=r"^Choose a sample file\.$"):
        load(TITLES[-2])["read_sample"]("", "Light")
    world.glyph("beh.medi")
    panel = load(TITLES[-2])["main"]()
    assert panel.status.text == "Choose a sample file."


@pytest.mark.parametrize("title", TITLES[-2:])
def test_cursive_sloped_tangents(world: Any, title: str) -> None:
    rings = [[(0, 0), (100, 100), (100, 140), (0, 40), (0, 0)]]
    tool = load(title)
    low, high, bottom, top = tool["vertical_spans"](rings, 50)[0]
    assert (low, high) == (50, 90)
    assert bottom == pytest.approx(math.pi / 4)
    assert top == pytest.approx(math.pi / 4)
    sample = tool["measure_sample"](rings, [(50, 60)])
    assert sample["below"] == 10 and sample["above"] == 30
    assert sample["lower_angle"] == pytest.approx(math.pi / 4)


def test_conflict_note_does_not_disable_clean_base_writer(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    composite_fixture(world)
    world.glyph("secondbase")
    world.glyph("clean")
    base, mark = world.layer("composite").shapes
    world.layer("clean").shapes = [
        NS(
            isComponent=True,
            shapeData=NS(componentGlyph="secondbase", componentLayer=""),
            transform=matrix(),
        ),
        mark,
    ]
    world.glyph("conflict")
    world.layer("conflict").shapes = [
        base,
        NS(
            isComponent=True,
            shapeData=NS(componentGlyph="mark", componentLayer=""),
            transform=matrix((1, 0, 0, 1, 200, 300)),
        ),
    ]
    catalogue(monkeypatch, [(name, "", "") for name in world.glyphs])
    panel = load(TITLES[2])["main"]()
    assert panel.apply_button.enabled, (
        "A nonblocking note must not disable clean base edits"
    )
    panel.apply()
    assert world.points("base") == {}
    assert world.points("secondbase") == {"top": (110, 220)}
    assert len(world.notifications()) == 1


def test_sample_chooser_avoids_false_overwrite_confirmation(
    world: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import fly.ap.layer_selection as layer_selection  # noqa: PLR0402
    import fly.ap.qt_dialogs as qt_dialogs  # noqa: PLR0402

    tool = load(TITLES[-1])
    world.glyph("sample", anchors={"Light": [("entry", 50, 10)]})
    layer = world.layer("sample")
    layer.name, layer.isMaskLayer, layer.isService = "Light", False, False
    rings = [[(0, 0), (100, 0), (100, 40), (0, 40), (0, 0)]]
    monkeypatch.setitem(
        tool["sample_document"].__globals__, "outline_rings", lambda layer: rings
    )
    monkeypatch.setattr(
        layer_selection, "capture", lambda deadline: NS(occurrences=[NS(layer=layer)])
    )
    settings = {}

    def choose(gui: Any, configure: Any, title: str, directory: str) -> list[str]:
        assert directory == str(Path.home()), (
            "Save chooser must start in the home folder"
        )
        kind = NS(AcceptSave=1, AnyFile=2, DontConfirmOverwrite=3)
        dialog = NS(
            setAcceptMode=lambda value: settings.update(mode=value),
            setOption=lambda key, value: settings.update(option=(key, value)),
            setFileMode=lambda value: None,
            setNameFilter=lambda value: None,
            setDefaultSuffix=lambda value: None,
        )
        configure(kind, dialog)
        return [str(tmp_path / "new.json")]

    monkeypatch.setattr(qt_dialogs, "run_file_dialog", choose)
    assert tool["main"]()["master"] == "Light"
    assert settings == {"mode": 1, "option": (3, True)}


def test_myanmar_bad_source_layer_is_a_note_and_other_master_runs(
    world: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    world.glyph("round", anchors={"Bold": [("top", 20, 600)]}, auto=("Light",))
    world.glyph("angular")
    world.glyph("recipient")
    catalogue(
        monkeypatch,
        [
            ("round", "U+101D", ""),
            ("angular", "U+1000", ""),
            ("recipient", "U+1001", ""),
        ],
    )
    panel = load(TITLES[1])["main"]()
    assert panel.apply_button.enabled
    panel.apply()
    assert world.points("recipient") == {}
    assert world.points("recipient", "Bold") == {"top": (20, 600)}
    assert world.notifications()[0][2] == ["recipient/Bold", "recipient"]
