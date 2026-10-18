# this_file: tests/test_guides.py
# SPDX-License-Identifier: Apache-2.0
"""Actual guide-panel construction and controls with owned Qt-shaped widgets."""

import importlib.util
import math
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_components import components  # noqa: F401
from test_masters import masters  # noqa: F401

ROOT = Path(__file__).parents[1]


@pytest.fixture
def guides(components, monkeypatch, app_sources):  # noqa: F811
    base = components

    class Combo(base.qt.QtGui.QComboBox):
        def addItems(self, values):
            for value in values:
                self.addItem(value)

    base.qt.QtGui.QComboBox = Combo
    for name in [
        "_masters_dialog",
        "_guides_sources",
        "guides",
        "_guides_dialog",
        "_guides_views",
    ]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        base.modules[name] = module

    def menu(title):
        spec = importlib.util.spec_from_file_location(
            "guide_menu", ROOT / "Scripts/Guides" / (title + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    base.module = menu
    base.modules["guides"].layer_path = lambda layer: NS(outline="owned H/O/n path")
    base.qt.QtCore.QLineF = lambda *values: values
    native = base.modules["scripting"]._native("fontlab")

    def guide(line, flags, style):
        x, y, x2, y2 = line
        return NS(
            centerPoint=NS(x=lambda: x, y=lambda: y),
            angle=math.atan2(y2 - y, x2 - x),
            name="",
            isHint=False,
        )

    native.flGuideLine = guide
    base.qt.QtCore.QDateTime = NS(currentDateTimeUtc=lambda: "UTC stamp")
    base.state.history = []
    native.flItems = lambda: NS(
        notifyChangesApplied=lambda title, objects: base.state.history.append(
            (title, objects)
        )
    )
    oldfont = base.font

    def font():
        package, layers = oldfont()
        package.guidelines = []
        for g in base.state.glyphs:
            g.checkInitHistoryState = lambda index: None
            g.lastModified = "before"
            g.layers = list(layers[g.name].values())
            for layer in g.layers:
                layer.checkInitHistoryState = lambda index: None
                layer.guidelines = []
                layer.appendGuidelines = layer.guidelines.extend
        return package, layers

    base.font = font
    return base


def test_font_guides_no_font_still_has_diagnosis_close_and_registry_cleanup(
    guides, monkeypatch
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = guides.module("Font Guides Panel").main()
    assert not dialog._snapshot_valid and "font" in dialog.font_guides.text.lower()
    assert not dialog.apply_button.enabled and dialog.close_button.enabled
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and not sys._fontlab_samples


def test_font_guides_complete_scope_name_position_and_plan_controls(guides):
    guides.font()
    dialog = guides.module("Font Guides Panel").FontGuidesPanel()
    assert dialog._snapshot_valid and [g.name for g in dialog.glyphs] == ["H", "O", "n"]
    assert dialog.position.range == (-5000, 5000)
    assert dialog.direction.items == ["Horizontal", "Vertical"]
    assert dialog.scope.items == ["Current master (Bold)", "All masters (2)"]
    assert not dialog.apply_button.enabled
    dialog.guide_name.setText("Owned guide")
    dialog.position.setValue(432)
    assert dialog.apply_button.enabled and dialog.record() == (
        0.0,
        432.0,
        0.0,
        "Owned guide",
    )
    assert dialog.table.rowCount == 3
    dialog.scope.setCurrentIndex(1)
    assert dialog.table.rowCount == 6
    dialog.direction.setCurrentIndex(1)
    assert dialog.record() == (432.0, 0.0, 90.0, "Owned guide")
    assert all(row[-1] == "add" for row in dialog.plan())


def test_font_guides_stale_selection_refuses_before_any_writer(guides, monkeypatch):
    guides.font()
    dialog = guides.module("Font Guides Panel").FontGuidesPanel()
    dialog.guide_name.setText("Owned guide")
    calls = []
    monkeypatch.setattr(
        guides.modules["guides"], "add_guides", lambda *a: calls.append(a)
    )
    guides.state.selected.clear()
    dialog.apply_button.clicked.emit()
    assert not calls and not dialog._snapshot_valid and dialog.package is None
    assert not dialog.glyphs and not dialog.apply_button.enabled and dialog.last_error
    assert dialog.font_guides.text == ""


@pytest.mark.parametrize("title", ["Grid Generator", "Metric Reference Lines"])
def test_other_complete_guide_panels_construct_without_font_and_close(
    guides, monkeypatch, title
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = guides.module(title).main()
    assert not dialog._snapshot_valid and "font" in dialog.subtitle.text.lower()
    assert not dialog.apply_button.enabled and dialog.close_button.enabled
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and not sys._fontlab_samples


@pytest.mark.parametrize(
    "title,klass,count",
    [
        ("Font Guides Panel", "FontGuidesPanel", 6),
        ("Grid Generator", "GridGenerator", 36),
        ("Metric Reference Lines", "MetricLines", 6),
    ],
)
def test_complete_guide_controls_apply_real_backend_and_second_apply_is_exact_noop(
    guides, title, klass, count
):
    _package, layers = guides.font()
    menu = guides.module(title)
    dialog = getattr(menu, klass)()
    assert dialog._snapshot_valid, dialog.last_error
    assert dialog.scope.items == ["Current master (Bold)", "All masters (2)"]
    if klass == "FontGuidesPanel":
        dialog.guide_name.setText("Owned guide")
        dialog.position.setValue(432)
    elif klass == "GridGenerator":
        assert dialog.direction.items == [
            "Horizontal and vertical",
            "Horizontal",
            "Vertical",
        ]
        assert (dialog.origin.range, dialog.step.range, dialog.count.range) == (
            (-5000, 5000),
            (1, 5000),
            (1, 100),
        )
        dialog.count.setValue(3)
        dialog.step.setValue(80)
        dialog.origin.setValue(11)
        assert dialog.preview.path.outline == "owned H/O/n path"
    else:
        assert list(dialog.metric_checks) == [
            "Baseline",
            "x-height",
            "Cap height",
            "Ascender",
            "Descender",
        ]
        assert dialog.offset.range == (-2000, 2000)
        for label, check in dialog.metric_checks.items():
            check.setChecked(label == "Baseline")
        dialog.offset.setValue(17)
    dialog.scope.setCurrentIndex(1)
    assert dialog.apply_button.enabled and dialog.table.rowCount == 6
    dialog.apply_button.clicked.emit()
    assert dialog.last_result == {"layers": 6, "guides": count}, dialog.last_error
    assert len(guides.state.history) == 1 and all(
        title == menu.TITLE for title, objects in guides.state.history
    )
    assert not dialog.apply_button.enabled
    snapshot = [
        [tuple(guides.modules["guides"].guide_record(g)) for g in layer.guidelines]
        for rows in layers.values()
        for layer in rows.values()
    ]
    dialog.apply()
    assert (
        dialog.last_result == {"layers": 0, "guides": 0}
        and len(guides.state.history) == 1
    )
    assert snapshot == [
        [tuple(guides.modules["guides"].guide_record(g)) for g in layer.guidelines]
        for rows in layers.values()
        for layer in rows.values()
    ]


def test_all_prior61_rows_and_menu_bytes_remain_immutable():
    import hashlib
    import json

    rows = json.loads((ROOT / "migration.json").read_text())
    assert len(rows) == 67
    assert (
        hashlib.sha256(
            json.dumps(rows[:61], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == "3b93696d8a5fd0d74e0e4afa9b6de930aa7032b21d702a794c31ae99911b1a66"
    )
    for row in rows[:61]:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        ), row["destination"]


def test_grid_failed_error_hook_still_clears_native_paths_and_releases_painter(guides,monkeypatch):
    guides.font()
    dialog=guides.module('Grid Generator').GridGenerator()
    ended=[]
    painter=NS(isActive=lambda:False,end=lambda:ended.append(True) or True)
    monkeypatch.setattr(guides.modules['_proof_views'].QtGui,'QPainter',lambda owner:painter)
    def failed_hook(text):raise RuntimeError('owned error hook fault')
    dialog.preview.on_error=failed_hook
    dialog.preview.paintEvent(None)
    assert ended==[True]
    assert not dialog._snapshot_valid and dialog.preview.path is None and not dialog.preview.records
    assert 'owned error hook fault' in dialog.preview.paint_error
    assert 'owned error hook fault' in dialog.status.text
