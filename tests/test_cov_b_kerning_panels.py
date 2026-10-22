# this_file: tests/test_cov_b_kerning_panels.py
"""Drive the five read-only kerning panels through their real dialogs."""

import runpy
import sys

import pytest
from _cov_b_support import ROOT, Env, Package, check_clean, make_package


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
def test_classes_dialog_when_opened_then_every_class_is_listed_with_side_and_size(env):
    dialog = env.open("Kerning", "Classes Browser", "ClassesBrowser")
    check_clean(dialog)
    assert dialog.list.items == [
        "@Both   both · 1",
        "@L_A   left · 2",
        "@R_V   right · 1",
    ], dialog.list.items
    assert dialog.subtitle.text == (
        "3 classes: 1 left, 1 right, 1 both sides. Values are shown for all 2 masters."
    ), dialog.subtitle.text
    assert dialog.status.text == "@Both: 1 members, used in 0 pairs", dialog.status.text
    assert dialog.title.text == "@Both · both side", "expected: dialog.title.text == '@Both · both side'"


def test_classes_dialog_when_class_chosen_then_pairs_show_values_per_master(env):
    dialog = env.open("Kerning", "Classes Browser", "ClassesBrowser")
    dialog.select_class("L_A")
    check_clean(dialog)
    assert dialog.title.text == "@L_A · left side", "expected: dialog.title.text == '@L_A · left side'"
    assert dialog.members.text == "A Aacute", dialog.members.text
    assert dialog.pairs.texts() == [
        ["@L_A  @R_V", "-80", "-90"],
        ["@L_A  V", "-40", "–"],
    ], "a master without the pair shows a dash"
    assert dialog.status.text == "@L_A: 2 members, used in 2 pairs", dialog.status.text
    assert dialog.pair_rows == {"@L_A @R_V": {"Regular": -80, "Bold": -90},
                                "@L_A V": {"Regular": -40}}, "expected: dialog.pair_rows == {'@L_A @R_V': {'Regular': -80, 'Bold': -90}, '@..."
    assert dialog.select_button.enabled, "expected: dialog.select_button.enabled"


def test_classes_dialog_when_filtered_then_name_or_exact_member_matches(env):
    dialog = env.open("Kerning", "Classes Browser", "ClassesBrowser")
    dialog.filter.setText("aacute")
    assert dialog.list.items == [], "member names are case-sensitive"
    assert dialog.status.text == "0 of 3 classes", dialog.status.text
    assert dialog.title.text == "No class" and not dialog.select_button.enabled, "expected: dialog.title.text == 'No class' and (not dialog.select_button.enabled)"
    dialog.filter.setText("Aacute")
    assert dialog.list.items == ["@L_A   left · 2"], dialog.list.items
    assert dialog.selected == "L_A", "the first match is shown automatically"
    dialog.filter.setText("r_")
    assert dialog.list.items == ["@R_V   right · 1"], "class names match in any case"


def test_classes_dialog_when_select_members_clicked_then_font_selection_changes(env):
    dialog = env.open("Kerning", "Classes Browser", "ClassesBrowser")
    dialog.select_class("L_A")
    dialog.select_button.clicked.emit()
    check_clean(dialog)
    names = [glyph.name for glyph in env.glyph_list]
    assert env.selected == {names.index("A"), names.index("Aacute")}, env.selected
    assert dialog.status.text == "Selected 2 glyphs of @L_A in the Font window", "expected: dialog.status.text == 'Selected 2 glyphs of @L_A in the Font window'"
    assert env.updates == 0, "selection makes no UpdateAll call: it queues glyph ids (fl#8537)"


def test_classes_dialog_when_nothing_chosen_then_select_members_does_nothing(env):
    dialog = env.open("Kerning", "Classes Browser", "ClassesBrowser")
    dialog.filter.setText("zzz")
    dialog.select_members()
    assert env.selected == set(), "no class means no selection change"


def test_classes_dialog_when_font_replaced_then_selection_is_refused(env):
    dialog = env.open("Kerning", "Classes Browser", "ClassesBrowser")
    dialog.select_class("L_A")
    replace_font(env)
    dialog.select_button.clicked.emit()
    assert "stale" in dialog.slot_error, dialog.slot_error
    assert env.selected == set(), "a stale panel must not touch the selection"
    assert dialog.classes == {} and not dialog.select_button.enabled, "expected: dialog.classes == {} and (not dialog.select_button.enabled)"


def test_classes_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Classes Browser", "ClassesBrowser")
    check_clean(dialog)
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.list.items == [] and dialog.classes == {}, "expected: dialog.list.items == [] and dialog.classes == {}"


def test_classes_module_when_helpers_called_then_class_use_is_collected(env):
    module = env.load("Kerning", "Classes Browser")
    rows = module.pairs_using(env.package, ["Regular", "Bold"], "R_V")
    assert rows[("A", "@R_V")] == {"Regular": -60}, rows
    assert module.matches("L_A", ["A"], "  "), "blank text matches everything"
    assert module.matches("L_A", ["A"], "A"), "an exact member matches"


# ---------------------------------------------------------------- Compare Masters
def test_compare_dialog_when_opened_then_all_pairs_show_values_and_flags(env):
    dialog = env.open("Kerning", "Compare Masters", "CompareMasters")
    check_clean(dialog)
    rows = dialog.table.texts()
    assert len(rows) == 8, rows
    assert rows[0] == ["@L_A  @R_V", "-80", "-90", ""], "close values carry no flag"
    assert ["T  o", "3", "-3", "sign"] in rows, "a sign change is flagged"
    assert ["V  A", "-4", "–", "missing"] in rows, "a pair absent on one master is flagged"
    assert dialog.status.text == "8 rows shown · 5 of 8 pairs flagged", dialog.status.text
    assert dialog.subtitle.text.startswith("8 pairs across 2 masters."), dialog.subtitle.text
    assert dialog.table.columnCount == 4, "expected: dialog.table.columnCount == 4"


def test_compare_dialog_when_filtering_then_search_threshold_and_flag_options_apply(env):
    dialog = env.open("Kerning", "Compare Masters", "CompareMasters")
    dialog.only_flagged.setChecked(True)
    assert len(dialog.shown) == 5 and dialog.status.text.startswith("5 rows shown"), "expected: len(dialog.shown) == 5 and dialog.status.text.startswith('5 rows sh..."
    dialog.search.setText("@L_")
    assert [pair for pair, *_ in dialog.shown] == [("@L_A", "V")], dialog.shown
    dialog.search.setText("")
    dialog.only_flagged.setChecked(False)
    dialog.threshold.setValue(5)
    rows = {row[0]: row[3] for row in dialog.table.texts()}
    assert rows["T  o"] == "sign, jump", "both reasons are listed"
    assert rows["A  V"] == "jump", "a 10 unit gap exceeds a threshold of 5"
    assert dialog.status.text == "8 rows shown · 7 of 8 pairs flagged", dialog.status.text


def test_compare_dialog_when_reload_clicked_then_new_kerning_is_read(env):
    dialog = env.open("Kerning", "Compare Masters", "CompareMasters")
    env.package.kerning("Bold").stored[(("Z", "glyphMode"), ("Z", "glyphMode"))] = 7
    dialog.reload_button.clicked.emit()
    check_clean(dialog)
    assert dialog.table.rowCount == 9, "the reload must pick up the added pair"
    assert dialog.table.texts()[-1] == ["Z  Z", "–", "7", "missing"], "expected: dialog.table.texts()[-1] == ['Z Z', '–', '7', 'missing']"


def test_compare_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Compare Masters", "CompareMasters")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.table.texts() == [], "expected: dialog.table.texts() == []"


def test_compare_module_when_no_masters_then_table_is_empty(env):
    module = env.load("Kerning", "Compare Masters")
    assert module.table(env.package, []) == {}, "no masters means no rows"


# ---------------------------------------------------------------- Pair List Browser
def test_pair_list_when_opened_then_sorted_pairs_of_current_master_are_shown(env):
    dialog = env.open("Kerning", "Pair List Browser", "PairList")
    check_clean(dialog)
    assert dialog.table.texts() == [
        ["@L_A", "@R_V", "-90"],
        ["A", "V", "-70"],
        ["T", "V", "10"],
        ["T", "o", "-3"],
    ], dialog.table.texts()
    assert dialog.subtitle.text == "Bold: 4 pairs, 1 of them with a class side", "expected: dialog.subtitle.text == 'Bold: 4 pairs, 1 of them with a class side'"
    assert dialog.status.text == "4 pairs" and dialog.export_button.enabled, "expected: dialog.status.text == '4 pairs' and dialog.export_button.enabled"


def test_pair_list_when_master_or_filter_changes_then_rows_follow(env):
    dialog = env.open("Kerning", "Pair List Browser", "PairList")
    dialog.master.setCurrentIndex(0)
    assert dialog.subtitle.text == "Regular: 8 pairs, 3 of them with a class side", "expected: dialog.subtitle.text == 'Regular: 8 pairs, 3 of them with a class s..."
    dialog.filter.setText("=T")
    assert [row[:2] for row in dialog.table.texts()] == [["T", "V"], ["T", "o"]], "expected: [row[:2] for row in dialog.table.texts()] == [['T', 'V'], ['T', 'o']]"
    assert dialog.status.text == "2 of 8 pairs", dialog.status.text
    dialog.filter.setText("nothing")
    assert dialog.table.texts() == [] and not dialog.export_button.enabled, "expected: dialog.table.texts() == [] and (not dialog.export_button.enabled)"


def test_pair_list_when_export_chosen_then_csv_has_shown_rows_in_order(env, tmp_path):
    dialog = env.open("Kerning", "Pair List Browser", "PairList")
    dialog.filter.setText("=T")
    dialog.export_button.clicked.emit()
    check_clean(dialog)
    chooser = dialog.file_dialog
    assert chooser.opened == 1 and chooser.selected == "kerning-Bold.csv", (
        "the chooser opens non-modally with a master-based file name"
    )
    dialog.export_button.clicked.emit()
    assert dialog.file_dialog is chooser and chooser.opened == 2, "the chooser is reused"
    target = tmp_path / "pairs.csv"
    chooser.fileSelected.emit(str(target))
    check_clean(dialog)
    assert target.read_bytes() == (
        b"left,right,value,master\r\nT,V,10,Bold\r\nT,o,-3,Bold\r\n"
    ), target.read_bytes()
    assert dialog.last_export == {"path": str(target), "pairs": 2}, "expected: dialog.last_export == {'path': str(target), 'pairs': 2}"
    assert dialog.status.text == "Exported 2 pairs to pairs.csv", dialog.status.text


def test_pair_list_when_font_replaced_then_export_and_chooser_are_refused(env, tmp_path):
    dialog = env.open("Kerning", "Pair List Browser", "PairList")
    replace_font(env)
    dialog.export_button.clicked.emit()
    assert "stale" in dialog.slot_error, dialog.slot_error
    assert dialog.file_dialog is None, "no chooser for a stale panel"
    target = tmp_path / "must-not-exist.csv"
    with pytest.raises(ValueError, match="stale"):
        dialog.export(str(target))
    assert not target.exists(), "a stale export must not create its file"


def test_pair_list_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Pair List Browser", "PairList")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.table.texts() == [] and not dialog.export_button.enabled, "expected: dialog.table.texts() == [] and (not dialog.export_button.enabled)"


def test_pair_list_module_when_fractional_value_exported_then_general_format_is_used(env, tmp_path):
    module = env.load("Kerning", "Pair List Browser")
    target = tmp_path / "out.csv"
    assert module.export_csv([("A", "V", 0.5)], "Bold", target) == 1, "expected: module.export_csv([('A', 'V', 0.5)], 'Bold', target) == 1"
    assert target.read_bytes() == b"left,right,value,master\r\nA,V,0.5,Bold\r\n", "expected: target.read_bytes() == b'left,right,value,master\\r\\nA,V,0.5,Bold\\r\\n'"


# ---------------------------------------------------------------- Missing Pairs
def test_missing_dialog_when_opened_then_default_combinations_are_checked(env):
    dialog = env.open("Kerning", "Missing Pairs", "MissingPairs")
    check_clean(dialog)
    assert dialog.lefts == list("AFLPTVWY") and dialog.rights == list("aeosuy"), "expected: dialog.lefts == list('AFLPTVWY') and dialog.rights == list('aeosuy')"
    assert ("T", "o") not in dialog.missing, "an explicit pair covers its combination"
    assert len(dialog.missing) == 47, "expected: len(dialog.missing) == 47"
    assert dialog.status.text == "47 of 48 combinations unkerned (97 %)", dialog.status.text
    assert dialog.copy_button.enabled, "expected: dialog.copy_button.enabled"
    assert dialog.table.rowCount == 47, "expected: dialog.table.rowCount == 47"


def test_missing_dialog_when_classes_cover_pairs_then_nothing_is_listed(env):
    dialog = env.open("Kerning", "Missing Pairs", "MissingPairs")
    dialog.left_text.setText("@L_A")
    dialog.right_text.setText("V")
    check_clean(dialog)
    assert dialog.lefts == ["A", "Aacute"] and dialog.rights == ["V"], "expected: dialog.lefts == ['A', 'Aacute'] and dialog.rights == ['V']"
    assert dialog.missing == [], "a class pair covers its members"
    assert dialog.status.text == "0 of 2 combinations unkerned (0 %)", dialog.status.text
    assert not dialog.copy_button.enabled, "expected: not dialog.copy_button.enabled"


def test_missing_dialog_when_zero_pair_exists_then_it_still_covers(env):
    dialog = env.open("Kerning", "Missing Pairs", "MissingPairs")
    dialog.master.setCurrentIndex(0)
    dialog.left_text.setText("Aacute")
    dialog.right_text.setText("V")
    assert dialog.missing == [], "an explicit zero is coverage, not absence"
    dialog.right_text.setText("A")
    assert dialog.missing == [("Aacute", "A")], "expected: dialog.missing == [('Aacute', 'A')]"
    assert dialog.table.texts() == [["Aacute", "A"]], "expected: dialog.table.texts() == [['Aacute', 'A']]"


def test_missing_dialog_when_text_has_no_glyphs_then_no_combinations(env):
    dialog = env.open("Kerning", "Missing Pairs", "MissingPairs")
    dialog.left_text.setText("???")
    assert dialog.lefts == [] and dialog.status.text == "0 of 0 combinations unkerned", "expected: dialog.lefts == [] and dialog.status.text == '0 of 0 combinations u..."


def test_missing_dialog_when_copied_then_pairs_reach_the_clipboard(env):
    dialog = env.open("Kerning", "Missing Pairs", "MissingPairs")
    dialog.left_text.setText("T")
    dialog.right_text.setText("o V")
    assert dialog.missing == [] and not dialog.copy_button.enabled, (
        "T o and T V are both kerned on Bold, so there is nothing to copy"
    )
    dialog.left_text.setText("V")
    dialog.copy_button.clicked.emit()
    assert clipboard(env).copied == ["V o\nV V"], clipboard(env).copied
    assert dialog.status.text == "Copied 2 pairs to the clipboard", "expected: dialog.status.text == 'Copied 2 pairs to the clipboard'"


def test_missing_dialog_when_font_replaced_then_copy_is_refused(env):
    dialog = env.open("Kerning", "Missing Pairs", "MissingPairs")
    replace_font(env)
    dialog.copy_button.clicked.emit()
    assert "stale" in dialog.slot_error, dialog.slot_error
    assert clipboard(env).copied == [], "a stale panel must not copy"


def test_missing_dialog_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Kerning", "Missing Pairs", "MissingPairs")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert dialog.chosen_master() == "" and dialog.missing == [], "expected: dialog.chosen_master() == '' and dialog.missing == []"


# ---------------------------------------------------------------- Text Preview
def painter_of(env):
    created = env.qt.QtGui.QPainter.created
    assert created, "the canvas must have created a painter"
    return created[-1]


def test_preview_dialog_when_text_typed_then_rows_follow_effective_kerning(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")
    check_clean(dialog)
    dialog.text.setText("AV")
    check_clean(dialog)
    assert dialog.rows == [("A", 0, 600, 0), ("V", 530, 650, -70)], dialog.rows
    assert dialog.status.text == "2 glyphs · 1 kerned gaps, -70 units in total", "expected: dialog.status.text == '2 glyphs · 1 kerned gaps, -70 units in total'"
    assert dialog.subtitle.text == "Bold master · glyph outlines with kerning applied", "expected: dialog.subtitle.text == 'Bold master · glyph outlines with kerning ..."
    dialog.kerned.setChecked(False)
    assert dialog.rows[1] == ("V", 600, 650, 0), "kerning off keeps the plain advance"
    assert dialog.status.text == "2 glyphs · 0 kerned gaps, 0 units in total", "expected: dialog.status.text == '2 glyphs · 0 kerned gaps, 0 units in total'"
    assert "kerning off" in dialog.subtitle.text, "expected: 'kerning off' in dialog.subtitle.text"
    dialog.kerned.setChecked(True)
    dialog.master.setCurrentIndex(0)
    assert dialog.rows[1][3] == -60, "Regular has a different A V value"


def test_preview_dialog_when_size_changes_then_label_and_canvas_update(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")
    before = dialog.canvas.updates
    dialog.size_slider.setValue(100)
    assert dialog.size_label.text == "100 px", dialog.size_label.text
    assert dialog.canvas.updates > before, "the proof must be repainted"
    before = dialog.canvas.updates
    dialog.show_values.setChecked(False)
    assert dialog.canvas.updates == before + 1, "toggling the labels repaints"


def test_preview_canvas_when_painted_then_outlines_and_kern_labels_are_drawn(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")
    dialog.text.setText("AV")
    dialog.canvas.paintEvent(None)
    assert dialog.canvas.paint_error is None, dialog.canvas.paint_error
    painter = painter_of(env)
    assert painter.paths == 2, "one outline per glyph"
    assert painter.texts == ["-70"], "the kerned gap is labelled"
    assert painter.ended, "the painter is always released"
    dialog.show_values.setChecked(False)
    dialog.canvas.paintEvent(None)
    assert painter_of(env).texts == [], "labels are off"


def test_preview_canvas_when_no_text_then_prompt_is_drawn(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")
    dialog.text.setText("")
    dialog.canvas.paintEvent(None)
    assert painter_of(env).texts == ["Type some text above."], painter_of(env).texts
    assert dialog.status.text == "0 glyphs · 0 kerned gaps, 0 units in total", "expected: dialog.status.text == '0 glyphs · 0 kerned gaps, 0 units in total'"


def test_preview_canvas_when_no_font_then_open_font_prompt_is_drawn(no_font):
    dialog = no_font.open("Kerning", "Text Preview", "TextPreview")
    dialog.canvas.paintEvent(None)
    assert painter_of(no_font).texts == ["Open a font first."], painter_of(no_font).texts
    assert dialog.subtitle.text == "Open a font first.", "expected: dialog.subtitle.text == 'Open a font first.'"
    assert dialog.upm == 1000 and dialog.ascender == 800, "defaults without a font"


def test_preview_canvas_when_font_replaced_then_paint_error_is_contained(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")
    dialog.text.setText("AV")
    replace_font(env)
    dialog.canvas.paintEvent(None)
    assert "stale" in dialog.canvas.paint_error, dialog.canvas.paint_error
    assert dialog.status.text.startswith("Proof error:"), dialog.status.text
    assert dialog.rows == [], "a failed proof clears its rows"
    assert painter_of(env).ended, "the painter is released after the failure"


def test_preview_canvas_when_error_hook_fails_then_failure_is_still_contained(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")
    canvas = dialog.canvas
    canvas.owner = None
    canvas.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("draw"))
    canvas.paintEvent(None)
    assert canvas.paint_error == "RuntimeError('draw')", "expected: canvas.paint_error == 'RuntimeError('draw')'"
    assert canvas.error_hook_failed, "a failing hook must be recorded, not raised"


def test_preview_canvas_when_painter_end_fails_then_error_is_recorded(env):
    dialog = env.open("Kerning", "Text Preview", "TextPreview")

    def broken_end(self):
        raise RuntimeError("end")

    env.qt.QtGui.QPainter.end = broken_end
    dialog.canvas.paintEvent(None)
    assert dialog.canvas.paint_error == "RuntimeError('end')", dialog.canvas.paint_error
    assert dialog.status.text == "Proof error: RuntimeError('end')", dialog.status.text


def test_preview_module_when_text_has_unknown_tokens_then_they_are_skipped(env):
    module = env.load("Kerning", "Text Preview")
    names = module.parse_text("A/zzz V/ /Aacute", env.package)
    assert names == ["A", "V", "Aacute"], "unknown and empty slash tokens are dropped"


def test_preview_module_when_outline_built_then_it_is_a_path(env):
    module = env.load("Kerning", "Text Preview")
    path = module.outline(env.package.findName("A").findLayer("Bold"))
    assert path.boundingRect().right() == 600, "the fake outline spans the advance"


# ---------------------------------------------------------------- shared lifecycle
PANELS = [
    ("Classes Browser", "ClassesBrowser"),
    ("Compare Masters", "CompareMasters"),
    ("Pair List Browser", "PairList"),
    ("Missing Pairs", "MissingPairs"),
    ("Text Preview", "TextPreview"),
]


@pytest.mark.parametrize(("title", "_cls"), PANELS)
def test_panels_when_closed_then_registry_and_slots_are_released(env, title, _cls):
    module = env.load("Kerning", title)
    dialog = module.main()
    assert sys._fontlab_samples[module.KEY] is dialog, "expected: sys._fontlab_samples[module.KEY] is dialog"
    dialog.close_button.clicked.emit()
    assert sys._fontlab_samples == {} and dialog.deleted, "Close releases and deletes"
    assert dialog._connections == [], "Close disconnects every owned slot"


@pytest.mark.parametrize(("title", "_cls"), PANELS)
def test_panels_when_run_as_script_then_main_opens_the_dialog(env, title, _cls):
    namespace = runpy.run_path(
        str(ROOT / "Scripts/Kerning" / f"{title}.py"), run_name="__main__"
    )
    assert namespace["KEY"] in sys._fontlab_samples, "running as a script opens the dialog"
