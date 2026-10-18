# this_file: tests/test_readonly_tail.py
# SPDX-License-Identifier: Apache-2.0
"""Complete remaining static read-only panels and immutable released57 menus."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_anchors import AnchorRect, anchors, components, masters  # noqa: F401
from test_proof import Widget

ROOT = Path(__file__).parents[1]
RELEASED57_DIGEST = "96639ca3078fb00fd90919b87e2217679e30d723e86fac361f327af527bc46b9"
TOOLS = [
    ("Cleanup/Select Unreferenced Glyphs", "Dialog"),
    ("Masters/Interpolation Preview", "Interpolation"),
]


@pytest.fixture
def reviews(anchors, monkeypatch, app_sources):  # noqa: F811
    anchors.qt.QtCore.Qt.NoFocus = 0

    class Slider(Widget):
        def setValue(self, value):
            self.value = value
            if not self.blocked:
                self.valueChanged.emit()

    anchors.qt.QtGui.QSlider = Slider

    class Path:
        def __init__(self):
            self.points = []

        def moveTo(self, x, y):
            self.points.append((x, y))

        def lineTo(self, x, y):
            self.points.append((x, y))

        def quadTo(self, *values):
            self.points.extend(zip(values[::2], values[1::2]))

        def cubicTo(self, *values):
            self.points.extend(zip(values[::2], values[1::2]))

        def closeSubpath(self):
            pass

        def boundingRect(self):
            if not self.points:
                return AnchorRect()
            xs, ys = zip(*self.points)
            return AnchorRect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    anchors.qt.QtGui.QPainterPath = Path
    anchors.qt.QtGui.QPen = lambda *args: NS(
        setCosmetic=lambda value: None,
        setStyle=lambda value: None,
        setWidthF=lambda value: None,
        setCapStyle=lambda value: None,
    )
    anchors.qt.QtCore.Qt.DashLine = 1
    anchors.qt.QtCore.Qt.RoundCap = 2
    for name in [
        "unreferenced",
        "interpolation",
        "_review_dialog",
        "_interpolation_view",
    ]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        anchors.modules[name] = module

    class Groups(dict):
        def getAsClassRecords(self):
            return []

    class Features:
        def get_prefix(self):
            return anchors.state.review_feature_text

        def __iter__(self):
            return iter(())

        def keys(self):
            return []

    native = anchors.modules["scripting"]._native("fontlab")
    anchors.state.review_feature_text = ""
    native.CurrentFont = lambda: NS(
        glyphs=anchors.state.glyphs, features=Features(), groups=Groups()
    )
    previous_font = anchors.font

    def font():
        package, layers = previous_font()
        for glyph in anchors.state.glyphs:
            glyph.layers = list(layers[glyph.name].values())
            if glyph.name == "n":
                glyph.unicodes = []
            for master, layer in layers[glyph.name].items():
                layer.name, layer.recipe = master, ""
        return package, layers

    def module(path):
        spec = importlib.util.spec_from_file_location(
            path, ROOT / "Scripts" / (path + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    anchors.font, anchors.module = font, module
    return anchors


@pytest.mark.parametrize("path,klass", TOOLS)
def test_readonly_tail_no_font_panels_have_controls_status_and_close(
    reviews, monkeypatch, path, klass
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    module = reviews.module(path)
    dialog = module.main()
    assert isinstance(dialog, getattr(module, klass))
    assert dialog.close_button and dialog.status and not dialog._snapshot_valid
    connections = list(dialog._connections)
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not sys._fontlab_samples and not dialog._connections
    assert all(slot not in signal.slots for signal, slot in connections)


@pytest.mark.parametrize("path,klass", TOOLS)
def test_readonly_tail_bound_values_and_visible_controls_after_late_binding(
    reviews, path, klass
):
    reviews.font()
    dialog = getattr(reviews.module(path), klass)()
    assert dialog._snapshot_valid, dialog.last_error
    if klass == "Dialog":
        assert dialog.rows == [("n", "")]
        assert dialog.table.rowCount == 1 and dialog.apply_button.enabled
        dialog.apply_button.clicked.emit()
        assert reviews.state.selected == {2}
        assert dialog.last_result == {"selected": 1}
    else:
        assert dialog.glyph_combo.items == ["H", "O", "n"]
        assert dialog.first.items == dialog.second.items == ["Bold", "Light"]
        assert dialog.second.currentText == "Light"
        assert dialog.slider.range == (0, 100) and dialog.slider.value == 50
        assert dialog.percent.text == "50 %"
        assert dialog.mix[0] == [
            (0, 0, True),
            (15, 0, True),
            (15, 15, True),
            (0, 15, True),
        ]
        dialog.slider.setValue(25)
        assert dialog.percent.text == "25 %" and dialog.mix[0][1][0] == 17.5


@pytest.mark.parametrize("path,klass", TOOLS)
@pytest.mark.parametrize("change", ["font", "closed", "master", "membership", "source"])
def test_readonly_tail_actual_slots_refuse_stale_source_before_action_or_blend(
    reviews, path, klass, change
):
    package, layers = reviews.font()
    dialog = getattr(reviews.module(path), klass)()
    assert dialog._snapshot_valid, dialog.last_error
    selected = set(reviews.state.selected)
    if change == "font":
        reviews.state.package = NS(id=8, isNull=False)
        package.findName = lambda name: pytest.fail("Read a stale native glyph handle")
    elif change == "closed":
        reviews.state.package = None
    elif change == "master":
        package.master = "Light"
    elif change == "membership":
        reviews.state.glyphs.reverse()
    elif klass == "Dialog":
        reviews.state.review_feature_text = "n"
    else:
        layers["H"]["Bold"].advanceWidth += 1
    if klass == "Dialog":
        dialog.apply_button.clicked.emit()
    else:
        dialog.slider.setValue(25)
    assert not dialog._snapshot_valid and dialog.package is None
    assert dialog._source is None and not dialog.rows
    assert dialog.last_error and "Error:" in dialog.status.text
    assert reviews.state.selected == selected
    if klass == "Dialog":
        assert not dialog.apply_button.enabled
    else:
        assert (
            not dialog.mix
            and not dialog.view.a
            and not dialog.view.b
            and not dialog.view.mix
        )
        dialog.slider.setValue(50)
        assert not dialog._snapshot_valid and not dialog.mix


@pytest.mark.parametrize("path,klass", TOOLS)
def test_readonly_tail_initial_source_read_failure_leaves_empty_diagnosed_closable_panel(
    reviews, monkeypatch, path, klass
):
    reviews.font()
    data = reviews.modules["unreferenced" if klass == "Dialog" else "components"]

    def broken(*args, **kwargs):
        raise RuntimeError("owned review source read failure")

    monkeypatch.setattr(data, "source_values", broken)
    dialog = getattr(reviews.module(path), klass)()
    assert not dialog._snapshot_valid and dialog.package is None
    assert "owned review source read failure" in dialog.last_error
    assert not dialog.rows and not dialog.mix
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


def test_readonly_tail_full_interpolation_paint_and_fault_release_cached_geometry(
    reviews,
):
    reviews.font()
    dialog = reviews.module("Masters/Interpolation Preview").Interpolation()
    dialog.view.paintEvent(None)
    assert dialog.view.error is None, dialog.view.error
    assert dialog.view._paint_error == ""
    assert sum(name == "drawPath" for name, _ in reviews.painter.calls) == 3
    assert sum(name == "drawPoint" for name, _ in reviews.painter.calls) == 4

    def broken(painter):
        raise RuntimeError("owned interpolation paint failure")

    dialog.view.paint = broken
    dialog.view.paintEvent(None)
    assert "owned interpolation paint failure" in dialog.view._paint_error
    assert not dialog._snapshot_valid and dialog.package is None
    assert (
        not dialog.mix
        and not dialog.view.a
        and not dialog.view.b
        and not dialog.view.mix
    )
    assert reviews.painter.ended


@pytest.mark.parametrize("path,klass", TOOLS)
def test_readonly_tail_cached_result_corruption_cannot_be_silently_replaced(
    reviews, path, klass
):
    reviews.font()
    dialog = getattr(reviews.module(path), klass)()
    if klass == "Dialog":
        dialog.rows.append(("not-a-candidate", ""))
        dialog.apply_button.clicked.emit()
    else:
        dialog.mix[0][1] = (999, 999, True)
        dialog.slider.setValue(25)
    assert not dialog._snapshot_valid and dialog.package is None
    assert not dialog.rows and not dialog.mix
    assert "results changed" in dialog.last_error.lower()


def test_readonly_tail_blocked_slider_change_is_refused_before_cached_paint(reviews):
    reviews.font()
    dialog = reviews.module("Masters/Interpolation Preview").Interpolation()
    dialog.slider.blockSignals(True)
    dialog.slider.setValue(30)
    dialog.view.paintEvent(None)
    assert not dialog._snapshot_valid and dialog.package is None
    assert not dialog.mix and not dialog.view.mix
    assert "options changed without refresh" in dialog.view._paint_error


@pytest.mark.parametrize(
    "path",
    ["Cleanup/Select Unreferenced Glyphs.py", "Masters/Interpolation Preview.py"],
)
def test_readonly_tail_complete_menu_exists(path):
    assert (ROOT / "Scripts" / path).is_file(), f"Missing complete tool: {path}"


def test_readonly_tail_prior57_manifest_and_every_menu_byte_remain_immutable():
    rows = json.loads((ROOT / "migration.json").read_text())
    assert len(rows) == 60, (
        "Retain all 59 released tools and the complete new mapping"
    )
    assert (
        hashlib.sha256(
            json.dumps(rows[:57], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == RELEASED57_DIGEST
    )
    for row in rows[:57]:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        ), row["destination"]
