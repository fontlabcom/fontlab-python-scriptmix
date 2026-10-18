# this_file: tests/test_anchors.py
# SPDX-License-Identifier: Apache-2.0
"""Complete three anchor panels, native-shaped state and immutable prior54."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_components import (  # noqa: F401
    ComponentItem,
    ComponentWidget,
    Rect,
    components,
)
from test_inspectors import Combo
from test_masters import masters  # noqa: F401
from test_proof import Signal

ROOT = Path(__file__).parents[1]
TOOLS = [
    ("Cloud View", "AnchorCloud"),
    ("Compatibility Report", "AnchorCompatibility"),
    ("Mark Attachment Preview", "MarkPreview"),
]
RELEASED54_DIGEST = "930fa7266be5d8e3a830355caf3e7296e3002dc3cec5267a824406e5c3acf07e"


class AnchorCombo(Combo):
    def addItems(self, values):
        for value in values:
            self.addItem(value)

    def findText(self, value):
        return self.items.index(value) if value in self.items else -1


class AnchorTree(ComponentWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.itemDoubleClicked = Signal()

    def topLevelItem(self, index):
        return self.children[index]


class AnchorItem(ComponentItem):
    def setData(self, column, role, value):
        self.value = value

    def data(self, column, role):
        return self.value

    def childCount(self):
        return len(self.children)

    def child(self, index):
        return self.children[index]


class AnchorRect(Rect):
    def __init__(self, *values):
        super().__init__(*(values or (0, 0, 0, 0)))


@pytest.mark.parametrize("title,klass", TOOLS)
def test_complete_anchor_menu_exists(title, klass):
    assert (ROOT / "Scripts/Anchors" / (title + ".py")).is_file(), title


def test_immutable_prior54_manifest_and_menu_hashes():
    rows = json.loads((ROOT / "migration.json").read_text())
    assert len(rows) == 67
    assert (
        hashlib.sha256(
            json.dumps(rows[:54], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == RELEASED54_DIGEST
    )
    for row in rows[:54]:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        ), row["destination"]


def test_compatibility_columns_show_every_bound_master_after_late_binding(anchors):
    """Do not hide comparisons when controls precede native font capture."""
    anchors.font()
    dialog = anchors.module("Compatibility Report").AnchorCompatibility()
    assert dialog._snapshot_valid, dialog.last_error
    assert dialog.tree.columnCount == len(dialog.masters) + 2, (
        "Each bound master needs its own visible comparison column"
    )
    assert dialog.tree.headers == ["Glyph / anchor", *dialog.masters, ""]
    dialog.only_bad.setChecked(True)
    dialog.rescan()
    assert dialog.tree.columnCount == 4
    assert dialog.tree.headers == ["Glyph / anchor", "Bold", "Light", ""]


@pytest.fixture
def anchors(components, monkeypatch, app_sources):  # noqa: F811 - imported pytest fixture
    qt = components.qt
    qt.QtGui.QGridLayout = ComponentWidget
    qt.QtGui.QComboBox = AnchorCombo
    qt.QtGui.QTreeWidget = AnchorTree
    qt.QtGui.QTreeWidgetItem = AnchorItem
    qt.QtCore.Qt.UserRole = 256
    qt.QtCore.Qt.AlignHCenter = 4
    qt.QtCore.Qt.AlignTop = 32
    qt.QtCore.QLineF = lambda *args: args
    qt.QtCore.QRectF = AnchorRect
    qt.QtGui.QTransform = lambda *args: NS(map=lambda value: value)
    qt.QtGui.QFontMetrics = lambda font: NS(
        width=lambda text: len(text) * 6, height=lambda: 12
    )
    for name in ["anchors", "_anchors_views", "_anchors_dialog"]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        components.modules[name] = module
    previous_font = components.font

    def font():
        package, layers = previous_font()
        for master in package.masters:
            for name, points in [
                ("H", [("top", 100, 700)]),
                ("O", [("_top", 20, 30)]),
                (
                    "n",
                    [("top", 200, 600)]
                    + ([("bottom", 0, 0)] if master == "Light" else []),
                ),
            ]:
                layers[name][master].anchors = [
                    NS(name=name, point=NS(x=lambda x=x: x, y=lambda y=y: y))
                    for name, x, y in points
                ]
        return package, layers

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Anchors" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    components.font, components.module = font, module
    return components


@pytest.mark.parametrize("title,klass", TOOLS)
def test_anchor_no_font_panel_is_complete_visible_and_close_releases_signals(
    anchors, monkeypatch, title, klass
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = anchors.module(title)
    dialog = module.main()
    assert isinstance(dialog, getattr(module, klass))
    assert hasattr(dialog, "status") and hasattr(dialog, "close_button")
    assert dialog.last_error is None and not dialog._snapshot_valid
    connections = list(dialog._connections)
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and not sys._fontlab_samples
    assert all(slot not in signal.slots for signal, slot in connections)


@pytest.mark.parametrize("title,klass", TOOLS)
def test_anchor_complete_original_values_choices_and_paint(anchors, title, klass):
    _package, layers = anchors.font()
    module = anchors.module(title)
    dialog = getattr(module, klass)()
    assert dialog.last_error is None, dialog.last_error
    assert dialog._snapshot_valid and dialog.masters == ["Bold", "Light"]
    if klass == "AnchorCloud":
        dialog.choose("top")
        assert dialog.points == {
            "Bold": [("H", 100, 700), ("n", 200, 600)],
            "Light": [("H", 100, 700), ("n", 200, 600)],
        }
        assert len(dialog.view.panels) == 2
        dialog.choose("_top")
        assert dialog.points["Bold"] == [("O", 20, 30)]
    elif klass == "AnchorCompatibility":
        assert dialog.mismatches() == ["n"]
        assert len(dialog.rows) == 3
        dialog.only_bad.setChecked(True)
        dialog.open_item(dialog.tree.topLevelItem(0))
        assert anchors.state.selected == {2}
        layers["H"]["Light"].anchors.append(
            NS(name="probe", point=NS(x=lambda: 10, y=lambda: 20))
        )
        dialog.rescan()
        assert dialog.mismatches() == ["H", "n"]
    else:
        dialog.choose(base="H", mark="O", family="top")
        assert dialog.offsets == {"Bold": (80, 670), "Light": (80, 670)}
        assert len(dialog.view.panels) == 2
        dialog.choose(base="n")
        assert dialog.offsets == {"Bold": (180, 570), "Light": (180, 570)}
    if hasattr(dialog, "view"):
        dialog.view.paintEvent(None)
        assert dialog.view.error is None
        assert anchors.painter.ended


@pytest.mark.parametrize("title,klass", TOOLS)
@pytest.mark.parametrize(
    "change", ["font", "closed", "master", "master_order", "membership", "anchor"]
)
def test_anchor_actual_slots_refuse_stale_source_and_release_all_caches(
    anchors, title, klass, change
):
    package, layers = anchors.font()
    dialog = getattr(anchors.module(title), klass)()
    assert dialog._snapshot_valid, dialog.last_error
    if change == "font":
        anchors.state.package = NS(id=999, isNull=False)
    elif change == "closed":
        anchors.state.package = None
    elif change == "master":
        package.master = "Light"
    elif change == "master_order":
        package.masters.reverse()
    elif change == "membership":
        anchors.state.glyphs.reverse()
    else:
        layers["H"]["Bold"].anchors[0].point.x = lambda: 100.01
    selected = set(anchors.state.selected)
    if klass == "AnchorCloud":
        dialog.name.setCurrentIndex(1)
    elif klass == "AnchorCompatibility":
        dialog.select_button.clicked.emit()
    else:
        dialog.base.setCurrentIndex(1)
    assert dialog.last_error and "Error:" in dialog.status.text
    assert not dialog._snapshot_valid and dialog.package is None
    assert (
        not dialog.points
        and not dialog.offsets
        and not dialog.rows
        and not dialog.glyphs
    )
    assert not dialog._draw_names and dialog._result_options is None
    if hasattr(dialog, "view"):
        assert not dialog.view.panels
    assert anchors.state.selected == selected
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


@pytest.mark.parametrize("title,klass", TOOLS)
@pytest.mark.parametrize(
    "stage", ["binding", "identity", "masters", "master", "names", "selection", "scan"]
)
def test_anchor_initial_faults_keep_complete_diagnosed_close(
    anchors, monkeypatch, title, klass, stage
):
    package, _layers = anchors.font()

    def fail(*args, **kwargs):
        raise RuntimeError("injected anchor read")

    api = anchors.modules["anchors"]
    if stage == "binding":
        monkeypatch.setattr(anchors.modules["_proof_dialog"], "current_package", fail)
    elif stage in {"identity", "masters", "master"}:
        field = "id" if stage == "identity" else stage

        class Fault:
            def __getattr__(self, name):
                return fail() if name == field else getattr(package, name)

        anchors.state.package = Fault()
    elif stage == "names":
        monkeypatch.setattr(anchors.modules["components"], "font_glyph_names", fail)
    elif stage == "selection":
        name = (
            "selected_glyphs"
            if klass == "AnchorCloud"
            else "exact_selected_names"
            if klass == "AnchorCompatibility"
            else "selected_names"
        )
        monkeypatch.setattr(api, name, fail)
    else:
        name = (
            "anchor_names"
            if klass == "AnchorCloud"
            else "anchor_sets"
            if klass == "AnchorCompatibility"
            else "classify"
        )
        monkeypatch.setattr(api, name, fail)
    dialog = getattr(anchors.module(title), klass)()
    assert dialog.last_error and "injected anchor read" in dialog.status.text
    assert not dialog._snapshot_valid and dialog.package is None
    assert (
        not dialog.rows
        and not dialog.points
        and not dialog.offsets
        and not dialog.glyphs
    )
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


@pytest.mark.parametrize("title,klass", [TOOLS[0], TOOLS[2]])
@pytest.mark.parametrize("mode", ["inactive", "end_false", "end_raises", "hook_raises"])
def test_anchor_painter_terminal_failure_is_contained_and_empty_updates_settle(
    anchors, monkeypatch, title, klass, mode
):
    anchors.font()
    dialog = getattr(anchors.module(title), klass)()
    view, painter = dialog.view, anchors.painter
    updates = []
    view.update = lambda: updates.append(1)
    if mode == "inactive":
        monkeypatch.setattr(painter, "isActive", lambda: False)
    else:
        original_end = painter.end

        def end():
            original_end()
            if mode in {"end_raises", "hook_raises"}:
                raise RuntimeError("terminal end failed")
            return False

        monkeypatch.setattr(painter, "end", end)
        if mode == "hook_raises":

            def hook(text):
                raise RuntimeError("diagnostic hook failed")

            view.on_error = hook
    view.paintEvent(None)
    assert view.error is not None and painter.ended
    assert not view.panels and not dialog._snapshot_valid and dialog.package is None
    assert dialog.last_error and "Error:" in dialog.status.text
    for _ in range(5):
        view.paintEvent(None)
    assert len(updates) == 1, "Empty failed paints must not replenish the event queue"
    dialog.close_button.clicked.emit()
    assert view.before_draw is view.on_error is view.failure_cleanup is None


def test_anchor_falsey_current_fallback_and_exact_empty_compatibility_scope(anchors):
    anchors.font()
    anchors.state.selected.clear()

    class Current:
        name = "H"

        def __bool__(self):
            return False

    anchors.state.fallback = Current()
    cloud = anchors.module("Cloud View").AnchorCloud()
    assert cloud.selection == ["H"] and cloud.points["Bold"] == [("H", 100, 700)]
    preview = anchors.module("Mark Attachment Preview").MarkPreview()
    assert preview.base.currentText == "H"
    compatibility = anchors.module("Compatibility Report").AnchorCompatibility()
    compatibility.scope.setCurrentIndex(1)
    assert compatibility.selection == [] and compatibility.rows == []


@pytest.mark.parametrize("title,klass", [TOOLS[0], TOOLS[2]])
def test_anchor_paint_refuses_blocked_selector_changes_and_geometry_drift(
    anchors, title, klass
):
    _package, layers = anchors.font()
    dialog = getattr(anchors.module(title), klass)()
    combo = dialog.name if klass == "AnchorCloud" else dialog.base
    combo.blockSignals(True)
    combo.setCurrentIndex(1)
    combo.blockSignals(False)
    dialog.view.paintEvent(None)
    assert "options changed" in dialog.view.error and not dialog.view.panels
    other = getattr(anchors.module(title), klass)()
    layers["H"]["Bold"].advanceWidth += 0.01
    other.view.paintEvent(None)
    assert other.view.error is not None and not other.view.panels


@pytest.mark.parametrize("title,klass", [TOOLS[0], TOOLS[2]])
def test_anchor_selector_cannot_adopt_changed_source_after_stale_failure(
    anchors, title, klass
):
    _package, layers = anchors.font()
    dialog = getattr(anchors.module(title), klass)()
    layers["H"]["Bold"].anchors[0].point.x = lambda: 101
    combo = dialog.name if klass == "AnchorCloud" else dialog.base
    combo.setCurrentIndex(1)
    assert not dialog._snapshot_valid
    combo.setCurrentIndex(0)
    assert not dialog._snapshot_valid and dialog.package is None, (
        "Selector retries must keep refusing stale source until the script is reopened"
    )
    fresh = getattr(anchors.module(title), klass)()
    assert fresh._snapshot_valid and fresh.last_error is None


def test_compatibility_explicit_rescan_retains_its_original_selected_scope(anchors):
    _package, layers = anchors.font()
    dialog = anchors.module("Compatibility Report").AnchorCompatibility()
    dialog.scope.setCurrentIndex(1)
    captured = list(dialog.selection)
    layers["H"]["Bold"].anchors[0].point.x = lambda: 100.01
    dialog.select_button.clicked.emit()
    assert not dialog._snapshot_valid
    anchors.state.selected = {1}
    dialog.rescan()
    assert dialog._snapshot_valid and dialog.selection == captured
    assert len(dialog.rows) == 3, "Explicit rescan retains original selected scope"
