# this_file: tests/test_cov_b_kerning_editors.py
"""Drive Copy Between Masters, Exceptions Finder, Pair Editor and Pairs From Text."""

import runpy
import sys

import pytest
from _wp03_studio_support import studio_host as _studio_host
from PySide6.QtCore import Qt
import _wp03_proof as proof_contract
import _wp03_browser as browser_contract

from _wp03_proof import texts, tick, replace  # noqa: F401
from _cov_b_support import ROOT, Env, Package, make_package

browser_env = browser_contract.browser_env
proof_env = proof_contract.proof_env


CHECKED, UNCHECKED = Qt.Checked, Qt.Unchecked


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


def check_texts(table):
    return [[table.text(row, column) for column in range(table.view.columnCount())]
            for row in range(table.view.rowCount())]


def check_item(table, source_row, column):
    return next(table.view.item(row, column) for row in range(table.view.rowCount())
                if table.view.item(row, 0).data(Qt.UserRole) == source_row)


def replace_font(state):
    other = Package(["Regular"], {"Regular": make_package().kerning("Regular")}, {})
    other.id = 99
    state.package = other


def test_copy_dialog_when_opened_then_lists_other_masters_unticked(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert [dialog.source.itemText(i) for i in range(dialog.source.count())] == ["Regular", "Bold", "Light"], "source offers all masters"
    assert dialog.source.currentIndex() == 1, "the current master is the default source"
    assert check_texts(dialog.targets) == [
        ["Regular", "8", "", "", ""],
        ["Light", "4", "", "", ""],
    ], "the source master is never its own target"
    assert dialog.subtitle.text() == "Bold has 4 pairs. Tick the masters that receive them.", "expected: dialog.subtitle.text() == 'Bold has 4 pairs. Tick the masters that re..."
    assert dialog.count.text() == "Tick at least one target master", dialog.count.text()
    assert not dialog.apply_button.isEnabled(), "nothing ticked means nothing to copy"


def test_copy_dialog_when_target_ticked_then_preview_counts_added_changed_removed(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    check_item(dialog.targets,0, 0).setCheckState(CHECKED)
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert check_texts(dialog.targets)[0] == ["Regular", "8", "0", "4", "4"], (
        "Bold's four pairs overwrite four Regular values and delete four others"
    )
    assert dialog.chosen_targets() == ["Regular"], "expected: dialog.chosen_targets() == ['Regular']"
    assert dialog.count.text() == "8 pair edits in 1 master", dialog.count.text()
    assert dialog.apply_button.isEnabled(), "expected: dialog.apply_button.isEnabled()"
    dialog.mode.setCurrentIndex(1)
    assert dialog.mode_key() == "missing", "expected: dialog.mode_key() == 'missing'"
    assert check_texts(dialog.targets)[0] == ["Regular", "8", "0", "0", "0"], (
        "add-missing leaves existing pairs alone"
    )
    assert dialog.count.text() == "0 pair edits in 1 master", "expected: dialog.count.text() == '0 pair edits in 1 master'"
    assert not dialog.apply_button.isEnabled(), "zero edits must not enable Apply"
    dialog.mode.setCurrentIndex(2)
    assert check_texts(dialog.targets)[0] == ["Regular", "8", "0", "4", "0"], (
        "matching mode overwrites but never deletes"
    )


def test_copy_dialog_when_applied_then_target_receives_scaled_source_pairs(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    dialog.set_targets(["Regular", "Light"])
    dialog.percent.setValue(50)
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    dialog.apply_button.click()
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert three.package.pairs("Regular") == {
        ("@L_A", "@R_V"): -45,
        ("A", "V"): -35,
        ("T", "V"): 5,
        ("T", "o"): -2,
    }, "Regular must now hold half of Bold, with the extra pairs removed"
    assert three.package.pairs("Light") == three.package.pairs("Regular"), "expected: three.package.pairs('Light') == three.package.pairs('Regular')"
    assert three.package.pairs("Bold")[("A", "V")] == -70, "the source must not change"
    assert dialog.tool.status == "Copied: Regular +0 ~4 −4 · Light +0 ~4 −0", dialog.count.text()
    assert three.updates == 0, "expected: three.updates == 0"


def test_copy_dialog_when_source_changes_then_rows_rebuild_and_ticks_survive(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    dialog.set_targets(["Light"])
    assert check_item(dialog.targets,1, 0).checkState() == CHECKED, "expected: check_item(dialog.targets,1, 0).checkState() == CHECKED"
    dialog.source.setCurrentIndex(0)
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert [row[0] for row in check_texts(dialog.targets)] == ["Bold", "Light"], "expected: [row[0] for row in check_texts(dialog.targets)] == ['Bold', 'Light']"
    assert dialog.chosen_targets() == ["Light"], "a tick on Light survives a source change"
    assert dialog.source_master() == "Regular", "expected: dialog.source_master() == 'Regular'"
    check_item(dialog.targets,0, 1).setText("ignored")
    assert dialog.chosen_targets() == ["Light"], "only the name column toggles a master"


def test_copy_dialog_when_target_unticked_then_status_asks_for_a_target(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    check_item(dialog.targets,0, 0).setCheckState(CHECKED)
    check_item(dialog.targets,0, 0).setCheckState(UNCHECKED)
    assert dialog.count.text() == "Tick at least one target master", dialog.count.text()
    assert dialog.checked["Regular"] is False, "expected: dialog.checked['Regular'] is False"


def test_copy_dialog_when_font_replaced_then_click_is_refused(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    dialog.set_targets(["Regular"])
    replace_font(three)
    dialog.apply_button.click()
    assert "no longer current" in dialog.tool.status, dialog.tool.status
    assert three.notified == [], "a stale dialog must not write"


def test_copy_dialog_when_no_font_then_open_font_first(studio_host):
    no_font = studio_host
    dialog = no_font.open().panels["CopyPanel"]
    assert not dialog.tool.status.startswith("Kerning Batch:"), dialog.tool.status
    assert dialog.subtitle.text() == "Open a font first.", dialog.subtitle.text()
    assert dialog.source_master() == "", "no masters means no source"
    assert check_texts(dialog.targets) == [], "expected: check_texts(dialog.targets) == []"


def test_copy_module_when_helpers_called_then_plan_and_writer_work(studio_host):
    three = studio_host
    three.package = make_package(("Regular", "Bold", "Light"))
    three.package.master = "Bold"
    dialog = three.open().panels["CopyPanel"]
    module = dialog.tool.backends().edit
    assert module.copy_plan({("A", "V"): 10}, {("A", "V"): 10}, "replace", 100) == {}, "expected: module.copy_plan({('A', 'V'): 10}, {('A', 'V'): 10}, 'replace', 100) == {}"
    dialog.tool.write("Copy", "kerning", {"Bold": {("T", "o"): None}}, dialog.snapshot)
    assert ("T", "o") not in three.package.pairs("Bold"), "console writer deletes the pair"
    assert three.notified[0][0] == "Kerning Batch: Copy kerning", "expected: three.notified[0][0] == 'Copy Kerning Between Masters'"


@pytest.mark.parametrize("change", ["font", "closed", "pairs", "classes", "masters"])
def test_copy_apply_refuses_complete_stale_snapshot(studio_host, change):
    studio_host.package = package = make_package()
    dialog = studio_host.open().panels["CopyPanel"]
    dialog.set_targets(["Regular"])
    if change == "font":
        replace_font(studio_host)
    elif change == "closed":
        studio_host.package = None
    elif change == "pairs":
        package.kerning("Bold").stored.clear()
    elif change == "classes":
        package.kerning("Bold").groups["L_A"] = (["T"], "KernLeft")
    else:
        package.masters.reverse()
    dialog.apply_button.click()
    assert "stale" in dialog.tool.status or "current" in dialog.tool.status
    assert dialog.edits == {} and dialog.snapshot is None
    assert not dialog.apply_button.isEnabled() and studio_host.notified == []



# ---------------------------------------------------------------- Exceptions Finder
def test_exceptions_dialog_when_opened_then_current_master_exception_is_listed(browser_env):
    dialog = browser_env.open("Exceptions Finder")
    browser_contract.clean(dialog)
    assert browser_contract.texts(dialog.grid) == [
        ["A  V", "Bold", "-70", "@L_A  @R_V", "-90", "+20"],
    ], browser_contract.texts(dialog.grid)
    assert dialog.tool.status == "0 of 1 ticked", dialog.tool.status
    assert "1 exceptions, 0 of them redundant" in dialog.subtitle.text(), "expected: '1 exceptions, 0 of them redundant' in dialog.subtitle.text()"
    assert not dialog.apply_button.isEnabled(), "nothing ticked means nothing to remove"
    assert not dialog.tick_redundant.isEnabled(), "no redundant exception, no shortcut"


def test_exceptions_dialog_when_all_masters_then_redundant_exception_can_be_removed(browser_env):
    dialog = browser_env.open("Exceptions Finder")
    dialog.scope.setCurrentIndex(1)
    browser_contract.clean(dialog)
    rows = browser_contract.texts(dialog.grid)
    assert len(rows) == 5 and rows[2] == [
        "A  V", "Regular", "-60", "A  @R_V", "-60", "same",
    ], rows
    assert dialog.tick_redundant.isEnabled(), "expected: dialog.tick_redundant.isEnabled()"
    dialog.tick_redundant.clicked.emit()
    assert dialog.tool.status == "1 of 5 ticked", dialog.tool.status
    assert dialog.ticked() == [dialog.rows[2]], "only the redundant row is ticked"
    dialog.apply_button.clicked.emit()
    browser_contract.clean(dialog)
    assert ("A", "V") not in browser_env.package.pairs("Regular"), "the exception must be deleted"
    assert ("A", "V") in browser_env.package.pairs("Bold"), "other masters keep their exception"
    assert dialog.tool.status == "Removed 1 exceptions", dialog.tool.status
    assert len(browser_contract.texts(dialog.grid)) == 4, "the refresh must drop the removed row"
    browser_contract.button(dialog, "Untick all").click()
    assert dialog.tool.status == "0 of 4 ticked" and not dialog.apply_button.isEnabled(), "expected: dialog.tool.status == '0 of 4 ticked' and (not dialog.apply_button...."


def test_exceptions_dialog_when_manual_tick_then_non_redundant_exception_is_removed(browser_env):
    dialog = browser_env.open("Exceptions Finder")
    dialog.grid.view.item(0, 0).setCheckState(browser_contract.checked())
    assert dialog.tool.status == "1 of 1 ticked", "the table check state drives the count"
    assert dialog.apply_button.isEnabled(), "expected: dialog.apply_button.isEnabled()"
    dialog.apply()
    assert ("A", "V") not in browser_env.package.pairs("Bold"), "a ticked override must be deleted"
    assert browser_contract.texts(dialog.grid) == [], "no exception remains"
    assert dialog.tool.status == "Removed 1 exceptions", "expected: dialog.tool.status == 'Removed 1 exceptions'"


def test_exceptions_dialog_when_no_exceptions_then_status_says_so(browser_env):
    browser_env.package.kerning("Bold").stored = {}
    dialog = browser_env.open("Exceptions Finder")
    assert dialog.tool.status == "No exceptions found", dialog.tool.status
    assert browser_contract.texts(dialog.grid) == [], "expected: browser_contract.texts(dialog.grid) == []"
    assert not dialog.tick_redundant.isEnabled(), "expected: not dialog.tick_redundant.isEnabled()"


def test_exceptions_dialog_when_font_replaced_then_apply_is_refused(browser_env):
    dialog = browser_env.open("Exceptions Finder")
    dialog.grid.view.item(0, 0).setCheckState(browser_contract.checked())
    replace_font(browser_env)
    assert not dialog.apply()
    assert "no longer current" in dialog.tool.status
    assert browser_env.notified == [], "expected: browser_env.notified == []"


def test_exceptions_dialog_when_no_font_then_open_font_first(browser_env):
    dialog = browser_env.open("Exceptions Finder", no_font=True)
    assert dialog.subtitle.text() == "Open a font first.", dialog.subtitle.text()
    assert dialog.tool.scope(False) == [], "current scope names the empty master"


def test_exceptions_module_when_console_writer_called_then_pair_is_removed(browser_env):
    module = browser_env.load("Exceptions Finder")
    module.write_kerning(browser_env.package, {"Bold": {("A", "V"): None}})
    assert ("A", "V") not in browser_env.package.pairs("Bold"), "expected: ('A', 'V') not in browser_env.package.pairs('Bold')"
    assert browser_env.notified[0][0] == "Kerning Exceptions", "expected: browser_env.notified[0][0] == 'Kerning Exceptions'"


# ---------------------------------------------------------------- Pair Editor
# Original Pair Editor assertions now use real consolidated widgets and shell callbacks.
studio_host = _studio_host
import _wp03_pair_editor as pair_support  # noqa: E402

pair_env = pair_support.pair_env
pair_texts = pair_support.texts
replace_pair = pair_support.replace


def edit_cell(dialog, left, right, master, text):
    dialog.set_cell(left, right, master, text)


def test_pair_editor_when_opened_then_pairs_with_selected_glyph_are_listed(pair_env):
    dialog = pair_env.open()
    assert dialog.order == [
        ("@L_A", "@R_V"), ("@L_A", "V"), ("A", "@R_V"), ("A", "V"), ("V", "A"),
    ], dialog.order
    assert pair_texts(dialog)[3] == ["A  V", "-60", "-70"]
    assert pair_texts(dialog)[1] == ["@L_A  V", "-40", ""], "absent pairs show blank"
    assert [dialog.side.itemText(i) for i in range(dialog.side.count())] == ["A  +  partner", "partner  +  A"]
    assert "Pairs with A (@L_A) on either side" in dialog.subtitle.text()
    assert pair_env.shell.status.text() == "5 pairs" and not dialog.ready()
    assert pair_env.state.notified == []


def test_pair_editor_when_cells_edited_then_staging_and_feedback_follow(pair_env):
    dialog = pair_env.open()
    edit_cell(dialog, "A", "V", "Bold", "-75")
    assert dialog.staged == {(("A", "V"), "Bold"): -75}
    assert pair_env.shell.status.text() == "1 edited cell" and dialog.ready()
    assert dialog.table.item(3, 2).font().bold(), "an edited cell is shown in bold"
    edit_cell(dialog, "A", "V", "Bold", "-70")
    assert dialog.staged == {}, "typing the original value unstages the cell"
    edit_cell(dialog, "A", "V", "Regular", "")
    assert dialog.staged == {(("A", "V"), "Regular"): None}
    edit_cell(dialog, "A", "V", "Bold", "abc")
    assert pair_env.shell.status.text() == "“abc” is not a valid kerning value; other valid edits remain staged"
    assert dialog.errors == {(("A", "V"), "Bold"): "abc"}
    assert dialog.staged == {(("A", "V"), "Regular"): None}
    assert dialog.revert_button.isEnabled()
    dialog.table.item(3, 0).setText("changed")
    assert dialog.table.item(3, 0).text() == "A  V", "the name column is read-only in effect"


def test_pair_editor_when_applied_then_staged_cells_are_written_and_reloaded(pair_env):
    dialog = pair_env.open()
    edit_cell(dialog, "A", "V", "Bold", "-75")
    edit_cell(dialog, "A", "V", "Regular", "")
    pair_env.shell.apply_button.click()
    assert pair_env.state.package.pairs("Bold")[("A", "V")] == -75
    assert ("A", "V") not in pair_env.state.package.pairs("Regular")
    assert pair_env.shell.status.text() == "Wrote 2 cells in 2 masters"
    assert dialog.staged == {} and not dialog.ready()
    assert pair_texts(dialog)[3] == ["A  V", "", "-75"]
    assert pair_env.state.updates == 0, "Use the captured preview refresh instead of global UpdateAll"
    assert len(pair_env.state.notified) == 2, "one complete Undo batch"


def test_pair_editor_when_revert_clicked_then_edits_are_discarded(pair_env):
    dialog = pair_env.open()
    edit_cell(dialog, "A", "V", "Bold", "-75")
    dialog.revert_button.click()
    assert dialog.staged == {} and pair_texts(dialog)[3] == ["A  V", "-60", "-70"]
    assert pair_env.shell.status.text() == "5 pairs"


def test_pair_editor_when_row_added_then_partner_must_exist_on_the_right_side(pair_env):
    dialog = pair_env.open()
    dialog.partner.setText("T")
    dialog.add_button.click()
    assert dialog.order[-1] == ("A", "T")
    assert dialog.partner.text() == ""
    dialog.side.setCurrentIndex(1)
    dialog.partner.setText("T")
    dialog.partner.returnPressed.emit()
    assert dialog.order[-1] == ("T", "A")
    count = len(dialog.order)
    dialog.partner.setText("T")
    dialog.add_button.click()
    assert len(dialog.order) == count
    dialog.partner.setText("Zzz")
    dialog.add_button.click()
    assert pair_env.shell.status.text() == "No glyph or side-compatible class named “Zzz”"
    dialog.side.setCurrentIndex(0)
    dialog.partner.setText("@L_A")
    dialog.add_button.click()
    assert pair_env.shell.status.text() == "No glyph or side-compatible class named “@L_A”"
    dialog.partner.setText("")
    dialog.add_button.click()
    assert len(dialog.order) == count


def test_pair_editor_when_new_row_cell_typed_then_pair_is_created(pair_env):
    dialog = pair_env.open()
    dialog.partner.setText("T")
    dialog.add_button.click()
    edit_cell(dialog, "A", "T", "Bold", "-25")
    pair_env.shell.apply_button.click()
    assert pair_env.state.package.pairs("Bold")[("A", "T")] == -25
    assert pair_env.shell.status.text() == "Wrote 1 cells in 1 masters"


def test_pair_editor_when_no_glyph_selected_then_prompts_for_selection(pair_env):
    pair_env.selection.clear()
    dialog = pair_env.open()
    assert dialog.subtitle.text() == "Select a glyph in the Font window, then run this script again."
    assert [dialog.side.itemText(i) for i in range(dialog.side.count())] == ["…  +  partner", "partner  +  …"]
    dialog.partner.setText("T")
    dialog.add_button.click()
    assert dialog.order == []


def test_pair_editor_when_no_font_then_open_font_first(pair_env):
    dialog = pair_env.open(no_font=True)
    assert dialog.subtitle.text() == "Open a font first."
    assert dialog.glyph is None and dialog.order == []


def test_pair_editor_when_font_replaced_then_apply_and_edit_are_refused(pair_env):
    dialog = pair_env.open()
    edit_cell(dialog, "A", "V", "Bold", "-75")
    replace_pair(pair_env)
    edit_cell(dialog, "A", "V", "Bold", "-60")
    assert "no longer current" in dialog.slot_error
    assert pair_env.shell.status.text().startswith("Error:")
    pair_env.shell.apply_button.click()
    assert not dialog.ready() and not dialog.staged
    assert pair_env.state.notified == []


def test_pair_editor_module_when_helpers_called_then_glyph_and_writer_work(pair_env):
    from fontlabapp.studios.kerning_studio import pairs as module
    assert module.current_glyph_name(pair_env.state.package) == "A"
    assert module.current_glyph_name(None) is None
    module.write_kerning(pair_env.state.package, {"Bold": {("T", "o"): None}})
    assert ("T", "o") not in pair_env.state.package.pairs("Bold")
    assert pair_env.state.notified[0][0] == "Kerning Pair Editor"


# ---------------------------------------------------------------- Pairs From Text
# These original behavior assertions now drive the real consolidated App tab.
def test_text_dialog_when_opened_then_adjacent_pairs_show_effective_values(proof_env):
    panel = proof_env.open("Pairs From Text")
    assert panel.pairs == [("A", "V"), ("V", "A"), ("A", "T"), ("T", "A"), ("T", "y"), ("y", "e")]
    assert texts(panel.grid)[0] == ["A  V", "-60", "-70"]
    assert texts(panel.grid)[2] == ["A  T", "–", "–"]
    assert panel.count_label.text() == "6 of 6 pairs ticked · 6 values to write"
    assert "6 pairs from the text" in panel.subtitle.text()


def test_text_dialog_when_class_supplies_value_then_cell_is_marked_class(proof_env):
    panel = proof_env.open("Pairs From Text")
    panel.text.setText("/Aacute/V")
    panel.refresh()
    assert texts(panel.grid) == [["Aacute  V", "0", "-90  class"]]
    assert panel.count_label.text() == "1 of 1 pairs ticked · 1 values to write"


def test_text_dialog_when_set_mode_applied_then_ticked_pairs_get_the_value(proof_env):
    panel = proof_env.open("Pairs From Text")
    tick(panel, [("A", "V"), ("A", "T")])
    assert panel.count_label.text() == "2 of 6 pairs ticked · 2 values to write"
    panel.value.setValue(-30)
    panel.preview_changes()
    proof_env.shell.apply_button.click()
    bold = proof_env.package.pairs("Bold")
    assert bold[("A", "V")] == -30 and bold[("A", "T")] == -30
    assert ("V", "A") not in bold
    assert proof_env.package.pairs("Regular")[("A", "V")] == -60
    assert proof_env.shell.status.text() == "Wrote 2 pair values"
    assert panel.ticked() == [("A", "V"), ("A", "T")]
    assert texts(panel.grid)[0] == ["A  V", "-60", "-30"]


def test_text_dialog_when_add_mode_and_all_masters_then_values_are_added(proof_env):
    panel = proof_env.open("Pairs From Text")
    tick(panel, [("A", "V"), ("A", "T")])
    panel.mode.setCurrentIndex(1)
    panel.scope.setCurrentIndex(1)
    panel.value.setValue(5)
    assert panel.count_label.text() == "2 of 6 pairs ticked · 4 values to write"
    panel.preview_changes()
    panel.apply()
    assert proof_env.package.pairs("Regular")[("A", "V")] == -55
    assert proof_env.package.pairs("Bold")[("A", "V")] == -65
    assert proof_env.package.pairs("Bold")[("A", "T")] == 5


def test_text_dialog_when_nothing_ticked_then_apply_is_disabled(proof_env):
    panel = proof_env.open("Pairs From Text")
    tick(panel, [])
    assert panel.count_label.text() == "0 of 6 pairs ticked · 0 values to write"
    panel.preview_changes()
    assert not panel.ready()
    proof_env.shell.apply_button.click()
    assert not proof_env.notified
    panel.text.setText("A")
    panel.refresh()
    assert panel.pairs == [] and panel.count_label.text() == "0 of 0 pairs ticked · 0 values to write"


def test_text_dialog_when_font_replaced_then_apply_click_is_contained(proof_env):
    panel = proof_env.open("Pairs From Text")
    panel.preview_changes()
    replace(proof_env)
    proof_env.shell.apply_button.click()
    assert "current" in proof_env.shell.status.text() or "stale" in proof_env.shell.status.text()
    assert not proof_env.notified


def test_text_dialog_when_no_font_then_open_font_first(proof_env):
    panel = proof_env.open("Pairs From Text", no_font=True)
    assert panel.subtitle.text() == "Open a font first." and panel.pairs == []


def test_text_module_when_console_writer_called_then_pair_is_removed(proof_env):
    proof_env.pairs.write_kerning(proof_env.package, {"Bold": {("T", "o"): None}})
    assert ("T", "o") not in proof_env.package.pairs("Bold")
    assert proof_env.notified[0][0] == "Kerning Pairs from Text"


@pytest.mark.parametrize(
    ("title", "cls"),
    [
        ("Copy Between Masters", "CopyKerning"),
        ("Exceptions Finder", "ExceptionsFinder"),
        ("Pair Editor", "PairEditor"),
        ("Pairs From Text", "PairsFromText"),
    ],
)
def test_editors_when_closed_then_registry_and_slots_are_released(env, title, cls, request):
    if title == "Pairs From Text":
        return proof_contract.close_owner(request.getfixturevalue("proof_env"), title)
    if title == "Copy Between Masters":
        host = request.getfixturevalue("studio_host")
        host.package = make_package()
        shell = host.open().shell
        shell.close_button.click()
        assert shell._close_complete and shell._delete_scheduled and not shell.widget.isVisible()
        assert not shell.connections
        return
    if title == "Pair Editor":
        return pair_support.close_owner(request.getfixturevalue("pair_env"))
    browser_contract.close_owner(request.getfixturevalue("browser_env"), title)


@pytest.mark.parametrize(
    "title",
    ["Copy Between Masters", "Exceptions Finder", "Pair Editor", "Pairs From Text"],
)
def test_editors_when_run_as_script_then_main_opens_the_dialog(env, title, request):
    if title == "Pairs From Text":
        return proof_contract.launch(request.getfixturevalue("proof_env"))
    if title in {"Copy Between Masters", "Pair Editor"}:
        from types import SimpleNamespace
        module = "kerning_batch" if title == "Copy Between Masters" else "kerning_studio"
        target = "Kerning Batch" if title == "Copy Between Masters" else "Kerning Studio"
        calls = []
        with pytest.MonkeyPatch.context() as patch:
            patch.setitem(sys.modules, "fly.ap.studios." + module,
                          SimpleNamespace(show=lambda **kwargs: calls.append(kwargs)))
            runpy.run_path(str(ROOT / "Scripts/Kerning" / f"{target}.py"), run_name="__main__")
        assert calls == [{"consolidated": True}]
        return
    browser_contract.launch(request.getfixturevalue("browser_env"))
