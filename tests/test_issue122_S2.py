# this_file: tests/test_issue122_S2.py
# SPDX-License-Identifier: Apache-2.0
"""Three sidebearing Metrics scripts, tested against owned fakes and the real App helpers.

Equalize Sidebearings, Sidebearings Tuner and Copy Metrics From Reference sit on
the shared App panel ``fly.ap.metrics.panel.model``. The fakes replace FontLab layers,
the ``fontlab`` module and Qt widgets; the real App modules (``metrics_panel``,
``history``) run over them, reached as ``fly.ap.<module>`` like inside FontLab.
The tests prove the planning arithmetic, the refusal paths and the Undo shape
(one notified list, no auto layers). They do not prove native FontLab behaviour.
"""

import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import ClassVar

import pytest
from _fgpackage_support import fg_package
from conftest import app_names_used, app_namespace, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "Scripts/Metrics"
NAMES = [
    "Equalize Sidebearings",
    "Sidebearings Tuner",
    "Copy Metrics From Reference",
]
CLASS = {
    "Equalize Sidebearings": "EqualizeSidebearings",
    "Sidebearings Tuner": "SidebearingsTuner",
    "Copy Metrics From Reference": "CopyMetricsFromReference",
    "Vertical Metrics Diagram": "VerticalMetricsDiagram",
}
KEYS = {
    "Equalize Sidebearings": "metrics_equalize_sidebearings",
    "Sidebearings Tuner": "metrics_sidebearings_tuner",
    "Copy Metrics From Reference": "metrics_copy_from_reference",
    "Vertical Metrics Diagram": "metrics_vertical_metrics_diagram",
}
DIAGRAM = "Vertical Metrics Diagram"  # Read-only; not a writer, so not in NAMES.
#: Members of QObject/QWidget/QDialog that a Python subclass must not shadow.
NATIVE_MEMBERS = frozenset(
    {
        "accept",
        "accepted",
        "activateWindow",
        "children",
        "close",
        "cursor",
        "destroyed",
        "done",
        "enabled",
        "event",
        "exec",
        "finished",
        "focusWidget",
        "font",
        "geometry",
        "height",
        "hide",
        "layout",
        "locale",
        "mask",
        "modal",
        "move",
        "name",
        "objectName",
        "open",
        "palette",
        "parent",
        "pos",
        "property",
        "raise_",
        "rect",
        "reject",
        "rejected",
        "repaint",
        "resize",
        "result",
        "scroll",
        "sender",
        "setResult",
        "show",
        "size",
        "sizeHint",
        "style",
        "title",
        "tr",
        "update",
        "visible",
        "width",
        "windowTitle",
        "x",
        "y",
    }
)


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
            "textChanged",
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
    """A PythonQt QDialog: a subclass attribute must not shadow a native member."""

    def __setattr__(self, name, value):
        if name in NATIVE_MEMBERS:
            raise AttributeError(f"Slot '{name}' can not be overwritten")
        object.__setattr__(self, name, value)

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


class LineEdit(Widget):
    def __init__(self, text="", *a):
        super().__init__()
        self._text = text
        self.completer = None
        self.placeholder = ""

    @property
    def text(self):
        return self._text

    def setText(self, text):
        if text != self._text:
            self._text = text
            self.textChanged.emit(text)

    def setCompleter(self, completer):
        self.completer = completer

    def setPlaceholderText(self, text):
        self.placeholder = text


class Completer(Widget):
    def __init__(self, *a):
        super().__init__()
        self.model = None

    def setModel(self, model):
        self.model = model


class StringListModel(Widget):
    def __init__(self, *a):
        super().__init__()
        self.strings = []

    def setStringList(self, strings):
        self.strings = list(strings)


class Spin(Widget):
    def __init__(self, *a):
        super().__init__()
        self._value = 0
        self.range = (0, 0)
        self.suffix = ""

    @property
    def value(self):
        return self._value

    def setRange(self, low, high):
        self.range = (low, high)

    def setSuffix(self, text):
        self.suffix = text

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

    def font(self):
        return FakeFont()

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


class FakeTransform:
    def __init__(self, m11=1, m12=0, m21=0, m22=1, dx=0, dy=0):
        self.m = (m11, m12, m21, m22, dx, dy)

    def point(self, p):
        m11, m12, m21, m22, dx, dy = self.m
        return (m11 * p[0] + m21 * p[1] + dx, m12 * p[0] + m22 * p[1] + dy)

    def map(self, path):
        return FakePath(self.point(p) for p in path.points)


class FakePath:
    def __init__(self, points=()):
        self.points = list(points)

    def addPath(self, other):
        self.points.extend(other.points)

    def setFillRule(self, rule):
        pass


class Painter:
    """Records every drawing call; end() must always run."""

    made: ClassVar[list] = []
    Antialiasing = 1

    def __init__(self, device=None):
        self.calls = []
        self.ended = False
        Painter.made.append(self)

    def end(self):
        self.ended = True

    def font(self):
        return FakeFont()

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: self.calls.append((name, a))


class QWidgetFake(Widget):
    """A native QWidget: width/height are read-only properties in PythonQt."""

    width = 600
    height = 300

    def __setattr__(self, name, value):
        if name in NATIVE_MEMBERS:
            raise AttributeError(f"Slot '{name}' can not be overwritten")
        object.__setattr__(self, name, value)


def fake_qt():
    qt = ModuleType("fly.qt")
    gui, core = ModuleType("QtGui"), ModuleType("QtCore")
    gui.QDialog = Dialog
    gui.QLabel = Label
    gui.QLineEdit = LineEdit
    gui.QCompleter = Completer
    gui.QStringListModel = StringListModel
    gui.QSpinBox = Spin
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
    gui.QTransform = FakeTransform
    gui.QPainterPath = FakePath
    gui.QPainter = Painter
    gui.QWidget = QWidgetFake
    gui.QPen = lambda *a: ("pen", a)
    core.QPointF = lambda x, y: (x, y)
    core.QRectF = lambda *a: ("rect", a)
    core.Qt = Consts()
    core.QDateTime = DateTime
    qt.QtGui, qt.QtCore = gui, core
    return qt


# ---------------------------------------------------------------- FontLab fakes
LOG: list = []  # Ordered ("init" | "edit" | "stamp" | "notify", detail) events.
STAMP = "UTC-stamp"


class DateTime:
    @staticmethod
    def currentDateTimeUtc():
        return STAMP


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


class Layer:
    isNull = False
    isMasterLayer = True

    def __init__(self, width, points=(), auto=False):
        self._width = width
        self.points = list(points)
        self.autoLayer = auto
        self.transforms = []
        self.init_calls = []
        self.edit_log = []
        self.shapes = [Shape(self)]
        self.metricsLeft = self.metricsRight = self.metricsWidth = ""
        self.cache_ok = True

    @property
    def advanceWidth(self):
        return self._width

    @advanceWidth.setter
    def advanceWidth(self, value):
        self.log("width")
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

    def __init__(self, name, layers):
        self.name, self.layers_by_master = name, layers
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
        self.fgPackage = fg_package(self.glyphs)
        self.metrics = {
            m: {"ascender": 800, "capsHeight": 700, "xHeight": 500, "descender": -200}
            for m in masters
        }
        self.metric_reads = []

    def font_metrics(self, master):
        """Stand-in for fontlab.FontMetrics(package, master): no master switch."""
        self.metric_reads.append(master)
        values = self.metrics[master]
        if values is None:
            raise RuntimeError("metrics not readable")
        found = ModuleType("FontMetrics")
        for key, value in values.items():
            setattr(found, key, value)
        return found

    def setMaster(self, *args):
        raise AssertionError("the read-only diagram must not switch masters")

    def findName(self, name):
        return self.glyphs.get(name)


def rect(left, right, top=100):
    return [(left, 0), (right, 0), (right, top), (left, top)]


def glyph2(name="n", light=(100, 10, 90), bold=(120, 12, 108)):
    """Two masters; each tuple is (advance, left ink edge, right ink edge)."""
    return Glyph(
        name,
        {
            "Light": Layer(light[0], rect(light[1], light[2])),
            "Bold": Layer(bold[0], rect(bold[1], bold[2])),
        },
    )


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
        self.names_error = None


@pytest.fixture
def world(monkeypatch, real_app):
    state = World()
    state.mp = monkeypatch
    LOG.clear()
    fly = ModuleType("fly")
    ap = app_namespace()
    scripting = ModuleType("fly.ap.core.scripting")
    completion = ModuleType("fly.ap.core.completion")
    fontlab = ModuleType("fontlab")
    items = ModuleType("items")

    def notify(title, objs):
        LOG.append(("notify", title))
        state.history.append((title, objs))

    items.notifyChangesApplied = notify
    fontlab.flItems = lambda: items
    fontlab.flGlyph = ModuleType("flGlyph")
    fontlab.flGlyph.updatedFgGlyphs = lambda: list(state.updates)
    fontlab.FontMetrics = lambda package, master: package.font_metrics(master)
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

    def font_glyphs():
        if state.names_error is not None:
            raise state.names_error
        return [(n, []) for n in state.font_names]

    scripting.current_package = lambda expected_id=None: state.package
    scripting.names_selected_names = lambda: list(state.selection)
    scripting.names_font_glyphs = font_glyphs

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
        "fly.ap.core.scripting": scripting,
        "fly.ap.core.completion": completion,
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


def load(name: str):
    assert name == DIAGRAM
    return importlib.import_module("fontlabapp.studios.vertical_metrics.diagram")


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


def auto_base_world(world, name):
    """Glyph n is the base of the auto glyph ntilde. Return (module, panel, n)."""
    base = glyph2("n", (101, 10, 90), (101, 10, 90))
    layer = Layer(100, [], auto=True)
    shape = Shape(layer)
    shape.isComponent = True
    shape.shapeData = ModuleType("shapeData")
    shape.shapeData.componentGlyph = "n"
    layer.shapes = [shape]
    ref = glyph2("H", (100, 30, 70), (100, 30, 70))
    world.package = Package([base, Glyph("ntilde", {"Light": layer}), ref])
    world.selection = ["n"]
    world.font_names = ["n", "ntilde", "H"]
    from _wp03_metrics_tabs import spacing_writer

    studio, panel, staged, shell = spacing_writer(world, name, list(world.package.glyphs.values()), selection=["n"])
    return studio, panel, staged, shell, base


# ---------------------------------------------------------------- files
@pytest.mark.parametrize("name", NAMES)
def test_script_file_when_listed_then_has_house_header_and_py311_syntax(name):
    from _wp03_metrics_tabs import historical_text
    path = METRICS / f"{name}.py"
    text = historical_text(path)
    assert (METRICS / "Spacing Studio.py").is_file()
    assert text.startswith(f"# this_file: Scripts/Metrics/{name}.py\n"), "this_file"
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
    flat = " ".join(doc.split())
    assert "the author's own FontLab sample, Apache-2.0" in flat, "credit wording"
    for jargon in (
        "issue 122",
        "D22",
        "batch",
        "reviewed App",
        "S2",
        "owner decision",
        "fragment",
    ):
        assert jargon not in text, f"{name}: internal jargon '{jargon}'"
    for claim in ("measured natively", "Undo restores", "stem hints", "Stem hints"):
        assert claim not in text, f"{name}: unproven claim '{claim}'"
    assert "clone" not in text, f"{name}: shapes must not be cloned"
    assert "UpdateAll()" not in text.replace("does not call UpdateAll", ""), (
        "no UpdateAll"
    )
    assert "Native Undo/Redo/reopen" not in doc, "no acceptance-status line"
    assert "from fly.ap import" not in text, "import App modules as fly.ap.<module>"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None or node.name == "__init__", (
                f"{name}: {node.name} lacks a return annotation"
            )
            for arg in node.args.args + node.args.kwonlyargs:
                assert arg.arg == "self" or arg.annotation is not None, (
                    f"{name}: {node.name}({arg.arg}) lacks a type hint"
                )


def test_real_app_names_when_imported_from_installed_app_then_all_exist(tmp_path):
    """No fakes: the real Fly aliases give every App name that the scripts use."""
    from _wp03_metrics_tabs import historical_text

    paths = []
    for name in [*NAMES, DIAGRAM]:
        path = tmp_path / f"{name}.py"
        path.write_text(historical_text(METRICS / f"{name}.py"))
        paths.append(path)
    used = app_names_used(paths)
    assert {"fly.ap.core.scripting", "fly.ap.metrics.panel.model"} <= set(used), used
    assert {"panel_type", "make_plan", "ink_edges", "unit"} <= used[
        "fly.ap.metrics.panel.model"
    ]
    check_real_app_names(used)


def test_scripts_when_loaded_then_panel_base_is_the_shared_app_class(world):
    tabs = importlib.import_module("fontlabapp.studios.spacing_studio.tabs")
    for cls in (tabs.SidebearingsTab, tabs.ReferenceTab):
        assert cls.__mro__[1] is tabs.Tab
    for moved in ("survey", "commit", "auto_dependants", "make_table"):
        assert moved not in vars(tabs), f"spacing tabs still define {moved}"


def test_dialog_fake_when_native_member_assigned_then_raises():
    with pytest.raises(AttributeError, match="can not be overwritten"):
        Dialog().result = 1


# ---------------------------------------------------------------- arithmetic
@pytest.mark.parametrize(
    ("lsb", "rsb", "rule", "expected"),
    [
        (10, 20, "average", (15, 15)),
        (10, 21, "average", (15, 16)),
        (-3, 0, "average", (-2, -1)),
        (10, 20, "lsb", (10, 10)),
        (10, 20, "rsb", (20, 20)),
        (10, -20, "min", (-20, -20)),
        (10, -20, "max", (10, 10)),
    ],
)
def test_equalized_when_rule_given_then_exact_sides(world, lsb, rsb, rule, expected):
    from fontlabapp.studios.spacing_studio import model as module
    assert module.equalized(lsb, rsb, rule) == expected, (lsb, rsb, rule)


def test_equalize_planner_when_average_then_width_kept_and_right_takes_odd_unit(world):
    from fontlabapp.studios.spacing_studio import model
    before = model.measure((10, 79), 100)
    plan = model.equalize(before, "average")
    assert (plan.dx, plan.width, plan.changed) == (5, 100, True)
    assert tuple(map(str, (before.lsb, before.rsb, before.width, plan.lsb, plan.rsb, plan.width))) == ("10", "21", "100", "15", "16", "100")
    plan = model.equalize(before, "lsb")
    assert (plan.dx, plan.width) == (0, 89), "rsb21 becomes10: width drops by11"
    assert not model.equalize(model.measure((10, 89), 100), "average").changed


def test_equalize_planner_when_empty_or_negative_width_then_skip_text(world):
    from _wp03_metrics_tabs import spacing_panel
    from fontlabapp.studios.spacing_studio import model
    for layer, note in [(Layer(100), "empty (no outline)"), (Layer(0, rect(0, 300)), "negative width (skipped)")]:
        studio, _ = spacing_panel(world, "Equalize Sidebearings", [Glyph("n", {"Light": layer})])
        rows = studio.plan(lambda n, before, layer, master: model.equalize(before, "min"), ["n"])
        assert rows[0].note == note


@pytest.mark.parametrize(
    ("current", "mode", "value", "expected"),
    [
        (40, "set", 25, 25),
        (40, "add", -5, 35),
        (40, "scale", 150, 60),
        (25, "scale", 50, 13),
        (-25, "scale", 50, -12),
        (40, "scale", 0, 0),
    ],
)
def test_tuned_when_mode_given_then_whole_units_half_up(
    world, current, mode, value, expected
):
    from fontlabapp.studios.spacing_studio import model

    assert model.tuned(current, mode, value) == expected, (current, mode, value)


def test_tuner_planner_when_sides_chosen_then_dx_and_width_follow(world):
    from _wp03_metrics_tabs import spacing_panel
    from fontlabapp.studios.spacing_studio import model
    before = model.measure((10, 89), 100)
    plan = model.tune(before, "set", 20, 30)
    assert (plan.dx, plan.width, plan.changed) == (10, 129, True)
    assert tuple(map(str, (before.lsb, before.rsb, plan.lsb, plan.rsb, plan.width))) == ("10", "11", "20", "30", "129")
    plan = model.tune(before, "add", None, 5)
    assert (plan.dx, plan.width) == (0, 105), "RSB only: outline stays"
    assert not model.tune(before, "set", None, None).changed
    studio, _ = spacing_panel(world, "Sidebearings Tuner", [Glyph("n", {"Light": Layer(100)})])
    rows = studio.plan(lambda n, before, layer, master: model.tune(before, "set", 0, 0), ["n"])
    assert rows[0].note == "empty (no outline)"
    assert model.tune(before, "set", -100, 0) == "negative width (skipped)"


@pytest.mark.parametrize(
    ("mode", "offset", "expected"),
    [
        ("both", 0, (30, 40, 149)),
        ("both", 5, (35, 45, 159)),
        ("lsb", 0, (30, 11, 120)),
        ("rsb", -2, (10, 38, 127)),
        ("width", 0, (60, 61, 200)),
        ("width", -1, (59, 61, 199)),
    ],
)
def test_copied_when_mode_given_then_reference_values_plus_offset(
    world, mode, offset, expected
):
    from fontlabapp.studios.spacing_studio import model

    # Own: lsb 10, rsb 11, width 100, ink 79. Reference: lsb 30, rsb 40, width 200.
    plan = model.copied(model.measure((10, 89), 100), (30, 40, 200), mode, offset)
    assert (plan.lsb, plan.rsb, plan.width) == expected


def test_copied_when_width_shrinks_by_odd_amount_then_right_takes_odd_unit(world):
    from fontlabapp.studios.spacing_studio import model

    # Width 100 -> 95: change -5, split toward zero: left -2, right -3.
    plan = model.copied(model.measure((10, 89), 100), (0, 0, 95), "width", 0)
    assert (plan.lsb, plan.rsb, plan.width) == (8, 8, 95)


def test_copy_planner_when_reference_layer_missing_or_empty_then_skip_text(world):
    from _wp03_metrics_tabs import spacing_panel
    from fontlabapp.studios.spacing_studio import model
    ref = Glyph("H", {"Light": Layer(200)})
    own = Layer(100, rect(10, 89))
    studio, _ = spacing_panel(world, "Copy Metrics From Reference", [Glyph("n", {"Light": own}), ref])
    before = model.measure((10, 89), 100)
    assert studio.reference_planner("H", "both", 0)("n", before, own, "Bold") == "no reference layer in this master"
    assert studio.reference_planner("H", "both", 0)("n", before, own, "Light") == "reference has no outline"
    plan = studio.reference_planner("H", "width", 0)("n", before, own, "Light")
    assert (plan.dx, plan.width) == (50, 200), "width mode needs only the advance"
    world.package.glyphs["n"].layers_by_master["Light"] = Layer(100)
    assert studio.plan(studio.reference_planner("H", "width", 0), ["n"])[0].note == "empty (no outline)"


# ---------------------------------------------------------------- panels
@pytest.mark.parametrize("name", NAMES)
def test_panel_when_opened_without_font_then_refuses_and_apply_is_off(world, name):
    from _wp03_metrics_tabs import spacing_writer

    studio, panel, staged, shell = spacing_writer(world, name, None)
    assert studio.status.startswith("Open a font"), studio.status
    assert not shell.apply_button._enabled
    shell.run("apply")
    assert world.history == [] and studio.rows == [] and not staged.ready()


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_selection_empty_then_refuses(world, name):
    from _wp03_metrics_tabs import spacing_writer

    studio, panel, staged, shell = spacing_writer(world, name, [glyph2(), glyph2("H")], selection=[])
    assert "Select" in studio.status, studio.status
    assert not shell.apply_button._enabled
    shell.run("apply")
    assert world.history == [] and not staged.ready()


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_font_switches_then_apply_refuses(world, name):
    from _wp03_metrics_tabs import spacing_writer

    _, panel, staged, shell = spacing_writer(world, name,
        [glyph2("n", (101, 10, 90)), glyph2("H", (100, 30, 70))], selection=["n"])
    shell.run("preview")
    assert staged.ready() and shell.apply_button._enabled, shell.status.text
    world.package = Package([], ident=99)
    shell.run("apply")
    assert world.history == [], "switched font must not be edited"
    assert "original font" in shell.status.text, shell.status.text


@pytest.mark.parametrize("name", NAMES)
def test_panel_when_glyph_is_base_of_auto_composite_then_refused_until_ticked(
    world, name
):
    studio, panel, staged, shell, base = auto_base_world(world, name)
    shell.run("preview")
    assert studio.status.startswith("Refused."), studio.status
    assert "FontLab rebuilds auto glyphs ntilde" in studio.status
    assert not shell.apply_button._enabled and not staged.ready()
    shell.run("apply")
    assert world.history == [] and base.findLayer("Light").advanceWidth == 101
    panel.allow_bases.setChecked(True)
    shell.run("preview")
    shell.run("apply")
    assert len(world.history) == 1, shell.status.text
    assert world.history[0][1] == [base.findLayer("Light"), base]


@pytest.mark.parametrize("name", NAMES)
def test_main_when_called_then_opens_one_keyed_panel(world, name):
    import runpy
    import fontlabapp.studios.spacing_studio as app
    calls = []
    world.mp.setattr(app, "show", lambda: calls.append(name))
    world.mp.setitem(sys.modules, "fly.ap.studios.spacing_studio", app)
    runpy.run_path(str(METRICS / "Spacing Studio.py"), run_name="__main__")
    assert calls == [name]
    # App test_studio_spacing_studio.py::test_wp03_spacing_profile_refresh_and_close_owns_connections retains actual lifecycle.


@pytest.mark.parametrize("name", NAMES)
def test_apply_when_native_updates_pending_then_writes_and_discloses(world, name):
    from _wp03_metrics_tabs import spacing_writer

    _, panel, staged, shell = spacing_writer(world, name,
        [glyph2("n", (101, 10, 90)), glyph2("H", (100, 30, 70))], selection=["n"])
    shell.run("preview")
    world.updates = [17]
    LOG.clear()
    shell.run("apply")
    assert world.history and world.updates == [17]
    result = world.commit_result
    assert result.pending_updates == (17,) and "8537" in shell.status.text and result.pending_note in shell.status.text


def test_equalize_when_applied_on_all_masters_then_one_undo_and_auto_skipped(world):
    n = glyph2("n", (100, 10, 80), (120, 12, 100))
    auto = Layer(101, rect(5, 95), auto=True)
    o = Glyph("o", {"Light": auto, "Bold": Layer(130, rect(10, 120))})
    from _wp03_metrics_tabs import spacing_panel

    studio, panel = spacing_panel(world, "Equalize Sidebearings", [n, o])
    panel.all_masters.setChecked(True)
    assert panel.equalize()
    light, bold = n.findLayer("Light"), n.findLayer("Bold")
    assert (light.advanceWidth, light.points) == (100, rect(15, 85))
    assert (bold.advanceWidth, bold.points) == (120, rect(16, 104)), "12+20 -> 16+16"
    assert light.transforms == [(1, 0, 0, 1, 5, 0)], "one in-place shift"
    assert auto.advanceWidth == 101 and auto.transforms == []
    check_one_undo(world, "Spacing Studio: equalize sidebearings n", [light, bold], [n])
    assert [row.note for row in studio.rows if row.glyph == "o"] == [
        "auto layer (skipped)",
        "glyph has auto layers (skipped)",
    ]
    assert "auto layer (skipped)" in studio.status, studio.status


ADD, SET, SCALE = 0, 1, 2  # Sidebearings Tuner operation order.


def test_tuner_when_opened_then_add_zero_and_first_preview_changes_nothing(world):
    from _wp03_metrics_tabs import spacing_panel
    from fontlabapp.studios.spacing_studio.staged import Staged

    _, panel = spacing_panel(world, "Sidebearings Tuner", [glyph2()])
    assert panel.operation.currentIndex == ADD
    assert "Add" in panel.operation.items[0]
    assert (panel.lsb_field.text, panel.rsb_field.text) == ("0", "0")
    staged = Staged(panel)
    staged.preview(panel.tune)
    assert not staged.ready(), "one Enter key press writes nothing"
    assert world.history == []


def test_tuner_when_scale_chosen_then_value_becomes_percent_and_back(world):
    from _wp03_metrics_tabs import spacing_panel
    from fontlabapp.studios.spacing_studio.staged import Staged

    _, panel = spacing_panel(world, "Sidebearings Tuner", [glyph2()])
    panel.operation.pick(SCALE)
    assert (panel.lsb_field.text, panel.rsb_field.text) == ("100", "100")
    assert panel.units.text == "%"
    staged = Staged(panel)
    staged.preview(panel.tune)
    assert not staged.ready(), "100 % is a no-op"
    panel.operation.pick(SET)
    assert (panel.lsb_field.text, panel.rsb_field.text) == ("0", "0")
    assert panel.units.text == "units"
    panel.rsb_field.setText("")
    panel.operation.pick(SCALE)
    assert panel.lsb_field.text == "100" and panel.rsb_field.text == "", "blank keeps the unticked side"



def test_tuner_when_typed_100_goes_through_scale_then_value_is_kept(world):
    from _wp03_metrics_tabs import spacing_panel

    _, panel = spacing_panel(world, "Sidebearings Tuner", [glyph2()])
    panel.operation.pick(SET)
    panel.lsb_field.setText("100")
    panel.operation.pick(SCALE)
    assert int(panel.lsb_field.text) == 100 and int(panel.rsb_field.text) == 100
    panel.operation.pick(SET)
    assert int(panel.lsb_field.text) == 100, "a typed 100 is not the neutral value"
    assert int(panel.rsb_field.text) == 0, "the neutral 100 that the swap put in goes back"


def test_tuner_when_scale_value_edited_then_leaving_keeps_it(world):
    from _wp03_metrics_tabs import spacing_panel

    _, panel = spacing_panel(world, "Sidebearings Tuner", [glyph2()])
    panel.operation.pick(SCALE)
    panel.lsb_field.setText("150")
    panel.operation.pick(ADD)
    assert (int(panel.lsb_field.text), int(panel.rsb_field.text)) == (150, 0)
    panel.operation.pick(SET)
    assert (int(panel.lsb_field.text), int(panel.rsb_field.text)) == (150, 0), "no swap"


def test_tuner_when_side_unticked_then_its_value_is_off_and_kept(world):
    n = glyph2("n", (100, 10, 89))
    from _wp03_metrics_tabs import spacing_panel

    _, panel = spacing_panel(world, "Sidebearings Tuner", [n])
    panel.lsb_field.setText("")
    panel.rsb_field.setText("4")
    assert panel.tune()
    light = n.findLayer("Light")
    assert (light.advanceWidth, light.points) == (104, rect(10, 89)), "LSB kept"
    assert light.edit_log == ["width"], "no shift when LSB is off"
    check_one_undo(world, "Spacing Studio: add sidebearings n", [light], [n])


def test_tuner_when_both_sides_unticked_then_nothing_to_change(world):
    from _wp03_metrics_tabs import spacing_panel, stage_panel

    studio, panel = spacing_panel(world, "Sidebearings Tuner", [glyph2()])
    panel.lsb_field.setText("")
    panel.rsb_field.setText("")
    staged, shell = stage_panel(studio, panel)
    staged.action = panel.tune
    shell.run("preview")
    assert not staged.ready() and not shell.apply_button._enabled
    assert "Type an LSB or RSB value" in studio.status
    shell.run("apply")
    assert world.history == []


def test_copy_when_reference_typed_then_targets_follow_per_master(world):
    n = glyph2("n", (100, 10, 89), (120, 12, 100))
    ref = glyph2("H", (200, 30, 160), (240, 40, 190))
    from _wp03_metrics_tabs import spacing_panel, stage_panel

    studio, panel = spacing_panel(world, "Copy Metrics From Reference", [n, ref])
    staged, shell = stage_panel(studio, panel)
    assert panel.completion_model.strings == ["n", "H"], "completer lists the font"
    assert panel.reference_field.completer is panel.completer
    shell.run("preview")
    assert "Type" in studio.status, studio.status
    assert not shell.apply_button._enabled
    panel.reference_field.setText("Q")
    shell.run("preview")
    assert "Glyph Q is not in the font" in shell.status.text, shell.status.text
    panel.reference_field.setText(" H ")
    panel.all_masters.setChecked(True)
    shell.run("preview")
    assert {row.glyph for row in studio.rows} == {"n"}, "the reference is not edited"
    shell.run("apply")
    light, bold = n.findLayer("Light"), n.findLayer("Bold")
    assert (light.advanceWidth, light.points) == (149, rect(30, 109)), "lsb 30 rsb 40"
    assert (bold.advanceWidth, bold.points) == (178, rect(40, 128)), "lsb 40 rsb 50"
    check_one_undo(world, "Spacing Studio: copy metrics from H to n", [light, bold], [n])
    assert ref.findLayer("Light").edit_log == [], "reference untouched"


def test_copy_when_only_reference_selected_then_selection_refusal(world):
    from _wp03_metrics_tabs import spacing_panel, stage_panel

    studio, panel = spacing_panel(world, "Copy Metrics From Reference", [glyph2(), glyph2("H")], selection=["H"])
    panel.reference_field.setText("H")
    staged, shell = stage_panel(studio, panel)
    shell.run("preview")
    assert "Choose glyphs other than the reference" in studio.status, studio.status
    assert not shell.apply_button._enabled and not staged.ready()
    assert world.history == []


def test_copy_when_glyph_list_cannot_be_read_then_panel_still_opens(world):
    world.names_error = RuntimeError("no font list")
    from _wp03_metrics_tabs import spacing_panel

    _, panel = spacing_panel(world, "Copy Metrics From Reference", [glyph2()])
    assert panel.completion_model.strings == []
    assert panel.widget is not None
    assert panel.reference_field.placeholder.startswith("Glyph list not read (no font list)")
    world.names_error = None
    panel.use_selection()
    assert panel.reference_field.placeholder == "Glyph name, e.g. H or n", "reason cleared"



def test_copy_when_use_selection_pressed_then_completer_names_refresh(world):
    from _wp03_metrics_tabs import spacing_panel

    _, panel = spacing_panel(world, "Copy Metrics From Reference", [glyph2()])
    world.font_names = ["n", "H", "O"]
    panel.use_selection()
    assert panel.completion_model.strings == ["n", "H", "O"]


def test_apply_when_cache_update_fails_then_undo_hint_shown(world):
    n = glyph2("n", (100, 10, 80))
    n.findLayer("Light").cache_ok = False
    from _wp03_metrics_tabs import spacing_panel, stage_panel

    studio, panel = spacing_panel(world, "Equalize Sidebearings", [n])
    staged, shell = stage_panel(studio, panel)
    staged.action = panel.equalize
    shell.run("preview")
    shell.run("apply")
    assert len(world.history) == 1, "the notification still runs"
    assert "Native changes may remain; use Edit > Undo" in shell.status.text, shell.status.text


def test_planners_when_sides_already_match_then_fractional_width_is_kept(world):
    from fontlabapp.studios.spacing_studio import model
    before = model.measure((10, 80), 100.4)
    assert not model.equalize(model.measure((15, 85), 100.4), "average").changed, "no rounding edit"
    assert not model.tune(before, "add", 0, 0).changed, "add0 keeps fractional advance"
    assert not model.copied(before, (10, 20, 50), "both", 0).changed, "same sides keep fractional advance"


def test_copy_when_width_mode_and_offset_then_centred_and_master_gap_listed(world):
    n = glyph2("n", (100, 10, 89), (120, 12, 100))
    ref = Glyph("H", {"Light": Layer(200, rect(30, 160))})
    from _wp03_metrics_tabs import spacing_panel, stage_panel

    studio, panel = spacing_panel(world, "Copy Metrics From Reference", [n, ref], selection=["n"])
    panel.reference_field.setText("H")
    panel.copy_mode.pick(3)
    panel.offset_field.setText("-1")
    panel.all_masters.setChecked(True)
    _, shell = stage_panel(studio, panel)
    shell.run("preview")
    assert [row.note for row in studio.rows] == ["", "no reference layer in this master"]
    assert panel.records[1] == ("n", "Bold", ("12", "20", "120", "no reference layer in this master"))
    shell.run("apply")
    light = n.findLayer("Light")
    assert (light.advanceWidth, light.points) == (199, rect(59, 138)), "99: 49 left"
    assert n.findLayer("Bold").edit_log == [], "no reference in Bold: untouched"
    check_one_undo(world, "Spacing Studio: copy metrics from H to n", [light], [n])


# ---------------------------------------------------------------- Vertical Metrics Diagram
def diagram_panel(world):
    """Run the real DiagramPanel read/paint lifecycle with owned controls for its new Nodes tab."""
    from types import SimpleNamespace as NS
    module = load(DIAGRAM)
    panel = object.__new__(module.DiagramPanel)
    panel.tool = NS(package=world.package, app="Vertical Metrics", selected_names=lambda: ["H"])
    panel.tool.say = lambda text: setattr(panel.tool, "status", text)
    panel.subtitle, panel.notes, panel.status = Label(), Label(), Label()
    panel.grid = NS(set_rows=lambda rows: None)
    panel.select_button = NS(setEnabled=lambda value: None)
    # Nodes Near Zones is separately covered by App tests; these retained oracles cover Diagram.
    panel.rescan = lambda: None
    panel.diagram = module.Diagram(panel)
    panel.reload_view()
    return panel


def diagram_font():
    """H and b in both masters; x only in Light; no p."""
    return [
        glyph2("H", (600, 50, 550), (700, 60, 640)),
        Glyph("x", {"Light": Layer(500, rect(20, 480, 500))}),
        glyph2("b", (550, 40, 510), (600, 50, 560)),
    ]


def test_diagram_file_when_read_then_read_only_house_text():
    import json
    from menu_layout import source_bytes
    path = f"Scripts/Metrics/{DIAGRAM}.py"
    rows = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
    source = next(row["source"] for row in rows if row["source"]["path"] == path)
    text = source_bytes(ROOT, source).decode()
    assert (METRICS / "Vertical Metrics.py").is_file()
    assert text.startswith(f"# this_file: Scripts/Metrics/{DIAGRAM}.py\n")
    assert "# SPDX-License-Identifier: Apache-2.0" in text.splitlines()[1]
    tree = ast.parse(text, feature_version=(3, 11))
    flat = " ".join((ast.get_docstring(tree) or "").split())
    for word in (
        "What it does",
        "How it works",
        "Why",
        "How to use",
        "Benefit",
        "Credit",
    ):
        assert word in flat, f"docstring lacks '{word}'"
    assert "Font Info > Master Metrics Table" in flat, "edits are pointed elsewhere"
    assert "the author's own FontLab sample, Apache-2.0" in flat
    for word in (
        "issue 122",
        "D22",
        "batch",
        "reviewed App",
        "S2",
        "fragment",
        "clone",
    ):
        assert word not in text, f"forbidden text '{word}'"
    for writer in ("notifyChangesApplied", "setMaster", "history", "_value"):
        assert writer not in text, f"read-only diagram uses '{writer}'"
    assert "from fly.ap import" not in text
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None or node.name == "__init__", node.name


def test_frame_when_two_masters_then_exact_units_to_pixels(world):
    module = load(DIAGRAM)
    metrics = [
        {"ascender": 800, "capsHeight": 700, "xHeight": 500, "descender": -200},
        {"ascender": 820, "capsHeight": 700, "xHeight": 520, "descender": -210},
    ]
    frame = module.frame(600, 300, metrics, 2000)
    # top 820+60, bottom -210-40: 1130 units. Height scale 266/1130; width scale
    # column 250 * 0.9 / 2000 = 0.1125 is smaller.
    assert frame.column == 250 and frame.scale == pytest.approx(0.1125)
    assert frame.baseline == pytest.approx(
        22 + (266 - 1130 * 0.1125) / 2 + 880 * 0.1125
    )
    assert frame.x(0, 0) == pytest.approx(84)
    assert frame.x(1, 100) == pytest.approx(84 + 250 + 11.25)
    assert frame.y(0) == pytest.approx(frame.baseline)
    assert frame.y(500) == pytest.approx(frame.baseline - 56.25)
    tall = module.frame(600, 300, metrics, 100)
    assert tall.scale == pytest.approx(266 / 1130), "height limits a narrow sample"
    assert tall.baseline == pytest.approx(22 + 880 * 266 / 1130), "no vertical slack"


def test_line_start_when_sample_narrower_than_column_then_centred(world):
    module = load(DIAGRAM)
    frame = module.Frame(left=84, column=250, scale=0.125, baseline=200)
    assert module.line_start(frame, 1000) == pytest.approx(500), "(2000 - 1000) / 2"
    assert module.line_start(frame, 2400) == pytest.approx(-200), "wider: overhangs"


def test_collect_when_glyph_or_layer_missing_then_notes_not_errors(world):
    module = load(DIAGRAM)
    package = Package(diagram_font())
    samples, widest, notes = module.collect(package, ["Light", "Bold"])
    assert [name for name, _, _ in samples["Light"]] == ["H", "x", "b"]
    assert [name for name, _, _ in samples["Bold"]] == ["H", "b"]
    assert widest == 1650, "Light: 600 + 500 + 550"
    assert notes == ["x: no layer in Bold", "p: not in this font"], "sample order"
    path = samples["Light"][0][1]
    assert path.points == rect(50, 550), (
        "outline read in place through the shape transform"
    )


def test_diagram_panel_when_opened_then_reads_each_master_without_switching(world):
    world.package = Package(diagram_font())
    panel = diagram_panel(world)
    assert world.package.metric_reads == ["Light", "Bold"]
    assert panel.metrics["Bold"]["capsHeight"] == 700
    assert "p: not in this font" in panel.notes.text
    assert "x: no layer in Bold" in panel.notes.text
    assert "Metrics table tab" in panel.subtitle.text
    Painter.made.clear()
    panel.diagram.paintEvent(None)
    (painter,) = Painter.made
    assert painter.ended and panel.diagram.paint_error == ""
    names = [name for name, _ in painter.calls]
    assert names.count("drawPath") == 5, "3 Light + 2 Bold sample outlines"
    assert names.count("drawLine") == 10, "5 lines (baseline + 4 metrics) x 2 masters"


def test_diagram_paint_when_drawing_fails_then_contained_and_painter_ended(world):
    world.package = Package(diagram_font())
    panel = diagram_panel(world)
    panel.metrics = {"Light": {}, "Bold": {}}  # max() of nothing raises ValueError
    Painter.made.clear()
    panel.diagram.paintEvent(None)
    (painter,) = Painter.made
    assert painter.ended, "the painter ends in finally"
    assert panel.diagram.paint_error.startswith("ValueError"), panel.diagram.paint_error


def test_diagram_panel_when_no_font_then_message_and_clean_paint(world):
    panel = diagram_panel(world)
    assert panel.subtitle.text.startswith("Open a font"), panel.subtitle.text
    Painter.made.clear()
    panel.diagram.paintEvent(None)
    (painter,) = Painter.made
    assert painter.ended and panel.diagram.paint_error == ""
    assert [name for name, _ in painter.calls].count("drawPath") == 0


def test_diagram_panel_when_metrics_unreadable_then_error_and_reload_recovers(world):
    world.package = Package(diagram_font())
    world.package.metrics["Bold"] = None
    panel = diagram_panel(world)
    assert panel.tool.status.startswith("Vertical Metrics:"), panel.status.text
    assert panel.metrics == {}
    world.package.metrics["Bold"] = {
        "ascender": 750,
        "capsHeight": 690,
        "xHeight": 480,
        "descender": -190,
    }
    panel.reload_view()
    assert panel.metrics["Bold"]["ascender"] == 750
    assert "2 masters · 3 of 4 sample glyphs" in panel.subtitle.text


def test_diagram_main_when_called_then_one_keyed_panel_and_close_helper(world):
    import runpy
    from fontlabapp.studios.vertical_metrics import app
    calls = []
    world.mp.setattr(app, "show_vertical_metrics", lambda: calls.append("Vertical Metrics"))
    world.mp.setitem(sys.modules, "fly.ap.studios.vertical_metrics.app", app)
    runpy.run_path(str(METRICS / "Vertical Metrics.py"), run_name="__main__")
    assert calls == ["Vertical Metrics"]
    # Actual Refresh/Close: App test_studio_vertical_metrics.py::test_wp03_vertical_profile_diagram_refresh_and_owned_close.


def test_widget_fake_when_native_member_assigned_then_raises():
    with pytest.raises(AttributeError, match="can not be overwritten"):
        QWidgetFake().width = 10
