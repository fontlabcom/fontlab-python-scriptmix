# this_file: tests/test_cov_b_reports.py
"""Drive the Reports dialogs through their real classes with an owned report font."""

import runpy
import sys
from types import SimpleNamespace as NS

import pytest
from _cov_b_support import (
    ROOT,
    Contour,
    Glyph,
    Layer,
    Node,
    Package,
    ReportEnv,
    ReportPackage,
    Shape,
    check_clean,
    make_package,
    square,
)


@pytest.fixture
def env(monkeypatch, real_app, app_sources):
    """Report font with ten glyphs on two masters; Bold is current."""
    return ReportEnv(monkeypatch, real_app)


@pytest.fixture
def no_font(monkeypatch, real_app, app_sources):
    """No font open."""
    return ReportEnv(monkeypatch, real_app, None)


def replace_font(env):
    """Swap in a different current font, as if the user switched documents."""
    other = Package(["Regular"], {"Regular": make_package().kerning("Regular")}, {})
    other.id = 99
    env.package = other


def selected_names(env):
    """Names currently selected in the Font window."""
    return sorted(env.glyph_list[i].name for i in env.selected)


def fail_font(env):
    """Make every scan fail the way a broken native read would."""

    def broken():
        raise RuntimeError("native read failed")

    env.fontlab.CurrentFont = broken


# ---------------------------------------------------------------- Empty Glyphs
def test_empty_glyphs_when_opened_then_whitespace_is_hidden_and_partial_rows_found(env):
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    check_clean(dialog)
    assert dialog.table.texts() == [
        ["period", "empty", "empty"],
        ["acute", "✓", "empty"],
    ], "composites with contours and space-like glyphs are not reported"
    assert dialog.subtitle.text == (
        "2 glyphs without outlines on at least one of 2 masters; 1 only on some (likely mistakes)."
    ), dialog.subtitle.text
    assert dialog.table.headers == ["Glyph", "Regular", "Bold"], dialog.table.headers
    assert dialog.status.text == "Double-click a row to select it.", "expected: dialog.status.text == 'Double-click a row to select it.'"
    assert dialog.select_button.enabled and dialog.package_id == 11, "expected: dialog.select_button.enabled and dialog.package_id == 11"


def test_empty_glyphs_when_whitespace_shown_then_space_like_glyphs_are_listed(env):
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    dialog.skip_whitespace.setChecked(False)
    check_clean(dialog)
    assert [row[0] for row in dialog.table.texts()] == [
        ".notdef", "space", "period", "acute", "zero.zero",
    ], dialog.table.texts()
    assert dialog.subtitle.text.startswith("5 glyphs without outlines"), "expected: dialog.subtitle.text.startswith('5 glyphs without outlines')"


def test_empty_glyphs_when_select_clicked_then_all_listed_glyphs_are_selected(env):
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    dialog.select_button.clicked.emit()
    check_clean(dialog)
    assert selected_names(env) == ["acute", "period"], selected_names(env)
    assert dialog.status.text == "Selected 2 glyphs", "expected: dialog.status.text == 'Selected 2 glyphs'"
    assert dialog.last_result == {"selected": ["period", "acute"]}, "expected: dialog.last_result == {'selected': ['period', 'acute']}"


def test_empty_glyphs_when_rows_chosen_then_only_those_are_selected(env):
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    dialog.table.selected_rows = [1]
    dialog.select_button.clicked.emit()
    assert selected_names(env) == ["acute"], "the chosen table row wins over all rows"
    assert dialog.status.text == "Selected 1 glyph", "expected: dialog.status.text == 'Selected 1 glyph'"
    dialog.table.cellDoubleClicked.emit(0, 0)
    assert selected_names(env) == ["period"], "a double click selects its own row"
    dialog.table.cellDoubleClicked.emit(9, 0)
    assert selected_names(env) == [], "an out-of-range row selects nothing"


def test_empty_glyphs_when_layer_missing_then_master_counts_as_empty(env):
    del env.package.glyphs["acute"].layers["Regular"]
    ghost = NS(name="ghost", unicodes=[])
    env.fontlab.CurrentFont = lambda: NS(glyphs=[*env.package.glyphs.values(), ghost])
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    assert dialog.table.texts()[1] == ["acute", "empty", "empty"], dialog.table.texts()
    assert "ghost" not in [row[0] for row in dialog.table.texts()], (
        "a glyph the package does not know is skipped"
    )


def test_empty_glyphs_when_font_replaced_then_selection_is_refused(env):
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    replace_font(env)
    dialog.select_button.clicked.emit()
    assert "no longer current" in dialog.slot_error, dialog.slot_error
    assert selected_names(env) == [] and dialog.status.text.startswith("Error:"), "expected: selected_names(env) == [] and dialog.status.text.startswith('Error:')"


def test_empty_glyphs_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    assert dialog.status.text == "No font open." and dialog.subtitle.text == "Open a font first.", "expected: dialog.status.text == 'No font open.' and dialog.subtitle.text == '..."
    assert not dialog.select_button.enabled and dialog.package_id is None, "expected: not dialog.select_button.enabled and dialog.package_id is None"
    with pytest.raises(ValueError, match="Refresh the report"):
        dialog.select_rows()


def test_empty_glyphs_when_scan_fails_then_partial_results_are_cleared(env):
    dialog = env.open("Reports", "Empty Glyphs", "EmptyGlyphs")
    fail_font(env)
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.rescan()
    assert dialog.rows == [] and dialog.package_id is None, "no stale rows may survive"
    assert dialog.table.rowCount == 0 and not dialog.select_button.enabled, "expected: dialog.table.rowCount == 0 and (not dialog.select_button.enabled)"
    dialog.rescan_button.clicked.emit()
    assert "native read failed" in dialog.slot_error, "the click path contains the error"


def test_empty_glyphs_core_when_names_and_codes_given_then_whitespace_is_recognised(env):
    module = env.load("Reports", "Empty Glyphs")
    assert module.is_whitespace("x", [0x200B]), "zero width space is a format character"
    assert module.is_whitespace("x", [0x20]), "U+0020 is a space separator"
    assert module.is_whitespace("hairspace", []), "names ending in space count"
    assert module.is_whitespace("CR", []) and module.is_whitespace(".notdef", []), "expected: module.is_whitespace('CR', []) and module.is_whitespace('.notdef', [])"
    assert not module.is_whitespace("period", [0x2E]), "a full stop is not whitespace"
    assert module.is_empty(Layer(100)) and not module.is_empty(
        Layer(100, [Shape([square()])])
    ), "expected: module.is_empty(Layer(100)) and (not module.is_empty(Layer(100, [Sh..."


# ---------------------------------------------------------------- Font Overview
def test_overview_when_opened_then_cards_and_master_rows_describe_the_font(env):
    dialog = env.open("Reports", "Font Overview", "Overview")
    check_clean(dialog)
    assert {k: v.text for k, v in dialog.card_values.items()} == {
        "Glyphs": "10",
        "Encoded glyphs": "8",
        "Code points": "9",
        "Masters": "2",
        "Composites": "2",
        "Empty on Bold": "5",
        "Marked": "3",
        "With notes": "1",
    }, "a blank note must not count as a note"
    assert dialog.table.texts() == [
        ["Regular", "750", "700", "500", "-200", "0"],
        ["Bold", "760", "710", "510", "-210", "1"],
    ], dialog.table.texts()
    assert dialog.subtitle.text == "Sample Sans · 1000 units per em · current master Bold", "expected: dialog.subtitle.text == 'Sample Sans · 1000 units per em · current ..."
    assert dialog.grid.count() == 8, "one card per figure"


def test_overview_when_master_changes_then_cards_are_rebuilt(env):
    dialog = env.open("Reports", "Font Overview", "Overview")
    old_cards = list(dialog.grid.items)
    env.package.master = "Regular"
    dialog.refresh_button.clicked.emit()
    check_clean(dialog)
    assert "Empty on Regular" in dialog.card_values and "Empty on Bold" not in dialog.card_values, "expected: 'Empty on Regular' in dialog.card_values and 'Empty on Bold' not in..."
    assert dialog.card_values["Empty on Regular"].text == "4", (
        "acute is drawn on Regular, so four glyphs are empty there"
    )
    assert dialog.grid.count() == 8 and dialog.grid.items != old_cards, "expected: dialog.grid.count() == 8 and dialog.grid.items != old_cards"
    assert all(card.deleted for card in old_cards), "replaced cards are scheduled for deletion"


def test_overview_when_font_closes_then_cards_reset_and_status_says_so(env):
    dialog = env.open("Reports", "Font Overview", "Overview")
    env.package = None
    dialog.refresh_button.clicked.emit()
    assert dialog.status.text == "No font open." and dialog.subtitle.text == "Open a font first.", "expected: dialog.status.text == 'No font open.' and dialog.subtitle.text == '..."
    assert {v.text for v in dialog.card_values.values()} == {"–"}, "cards show a dash"
    assert dialog.table.rowCount == 0 and dialog.rows == [], "expected: dialog.table.rowCount == 0 and dialog.rows == []"


def test_overview_when_opened_without_font_then_no_cards_exist(no_font):
    dialog = no_font.open("Reports", "Font Overview", "Overview")
    assert dialog.status.text == "No font open." and dialog.card_values == {}, "expected: dialog.status.text == 'No font open.' and dialog.card_values == {}"


def test_overview_core_when_component_has_no_data_then_it_is_ignored(env):
    module = env.load("Reports", "Font Overview")
    layer = Layer(100, [Shape([square()]), Shape(base="A")])
    assert module.component_names(layer) == ["A"], "only real components are named"


# ---------------------------------------------------------------- Glyph Table CSV
def test_csv_when_opened_then_all_glyphs_are_tabulated(env):
    dialog = env.open("Reports", "Glyph Table CSV", "GlyphTable")
    check_clean(dialog)
    assert dialog.scope.items == ["All glyphs", "Selected glyphs (0)"], "expected: dialog.scope.items == ['All glyphs', 'Selected glyphs (0)']"
    assert dialog.header == [
        "glyph", "unicode", "width Regular", "width Bold", "contours", "components",
    ], "expected: dialog.header == ['glyph', 'unicode', 'width Regular', 'width Bold'..."
    assert dialog.table.texts()[6] == ["Aacute", "00C1", "600", "600", "2", "A acute"], (
        dialog.table.texts()[6]
    )
    assert dialog.table.texts()[8][1] == "20AC 20000", "all code points are listed"
    assert dialog.table.texts()[4][2:4] == ["600", "620"], "widths come per master"
    assert dialog.subtitle.text.startswith("10 glyphs · widths for 2 masters"), "expected: dialog.subtitle.text.startswith('10 glyphs · widths for 2 masters')"
    assert dialog.status.text == "Choose a file to export, or copy the CSV.", "expected: dialog.status.text == 'Choose a file to export, or copy the CSV.'"
    assert dialog.copy_button.enabled and not dialog.export_button.enabled, "expected: dialog.copy_button.enabled and (not dialog.export_button.enabled)"


def test_csv_when_path_given_then_export_writes_bom_utf8_with_lf(env, tmp_path):
    dialog = env.open("Reports", "Glyph Table CSV", "GlyphTable")
    target = tmp_path / "glyphs.csv"
    dialog.path.setText(str(target))
    assert dialog.export_button.enabled, "a path enables Export"
    dialog.export_button.clicked.emit()
    check_clean(dialog)
    data = target.read_bytes()
    assert data.startswith(b"\xef\xbb\xbfglyph,unicode,width Regular"), data[:40]
    assert b"\r" not in data and data.endswith(b"zero.zero,200B,0,0,0,\n"), data[-40:]
    assert dialog.status.text == "Wrote 10 rows to glyphs.csv", dialog.status.text
    assert dialog.last_result == {"path": str(target), "rows": 10, "bytes": len(data)}, "expected: dialog.last_result == {'path': str(target), 'rows': 10, 'bytes': le..."
    other = tmp_path / "other.csv"
    assert dialog.export(str(other)) == str(other) and other.exists(), "expected: dialog.export(str(other)) == str(other) and other.exists()"
    dialog.path.setText("  ")
    assert not dialog.export_button.enabled, "a blank path disables Export"


def test_csv_when_copy_clicked_then_clipboard_holds_the_whole_table(env):
    dialog = env.open("Reports", "Glyph Table CSV", "GlyphTable")
    dialog.copy_button.clicked.emit()
    text = env.qt.QtGui.QApplication.clipboard().copied[-1]
    assert text.startswith("glyph,unicode,width Regular,width Bold,contours,components\n"), "expected: text.startswith('glyph,unicode,width Regular,width Bold,contours,co..."
    assert text.count("\n") == 11, "a header plus ten glyph rows"
    assert "Euro,20AC 20000,550,550,1,\n" in text, "expected: 'Euro,20AC 20000,550,550,1,\\n' in text"
    assert dialog.status.text == "Copied 10 rows", "expected: dialog.status.text == 'Copied 10 rows'"


def test_csv_when_glyphs_selected_then_scope_defaults_to_the_selection(env):
    env.select("A", "x")
    dialog = env.open("Reports", "Glyph Table CSV", "GlyphTable")
    assert dialog.scope.currentIndex == 1 and dialog.scope.items[1] == "Selected glyphs (2)", "expected: dialog.scope.currentIndex == 1 and dialog.scope.items[1] == 'Select..."
    assert [row[0] for row in dialog.table.texts()] == ["A", "x"], dialog.table.texts()
    dialog.scope.setCurrentIndex(0)
    assert len(dialog.table.texts()) == 10, "switching scope rebuilds the table"


def test_csv_when_choose_clicked_then_chosen_file_lands_in_the_path_field(env, tmp_path):
    dialog = env.open("Reports", "Glyph Table CSV", "GlyphTable")
    dialog.choose_button.clicked.emit()
    first = dialog.chooser
    assert first.opened == 1 and first.init_args[1:] == (
        "Export glyph table", "glyphs.csv", "CSV files (*.csv)",
    ), first.init_args
    first.fileSelected.emit(str(tmp_path / "chosen.csv"))
    assert dialog.path.text == str(tmp_path / "chosen.csv") and dialog.export_button.enabled, "expected: dialog.path.text == str(tmp_path / 'chosen.csv') and dialog.export_..."
    dialog.choose_button.clicked.emit()
    assert dialog.chooser is not first and not first.visible, "the old chooser is closed"
    dialog.close_button.clicked.emit()
    assert dialog.chooser is None and dialog.deleted, "Close releases the chooser"


def test_csv_when_font_missing_then_nothing_can_be_exported(no_font):
    dialog = no_font.open("Reports", "Glyph Table CSV", "GlyphTable")
    assert dialog.subtitle.text == "Open a font first.", dialog.subtitle.text
    assert not dialog.copy_button.enabled and not dialog.export_button.enabled, "expected: not dialog.copy_button.enabled and (not dialog.export_button.enabled)"
    assert dialog.rows == [] and dialog.package_id is None, "expected: dialog.rows == [] and dialog.package_id is None"


def test_csv_when_scan_fails_then_exports_are_disabled(env):
    dialog = env.open("Reports", "Glyph Table CSV", "GlyphTable")
    fail_font(env)
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.refresh()
    assert dialog.rows == [] and not dialog.copy_button.enabled, "expected: dialog.rows == [] and (not dialog.copy_button.enabled)"
    assert dialog.table.rowCount == 0 and dialog.package_id is None, "expected: dialog.table.rowCount == 0 and dialog.package_id is None"


def test_csv_core_when_selection_unreadable_then_it_is_empty_and_unknown_names_skipped(env):
    module = env.load("Reports", "Glyph Table CSV")
    assert module.selected_names() == [], "nothing selected yet"
    del env.FL.fl.font
    assert module.selected_names() == [], "an unreadable Font window yields no names"
    header, rows = module.table(env.package, ["nope", "A"])
    assert [row[0] for row in rows] == ["A"] and header[0] == "glyph", "expected: [row[0] for row in rows] == ['A'] and header[0] == 'glyph'"
    env.package.glyphs["A"].layers.pop("Regular")
    assert module.table(env.package, ["A"])[1][0][2] == "", "a missing layer leaves a blank width"


# ---------------------------------------------------------------- Label Statistics
def test_labels_when_opened_then_marks_and_suffixes_are_counted(env):
    dialog = env.open("Reports", "Label Statistics", "LabelStatistics")
    check_clean(dialog)
    assert dialog.mark_table.texts() == [
        ["Unmarked", "7"], ["Green (hue 99°)", "1"], ["Grey 100", "1"], ["Red (hue 4°)", "1"],
    ], dialog.mark_table.texts()
    assert dialog.suffix_table.texts() == [
        ["(no suffix)", "8"], [".ss01", "1"], [".zero", "1"],
    ], dialog.suffix_table.texts()
    assert dialog.subtitle.text == (
        "10 glyphs: 3 marked in 3 colours, 2 with a suffix in 2 sets. "
        "Click a row to select those glyphs."
    ), dialog.subtitle.text


def test_labels_when_row_clicked_then_group_is_selected_with_optional_add(env):
    dialog = env.open("Reports", "Label Statistics", "LabelStatistics")
    dialog.mark_table.cellClicked.emit(1, 0)
    check_clean(dialog)
    assert selected_names(env) == ["A"], "the green group holds glyph A"
    assert dialog.status.text == "Selected 1 glyph" and dialog.last_result["group"] == 100, "expected: dialog.status.text == 'Selected 1 glyph' and dialog.last_result['gr..."
    env.select("x")
    dialog.add.setChecked(True)
    dialog.suffix_table.cellClicked.emit(1, 0)
    assert selected_names(env) == ["A.ss01", "x"], "Add keeps the current selection"
    assert dialog.status.text == "Selected 2 glyphs", "expected: dialog.status.text == 'Selected 2 glyphs'"
    dialog.suffix_table.cellClicked.emit(99, 0)
    assert selected_names(env) == ["A.ss01", "x"], "an out-of-range row changes nothing"


def test_labels_when_font_replaced_then_group_selection_is_refused(env):
    dialog = env.open("Reports", "Label Statistics", "LabelStatistics")
    replace_font(env)
    dialog.mark_table.cellClicked.emit(1, 0)
    assert "stale font" in dialog.slot_error, dialog.slot_error
    assert selected_names(env) == [], "expected: selected_names(env) == []"


def test_labels_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Reports", "Label Statistics", "LabelStatistics")
    assert dialog.subtitle.text == "Open a font first." and dialog.package_id is None, "expected: dialog.subtitle.text == 'Open a font first.' and dialog.package_id ..."
    with pytest.raises(ValueError, match="Refresh the report"):
        dialog.select_group([], 0)


def test_labels_when_font_has_no_glyphs_then_subtitle_asks_for_a_font(env):
    env.fontlab.CurrentFont = lambda: NS(glyphs=[])
    dialog = env.open("Reports", "Label Statistics", "LabelStatistics")
    assert dialog.subtitle.text == "Open a font first." and dialog.mark_table.rowCount == 0, "expected: dialog.subtitle.text == 'Open a font first.' and dialog.mark_table...."


def test_labels_when_scan_fails_then_tables_are_cleared(env):
    dialog = env.open("Reports", "Label Statistics", "LabelStatistics")
    fail_font(env)
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.refresh()
    assert dialog.marks == [] and dialog.suffixes == [] and dialog.package_id is None, "expected: dialog.marks == [] and dialog.suffixes == [] and (dialog.package_id..."
    assert dialog.mark_table.rowCount == 0, "expected: dialog.mark_table.rowCount == 0"


def test_labels_core_when_marks_and_names_given_then_colours_and_labels_resolve(env):
    module = env.load("Reports", "Label Statistics")
    assert module.mark_color(0) is None and module.mark_label(0) == "Unmarked", "expected: module.mark_color(0) is None and module.mark_label(0) == 'Unmarked'"
    assert module.mark_color(5).hsl == (4, 200, 150), "marks are hue plus one"
    assert module.mark_color(1100).args == (125, 125, 125), "grey marks sit above 1000"
    assert module.mark_label(1100) == "Grey 100", "expected: module.mark_label(1100) == 'Grey 100'"
    assert module.mark_label(341) == "Red (hue 340°)", "late hues wrap to red"
    assert module.mark_label(46) == "Yellow (hue 45°)", "expected: module.mark_label(46) == 'Yellow (hue 45°)'"
    assert module.suffix_of("a.ss01.sc") == ".ss01.sc" and module.suffix_of(".notdef") == "", "expected: module.suffix_of('a.ss01.sc') == '.ss01.sc' and module.suffix_of('...."
    marks, suffixes = module.statistics([("a", 1), ("b", 1), ("c.alt", 0)])
    assert marks == [(1, ["a", "b"]), (0, ["c.alt"])], marks
    assert suffixes == [("", ["a", "b"]), (".alt", ["c.alt"])], suffixes


def test_labels_core_when_swatch_drawn_then_painter_is_always_released(env):
    module = env.load("Reports", "Label Statistics")
    module.swatch(0)
    module.swatch(5)
    painters = env.qt.QtGui.QPainter.created
    assert len(painters) == 2 and all(p.ended for p in painters), "painters must be ended"
    assert module.font_labels()[0] == (".notdef", 0), "expected: module.font_labels()[0] == ('.notdef', 0)"
    env.fontlab.CurrentFont = lambda: None
    assert module.font_labels() == [], "no font means no labels"


# ---------------------------------------------------------------- Live Glyph Info
def test_live_when_glyph_selected_then_every_master_row_is_shown(env):
    env.select("A")
    dialog = env.open("Reports", "Live Glyph Info", "GlyphInfoLive")
    check_clean(dialog)
    assert dialog.glyph_label.text == "A  U+0041", "expected: dialog.glyph_label.text == 'A U+0041'"
    assert dialog.table.texts() == [
        ["Regular", "600", "50", "150", "50, 0, 400, 400", "1", "4", "–", "0"],
        ["Bold", "620", "50", "170", "50, 0, 400, 400", "2", "8", "–", "2"],
    ], dialog.table.texts()
    assert dialog.table.item(0, 5).foreground is not None, "differing contour counts glow"
    assert dialog.table.item(0, 7).foreground is None, "equal component lists do not"
    assert dialog.status.text == "Updated 12:34:56" and dialog.shown_name == "A", "expected: dialog.status.text == 'Updated 12:34:56' and dialog.shown_name == 'A'"
    assert dialog.timer.active and dialog.timer.interval == 500, "polling starts at once"


def test_live_when_timer_ticks_then_selection_change_is_followed(env):
    env.select("A")
    dialog = env.open("Reports", "Live Glyph Info", "GlyphInfoLive")
    env.select("space")
    dialog.timer.timeout.emit()
    check_clean(dialog)
    assert dialog.glyph_label.text == "space  U+0020", "expected: dialog.glyph_label.text == 'space U+0020'"
    assert dialog.table.texts()[0][1:5] == ["250", "–", "–", "empty"], (
        "an empty layer shows dashes and 'empty'"
    )
    dialog.pause.setChecked(True)
    assert not dialog.timer.active, "Pause stops polling"
    dialog.pause.setChecked(False)
    assert dialog.timer.active, "unchecking Pause resumes polling"


def test_live_when_nothing_selected_then_current_glyph_or_prompt_is_used(env):
    dialog = env.open("Reports", "Live Glyph Info", "GlyphInfoLive")
    assert dialog.subtitle.text == "Select a glyph in the Font window.", dialog.subtitle.text
    assert dialog.glyph_label.text == "–" and dialog.table.rowCount == 0, "expected: dialog.glyph_label.text == '–' and dialog.table.rowCount == 0"
    env.current_glyph = NS(name="acute")
    dialog.refresh()
    assert dialog.glyph_label.text == "acute  U+00B4", "the current glyph is the fallback"
    assert dialog.table.texts() == [
        ["Regular", "300", "10", "190", "10, 600, 100, 100", "1", "4", "–", "0"],
        ["Bold", "300", "–", "–", "empty", "0", "0", "–", "0"],
    ], dialog.table.texts()


def test_live_when_font_window_unreadable_then_current_glyph_is_used(env):
    def broken(index):
        raise RuntimeError("no Font window")

    env.FL.fl.Selected = broken
    env.current_glyph = NS(name="A")
    dialog = env.open("Reports", "Live Glyph Info", "GlyphInfoLive")
    assert dialog.glyph_label.text == "A  U+0041", dialog.glyph_label.text


def test_live_when_no_font_then_open_font_prompt(no_font):
    dialog = no_font.open("Reports", "Live Glyph Info", "GlyphInfoLive")
    assert dialog.subtitle.text == "Open a font and select a glyph.", "expected: dialog.subtitle.text == 'Open a font and select a glyph.'"
    assert dialog.package_id is None, "expected: dialog.package_id is None"


def test_live_when_refresh_fails_then_rows_are_cleared_and_timer_stops_on_close(env):
    env.select("A")
    dialog = env.open("Reports", "Live Glyph Info", "GlyphInfoLive")

    def broken(name):
        raise RuntimeError("native read failed")

    env.package.findName = broken
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.refresh()
    assert dialog.rows == [] and dialog.glyph_label.text == "–" and dialog.package_id is None, "expected: dialog.rows == [] and dialog.glyph_label.text == '–' and (dialog.pa..."
    dialog.timer.timeout.emit()
    assert "native read failed" in dialog.slot_error, "a tick contains the failure"
    dialog.close_button.clicked.emit()
    assert not dialog.timer.active, "Close must stop the poll timer"


def test_live_core_when_layer_is_empty_or_missing_then_rows_follow(env):
    module = env.load("Reports", "Live Glyph Info")
    assert module.glyph_info(env.package, "missing") == [], "expected: module.glyph_info(env.package, 'missing') == []"
    del env.package.glyphs["A"].layers["Regular"]
    assert [m for m, _ in module.glyph_info(env.package, "A")] == ["Bold"], "expected: [m for m, _ in module.glyph_info(env.package, 'A')] == ['Bold']"
    info = module.layer_info(Layer(300))
    assert info[:4] == ["300", "–", "–", "empty"], info


# ---------------------------------------------------------------- Nodes Near Zones
def test_zones_when_glyph_selected_then_near_misses_are_listed_per_master(env):
    env.select("x")
    dialog = env.open("Reports", "Nodes Near Zones", "NodesNearZones")
    check_clean(dialog)
    assert dialog.table.texts() == [
        ["x · Regular", "baseline 0", "10, 3", "3", "+3"],
        ["x · Regular", "x-height 500", "20, 497", "497", "-3"],
        ["x · Bold", "baseline 0", "10, 3", "3", "+3"],
        ["x · Bold", "x-height 510", "50, 506", "506", "-4"],
    ], "on-curve nodes only; the off-curve 503 and the component are ignored"
    assert dialog.status.text == "4 near misses in 1 glyph", dialog.status.text
    assert dialog.scope.items[0] == "Selected glyphs (1)" and dialog.scope.currentIndex == 0, "expected: dialog.scope.items[0] == 'Selected glyphs (1)' and dialog.scope.cur..."
    assert "1–4 units off baseline" in dialog.subtitle.text, "expected: '1–4 units off baseline' in dialog.subtitle.text"


def test_zones_when_tolerance_changes_then_rows_follow(env):
    env.select("x")
    dialog = env.open("Reports", "Nodes Near Zones", "NodesNearZones")
    dialog.tolerance.setValue(3)
    assert dialog.status.text == "3 near misses in 1 glyph", dialog.status.text
    dialog.tolerance.setValue(1)
    assert dialog.status.text == "0 near misses in 0 glyphs" and not dialog.select_button.enabled, "expected: dialog.status.text == '0 near misses in 0 glyphs' and (not dialog.s..."
    assert dialog.table.rowCount == 0, "expected: dialog.table.rowCount == 0"
    dialog.tolerance.setValue(3)
    dialog.table.selected_rows = [0]
    dialog.select_button.clicked.emit()
    check_clean(dialog)
    assert selected_names(env) == ["x"] and dialog.status.text == "Selected 1 glyph", "expected: selected_names(env) == ['x'] and dialog.status.text == 'Selected 1 ..."


def test_zones_when_nothing_selected_then_all_glyphs_are_scanned(env):
    dialog = env.open("Reports", "Nodes Near Zones", "NodesNearZones")
    assert dialog.scope.currentIndex == 1, "an empty selection falls back to all glyphs"
    assert dialog.status.text == "4 near misses in 1 glyph", dialog.status.text
    assert dialog.subtitle.text.startswith("10 glyphs × 2 masters checked"), "expected: dialog.subtitle.text.startswith('10 glyphs × 2 masters checked')"
    dialog.table.cellDoubleClicked.emit(2, 0)
    assert selected_names(env) == ["x"], "expected: selected_names(env) == ['x']"
    dialog.select_button.clicked.emit()
    assert selected_names(env) == ["x"], "all rows name the same glyph"
    dialog.table.cellDoubleClicked.emit(40, 0)
    assert selected_names(env) == [], "an out-of-range row selects nothing"


def test_zones_when_single_near_miss_then_status_is_singular(env):
    env.package.glyphs["x"].layers["Bold"] = Layer(
        500, [Shape([Contour([Node(0, 2)])])], (0, 2, 0, 0)
    )
    env.package.glyphs["x"].layers["Regular"] = Layer(500)
    dialog = env.open("Reports", "Nodes Near Zones", "NodesNearZones")
    assert dialog.status.text == "1 near miss in 1 glyph", dialog.status.text


def test_zones_when_font_replaced_then_selection_is_refused(env):
    dialog = env.open("Reports", "Nodes Near Zones", "NodesNearZones")
    replace_font(env)
    dialog.select_button.clicked.emit()
    assert "stale font" in dialog.slot_error, dialog.slot_error
    assert selected_names(env) == [], "expected: selected_names(env) == []"


def test_zones_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Reports", "Nodes Near Zones", "NodesNearZones")
    assert dialog.subtitle.text == "Open a font first." and not dialog.select_button.enabled, "expected: dialog.subtitle.text == 'Open a font first.' and (not dialog.select..."
    with pytest.raises(ValueError, match="Refresh the report"):
        dialog.select_rows()


def test_zones_when_scan_fails_then_results_are_cleared(env):
    dialog = env.open("Reports", "Nodes Near Zones", "NodesNearZones")
    fail_font(env)
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.rescan()
    assert dialog.rows == [] and dialog.package_id is None and dialog.table.rowCount == 0, "expected: dialog.rows == [] and dialog.package_id is None and (dialog.table.r..."


def test_zones_core_when_points_and_metrics_given_then_only_near_misses_remain(env):
    module = env.load("Reports", "Nodes Near Zones")
    hits = module.near_misses([(0, 0), (1, 3.5), (2, 10), (3, -4)], [("baseline", 0.0)], 4)
    assert hits == [("baseline", 0.0, 1, 3.5), ("baseline", 0.0, 3, -4)], hits
    layer = Layer(
        100,
        [
            Shape([Contour([Node(1, 2), Node(3, 4, on=False)])], dx=10),
            Shape([Contour([Node(9, 9)])], base="acute"),
        ],
    )
    assert module.on_curve_points(layer) == [(11, 2)], (
        "the transform is applied and off-curve nodes and components are skipped"
    )
    metrics = module.master_metrics(env.package, "Bold")
    assert metrics[1:3] == [("x-height", 510), ("cap height", 710)], metrics
    assert module.selected_names() == [], "expected: module.selected_names() == []"


# ---------------------------------------------------------------- Open Contours
def test_open_contours_when_opened_then_gap_between_end_nodes_is_reported(env):
    dialog = env.open("Reports", "Open Contours", "OpenContours")
    check_clean(dialog)
    assert dialog.table.texts() == [["A", "Bold", "#2", "4", "100.0"]], dialog.table.texts()
    assert dialog.subtitle.text == "1 open contour in 1 glyph across 2 masters.", "expected: dialog.subtitle.text == '1 open contour in 1 glyph across 2 masters.'"
    assert dialog.status.text == "Double-click a row to select that glyph.", "expected: dialog.status.text == 'Double-click a row to select that glyph.'"
    assert dialog.table.item(0, 4).foreground is not None, "a real gap is highlighted"
    dialog.select_button.clicked.emit()
    assert selected_names(env) == ["A"] and dialog.status.text == "Selected 1 glyph", "expected: selected_names(env) == ['A'] and dialog.status.text == 'Selected 1 ..."
    dialog.table.cellDoubleClicked.emit(0, 0)
    assert selected_names(env) == ["A"], "expected: selected_names(env) == ['A']"


def test_open_contours_when_all_closed_then_report_says_none(env):
    for contour in env.package.glyphs["A"].layers["Bold"].shapes[0].getContours():
        contour.closed = True
    dialog = env.open("Reports", "Open Contours", "OpenContours")
    assert dialog.subtitle.text == "No open contours on any of 2 masters.", "expected: dialog.subtitle.text == 'No open contours on any of 2 masters.'"
    assert dialog.status.text == "" and not dialog.select_button.enabled, "expected: dialog.status.text == '' and (not dialog.select_button.enabled)"


def test_open_contours_when_contour_has_one_node_then_gap_is_zero(env):
    env.package.glyphs["x"].layers["Bold"] = Layer(
        500, [Shape([Contour([Node(5, 5)], closed=False)])]
    )
    dialog = env.open("Reports", "Open Contours", "OpenContours")
    assert ["x", "Bold", "#1", "1", "0.0"] in dialog.table.texts(), dialog.table.texts()
    assert dialog.subtitle.text == "2 open contours in 2 glyphs across 2 masters.", "expected: dialog.subtitle.text == '2 open contours in 2 glyphs across 2 maste..."


def test_open_contours_when_layer_missing_then_master_is_skipped(env):
    del env.package.glyphs["A"].layers["Bold"]
    dialog = env.open("Reports", "Open Contours", "OpenContours")
    assert dialog.table.texts() == [] and dialog.subtitle.text.startswith("No open contours"), "expected: dialog.table.texts() == [] and dialog.subtitle.text.startswith('No ..."


def test_open_contours_when_font_replaced_then_selection_is_refused(env):
    dialog = env.open("Reports", "Open Contours", "OpenContours")
    replace_font(env)
    dialog.select_button.clicked.emit()
    assert "no longer current" in dialog.slot_error, dialog.slot_error
    assert selected_names(env) == [], "expected: selected_names(env) == []"


def test_open_contours_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Reports", "Open Contours", "OpenContours")
    assert dialog.status.text == "No font open." and dialog.subtitle.text == "Open a font first.", "expected: dialog.status.text == 'No font open.' and dialog.subtitle.text == '..."
    with pytest.raises(ValueError, match="Refresh the report"):
        dialog.select_rows()


def test_open_contours_when_scan_fails_then_results_are_cleared(env):
    dialog = env.open("Reports", "Open Contours", "OpenContours")
    fail_font(env)
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.rescan()
    assert dialog.rows == [] and dialog.package_id is None and dialog.table.rowCount == 0, "expected: dialog.rows == [] and dialog.package_id is None and (dialog.table.r..."


# ---------------------------------------------------------------- Unicode Coverage
def test_coverage_when_opened_then_blocks_touched_by_the_font_are_listed(env):
    dialog = env.open("Reports", "Unicode Coverage", "Coverage")
    check_clean(dialog)
    assert dialog.table.texts() == [
        ["Basic Latin", "0000–007F", "", "4 / 128"],
        ["Latin-1 Supplement", "0080–00FF", "", "2 / 128"],
        ["General Punctuation", "2000–206F", "", "1 / 111"],
        ["Currency Symbols", "20A0–20CF", "", "1 / 33"],
    ], dialog.table.texts()
    assert dialog.table.cell_widgets[0, 2].last_call("setFormat") == ("3%",), (
        "4 of 128 code points is 3 percent"
    )
    assert dialog.status.text == "4 blocks listed · 1 code points outside planes 0–1", "expected: dialog.status.text == '4 blocks listed · 1 code points outside plan..."
    assert dialog.subtitle.text == (
        "9 code points in 4 blocks; 0 complete. Double-click a block to select its glyphs."
    ), dialog.subtitle.text


def test_coverage_when_untouched_blocks_shown_then_every_block_is_listed(env):
    module = env.load("Reports", "Unicode Coverage")
    dialog = module.Coverage()
    dialog.show_all.setChecked(True)
    check_clean(dialog)
    assert dialog.table.rowCount == len(module.BLOCKS), "one row per Unicode block"
    assert dialog.status.text.startswith(f"{len(module.BLOCKS)} blocks listed"), "expected: dialog.status.text.startswith(f'{len(module.BLOCKS)} blocks listed')"


def test_coverage_when_block_has_no_assigned_characters_then_bar_shows_a_dash(env, monkeypatch):
    module = env.load("Reports", "Unicode Coverage")
    monkeypatch.setattr(module, "assigned", lambda start, end: 0)
    dialog = module.Coverage()
    assert dialog.table.cell_widgets[0, 2].last_call("setFormat") == ("–",), "expected: dialog.table.cell_widgets[0, 2].last_call('setFormat') == ('–',)"
    assert dialog.table.texts()[0][3] == "4 / 0", "expected: dialog.table.texts()[0][3] == '4 / 0'"


def test_coverage_when_block_complete_then_it_is_counted_complete(monkeypatch, real_app, app_sources):
    codes = range(0xFE00, 0xFE10)
    glyphs = [
        Glyph(f"vs{i}", [code], {"Regular": Layer(0), "Bold": Layer(0)})
        for i, code in enumerate(codes)
    ]
    env = ReportEnv(monkeypatch, real_app, ReportPackage(glyphs))
    dialog = env.open("Reports", "Unicode Coverage", "Coverage")
    assert dialog.table.texts() == [["Variation Selectors", "FE00–FE0F", "", "16 / 16"]], "expected: dialog.table.texts() == [['Variation Selectors', 'FE00–FE0F', '', '..."
    assert "; 1 complete." in dialog.subtitle.text, dialog.subtitle.text
    assert dialog.table.cell_widgets[0, 2].last_call("setFormat") == ("100%",), "expected: dialog.table.cell_widgets[0, 2].last_call('setFormat') == ('100%',)"
    assert dialog.status.text == "1 blocks listed", "expected: dialog.status.text == '1 blocks listed'"


def test_coverage_when_block_double_clicked_then_its_glyphs_are_selected(env):
    dialog = env.open("Reports", "Unicode Coverage", "Coverage")
    dialog.table.cellDoubleClicked.emit(0, 0)
    check_clean(dialog)
    assert selected_names(env) == ["A", "period", "space", "x"], selected_names(env)
    assert dialog.status.text == "Basic Latin: selected 4 glyphs", dialog.status.text
    dialog.table.cellDoubleClicked.emit(3, 0)
    assert selected_names(env) == ["Euro"] and dialog.status.text == (
        "Currency Symbols: selected 1 glyph"
    ), "expected: selected_names(env) == ['Euro'] and dialog.status.text == 'Currency..."
    dialog.table.cellDoubleClicked.emit(50, 0)
    assert selected_names(env) == ["Euro"], "an out-of-range row changes nothing"


def test_coverage_when_font_replaced_then_selection_is_refused(env):
    dialog = env.open("Reports", "Unicode Coverage", "Coverage")
    replace_font(env)
    dialog.table.cellDoubleClicked.emit(0, 0)
    assert "stale font" in dialog.slot_error, dialog.slot_error
    assert selected_names(env) == [], "expected: selected_names(env) == []"


def test_coverage_when_no_font_then_open_font_first(no_font):
    dialog = no_font.open("Reports", "Unicode Coverage", "Coverage")
    assert dialog.subtitle.text == "Open a font first." and dialog.package_id is None, "expected: dialog.subtitle.text == 'Open a font first.' and dialog.package_id ..."
    with pytest.raises(ValueError, match="Refresh the report"):
        dialog.select_block(0)


def test_coverage_when_font_has_no_encoded_glyphs_then_subtitle_says_so(monkeypatch, real_app, app_sources):
    glyphs = [Glyph("a.alt", [], {"Regular": Layer(0), "Bold": Layer(0)})]
    env = ReportEnv(monkeypatch, real_app, ReportPackage(glyphs))
    dialog = env.open("Reports", "Unicode Coverage", "Coverage")
    assert dialog.subtitle.text == "Open a font with encoded glyphs first.", "expected: dialog.subtitle.text == 'Open a font with encoded glyphs first.'"
    assert dialog.table.rowCount == 0 and dialog.status.text == "0 blocks listed", "expected: dialog.table.rowCount == 0 and dialog.status.text == '0 blocks listed'"


def test_coverage_when_scan_fails_then_results_are_cleared(env):
    dialog = env.open("Reports", "Unicode Coverage", "Coverage")
    fail_font(env)
    with pytest.raises(RuntimeError, match="native read failed"):
        dialog.refresh()
    assert dialog.rows == [] and dialog.codes == {} and dialog.package_id is None, "expected: dialog.rows == [] and dialog.codes == {} and (dialog.package_id is ..."


def test_coverage_core_when_codes_given_then_blocks_and_outliers_are_split(env):
    module = env.load("Reports", "Unicode Coverage")
    rows, outside = module.coverage([65, 0x20000])
    assert rows == [(0, 0x7F, "Basic Latin", 1, 128)], rows
    assert outside == [0x20000], "plane 2 is outside the listed blocks"
    assert module.assigned(0x41, 0x5A) == 26, "A to Z are all assigned"
    env.fontlab.CurrentFont = lambda: None
    assert module.font_codes() == {}, "no font means no code points"


# ---------------------------------------------------------------- shared lifecycle
REPORTS = [
    "Empty Glyphs",
    "Font Overview",
    "Glyph Table CSV",
    "Label Statistics",
    "Live Glyph Info",
    "Nodes Near Zones",
    "Open Contours",
    "Unicode Coverage",
]


@pytest.mark.parametrize("title", REPORTS)
def test_reports_when_closed_then_registry_and_slots_are_released(env, title):
    module = env.load("Reports", title)
    dialog = module.main()
    assert sys._fontlab_samples[module.KEY] is dialog, "main registers the report"
    dialog.close_button.clicked.emit()
    assert sys._fontlab_samples == {} and dialog.deleted, "Close releases and deletes"
    assert dialog._connections == [], "Close disconnects every owned slot"


@pytest.mark.parametrize("title", REPORTS)
def test_reports_when_run_as_script_then_main_opens_the_dialog(env, title):
    namespace = runpy.run_path(str(ROOT / "Scripts/Reports" / f"{title}.py"), run_name="__main__")
    assert namespace["KEY"] in sys._fontlab_samples, "running as a script opens the report"
