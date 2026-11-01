# this_file: tests/test_cov_b_kerning_values.py
"""Drive the Round, Scale and Remove Small kerning editors through their real dialogs."""

import runpy
import sys

import pytest
from _cov_b_support import ROOT, Env, Package, check_clean, make_package


@pytest.fixture
def env(monkeypatch, real_app, app_sources):
    """Fake PythonQt plus the real App helpers and an integer-valued font."""
    return Env(monkeypatch, real_app, make_package())


@pytest.fixture
def no_font(monkeypatch, real_app, app_sources):
    """The same fakes with no font open."""
    return Env(monkeypatch, real_app, None)


EDITORS = [
    ("Round Values", "RoundKerning", "Round Kerning"),
    ("Scale Values", "ScaleKerning", "Scale Kerning"),
]


# ---------------------------------------------------------------- Round Values
def test_round_dialog_when_opened_then_preview_lists_the_pair_that_moves(env):
    dialog = env.open("Kerning", "Round Values", "RoundKerning")
    check_clean(dialog)
    assert dialog.scope.items == ["Current master (Bold)", "All masters (2)"], (
        "scope combo must name the current master and the master count"
    )
    assert dialog.table.texts() == [["T  o", "Bold", "-3", "-5"]], (
        "only -3 is off the step of five on the current master"
    )
    assert dialog.status.text == "1 pairs change (Bold 1)", dialog.status.text
    assert dialog.apply_button.enabled, "Apply must be enabled when a pair changes"
    assert "multiples of 5" in dialog.subtitle.text, dialog.subtitle.text


def test_round_dialog_when_step_and_scope_change_then_zero_pairs_are_deleted(env):
    dialog = env.open("Kerning", "Round Values", "RoundKerning")
    dialog.step.setValue(10)
    dialog.scope.setCurrentIndex(1)
    check_clean(dialog)
    rows = dialog.table.texts()
    assert ["T  V", "Regular", "12", "10"] in rows, rows
    assert ["Aacute  V", "Regular", "0", "removed"] in rows, (
        "an explicit zero is deleted when the drop-zero option is on"
    )
    assert dialog.status.text == "5 pairs change (Regular 4 · Bold 1)", dialog.status.text
    dialog.drop_zero.setChecked(False)
    assert ["Aacute  V", "Regular", "0", "removed"] not in dialog.table.texts(), (
        "keeping zeros must stop the explicit zero from being deleted"
    )
    assert dialog.chosen_masters() == ["Regular", "Bold"], "expected: dialog.chosen_masters() == ['Regular', 'Bold']"


def test_round_dialog_when_apply_clicked_then_all_masters_are_rewritten(env):
    dialog = env.open("Kerning", "Round Values", "RoundKerning")
    dialog.step.setValue(10)
    dialog.scope.setCurrentIndex(1)
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    assert env.package.pairs("Regular") == {
        ("@L_A", "@R_V"): -80,
        ("A", "@R_V"): -60,
        ("@L_A", "V"): -40,
        ("A", "V"): -60,
        ("T", "V"): 10,
    }, "Regular must keep multiples of ten and lose the zero and small pairs"
    assert ("T", "o") not in env.package.pairs("Bold"), "Bold -3 rounds to zero and goes"
    assert env.updates == 1, "UpdateAll must run once after the batch"
    assert [name for name, _ in env.notified] == ["Round Kerning"] * 2, (
        "one Undo step brackets the native writes"
    )
    assert dialog.status.text == "Changed 5 pairs (Regular 4 · Bold 1)", dialog.status.text
    assert dialog.last_result == {"Regular": 4, "Bold": 1}, dialog.last_result


def test_round_dialog_when_nothing_changes_then_apply_stays_disabled(env):
    for master in env.package.masters:
        kerning = env.package.kerning(master)
        kerning.stored = {k: round(v / 5) * 5 for k, v in kerning.stored.items() if v}
    dialog = env.open("Kerning", "Round Values", "RoundKerning")
    assert dialog.status.text == "Nothing to change", dialog.status.text
    assert not dialog.apply_button.enabled, "nothing to write means no Apply"
    dialog.apply()
    assert dialog.status.text == "Changed 0 pairs (Bold 0)", dialog.status.text
    assert env.notified == [], "a no-op must not create history"


# ---------------------------------------------------------------- Scale Values
def test_scale_dialog_when_percent_changes_then_preview_uses_halves_away_from_zero(env):
    dialog = env.open("Kerning", "Scale Values", "ScaleKerning")
    check_clean(dialog)
    assert dialog.status.text == "Nothing to change", "100 % changes nothing"
    dialog.percent.setValue(50)
    check_clean(dialog)
    assert dialog.table.texts() == [
        ["@L_A  @R_V", "Bold", "-90", "-45"],
        ["A  V", "Bold", "-70", "-35"],
        ["T  V", "Bold", "10", "5"],
        ["T  o", "Bold", "-3", "-2"],
    ], "-1.5 rounds away from zero to -2"
    assert "multiplied by 50 %" in dialog.subtitle.text, dialog.subtitle.text


def test_scale_dialog_when_apply_clicked_then_values_are_written(env):
    dialog = env.open("Kerning", "Scale Values", "ScaleKerning")
    dialog.percent.setValue(50)
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    assert env.package.pairs("Bold") == {
        ("@L_A", "@R_V"): -45,
        ("A", "V"): -35,
        ("T", "V"): 5,
        ("T", "o"): -2,
    }, env.package.pairs("Bold")
    assert env.package.pairs("Regular")[("A", "V")] == -60, "Regular was out of scope"
    assert dialog.status.text == "Changed 4 pairs (Bold 4)", dialog.status.text
    assert all(factor in (0.0, 1.0) for factor in env.package.kerning("Bold").scales), "expected: all((factor in (0.0, 1.0) for factor in env.package.kerning('Bold')..."


def test_scale_dialog_when_zero_percent_then_drop_option_decides_deletion(env):
    dialog = env.open("Kerning", "Scale Values", "ScaleKerning")
    dialog.percent.setValue(0)
    assert {row[3] for row in dialog.table.texts()} == {"removed"}, (
        "scaling to zero with the option on deletes every nonzero pair"
    )
    dialog.drop_zero.setChecked(False)
    assert {row[3] for row in dialog.table.texts()} == {"0"}, (
        "with the option off the pairs are kept as explicit zeros"
    )
    dialog.apply()
    assert set(env.package.pairs("Bold").values()) == {0}, "explicit zeros must survive"
    assert len(env.package.pairs("Bold")) == 4, "expected: len(env.package.pairs('Bold')) == 4"


def test_scale_dialog_when_result_exceeds_native_range_then_apply_refuses(env):
    env.package.upm = 100
    dialog = env.open("Kerning", "Scale Values", "ScaleKerning")
    dialog.percent.setValue(400)
    with pytest.raises(ValueError, match="save/reopen range"):
        dialog.apply()
    assert env.package.pairs("Bold")[("@L_A", "@R_V")] == -90, "nothing may be written"
    assert not dialog.apply_button.enabled, "a refused batch disables Apply"
    assert env.notified == [], "a refused batch must not create history"


# ---------------------------------------------------------------- Remove Small Pairs
def test_remove_small_dialog_when_opened_then_lists_pairs_below_threshold(env):
    dialog = env.open("Kerning", "Remove Small Pairs", "RemoveSmall")
    check_clean(dialog)
    assert dialog.table.texts() == [["T  o", "Bold", "-3"]], dialog.table.texts()
    assert dialog.status.text == "1 to remove (Bold 1)", dialog.status.text
    assert dialog.subtitle.text.startswith("4 pairs in 1 master;"), dialog.subtitle.text
    dialog.threshold.setValue(1)
    assert dialog.table.texts() == [], "nothing is below one unit on Bold"
    assert dialog.status.text == "No pairs below the threshold", dialog.status.text
    assert not dialog.apply_button.enabled, "expected: not dialog.apply_button.enabled"


def test_remove_small_dialog_when_all_masters_applied_then_pairs_are_deleted(env):
    dialog = env.open("Kerning", "Remove Small Pairs", "RemoveSmall")
    dialog.scope.setCurrentIndex(1)
    assert dialog.table.texts() == [
        ["Aacute  V", "Regular", "0"],
        ["T  o", "Regular", "3"],
        ["V  A", "Regular", "-4"],
        ["T  o", "Bold", "-3"],
    ], "pairs are ordered by magnitude, then by name, per master"
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    assert set(env.package.pairs("Regular")) == {
        ("@L_A", "@R_V"),
        ("A", "@R_V"),
        ("@L_A", "V"),
        ("A", "V"),
        ("T", "V"),
    }, "small Regular pairs must be gone"
    assert ("T", "o") not in env.package.pairs("Bold"), "expected: ('T', 'o') not in env.package.pairs('Bold')"
    assert dialog.status.text == "Removed 4 pairs (Regular 3 · Bold 1)", dialog.status.text
    assert env.updates == 1, "expected: env.updates == 1"


def test_remove_small_dialog_when_font_changes_before_apply_then_click_is_contained(env):
    dialog = env.open("Kerning", "Remove Small Pairs", "RemoveSmall")
    env.package = Package(["Regular"], {"Regular": make_package().kerning("Regular")}, {})
    env.package.id = 8
    dialog.apply_button.clicked.emit()
    assert "no longer current" in dialog.slot_error, dialog.slot_error
    assert dialog.status.text.startswith("Error:"), dialog.status.text
    assert not dialog.apply_button.enabled, "a stale dialog must not offer Apply"
    assert env.notified == [], "a stale click must not write"


def test_remove_small_dialog_when_pair_is_fractional_then_apply_refuses_without_writing(env):
    env.package.kerning("Bold").stored[(("T", "glyphMode"), ("o", "glyphMode"))] = -2.5
    dialog = env.open("Kerning", "Remove Small Pairs", "RemoveSmall")
    assert dialog.table.texts() == [["T  o", "Bold", "-2.5"]], "the preview still lists it"
    with pytest.raises(ValueError, match="fractional"):
        dialog.apply()
    assert env.package.pairs("Bold")[("T", "o")] == -2.5, "a refused write changes nothing"
    assert env.notified == [], "a refused write must not create history"


# ---------------------------------------------------------------- shared refusal paths
@pytest.mark.parametrize(("title", "cls", "_undo"), EDITORS)
def test_value_editors_when_no_font_then_open_font_first(no_font, title, cls, _undo):
    dialog = no_font.open("Kerning", title, cls)
    check_clean(dialog)
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.table.texts() == [], "no font means no rows"
    assert not dialog.apply_button.enabled, "no font means no Apply"
    assert dialog.status.text == "Nothing to change", dialog.status.text


def test_remove_small_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Remove Small Pairs", "RemoveSmall")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.status.text == "No pairs below the threshold", dialog.status.text


@pytest.mark.parametrize(
    "title",
    ["Round Values", "Scale Values", "Remove Small Pairs"],
)
def test_editors_when_close_clicked_then_registry_entry_is_released(env, title):
    module = env.load("Kerning", title)
    dialog = module.main()
    assert sys._fontlab_samples[module.KEY] is dialog, "main registers the dialog"
    dialog.close_button.clicked.emit()
    assert sys._fontlab_samples == {}, "Close must release the registry entry"
    assert dialog.deleted, "Close must schedule destruction"
    assert dialog.refresh_button.clicked.slots == [], "Close must disconnect its slots"


@pytest.mark.parametrize(
    "title", ["Round Values", "Scale Values", "Remove Small Pairs"]
)
def test_editors_when_run_as_script_then_main_is_called(env, title):
    namespace = runpy.run_path(
        str(ROOT / "Scripts/Kerning" / f"{title}.py"), run_name="__main__"
    )
    assert namespace["KEY"] in sys._fontlab_samples, "running as a script opens the dialog"


@pytest.mark.parametrize(
    ("title", "undo"),
    [
        ("Round Values", "Round Kerning"),
        ("Scale Values", "Scale Kerning"),
        ("Remove Small Pairs", "Remove Small Kerning"),
    ],
)
def test_write_kerning_when_called_from_console_then_edit_uses_tool_undo_name(env, title, undo):
    module = env.load("Kerning", title)
    module.write_kerning(env.package, {"Bold": {("T", "o"): None}})
    assert ("T", "o") not in env.package.pairs("Bold"), "the console writer must delete the pair"
    assert env.notified[0][0] == undo, env.notified
