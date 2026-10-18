# this_file: tests/test_live_nodes.py
# SPDX-License-Identifier: Apache-2.0
"""Real panel slots with owned Qt-shaped timers and clipboard, without a host."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_anchors import anchors, components, masters  # noqa: F401
from test_proof import Signal

ROOT = Path(__file__).parents[1]


@pytest.fixture
def nodes(anchors, monkeypatch, app_sources):  # noqa: F811
    class Timer:
        def __init__(self, parent):
            self.timeout, self.active, self.interval = Signal(), False, None

        def setInterval(self, interval):
            self.interval = interval

        def start(self):
            self.active = True

        def stop(self):
            self.active = False

        def isActive(self):
            return self.active

    anchors.qt.QtCore.QTimer = Timer
    spec = importlib.util.spec_from_file_location(
        "fontlabapp.node_coordinates", app_sources / "node_coordinates.py"
    )
    api = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fontlabapp.node_coordinates", api)
    spec.loader.exec_module(api)
    spec = importlib.util.spec_from_file_location(
        "live_nodes", ROOT / "Scripts/Outlines/Node Coordinates Panel.py"
    )
    menu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(menu)
    anchors.api, anchors.menu = api, menu
    previous_font = anchors.font

    def font():
        package, layers = previous_font()
        for master_layers in layers.values():
            for layer in master_layers.values():
                for shape in layer.shapes:
                    for contour in shape.contours:
                        points = contour.nodes()
                        contour.nodes = lambda points=points: points
                        for node in points:
                            node.selected = False
        anchors.state.fallback = NS(name="H")
        return package, layers

    anchors.font = font
    return anchors


def selected(layers, name="H", master="Bold", indices=(0, 1, 3)):
    nodes = layers[name][master].shapes[0].contours[0].nodes()
    for i in indices:
        nodes[i].selected = True
    return nodes


def test_no_font_is_diagnosed_complete_and_owned_close_disconnects_timer(
    nodes, monkeypatch
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = nodes.menu.main()
    assert dialog.status and dialog.close_button and not dialog.apply_button.enabled
    assert dialog.package is None and not dialog.timer.isActive()
    assert "font" in dialog.status.text.lower()
    connections = list(dialog._connections)
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and not sys._fontlab_samples
    assert all(slot not in signal.slots for signal, slot in connections)


def test_timer_tracks_selection_geometry_master_and_falsey_current_glyph(nodes):
    package, layers = nodes.font()
    dialog = nodes.menu.NodePanel()
    assert dialog.timer.isActive() and dialog.timer.interval == 400
    selected(layers)
    dialog.timer.timeout.emit()
    assert (
        len(dialog.rows_data) == 3
        and dialog.nodes.rowCount == 3
        and dialog.pairs.rowCount == 2
    )
    assert dialog.apply_button.enabled
    points = selected(layers)
    points[0].x += 13
    dialog.timer.timeout.emit()
    assert dialog.rows_data[0][2] == points[0].x
    package.master = "Light"
    selected(layers, master="Light", indices=(1,))
    dialog.timer.timeout.emit()
    assert dialog.signature[1] == "Light" and len(dialog.rows_data) == 1

    class Falsey:
        name = "O"

        def __bool__(self):
            return False

    nodes.state.fallback = Falsey()
    selected(layers, "O", "Light", indices=(0, 1))
    dialog.timer.timeout.emit()
    assert dialog.glyph_name == "O" and len(dialog.rows_data) == 2


def test_copy_rechecks_current_nodes_before_owned_clipboard_write(nodes):
    _package, layers = nodes.font()
    selected(layers)
    dialog = nodes.menu.NodePanel()
    dialog.apply_button.clicked.emit()
    assert nodes.state.copied == ["1:0\t0\t0\n1:1\t20\t0\n1:3\t0\t20"]
    assert dialog.last_result == {"copied": 3}
    selected(layers)[0].x += 1
    dialog.apply_button.clicked.emit()
    assert len(nodes.state.copied) == 1 and not dialog.rows_data
    assert "changed" in dialog.last_error.lower() and not dialog.apply_button.enabled
    dialog.timer.timeout.emit()
    assert dialog.rows_data and dialog.apply_button.enabled


@pytest.mark.parametrize("change", ["switched", "closed", "read", "render"])
def test_faults_clear_partial_values_and_bound_font_switch_is_terminal(
    nodes, monkeypatch, change
):
    package, layers = nodes.font()
    selected(layers)
    dialog = nodes.menu.NodePanel()
    if change in {"switched", "closed"}:
        nodes.state.package = NS(id=8, isNull=False) if change == "switched" else None
        package.findName = lambda name: pytest.fail("Dereferenced stale bound package")
    elif change == "read":
        monkeypatch.setattr(
            nodes.menu,
            "selected_nodes",
            lambda layer: (_ for _ in ()).throw(RuntimeError("owned read fault")),
        )
    else:
        selected(layers)[0].x += 1
        monkeypatch.setattr(
            nodes.menu,
            "fill_table",
            lambda *a: (_ for _ in ()).throw(RuntimeError("owned render fault")),
        )
    dialog.timer.timeout.emit()
    assert not dialog.rows_data and dialog.nodes.rowCount == dialog.pairs.rowCount == 0
    assert not dialog.apply_button.enabled and dialog.last_error
    if change in {"switched", "closed"}:
        assert dialog.package is None and not dialog.timer.isActive()
        nodes.state.package = package
        dialog.tick()
        assert not dialog.rows_data
    dialog.close_button.clicked.emit()
    assert (
        dialog.package is None
        and not dialog.timer.isActive()
        and not dialog._connections
    )


def test_no_selection_copy_and_post_close_refresh_never_write_clipboard(nodes):
    nodes.font()
    dialog = nodes.menu.NodePanel()
    dialog.apply()
    assert not nodes.state.copied
    dialog.close()
    dialog.tick()
    dialog.apply()
    assert not nodes.state.copied and dialog.package is None and not dialog.rows_data


def test_opening_binding_failure_keeps_all_controls_and_no_running_timer(
    nodes, monkeypatch
):
    nodes.font()

    def broken(*args):
        raise RuntimeError("owned binding fault")

    monkeypatch.setattr(nodes.menu, "current_package", broken)
    dialog = nodes.menu.NodePanel()
    assert "owned binding fault" in dialog.last_error
    assert (
        dialog.close_button and not dialog.timer.isActive() and dialog.package is None
    )
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


def test_switch_during_table_render_cannot_publish_old_font_rows(nodes, monkeypatch):
    _package, layers = nodes.font()
    selected(layers)
    original = nodes.menu.fill_table

    def switched(*args):
        original(*args)
        nodes.state.package = NS(id=8, isNull=False)

    monkeypatch.setattr(nodes.menu, "fill_table", switched)
    dialog = nodes.menu.NodePanel()
    assert not dialog.rows_data and not dialog._snapshot_valid
    assert not dialog.timer.isActive() and dialog.package is None


def test_clipboard_fault_clears_values_and_next_tick_can_recover(nodes, monkeypatch):
    _package, layers = nodes.font()
    selected(layers)
    dialog = nodes.menu.NodePanel()

    def broken(text):
        raise RuntimeError("owned clipboard fault")

    monkeypatch.setattr(
        nodes.qt.QtGui.QApplication, "clipboard", lambda: NS(setText=broken)
    )
    dialog.apply_button.clicked.emit()
    assert not dialog.rows_data and "owned clipboard fault" in dialog.last_error
    assert not dialog.apply_button.enabled and not nodes.state.copied
    dialog.timer.timeout.emit()
    assert dialog.rows_data and dialog.apply_button.enabled and dialog.last_error == ""


def test_main_replacement_closes_old_panel_and_releases_its_font_and_timer(
    nodes, monkeypatch
):
    nodes.font()
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    old = nodes.menu.main()
    new = nodes.menu.main()
    assert (
        old.deleted
        and old.package is None
        and not old.timer.isActive()
        and not old._connections
    )
    assert new is sys._fontlab_samples[nodes.menu.KEY] and new.timer.isActive()


def test_cached_row_tampering_is_refused_before_copy(nodes):
    _package, layers = nodes.font()
    selected(layers)
    dialog = nodes.menu.NodePanel()
    dialog.rows_data.append((99, 99, 99, 99, True))
    dialog.apply_button.clicked.emit()
    assert (
        not dialog.rows_data
        and not dialog.apply_button.enabled
        and not nodes.state.copied
    )


def test_every_released59_mapping_and_menu_remains_byte_exact():
    rows = json.loads((ROOT / "migration.json").read_text())
    assert len(rows) == 60
    assert (
        hashlib.sha256(
            json.dumps(rows[:59], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == "8d9d4202f2c7ffbfa425072c945d7c7debeb8a84d064d7f3a06c4555f9efeab2"
    )
    for row in rows[:59]:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        ), row["destination"]
