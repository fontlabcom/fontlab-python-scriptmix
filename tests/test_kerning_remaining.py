# this_file: tests/test_kerning_remaining.py
"""Preserve the final two complete kerning editors without a native host."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from test_kerning_editors import editors, load  # noqa: F401 - fixture dependencies

TITLES = ["Exceptions Finder", "Pairs From Text"]


@pytest.mark.parametrize("title", TITLES)
def test_requested_complete_editor_exists(title):
    assert (
        Path(__file__).parents[1] / "Scripts/Kerning" / (title + ".py")
    ).is_file(), "Requested complete kerning editor missing"


@pytest.fixture
def remaining(editors, monkeypatch, app_sources):  # noqa: F811 - pytest fixture
    spec = importlib.util.spec_from_file_location(
        "fontlabapp.kerning_selection", app_sources / "kerning_selection.py"
    )
    api = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fontlabapp.kerning_selection", api)
    spec.loader.exec_module(api)
    return editors


def panel(remaining, title):
    module, state, _, _shared, _qt = remaining
    cls = getattr(
        module(title),
        {"Exceptions Finder": "ExceptionsFinder", "Pairs From Text": "PairsFromText"}[
            title
        ],
    )
    dialog = cls.__new__(cls)
    dialog.package = state.package
    dialog.masters = list(state.package.masters)
    dialog.current_master = state.package.master
    dialog._snapshot_valid, dialog._scanned_id = True, state.package.id
    dialog._kerning_snapshot = sys.modules["fontlabapp.kerning_batch"].snapshot_kerning(
        state.package
    )
    dialog.messages, dialog.enabled = [], []
    dialog.status = NS(setText=dialog.messages.append)
    dialog.subtitle = NS(setText=dialog.messages.append)
    dialog.apply_button = NS(setEnabled=dialog.enabled.append)
    dialog.table = NS(setRowCount=lambda n: None)
    dialog.staged, dialog.values, dialog.rows, dialog.pairs = {}, {}, [], []
    dialog.filling = False
    dialog.scope = NS(currentIndex=0)
    dialog.mode = NS(currentIndex=1)
    dialog.value = NS(value=-10)
    dialog.file_dialog, dialog._key, dialog._connections = None, module(title).KEY, []
    return dialog, cls


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("change", ["font", "closed", "pairs", "classes", "masters"])
def test_apply_refuses_changed_full_snapshot_and_clears_results(
    remaining, title, change
):
    dialog, cls = panel(remaining, title)
    state = remaining[1]
    dialog.values["partial"] = 9
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
    assert not dialog._snapshot_valid and dialog.values == {} and dialog.rows == {}
    assert dialog.enabled[-1] is False


@pytest.mark.parametrize("title", TITLES)
def test_actual_owned_close_disconnects_and_releases_registry(
    remaining, monkeypatch, title
):
    dialog, cls = panel(remaining, title)
    calls = []
    remaining[4].QtGui.QDialog = NS(closeEvent=lambda d, e: calls.append("close"))
    dialog.deleteLater = lambda: calls.append("delete")
    dialog._connections = [
        (NS(disconnect=lambda slot: calls.append(slot)), "owned-wrapper")
    ]
    windows = {dialog._key: dialog}
    monkeypatch.setattr(sys, "_fontlab_samples", windows, raising=False)
    cls.closeEvent(dialog, None)
    assert calls == ["owned-wrapper", "close", "delete"] and not windows
    assert cls._connect is remaining[3].KerningEditDialog._connect


def checkboxes(remaining, dialog, rows):
    qt = remaining[4]
    qt.QtCore.Qt.Checked, qt.QtCore.Qt.Unchecked = 2, 0
    callbacks = []
    signal = NS(connect=callbacks.append)
    dialog._connect(signal, lambda *args: dialog.count())

    class Item:
        def __init__(self):
            self.state = 0

        def checkState(self):
            return self.state

        def setCheckState(self, state):
            self.state = state
            for callback in callbacks:
                callback(self)

    items = [Item() for _ in rows]
    dialog.table = NS(
        rowCount=len(rows), item=lambda r, c: items[r], setRowCount=lambda n: None
    )
    return items


def test_redundant_and_manual_ticks_emit_actual_shared_callbacks(remaining):
    dialog, cls = panel(remaining, "Exceptions Finder")
    dialog.rows = [
        ("Bold", ("A", "V"), 0, ("A", "@R_V"), 0),
        ("Bold", ("T", "V"), -10, ("T", "@R_V"), -60),
    ]
    dialog.tick_redundant = NS(setEnabled=lambda value: None)
    items = checkboxes(remaining, dialog, dialog.rows)
    cls.tick(dialog, lambda row: row[2] == row[4])
    assert (
        cls.ticked(dialog) == [dialog.rows[0]]
        and dialog.messages[-1] == "1 of 2 ticked"
    )
    items[1].setCheckState(2)
    assert cls.ticked(dialog) == dialog.rows and dialog.messages[-1] == "2 of 2 ticked"
    cls.tick(dialog, lambda row: False)
    assert not cls.ticked(dialog) and dialog.enabled[-1] is False


def test_text_manual_ticks_plan_effective_add_on_chosen_masters(remaining):
    dialog, cls = panel(remaining, "Pairs From Text")
    dialog.pairs = [("A", "V"), ("T", "V")]
    dialog.values = {
        (("A", "V"), "Regular"): (0, True),
        (("A", "V"), "Bold"): (-80, False),
        (("T", "V"), "Regular"): (-5, True),
        (("T", "V"), "Bold"): (-10, True),
    }
    items = checkboxes(remaining, dialog, dialog.pairs)
    cls.tick(dialog, [("A", "V")])
    assert cls.plan(dialog) == {"Bold": {("A", "V"): -90}}
    dialog.scope.currentIndex = 1
    items[0].setCheckState(2)
    assert cls.plan(dialog) == {"Regular": {("A", "V"): -10}, "Bold": {("A", "V"): -90}}
    dialog.mode.currentIndex, dialog.value.value = 0, 0
    assert cls.plan(dialog) == {"Regular": {("A", "V"): 0}, "Bold": {("A", "V"): 0}}
    cls.tick(dialog, [])
    assert cls.plan(dialog) == {} and dialog.enabled[-1] is False


@pytest.mark.parametrize("title", TITLES)
def test_postwrite_preview_failure_reports_applied_outcome_without_success(
    remaining, title
):
    dialog, cls = panel(remaining, title)
    dialog.ticked = list
    dialog.plan = lambda: {"Bold": {("A", "V"): -90}}

    def write(edits, title):
        dialog._batch_written = True

    dialog.write_edits = write

    def fail(*args, **kwargs):
        dialog._snapshot_valid = False
        dialog.slot_error = "readback unavailable"

    dialog.refresh = fail
    with pytest.raises(RuntimeError, match="Kerning was applied.*preview failed"):
        cls.apply(dialog)
    assert not dialog._snapshot_valid and dialog.last_result is None
    assert not any(
        message.startswith(("Wrote", "Removed")) for message in dialog.messages
    )


@pytest.mark.parametrize("title", TITLES)
def test_native_write_failure_clears_staging_and_preserves_honest_error(
    remaining, title
):
    dialog, cls = panel(remaining, title)
    dialog.ticked = lambda: [("Bold", ("A", "V"), 0, ("A", "@R_V"), 0)]
    dialog.plan = lambda: {"Bold": {("A", "V"): -90}}

    def fail(*args):
        raise RuntimeError("Kerning may be partially changed; use Undo and Refresh.")

    dialog.write_edits = fail
    with pytest.raises(RuntimeError, match="partially changed.*Undo"):
        cls.apply(dialog)
    assert not dialog._snapshot_valid and dialog.last_result is None


def test_failed_effective_preview_clears_every_partial_text_result(remaining):
    dialog, cls = panel(remaining, "Pairs From Text")
    dialog.text = NS(text="AVA")
    dialog.package.kerning("Regular").get = lambda pair: (_ for _ in ()).throw(
        RuntimeError("broken effective read")
    )
    cls.refresh(dialog)
    assert dialog.values == {} and dialog.pairs == [] and not dialog._snapshot_valid
    assert (
        "broken effective read" in dialog.messages[-1]
        and "Refresh" in dialog.messages[-1]
    )


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("phase", ["update", "preview"])
def test_guarded_apply_retains_completed_write_and_recovery_on_display_failure(
    remaining, monkeypatch, title, phase
):
    dialog, cls = panel(remaining, title)
    dialog.ticked = list
    dialog.plan = lambda: {"Bold": {("A", "V"): -90}}
    dialog.staged["old"] = 1
    completed = []

    def write(edits, title):
        completed.append(edits)
        dialog._batch_written = True

    dialog.write_edits = write

    def fail(*args, **kwargs):
        raise RuntimeError(f"native {phase} failed")

    monkeypatch.setattr(
        remaining[0](title).fontlab,
        "UpdateAll",
        fail if phase == "update" else lambda: None,
    )
    dialog.refresh = fail if phase == "preview" else lambda **kwargs: None
    callbacks = []
    dialog._connect(NS(connect=callbacks.append), lambda *args: cls.apply(dialog))
    callbacks[0](False)
    assert completed, (
        "The owned write must complete before the injected display failure"
    )
    assert (
        not dialog._snapshot_valid and dialog.last_result is None and not dialog.staged
    )
    assert dialog.enabled[-1] is False
    message = dialog.messages[-1]
    assert all(
        text in message
        for text in ("Kerning was applied", f"native {phase} failed", "Undo", "Refresh")
    ), message
    assert not any(
        message.startswith(("Wrote", "Removed")) for message in dialog.messages
    )


def test_guarded_text_apply_retains_completed_write_when_postwrite_ticks_fail(
    remaining,
):
    dialog, cls = panel(remaining, "Pairs From Text")
    dialog.plan = lambda: {"Bold": {("A", "V"): -90}}

    def write(edits, title):
        dialog._batch_written = True

    dialog.write_edits = write

    def fail():
        raise RuntimeError("postwrite check state failed")

    dialog.ticked = fail
    callbacks = []
    dialog._connect(NS(connect=callbacks.append), lambda *args: cls.apply(dialog))
    callbacks[0](False)
    assert (
        not dialog._snapshot_valid and not dialog.staged and dialog.enabled[-1] is False
    )
    message = dialog.messages[-1]
    assert all(
        text in message
        for text in (
            "Kerning was applied",
            "postwrite check state failed",
            "Undo",
            "Refresh",
        )
    ), message


@pytest.mark.parametrize("title", TITLES)
def test_guarded_apply_keeps_preflight_and_partial_writer_diagnostics(remaining, title):
    dialog, cls = panel(remaining, title)
    dialog._batch_written = (
        True  # Earlier successful Apply must not taint this refusal.
    )
    dialog._snapshot_valid = False
    callbacks = []
    dialog._connect(NS(connect=callbacks.append), lambda *args: cls.apply(dialog))
    callbacks[0](False)
    assert (
        "stale" in dialog.messages[-1]
        and "Kerning was applied" not in dialog.messages[-1]
    )
    dialog, cls = panel(remaining, title)
    dialog.plan = lambda: {"Bold": {("A", "V"): -90}}
    dialog.ticked = list

    def fail(*args):
        raise RuntimeError(
            "Kerning may be partially changed; use Undo and Refresh. setter failed"
        )

    dialog.write_edits = fail
    callbacks = []
    dialog._connect(NS(connect=callbacks.append), lambda *args: cls.apply(dialog))
    callbacks[0](False)
    assert (
        "partially changed" in dialog.messages[-1]
        and "setter failed" in dialog.messages[-1]
    )
    assert "Kerning was applied" not in dialog.messages[-1]
