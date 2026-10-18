# this_file: tests/test_master_switcher.py
# SPDX-License-Identifier: Apache-2.0
"""Real compact-panel construction and slots with owned Qt-shaped controls."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_masters import MasterWidget, masters  # noqa: F401

ROOT = Path(__file__).parents[1]


@pytest.fixture
def switcher(masters, monkeypatch, app_sources):  # noqa: F811
    class Button(MasterWidget):
        def __init__(self, *args):
            super().__init__(*args)
            self.checked, self.bold, self.shortcut = False, False, None
            self.font.setBold = lambda value: setattr(self, "bold", value)

        def setChecked(self, value):
            self.checked = value

        def setShortcut(self, value):
            self.shortcut = value

    class Group(MasterWidget):
        def addButton(self, button):
            self.children.append(button)

        def setExclusive(self, value):
            self.exclusive = value

    class Grid(MasterWidget):
        def addWidget(self, button, row, column):
            self.children.append((button, row, column))

    masters.qt.QtGui.QToolButton = Button
    masters.qt.QtGui.QButtonGroup = Group
    masters.qt.QtGui.QGridLayout = Grid
    masters.qt.QtGui.QKeySequence = lambda text: text
    masters.qt.QtGui.QSizePolicy = NS(Expanding=1, Fixed=2)
    masters.qt.QtCore.Qt.ToolButtonTextOnly = 0
    for name in ["master_switcher", "_switcher_dialog"]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        masters.modules[name] = module
    spec = importlib.util.spec_from_file_location(
        "switcher_menu", ROOT / "Scripts/Masters/Master Switcher.py"
    )
    menu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(menu)
    masters.menu = menu
    previous_font = masters.font

    def font():
        p, _layers = previous_font()
        p.masters, p.master = ["Bold", "Regular", "Light"], "Regular"
        p.axes = [NS(shortName="wght")]
        p.location = lambda master: {
            "wght": {"Bold": 900, "Regular": 400, "Light": 100}[master]
        }
        masters.calls = []

        def choose(name, notify):
            masters.calls.append((name, notify))
            p.master = name

        p.setMaster = choose
        return p

    masters.font = font
    return masters


def test_no_font_has_complete_diagnosis_and_owned_close(switcher, monkeypatch):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = switcher.menu.main()
    assert not dialog.buttons and dialog.close_button and dialog.status
    assert not dialog._snapshot_valid and "font" in dialog.subtitle.text.lower()
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and not sys._fontlab_samples


def test_original_buttons_locations_checks_bold_shortcuts_and_actual_slots(switcher):
    p = switcher.font()
    dialog = switcher.menu.Switcher()
    assert list(dialog.buttons) == ["Light", "Regular", "Bold"]
    assert [b.text for b in dialog.buttons.values()] == [
        "Light\n100",
        "Regular\n400",
        "Bold\n900",
    ]
    assert [b.shortcut for b in dialog.buttons.values()] == [
        "Ctrl+1",
        "Ctrl+2",
        "Ctrl+3",
    ]
    assert dialog.group.exclusive
    assert [name for name, b in dialog.buttons.items() if b.checked and b.bold] == [
        "Regular"
    ]
    dialog.buttons["Bold"].clicked.emit()
    assert p.master == "Bold" and switcher.calls == [("Bold", True)]
    assert dialog.buttons["Bold"].checked and dialog.buttons["Bold"].bold
    assert not dialog.buttons["Regular"].checked and not dialog.buttons["Regular"].bold
    dialog.buttons["Light"].clicked.emit()
    assert p.master == "Light" and "Light" in dialog.status.text


@pytest.mark.parametrize(
    "change", ["font", "closed", "masters", "location", "label", "order"]
)
def test_stale_source_or_button_data_is_refused_before_native_switch(switcher, change):
    p = switcher.font()
    dialog = switcher.menu.Switcher()
    if change == "font":
        switcher.state.package = NS(id=8, isNull=False)
    elif change == "closed":
        switcher.state.package = None
    elif change == "masters":
        p.masters.append("Other")
    elif change == "location":
        p.location = lambda master: {"wght": 0}
    elif change == "label":
        dialog.buttons["Bold"].setText("Light")
    else:
        dialog.buttons = dict(reversed(list(dialog.buttons.items())))
    dialog.buttons["Bold"].clicked.emit()
    assert not switcher.calls and not dialog._snapshot_valid and dialog.package is None
    assert all(not b.enabled for b in dialog.buttons.values())
    assert dialog.last_error and "Error:" in dialog.status.text


def test_external_current_master_change_keeps_explicit_destination_action_valid(
    switcher,
):
    p = switcher.font()
    dialog = switcher.menu.Switcher()
    p.master = "Light"
    dialog.buttons["Bold"].clicked.emit()
    assert (
        p.master == "Bold"
        and dialog._snapshot_valid
        and switcher.calls == [("Bold", True)]
    )


def test_unknown_master_is_rejected_without_default_fallback(switcher):
    switcher.font()
    dialog = switcher.menu.Switcher()
    with pytest.raises(ValueError, match="master"):
        dialog.choose("missing")
    assert not switcher.calls


def test_many_masters_wrap_in_three_columns_and_only_first_nine_have_shortcuts(
    switcher,
):
    p = switcher.font()
    p.masters = [f"M{i}" for i in range(12)]
    p.master = "M0"
    p.axes = []
    p.location = lambda master: {}
    dialog = switcher.menu.Switcher()
    assert list(dialog.buttons) == p.masters
    assert [(r, c) for b, r, c in dialog.button_grid.children] == [
        (i // 3, i % 3) for i in range(12)
    ]
    assert [b.shortcut for b in dialog.buttons.values()] == [
        f"Ctrl+{i}" for i in range(1, 10)
    ] + [None, None, None]
    assert [b.text for b in dialog.buttons.values()] == p.masters
    dialog.buttons["M11"].clicked.emit()
    assert p.master == "M11" and switcher.calls == [("M11", True)]


def test_opening_native_read_fault_keeps_diagnosed_closable_panel(
    switcher, monkeypatch
):
    switcher.font()

    def broken(*args):
        raise RuntimeError("owned switcher read fault")

    monkeypatch.setattr(switcher.modules["master_switcher"], "button_values", broken)
    dialog = switcher.menu.Switcher()
    assert (
        not dialog._snapshot_valid and "owned switcher read fault" in dialog.last_error
    )
    assert dialog.close_button and all(not b.enabled for b in dialog.buttons.values())
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections


def test_all_released60_rows_and_menu_bytes_remain_immutable():
    rows = json.loads((ROOT / "migration.json").read_text())
    assert len(rows) == 61
    assert (
        hashlib.sha256(
            json.dumps(rows[:60], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == "5802a1d55ccce6eebb1531794bd0aaa8f935e943314912be1ba1a8dbc23832df"
    )
    for row in rows[:60]:
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        ), row["destination"]
