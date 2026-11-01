# this_file: tests/test_master_angles.py
# SPDX-License-Identifier: Apache-2.0
"""Complete italic-angle controls, source binding, painter boundary and Close."""

import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_masters import MasterWidget, masters  # noqa: F401

ROOT = Path(__file__).parents[1]


@pytest.fixture
def angles(masters, monkeypatch, app_sources):  # noqa: F811
    class Spin(MasterWidget):
        def setRange(self, low, high):
            self.range = (low, high)

        def setDecimals(self, count):
            self.decimals = count

        def setSuffix(self, suffix):
            self.suffix = suffix

    masters.qt.QtGui.QDoubleSpinBox = Spin

    class Scroll(MasterWidget):
        def setWidget(self, child):
            self.child = child

        def setWidgetResizable(self, enabled):
            self.resizable = enabled

    masters.qt.QtGui.QScrollArea = Scroll
    masters.qt.QtGui.QFontMetrics = lambda font: NS(width=lambda text: len(text) * 7)
    monkeypatch.setattr(
        MasterWidget,
        "setMinimumWidth",
        lambda self, value: setattr(self, "minimum_width", value),
        raising=False,
    )
    masters.qt.QtGui.QPen = lambda *a: NS(
        setWidthF=lambda v: None, setCapStyle=lambda v: None
    )
    masters.qt.QtCore.Qt.RoundCap = 3
    masters.qt.QtGui.QPainter.Antialiasing = 1
    for name in ("master_angles", "_master_angles_views", "_master_angles_dialog"):
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        monkeypatch.setattr(sys.modules["fontlabapp"], name, module, raising=False)
        masters.modules[name] = module
    spec = importlib.util.spec_from_file_location(
        "italic_angle_menu", ROOT / "Scripts/Masters/Italic Angle.py"
    )
    masters.menu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(masters.menu)

    class Package:
        id, isNull, master = 7, False, "Regular"

        def __init__(self):
            self.masters = ["Thin", "Regular", "Black"]
            self.info = NS(postscriptBlueScale=0.039625)
            self.values = dict.fromkeys(self.masters, -10.0)
            self.events, self.failure = [], False
            self.container = NS(
                checkInitHistoryState=lambda n: self.events.append("init")
            )

        def setMaster(self, name, notify=False):
            self.master = name

        @property
        def italicAngle_value(self):
            if self.failure:
                raise RuntimeError("owned read failed")
            return self.values[self.master]

        @italicAngle_value.setter
        def italicAngle_value(self, value):
            self.values[self.master] = value
            self.events.append((self.master, value))

        def mastersContainer(self):
            return self.container

        @property
        def hinting(self):
            return NS(blueScale=0.039625)

    def font():
        p = Package()
        masters.state.package = p
        native = masters.modules["scripting"]._native("fontlab")
        native.flItems = NS(
            notifyChangesApplied=lambda title, objects: p.events.append(
                (title, objects)
            )
        )
        native.UpdateAll = lambda: p.events.append("update")
        return p

    masters.font = font
    return masters


def test_no_font_has_complete_controls_diagnosis_and_owned_close(angles, monkeypatch):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    d = angles.menu.main()
    assert not d.spins and not d.gauge.angles and not d.apply_button.enabled
    assert "Open a font" in d.subtitle.text
    d.close_button.clicked.emit()
    assert d.deleted and not d._connections and not sys._fontlab_samples


def test_complete_original_controls_preview_apply_and_noop(angles):
    p = angles.font()
    d = angles.menu.ItalicAngle()
    assert not d.last_error and d._snapshot_valid, d.last_error
    assert d.saved == dict.fromkeys(p.masters, -10)
    assert list(d.spins) == p.masters and p.master == "Regular"
    assert [(s.range, s.decimals, s.suffix) for s in d.spins.values()] == [
        ((-45, 45), 1, "°")
    ] * 3
    assert not d.apply_button.enabled and p.events == []
    d.spins["Thin"].setValue(-12)
    d.spins["Regular"].setValue(-11)
    assert d.gauge.angles == [("Thin", -12), ("Regular", -11), ("Black", -10)]
    assert d.status.text == "2 masters changed" and d.apply_button.enabled
    d.apply_button.clicked.emit()
    assert d.last_result == {"changed": ["Thin", "Regular"], "angles": p.values}
    assert p.master == "Regular" and not d.apply_button.enabled
    before = list(p.events)
    d.apply()
    assert p.events == before and d.last_result["changed"] == []


@pytest.mark.parametrize(
    "drift", ["font", "closed", "master", "order", "value", "read"]
)
def test_stale_control_slot_clears_every_preview_and_refuses_writes(angles, drift):
    p = angles.font()
    d = angles.menu.ItalicAngle()
    spins = list(d.spins.values())
    if drift == "font":
        angles.state.package = NS(id=99, isNull=False)
    elif drift == "closed":
        angles.state.package = None
    elif drift == "master":
        p.master = "Black"
    elif drift == "order":
        p.masters.reverse()
    elif drift == "value":
        p.values["Thin"] = -9
    else:
        p.failure = True
    spins[0].setValue(-12)
    assert d.last_error and d.package is None and not d._snapshot_valid
    assert (
        not d.spins
        and not d.saved
        and not d.gauge.angles
        and not d.apply_button.enabled
    )
    assert all(not s.valueChanged.slots for s in spins)
    assert p.events == []


def test_failed_open_is_closable_and_disconnected(angles):
    p = angles.font()
    p.failure = True
    d = angles.menu.ItalicAngle()
    assert "owned read failed" in d.last_error
    assert not d.spins and d.close_button and d.package is None
    d.close_button.clicked.emit()
    assert d.deleted and not d._connections


def test_real_gauge_draws_both_angle_signs_and_ends_painter(angles):
    angles.font()
    d = angles.menu.ItalicAngle()
    d.spins["Thin"].setValue(-45)
    d.spins["Regular"].setValue(45)
    d.gauge.paintEvent(None)
    assert not d.gauge._paint_error and not d.last_error
    d.close_button.clicked.emit()
    assert not d.gauge.angles and d.gauge.before_draw is None and d.gauge.report is None


def test_gauge_failure_ends_painter_and_invalidates_actions(angles):
    angles.font()
    d = angles.menu.ItalicAngle()
    d.gauge.draw = lambda painter: (_ for _ in ()).throw(
        RuntimeError("owned paint failure")
    )
    d.gauge.paintEvent(None)
    assert "owned paint failure" in d.last_error
    assert not d.gauge.angles and not d.spins and not d.apply_button.enabled


def test_original_helper_interfaces_remain_available(angles):
    p = angles.font()
    assert angles.menu.read_angles(p, p.masters) == p.values
    assert angles.menu.write_angles(p, {"Thin": -12}) == ["Thin"]
    assert angles.menu.Gauge and angles.menu.SampleDialog


def test_native_main_entry_uses_same_owned_registry_and_close(angles, monkeypatch):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    shown = []
    monkeypatch.setattr(
        MasterWidget, "show", lambda self: shown.append(self), raising=False
    )
    runpy.run_path(str(ROOT / "Scripts/Masters/Italic Angle.py"), run_name="__main__")
    d = sys._fontlab_samples["masters_italic_angle"]
    assert shown == [d] and d.close_button and not d.spins
    d.close_button.clicked.emit()
    assert not sys._fontlab_samples and d.deleted


def test_empty_and_upright_gauges_draw_without_division_or_slope_errors(angles):
    gauge = angles.menu.Gauge()
    gauge.paintEvent(None)
    assert not gauge._paint_error
    gauge.angles = [("Upright", 0)]
    gauge.paintEvent(None)
    assert not gauge._paint_error


def test_failed_apply_clears_staged_rows_and_retains_a_closable_panel(
    angles, monkeypatch
):
    p = angles.font()
    d = angles.menu.ItalicAngle()
    d.spins["Thin"].setValue(-12)

    def fail(*args, **kwargs):
        raise RuntimeError("owned writer failure")

    monkeypatch.setattr(angles.modules["master_angles"], "apply", fail)
    d.apply_button.clicked.emit()
    assert "owned writer failure" in d.last_error
    assert not d.spins and not d.gauge.angles and not d.apply_button.enabled
    assert not p.events
    d.close_button.clicked.emit()
    assert d.deleted and not d._connections


def test_invalidating_after_success_clears_the_previous_result(angles):
    p = angles.font()
    d = angles.menu.ItalicAngle()
    d.spins["Thin"].setValue(-12)
    d.apply_button.clicked.emit()
    assert d.last_result["changed"] == ["Thin"]
    p.values["Black"] = -9
    d.spins["Thin"].setValue(-13)
    assert d.last_error and d.last_result is None


def test_empty_gauge_after_failure_preserves_the_original_diagnosis(angles):
    p = angles.font()
    d = angles.menu.ItalicAngle()
    p.failure = True
    d.spins["Thin"].setValue(-12)
    diagnosis = d.last_error
    assert "owned read failed" in diagnosis
    d.gauge.paintEvent(None)
    assert not d.gauge._paint_error and d.last_error == diagnosis


def test_many_master_gauge_keeps_full_labels_accessible_in_scroll_area(angles):
    p = angles.font()
    p.masters = [f"Long master label {index:02d}" for index in range(25)]
    p.master = p.masters[0]
    p.values = dict.fromkeys(p.masters, -10.0)
    d = angles.menu.ItalicAngle()
    assert len(d.spins) == d.table.rowCount == 25 and not d.last_error
    required_slot = len(f"{p.masters[-1]}  -10°") * 7 + 24
    assert d.gauge.minimum_width >= required_slot * 25
    assert d.scroll_area.resizable and d.scroll_area.child is d.gauge
    assert not p.events
