# this_file: tests/test_masters.py
"""Source-first checks of the four full Masters menus."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TOOLS = [
    ("Overview", "Overview"),
    ("Width Chart", "WidthChart"),
    ("Glyph Weight Chart", "WeightChart"),
    ("Compatibility Check", "Compatibility"),
]


@pytest.mark.parametrize("title,klass", TOOLS)
def test_complete_masters_menu_exists(title, klass):
    assert (ROOT / "Scripts/Masters" / (title + ".py")).is_file(), (
        "Missing complete Masters menu"
    )


import importlib.util
import sys
from types import SimpleNamespace as NS

from test_proof import Box, Color, Signal, Widget
from test_proof import load as proof_load


class MasterWidget(Widget):
    def __init__(self, *args):
        super().__init__(*args)
        self.cells, self.rowCount, self.columnCount, self.children = {}, 0, 0, []
        self.cellDoubleClicked = Signal()
        self.palette = NS(color=lambda *a: MasterColor(), setColor=lambda *a: None)

    def horizontalHeader(self):
        return self

    def verticalHeader(self):
        return self

    def header(self):
        return self

    def setRowCount(self, n):
        self.rowCount = n
        if not n:
            self.cells.clear()

    def setColumnCount(self, n):
        self.columnCount = n

    def setHorizontalHeaderLabels(self, labels):
        self.headers = list(labels)
        self.columnCount = len(labels)

    def setItem(self, row, column, item):
        self.cells[row, column] = item

    def item(self, row, column):
        return self.cells[row, column]

    def clearSpans(self):
        pass

    def clear(self):
        self.children.clear()

    def setItemText(self, i, value):
        self.items[i] = value

    @property
    def rect(self):
        return Box(0, 0, self.width, self.height)


class MasterColor(Color):
    def hsvHue(self):
        return 200

    def hsvSaturation(self):
        return 180

    def value(self):
        return 200

    def setHsv(self, *args):
        pass


class Item:
    def __init__(self, parent):
        self.texts, self.children, self.bold = {}, [], False
        if isinstance(parent, str):
            self.texts[0] = parent
        else:
            parent.children.append(self)

    def setText(self, *args):
        column, text = args if len(args) == 2 else (0, args[0])
        self.texts[column] = text

    def text(self):
        return self.texts.get(0, "")

    def font(self, *args):
        return NS(setBold=lambda value: setattr(self, "bold", value))

    def __getattr__(self, name):
        if name.startswith("set"):
            return lambda *a: None
        raise AttributeError(name)


class Point:
    def __init__(self, x, y):
        self._x, self._y = x, y

    def x(self):
        return self._x

    def y(self):
        return self._y


@pytest.fixture
def masters(monkeypatch, app_sources):
    base = proof_load.__wrapped__(monkeypatch, app_sources)
    qt = base.qt
    for name in [
        "QDialog",
        "QWidget",
        "QVBoxLayout",
        "QHBoxLayout",
        "QGridLayout",
        "QLabel",
        "QPushButton",
        "QComboBox",
        "QTableWidget",
        "QTreeWidget",
    ]:
        setattr(qt.QtGui, name, MasterWidget)
    qt.QtGui.QColor = MasterColor
    qt.QtGui.QTableWidgetItem = qt.QtGui.QTreeWidgetItem = Item
    qt.QtGui.QAbstractItemView = NS(NoEditTriggers=0, NoSelection=0)
    qt.QtGui.QHeaderView = NS(Stretch=0, ResizeToContents=1)
    qt.QtGui.QPalette = NS(
        Text=1, WindowText=2, Base=3, Active=4, Link=5, Inactive=6, ButtonText=7
    )
    qt.QtGui.QFont = lambda value: NS(
        pointSizeF=lambda: 12, setPointSizeF=lambda v: None, setBold=lambda v: None
    )
    qt.QtGui.QPen = lambda *a: NS(setWidthF=lambda v: None)
    qt.QtCore.QPointF = Point
    qt.QtCore.Qt.AlignHCenter = 64
    qt.QtCore.Qt.NoPen = 0
    base.painter.font = lambda: NS(pointSizeF=lambda: 12)
    base.painter.boundingRect = lambda *a: NS(width=lambda: 60)
    base.modules["scripting"]._native("fontlab").UpdateAll = lambda: None
    fl = base.modules["scripting"]._native("FL").fl
    fl.Unselect = base.state.selected.clear
    fl.Select = lambda i: base.state.selected.add(i)
    # Reload existing shared UI bases under the richer native-shaped Qt controls.
    for name in [
        "_names_dialog",
        "_proof_dialog",
        "_proof_views",
        "masters",
        "_masters_dialog",
        "_masters_views",
    ]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        base.modules[name] = module

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Masters" / (title + ".py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    base.module = module

    def font():
        layers = {}
        for name in ["H", "O", "n"]:
            layers[name] = {}
            for master, size in [("Bold", 20), ("Light", 10)]:
                pts = [(0, 0), (size, 0), (size, size), (0, size)]
                contour = NS(
                    nodes=lambda pts=pts: [
                        NS(x=x, y=y, isOn=lambda: True) for x, y in pts
                    ]
                )
                shape = NS(
                    isComponent=False,
                    contours=[contour],
                    transform=NS(isIdentity=lambda: True),
                )
                layers[name][master] = NS(
                    isNull=False,
                    autoLayer=False,
                    advanceWidth=size * 10,
                    shapes=[shape],
                    anchors=[NS(name="top")],
                )
        glyphs = {
            name: NS(name=name, isNull=False, unicodes=[ord(name)], findLayer=rows.get)
            for name, rows in layers.items()
        }
        base.state.glyphs[:] = list(glyphs.values())
        package = NS(
            id=7,
            isNull=False,
            masters=["Bold", "Light"],
            master="Bold",
            axes=[NS(shortName="Weight", tag="wght", name="Weight")],
            findName=glyphs.get,
            location=lambda m: {"Weight": 0 if m == "Light" else 1},
        )
        package.setMaster = lambda name, *a: setattr(package, "master", name)
        package.italicAngle_value = -10
        base.modules["scripting"]._native("fontlab").FontMetrics = lambda p, m: NS(
            ascender=800, capsHeight=700, xHeight=500, descender=-200
        )
        base.state.package = package
        base.state.selected.update({0, 1, 2})
        return package, layers

    base.font = font
    return base


@pytest.mark.parametrize("title,klass", TOOLS)
def test_actual_full_constructor_no_font_close_registry(
    masters, monkeypatch, title, klass
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = masters.module(title)
    dialog = module.main()
    assert isinstance(dialog, getattr(module, klass))
    assert "Open a font" in dialog.subtitle.text
    assert dialog._connections and not dialog._snapshot_valid
    dialog.close_button.clicked.emit()
    assert dialog.deleted and dialog.closed and not dialog._connections
    assert sys._fontlab_samples == {} and dialog.package is None


@pytest.mark.parametrize("title,klass", TOOLS)
def test_complete_bound_data_and_current_master_restoration(masters, title, klass):
    package, layers = masters.font()
    dialog = getattr(masters.module(title), klass)()
    assert not dialog.last_error and dialog._snapshot_valid, dialog.last_error
    assert package.master == "Bold"
    if title == "Overview":
        assert [r[0] for r in dialog.rows] == ["Bold", "Light"]
        assert (
            dialog.table.rowCount == 2 and "(current)" in dialog.table.item(0, 0).text()
        )
        dialog.make_current(1)
        assert package.master == "Light"
    elif title == "Width Chart":
        assert dialog.chart.masters == ["Light", "Bold"]
        assert dialog.data["H"] == [("Light", 100.0), ("Bold", 200.0)]
    elif title == "Glyph Weight Chart":
        assert dialog.areas["O"] == [100.0, 400.0]
        assert dialog.table.headers == ["Glyph", "Light (units²)", "Bold (units²)"]
    else:
        assert dialog.results == dict.fromkeys(["H", "O", "n"], True)
        layers["H"]["Bold"].anchors = []
        dialog.refresh()
        assert dialog.failing == ["H"]
        dialog.apply()
        assert masters.state.selected == {0}
        assert dialog.tree.children[0].texts[5].startswith("✗")


@pytest.mark.parametrize("title,klass", TOOLS)
@pytest.mark.parametrize(
    "stage", ["binding", "identity", "selection", "masters", "master", "scan"]
)
def test_early_failure_occurs_after_status_close_then_recovers(
    masters, monkeypatch, title, klass, stage
):
    package, _ = masters.font()
    mod = masters.module(title)

    def fail(*args):
        panel = [w for w in Widget.instances if isinstance(w, getattr(mod, klass))][-1]
        assert hasattr(panel, "status") and hasattr(panel, "close_button")
        raise RuntimeError("early " + stage)

    class Broken:
        def __getattr__(self, name):
            return fail() if name == stage else getattr(package, name)

    with monkeypatch.context() as broken:
        if stage == "binding":
            broken.setattr(masters.modules["_proof_dialog"], "current_package", fail)
        elif stage == "selection":
            broken.setattr(masters.modules["_masters_dialog"], "selected_names", fail)
        elif stage in ["masters", "master"]:
            masters.state.package = Broken()
        elif stage == "identity":

            class BadId:
                @property
                def id(self):
                    return fail()

                isNull = False

            masters.state.package = BadId()
        else:
            broken.setattr(
                mod,
                {
                    "Overview": "overview",
                    "Width Chart": "widths",
                    "Glyph Weight Chart": "ink_area",
                    "Compatibility Check": "check_glyph",
                }[title],
                fail,
            )
        dialog = getattr(mod, klass)()
        assert "early " + stage in dialog.status.text
        assert not dialog._snapshot_valid and dialog.package is None
    masters.state.package = package
    dialog.refresh()
    assert dialog._snapshot_valid and not dialog.last_error
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


@pytest.mark.parametrize("title,klass", TOOLS)
@pytest.mark.parametrize("closed", [True, False])
def test_refresh_never_adopts_another_font_or_dereferences_closed_handles(
    masters, title, klass, closed
):
    package, _ = masters.font()
    dialog = getattr(masters.module(title), klass)()
    masters.state.package = None if closed else NS(isNull=False, id=9)
    package.findName = lambda name: pytest.fail("Read stale wrapper")
    with pytest.raises(ValueError, match="original font"):
        dialog.refresh()
    assert dialog.package is None and not dialog._snapshot_valid
    dialog.close_button.clicked.emit()
    assert dialog.deleted


@pytest.mark.parametrize("change", ["structure", "master", "masters"])
def test_selection_refuses_stale_displayed_source(masters, change):
    package, layers = masters.font()
    dialog = masters.module("Compatibility Check").Compatibility()
    layers["H"]["Bold"].anchors = []
    dialog.refresh()
    if change == "structure":
        layers["H"]["Bold"].anchors = [NS(name="new")]
    elif change == "master":
        package.master = "Light"
    else:
        package.masters.reverse()
    before = masters.state.selected.copy()
    with pytest.raises(ValueError, match="changed"):
        dialog.apply()
    assert before == masters.state.selected and not dialog._snapshot_valid


@pytest.mark.parametrize(
    "title,klass",
    [("Width Chart", "WidthChart"), ("Glyph Weight Chart", "WeightChart")],
)
@pytest.mark.parametrize(
    "failure", ["none", "draw", "hook", "end", "inactive", "create"]
)
def test_actual_original_chart_draws_lines_bars_and_contains_failures(
    masters, title, klass, failure
):
    masters.font()
    dialog = getattr(masters.module(title), klass)()
    chart = dialog.chart
    masters.qt.QtGui.QPainter.Antialiasing = 1
    if failure in ["draw", "hook"]:
        chart.draw = lambda p: (_ for _ in ()).throw(RuntimeError("draw failed"))
    if failure == "hook":
        chart.report = lambda text: (_ for _ in ()).throw(RuntimeError("hook failed"))
    if failure == "end":
        masters.painter.end = lambda: (_ for _ in ()).throw(RuntimeError("end failed"))
    if failure == "inactive":
        masters.painter.isActive = lambda: False
    if failure == "create":
        masters.qt.QtGui.QPainter = lambda owner: (_ for _ in ()).throw(
            RuntimeError("create failed")
        )
    chart.paintEvent(None)
    if failure == "none":
        assert not chart._paint_error, chart._paint_error
        commands = [name for name, args in masters.painter.calls]
        assert (
            "drawEllipse" if title == "Width Chart" else "drawRoundedRect"
        ) in commands
        assert "drawText" in commands and commands[-1] == "end"
    else:
        assert (
            "not active" if failure == "inactive" else failure
        ) in chart._paint_error
        if failure not in ["create", "end", "inactive"]:
            assert masters.painter.calls[-1][0] == "end"


def test_original_defaults_signal_expressions_and_previous_menus_unchanged(request):
    import ast
    import hashlib
    import json

    now = json.loads((ROOT / "migration.json").read_text())
    old = now[:41]
    assert (
        hashlib.sha256(json.dumps(old, sort_keys=True).encode()).hexdigest()
        == "cf656208d280bd9f1a7e74de6eaf79b497a837d38306e8068351566d93f6f7a4"
    )
    for row in old:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        )
    source_root = request.config.getoption("--original-source-root")
    if source_root is None:
        return
    for title, klass in TOOLS:
        row = next(r for r in now if r["destination"] == f"Scripts/Masters/{title}.py")
        before = ast.parse((source_root / row["source"]).read_text())
        after = ast.parse((ROOT / row["destination"]).read_text())
        constants = lambda tree: {
            n.targets[0].id: ast.literal_eval(n.value)
            for n in tree.body
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and not isinstance(n.value, ast.Attribute)
            and n.targets[0].id
            in {"TITLE", "KEY", "METRICS", "STEPS", "MAX_GLYPHS", "MAX_SERIES"}
        }
        assert constants(before) == constants(after)

        def connections(tree, klass=klass):
            c = next(
                n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == klass
            )
            return [
                ast.dump(n, include_attributes=False)
                for n in ast.walk(c)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "_connect"
            ]

        assert connections(before) == connections(after)


@pytest.mark.parametrize("title,klass", TOOLS)
def test_initial_failure_remains_closable_while_read_still_fails(
    masters, monkeypatch, title, klass
):
    masters.font()
    module = masters.module(title)
    calls = []

    def failed():
        calls.append("read")
        raise RuntimeError("binding unavailable")

    monkeypatch.setattr(masters.modules["_proof_dialog"], "current_package", failed)
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = module.main()
    assert "binding unavailable" in dialog.last_error and not dialog._snapshot_valid
    dialog.close_button.clicked.emit()
    assert calls == ["read"] and dialog.deleted and not dialog._connections
    assert sys._fontlab_samples == {} and dialog.package is None


@pytest.mark.parametrize("title,klass", TOOLS)
def test_failed_known_font_does_not_adopt_current_on_retry(
    masters, monkeypatch, title, klass
):
    _package, _ = masters.font()
    module = masters.module(title)
    with monkeypatch.context() as broken:
        broken.setattr(
            masters.modules["_masters_dialog"],
            "selected_names",
            lambda: (_ for _ in ()).throw(RuntimeError("selection unavailable")),
        )
        dialog = getattr(module, klass)()
    assert dialog._bound_id == 7
    masters.state.package = NS(isNull=False, id=9)
    with pytest.raises(ValueError, match="original font"):
        dialog.refresh()
    assert dialog.package is None and dialog._bound_id == 7


@pytest.mark.parametrize(
    "title,klass,limit",
    [("Width Chart", "WidthChart", 12), ("Glyph Weight Chart", "WeightChart", 10)],
)
def test_original_glyph_limits_and_missing_layer_values(masters, title, klass, limit):
    package, layers = masters.font()
    original = masters.state.glyphs[0]
    masters.state.glyphs[:] = [
        NS(name=f"g{i}", isNull=False, unicodes=[], findLayer=original.findLayer)
        for i in range(limit + 2)
    ]
    package.findName = {g.name: g for g in masters.state.glyphs}.get
    masters.state.selected.update(range(limit + 2))
    layers["H"].pop("Light")
    dialog = getattr(masters.module(title), klass)()
    values = dialog.data if title == "Width Chart" else dialog.areas
    assert len(values) == limit and list(values) == [f"g{i}" for i in range(limit)]
    if title == "Width Chart":
        assert dialog.data["g0"] == [("Light", None), ("Bold", 200.0)]
        assert "first 12 glyphs shown" in dialog.status.text
    else:
        assert dialog.areas["g0"] == [0.0, 400.0]


def test_compatibility_whole_font_auto_and_missing_rows(masters):
    _package, layers = masters.font()
    masters.state.selected = {0}
    layers["O"]["Light"].autoLayer = True
    layers["n"].pop("Light")
    dialog = masters.module("Compatibility Check").Compatibility()
    assert list(dialog.results) == ["H"]
    dialog.source.setCurrentIndex(1)
    assert dialog.results == {"H": True, "O": True, "n": False}
    assert dialog.tree.children[1].children[1].texts[1] == "auto layer · not compared"
    assert "missing layer" in dialog.tree.children[2].texts[5]
    assert dialog.source.items == ["Selected glyphs (1)", "Whole font"]


def test_overview_metadata_changed_and_master_switch_refuse_explicit_action(masters):
    package, _ = masters.font()
    dialog = masters.module("Overview").Overview()
    package.italicAngle_value = -11
    with pytest.raises(ValueError, match="Source changed"):
        dialog.make_current(1)
    assert package.master == "Bold" and not dialog._snapshot_valid


@pytest.mark.parametrize(
    "title,klass",
    [("Width Chart", "WidthChart"), ("Glyph Weight Chart", "WeightChart")],
)
def test_chart_binding_failure_precedes_painter_and_recovery_closes_callbacks(
    masters, title, klass
):
    package, _ = masters.font()
    dialog = getattr(masters.module(title), klass)()
    chart = dialog.chart
    masters.state.package = NS(isNull=False, id=9)
    chart.paintEvent(None)
    assert "original font" in chart._paint_error and not masters.painter.calls
    assert not dialog._snapshot_valid and dialog.package is None
    masters.state.package = package
    dialog.refresh()
    masters.qt.QtGui.QPainter.Antialiasing = 1
    chart.paintEvent(None)
    assert not chart._paint_error
    dialog.close_button.clicked.emit()
    assert chart.before_draw is chart.report is chart.on_error is None
    assert dialog.deleted and not dialog._connections


@pytest.mark.parametrize("change", ["append", "delete", "reorder"])
def test_review_master_change_before_scope_refresh_uses_actual_order(masters, change):
    package, layers = masters.font()
    layers["H"]["Bold"].anchors = []
    dialog = masters.module("Compatibility Check").Compatibility()
    if change == "append":
        package.masters.append("New")
    elif change == "delete":
        package.masters.remove("Light")
    else:
        package.masters.reverse()
    dialog.source.setCurrentIndex(1)
    want = {
        g.name: masters.modules["masters"].check_glyph(g, package.masters)[1]
        for g in masters.state.glyphs
    }
    assert dialog.masters == package.masters, "Refresh retained the old master domain"
    assert dialog.results == want, (
        "Published results disagree with current-domain checks"
    )
    assert dialog._display_masters == tuple(package.masters)
    dialog.apply()
    assert {masters.state.glyphs[i].name for i in masters.state.selected} == {
        name for name, ok in want.items() if not ok
    }


@pytest.mark.parametrize("change", ["insert", "delete", "reorder"])
def test_review_whole_font_membership_change_refuses_until_complete_refresh(
    masters, change
):
    package, layers = masters.font()
    layers["H"]["Bold"].anchors = []
    dialog = masters.module("Compatibility Check").Compatibility()
    dialog.source.setCurrentIndex(1)
    if change == "insert":
        masters.state.glyphs.append(
            NS(
                name="NewGlyph",
                unicodes=[],
                isNull=False,
                findLayer=lambda name: layers["H"]["Bold"] if name == "Bold" else None,
            )
        )
    elif change == "delete":
        masters.state.glyphs.pop()
    else:
        masters.state.glyphs.reverse()
    package.findName = {g.name: g for g in masters.state.glyphs}.get
    selected = masters.state.selected.copy()
    with pytest.raises(ValueError, match="changed"):
        dialog.apply()
    assert masters.state.selected == selected and not dialog._snapshot_valid
    dialog.refresh()
    assert list(dialog.results) == [g.name for g in masters.state.glyphs]
    dialog.apply()
    assert {masters.state.glyphs[i].name for i in masters.state.selected} == set(
        dialog.failing
    )


def test_review_selected_scope_preserves_captured_names_when_whole_domain_grows(
    masters,
):
    package, layers = masters.font()
    masters.state.selected = {0}
    layers["H"]["Bold"].anchors = []
    dialog = masters.module("Compatibility Check").Compatibility()
    masters.state.glyphs.append(
        NS(
            name="NewGlyph",
            unicodes=[],
            isNull=False,
            findLayer=lambda name: layers["H"]["Bold"] if name == "Bold" else None,
        )
    )
    package.findName = {g.name: g for g in masters.state.glyphs}.get
    dialog.apply()
    assert dialog.failing == ["H"] and masters.state.selected == {0}


@pytest.mark.parametrize(
    "title,klass",
    [("Width Chart", "WidthChart"), ("Glyph Weight Chart", "WeightChart")],
)
@pytest.mark.parametrize("fault", ["switched", "closed", "create", "draw", "end"])
def test_review_persistent_paint_fault_drains_queue_then_explicit_refresh_recovers(
    masters, monkeypatch, title, klass, fault
):
    package, _ = masters.font()
    dialog = getattr(masters.module(title), klass)()
    chart, pending, frames = dialog.chart, [True], []
    chart.update = lambda: pending.append(True)
    masters.qt.QtGui.QPainter.Antialiasing = 1
    with monkeypatch.context() as broken:
        if fault == "switched":
            masters.state.package = NS(isNull=False, id=9)
        elif fault == "closed":
            masters.state.package = None
        elif fault == "create":
            broken.setattr(
                masters.qt.QtGui,
                "QPainter",
                lambda owner: (_ for _ in ()).throw(RuntimeError("persistent create")),
            )
        elif fault == "draw":
            broken.setattr(
                chart,
                "draw",
                lambda painter: (_ for _ in ()).throw(RuntimeError("persistent draw")),
            )
        else:
            broken.setattr(
                masters.painter,
                "end",
                lambda: (_ for _ in ()).throw(RuntimeError("persistent end")),
            )
        while pending and len(frames) < 5:
            pending.pop()
            frames.append(True)
            chart.paintEvent(None)
        assert not pending and len(frames) <= 2, (
            "Invalidation keeps scheduling failed paints"
        )
        assert not dialog._snapshot_valid and dialog.package is None
        assert dialog.last_error, "Persistent failure lost its visible diagnosis"
    masters.state.package = package
    dialog.refresh()
    chart.paintEvent(None)
    assert dialog._snapshot_valid and not chart._paint_error
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


@pytest.mark.parametrize(
    "values",
    [
        (494, 713),
        (499, 713),
        (-713, -494),
        (-713, 494),
        (500, 500),
        (1e300, 1e300),
        (1e300, 1.4e300),
    ],
)
def test_fix2_actual_line_commands_keep_every_data_point_inside_axis(masters, values):
    import math

    chart = masters.modules["_masters_views"].LineChart()
    chart.masters = ["Light", "Bold"]
    chart.series = [("O", list(values))]
    masters.qt.QtGui.QPainter.Antialiasing = 1
    chart.paintEvent(None)
    assert not chart._paint_error, chart._paint_error
    points = [args[0] for name, args in masters.painter.calls if name == "drawEllipse"]
    assert len(points) == len(values)
    assert all(
        math.isfinite(p.y()) and 18 <= p.y() <= chart.height - 34 for p in points
    ), "Actual data points fall outside the drawn axis"


@pytest.mark.parametrize(
    "values",
    [
        (499, 713),
        (499, 625),
        (0, 713),
        (0, 0),
        (500, 500),
        (1e300, 1e300),
        (1e300, 1.4e300),
    ],
)
def test_fix2_actual_bar_commands_keep_every_data_bar_inside_axis(masters, values):
    import math

    chart = masters.modules["_masters_views"].BarChart()
    chart.masters = ["Light", "Bold"]
    chart.groups = [("O", list(values))]
    masters.qt.QtGui.QPainter.Antialiasing = 1
    chart.paintEvent(None)
    assert not chart._paint_error, chart._paint_error
    rectangles = [
        args[0] for name, args in masters.painter.calls if name == "drawRoundedRect"
    ][len(chart.masters) :]
    assert len(rectangles) == len(values)
    assert all(
        math.isfinite(r.top()) and 34 <= r.top() <= r.bottom() <= chart.height - 30
        for r in rectangles
    ), "Actual data bars extend above the drawn axis"
