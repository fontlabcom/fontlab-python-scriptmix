# this_file: tests/test_kerning_editors.py
"""Preserve five complete kerning editors and their owned-host behavior."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TITLES = [
    "Copy Between Masters",
    "Pair Editor",
    "Scale Values",
    "Round Values",
    "Remove Small Pairs",
]


@pytest.mark.parametrize("title", TITLES)
def test_requested_complete_editor_exists(title):
    assert (ROOT / "Scripts/Kerning" / (title + ".py")).is_file(), (
        "Requested kerning editor is missing"
    )


import importlib.util
import sys
from types import SimpleNamespace as NS

from test_kerning import fixture_font
from test_kerning import load as native_load

load = native_load


@pytest.fixture
def editors(load, monkeypatch, app_sources):
    module, state, scripting, _shared, qt = load
    for name in (
        "kerning_edit",
        "kerning_batch",
        "_kerning_edit_dialog",
        "_kerning_value_dialog",
    ):
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, result)
        spec.loader.exec_module(result)
    state.package, _, _ = fixture_font()
    return module, state, scripting, sys.modules["fontlabapp._kerning_edit_dialog"], qt


def panel(editors, title):
    module, state, _, _shared, _ = editors
    cls = getattr(
        module(title),
        {
            "Copy Between Masters": "CopyKerning",
            "Pair Editor": "PairEditor",
            "Scale Values": "ScaleKerning",
            "Round Values": "RoundKerning",
            "Remove Small Pairs": "RemoveSmall",
        }[title],
    )
    dialog = cls.__new__(cls)
    dialog.package = state.package
    dialog.masters = list(state.package.masters)
    dialog._snapshot_valid, dialog._scanned_id = True, state.package.id
    batch = sys.modules["fontlabapp.kerning_batch"]
    dialog._kerning_snapshot = batch.snapshot_kerning(state.package)
    dialog.staged, dialog.errors = {}, {}
    dialog.messages, dialog.enabled, dialog.table_sizes = [], [], []
    dialog.status = NS(setText=dialog.messages.append)
    dialog.apply_button = NS(setEnabled=dialog.enabled.append)
    dialog.table = NS(setRowCount=dialog.table_sizes.append)
    return dialog, cls


@pytest.mark.parametrize("title", TITLES)
def test_editors_share_guarded_callbacks_close_and_original_keys(editors, title):
    module, _, _, shared, _ = editors
    _dialog, cls = panel(editors, title)
    assert cls._connect is shared.KerningEditDialog._connect
    assert cls.closeEvent is shared.KerningEditDialog.closeEvent
    assert module(title).KEY.startswith("kerning_")


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("change", ["font", "closed", "pairs", "classes", "masters"])
def test_each_real_apply_refuses_stale_before_body_and_clears_staged(
    editors, title, change
):
    dialog, cls = panel(editors, title)
    _, state, _, _, _ = editors
    dialog.staged[(("A", "V"), "Bold")] = -120
    if change == "font":
        state.package = NS(id=8, isNull=False)
    elif change == "closed":
        state.package = None
    elif change == "masters":
        dialog.package.masters.reverse()
    elif change == "pairs":
        dialog.package.kerning("Bold").items = list
    else:
        dialog.package.kerning("Bold").groups["L_A"] = (["T"], "KernLeft")
    with pytest.raises(ValueError, match="stale|current"):
        cls.apply(dialog)
    assert (
        not dialog.staged
        and not dialog._snapshot_valid
        and dialog._kerning_snapshot is None
    )
    assert dialog.enabled[-1] is False and dialog.table_sizes[-1] == 0


def test_failed_preview_disables_apply_and_leaves_explicit_refresh(editors):
    dialog, _ = panel(editors, "Pair Editor")
    shared = editors[3]

    @shared.editor_refresh
    def fail(self):
        self.staged["partial"] = 1
        raise RuntimeError("native read failed")

    fail(dialog)
    assert dialog.staged == {} and dialog.enabled[-1] is False
    assert (
        "native read failed" in dialog.messages[-1] and "Refresh" in dialog.messages[-1]
    )


def test_refresh_control_calls_the_owned_reload_callback(editors):
    shared, qt = editors[3:]
    calls = []
    qt.QtGui.QPushButton = lambda text: NS(text=text, clicked="clicked")
    dialog = NS(
        status=NS(setWordWrap=lambda value: calls.append(("wrap", value))),
        _connect=lambda signal, slot: calls.append(("slot", slot)),
    )
    footer = NS(
        insertWidget=lambda index, button: calls.append(("button", index, button.text))
    )
    shared.KerningEditDialog.add_refresh(dialog, footer, lambda: calls.append("reload"))
    assert calls[:2] == [("wrap", True), ("button", 1, "Refresh")]
    calls[2][1]()
    assert calls[-1] == "reload"


def test_pair_invalid_cell_keeps_three_other_valid_edits_and_feedback(editors):
    dialog, cls = panel(editors, "Pair Editor")
    dialog.filling = False
    dialog.order = [("A", "V"), ("T", "V")]
    dialog.rows = {
        ("A", "V"): {"Regular": 0, "Bold": 0},
        ("T", "V"): {"Regular": 12.5, "Bold": 12.5},
    }
    dialog.refresh = lambda: None

    def item(row, column, text):
        return NS(row=lambda: row, column=lambda: column, text=lambda: text)

    cls.cell_edited(dialog, item(0, 2, "-120"))
    cls.cell_edited(dialog, item(0, 1, ""))
    cls.cell_edited(dialog, item(1, 1, "-5"))
    cls.cell_edited(dialog, item(1, 2, "abc"))
    assert len(dialog.staged) == 3 and dialog.staged[(("A", "V"), "Regular")] is None
    assert (("T", "V"), "Bold") not in dialog.staged and "abc" in dialog.messages[-1]
    assert (
        dialog.messages[-1]
        == "“abc” is not a valid kerning value; other valid edits remain staged"
    ), "Invalid input must use plain-language feedback"
    cls.cell_edited(dialog, item(0, 2, "inf"))
    assert len(dialog.staged) == 2, (
        "Invalid replacement removes only its own prior staged value"
    )


def test_pair_wrong_side_class_cell_never_enters_staged_map(editors):
    dialog, cls = panel(editors, "Pair Editor")
    dialog.filling = False
    dialog.order = [("@R_V", "V")]
    dialog.rows = {}
    dialog.refresh = lambda: None
    cls.cell_edited(dialog, NS(row=lambda: 0, column=lambda: 1, text=lambda: "-50"))
    assert not dialog.staged and "wrong-side" in dialog.messages[-1]


def test_pair_rebuild_retains_staged_and_invalid_text(editors):
    dialog, cls = panel(editors, "Pair Editor")
    qt = editors[4]
    qt.QtCore.Qt.AlignRight, qt.QtCore.Qt.AlignVCenter = 1, 2
    qt.QtGui.QTableWidgetItem = lambda value: NS(
        text=lambda: value, setTextAlignment=lambda value: None
    )
    values = {}
    dialog.table = NS(
        setRowCount=lambda n: None,
        setItem=lambda row, column, item: values.__setitem__(
            (row, column), item.text()
        ),
    )
    dialog.rows = {("A", "V"): {"Regular": -10, "Bold": -20}}
    dialog.order = [("A", "V")]
    dialog.staged = {(("A", "V"), "Bold"): -120}
    dialog.errors = {(("A", "V"), "Regular"): "abc"}
    dialog.refresh = lambda: None
    cls.fill(dialog)
    assert values[0, 1] == "abc" and values[0, 2] == "-120"


def test_copy_remove_and_scale_round_expose_real_shared_plans(editors):
    module, state, _, _, _ = editors
    assert module("Copy Between Masters").plan({("A", "V"): 0}, {}, "missing", 100) == {
        ("A", "V"): 0
    }
    assert module("Scale Values").scaled(-3, 150) == -5
    assert module("Round Values").round_to(7.5, 5) == 10
    assert module("Remove Small Pairs").small_pairs(state.package, ["Regular"], 1) == {
        "Regular": [("A", "V", 0)]
    }


def test_applied_but_failed_refresh_never_reports_success_counts(editors):
    shared = editors[3]
    dialog = NS(
        _snapshot_valid=True, _batch_written=True, slot_error="native read failed"
    )

    def fail_refresh():
        dialog._snapshot_valid = False

    with pytest.raises(RuntimeError, match="Kerning was applied.*preview failed"):
        shared.KerningEditDialog.refresh_after_apply(dialog, fail_refresh)


def test_captured_snapshot_survives_unchanged_successful_refresh(editors):
    dialog, _ = panel(editors, "Pair Editor")
    shared = editors[3]

    @shared.editor_refresh
    def refresh(self):
        self.staged = {}

    refresh(dialog)
    assert dialog._snapshot_valid and dialog._kerning_snapshot.package_id == 7


def test_pair_apply_refuses_lossy_reopen_range_and_clears_staging(editors):
    _module, state, scripting, _, _ = editors
    font = state.package
    kern = font.kerning("Bold")
    original_items = kern.items()
    kern.items = lambda: [(pair, int(value)) for pair, value in original_items]
    font.upm = 1000
    font.mastersContainer = lambda: "masters"
    font.kerningContainer = lambda: "kerning"
    font.checkInitHistoryState = lambda _: pytest.fail(
        "Invalid final range initialized history"
    )
    scripting._native("fontlab").flItems = NS(
        notifyChangesApplied=lambda *args: pytest.fail(
            "Invalid final range created native history"
        )
    )
    dialog, cls = panel(editors, "Pair Editor")
    dialog.staged[(("A", "V"), "Bold")] = 2001
    before = {master: scripting.kerning_pairs(font, master) for master in font.masters}
    with pytest.raises(ValueError, match="save/reopen range"):
        cls.apply(dialog)
    assert (
        not dialog.staged and not dialog._snapshot_valid and dialog.enabled[-1] is False
    )
    assert {
        master: scripting.kerning_pairs(font, master) for master in font.masters
    } == before
