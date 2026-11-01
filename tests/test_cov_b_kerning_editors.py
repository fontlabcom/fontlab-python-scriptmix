# this_file: tests/test_cov_b_kerning_editors.py
"""Drive Copy Between Masters, Exceptions Finder, Pair Editor and Pairs From Text."""

import runpy
import sys

import pytest
from _cov_b_support import ROOT, Env, Package, check_clean, make_package

CHECKED, UNCHECKED = 2, 0


@pytest.fixture
def env(monkeypatch, real_app, app_sources):
    """Two masters, Bold current."""
    return Env(monkeypatch, real_app, make_package())


@pytest.fixture
def three(monkeypatch, real_app, app_sources):
    """Three masters with Bold current, so Copy has two targets."""
    package = make_package(("Regular", "Bold", "Light"))
    package.master = "Bold"
    return Env(monkeypatch, real_app, package)


@pytest.fixture
def no_font(monkeypatch, real_app, app_sources):
    """No font open."""
    return Env(monkeypatch, real_app, None)


def replace_font(env):
    """Swap in a different current font, as if the user switched documents."""
    other = Package(["Regular"], {"Regular": make_package().kerning("Regular")}, {})
    other.id = 99
    env.package = other


# ---------------------------------------------------------------- Copy Between Masters
def test_copy_dialog_when_opened_then_lists_other_masters_unticked(three):
    dialog = three.open("Kerning", "Copy Between Masters", "CopyKerning")
    check_clean(dialog)
    assert dialog.source.items == ["Regular", "Bold", "Light"], "source offers all masters"
    assert dialog.source.currentIndex == 1, "the current master is the default source"
    assert dialog.targets.texts() == [
        ["Regular", "8", "", "", ""],
        ["Light", "4", "", "", ""],
    ], "the source master is never its own target"
    assert dialog.subtitle.text == "Bold has 4 pairs. Tick the masters that receive them.", "expected: dialog.subtitle.text == 'Bold has 4 pairs. Tick the masters that re..."
    assert dialog.status.text == "Tick at least one target master", dialog.status.text
    assert not dialog.apply_button.enabled, "nothing ticked means nothing to copy"


def test_copy_dialog_when_target_ticked_then_preview_counts_added_changed_removed(three):
    dialog = three.open("Kerning", "Copy Between Masters", "CopyKerning")
    dialog.targets.item(0, 0).setCheckState(CHECKED)
    check_clean(dialog)
    assert dialog.targets.texts()[0] == ["Regular", "8", "0", "4", "4"], (
        "Bold's four pairs overwrite four Regular values and delete four others"
    )
    assert dialog.chosen_targets() == ["Regular"], "expected: dialog.chosen_targets() == ['Regular']"
    assert dialog.status.text == "8 pair edits in 1 master", dialog.status.text
    assert dialog.apply_button.enabled, "expected: dialog.apply_button.enabled"
    dialog.mode.setCurrentIndex(1)
    assert dialog.mode_key() == "missing", "expected: dialog.mode_key() == 'missing'"
    assert dialog.targets.texts()[0] == ["Regular", "8", "0", "0", "0"], (
        "add-missing leaves existing pairs alone"
    )
    assert dialog.status.text == "0 pair edits in 1 master", "expected: dialog.status.text == '0 pair edits in 1 master'"
    assert not dialog.apply_button.enabled, "zero edits must not enable Apply"
    dialog.mode.setCurrentIndex(2)
    assert dialog.targets.texts()[0] == ["Regular", "8", "0", "4", "0"], (
        "matching mode overwrites but never deletes"
    )


def test_copy_dialog_when_applied_then_target_receives_scaled_source_pairs(three):
    dialog = three.open("Kerning", "Copy Between Masters", "CopyKerning")
    dialog.set_targets(["Regular", "Light"])
    dialog.percent.setValue(50)
    check_clean(dialog)
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    assert three.package.pairs("Regular") == {
        ("@L_A", "@R_V"): -45,
        ("A", "V"): -35,
        ("T", "V"): 5,
        ("T", "o"): -2,
    }, "Regular must now hold half of Bold, with the extra pairs removed"
    assert three.package.pairs("Light") == three.package.pairs("Regular"), "expected: three.package.pairs('Light') == three.package.pairs('Regular')"
    assert three.package.pairs("Bold")[("A", "V")] == -70, "the source must not change"
    assert dialog.status.text == "Copied: Regular +0 ~4 −4 · Light +0 ~4 −0", dialog.status.text
    assert three.updates == 1, "expected: three.updates == 1"


def test_copy_dialog_when_source_changes_then_rows_rebuild_and_ticks_survive(three):
    dialog = three.open("Kerning", "Copy Between Masters", "CopyKerning")
    dialog.set_targets(["Light"])
    assert dialog.targets.item(1, 0).checkState() == CHECKED, "expected: dialog.targets.item(1, 0).checkState() == CHECKED"
    dialog.source.setCurrentIndex(0)
    check_clean(dialog)
    assert [row[0] for row in dialog.targets.texts()] == ["Bold", "Light"], "expected: [row[0] for row in dialog.targets.texts()] == ['Bold', 'Light']"
    assert dialog.chosen_targets() == ["Light"], "a tick on Light survives a source change"
    assert dialog.source_master() == "Regular", "expected: dialog.source_master() == 'Regular'"
    dialog.targets.item(0, 1).setText("ignored")
    assert dialog.chosen_targets() == ["Light"], "only the name column toggles a master"


def test_copy_dialog_when_target_unticked_then_status_asks_for_a_target(three):
    dialog = three.open("Kerning", "Copy Between Masters", "CopyKerning")
    dialog.targets.item(0, 0).setCheckState(CHECKED)
    dialog.targets.item(0, 0).setCheckState(UNCHECKED)
    assert dialog.status.text == "Tick at least one target master", dialog.status.text
    assert dialog.checked["Regular"] is False, "expected: dialog.checked['Regular'] is False"


def test_copy_dialog_when_font_replaced_then_click_is_refused(three):
    dialog = three.open("Kerning", "Copy Between Masters", "CopyKerning")
    dialog.set_targets(["Regular"])
    replace_font(three)
    dialog.apply_button.clicked.emit()
    assert "no longer current" in dialog.slot_error, dialog.slot_error
    assert dialog.status.text.startswith("Error:"), "expected: dialog.status.text.startswith('Error:')"
    assert three.notified == [], "a stale dialog must not write"


def test_copy_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Copy Between Masters", "CopyKerning")
    check_clean(dialog)
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.source_master() == "", "no masters means no source"
    assert dialog.targets.texts() == [], "expected: dialog.targets.texts() == []"


def test_copy_module_when_helpers_called_then_plan_and_writer_work(three):
    module = three.load("Kerning", "Copy Between Masters")
    assert module.plan({("A", "V"): 10}, {("A", "V"): 10}, "replace", 100) == {}, "expected: module.plan({('A', 'V'): 10}, {('A', 'V'): 10}, 'replace', 100) == {}"
    module.write_kerning(three.package, {"Bold": {("T", "o"): None}})
    assert ("T", "o") not in three.package.pairs("Bold"), "console writer deletes the pair"
    assert three.notified[0][0] == "Copy Kerning Between Masters", "expected: three.notified[0][0] == 'Copy Kerning Between Masters'"


# ---------------------------------------------------------------- Exceptions Finder
def test_exceptions_dialog_when_opened_then_current_master_exception_is_listed(env):
    dialog = env.open("Kerning", "Exceptions Finder", "ExceptionsFinder")
    check_clean(dialog)
    assert dialog.table.texts() == [
        ["A  V", "Bold", "-70", "@L_A  @R_V", "-90", "+20"],
    ], dialog.table.texts()
    assert dialog.status.text == "0 of 1 ticked", dialog.status.text
    assert "1 exceptions, 0 of them redundant" in dialog.subtitle.text, "expected: '1 exceptions, 0 of them redundant' in dialog.subtitle.text"
    assert not dialog.apply_button.enabled, "nothing ticked means nothing to remove"
    assert not dialog.tick_redundant.enabled, "no redundant exception, no shortcut"


def test_exceptions_dialog_when_all_masters_then_redundant_exception_can_be_removed(env):
    dialog = env.open("Kerning", "Exceptions Finder", "ExceptionsFinder")
    dialog.scope.setCurrentIndex(1)
    check_clean(dialog)
    rows = dialog.table.texts()
    assert len(rows) == 5 and rows[2] == [
        "A  V", "Regular", "-60", "A  @R_V", "-60", "same",
    ], rows
    assert dialog.tick_redundant.enabled, "expected: dialog.tick_redundant.enabled"
    dialog.tick_redundant.clicked.emit()
    assert dialog.status.text == "1 of 5 ticked", dialog.status.text
    assert dialog.ticked() == [dialog.rows[2]], "only the redundant row is ticked"
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    assert ("A", "V") not in env.package.pairs("Regular"), "the exception must be deleted"
    assert ("A", "V") in env.package.pairs("Bold"), "other masters keep their exception"
    assert dialog.status.text == "Removed 1 exceptions", dialog.status.text
    assert len(dialog.table.texts()) == 4, "the refresh must drop the removed row"
    dialog.tick_none.clicked.emit()
    assert dialog.status.text == "0 of 4 ticked" and not dialog.apply_button.enabled, "expected: dialog.status.text == '0 of 4 ticked' and (not dialog.apply_button...."


def test_exceptions_dialog_when_manual_tick_then_non_redundant_exception_is_removed(env):
    dialog = env.open("Kerning", "Exceptions Finder", "ExceptionsFinder")
    dialog.table.item(0, 0).setCheckState(CHECKED)
    assert dialog.status.text == "1 of 1 ticked", "the table check state drives the count"
    assert dialog.apply_button.enabled, "expected: dialog.apply_button.enabled"
    dialog.apply()
    assert ("A", "V") not in env.package.pairs("Bold"), "a ticked override must be deleted"
    assert dialog.table.texts() == [], "no exception remains"
    assert dialog.status.text == "Removed 1 exceptions", "expected: dialog.status.text == 'Removed 1 exceptions'"


def test_exceptions_dialog_when_no_exceptions_then_status_says_so(env):
    env.package.kerning("Bold").stored = {}
    dialog = env.open("Kerning", "Exceptions Finder", "ExceptionsFinder")
    assert dialog.status.text == "No exceptions found", dialog.status.text
    assert dialog.table.texts() == [], "expected: dialog.table.texts() == []"
    assert not dialog.tick_redundant.enabled, "expected: not dialog.tick_redundant.enabled"


def test_exceptions_dialog_when_font_replaced_then_apply_is_refused(env):
    dialog = env.open("Kerning", "Exceptions Finder", "ExceptionsFinder")
    dialog.table.item(0, 0).setCheckState(CHECKED)
    replace_font(env)
    with pytest.raises(ValueError, match="no longer current"):
        dialog.apply()
    assert env.notified == [], "expected: env.notified == []"


def test_exceptions_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Exceptions Finder", "ExceptionsFinder")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.chosen_masters() == [""], "current scope names the empty master"


def test_exceptions_module_when_console_writer_called_then_pair_is_removed(env):
    module = env.load("Kerning", "Exceptions Finder")
    module.write_kerning(env.package, {"Bold": {("A", "V"): None}})
    assert ("A", "V") not in env.package.pairs("Bold"), "expected: ('A', 'V') not in env.package.pairs('Bold')"
    assert env.notified[0][0] == "Kerning Exceptions", "expected: env.notified[0][0] == 'Kerning Exceptions'"


# ---------------------------------------------------------------- Pair Editor
@pytest.fixture
def glyph_a(env):
    """Select glyph A in the Font window."""
    env.scripting.names_selected_names = lambda: ["A"]
    return env


def edit_cell(dialog, left, right, master, text):
    dialog.set_cell(left, right, master, text)


def test_pair_editor_when_opened_then_pairs_with_selected_glyph_are_listed(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    check_clean(dialog)
    assert dialog.order == [
        ("@L_A", "@R_V"), ("@L_A", "V"), ("A", "@R_V"), ("A", "V"), ("V", "A"),
    ], dialog.order
    assert dialog.table.texts()[3] == ["A  V", "-60", "-70"], dialog.table.texts()[3]
    assert dialog.table.texts()[1] == ["@L_A  V", "-40", ""], "absent pairs show blank"
    assert dialog.side.items == ["A  +  partner", "partner  +  A"], "expected: dialog.side.items == ['A + partner', 'partner + A']"
    assert "Pairs with A (@L_A) on either side" in dialog.subtitle.text, "expected: 'Pairs with A (@L_A) on either side' in dialog.subtitle.text"
    assert dialog.status.text == "5 pairs" and not dialog.apply_button.enabled, "expected: dialog.status.text == '5 pairs' and (not dialog.apply_button.enabled)"


def test_pair_editor_when_cells_edited_then_staging_and_feedback_follow(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    edit_cell(dialog, "A", "V", "Bold", "-75")
    check_clean(dialog)
    assert dialog.staged == {(("A", "V"), "Bold"): -75}, dialog.staged
    assert dialog.status.text == "1 edited cell" and dialog.apply_button.enabled, "expected: dialog.status.text == '1 edited cell' and dialog.apply_button.enabled"
    assert dialog.table.item(3, 2).font().bold, "an edited cell is shown in bold"
    edit_cell(dialog, "A", "V", "Bold", "-70")
    assert dialog.staged == {}, "typing the original value unstages the cell"
    edit_cell(dialog, "A", "V", "Regular", "")
    assert dialog.staged == {(("A", "V"), "Regular"): None}, "a blank cell deletes the pair"
    edit_cell(dialog, "A", "V", "Bold", "abc")
    assert dialog.status.text == (
        "“abc” is not a valid kerning value; other valid edits remain staged"
    ), dialog.status.text
    assert dialog.errors == {(("A", "V"), "Bold"): "abc"}, "the invalid text is retained"
    assert dialog.staged == {(("A", "V"), "Regular"): None}, "valid edits stay staged"
    assert dialog.revert_button.enabled, "invalid cells can be reverted"
    dialog.table.item(3, 0).setText("changed")
    assert dialog.table.item(3, 0).text() == "A  V", "the name column is read-only in effect"


def test_pair_editor_when_applied_then_staged_cells_are_written_and_reloaded(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    edit_cell(dialog, "A", "V", "Bold", "-75")
    edit_cell(dialog, "A", "V", "Regular", "")
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    assert glyph_a.package.pairs("Bold")[("A", "V")] == -75, "expected: glyph_a.package.pairs('Bold')['A', 'V'] == -75"
    assert ("A", "V") not in glyph_a.package.pairs("Regular"), "blank cell deleted the pair"
    assert dialog.status.text == "Wrote 2 cells in 2 masters", dialog.status.text
    assert dialog.staged == {} and not dialog.apply_button.enabled, "expected: dialog.staged == {} and (not dialog.apply_button.enabled)"
    assert dialog.table.texts()[3] == ["A  V", "", "-75"], "the reload shows the new values"
    assert glyph_a.updates == 1, "expected: glyph_a.updates == 1"


def test_pair_editor_when_revert_clicked_then_edits_are_discarded(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    edit_cell(dialog, "A", "V", "Bold", "-75")
    dialog.revert_button.clicked.emit()
    assert dialog.staged == {} and dialog.table.texts()[3] == ["A  V", "-60", "-70"], "expected: dialog.staged == {} and dialog.table.texts()[3] == ['A V', '-60', '..."
    assert dialog.status.text == "5 pairs", "expected: dialog.status.text == '5 pairs'"


def test_pair_editor_when_row_added_then_partner_must_exist_on_the_right_side(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    dialog.partner.setText("T")
    dialog.add_button.clicked.emit()
    check_clean(dialog)
    assert dialog.order[-1] == ("A", "T"), "partner follows the selected glyph on side 0"
    assert dialog.partner.text == "", "the partner field is cleared after adding"
    dialog.side.setCurrentIndex(1)
    dialog.partner.setText("T")
    dialog.partner.returnPressed.emit()
    assert dialog.order[-1] == ("T", "A"), "side 1 puts the partner first"
    count = len(dialog.order)
    dialog.partner.setText("T")
    dialog.add_button.clicked.emit()
    assert len(dialog.order) == count, "an existing row is not duplicated"
    dialog.partner.setText("Zzz")
    dialog.add_button.clicked.emit()
    assert dialog.status.text == "No glyph or side-compatible class named “Zzz”", "expected: dialog.status.text == 'No glyph or side-compatible class named “Zzz”'"
    dialog.side.setCurrentIndex(0)
    dialog.partner.setText("@L_A")
    dialog.add_button.clicked.emit()
    assert dialog.status.text == "No glyph or side-compatible class named “@L_A”", (
        "a left class cannot stand on the right side"
    )
    dialog.partner.setText("")
    dialog.add_button.clicked.emit()
    assert len(dialog.order) == count, "an empty partner adds nothing"


def test_pair_editor_when_new_row_cell_typed_then_pair_is_created(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    dialog.partner.setText("T")
    dialog.add_button.clicked.emit()
    edit_cell(dialog, "A", "T", "Bold", "-25")
    dialog.apply()
    check_clean(dialog)
    assert glyph_a.package.pairs("Bold")[("A", "T")] == -25, "new pair is written"
    assert dialog.status.text == "Wrote 1 cells in 1 masters", dialog.status.text


def test_pair_editor_when_no_glyph_selected_then_prompts_for_selection(env):
    env.scripting.names_selected_names = lambda: []
    dialog = env.open("Kerning", "Pair Editor", "PairEditor")
    assert dialog.subtitle.text == (
        "Select a glyph in the Font window, then run this script again."
    ), dialog.subtitle.text
    assert dialog.side.items == ["…  +  partner", "partner  +  …"], "expected: dialog.side.items == ['… + partner', 'partner + …']"
    dialog.partner.setText("T")
    dialog.add_button.clicked.emit()
    assert dialog.order == [], "no glyph means no new rows"


def test_pair_editor_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Pair Editor", "PairEditor")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.glyph is None and dialog.order == [], "expected: dialog.glyph is None and dialog.order == []"


def test_pair_editor_when_font_replaced_then_apply_and_edit_are_refused(glyph_a):
    dialog = glyph_a.open("Kerning", "Pair Editor", "PairEditor")
    edit_cell(dialog, "A", "V", "Bold", "-75")
    replace_font(glyph_a)
    edit_cell(dialog, "A", "V", "Bold", "-60")
    assert "no longer current" in dialog.slot_error, "a stale edit must be refused"
    assert dialog.status.text.startswith("Error:"), dialog.status.text
    dialog.apply_button.clicked.emit()
    assert "stale" in dialog.slot_error, dialog.slot_error
    assert glyph_a.notified == [], "a stale dialog must not write"


def test_pair_editor_module_when_helpers_called_then_glyph_and_writer_work(glyph_a):
    module = glyph_a.load("Kerning", "Pair Editor")
    assert module.current_glyph_name(glyph_a.package) == "A", "expected: module.current_glyph_name(glyph_a.package) == 'A'"
    assert module.current_glyph_name(None) is None, "no font means no glyph"
    module.write_kerning(glyph_a.package, {"Bold": {("T", "o"): None}})
    assert ("T", "o") not in glyph_a.package.pairs("Bold"), "expected: ('T', 'o') not in glyph_a.package.pairs('Bold')"
    assert glyph_a.notified[0][0] == "Kerning Pair Editor", "expected: glyph_a.notified[0][0] == 'Kerning Pair Editor'"


# ---------------------------------------------------------------- Pairs From Text
def test_text_dialog_when_opened_then_adjacent_pairs_show_effective_values(env):
    dialog = env.open("Kerning", "Pairs From Text", "PairsFromText")
    check_clean(dialog)
    assert dialog.pairs == [
        ("A", "V"), ("V", "A"), ("A", "T"), ("T", "A"), ("T", "y"), ("y", "e"),
    ], "unknown letters are skipped, so known neighbours stay adjacent"
    assert dialog.table.texts()[0] == ["A  V", "-60", "-70"], "expected: dialog.table.texts()[0] == ['A V', '-60', '-70']"
    assert dialog.table.texts()[2] == ["A  T", "–", "–"], "absent pairs show a dash"
    assert dialog.status.text == "6 of 6 pairs ticked · 6 values to write", "expected: dialog.status.text == '6 of 6 pairs ticked · 6 values to write'"
    assert "6 pairs from the text" in dialog.subtitle.text, "expected: '6 pairs from the text' in dialog.subtitle.text"


def test_text_dialog_when_class_supplies_value_then_cell_is_marked_class(env):
    dialog = env.open("Kerning", "Pairs From Text", "PairsFromText")
    dialog.text.setText("/Aacute/V")
    check_clean(dialog)
    assert dialog.table.texts() == [["Aacute  V", "0", "-90  class"]], (
        "Regular has an explicit zero; Bold inherits the class pair"
    )
    assert dialog.status.text == "1 of 1 pairs ticked · 1 values to write", "expected: dialog.status.text == '1 of 1 pairs ticked · 1 values to write'"


def test_text_dialog_when_set_mode_applied_then_ticked_pairs_get_the_value(env):
    dialog = env.open("Kerning", "Pairs From Text", "PairsFromText")
    dialog.tick([("A", "V"), ("A", "T")])
    assert dialog.status.text == "2 of 6 pairs ticked · 2 values to write", "expected: dialog.status.text == '2 of 6 pairs ticked · 2 values to write'"
    dialog.value.setValue(-30)
    dialog.apply_button.clicked.emit()
    check_clean(dialog)
    bold = env.package.pairs("Bold")
    assert bold[("A", "V")] == -30 and bold[("A", "T")] == -30, bold
    assert ("V", "A") not in bold, "unticked pairs are left alone"
    assert env.package.pairs("Regular")[("A", "V")] == -60, "Regular is out of scope"
    assert dialog.status.text == "Wrote 2 pair values", dialog.status.text
    assert dialog.ticked() == [("A", "V"), ("A", "T")], "ticks survive the post-apply refresh"
    assert dialog.table.texts()[0] == ["A  V", "-60", "-30"], "expected: dialog.table.texts()[0] == ['A V', '-60', '-30']"


def test_text_dialog_when_add_mode_and_all_masters_then_values_are_added(env):
    dialog = env.open("Kerning", "Pairs From Text", "PairsFromText")
    dialog.tick([("A", "V"), ("A", "T")])
    dialog.mode.setCurrentIndex(1)
    dialog.scope.setCurrentIndex(1)
    dialog.value.setValue(5)
    assert dialog.status.text == "2 of 6 pairs ticked · 4 values to write", "expected: dialog.status.text == '2 of 6 pairs ticked · 4 values to write'"
    dialog.apply()
    check_clean(dialog)
    assert env.package.pairs("Regular")[("A", "V")] == -55, "expected: env.package.pairs('Regular')['A', 'V'] == -55"
    assert env.package.pairs("Bold")[("A", "V")] == -65, "expected: env.package.pairs('Bold')['A', 'V'] == -65"
    assert env.package.pairs("Bold")[("A", "T")] == 5, "an absent pair adds to zero"


def test_text_dialog_when_nothing_ticked_then_apply_is_disabled(env):
    dialog = env.open("Kerning", "Pairs From Text", "PairsFromText")
    dialog.tick([])
    assert dialog.status.text == "0 of 6 pairs ticked · 0 values to write", "expected: dialog.status.text == '0 of 6 pairs ticked · 0 values to write'"
    assert not dialog.apply_button.enabled, "expected: not dialog.apply_button.enabled"
    dialog.text.setText("A")
    assert dialog.pairs == [] and dialog.status.text == "0 of 0 pairs ticked · 0 values to write", "expected: dialog.pairs == [] and dialog.status.text == '0 of 0 pairs ticked ·..."


def test_text_dialog_when_font_replaced_then_apply_click_is_contained(env):
    dialog = env.open("Kerning", "Pairs From Text", "PairsFromText")
    replace_font(env)
    dialog.apply_button.clicked.emit()
    assert "no longer current" in dialog.slot_error, dialog.slot_error
    assert env.notified == [], "expected: env.notified == []"


def test_text_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Pairs From Text", "PairsFromText")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.pairs == [], "expected: dialog.pairs == []"


def test_text_module_when_console_writer_called_then_pair_is_removed(env):
    module = env.load("Kerning", "Pairs From Text")
    module.write_kerning(env.package, {"Bold": {("T", "o"): None}})
    assert ("T", "o") not in env.package.pairs("Bold"), "expected: ('T', 'o') not in env.package.pairs('Bold')"
    assert env.notified[0][0] == "Kerning Pairs from Text", "expected: env.notified[0][0] == 'Kerning Pairs from Text'"


@pytest.mark.parametrize(
    ("title", "cls"),
    [
        ("Copy Between Masters", "CopyKerning"),
        ("Exceptions Finder", "ExceptionsFinder"),
        ("Pair Editor", "PairEditor"),
        ("Pairs From Text", "PairsFromText"),
    ],
)
def test_editors_when_closed_then_registry_and_slots_are_released(env, title, cls):
    module = env.load("Kerning", title)
    dialog = module.main()
    assert sys._fontlab_samples[module.KEY] is dialog, "expected: sys._fontlab_samples[module.KEY] is dialog"
    dialog.close_button.clicked.emit()
    assert sys._fontlab_samples == {} and dialog.deleted, "Close releases and deletes"
    assert dialog._connections == [], "Close disconnects every owned slot"


@pytest.mark.parametrize(
    "title",
    ["Copy Between Masters", "Exceptions Finder", "Pair Editor", "Pairs From Text"],
)
def test_editors_when_run_as_script_then_main_opens_the_dialog(env, title):
    namespace = runpy.run_path(
        str(ROOT / "Scripts/Kerning" / f"{title}.py"), run_name="__main__"
    )
    assert namespace["KEY"] in sys._fontlab_samples, "running as a script opens the dialog"
