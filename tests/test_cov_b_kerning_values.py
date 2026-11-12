# this_file: tests/test_cov_b_kerning_values.py
"""Original Round/Scale/Remove Small assertions on actual studio action widgets."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest
from _cov_b_support import Package, make_package
from _wp03_studio_support import rows as displayed_rows, studio_host as _studio_host
studio_host = _studio_host


@pytest.fixture
def env(studio_host):
    studio_host.package = make_package()
    class Environment:
        state = studio_host
        @property
        def package(self):
            return self.state.package
        @package.setter
        def package(self, value):
            self.state.package = value
        def open(self, panel):
            self.app = self.state.open()
            return self.app.panels[panel]
    return Environment()


def test_round_dialog_when_opened_then_preview_lists_the_pair_that_moves(env):
    dialog = env.open("RoundPanel")
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert env.state.notified == [], "Opening and preview must not create history"
    assert [dialog.scope.itemText(i) for i in range(dialog.scope.count())] == ["Current master (Bold)", "All masters (2)"], (
        "scope combo must name the current master and the master count"
    )
    assert displayed_rows(dialog) == [["T  o", "Bold", "-3", "-5"]], (
        "only -3 is off the step of five on the current master"
    )
    assert dialog.count.text() == "1 pairs change (Bold 1)", dialog.count.text()
    assert dialog.apply_button.isEnabled(), "Apply must be enabled when a pair changes"
    assert "multiples of 5" in dialog.subtitle.text(), dialog.subtitle.text()


def test_round_dialog_when_step_and_scope_change_then_zero_pairs_are_deleted(env):
    dialog = env.open("RoundPanel")
    dialog.parameter.setValue(10)
    dialog.scope.setCurrentIndex(1)
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert env.state.notified == [], "Changing controls must not create history"
    rows = displayed_rows(dialog)
    assert ["T  V", "Regular", "12", "10"] in rows, rows
    assert ["Aacute  V", "Regular", "0", "removed"] in rows, (
        "an explicit zero is deleted when the drop-zero option is on"
    )
    assert dialog.count.text() == "5 pairs change (Regular 4 · Bold 1)", dialog.count.text()
    dialog.drop_zero.setChecked(False)
    assert ["Aacute  V", "Regular", "0", "removed"] not in displayed_rows(dialog), (
        "keeping zeros must stop the explicit zero from being deleted"
    )
    assert dialog.tool.scope(dialog.scope.currentIndex() == 1) == ["Regular", "Bold"], "expected: dialog.tool.scope(dialog.scope.currentIndex() == 1) == ['Regular', 'Bold']"


def test_round_dialog_when_apply_clicked_then_all_masters_are_rewritten(env):
    dialog = env.open("RoundPanel")
    dialog.parameter.setValue(10)
    dialog.scope.setCurrentIndex(1)
    planned = {master: len(edits) for master, edits in dialog.edits.items()}
    assert planned == {"Regular": 4, "Bold": 1}
    dialog.apply_button.click()
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert env.package.pairs("Regular") == {
        ("@L_A", "@R_V"): -80,
        ("A", "@R_V"): -60,
        ("@L_A", "V"): -40,
        ("A", "V"): -60,
        ("T", "V"): 10,
    }, "Regular must keep multiples of ten and lose the zero and small pairs"
    assert ("T", "o") not in env.package.pairs("Bold"), "Bold -3 rounds to zero and goes"
    assert env.state.updates == 0, "The studio must not call global UpdateAll"
    assert [name for name, _ in env.state.notified] == ["Kerning Batch: Round kerning on Regular, Bold"] * 2, (
        "one Undo step brackets the native writes"
    )
    assert dialog.tool.status == "Changed 5 pairs (Regular 4 · Bold 1)", dialog.count.text()


def test_round_dialog_when_nothing_changes_then_apply_stays_disabled(env):
    for master in env.package.masters:
        kerning = env.package.kerning(master)
        kerning.stored = {k: round(v / 5) * 5 for k, v in kerning.stored.items() if v}
    dialog = env.open("RoundPanel")
    assert dialog.count.text() == "Nothing to change", dialog.count.text()
    assert not dialog.apply_button.isEnabled(), "nothing to write means no Apply"
    dialog.apply()
    assert dialog.tool.status == "Kerning Batch: Nothing to apply; use Refresh.", dialog.count.text()
    assert env.state.notified == [], "a no-op must not create history"


# ---------------------------------------------------------------- Scale Values
def test_scale_dialog_when_percent_changes_then_preview_uses_halves_away_from_zero(env):
    dialog = env.open("ScalePanel")
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert dialog.count.text() == "Nothing to change", "100 % changes nothing"
    dialog.parameter.setValue(50)
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert displayed_rows(dialog) == [
        ["@L_A  @R_V", "Bold", "-90", "-45"],
        ["A  V", "Bold", "-70", "-35"],
        ["T  V", "Bold", "10", "5"],
        ["T  o", "Bold", "-3", "-2"],
    ], "-1.5 rounds away from zero to -2"
    assert "multiplied by 50 %" in dialog.subtitle.text(), dialog.subtitle.text()
    assert env.state.notified == [], "Scaling preview must not create history"


def test_scale_dialog_when_apply_clicked_then_values_are_written(env):
    dialog = env.open("ScalePanel")
    dialog.parameter.setValue(50)
    dialog.apply_button.click()
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert env.package.pairs("Bold") == {
        ("@L_A", "@R_V"): -45,
        ("A", "V"): -35,
        ("T", "V"): 5,
        ("T", "o"): -2,
    }, env.package.pairs("Bold")
    assert env.package.pairs("Regular")[("A", "V")] == -60, "Regular was out of scope"
    assert dialog.tool.status == "Changed 4 pairs (Bold 4)", dialog.count.text()
    assert all(factor in (0.0, 1.0) for factor in env.package.kerning("Bold").scales), "expected: all((factor in (0.0, 1.0) for factor in env.package.kerning('Bold')..."


def test_scale_dialog_when_zero_percent_then_drop_option_decides_deletion(env):
    dialog = env.open("ScalePanel")
    dialog.parameter.setValue(0)
    assert {row[3] for row in displayed_rows(dialog)} == {"removed"}, (
        "scaling to zero with the option on deletes every nonzero pair"
    )
    dialog.drop_zero.setChecked(False)
    assert {row[3] for row in displayed_rows(dialog)} == {"0"}, (
        "with the option off the pairs are kept as explicit zeros"
    )
    dialog.apply()
    assert set(env.package.pairs("Bold").values()) == {0}, "explicit zeros must survive"
    assert len(env.package.pairs("Bold")) == 4, "expected: len(env.package.pairs('Bold')) == 4"


def test_scale_dialog_when_result_exceeds_native_range_then_apply_refuses(env):
    env.package.upm = 100
    dialog = env.open("ScalePanel")
    dialog.parameter.setValue(400)
    assert dialog.apply() is False
    assert "save/reopen range" in dialog.tool.status
    assert env.package.pairs("Bold")[("@L_A", "@R_V")] == -90, "nothing may be written"
    assert not dialog.apply_button.isEnabled(), "a refused batch disables Apply"
    assert env.state.notified == [], "a refused batch must not create history"


# ---------------------------------------------------------------- Remove Small Pairs
def test_remove_small_dialog_when_opened_then_lists_pairs_below_threshold(env):
    dialog = env.open("RemoveSmallPanel")
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert displayed_rows(dialog) == [["T  o", "Bold", "-3"]], displayed_rows(dialog)
    assert dialog.count.text() == "1 to remove (Bold 1)", dialog.count.text()
    assert dialog.subtitle.text().startswith("4 pairs in 1 master;"), dialog.subtitle.text()
    dialog.threshold.setValue(1)
    assert displayed_rows(dialog) == [], "nothing is below one unit on Bold"
    assert dialog.count.text() == "No pairs below the threshold", dialog.count.text()
    assert not dialog.apply_button.isEnabled(), "expected: not dialog.apply_button.isEnabled()"


def test_remove_small_dialog_when_all_masters_applied_then_pairs_are_deleted(env):
    dialog = env.open("RemoveSmallPanel")
    dialog.scope.setCurrentIndex(1)
    assert displayed_rows(dialog) == [
        ["Aacute  V", "Regular", "0"],
        ["T  o", "Regular", "3"],
        ["V  A", "Regular", "-4"],
        ["T  o", "Bold", "-3"],
    ], "pairs are ordered by magnitude, then by name, per master"
    dialog.apply_button.click()
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert set(env.package.pairs("Regular")) == {
        ("@L_A", "@R_V"),
        ("A", "@R_V"),
        ("@L_A", "V"),
        ("A", "V"),
        ("T", "V"),
    }, "small Regular pairs must be gone"
    assert ("T", "o") not in env.package.pairs("Bold"), "expected: ('T', 'o') not in env.package.pairs('Bold')"
    assert dialog.tool.status == "Removed 4 pairs (Regular 3 · Bold 1)", dialog.count.text()
    assert env.state.updates == 0, "expected: env.state.updates == 0"


def test_remove_small_dialog_when_font_changes_before_apply_then_click_is_contained(env):
    dialog = env.open("RemoveSmallPanel")
    env.package = Package(["Regular"], {"Regular": make_package().kerning("Regular")}, {})
    env.package.id = 8
    dialog.apply_button.click()
    assert "no longer current" in dialog.tool.status, dialog.tool.status
    assert not dialog.apply_button.isEnabled(), "a stale dialog must not offer Apply"
    assert env.state.notified == [], "a stale click must not write"


def test_remove_small_dialog_when_pair_is_fractional_then_apply_refuses_without_writing(env):
    env.package.kerning("Bold").stored[(("T", "glyphMode"), ("o", "glyphMode"))] = -2.5
    dialog = env.open("RemoveSmallPanel")
    assert displayed_rows(dialog) == [["T  o", "Bold", "-2.5"]], "the preview still lists it"
    assert dialog.apply() is False
    assert "fractional" in dialog.tool.status
    assert env.package.pairs("Bold")[("T", "o")] == -2.5, "a refused write changes nothing"
    assert env.state.notified == [], "a refused write must not create history"


@pytest.mark.parametrize("panel", ["RoundPanel", "ScalePanel", "RemoveSmallPanel"])
def test_value_editors_when_no_font_then_open_font_first(studio_host, panel):
    app = studio_host.open()
    dialog = app.panels[panel]
    assert dialog.subtitle.text() == "Open a font first."
    assert displayed_rows(dialog) == [], "No font means no rows"
    assert not dialog.apply_button.isEnabled(), "No font means no Apply"
    assert app.tool.status == "Open a font first."


@pytest.mark.parametrize("panel", ["RoundPanel", "ScalePanel", "RemoveSmallPanel"])
def test_editors_when_close_clicked_then_owned_callbacks_are_released(env, panel):
    dialog = env.open(panel)
    shell = dialog.tool.shell
    shell.close_button.click()
    assert shell.closed and shell._close_complete and shell._delete_scheduled
    assert not shell.widget.isVisible(), "Closed studios must leave the screen"
    assert shell.connections == [], "Close must disconnect every owned callback"


@pytest.mark.parametrize("title", ["Round Values", "Scale Values", "Remove Small Pairs"])
def test_editors_when_run_as_script_then_main_is_called(monkeypatch, title):
    calls = []
    monkeypatch.setitem(sys.modules, "fly.ap.studios.kerning_batch",
                        NS(show=lambda **kwargs: calls.append(kwargs)))
    path = Path(__file__).parents[1] / "Scripts/Kerning/Kerning Batch.py"
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [{"consolidated": True}], f"{title} is available in the shared studio"


@pytest.mark.parametrize("panel,action", [("RoundPanel", "Round"), ("ScalePanel", "Scale"),
                                          ("RemoveSmallPanel", "Remove")])
def test_write_kerning_when_called_from_console_then_edit_uses_tool_undo_name(env, panel, action):
    dialog = env.open(panel)
    dialog.tool.write(action, "kerning on Bold", {"Bold": {("T", "o"): None}}, dialog.snapshot)
    assert ("T", "o") not in env.package.pairs("Bold"), "The console writer must delete the pair"
    assert env.state.notified[0][0] == f"Kerning Batch: {action} kerning on Bold"


@pytest.mark.parametrize("panel", ["RoundPanel", "ScalePanel", "RemoveSmallPanel"])
@pytest.mark.parametrize("change", ["font", "closed", "pairs", "classes", "masters"])
def test_each_real_apply_refuses_stale_before_body_and_clears_staged(env, panel, change):
    dialog = env.open(panel)
    if panel == "ScalePanel":
        dialog.parameter.setValue(50)
    original_package = env.package
    if change == "font":
        env.package = NS(id=8, isNull=False)
    elif change == "closed":
        env.package = None
    elif change == "masters":
        original_package.masters.reverse()
    elif change == "pairs":
        original_package.kerning("Bold").stored.clear()
    else:
        original_package.kerning("Bold").groups["L_A"] = (["T"], "KernLeft")
    assert dialog.apply() is False
    assert "stale" in dialog.tool.status or "current" in dialog.tool.status
    assert not dialog.edits and dialog.snapshot is None
    assert not dialog.apply_button.isEnabled()
    assert displayed_rows(dialog) == [], "Stale previews must clear their old rows"
    assert env.state.notified == [], "Preflight refusals must not open history"
