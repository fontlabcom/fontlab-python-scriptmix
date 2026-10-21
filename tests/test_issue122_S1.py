# this_file: tests/test_issue122_S1.py
# SPDX-License-Identifier: Apache-2.0
"""Six Metrics scripts, tested against owned fakes and the real App helpers.

The fakes replace FontLab layers, the `fontlab` module and Qt widgets. The real
installed App modules (`fly.ap.metrics_panel`, `fly.ap.history`) run over them,
reached as `fly.ap.<module>` like inside FontLab. The tests prove the planning
arithmetic, the refusal paths and the Undo shape (one notified list, no auto
layers). They do not prove native FontLab behaviour.
"""

import ast
import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "Scripts/Metrics"
NAMES = [
    "Italic Sidebearings",
    "Round Advances",
    "Centre In Advance",
    "Zero-Width Marks",
    "Tabular Width",
    "Scale Advances",
]
CLASS = {
    "Italic Sidebearings": "ItalicSidebearings",
    "Round Advances": "RoundAdvances",
    "Centre In Advance": "CentreInAdvance",
    "Zero-Width Marks": "ZeroWidthMarks",
    "Tabular Width": "TabularWidth",
    "Scale Advances": "ScaleAdvances",
}


# ---------------------------------------------------------------- Qt fakes
class Signal:
    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)

    def disconnect(self, slot):
        self.slots.remove(slot)

    def emit(self, *args):
        for slot in list(self.slots):
            slot(*args)


class Consts:
    """Any attribute is a distinct small integer, like a Qt enum."""

    def __getattr__(self, name):
        return sum(map(ord, name)) % 997


class FakeColor:
    HexArgb = 2

    def __init__(self, source=None):
        self.source = source

    def name(self, *args):
        return "#000000"

    def setAlpha(self, alpha):
        pass


class FakePalette:
    def color(self, *args):
        return FakeColor()

    def setColor(self, *args):
        pass


class FakeFont:
    def pointSizeF(self):
        return 10.0

    def __getattr__(self, name):
        return lambda *a, **k: None


class Widget:
    SIGNALS = frozenset(
        {
            "valueChanged",
            "currentIndexChanged",
            "toggled",
            "clicked",
            "finished",
            "destroyed",
        }
    )

    def __init__(self, *args, **kwargs):
        self._signals = {}
        self._enabled = True
        self.args = args

    @property
    def palette(self):
        return FakePalette()

    @property
    def font(self):
        return FakeFont()

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        if name in Widget.SIGNALS:
            return self._signals.setdefault(name, Signal())
        return lambda *a, **k: None

    def setVisible(self, flag):
        self._visible = bool(flag)

    def setEnabled(self, flag):
        self._enabled = bool(flag)

    def isEnabled(self):
        return self._enabled


class Dialog(Widget):
    def close(self):
        event = ModuleType("event")
        self.closeEvent(event)
        return True

    def closeEvent(self, event):
        pass


class Label(Widget):
    def __init__(self, text="", *a):
        super().__init__()
        self._text = text

    @property
    def text(self):
        return self._text

    def setText(self, text):
        self._text = text


class Spin(Widget):
    def __init__(self, *a):
        super().__init__()
        self._value = 0
        self.range = (0, 0)

    @property
    def value(self):
        return self._value

    def setRange(self, low, high):
        self.range = (low, high)

    def setValue(self, value):
        if value != self._value:
            self._value = value
            self.valueChanged.emit(value)


class Combo(Widget):
    def __init__(self, *a):
        super().__init__()
        self.items = []
        self._index = 0

    @property
    def currentIndex(self):
        return self._index

    def addItem(self, text):
        self.items.append(text)

    def pick(self, index):
        self._index = index
        self.currentIndexChanged.emit(index)


class Check(Widget):
    def __init__(self, *a):
        super().__init__()
        self._checked = False

    def setChecked(self, flag):
        self._checked = bool(flag)

    def isChecked(self):
        return self._checked

    def tick(self, flag):
        self._checked = flag
        self.toggled.emit(flag)


class Button(Widget):
    def __init__(self, text="", *a):
        super().__init__()
        self.label = text

    def press(self):
        self.clicked.emit(False)


class Item:
    def __init__(self, text=""):
        self.text = text
        self.bold = False

    def font(self):
        return FakeFont()

    def setFont(self, font):
        self.bold = True

    def __getattr__(self, name):
        return lambda *a, **k: None


class Table(Widget):
    def __init__(self, rows=0, columns=0):
        super().__init__()
        self.rows = rows
        self.cells = {}

    def horizontalHeader(self):
        return Widget()

    def verticalHeader(self):
        return Widget()

    def setRowCount(self, count):
        self.rows = count
        self.cells = {}

    def setItem(self, row, column, item):
        self.cells[row, column] = item

    def texts(self, row):
        columns = sorted(c for r, c in self.cells if r == row)
        return [self.cells[row, c].text for c in columns]


class Grid(Widget):
    pass


def fake_qt():
    qt = ModuleType("fly.qt")
    gui, core = ModuleType("QtGui"), ModuleType("QtCore")
    gui.QDialog = Dialog
    gui.QLabel = Label
    gui.QSpinBox = Spin
    gui.QDoubleSpinBox = Spin
    gui.QComboBox = Combo
    gui.QCheckBox = Check
    gui.QPushButton = Button
    gui.QTableWidget = Table
    gui.QTableWidgetItem = Item
    gui.QVBoxLayout = gui.QHBoxLayout = gui.QGridLayout = Grid
    gui.QBrush = lambda color: color
    gui.QColor = FakeColor
    for name in ("QPalette", "QAbstractItemView", "QHeaderView"):
        setattr(gui, name, Consts())
    gui.QPainterPath = FakePath
    gui.QTransform = FakeTransform
    core.Qt = Consts()
    core.QDateTime = DateTime
    qt.QtGui, qt.QtCore = gui, core
    return qt


# ---------------------------------------------------------------- geometry fakes
class Box:
    def __init__(self, left, bottom, right, top):
        self._v = (left, bottom, right - left, top - bottom)

    def x(self):
        return self._v[0]

    def y(self):
        return self._v[1]

    def width(self):
        return self._v[2]

    def height(self):
        return self._v[3]


def bounds(points):
    if not points:
        return Box(0, 0, 0, 0)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return Box(min(xs), min(ys), max(xs), max(ys))


class FakePath:
    def __init__(self, points=()):
        self.points = list(points)

    def addPath(self, other):
        self.points.extend(other.points)

    def isEmpty(self):
        return not self.points

    def boundingRect(self):
        return bounds(self.points)


class FakeTransform:
    def __init__(self, m11=1, m12=0, m21=0, m22=1, dx=0, dy=0):
        self.m = (m11, m12, m21, m22, dx, dy)

    def point(self, p):
        m11, m12, m21, m22, dx, dy = self.m
        return (m11 * p[0] + m21 * p[1] + dx, m12 * p[0] + m22 * p[1] + dy)

    def map(self, path):
        return FakePath(self.point(p) for p in path.points)


# ---------------------------------------------------------------- FontLab fakes
LOG: list = []  # Ordered ("init" | "edit" | "notify", detail) events of one test.
STAMP = "UTC-stamp"


class DateTime:
    @staticmethod
    def currentDateTimeUtc():
        return STAMP


class Contour:
    def __init__(self, layer):
        self.layer = layer

    def path(self):
        return FakePath(self.layer.points)


class Shape:
    isComponent = False

    def __init__(self, layer):
        self.layer = layer
        self.transform = FakeTransform()

    def getContours(self):
        return [Contour(self.layer)]

    def clone(self):
        self.layer.clones += 1
        return Shape(self.layer)


class Layer:
    isNull = False
    isMasterLayer = True

    def __init__(self, width, points=(), auto=False):
        self._width = width
        self.points = list(points)
        self.autoLayer = auto
        self.clones = 0
        self.swaps = 0
        self.transforms = []
        self.init_calls = []
        self.edit_log = []
        self.shapes = [Shape(self)]
        self.metricsLeft = self.metricsRight = self.metricsWidth = ""
        self.stubborn_width = False
        self.cache_ok = True

    @property
    def advanceWidth(self):
        return self._width

    @advanceWidth.setter
    def advanceWidth(self, value):
        self.log("width")
        if not self.stubborn_width:
            self._width = value

    def log(self, kind):
        LOG.append(("edit", kind))
        self.edit_log.append(kind)

    def checkInitHistoryState(self, level):
        LOG.append(("init", "layer"))
        self.init_calls.append(level)

    @property
    def boundingBox(self):
        return bounds(self.points)

    def removeShape(self, shape):
        self.swaps += 1
        self.shapes.remove(shape)

    def insertShape(self, index, shape):
        self.swaps += 1
        self.shapes.insert(index, shape)

    def applyTransform(self, transform):
        self.log("move")
        self.transforms.append(transform.m)
        self.points = [transform.point(p) for p in self.points]

    def changed(self):
        self.log("changed")

    def update(self):
        self.log("update")
        return self.cache_ok


class Glyph:
    isNull = False

    def __init__(self, name, layers, codes=None):
        self.name, self.layers_by_master = name, layers
        self.unicodes = list(codes or [])
        self.init_calls = []
        self._stamp = None

    @property
    def lastModified(self):
        return self._stamp

    @lastModified.setter
    def lastModified(self, value):
        LOG.append(("stamp", self.name))
        self._stamp = value

    def checkInitHistoryState(self, level):
        LOG.append(("init", "glyph"))
        self.init_calls.append(level)

    @property
    def layers(self):
        return list(self.layers_by_master.values())

    def findLayer(self, master):
        return self.layers_by_master.get(master)


class Package:
    def __init__(self, glyphs, masters=("Light", "Bold"), ident=7):
        self.id, self.master, self.masters = ident, masters[0], list(masters)
        self.glyphs = {g.name: g for g in glyphs}
        self.italicAngle_value = -10.0
        self.xHeight_value = 500

    def findName(self, name):
        return self.glyphs.get(name)


def rect(left, right, top=100):
    return [(left, 0), (right, 0), (right, top), (left, top)]


class World:
    """One shared fake state: font, selection, history, closed windows."""

    def __init__(self):
        self.package = None
        self.selection = []
        self.history = []
        self.closed = []
        self.shown = []
        self.font_names = []
        self.updates = []  # Queued native glyph updates (flGlyph.updatedFgGlyphs).


@pytest.fixture
def world(monkeypatch, real_app):
    state = World()
    LOG.clear()
    fly = ModuleType("fly")
    ap = ModuleType("fly.ap")
    scripting = ModuleType("fly.ap.scripting")
    completion = ModuleType("fly.ap.script_completion")

    fontlab = ModuleType("fontlab")
    items = ModuleType("items")

    def notify(title, objs):
        LOG.append(("notify", title))
        state.history.append((title, objs))

    items.notifyChangesApplied = notify
    fontlab.flItems = lambda: items
    fontlab.flGlyph = ModuleType("flGlyph")
    fontlab.flGlyph.updatedFgGlyphs = lambda: list(state.updates)
    font_api = ModuleType("FL")
    font_api.fl = ModuleType("fl")
    ap.fontlab, ap.FL = fontlab, font_api

    class FontSeq:
        def __len__(self):
            return len(state.font_names)

        def __getitem__(self, index):
            item = ModuleType("g")
            item.name = state.font_names[index]
            return item

    font_api.fl.font = FontSeq()

    scripting.current_package = lambda expected_id=None: state.package
    scripting.names_selected_names = lambda: list(state.selection)
    scripting.names_font_glyphs = lambda: [(n, []) for n in state.font_names]

    def connect_guarded(dialog, signal, callback):
        def guarded(*args):
            try:
                callback(*args)
            except Exception as error:  # noqa: BLE001
                dialog.status.setText("Error: " + repr(error))

        signal.connect(guarded)
        dialog._connections.append((signal, guarded))

    scripting.connect_guarded = connect_guarded

    def close_script_dialog(dialog, event, key, **kwargs):
        state.closed.append(key)

    scripting.close_script_dialog = close_script_dialog

    def show_script_dialog(dialog_type, key):
        dialog = dialog_type(None)
        state.shown.append((key, dialog))
        return dialog

    scripting.show_script_dialog = show_script_dialog
    completion.install = lambda dialog, key: ("completion", key)
    qt = fake_qt()
    fly.ap, fly.qt = ap, qt
    for name, module in {
        "fly": fly,
        "fly.ap": ap,
        "fly.qt": qt,
        "fly.ap.scripting": scripting,
        "fly.ap.script_completion": completion,
    }.items():
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
                "close_script_dialog",
                "show_script_dialog",
            )
        },
        completion=completion.install,
        modules=["history", "metrics_panel"],
    )
    return state


def load(name: str, prefix: str = "s1"):
    path = METRICS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{prefix}_{CLASS[name]}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous, sys.dont_write_bytecode = (
        sys.dont_write_bytecode,
        True,
    )  # no .pyc in Scripts
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
        sys.modules.pop(spec.name, None)
    return module


def open_panel(world, name, glyphs, selection=None, masters=("Light", "Bold")):
    module = load(name)
    world.package = Package(glyphs, masters)
    world.selection = [g.name for g in glyphs] if selection is None else selection
    panel = getattr(module, CLASS[name])(None)
    return module, panel


def two_master_glyph(name="n", light=(100, 10, 90), bold=(120, 12, 108)):
    layers = {
        "Light": Layer(light[0], rect(light[1], light[2])),
        "Bold": Layer(bold[0], rect(bold[1], bold[2])),
    }
    return Glyph(name, layers)


# ---------------------------------------------------------------- files
@pytest.mark.parametrize("name", NAMES)
def test_script_file_when_listed_then_has_house_header_and_py311_syntax(name):
    path = METRICS / f"{name}.py"
    text = path.read_text()
    assert path.is_file(), f"missing {path}"
    assert text.startswith(f"# this_file: Scripts/Metrics/{name}.py\n"), (
        "this_file header"
    )
    assert "# SPDX-License-Identifier: Apache-2.0" in text.splitlines()[1]
    tree = ast.parse(text, feature_version=(3, 11))
    doc = ast.get_docstring(tree) or ""
    for word in (
        "What it does",
        "How it works",
        "Why",
        "How to use",
        "Benefit",
        "Credit",
    ):
        assert word in doc, f"{name}: docstring lacks '{word}'"
    assert "Apache-2.0" in doc, "licence in docstring"
    for jargon in ("issue 122", "D22", "batch", "reviewed App", "S1", "owner decision"):
        assert jargon not in text, f"{name}: internal jargon '{jargon}'"
    for claim in ("measured natively", "Undo restores", "stem hints", "Stem hints"):
        assert claim not in text, f"{name}: unproven claim '{claim}'"
    assert "clone" not in text, f"{name}: shapes must not be cloned"
    assert doc.count("Native Undo/Redo/reopen") == 1, "pending note once"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None or node.name == "__init__", (
                f"{name}: {node.name} lacks a return annotation"
            )


def test_real_app_helpers_when_scripts_import_them_then_signatures_exist():
    scripting = importlib.import_module("fontlabapp.scripting")
    completion = importlib.import_module("fontlabapp.script_completion")
    assert list(inspect.signature(scripting.connect_guarded).parameters)[:3] == [
        "dialog",
        "signal",
        "callback",
    ]
    assert list(inspect.signature(scripting.close_script_dialog).parameters)[:3] == [
        "dialog",
        "event",
        "key",
    ]
    assert list(inspect.signature(scripting.show_script_dialog).parameters) == [
        "dialog_type",
        "key",
    ]
    for helper in ("current_package", "names_selected_names", "names_font_glyphs"):
        assert callable(getattr(scripting, helper)), helper
    assert list(inspect.signature(completion.install).parameters) == ["dialog", "key"]


# ---------------------------------------------------------------- core arithmetic
@pytest.mark.parametrize(
    ("width", "step", "direction", "expected"),
    [
        (495, 10, "nearest", 500),
        (494, 10, "nearest", 490),
        (12.5, 5, "nearest", 15),
        (491, 10, "up", 500),
        (490, 10, "up", 490),
        (499, 10, "down", 490),
        (500, 10, "down", 500),
        (0, 10, "nearest", 0),
        (-3, 2, "nearest", -2),
    ],
)
def test_rounded_when_direction_given_then_exact_multiple(
    world, width, step, direction, expected
):
    module = load("Round Advances")
    assert module.rounded(width, step, direction) == expected, (width, step, direction)


@pytest.mark.parametrize(
    ("width", "percent", "expected"),
    [
        (500, 110, (550, 25)),
        (501, 110, (551, 25)),
        (500, 99, (495, -2)),
        (500, 101, (505, 2)),
        (500, 100, (500, 0)),
        (0, 150, (0, 0)),
    ],
)
def test_scaled_when_percent_given_then_width_and_half_shift(
    world, width, percent, expected
):
    module = load("Scale Advances")
    assert module.scaled(width, percent) == expected, (width, percent)


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ((10, 90, 100, "keep", 0), (10, 10, 100, 10, 10)),
        ((0, 81, 100, "keep", 0), (0, 19, 100, 9, 10)),
        ((0, 81, 100, "set", 200), (0, 19, 200, 59, 60)),
        ((10, 90, 100, "add", 20), (10, 10, 120, 20, 20)),
    ],
)
def test_centred_when_mode_given_then_odd_unit_goes_right(world, args, expected):
    module = load("Centre In Advance")
    assert module.centred(*args) == expected, args


def test_italic_edges_when_outline_is_slanted_then_deslanted_box(world):
    module = load("Italic Sidebearings")
    layer = Layer(150, [(0, 0), (100, 0), (200, 100), (100, 100)])
    left, right = module.italic_edges(layer, -45.0, 0)
    assert left == pytest.approx(0) and right == pytest.approx(100), (left, right)
    assert module.italic_edges(Layer(150), -45.0, 0) is None, "empty layer"


def test_italic_planner_when_set_then_dx_and_width_follow_italic_values(world):
    module = load("Italic Sidebearings")
    layer = Layer(150, [(0, 0), (100, 0), (200, 100), (100, 100)])
    plan = module.italic_planner(-45.0, 0, "set", 20, 30)(layer, "Light")
    assert (plan.dx, plan.width, plan.changed) == (20, 150, True)
    assert plan.cells == ("0", "-50", "0", "50", "20", "30"), plan.cells
    plan = module.italic_planner(-45.0, 0, "add", 10, None)(layer, "Light")
    assert (plan.dx, plan.width) == (10, 160), "add to LSB only widens by the shift"
    same = module.italic_planner(-45.0, 0, "add", None, None)(layer, "Light")
    assert not same.changed, "no side ticked is a no-op"
    assert module.italic_planner(-45.0, 0, "set", 0, 0)(Layer(150), "Light") == (
        "empty (no outline)"
    )
    assert module.italic_planner(-45.0, 0, "set", None, -500)(layer, "L") == (
        "negative width (skipped)"
    ), "negative advance is refused"


def test_is_mark_when_category_or_name_then_true(world):
    module = load("Zero-Width Marks")
    assert module.is_mark(Glyph("anything", {}, [0x0301])), "Mn"
    assert module.is_mark(Glyph("enclose", {}, [0x20DD])), "Me"
    assert module.is_mark(Glyph("multi", {}, [0x41, 0x0301])), "any code point counts"
    assert module.is_mark(Glyph("acutecomb", {}, None)), "name"
    assert module.is_mark(Glyph("gravecomb.case", {}, None)), "suffix on name"
    assert not module.is_mark(Glyph("A", {}, [65])), "letter"
    assert not module.is_mark(Glyph("A", {}, None)), "no code point"
    assert not module.is_mark(Glyph("big", {}, [0x110000])), "out of Unicode range"
    assert not module.is_mark(Glyph("neg", {}, [-1])), "negative value"


def test_is_mark_when_unicodes_missing_then_error_surfaces(world):
    module = load("Zero-Width Marks")

    class NoCodes:
        name = "x"

    with pytest.raises(AttributeError):
        module.is_mark(NoCodes())


@pytest.mark.parametrize(
    ("placement", "width", "points", "dx"),
    [
        ("keep", 300, rect(100, 200), 0),
        ("hang", 300, rect(100, 200), -300),
        ("centre", 300, rect(100, 200), -150),
    ],
)
def test_zero_planner_when_placement_then_exact_shift(
    world, placement, width, points, dx
):
    module = load("Zero-Width Marks")
    plan = module.zero_planner(placement)(Layer(width, points), "Light")
    assert (plan.dx, plan.width, plan.changed) == (dx, 0, True), placement
    flat = module.zero_planner("keep")(Layer(0, points), "Light")
    assert not flat.changed, "already zero wide and kept in place"


def test_tabular_widths_when_widest_then_per_master_maximum(world):
    module = load("Tabular Width")
    one = two_master_glyph("one", (80, 10, 70), (130, 10, 120))
    two = two_master_glyph("two", (95, 10, 85), (110, 10, 100))
    assert module.target_widths([one, two], ["Light", "Bold"], "widest", 0) == {
        "Light": 95,
        "Bold": 130,
    }
    assert module.target_widths([one], ["Light"], "fixed", 600) == {"Light": 600}
    plan = module.tabular_planner({"Light": 100})(one.findLayer("Light"), "Light")
    assert (plan.dx, plan.width) == (10, 100), "ink 60 wide in 100: lsb 20, was 10"
    assert (
        module.tabular_planner({"Light": 100})(Layer(50), "Light")
        == "empty (no outline)"
    )


# ---------------------------------------------------------------- panels
@pytest.mark.parametrize("name", NAMES)
def test_panel_when_opened_without_font_then_refuses_and_apply_is_off(world, name):
    module = load(name)
    panel = getattr(module, CLASS[name])(None)
    assert panel.subtitle.text.startswith("Open a font"), panel.subtitle.text
    assert panel.apply_button._enabled is False
    panel.apply()
    assert world.history == [], "no font: nothing is notified"
    assert panel.entries == []


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_selection_empty_then_refuses(world, name):
    _, panel = open_panel(world, name, [two_master_glyph()], selection=[])
    assert "Select" in panel.subtitle.text or "no" in panel.subtitle.text.lower()
    assert panel.apply_button._enabled is False
    panel.apply()
    assert world.history == []


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_font_switches_then_apply_refuses(world, name):
    _, panel = open_panel(
        world, name, [two_master_glyph("n", (101, 10, 90), (121, 12, 108))]
    )
    world.package = Package([], ident=99)
    panel.apply()
    assert world.history == [], "switched font must not be edited"
    assert "font changed" in panel.status.text, panel.status.text


def edited(world, name, glyphs, configure=None, **kwargs):
    module, panel = open_panel(world, name, glyphs, **kwargs)
    if configure:
        configure(module, panel)
    panel.apply_button.press()
    return module, panel


def check_one_undo(world, title, layers, glyphs):
    """Exact order: init each, edit each, stamp, ONE notify, stamp (history.commit)."""
    assert len(world.history) == 1, "exactly one notification"
    ((name, items),) = world.history
    assert name == title
    assert items == layers + glyphs, "layers then glyphs, one list"
    stamps = [("stamp", g.name) for g in glyphs]
    edits = [("edit", kind) for layer in layers for kind in layer.edit_log]
    expected = (
        [("init", "layer")] * len(layers)
        + [("init", "glyph")] * len(glyphs)
        + edits
        + stamps
        + [("notify", title)]
        + stamps
    )
    assert LOG == expected, LOG
    for item in items:
        assert item.init_calls == [0], "checkInitHistoryState(0) once per object"
    for glyph in glyphs:
        assert glyph.lastModified == STAMP, "one shared UTC stamp"
    for layer in layers:
        assert (layer.clones, layer.swaps) == (0, 0), (
            "shapes move in place, never cloned"
        )


def test_round_advances_when_applied_then_rsb_absorbs_and_one_undo(world):
    n = two_master_glyph("n", (101, 10, 90), (126, 12, 108))
    auto = Layer(101, rect(5, 95), auto=True)
    o = Glyph("o", {"Light": auto, "Bold": Layer(130, rect(10, 120))})
    _, panel = edited(world, "Round Advances", [n, o], lambda m, p: p.scope.pick(1))
    assert n.findLayer("Light").advanceWidth == 100
    assert n.findLayer("Bold").advanceWidth == 130, "126 rounds to nearest 10"
    assert n.findLayer("Light").points == rect(10, 90), "outline stays"
    assert o.findLayer("Bold").advanceWidth == 130, "already rounded: untouched"
    assert auto.advanceWidth == 101, "auto layer is never edited"
    changed = [n.findLayer("Light"), n.findLayer("Bold")]
    check_one_undo(world, "Round Advances", changed, [n])
    assert auto not in world.history[0][1], "auto layers never enter the Undo list"
    assert [e.note for e in panel.entries if e.glyph is o] == [
        "auto layer (skipped)",
        "glyph has auto layers (skipped)",
    ], "a glyph that owns an auto layer is skipped as a whole"
    assert panel.last_result == {
        "layers": 2,
        "glyphs": 1,
        "auto_skipped": 2,
        "mismatches": [],
    }
    assert "Changed 2 layers in 1 glyphs" in panel.status.text
    assert "2 layers skipped (auto)" in panel.status.text, panel.status.text


def test_round_advances_when_glyph_owns_auto_layer_then_its_manual_layers_stay(world):
    auto = Layer(101, rect(5, 95), auto=True)
    manual = Layer(126, rect(10, 120))
    o = Glyph("o", {"Light": auto, "Bold": manual})
    n = two_master_glyph("n", (101, 10, 90), (126, 12, 108))
    edited(world, "Round Advances", [n, o], lambda m, p: p.scope.pick(1))
    assert manual.advanceWidth == 126, "the geometry policy skips auto owners whole"
    assert manual.edit_log == [], "no native call on the skipped layer"
    assert o not in world.history[0][1], "an auto owner is never notified"
    assert n.findLayer("Bold").advanceWidth == 130


def test_round_advances_when_all_glyphs_source_then_uses_font_list(world):
    n = two_master_glyph("n", (101, 10, 90), (101, 10, 90))
    world.font_names = ["n"]
    _, panel = open_panel(world, "Round Advances", [n], selection=[])
    assert "Select" in panel.subtitle.text
    panel.source.pick(1)
    assert panel.apply_button._enabled is True, "all glyphs works without a selection"
    panel.step.setValue(20)
    assert panel.entries[0].plan.width == 100, panel.entries[0].plan


def test_scale_advances_when_applied_then_centred_change(world):
    n = two_master_glyph("n", (100, 10, 90), (200, 20, 180))
    edited(
        world,
        "Scale Advances",
        [n],
        lambda m, p: (p.scope.pick(1), p.percent.setValue(110.0)),
    )
    light, bold = n.findLayer("Light"), n.findLayer("Bold")
    assert (light.advanceWidth, light.points[0][0]) == (110, 15), "shift by half of +10"
    assert (bold.advanceWidth, bold.points[0][0]) == (220, 30)
    check_one_undo(world, "Scale Advances", [light, bold], [n])


def test_centre_in_advance_when_applied_then_equal_sidebearings(world):
    n = two_master_glyph("n", (100, 0, 81), (100, 30, 60))
    edited(world, "Centre In Advance", [n], lambda m, p: p.scope.pick(1))
    light = n.findLayer("Light")
    assert light.points[0][0] == 9 and light.advanceWidth == 100, "lsb 9, rsb 10"
    bold = n.findLayer("Bold")
    assert bold.points[0][0] == 35, "ink 30 in 100: lsb 35"


def test_centre_in_advance_when_set_mode_then_default_width_offered(world):
    n = two_master_glyph("n", (100, 0, 80), (100, 0, 80))
    module, panel = open_panel(world, "Centre In Advance", [n])
    panel.mode.pick(1)
    assert panel.value.value == module.WIDTH_DEFAULT
    assert panel.entries[0].plan.width == module.WIDTH_DEFAULT
    panel.mode.pick(0)
    assert panel.value._enabled is False, "value unused when the width is kept"


def test_centre_in_advance_when_new_width_negative_then_layer_skipped(world):
    n = two_master_glyph("n", (100, 0, 80), (100, 0, 80))
    _, panel = open_panel(world, "Centre In Advance", [n])
    panel.mode.pick(2)
    panel.value.setValue(-200)
    assert panel.entries[0].note == "negative width (skipped)"
    assert panel.apply_button._enabled is False
    assert [panel.table.texts(0)] == [["n · Light", "negative width (skipped)"]]


def test_zero_width_marks_when_applied_then_hang_left_and_zero_width(world):
    mark = Glyph(
        "acutecomb",
        {"Light": Layer(300, rect(100, 200)), "Bold": Layer(320, rect(110, 210))},
    )
    letter = two_master_glyph("n")
    _, panel = open_panel(world, "Zero-Width Marks", [mark, letter])
    assert [e.glyph.name for e in panel.entries] == ["acutecomb"], "filter keeps marks"
    panel.placement.pick(1)
    panel.apply_button.press()
    light = mark.findLayer("Light")
    assert (light.advanceWidth, light.points[0][0]) == (0, -200)
    check_one_undo(world, "Zero-Width Marks", [light], [mark])
    assert letter.findLayer("Light").advanceWidth == 100, "base letters stay"


def test_zero_width_marks_when_filter_off_then_all_selected_glyphs(world):
    letter = two_master_glyph("n")
    _, panel = open_panel(world, "Zero-Width Marks", [letter])
    assert "no combining marks" in panel.subtitle.text.lower()
    assert panel.apply_button._enabled is False
    panel.only_marks.tick(False)
    assert [e.glyph.name for e in panel.entries] == ["n"]
    assert panel.apply_button._enabled is True


def test_tabular_width_when_preset_then_only_existing_figures_share_widest(world):
    one = two_master_glyph("one", (80, 10, 70), (130, 10, 120))
    two = two_master_glyph("two", (95, 10, 85), (110, 10, 100))
    other = two_master_glyph("n")
    world.package = Package([one, two, other])
    world.selection = ["n"]
    module = load("Tabular Width")
    panel = module.TabularWidth(None)
    assert sorted(e.glyph.name for e in panel.entries) == ["one", "two"], (
        "preset, not selection"
    )
    panel.scope.pick(1)
    panel.apply_button.press()
    assert one.findLayer("Light").advanceWidth == 95
    assert one.findLayer("Bold").advanceWidth == 130
    assert one.findLayer("Light").points[0][0] == 17, "ink 60 in 95: lsb 17 (was 10)"
    assert other.findLayer("Light").advanceWidth == 100, "glyphs outside the set stay"
    expected = [one.findLayer("Light"), two.findLayer("Bold"), one, two]
    assert len(world.history) == 1, "one Undo step"
    assert world.history[0][1] == expected, "edited layers, then their glyphs"


def test_tabular_width_when_fixed_then_value_used_and_no_figures_diagnosed(world):
    world.package = Package([two_master_glyph("n")])
    world.selection = ["n"]
    module = load("Tabular Width")
    panel = module.TabularWidth(None)
    assert "none of these glyphs" in panel.subtitle.text.lower()
    panel.group.pick(2)
    panel.mode.pick(1)
    panel.fixed.setValue(600)
    assert panel.fixed._enabled is True
    assert panel.entries[0].plan.width == 600


def test_italic_sidebearings_when_applied_then_outline_and_advance_follow(world):
    layer = Layer(150, [(0, 0), (100, 0), (200, 100), (100, 100)])
    glyph = Glyph(
        "n",
        {
            "Light": layer,
            "Bold": Layer(150, [(0, 0), (100, 0), (200, 100), (100, 100)]),
        },
    )
    world.package = Package([glyph])
    world.package.italicAngle_value = -45.0
    world.package.xHeight_value = 0
    world.selection = ["n"]
    module = load("Italic Sidebearings")
    panel = module.ItalicSidebearings(None)
    assert panel.angle.value == -45.0 and panel.pivot.value == 250, (
        "font angle, fallback x-height"
    )
    panel.pivot.setValue(0)
    panel.mode.pick(1)
    panel.lsb.setValue(20)
    panel.rsb.setValue(30)
    panel.apply_button.press()
    assert layer.advanceWidth == 150 and layer.points[0][0] == 20
    assert layer.clones == 0 and layer.swaps == 0, "outline moves in place"
    assert layer.transforms == [(1, 0, 0, 1, 20, 0)], "one shift on the original shapes"
    check_one_undo(world, "Italic Sidebearings", [layer], [glyph])
    panel.rsb_check.tick(False)
    assert panel.rsb._enabled is False and panel.lsb._enabled is True


def auto_composite_world(world):
    """Glyph n (width 101) is the base of the auto glyph ntilde."""
    base = two_master_glyph("n", (101, 10, 90), (101, 10, 90))
    layer = Layer(100, [], auto=True)
    shape = Shape(layer)
    shape.isComponent = True
    shape.shapeData = ModuleType("shapeData")
    shape.shapeData.componentGlyph = "n"
    layer.shapes = [shape]
    plain = two_master_glyph("o", (101, 10, 90), (101, 10, 90))
    world.package = Package([base, Glyph("ntilde", {"Light": layer}), plain])
    world.selection = ["n"]
    world.font_names = ["n", "ntilde", "o"]
    return base, plain


def test_panel_when_glyph_is_base_of_auto_composite_then_refused_until_ticked(world):
    base, _ = auto_composite_world(world)
    panel = load("Round Advances").RoundAdvances(None)
    assert panel.status.text.startswith("Refused."), panel.status.text
    assert "FontLab rebuilds auto glyphs ntilde" in panel.status.text, panel.status.text
    assert panel.apply_button._enabled is False and panel.allow_auto._visible is True
    panel.apply()
    assert world.history == [] and base.findLayer("Light").advanceWidth == 101, (
        "refused"
    )
    assert panel.status.text.startswith("Refused.")
    panel.allow_auto.tick(True)
    assert panel.apply_button._enabled is True, "the override enables Apply"


def test_panel_when_override_ticked_then_applies_and_keeps_warning(world):
    base, _ = auto_composite_world(world)
    panel = load("Round Advances").RoundAdvances(None)
    panel.allow_auto.tick(True)
    panel.apply_button.press()
    assert base.findLayer("Light").advanceWidth == 100
    assert len(world.history) == 1
    assert panel.status.text.startswith("Changed 1 layers in 1 glyphs")
    assert "FontLab rebuilds auto glyphs ntilde" in panel.status.text, panel.status.text


def test_panel_when_selection_changes_to_safe_glyph_then_override_is_forgotten(world):
    auto_composite_world(world)
    panel = load("Round Advances").RoundAdvances(None)
    panel.allow_auto.tick(True)
    world.selection = ["o"]
    panel.selection_button.press()
    assert panel.allow_auto.isChecked() is False and panel.allow_auto._visible is False
    assert panel.apply_button._enabled is True, (
        "no auto dependants: nothing to override"
    )


def test_panel_when_closed_then_shared_close_helper_runs_with_key(world):
    _, panel = open_panel(world, "Scale Advances", [two_master_glyph()])
    assert panel.close() is True
    assert world.closed == ["metrics_scale_advances"]


@pytest.mark.parametrize("name", NAMES)
def test_main_when_called_then_opens_one_keyed_panel(world, name):
    module = load(name)
    world.package = Package([two_master_glyph()])
    world.selection = ["n"]
    dialog = module.main()
    assert world.shown == [(getattr(module, CLASS[name]).KEY, dialog)]
    assert isinstance(dialog, getattr(module, CLASS[name]))


def test_commit_when_edit_raises_then_after_notification_still_sent(world):
    module = load("Scale Advances")
    shared, history = world.app["metrics_panel"], world.app["history"]
    layer = Layer(100, rect(10, 90))

    def broken(*args):
        raise RuntimeError("boom")

    layer.applyTransform = broken
    glyph = Glyph("n", {"Light": layer})
    world.package = Package([glyph], ("Light",))
    world.font_names = ["n"]
    entries = shared.survey([glyph], ["Light"], module.scale_planner(120.0))
    facts = history.scan_auto_facts(world.package)
    with pytest.raises(history.PartialWriteError, match="use Edit > Undo") as caught:
        shared.commit("Scale Advances", entries, facts=facts)
    assert "boom" in str(caught.value), caught.value
    assert len(world.history) == 1, "the notification still runs after a failed edit"
    assert glyph.lastModified == STAMP, "the glyph is stamped after the failed edit"


def test_unit_when_half_then_rounds_up_unlike_python_round(world):
    module = load("Scale Advances")
    unit = module.metrics_panel.unit
    assert [unit(v) for v in (0.5, 1.5, 2.5, -0.5, -1.5)] == [1, 2, 3, 0, -1]


def test_panel_when_native_read_fails_then_error_shown_and_apply_off(world):
    class Broken(Layer):
        @property
        def boundingBox(self):
            raise RuntimeError("native read failed")

    glyph = Glyph("n", {"Light": Broken(100, rect(10, 90)), "Bold": Layer(100)})
    world.package = Package([glyph])
    world.selection = ["n"]
    module = load("Centre In Advance")
    panel = module.CentreInAdvance(None)
    assert panel.status.text.startswith("Error: RuntimeError"), panel.status.text
    assert panel.apply_button._enabled is False
    panel.apply()
    assert world.history == [], "a failed plan never edits the font"
    assert panel.status.text.startswith("Error: RuntimeError")


# ---------------------------------------------------------------- real App names
def test_real_app_names_when_imported_from_installed_app_then_all_exist():
    """No fakes: the real Fly aliases give every App name that the scripts use."""
    used = app_names_used([METRICS / f"{name}.py" for name in NAMES])
    assert {"fly.ap.scripting", "fly.ap.metrics_panel"} <= set(used), used
    assert {"panel_type", "make_plan", "Planner", "LayerPlan"} <= used[
        "fly.ap.metrics_panel"
    ]
    check_real_app_names(used)


def test_scripts_when_loaded_then_panel_base_is_the_shared_app_class(world):
    for name in NAMES:
        module = load(name)
        assert module.metrics_panel is world.app["metrics_panel"], name
        assert module.MetricsPanel is module.metrics_panel.panel_type(), name
        assert getattr(module, CLASS[name]).__mro__[1] is module.MetricsPanel, name
        for moved in ("survey", "commit", "auto_dependants", "make_table"):
            assert moved not in vars(module), f"{name} still defines {moved}"


def auto_pair(base_name, auto_name):
    base = two_master_glyph(base_name, (101, 10, 90), (101, 10, 90))
    layer = Layer(100, [], auto=True)
    shape = Shape(layer)
    shape.isComponent = True
    shape.shapeData = ModuleType("shapeData")
    shape.shapeData.componentGlyph = base_name
    layer.shapes = [shape]
    return base, Glyph(auto_name, {"Light": layer})


def test_override_when_selection_moves_to_other_auto_base_then_cleared_and_refused(
    world,
):
    n, ntilde = auto_pair("n", "ntilde")
    m, mtilde = auto_pair("m", "mtilde")
    world.package = Package([n, ntilde, m, mtilde])
    world.selection = ["n"]
    world.font_names = ["n", "ntilde", "m", "mtilde"]
    panel = load("Round Advances").RoundAdvances(None)
    panel.allow_auto.tick(True)
    assert panel.apply_button._enabled is True
    world.selection = ["m"]
    panel.selection_button.press()
    assert panel.allow_auto.isChecked() is False, "override belonged to the first set"
    assert panel.status.text.startswith("Refused."), panel.status.text
    assert panel.apply_button._enabled is False
    panel.apply()
    assert world.history == [], "second set is refused without a new tick"


def test_override_when_glyph_source_changes_to_other_set_then_cleared(world):
    n, ntilde = auto_pair("n", "ntilde")
    m, mtilde = auto_pair("m", "mtilde")
    world.package = Package([n, ntilde, m, mtilde])
    world.selection = ["n"]
    world.font_names = ["n", "ntilde", "m", "mtilde"]
    panel = load("Round Advances").RoundAdvances(None)
    panel.allow_auto.tick(True)
    panel.source.pick(1)  # all glyphs: a different set of changed names
    assert panel.allow_auto.isChecked() is False
    assert panel.apply_button._enabled is False


def test_apply_when_width_does_not_stick_then_mismatch_reported(world):
    n = two_master_glyph("n", (101, 10, 90), (101, 10, 90))
    n.findLayer("Light").stubborn_width = True
    _, panel = open_panel(world, "Round Advances", [n])
    panel.apply_button.press()
    assert panel.last_result["mismatches"] == ["n · Light: advance 101, planned 100"]
    assert "did not read back as planned" in panel.status.text, panel.status.text
    assert "n · Light: advance 101, planned 100" in panel.status.text


def test_apply_when_outline_does_not_move_then_ink_edge_mismatch_reported(world):
    class Stuck(Layer):
        def applyTransform(self, transform):
            self.log("move")

    n = Glyph("n", {"Light": Stuck(100, rect(10, 90)), "Bold": Layer(100)})
    _, panel = open_panel(world, "Scale Advances", [n])
    panel.percent.setValue(110.0)
    panel.apply_button.press()
    assert any("ink edge" in text for text in panel.last_result["mismatches"]), (
        panel.last_result
    )


def test_apply_when_cache_update_fails_then_error_shown_and_history_still_notified(
    world,
):
    n = two_master_glyph("n", (100, 10, 90), (100, 10, 90))
    n.findLayer("Light").cache_ok = False
    _, panel = open_panel(world, "Scale Advances", [n])
    panel.percent.setValue(110.0)
    panel.apply_button.press()
    assert len(world.history) == 1, "the notification still runs"
    assert "Error: PartialWriteError" in panel.status.text, panel.status.text
    assert "use Edit > Undo" in panel.status.text, panel.status.text


def test_apply_when_native_updates_pending_then_refused_before_history(world):
    n = two_master_glyph("n", (101, 10, 90), (101, 10, 90))
    _, panel = open_panel(world, "Round Advances", [n])
    world.updates = [17]
    panel.apply_button.press()
    assert world.history == [] and LOG == [], "refused before any history call"
    assert n.findLayer("Light").advanceWidth == 101
    assert panel.status.text == (
        "Native glyph updates are pending; finish the current edit first."
    ), panel.status.text


def test_panel_when_base_reaches_auto_glyph_through_composite_then_refused(world):
    """n -> manual nbar -> auto nbaracute: the base is found through the chain."""
    n = two_master_glyph("n", (101, 10, 90), (101, 10, 90))
    bar = Layer(100, [])
    bar_shape = Shape(bar)
    bar_shape.isComponent = True
    bar_shape.shapeData = ModuleType("shapeData")
    bar_shape.shapeData.componentGlyph = "n"
    bar.shapes = [bar_shape]
    acute = Layer(100, [], auto=True)
    acute_shape = Shape(acute)
    acute_shape.isComponent = True
    acute_shape.shapeData = ModuleType("shapeData")
    acute_shape.shapeData.componentGlyph = "nbar"
    acute.shapes = [acute_shape]
    world.package = Package(
        [n, Glyph("nbar", {"Light": bar}), Glyph("nbaracute", {"Light": acute})]
    )
    world.selection = ["n"]
    world.font_names = ["n", "nbar", "nbaracute"]
    panel = load("Round Advances").RoundAdvances(None)
    assert panel.status.text.startswith("Refused."), panel.status.text
    assert "FontLab rebuilds auto glyphs nbaracute" in panel.status.text
    panel.apply()
    assert world.history == [] and n.findLayer("Light").advanceWidth == 101


@pytest.mark.parametrize("field", ["metricsLeft", "metricsRight", "metricsWidth"])
def test_survey_when_metrics_link_then_layer_listed_and_skipped(world, field):
    n = two_master_glyph("n", (101, 10, 90), (101, 10, 90))
    setattr(n.findLayer("Light"), field, "=o")
    _, panel = open_panel(world, "Round Advances", [n])
    panel.scope.pick(1)
    assert panel.entries[0].note == "metrics link or expression (skipped)", (
        panel.entries[0]
    )
    assert panel.table.texts(0) == ["n · Light", "metrics link or expression (skipped)"]
    panel.apply_button.press()
    assert n.findLayer("Light").advanceWidth == 101, "linked layer untouched"
    assert n.findLayer("Bold").advanceWidth == 100


def test_panel_when_glyph_lacks_master_then_row_says_so(world):
    glyph = Glyph("n", {"Light": Layer(101, rect(10, 90))})
    _, panel = open_panel(world, "Round Advances", [glyph])
    panel.scope.pick(1)
    assert [e.note for e in panel.entries] == ["", "no layer in this master"]
    assert panel.table.texts(1) == ["n · Bold", "no layer in this master"]
    panel.apply_button.press()
    assert glyph.findLayer("Light").advanceWidth == 100, "other masters still edited"


def test_centred_when_edges_fractional_then_ink_uses_rounded_edges(world):
    module = load("Centre In Advance")
    assert module.centred(0.4, 80.6, 100, "keep", 0) == (0, 19, 100, 9, 10)
    plan = module.centre_planner("keep", 0)(
        Layer(100, [(0.4, 0), (80.6, 0), (80.6, 5)]), "L"
    )
    assert (plan.dx, plan.width) == (9, 100), plan
