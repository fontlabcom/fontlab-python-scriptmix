# this_file: tests/test_inspectors.py
# SPDX-License-Identifier: Apache-2.0
"""Complete original metrics and outline menu acceptance with native-shaped doubles."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TOOLS = [
    ("Metrics", "Spacing String Preview", "SpacingPreview"),
    ("Metrics", "Width Table", "WidthTable"),
    ("Outlines", "Contour Order View", "ContourOrder"),
    ("Outlines", "Node Statistics", "NodeStatistics"),
]


@pytest.mark.parametrize("category,title,klass", TOOLS)
def test_complete_original_inspector_menu_exists(category, title, klass):
    assert (ROOT / "Scripts" / category / (title + ".py")).is_file(), (
        "Complete inspector missing"
    )


import ast
import hashlib
import importlib.util
import json
import sys
from types import SimpleNamespace as NS

from test_masters import (
    Item,
    MasterWidget,
    masters,  # noqa: F401
)
from test_proof import Box, Signal, Widget


class Check(MasterWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.checked = False
        self.toggled = Signal()

    def isChecked(self):
        return self.checked

    def setChecked(self, value):
        self.checked = value
        self.toggled.emit()


class Combo(MasterWidget):
    clear = Widget.clear


class NumericItem(Item):
    def __init__(self, parent):
        super().__init__(parent)
        self.value = parent

    def setData(self, role, value):
        self.value = value
        self.texts[0] = str(value)

    def data(self, role):
        return self.value


@pytest.fixture
def inspectors(masters, monkeypatch, app_sources):  # noqa: F811 - imported pytest fixture
    masters.qt.QtGui.QComboBox = Combo
    masters.qt.QtCore.Qt.DisplayRole = 0
    masters.qt.QtGui.QCheckBox = Check
    masters.qt.QtGui.QLineEdit = MasterWidget
    masters.qt.QtGui.QAbstractItemView.SelectRows = 1
    masters.qt.QtGui.QTableWidgetItem = NumericItem
    masters.qt.QtGui.QPalette.Mid = 8
    masters.qt.QtCore.Qt.AlignTop = 128
    for name in ["inspectors", "_inspectors_views", "_inspectors_dialog"]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        masters.modules[name] = module

    def module(title):
        category = next(cat for cat, t, _ in TOOLS if t == title)
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts" / category / (title + ".py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    original = masters.font

    def font():
        package, layers = original()
        package.ascender_value, package.descender_value = 800, -200
        package.findUnicode = lambda code: next(
            (g for g in masters.state.glyphs if code in g.unicodes), None
        )
        for rows in layers.values():
            for layer in rows.values():
                layer.boundingBox = NS(x=lambda: 0, width=lambda: 20, height=lambda: 20)
                for shape in layer.shapes:
                    for c in shape.contours:
                        c.nodesCount = len(c.nodes())
                        c.closed = True
        masters.modules["inspectors"].outline = lambda layer: (
            "path",
            layer.advanceWidth,
        )
        return package, layers

    masters.font, masters.module = font, module
    return masters


@pytest.mark.parametrize("category,title,klass", TOOLS)
def test_original_constructor_no_font_and_owned_close(
    inspectors, monkeypatch, category, title, klass
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = inspectors.module(title)
    dialog = module.main()
    assert isinstance(dialog, getattr(module, klass))
    assert "Open a font" in dialog.subtitle.text
    assert hasattr(dialog, "status") and hasattr(dialog, "close_button")
    if klass in ["ContourOrder", "SpacingPreview"]:
        assert dialog.ACTION is None and not hasattr(dialog, "apply_button")
    elif klass == "NodeStatistics":
        assert (
            dialog.ACTION == "Select Flagged"
            and dialog.apply_button.text == "Select Flagged"
        )
    else:
        assert (
            dialog.select_button is dialog.apply_button
            and dialog.select_button.text == "Select flagged"
        )
    assert not dialog._snapshot_valid and not dialog.last_error
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and sys._fontlab_samples == {}


@pytest.mark.parametrize("category,title,klass", TOOLS)
def test_complete_data_uses_font_order_and_current_master(
    inspectors, category, title, klass
):
    package, _layers = inspectors.font()
    dialog = getattr(inspectors.module(title), klass)()
    assert not dialog.last_error, dialog.last_error
    assert dialog._snapshot_valid and dialog.masters == ["Bold", "Light"]
    assert package.master == "Bold"
    if klass == "SpacingPreview":
        dialog.text.setText("HO/H/n")
        assert [row[:3] for row in dialog.rows] == [
            ("H", 0, 200),
            ("O", 200, 200),
            ("H", 400, 200),
            ("n", 600, 200),
        ]
        assert dialog.show_numbers.isChecked() and dialog.show_boxes.isChecked()
        dialog.master.setCurrentIndex(1)
        assert dialog.rows[1][1:3] == (100, 100)
    elif klass == "WidthTable":
        assert dialog.rows == [
            (name, [200, 100], "falling") for name in ["H", "O", "n"]
        ]
        assert dialog.table_values() == {name: [200, 100] for name in ["H", "O", "n"]}
        assert dialog.table.headers == ["Glyph", "Bold", "Light", "Progression"]
        assert not dialog.select_button.enabled
    elif klass == "ContourOrder":
        assert dialog.glyph_combo.items == ["H", "O", "n"]
        assert dialog.info == {m: [(0, (0, 0), "ccw", 4)] for m in ["Bold", "Light"]}
        dialog.glyph_combo.setCurrentIndex(1)
        assert dialog.status.text.startswith("O:")
    else:
        assert dialog.data == {
            name: {m: (1, 4) for m in ["Bold", "Light"]} for name in ["H", "O", "n"]
        }
        assert dialog.table.headers == ["Glyph", "Bold", "Light", "Masters"]
        assert not dialog.apply_button.enabled


@pytest.mark.parametrize("category,title,klass", TOOLS)
@pytest.mark.parametrize(
    "stage", ["binding", "identity", "selection", "masters", "master", "scan"]
)
def test_initial_failures_leave_complete_closable_panel_then_recover(
    inspectors, monkeypatch, category, title, klass, stage
):
    package, _ = inspectors.font()
    module = inspectors.module(title)
    if klass == "SpacingPreview" and stage == "selection":
        pytest.skip("Spacing Preview has no selection read")

    def fail(*args):
        panel = [w for w in Widget.instances if isinstance(w, getattr(module, klass))][
            -1
        ]
        assert hasattr(panel, "status") and hasattr(panel, "close_button")
        raise RuntimeError("initial " + stage)

    class Broken:
        def __getattr__(self, name):
            return fail() if name == stage else getattr(package, name)

    with monkeypatch.context() as broken:
        if stage == "binding":
            broken.setattr(inspectors.modules["_proof_dialog"], "current_package", fail)
        elif stage == "selection":
            broken.setattr(
                inspectors.modules["_masters_dialog"], "selected_names", fail
            )
        elif stage in ["identity", "masters", "master"]:
            if stage == "identity":

                class Bad:
                    isNull = False
                    id = property(lambda self: fail())

                inspectors.state.package = Bad()
            else:
                inspectors.state.package = Broken()
        else:
            broken.setattr(
                module,
                {
                    "SpacingPreview": "layout",
                    "WidthTable": "report",
                    "ContourOrder": "contour_info",
                    "NodeStatistics": "glyph_counts",
                }[klass],
                fail,
            )
        dialog = getattr(module, klass)()
        assert "initial " + stage in dialog.status.text
        assert not dialog._snapshot_valid and dialog.package is None
    inspectors.state.package = package
    dialog.refresh()
    assert dialog._snapshot_valid and not dialog.last_error
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


@pytest.mark.parametrize("category,title,klass", TOOLS)
@pytest.mark.parametrize("closed", [True, False])
def test_refresh_refuses_switched_or_closed_font_before_stale_reads(
    inspectors, category, title, klass, closed
):
    package, _ = inspectors.font()
    dialog = getattr(inspectors.module(title), klass)()
    inspectors.state.package = None if closed else NS(id=9, isNull=False)
    package.findName = lambda name: pytest.fail("stale wrapper access")
    with pytest.raises(ValueError, match="original font"):
        dialog.refresh()
    assert dialog.package is None and not dialog._snapshot_valid
    dialog.close_button.clicked.emit()
    assert dialog.deleted


def test_node_auto_missing_whole_font_filter_and_exact_selection(inspectors):
    _package, layers = inspectors.font()
    inspectors.state.selected = {0}
    layers["H"]["Bold"].shapes[0].contours[0].nodesCount = 7
    layers["O"]["Bold"].autoLayer = True
    layers["n"].pop("Light")
    dialog = inspectors.module("Node Statistics").NodeStatistics()
    assert dialog.flagged == ["H"]
    dialog.apply()
    assert inspectors.state.selected == {0} and dialog.last_result == {
        "selected": ["H"]
    }
    dialog.source.setCurrentIndex(1)
    assert list(dialog.data) == ["H", "O", "n"]
    assert dialog.data["O"]["Bold"] is None and dialog.data["n"] == {"Bold": (1, 4)}
    dialog.only_flagged.setChecked(True)
    assert dialog.table.rowCount == 1 and dialog.table.item(0, 0).text() == "H"


@pytest.mark.parametrize(
    "change",
    ["source", "master", "masters", "whole_order", "whole_delete", "whole_insert"],
)
def test_node_action_refuses_stale_source_and_domain(inspectors, change):
    package, layers = inspectors.font()
    layers["H"]["Bold"].shapes[0].contours[0].nodesCount = 7
    dialog = inspectors.module("Node Statistics").NodeStatistics()
    dialog.source.setCurrentIndex(1)
    if change == "source":
        layers["H"]["Bold"].shapes[0].contours[0].nodesCount = 9
    elif change == "master":
        package.master = "Light"
    elif change == "masters":
        package.masters.reverse()
    elif change == "whole_order":
        inspectors.state.glyphs.reverse()
    elif change == "whole_delete":
        inspectors.state.glyphs.pop()
    else:
        inspectors.state.glyphs.append(NS(name="new", unicodes=[]))
    before = inspectors.state.selected.copy()
    with pytest.raises(ValueError, match="changed"):
        dialog.apply()
    assert (
        inspectors.state.selected == before
        and not dialog._snapshot_valid
        and not dialog.data
    )


def test_width_mixed_zero_missing_numeric_display_and_select_exactly_flagged(
    inspectors,
):
    package, layers = inspectors.font()
    package.masters = ["Bold", "Light", "Other"]
    for name, rows in layers.items():
        rows["Other"] = NS(isNull=False, advanceWidth=300 if name == "H" else 0)
    layers["n"].pop("Light")
    dialog = inspectors.module("Width Table").WidthTable()
    assert dialog.flagged() == ["H"]
    assert dialog.table.item(0, 1).data(0) == 200 and isinstance(
        dialog.table.item(0, 1).data(0), int
    )
    assert dialog.table_values()["n"] == [200, "–", 0]
    dialog.only_flagged.setChecked(True)
    assert dialog.table.rowCount == 1
    dialog.select_flagged()
    assert inspectors.state.selected == {0}
    layers["H"]["Bold"].advanceWidth = 90
    with pytest.raises(ValueError, match="Source changed"):
        dialog.select_flagged()
    assert not dialog.rows and dialog.package is None


# Immutable Scriptmix v1.0.6: all 45 rows serialized with sorted keys and
# separators=(",", ":"). Verify this literal from the tag, never from current rows.
RELEASED_V1_0_6_MANIFEST_SHA256 = (
    "58d98d7622a78373b989e61a21e9c947ee1354a17b69b96c042091840df749e2"
)


def _assert_released45_invariant(rows: list[dict], root: Path) -> None:
    """Verify immutable released provenance and menu bytes without requiring Git."""
    assert len(rows) == 57, "Expected all 57 current migration rows"
    released = rows[:45]
    digest = hashlib.sha256(
        json.dumps(released, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == RELEASED_V1_0_6_MANIFEST_SHA256, (
        "The immutable v1.0.6 manifest rows changed"
    )
    for row in released:
        assert (
            hashlib.sha256((root / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        ), f"Changed released menu bytes: {row['destination']}"


def test_previous45_manifest_rows_and_menu_bytes_stay_exact():
    """Keep all prior release rows and menu bytes exact in checkouts or archives."""
    _assert_released45_invariant(
        json.loads((ROOT / "migration.json").read_text()), ROOT
    )


@pytest.mark.parametrize(
    "title,klass,view_name",
    [
        ("Spacing String Preview", "SpacingPreview", "canvas"),
        ("Contour Order View", "ContourOrder", "view"),
    ],
)
@pytest.mark.parametrize(
    "fault", ["switched", "closed", "create", "draw", "end", "inactive", "hook"]
)
def test_persistent_paint_failure_contains_error_drains_queue_recovers_and_closes(
    inspectors, monkeypatch, title, klass, view_name, fault
):
    package, _ = inspectors.font()
    dialog = getattr(inspectors.module(title), klass)()
    view = getattr(dialog, view_name)
    pending, frames = [True], []
    view.update = lambda: pending.append(True)
    with monkeypatch.context() as broken:
        if fault == "switched":
            inspectors.state.package = NS(id=9, isNull=False)
        elif fault == "closed":
            inspectors.state.package = None
        elif fault == "create":
            broken.setattr(
                inspectors.qt.QtGui,
                "QPainter",
                lambda owner: (_ for _ in ()).throw(RuntimeError("persistent create")),
            )
        elif fault == "inactive":
            inspectors.painter.isActive = lambda: False
        elif fault == "end":
            broken.setattr(
                inspectors.painter,
                "end",
                lambda: (_ for _ in ()).throw(RuntimeError("persistent end")),
            )
        else:
            broken.setattr(
                view,
                "draw",
                lambda painter: (_ for _ in ()).throw(RuntimeError("persistent draw")),
            )
            if fault == "hook":
                broken.setattr(
                    view,
                    "on_error",
                    lambda text: (_ for _ in ()).throw(RuntimeError("persistent hook")),
                )
        while pending and len(frames) < 6:
            pending.pop()
            frames.append(True)
            view.paintEvent(None)
        assert not pending and len(frames) <= 2, "Failed paints replenished their queue"
        assert view.paint_error
        assert dialog.last_error and dialog.status.text
        assert dialog.package is None and not dialog._snapshot_valid
        assert not dialog.paths and not dialog.info and not dialog.rows
    inspectors.painter.isActive = lambda: True
    inspectors.state.package = package
    dialog.refresh()
    # A successful draw still uses the actual paint boundary; the full original
    # draw methods are exercised separately below with geometry-shaped Qt values.
    with monkeypatch.context() as drawing:
        drawing.setattr(view, "draw", lambda painter: None)
        view.paintEvent(None)
    assert not view.paint_error and dialog._snapshot_valid
    if klass == "SpacingPreview":
        assert view.paint_error is None
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections
    assert view.before_draw is view.on_error is None
    assert view.owner is None if klass == "SpacingPreview" else view.report is None


@pytest.mark.parametrize("category,title,klass", TOOLS)
def test_master_domain_changes_during_scan_refuse_partial_results(
    inspectors, monkeypatch, category, title, klass
):
    package, _ = inspectors.font()
    mod = inspectors.module(title)
    helper = {
        "SpacingPreview": "layout",
        "WidthTable": "report",
        "ContourOrder": "contour_info",
        "NodeStatistics": "glyph_counts",
    }[klass]
    original = getattr(mod, helper)

    def changed(*args):
        result = original(*args)
        package.masters = ["Light", "Bold", "New"]
        return result

    with monkeypatch.context() as broken:
        broken.setattr(mod, helper, changed)
        dialog = getattr(mod, klass)()
    assert "Masters changed" in dialog.last_error
    assert not dialog._snapshot_valid and dialog.package is None
    assert not dialog.rows and not dialog.data and not dialog.info and not dialog.paths
    dialog.refresh()
    assert dialog._snapshot_valid and not dialog.last_error


def test_whole_font_membership_change_during_scan_refuses_publication(
    inspectors, monkeypatch
):
    _package, layers = inspectors.font()
    mod = inspectors.module("Node Statistics")
    dialog = mod.NodeStatistics()
    original = mod.glyph_counts

    def changed(*args):
        result = original(*args)
        if len(inspectors.state.glyphs) == 3:
            inspectors.state.glyphs.append(
                NS(name="new", unicodes=[], isNull=False, findLayer=layers["H"].get)
            )
        return result

    monkeypatch.setattr(mod, "glyph_counts", changed)
    dialog.source.setCurrentIndex(1)
    assert "glyph order changed" in dialog.last_error
    assert not dialog._snapshot_valid and not dialog.data and dialog.package is None


class GeometryBox(Box):
    def __init__(self, *values):
        super().__init__(*(values or (0, 0, 0, 0)))

    def x(self):
        return self.values[0]

    def y(self):
        return self.values[1]

    def width(self):
        return self.values[2]

    def height(self):
        return self.values[3]

    def translated(self, x, y):
        return GeometryBox(self.x() + x, self.y() + y, self.width(), self.height())

    def united(self, other):
        if not self.width() and not self.height():
            return other
        l, t = min(self.left(), other.left()), min(self.top(), other.top())
        return GeometryBox(
            l,
            t,
            max(self.right(), other.right()) - l,
            max(self.bottom(), other.bottom()) - t,
        )


class GeometryPath:
    def __init__(self):
        self.points = []

    def moveTo(self, x, y):
        self.points.append((x, y))

    def lineTo(self, x, y):
        self.points.append((x, y))

    def quadTo(self, *pts):
        self.points.extend(zip(pts[::2], pts[1::2]))

    def cubicTo(self, *pts):
        self.points.extend(zip(pts[::2], pts[1::2]))

    def closeSubpath(self):
        pass

    def boundingRect(self):
        xs, ys = zip(*self.points) if self.points else ([0], [0])
        return GeometryBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


class Transform:
    def __init__(self, *v):
        self.v = v or (1, 0, 0, 1, 0, 0)

    def m11(self):
        return self.v[0]

    def m12(self):
        return self.v[1]

    def m21(self):
        return self.v[2]

    def m22(self):
        return self.v[3]

    def dx(self):
        return self.v[4]

    def dy(self):
        return self.v[5]

    def map(self, value):
        from test_masters import Point

        if isinstance(value, GeometryPath):
            return value
        return Point(
            value.x() * self.m11() + self.dx(), value.y() * self.m22() + self.dy()
        )


@pytest.mark.parametrize(
    "title,klass,view_name",
    [
        ("Spacing String Preview", "SpacingPreview", "canvas"),
        ("Contour Order View", "ContourOrder", "view"),
    ],
)
def test_complete_original_painters_draw_geometry_labels_boxes_numbers_and_arrows(
    inspectors, monkeypatch, title, klass, view_name
):
    inspectors.font()
    inspectors.qt.QtCore.QRectF = GeometryBox
    inspectors.qt.QtGui.QPainterPath = GeometryPath
    inspectors.qt.QtGui.QTransform = Transform
    inspectors.qt.QtGui.QPolygonF = list
    inspectors.qt.QtGui.QPainter.Antialiasing = 1
    inspectors.painter.font = lambda: NS(
        pointSizeF=lambda: 12, setPointSizeF=lambda value: None
    )
    dialog = getattr(inspectors.module(title), klass)()
    view = getattr(dialog, view_name)
    if klass == "SpacingPreview":
        dialog.text.setText("HOH")
    view.paintEvent(None)
    assert not view.paint_error, view.paint_error
    calls = inspectors.painter.calls
    commands = [name for name, args in calls]
    assert commands[-1] == "end" and "drawPath" in commands and "drawText" in commands
    if klass == "SpacingPreview":
        assert commands.count("drawRect") == 3
        assert commands.count("drawPath") == 3
        assert commands.count("drawText") == 6
        inspectors.painter.calls = []
        dialog.show_boxes.setChecked(False)
        dialog.show_numbers.setChecked(False)
        view.paintEvent(None)
        assert "drawRect" not in [name for name, args in inspectors.painter.calls]
        assert "drawText" not in [name for name, args in inspectors.painter.calls]
        assert view.paint_error is None
    else:
        assert commands.count("drawPolygon") == 2 and commands.count("drawEllipse") == 2
        assert dialog.view.columns[0][0] == "Bold"
        assert view._paint_error == ""


@pytest.mark.parametrize(
    "title,klass",
    [
        ("Spacing String Preview", "SpacingPreview"),
        ("Contour Order View", "ContourOrder"),
    ],
)
@pytest.mark.parametrize("change", ["value", "master", "domain"])
def test_paint_refuses_stale_drawn_values_and_master_domain(
    inspectors, title, klass, change
):
    package, layers = inspectors.font()
    dialog = getattr(inspectors.module(title), klass)()
    if klass == "SpacingPreview":
        dialog.text.setText("H")
    if change == "master":
        package.master = "Light"
    elif change == "domain":
        package.masters.reverse()
    elif klass == "SpacingPreview":
        layers["H"]["Bold"].advanceWidth += 1
    else:
        layers["H"]["Bold"].shapes[0].contours[0].nodes = lambda: [
            NS(x=1, y=2, isOn=lambda: True)
        ]
    view = dialog.canvas if klass == "SpacingPreview" else dialog.view
    view.paintEvent(None)
    assert view.paint_error and not inspectors.painter.calls
    assert not dialog._snapshot_valid and dialog.package is None


def test_original_constants_helpers_classes_and_signal_interfaces(request):
    root = request.config.getoption("--original-source-root")
    if root is None:
        pytest.skip("Original source audit requires --original-source-root")
    rows = json.loads((ROOT / "migration.json").read_text())
    for category, title, klass in TOOLS:
        row = next(
            r for r in rows if r["destination"] == f"Scripts/{category}/{title}.py"
        )
        before = ast.parse((root / row["source"]).read_text())
        after = ast.parse((ROOT / row["destination"]).read_text())
        constants = lambda t: {
            n.targets[0].id: ast.literal_eval(n.value)
            for n in t.body
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in ["TITLE", "KEY", "DEFAULT_TEXT", "MARGIN"]
        }
        assert constants(before) == constants(after)
        before_names = {
            n.name
            for n in before.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))
        }
        after_names = (
            {
                n.name
                for n in after.body
                if isinstance(n, (ast.FunctionDef, ast.ClassDef))
            }
            | {
                n.targets[0].id
                for n in after.body
                if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
            }
            | {
                a.asname or a.name
                for n in after.body
                if isinstance(n, ast.ImportFrom)
                for a in n.names
            }
        )
        assert before_names <= after_names, before_names - after_names


def test_width_fractional_source_change_refuses_even_when_rounded_cell_stays_equal(
    inspectors,
):
    _package, layers = inspectors.font()
    layers["H"]["Bold"].advanceWidth = 200.1
    dialog = inspectors.module("Width Table").WidthTable()
    layers["H"]["Bold"].advanceWidth = 200.2
    with pytest.raises(ValueError, match="Source changed"):
        dialog.select_flagged()
    assert not dialog._snapshot_valid and dialog.package is None


@pytest.mark.parametrize("change", ["coordinates", "closure"])
def test_spacing_refuses_geometry_source_change_with_unchanged_advances(
    inspectors, change
):
    _package, layers = inspectors.font()
    dialog = inspectors.module("Spacing String Preview").SpacingPreview()
    dialog.text.setText("H")
    contour = layers["H"]["Bold"].shapes[0].contours[0]
    if change == "closure":
        contour.closed = False
    else:
        contour.nodes = lambda: [NS(x=1, y=1, isOn=lambda: True)]
    dialog.canvas.paintEvent(None)
    assert dialog.canvas.paint_error and not inspectors.painter.calls
    assert not dialog._outline_sources and not dialog.paths and dialog.package is None


@pytest.mark.parametrize("category,title,klass", TOOLS)
def test_final_master_domain_check_follows_all_snapshot_reads(
    inspectors, monkeypatch, category, title, klass
):
    package, _ = inspectors.font()
    base = inspectors.modules["_inspectors_dialog"].InspectorsDialog
    original = base.source_values

    def source_values(self, *, cached=False):
        result = original(self, cached=cached)
        if cached:
            package.masters.append("Late")
        return result

    monkeypatch.setattr(base, "source_values", source_values)
    dialog = getattr(inspectors.module(title), klass)()
    assert not dialog._snapshot_valid and dialog.package is None
    assert "Masters changed" in dialog.last_error


@pytest.mark.parametrize("field", ["source_sha256", "destination_sha256"])
def test_released45_fixed_manifest_rejects_changed_provenance(field):
    """A changed prior row cannot redefine the released manifest baseline."""
    rows = json.loads((ROOT / "migration.json").read_text())
    rows[0][field] = "0" * 64
    with pytest.raises(AssertionError, match="v1.0.6 manifest"):
        _assert_released45_invariant(rows, ROOT)


def test_released45_fixed_manifest_rejects_changed_menu_bytes(tmp_path):
    """A correct manifest still rejects a changed released menu payload."""
    rows = json.loads((ROOT / "migration.json").read_text())
    for row in rows[:45]:
        destination = tmp_path / row["destination"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / row["destination"]).read_bytes())
    (tmp_path / rows[0]["destination"]).write_bytes(b"# changed menu\n")
    with pytest.raises(AssertionError, match="released menu bytes"):
        _assert_released45_invariant(rows, tmp_path)
