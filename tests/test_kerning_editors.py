# this_file: tests/test_kerning_editors.py
"""Preserve five complete kerning editors and their owned-host behavior."""

from conftest import app_module_name, app_source_path, register_app_module
import importlib.util
import sys
from types import SimpleNamespace as NS
from test_kerning import fixture_font
from test_kerning import load as native_load
from pathlib import Path
import json

import test_cov_b_kerning_values as migrated_values
import test_cov_b_kerning_editors as migrated_editors
import _wp03_pair_editor as pair_support

import importlib.util
import sys
from types import SimpleNamespace as NS
from test_kerning import fixture_font
from test_kerning import load as native_load
import pytest
from menu_layout import source_bytes

pair_env = pair_support.pair_env

value_env = migrated_values.env
studio_host = migrated_values.studio_host
VALUE_PANELS = {"Round Values": "RoundPanel", "Scale Values": "ScalePanel", "Remove Small Pairs": "RemoveSmallPanel"}


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
    path = "Scripts/Kerning/" + title + ".py"
    row = next(row for row in json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
               if row["source"]["path"] == path)
    assert source_bytes(ROOT, row["source"])
    target = row["destination"]["path"] if row["acceptance"]["behavior_parity"] else path
    assert (ROOT / target).is_file(), "Requested kerning editor is missing"


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
            app_module_name(name), app_source_path(app_sources, name)
        )
        result = importlib.util.module_from_spec(spec)
        register_app_module(monkeypatch, name, result)
        spec.loader.exec_module(result)
    state.package, _, _ = fixture_font()
    return module, state, scripting, sys.modules["fontlabapp.kerning.edit.ui"], qt


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
    batch = sys.modules["fontlabapp.kerning.batch"]
    dialog._kerning_snapshot = batch.snapshot_kerning(state.package)
    dialog.staged, dialog.errors = {}, {}
    dialog.messages, dialog.enabled, dialog.table_sizes = [], [], []
    dialog.status = NS(setText=dialog.messages.append)
    dialog.apply_button = NS(setEnabled=dialog.enabled.append)
    dialog.table = NS(setRowCount=dialog.table_sizes.append)
    return dialog, cls


@pytest.mark.parametrize("title", TITLES)
def test_editors_share_guarded_callbacks_close_and_original_keys(request, title):
    if title in VALUE_PANELS:
        env = request.getfixturevalue("value_env")
        migrated_values.test_editors_when_close_clicked_then_owned_callbacks_are_released(env, VALUE_PANELS[title])
        return
    if title == "Pair Editor":
        pair_support.close_owner(request.getfixturevalue("pair_env"))
        return
    if title == "Copy Between Masters":
        state = request.getfixturevalue("studio_host")
        state.package = migrated_editors.make_package()
        shell = state.open().shell
        shell.close_button.click()
        assert shell.closed and shell._close_complete and shell._delete_scheduled
        assert not shell.widget.isVisible() and not shell.connections
        return
    editors = request.getfixturevalue("editors")
    module, _, _, shared, _ = editors
    _dialog, cls = panel(editors, title)
    assert cls._connect is shared.KerningEditDialog._connect
    assert cls.closeEvent is shared.KerningEditDialog.closeEvent
    assert module(title).KEY.startswith("kerning_")


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("change", ["font", "closed", "pairs", "classes", "masters"])
def test_each_real_apply_refuses_stale_before_body_and_clears_staged(
    request, title, change
):
    if title in VALUE_PANELS:
        env = request.getfixturevalue("value_env")
        migrated_values.test_each_real_apply_refuses_stale_before_body_and_clears_staged(env, VALUE_PANELS[title], change)
        return
    if title == "Pair Editor":
        pair_support.snapshot_refusal(request.getfixturevalue("pair_env"), change)
        return
    if title == "Copy Between Masters":
        migrated_editors.test_copy_apply_refuses_complete_stale_snapshot(request.getfixturevalue("studio_host"), change)
        return
    editors = request.getfixturevalue("editors")
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


def test_failed_preview_disables_apply_and_leaves_explicit_refresh(pair_env, monkeypatch):
    from fontlabapp.studios.kerning_studio import pairs
    dialog = pair_env.open()
    def fail(*args):
        dialog.staged["partial"] = 1
        raise RuntimeError("native read failed")
    monkeypatch.setattr(pairs.model, "involving", fail)
    pair_env.shell.refresh_button.click()
    assert dialog.staged == {} and not dialog.ready()
    assert "native read failed" in pair_env.shell.status.text() and "Refresh" in pair_env.shell.status.text()


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


def test_pair_invalid_cell_keeps_three_other_valid_edits_and_feedback(pair_env):
    pair_env.selection[:] = ["V"]
    for master in pair_env.state.package.masters:
        kern = pair_env.state.package.kerning(master)
        kern.stored[(("A", "glyphMode"), ("V", "glyphMode"))] = 0
        kern.stored[(("T", "glyphMode"), ("V", "glyphMode"))] = 12.5
    dialog = pair_env.open()
    dialog.set_cell("A", "V", "Bold", "-120")
    dialog.set_cell("A", "V", "Regular", "")
    dialog.set_cell("T", "V", "Regular", "-5")
    dialog.set_cell("T", "V", "Bold", "abc")
    assert len(dialog.staged) == 3 and dialog.staged[(("A", "V"), "Regular")] is None
    assert (("T", "V"), "Bold") not in dialog.staged
    assert pair_env.shell.status.text() == "“abc” is not a valid kerning value; other valid edits remain staged"
    dialog.set_cell("A", "V", "Bold", "inf")
    assert len(dialog.staged) == 2, "Invalid replacement removes only its own prior staged value"


def test_pair_wrong_side_class_cell_never_enters_staged_map(pair_env):
    dialog = pair_env.open()
    dialog.rows[("@R_V", "V")] = {}
    dialog.fill()
    dialog.set_cell("@R_V", "V", "Regular", "-50")
    assert not dialog.staged and "wrong-side" in pair_env.shell.status.text()


def test_pair_rebuild_retains_staged_and_invalid_text(pair_env):
    dialog = pair_env.open()
    dialog.set_cell("A", "V", "Bold", "-120")
    dialog.set_cell("A", "V", "Regular", "abc")
    dialog.partner.setText("T")
    dialog.add_button.click()
    values = {dialog.table.item(row, 0).text(): [dialog.table.item(row, col).text() for col in (1, 2)]
              for row in range(dialog.table.rowCount())}
    assert values["A  V"] == ["abc", "-120"]


def test_copy_remove_and_scale_round_expose_real_shared_plans(editors):
    module, state, _, _, _ = editors
    assert editors[2].kerning_editor_api().copy_plan({("A", "V"): 0}, {}, "missing", 100) == {
        ("A", "V"): 0
    }
    api = editors[2].kerning_editor_api()
    assert api.scaled(-3, 150) == -5
    assert api.round_to(7.5, 5) == 10
    assert api.small_pairs(state.package, ["Regular"], 1) == {
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


def test_captured_snapshot_survives_unchanged_successful_refresh(pair_env):
    dialog = pair_env.open()
    before = dialog.snapshot
    pair_env.shell.refresh_button.click()
    assert dialog.snapshot is not None and dialog.snapshot == before
    assert dialog.snapshot.package_id == pair_env.state.package.id


def test_pair_apply_refuses_lossy_reopen_range_and_clears_staging(pair_env):
    font = pair_env.state.package
    font.upm = 1000
    font.checkInitHistoryState = lambda _: pytest.fail("Invalid final range initialized history")
    dialog = pair_env.open()
    dialog.set_cell("A", "V", "Bold", "2001")
    before = {master: font.pairs(master) for master in font.masters}
    pair_env.shell.apply_button.click()
    assert "save/reopen range" in pair_env.shell.status.text()
    assert not dialog.staged and dialog.snapshot is None and not dialog.ready()
    assert not pair_env.state.notified, "Invalid final range created native history"
    assert {master: font.pairs(master) for master in font.masters} == before
