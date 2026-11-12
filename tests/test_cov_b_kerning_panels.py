# this_file: tests/test_cov_b_kerning_panels.py
"""Drive the five read-only kerning panels through their real dialogs."""


import pytest
import _wp03_proof as proof_contract
import _wp03_browser as browser_contract
from _wp03_studio_support import studio_host  # noqa: F401

from _wp03_proof import replace  # noqa: F401
from _cov_b_support import Env, Package, make_package


browser_env = browser_contract.browser_env
proof_env = proof_contract.proof_env


@pytest.fixture
def env(monkeypatch, real_app, app_sources):
    """Two masters, Bold current."""
    return Env(monkeypatch, real_app, make_package())


@pytest.fixture
def no_font(monkeypatch, real_app, app_sources):
    """No font open."""
    return Env(monkeypatch, real_app, None)


def replace_font(env):
    """Swap in a different current font, as if the user switched documents."""
    other = Package(["Regular"], {"Regular": make_package().kerning("Regular")}, {})
    other.id = 99
    env.package = other


def clipboard(env):
    return env.qt.QtGui.QApplication.clipboard()


# ---------------------------------------------------------------- Classes Browser
def test_classes_dialog_when_opened_then_every_class_is_listed_with_side_and_size(browser_env):
    dialog = browser_env.open("Classes Browser")
    browser_contract.clean(dialog)
    assert browser_contract.items(dialog.list) == [
        "@Both   both · 1",
        "@L_A   left · 2",
        "@R_V   right · 1",
    ], browser_contract.items(dialog.list)
    assert dialog.subtitle.text() == (
        "3 classes: 1 left, 1 right, 1 both sides. Values are shown for all 2 masters."
    ), dialog.subtitle.text()
    assert dialog.tool.status == "@Both: 1 members, used in 0 pairs", dialog.tool.status
    assert dialog.title.text() == "@Both · both side", "expected: dialog.title.text() == '@Both · both side'"


def test_classes_dialog_when_class_chosen_then_pairs_show_values_per_master(browser_env):
    dialog = browser_env.open("Classes Browser")
    dialog.select_class("L_A")
    browser_contract.clean(dialog)
    assert dialog.title.text() == "@L_A · left side", "expected: dialog.title.text() == '@L_A · left side'"
    assert dialog.members.text() == "A Aacute", dialog.members.text()
    assert browser_contract.texts(dialog.pairs) == [
        ["@L_A  @R_V", "-80", "-90"],
        ["@L_A  V", "-40", "–"],
    ], "a master without the pair shows a dash"
    assert dialog.tool.status == "@L_A: 2 members, used in 2 pairs", dialog.tool.status
    assert {" ".join(pair): values for pair, values in browser_env.load("Classes Browser").pairs_using(browser_env.package, browser_env.tool.masters, "L_A").items()} == {"@L_A @R_V": {"Regular": -80, "Bold": -90},
                                "@L_A V": {"Regular": -40}}, "expected: dialog.pair_rows == {'@L_A @R_V': {'Regular': -80, 'Bold': -90}, '@..."
    assert dialog.select_button.isEnabled(), "expected: dialog.select_button.isEnabled()"


def test_classes_dialog_when_filtered_then_name_or_exact_member_matches(browser_env):
    dialog = browser_env.open("Classes Browser")
    dialog.filter.setText("aacute")
    assert browser_contract.items(dialog.list) == [], "member names are case-sensitive"
    assert dialog.tool.status == "0 of 3 classes", dialog.tool.status
    assert dialog.title.text() == "No class" and not dialog.select_button.isEnabled(), "expected: dialog.title.text() == 'No class' and (not dialog.select_button.isEnabled())"
    dialog.filter.setText("Aacute")
    assert browser_contract.items(dialog.list) == ["@L_A   left · 2"], browser_contract.items(dialog.list)
    assert dialog.selected == "L_A", "the first match is shown automatically"
    dialog.filter.setText("r_")
    assert browser_contract.items(dialog.list) == ["@R_V   right · 1"], "class names match in any case"


def test_classes_dialog_when_select_members_clicked_then_font_selection_changes(browser_env):
    dialog = browser_env.open("Classes Browser")
    dialog.select_class("L_A")
    dialog.select_button.clicked.emit()
    browser_contract.clean(dialog)
    names = [glyph.name for glyph in browser_env.glyph_list]
    assert browser_env.selected == {names.index("A"), names.index("Aacute")}, browser_env.selected
    assert dialog.tool.status == "Selected 2 glyphs of @L_A in the Font window", "expected: dialog.tool.status == 'Selected 2 glyphs of @L_A in the Font window'"
    assert browser_env.updates == 0, "selection makes no UpdateAll call: it queues glyph ids (fl#8537)"


def test_classes_dialog_when_nothing_chosen_then_select_members_does_nothing(browser_env):
    dialog = browser_env.open("Classes Browser")
    dialog.filter.setText("zzz")
    dialog.select_members()
    assert browser_env.selected == set(), "no class means no selection change"


def test_classes_dialog_when_font_replaced_then_selection_is_refused(browser_env):
    dialog = browser_env.open("Classes Browser")
    dialog.select_class("L_A")
    replace_font(browser_env)
    dialog.select_button.clicked.emit()
    assert "no longer current" in dialog.tool.status, dialog.tool.status
    assert browser_env.selected == set(), "a stale panel must not touch the selection"
    assert dialog.classes == {} and not dialog.select_button.isEnabled(), "expected: dialog.classes == {} and (not dialog.select_button.isEnabled())"


def test_classes_dialog_when_no_font_then_open_font_first(browser_env):
    dialog = browser_env.open("Classes Browser", no_font=True)
    browser_contract.clean(dialog)
    assert dialog.subtitle.text() == "Open a font first.", dialog.subtitle.text()
    assert browser_contract.items(dialog.list) == [] and dialog.classes == {}, "expected: browser_contract.items(dialog.list) == [] and dialog.classes == {}"


def test_classes_module_when_helpers_called_then_class_use_is_collected(browser_env):
    module = browser_env.load("Classes Browser")
    rows = module.pairs_using(browser_env.package, ["Regular", "Bold"], "R_V")
    assert rows[("A", "@R_V")] == {"Regular": -60}, rows
    assert module.matches("L_A", ["A"], "  "), "blank text matches everything"
    assert module.matches("L_A", ["A"], "A"), "an exact member matches"


# ---------------------------------------------------------------- Compare Masters
def test_compare_dialog_when_opened_then_all_pairs_show_values_and_flags(browser_env):
    dialog = browser_env.open("Compare Masters")
    browser_contract.clean(dialog)
    rows = browser_contract.texts(dialog.grid)
    assert len(rows) == 8, rows
    assert rows[0] == ["@L_A  @R_V", "-80", "-90", ""], "close values carry no flag"
    assert ["T  o", "3", "-3", "sign"] in rows, "a sign change is flagged"
    assert ["V  A", "-4", "–", "missing"] in rows, "a pair absent on one master is flagged"
    assert dialog.tool.status == "8 rows shown · 5 of 8 pairs flagged", dialog.tool.status
    assert dialog.subtitle.text().startswith("8 pairs across 2 masters."), dialog.subtitle.text()
    assert dialog.grid.columnCount() == 4, "expected: dialog.grid.columnCount() == 4"


def test_compare_dialog_when_filtering_then_search_threshold_and_flag_options_apply(browser_env):
    dialog = browser_env.open("Compare Masters")
    dialog.only_flagged.setChecked(True)
    assert len(dialog.shown) == 5 and dialog.tool.status.startswith("5 rows shown"), "expected: len(dialog.shown) == 5 and dialog.tool.status.startswith('5 rows sh..."
    dialog.search.setText("@L_")
    assert [pair for pair, *_ in dialog.shown] == [("@L_A", "V")], dialog.shown
    dialog.search.setText("")
    dialog.only_flagged.setChecked(False)
    dialog.threshold.setValue(5)
    rows = {row[0]: row[3] for row in browser_contract.texts(dialog.grid)}
    assert rows["T  o"] == "sign, jump", "both reasons are listed"
    assert rows["A  V"] == "jump", "a 10 unit gap exceeds a threshold of 5"
    assert dialog.tool.status == "8 rows shown · 7 of 8 pairs flagged", dialog.tool.status


def test_compare_dialog_when_reload_clicked_then_new_kerning_is_read(browser_env):
    dialog = browser_env.open("Compare Masters")
    browser_env.package.kerning("Bold").stored[(("Z", "glyphMode"), ("Z", "glyphMode"))] = 7
    browser_env.shell.refresh_button.click()
    browser_contract.clean(dialog)
    assert len(browser_contract.texts(dialog.grid)) == 9, "the reload must pick up the added pair"
    assert browser_contract.texts(dialog.grid)[-1] == ["Z  Z", "–", "7", "missing"], "expected: browser_contract.texts(dialog.grid)[-1] == ['Z Z', '–', '7', 'missing']"


def test_compare_dialog_when_no_font_then_open_font_first(browser_env):
    dialog = browser_env.open("Compare Masters", no_font=True)
    assert dialog.subtitle.text() == "Open a font first.", dialog.subtitle.text()
    assert browser_contract.texts(dialog.grid) == [], "expected: browser_contract.texts(dialog.grid) == []"


def test_compare_module_when_no_masters_then_table_is_empty(browser_env):
    module = browser_env.load("Compare Masters")
    assert module.table(browser_env.package, []) == {}, "no masters means no rows"


# ---------------------------------------------------------------- Pair List Browser
def test_pair_list_when_opened_then_sorted_pairs_of_current_master_are_shown(browser_env):
    dialog = browser_env.open("Pair List Browser")
    browser_contract.clean(dialog)
    assert browser_contract.texts(dialog.grid) == [
        ["@L_A", "@R_V", "-90"],
        ["A", "V", "-70"],
        ["T", "V", "10"],
        ["T", "o", "-3"],
    ], browser_contract.texts(dialog.grid)
    assert dialog.subtitle.text() == "Bold: 4 pairs, 1 of them with a class side", "expected: dialog.subtitle.text() == 'Bold: 4 pairs, 1 of them with a class side'"
    assert dialog.tool.status == "4 pairs" and dialog.export_button.isEnabled(), "expected: dialog.tool.status == '4 pairs' and dialog.export_button.isEnabled()"


def test_pair_list_when_master_or_filter_changes_then_rows_follow(browser_env):
    dialog = browser_env.open("Pair List Browser")
    dialog.master.setCurrentIndex(0)
    assert dialog.subtitle.text() == "Regular: 8 pairs, 3 of them with a class side", "expected: dialog.subtitle.text() == 'Regular: 8 pairs, 3 of them with a class s..."
    dialog.filter.setText("=T")
    assert [row[:2] for row in browser_contract.texts(dialog.grid)] == [["T", "V"], ["T", "o"]], "expected: [row[:2] for row in browser_contract.texts(dialog.grid)] == [['T', 'V'], ['T', 'o']]"
    assert dialog.tool.status == "2 of 8 pairs", dialog.tool.status
    dialog.filter.setText("nothing")
    assert browser_contract.texts(dialog.grid) == [] and not dialog.export_button.isEnabled(), "expected: browser_contract.texts(dialog.grid) == [] and (not dialog.export_button.isEnabled())"


def test_pair_list_when_export_chosen_then_csv_has_shown_rows_in_order(browser_env, tmp_path):
    dialog = browser_env.open("Pair List Browser")
    dialog.filter.setText("=T")
    dialog.export_button.clicked.emit()
    browser_contract.clean(dialog)
    chooser = dialog.dialog
    assert chooser.isVisible() and chooser.selectedFiles()[0].endswith("kerning-Bold.csv"), (
        "the chooser opens non-modally with a master-based file name"
    )
    dialog.export_button.clicked.emit()
    assert dialog.dialog is chooser and chooser.isVisible(), "the chooser is reused"
    target = tmp_path / "pairs.csv"
    chooser.fileSelected.emit(str(target))
    browser_contract.clean(dialog)
    assert target.read_bytes() == (
        b"left,right,value,master\r\nT,V,10,Bold\r\nT,o,-3,Bold\r\n"
    ), target.read_bytes()
    assert dialog.last_export == {"path": str(target), "pairs": 2}, "expected: dialog.last_export == {'path': str(target), 'pairs': 2}"
    assert dialog.tool.status == "Exported 2 pairs to pairs.csv", dialog.tool.status


def test_pair_list_when_font_replaced_then_export_and_chooser_are_refused(browser_env, tmp_path):
    dialog = browser_env.open("Pair List Browser")
    replace_font(browser_env)
    dialog.export_button.clicked.emit()
    assert "no longer current" in dialog.tool.status, dialog.tool.status
    assert dialog.dialog is None, "no chooser for a stale panel"
    target = tmp_path / "must-not-exist.csv"
    with pytest.raises(ValueError, match="stale|current"):
        dialog.write(str(target))
    assert not target.exists(), "a stale export must not create its file"


def test_pair_list_when_no_font_then_open_font_first(browser_env):
    dialog = browser_env.open("Pair List Browser", no_font=True)
    assert dialog.subtitle.text() == "Open a font first.", dialog.subtitle.text()
    assert browser_contract.texts(dialog.grid) == [] and not dialog.export_button.isEnabled(), "expected: browser_contract.texts(dialog.grid) == [] and (not dialog.export_button.isEnabled())"


def test_pair_list_module_when_fractional_value_exported_then_general_format_is_used(browser_env, tmp_path):
    module = browser_env.load("Pair List Browser")
    target = tmp_path / "out.csv"
    assert module.export_csv([("A", "V", 0.5)], "Bold", target) == 1, "expected: module.export_csv([('A', 'V', 0.5)], 'Bold', target) == 1"
    assert target.read_bytes() == b"left,right,value,master\r\nA,V,0.5,Bold\r\n", "expected: target.read_bytes() == b'left,right,value,master\\r\\nA,V,0.5,Bold\\r\\n'"


# ---------------------------------------------------------------- Missing Pairs
def test_missing_dialog_when_opened_then_default_combinations_are_checked(browser_env):
    dialog = browser_env.open("Missing Pairs")
    browser_contract.clean(dialog)
    assert dialog.lefts == list("AFLPTVWY") and dialog.rights == list("aeosuy"), "expected: dialog.lefts == list('AFLPTVWY') and dialog.rights == list('aeosuy')"
    assert ("T", "o") not in dialog.missing, "an explicit pair covers its combination"
    assert len(dialog.missing) == 47, "expected: len(dialog.missing) == 47"
    assert dialog.tool.status == "47 of 48 combinations unkerned (97 %)", dialog.tool.status
    assert dialog.copy_button.isEnabled(), "expected: dialog.copy_button.isEnabled()"
    assert len(browser_contract.texts(dialog.grid)) == 47, "expected: len(browser_contract.texts(dialog.grid)) == 47"


def test_missing_dialog_when_classes_cover_pairs_then_nothing_is_listed(browser_env):
    dialog = browser_env.open("Missing Pairs")
    dialog.left_text.setText("@L_A")
    dialog.right_text.setText("V")
    browser_contract.clean(dialog)
    assert dialog.lefts == ["A", "Aacute"] and dialog.rights == ["V"], "expected: dialog.lefts == ['A', 'Aacute'] and dialog.rights == ['V']"
    assert dialog.missing == [], "a class pair covers its members"
    assert dialog.tool.status == "0 of 2 combinations unkerned (0 %)", dialog.tool.status
    assert not dialog.copy_button.isEnabled(), "expected: not dialog.copy_button.isEnabled()"


def test_missing_dialog_when_zero_pair_exists_then_it_still_covers(browser_env):
    dialog = browser_env.open("Missing Pairs")
    dialog.master.setCurrentIndex(0)
    dialog.left_text.setText("Aacute")
    dialog.right_text.setText("V")
    assert dialog.missing == [], "an explicit zero is coverage, not absence"
    dialog.right_text.setText("A")
    assert dialog.missing == [("Aacute", "A")], "expected: dialog.missing == [('Aacute', 'A')]"
    assert browser_contract.texts(dialog.grid) == [["Aacute", "A"]], "expected: browser_contract.texts(dialog.grid) == [['Aacute', 'A']]"


def test_missing_dialog_when_text_has_no_glyphs_then_no_combinations(browser_env):
    dialog = browser_env.open("Missing Pairs")
    dialog.left_text.setText("???")
    assert dialog.lefts == [] and dialog.tool.status == "0 of 0 combinations unkerned", "expected: dialog.lefts == [] and dialog.tool.status == '0 of 0 combinations u..."


def test_missing_dialog_when_copied_then_pairs_reach_the_clipboard(browser_env):
    dialog = browser_env.open("Missing Pairs")
    dialog.left_text.setText("T")
    dialog.right_text.setText("o V")
    assert dialog.missing == [] and not dialog.copy_button.isEnabled(), (
        "T o and T V are both kerned on Bold, so there is nothing to copy"
    )
    dialog.left_text.setText("V")
    dialog.copy_button.clicked.emit()
    assert browser_env.clipboard.text() == "V o\nV V", browser_env.clipboard.text()
    assert dialog.tool.status == "Copied 2 pairs to the clipboard", "expected: dialog.tool.status == 'Copied 2 pairs to the clipboard'"


def test_missing_dialog_when_font_replaced_then_copy_is_refused(browser_env):
    dialog = browser_env.open("Missing Pairs")
    replace_font(browser_env)
    dialog.copy_button.clicked.emit()
    assert "no longer current" in dialog.tool.status, dialog.tool.status
    assert browser_env.clipboard.text() == "", "a stale panel must not copy"


def test_missing_dialog_when_no_font_then_open_font_first(browser_env):
    dialog = browser_env.open("Missing Pairs", no_font=True)
    assert dialog.subtitle.text() == "Open a font first.", dialog.subtitle.text()
    assert dialog.chosen() == "" and dialog.missing == [], "expected: dialog.chosen() == '' and dialog.missing == []"


# ---------------------------------------------------------------- Text Preview
def painter_of(proof_env):
    assert proof_env.painter.created, "the canvas must create a painter"
    return proof_env.painter.created[-1]


def test_preview_dialog_when_text_typed_then_rows_follow_effective_kerning(proof_env):
    panel = proof_env.open("Text Preview")
    panel.text.setText("AV")
    assert panel.rows == [("A", 0, 600, 0), ("V", 530, 650, -70)]
    assert proof_env.shell.status.text() == "2 glyphs · 1 kerned gaps, -70 units in total"
    assert panel.subtitle.text() == "Bold master · glyph outlines with kerning applied"
    panel.kerned.setChecked(False)
    assert panel.rows[1] == ("V", 600, 650, 0)
    assert proof_env.shell.status.text() == "2 glyphs · 0 kerned gaps, 0 units in total"
    assert "kerning off" in panel.subtitle.text()
    panel.kerned.setChecked(True)
    panel.master.setCurrentIndex(0)
    assert panel.rows[1][3] == -60


def test_preview_dialog_when_size_changes_then_label_and_canvas_update(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview")
    calls = []
    monkeypatch.setattr(panel.canvas, 'update', lambda: calls.append('update'))
    panel.size.setValue(100)
    assert panel.size.value() == 100 and panel.size.suffix() == ' px'
    assert calls, "the proof must be repainted"
    calls.clear()
    panel.show_values.setChecked(False)
    assert calls == ["update"], "toggling labels repaints the actual canvas once"


def test_preview_canvas_when_painted_then_outlines_and_kern_labels_are_drawn(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview")
    panel.text.setText("AV")
    monkeypatch.setattr(proof_env.text.QtGui, 'QPainter', proof_env.painter)
    panel.canvas.paintEvent(None)
    assert panel.canvas.paint_error is None
    painter = painter_of(proof_env)
    assert painter.paths == 2 and painter.texts == ['-70'] and painter.ended
    panel.show_values.setChecked(False)
    panel.canvas.paintEvent(None)
    assert painter_of(proof_env).texts == []


def test_preview_canvas_when_no_text_then_prompt_is_drawn(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview")
    panel.text.setText("")
    monkeypatch.setattr(proof_env.text.QtGui, 'QPainter', proof_env.painter)
    panel.canvas.paintEvent(None)
    assert painter_of(proof_env).texts == ["Type some text above."]
    assert proof_env.shell.status.text() == "0 glyphs · 0 kerned gaps, 0 units in total"


def test_preview_canvas_when_no_font_then_open_font_prompt_is_drawn(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview", no_font=True)
    panel.refresh()
    monkeypatch.setattr(proof_env.text.QtGui, 'QPainter', proof_env.painter)
    panel.canvas.paintEvent(None)
    assert painter_of(proof_env).texts == ["Open a font first."]
    assert panel.subtitle.text() == "Open a font first."
    assert panel.upm == 1000 and panel.ascender == 800


def test_preview_canvas_when_font_replaced_then_paint_error_is_contained(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview")
    panel.text.setText("AV")
    replace(proof_env)
    monkeypatch.setattr(proof_env.text.QtGui, 'QPainter', proof_env.painter)
    panel.canvas.paintEvent(None)
    assert "stale" in panel.canvas.paint_error
    assert proof_env.shell.status.text().startswith("Proof error:")
    assert panel.rows == [] and painter_of(proof_env).ended


def test_preview_canvas_when_error_hook_fails_then_failure_is_still_contained(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview")
    monkeypatch.setattr(proof_env.text.QtGui, 'QPainter', proof_env.painter)
    canvas = panel.canvas
    canvas.owner = None
    canvas.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("draw"))
    canvas.paintEvent(None)
    assert canvas.paint_error == "RuntimeError('draw')" and canvas.error_hook_failed


def test_preview_canvas_when_painter_end_fails_then_error_is_recorded(proof_env, monkeypatch):
    panel = proof_env.open("Text Preview")
    monkeypatch.setattr(proof_env.text.QtGui, 'QPainter', proof_env.painter)
    def broken_end(self):
        raise RuntimeError('end')
    monkeypatch.setattr(proof_env.painter, 'end', broken_end)
    panel.canvas.paintEvent(None)
    assert panel.canvas.paint_error == "RuntimeError('end')"
    assert proof_env.shell.status.text() == "Proof error: RuntimeError('end')"


def test_preview_module_when_text_has_unknown_tokens_then_they_are_skipped(proof_env):
    assert proof_env.text.parse_text("A/zzz V/ /Aacute", proof_env.package) == ["A", "V", "Aacute"]


def test_preview_module_when_outline_built_then_it_is_a_path(proof_env):
    path = proof_env.text.outline(proof_env.package.findName("A").findLayer("Bold"))
    assert path.boundingRect().right() == 600


# ---------------------------------------------------------------- shared lifecycle
PANELS = [
    ("Classes Browser", "ClassesBrowser"),
    ("Compare Masters", "CompareMasters"),
    ("Pair List Browser", "PairList"),
    ("Missing Pairs", "MissingPairs"),
    ("Text Preview", "TextPreview"),
]


@pytest.mark.parametrize(("title", "_cls"), PANELS)
def test_panels_when_closed_then_registry_and_slots_are_released(env, title, _cls, request):
    if title == "Text Preview":
        return proof_contract.close_owner(request.getfixturevalue("proof_env"), title)
    browser_contract.close_owner(request.getfixturevalue("browser_env"), title)


@pytest.mark.parametrize(("title", "_cls"), PANELS)
def test_panels_when_run_as_script_then_main_opens_the_dialog(env, title, _cls, request):
    if title == "Text Preview":
        return proof_contract.launch(request.getfixturevalue("proof_env"))
    browser_contract.launch(request.getfixturevalue("browser_env"))
