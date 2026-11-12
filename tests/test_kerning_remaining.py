# this_file: tests/test_kerning_remaining.py
"""Preserve the final two complete kerning editors without a native host."""


import pytest
import _wp03_proof as proof_contract
import _wp03_browser as browser_contract

from _wp03_proof import tick  # noqa: F401

browser_env = browser_contract.browser_env
proof_env = proof_contract.proof_env

TITLES = ["Exceptions Finder", "Pairs From Text"]


@pytest.mark.parametrize("title", TITLES)
def test_requested_complete_editor_exists(title):
    proof_contract.identity(title)






@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("change", ["font", "closed", "pairs", "classes", "masters"])
def test_apply_refuses_changed_full_snapshot_and_clears_results(
    title, change, request):
    contract = proof_contract if title == "Pairs From Text" else browser_contract
    fixture = "proof_env" if title == "Pairs From Text" else "browser_env"
    contract.snapshot_refusal(request.getfixturevalue(fixture), change)


@pytest.mark.parametrize("title", TITLES)
def test_actual_owned_close_disconnects_and_releases_registry(
    monkeypatch, title, request):
    contract = proof_contract if title == "Pairs From Text" else browser_contract
    fixture = "proof_env" if title == "Pairs From Text" else "browser_env"
    contract.close_owner(request.getfixturevalue(fixture), title)




def test_redundant_and_manual_ticks_emit_actual_shared_callbacks(browser_env):
    dialog = browser_env.open("Exceptions Finder")
    dialog.rows = [("Bold", ("A", "V"), 0, ("A", "@R_V"), 0),
                   ("Bold", ("T", "V"), -10, ("T", "@R_V"), -60)]
    module = browser_env.load("Exceptions Finder")
    dialog.grid.set_rows([module.cells(row) for row in dialog.rows])
    dialog.tick(lambda row: row[2] == row[4])
    assert dialog.ticked() == [dialog.rows[0]] and dialog.tool.status == "1 of 2 ticked"
    dialog.grid.view.item(1, 0).setCheckState(browser_contract.checked())
    assert dialog.ticked() == dialog.rows and dialog.tool.status == "2 of 2 ticked"
    dialog.tick(lambda row: False)
    assert not dialog.ticked() and not dialog.apply_button.isEnabled()


def test_text_manual_ticks_plan_effective_add_on_chosen_masters(proof_env):
    dialog = proof_env.open("Pairs From Text")
    dialog.text.setText("AV TV")
    dialog.refresh()
    dialog.values = {(("A", "V"), "Regular"): (0, True), (("A", "V"), "Bold"): (-80, False),
                     (("T", "V"), "Regular"): (-5, True), (("T", "V"), "Bold"): (-10, True)}
    tick(dialog, [("A", "V")])
    dialog.mode.setCurrentIndex(1)
    dialog.value.setValue(-10)
    assert dialog.plan() == {"Bold": {("A", "V"): -90}}
    dialog.scope.setCurrentIndex(1)
    assert dialog.plan() == {"Regular": {("A", "V"): -10}, "Bold": {("A", "V"): -90}}
    dialog.mode.setCurrentIndex(0)
    dialog.value.setValue(0)
    assert dialog.plan() == {"Regular": {("A", "V"): 0}, "Bold": {("A", "V"): 0}}
    tick(dialog, [])
    dialog.preview_changes()
    assert dialog.plan() == {} and not dialog.ready()



@pytest.mark.parametrize("title", TITLES)
def test_postwrite_preview_failure_reports_applied_outcome_without_success(
    title, request):
    contract = proof_contract if title == "Pairs From Text" else browser_contract
    fixture = "proof_env" if title == "Pairs From Text" else "browser_env"
    contract.completed_failure(request.getfixturevalue(fixture))


@pytest.mark.parametrize("title", TITLES)
def test_native_write_failure_clears_staging_and_preserves_honest_error(
    title, request):
    contract = proof_contract if title == "Pairs From Text" else browser_contract
    fixture = "proof_env" if title == "Pairs From Text" else "browser_env"
    contract.partial_failure(request.getfixturevalue(fixture))


def test_failed_effective_preview_clears_every_partial_text_result(proof_env):
    dialog = proof_env.open("Pairs From Text")
    dialog.text.setText("/Aacute/V")
    proof_env.package.kerning("Bold").get = lambda pair: (_ for _ in ()).throw(RuntimeError("broken effective read"))
    dialog.reload_view()
    assert dialog.values == {} and dialog.pairs == [] and dialog.snapshot is None
    assert "broken effective read" in proof_env.shell.status.text() and "Refresh" in proof_env.shell.status.text()



@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("phase", ["update", "preview"])
def test_guarded_apply_retains_completed_write_and_recovery_on_display_failure(
    monkeypatch, title, phase, request):
    contract = proof_contract if title == "Pairs From Text" else browser_contract
    fixture = "proof_env" if title == "Pairs From Text" else "browser_env"
    contract.completed_failure(request.getfixturevalue(fixture), phase)


def test_guarded_text_apply_retains_completed_write_when_postwrite_ticks_fail(proof_env):
    proof_contract.postwrite_ticks(proof_env)



@pytest.mark.parametrize("title", TITLES)
def test_guarded_apply_keeps_preflight_and_partial_writer_diagnostics(title, request):
    contract = proof_contract if title == "Pairs From Text" else browser_contract
    fixture = "proof_env" if title == "Pairs From Text" else "browser_env"
    contract.preflight_and_partial(request.getfixturevalue(fixture))
