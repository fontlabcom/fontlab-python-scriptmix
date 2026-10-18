# this_file: tests/test_anchor_copy.py
# SPDX-License-Identifier: Apache-2.0
"""The complete anchor-copy panel on owned Qt-shaped controls."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_components import components  # noqa: F401
from test_guides import guides  # noqa: F401
from test_masters import masters  # noqa: F401

ROOT = Path(__file__).parents[1]


def test_all67_released_rows_and_menus_remain_byte_exact():
    import hashlib
    import json

    rows = json.loads((ROOT / "migration.json").read_text())
    assert len(rows) == 68
    digest = hashlib.sha256(
        json.dumps(rows[:67], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert digest == "fd69198872e2ac99337e7c8a1794ceb41f6cba973b63e97181cb23f5393eda2a"
    for row in rows[:67]:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        )


@pytest.fixture
def copying(guides, monkeypatch, app_sources):  # noqa: F811
    base = guides

    class Form(base.qt.QtGui.QGridLayout):
        def addRow(self, *values):
            self.addWidget(values[-1])

    base.qt.QtGui.QFormLayout = Form

    class Model:
        def __init__(self, parent):
            self.names = []

        def setStringList(self, names):
            self.names = list(names)

        def rowCount(self):
            return len(self.names)

    class Completer:
        def __init__(self, parent):
            pass

        def setModel(self, model):
            self._model = model

        def model(self):
            return self._model

        def setCaseSensitivity(self, value):
            self.case = value

        def setFilterMode(self, value):
            self.filter = value

    base.qt.QtGui.QStringListModel = Model
    base.qt.QtGui.QCompleter = Completer
    base.qt.QtCore.Qt.CaseInsensitive = 0
    base.qt.QtCore.Qt.MatchContains = 1
    base.qt.QtGui.QLineEdit.setCompleter = lambda self, value: setattr(
        self, "completer", value
    )
    for name in ["anchors", "anchor_copy", "_anchor_copy_dialog"]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        base.modules[name] = module

    def menu():
        spec = importlib.util.spec_from_file_location(
            "copy_anchor_menu", ROOT / "Scripts/Anchors/Copy Anchors From Glyph.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    base.menu = menu
    oldfont = base.font

    def font():
        package, layers = oldfont()
        for row in layers.values():
            for layer in row.values():
                for pin in layer.anchors:
                    pin.point = NS(x=lambda: 17.0, y=lambda: 688.0)
                    pin.appearance, pin.anchor = 5, True
                    pin.expressionX = pin.expressionY = ""
        return package, layers

    base.font = font
    return base


def test_no_font_keeps_copy_disabled_close_connected_and_completer_empty(
    copying, monkeypatch
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    d = copying.menu().main()
    assert not d._snapshot_valid and not d.apply_button.enabled
    assert d.close_button.enabled and d.completer.model().rowCount() == 0
    d.close_button.clicked.emit()
    assert d.deleted and not d._connections and not sys._fontlab_samples


def test_full_controls_and_fontwide_completer_preserve_original_defaults(copying):
    copying.font()
    d = copying.menu().CopyAnchors()
    assert d._snapshot_valid and not d.last_error, d.last_error
    assert d.names == ["H", "O", "n"] and d._selected_names == d.names
    assert d.completer.model().rowCount() == 3
    assert d.source.text == "" and not d.apply_button.enabled
    assert d.mode.items == [
        "Add and move (keep other anchors)",
        "Replace (remove anchors the source lacks)",
    ]
    assert d.scale.isChecked() and d.scope.items == [
        "Current master (Bold)",
        "All masters (2)",
    ]
    d.source.setText("unknown")
    assert not d.apply_button.enabled and "No glyph" in d.status.text


def test_source_width_change_invalidates_preview_and_clears_owned_completion(copying):
    _, layers = copying.font()
    d = copying.menu().CopyAnchors()
    d.source.setText("n")
    layers["n"]["Bold"].advanceWidth += 1
    with pytest.raises(ValueError, match="Source changed"):
        d.apply()
    assert not d._snapshot_valid and d.table.rowCount == 0
    assert d.completer.model().rowCount() == 0 and not d.apply_button.enabled


@pytest.mark.parametrize(
    "field,value",
    [
        ("appearance", 9),
        ("anchor", False),
        ("expressionX", "17"),
        ("expressionY", "19"),
        ("name", "changed"),
    ],
)
def test_changed_raw_source_pin_refuses_copy_and_releases_all_cached_data(
    copying, field, value
):
    _, layers = copying.font()
    d = copying.menu().CopyAnchors()
    d.source.setText("n")
    setattr(layers["n"]["Bold"].anchors[0], field, value)
    with pytest.raises(ValueError, match="Source changed"):
        d.apply()
    assert d.package is None and not d.glyphs and d.last_result is None
    assert not d._source_names and d.completer.model().rowCount() == 0


@pytest.mark.parametrize("option", ["source", "mode", "scale", "scope"])
def test_silent_option_change_refuses_the_copy_before_any_native_write(copying, option):
    copying.font()
    d = copying.menu().CopyAnchors()
    d.source.setText("n")
    control = getattr(d, option)
    blocked = control.blockSignals(True)
    try:
        if option == "source":
            control.setText("H")
        elif option == "scale":
            control.checked = False  # owned Check double emits despite blockSignals
        else:
            control.setCurrentIndex(1)
    finally:
        control.blockSignals(blocked)
    with pytest.raises(ValueError, match="Options changed"):
        d.apply()
    assert (
        not copying.state.history and d.package is None and not d.apply_button.enabled
    )


def test_origin_move_stays_visible_in_preview_but_refuses_copy(copying):
    _, layers = copying.font()
    for rows in layers.values():
        for layer in rows.values():
            layer.anchors[0].point = NS(x=lambda: 17.0, y=lambda: 0.0)
    layers["H"]["Bold"].advanceWidth = 0
    d = copying.menu().CopyAnchors()
    d.source.setText("n")
    assert d.table.rowCount and d.pending_origins
    assert not d.apply_button.enabled and "Redo" in d.status.text
