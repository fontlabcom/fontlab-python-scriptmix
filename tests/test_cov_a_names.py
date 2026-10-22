# this_file: tests/test_cov_a_names.py
# SPDX-License-Identifier: Apache-2.0
"""Coverage round A: the five Names panels on the real shared Names dialog."""

from __future__ import annotations

import runpy
from types import SimpleNamespace as NS
from typing import Any

import pytest
from _cov_a_support import ROOT, Host, host  # noqa: F401

NAMES = "Names/"
PACKAGE_ID = 11


def state_for(host: Host, glyphs: list[tuple[str, list[int]]], selection: list[str] | None = None) -> NS:
    """Open an owned font and return the state the scripting doubles read."""
    host.package = NS(id=PACKAGE_ID, isNull=False, master="Regular")
    state = NS(
        glyphs=glyphs,
        selection=list(selection or []),
        selects=[],
        select_return=None,
        copied=[],
    )
    return state


def scripting(state: NS) -> dict[str, Any]:
    """Shared-helper doubles: font reads, selection reads and the Font window writer."""

    def select_glyphs(names: Any, *, package_id: int, add: bool = False) -> list[str]:
        state.selects.append((list(names), package_id, add))
        return list(names) if state.select_return is None else state.select_return

    return {
        "names_font_glyphs": lambda: [(n, list(c)) for n, c in state.glyphs],
        "names_selected_names": lambda: list(state.selection),
        "names_font_window_selection": lambda: list(state.selection),
        "select_glyphs": select_glyphs,
    }


def clipboard(tool: Any) -> list[str]:
    copied: list[str] = []
    tool.QtGui.QApplication = NS(clipboard=lambda: NS(setText=copied.append))
    return copied


def load(host: Host, script: str, state: NS | None = None) -> Any:
    return host.load(NAMES + script, scripting=scripting(state) if state else None)


# ---- Case Pairs ------------------------------------------------------------------

CASE_GLYPHS = [("a", [97]), ("A", [65]), ("a.sc", []), ("A.sc", []), ("one", [49]), ("ae", [0xE6]), ("eszett", [0xDF])]


@pytest.mark.parametrize(
    ("char", "expected"), [("a", "A"), ("A", "a"), ("ß", ""), ("1", ""), ("İ", ""), ("é", "É")]
)
def test_swap_case_when_char_then_single_char_counterpart_or_empty(host, char, expected):
    tool = load(host, "Case Pairs.py")
    assert tool.swap_case(char) == expected, f"{char!r} counterpart"


def test_counterpart_when_encoded_then_how_describes_mapping_or_reason(host):
    tool = load(host, "Case Pairs.py")
    codes_of, by_code = tool.index(CASE_GLYPHS)
    assert tool.counterpart("a", codes_of, by_code) == ("A", "a → A"), "counterpart when encoded then how describes mapping or reason: expected tool.counterpart('a', codes_of, by_code) == ('A', 'a → A')"
    assert tool.counterpart("ae", codes_of, by_code) == (None, "æ has no counterpart in the font"), "counterpart when encoded then how describes mapping or reason: unexpected result"
    assert tool.counterpart("one", codes_of, by_code) == (None, "no case"), "counterpart when encoded then how describes mapping or reason: expected tool.counterpart('one', codes_of, by_code) == (None, 'no case')"
    assert tool.counterpart("eszett", codes_of, by_code) == (None, "no case"), "counterpart when encoded then how describes mapping or reason: expected tool.counterpart('eszett', codes_of, by_code) == (None, 'no case')"


def test_counterpart_when_unencoded_then_via_base_suffix_or_unencoded(host):
    tool = load(host, "Case Pairs.py")
    codes_of, by_code = tool.index(CASE_GLYPHS)
    assert tool.counterpart("a.sc", codes_of, by_code) == ("A.sc", "via a → A"), "counterpart when unencoded then via base suffix or unencoded: expected tool.counterpart('a.sc', codes_of, by_code) == ('A.sc', 'via a → A')"
    assert tool.counterpart("ghost", codes_of, by_code) == (None, "unencoded"), "counterpart when unencoded then via base suffix or unencoded: expected tool.counterpart('ghost', codes_of, by_code) == (None, 'unencoded')"
    assert tool.counterpart("one.sc", {"one": [49]}, {49: "one"}) == (None, "unencoded"), "counterpart when unencoded then via base suffix or unencoded: unexpected result"


def test_index_when_two_glyphs_share_code_then_first_wins(host):
    tool = load(host, "Case Pairs.py")
    codes_of, by_code = tool.index([("a", [97]), ("a.alt", [97])])
    assert by_code[97] == "a" and codes_of["a.alt"] == [97], "index when two glyphs share code then first wins: expected by_code[97] == 'a' and codes_of['a.alt'] == [97]"


def test_case_pairs_dialog_when_selection_then_rows_and_select_counterparts(host):
    state = state_for(host, CASE_GLYPHS, ["a", "a.sc", "one", "ae"])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    assert [dialog.table.row_texts(r) for r in range(4)] == [
        ["a", "A", "a → A"],
        ["a.sc", "A.sc", "via a → A"],
        ["one", "–", "no case"],
        ["ae", "–", "æ has no counterpart in the font"],
    ], "case pairs dialog when selection then rows and select counterparts: unexpected result"
    assert dialog.subtitle.text == "2 of 4 selected glyphs have a case counterpart in this font.", "case pairs dialog when selection then rows and select counterparts: unexpected result"
    assert dialog.status.text == "2 counterparts" and dialog.select_button.isEnabled(), "case pairs dialog when selection then rows and select counterparts: unexpected result"
    dialog.select_button.clicked.emit()
    assert state.selects == [(["A", "A.sc"], PACKAGE_ID, False)], "case pairs dialog when selection then rows and select counterparts: expected state.selects == [(['A', 'A.sc'], PACKAGE_ID, False)]"
    assert dialog.last_result == {"selected": ["A", "A.sc"]}, "case pairs dialog when selection then rows and select counterparts: expected dialog.last_result == {'selected': ['A', 'A.sc']}"
    assert dialog.status.text == "Selected 2 glyphs", "case pairs dialog when selection then rows and select counterparts: expected dialog.status.text == 'Selected 2 glyphs'"


def test_case_pairs_dialog_when_keep_checked_then_originals_added(host):
    state = state_for(host, CASE_GLYPHS, ["a", "one"])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    dialog.keep.setChecked(True)
    dialog.select_counterparts()
    assert state.selects[-1][0] == ["A", "a", "one"], "Partners first, then the scanned originals"
    state.select_return = ["A"]
    dialog.select_counterparts()
    assert dialog.status.text == "Selected 1 glyph", "Singular wording for one glyph"


def test_case_pairs_dialog_when_single_counterpart_then_singular_status(host):
    state = state_for(host, CASE_GLYPHS, ["a"])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    assert dialog.status.text == "1 counterpart", "case pairs dialog when single counterpart then singular status: expected dialog.status.text == '1 counterpart'"


def test_case_pairs_dialog_when_no_selection_then_hint_and_select_disabled(host):
    state = state_for(host, CASE_GLYPHS, [])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    assert dialog.subtitle.text == "Select glyphs in the Font window, then click Reload selection.", "case pairs dialog when no selection then hint and select disabled: unexpected result"
    assert not dialog.select_button.isEnabled() and dialog.table.rowCount == 0, 'case pairs dialog when no selection then hint and select disabled: expected not dialog.select_button.isEnabled() and dialog.table.rowCount == 0'


def test_case_pairs_dialog_when_selection_changes_then_reload_picks_it_up(host):
    state = state_for(host, CASE_GLYPHS, [])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    state.selection = ["A"]
    dialog.reload_button.clicked.emit()
    assert dialog.pairs == [("A", "a", "A → a")] and dialog.select_button.isEnabled(), "case pairs dialog when selection changes then reload picks it up: unexpected result"


def test_case_pairs_dialog_when_no_font_then_open_font_message(host):
    state = state_for(host, [], [])
    host.package = None
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    assert dialog.subtitle.text == "Open a font first." and not dialog.select_button.isEnabled(), "case pairs dialog when no font then open font message: unexpected result"
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.select_counterparts()


def test_case_pairs_dialog_when_font_closed_after_scan_then_selection_refused(host):
    state = state_for(host, CASE_GLYPHS, ["a"])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    host.package = None
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.select_counterparts()
    assert state.selects == [], "A stale snapshot never reaches the Font window"
    assert dialog.pairs == [] and not dialog.select_button.isEnabled(), "Stale results are cleared"


def test_case_pairs_font_access_wrappers_when_called_then_use_shared_helpers(host):
    state = state_for(host, CASE_GLYPHS, ["a"])
    tool = load(host, "Case Pairs.py", state)
    assert tool.selected_names() == ["a"] and tool.font_glyphs()[0] == ("a", [97]), "case pairs font access wrappers when called then use shared helpers: unexpected result"


def test_case_pairs_close_button_when_clicked_then_dialog_closes(host):
    state = state_for(host, CASE_GLYPHS, ["a"])
    tool = load(host, "Case Pairs.py", state)
    dialog = tool.CasePairs(None)
    dialog.close_button.clicked.emit()
    assert dialog.closed, "Close asks the dialog to close"


def test_case_pairs_main_when_run_as_script_then_window_opens(host):
    state = state_for(host, CASE_GLYPHS, ["a"])
    load(host, "Case Pairs.py", state)
    runpy.run_path(str(ROOT / "Scripts/Names/Case Pairs.py"), run_name="__main__")
    assert "names_case_pairs" in host.windows(), "case pairs main when run as script then window opens: expected 'names_case_pairs' in host.windows()"


# ---- Glyph Finder ----------------------------------------------------------------

FIND_GLYPHS = [("a", [97]), ("eacute", [0xE9]), ("eacute.ss01", []), ("A.alt", []), ("euro", [0x20AC]), ("dot", [0x2E])]


@pytest.mark.parametrize(
    ("query", "kind", "names"),
    [
        ("U+00E9", "code point", ["eacute"]),
        ("uni20AC", "code point", ["euro"]),
        ("0x61", None, None),  # too short for a code: treated as a name
        ("é", "character", ["eacute"]),
        (".", "character", ["dot"]),
        ("*.ss0?", "pattern", ["eacute.ss01"]),
        ("a", "name or character", ["a", "eacute", "eacute.ss01", "A.alt"]),
        ("ACUTE", "name", ["eacute", "eacute.ss01"]),
    ],
)
def test_find_when_query_kinds_then_matching_glyphs(host, query, kind, names):
    tool = load(host, "Glyph Finder.py")
    found_kind, found = tool.find(FIND_GLYPHS, query)
    if kind is None:
        assert found_kind == "name" and found == [], "A short hex string is not a code point"
        return
    assert found_kind == kind and [n for n, _ in found] == names, f"query {query!r}"


def test_find_when_empty_query_then_everything(host):
    tool = load(host, "Glyph Finder.py")
    kind, found = tool.find(FIND_GLYPHS, "   ")
    assert kind == "all" and found == FIND_GLYPHS, "find when empty query then everything: expected kind == 'all' and found == FIND_GLYPHS"


def test_glyph_finder_dialog_when_opened_then_all_rows_with_char_and_codes(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    assert dialog.table.rowCount == 6, 'glyph finder dialog when opened then all rows with char and codes: expected dialog.table.rowCount == 6'
    assert dialog.table.row_texts(1) == ["eacute", "é", "U+00E9"], "glyph finder dialog when opened then all rows with char and codes: expected dialog.table.row_texts(1) == ['eacute', 'é', 'U+00E9']"
    assert dialog.table.row_texts(2) == ["eacute.ss01", "", "–"], "Unencoded glyphs show a dash"
    assert dialog.subtitle.text.startswith("Searching 6 glyphs by all."), "glyph finder dialog when opened then all rows with char and codes: expected dialog.subtitle.text.startswith('Searching 6 glyphs by all.')"
    assert dialog.status.text == "6 matches" and dialog.select_button.isEnabled(), "glyph finder dialog when opened then all rows with char and codes: expected dialog.status.text == '6 matches' and dialog.select_button.isEnabled()"


def test_glyph_finder_dialog_when_typing_then_matches_narrow_and_singular_status(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    dialog.search.setText("euro")
    assert dialog.status.text == "1 match" and dialog.table.rowCount == 1, "glyph finder dialog when typing then matches narrow and singular status: expected dialog.status.text == '1 match' and dialog.table.rowCount == 1"
    dialog.search.setText("zzz")
    assert dialog.status.text == "0 matches" and not dialog.select_button.isEnabled(), "glyph finder dialog when typing then matches narrow and singular status: unexpected result"


def test_glyph_finder_dialog_when_many_matches_then_rows_capped(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    tool.MAX_ROWS = 2
    dialog = tool.Finder(None)
    dialog.search.setText("")
    dialog.refresh()
    assert dialog.table.rowCount == 2, 'glyph finder dialog when many matches then rows capped: expected dialog.table.rowCount == 2'
    assert dialog.status.text == "6 matches (showing 2)", "glyph finder dialog when many matches then rows capped: expected dialog.status.text == '6 matches (showing 2)'"


def test_glyph_finder_dialog_when_enter_pressed_then_all_matches_selected(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    dialog.search.setText("acute")
    dialog.search.returnPressed.emit()
    assert state.selects == [(["eacute", "eacute.ss01"], PACKAGE_ID, False)], "glyph finder dialog when enter pressed then all matches selected: expected state.selects == [(['eacute', 'eacute.ss01'], PACKAGE_ID, False)]"
    assert dialog.status.text == "Selected 2 glyphs in the Font window", "glyph finder dialog when enter pressed then all matches selected: expected dialog.status.text == 'Selected 2 glyphs in the Font window'"
    assert dialog.last_result == {"selected": ["eacute", "eacute.ss01"]}, "glyph finder dialog when enter pressed then all matches selected: expected dialog.last_result == {'selected': ['eacute', 'eacute.ss01']}"


def test_glyph_finder_dialog_when_rows_picked_then_only_those_selected(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    dialog.table.selected_rows = [3, 0]
    dialog.select_button.clicked.emit()
    assert state.selects[-1][0] == ["a", "A.alt"], "Picked rows are used in table order"
    state.select_return = ["a"]
    dialog.select_matches()
    assert dialog.status.text == "Selected 1 glyph in the Font window", "glyph finder dialog when rows picked then only those selected: expected dialog.status.text == 'Selected 1 glyph in the Font window'"


def test_glyph_finder_dialog_when_row_double_clicked_then_that_glyph_selected(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    dialog.table.cellDoubleClicked.emit(1, 0)
    assert state.selects[-1][0] == ["eacute"] and dialog.status.text == "Selected eacute", "glyph finder dialog when row double clicked then that glyph selected: unexpected result"
    state.select_return = []
    dialog.select_row(0)
    assert dialog.status.text == "Glyph not found", "glyph finder dialog when row double clicked then that glyph selected: expected dialog.status.text == 'Glyph not found'"
    n = len(state.selects)
    dialog.select_row(99)
    dialog.select_row(-1)
    assert len(state.selects) == n, "Out-of-range rows select nothing"


def test_glyph_finder_dialog_when_no_font_then_open_font_message(host):
    state = state_for(host, [])
    host.package = None
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    assert dialog.subtitle.text == "Open a font first." and not dialog.select_button.isEnabled(), "glyph finder dialog when no font then open font message: unexpected result"
    assert tool.font_glyphs() == [], 'glyph finder dialog when no font then open font message: expected tool.font_glyphs() == []'


def test_glyph_finder_dialog_when_font_closed_then_select_refused(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    host.package = None
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.select_matches()
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.select_row(0)


def test_glyph_finder_close_button_when_clicked_then_closes(host):
    state = state_for(host, FIND_GLYPHS)
    tool = load(host, "Glyph Finder.py", state)
    dialog = tool.Finder(None)
    dialog.close_button.clicked.emit()
    assert dialog.closed, 'glyph finder close button when clicked then closes: expected dialog.closed'


def test_glyph_finder_main_when_run_as_script_then_window_opens(host):
    state = state_for(host, FIND_GLYPHS)
    load(host, "Glyph Finder.py", state)
    runpy.run_path(str(ROOT / "Scripts/Names/Glyph Finder.py"), run_name="__main__")
    assert "names_glyph_finder" in host.windows(), "glyph finder main when run as script then window opens: expected 'names_glyph_finder' in host.windows()"


# ---- Select by Mark --------------------------------------------------------------


def marked_font(host: Host, marks: list[tuple[str, Any]], selection: list[str] | None = None) -> NS:
    state = state_for(host, [], selection)
    host.font = NS(glyphs=[NS(name=n, mark=m) for n, m in marks])
    return state


MARKS = [("a", 1), ("b", 1), ("c", 160), ("d", 0), ("e", None), ("f", 1100)]


def test_font_marks_when_font_open_then_names_with_integer_marks(host):
    state = marked_font(host, MARKS)
    tool = load(host, "Select by Mark.py", state)
    assert tool.font_marks() == [("a", 1), ("b", 1), ("c", 160), ("d", 0), ("e", 0), ("f", 1100)], "font marks when font open then names with integer marks: unexpected result"
    host.font = None
    assert tool.font_marks() == [], "No font means no marks"


def test_font_window_selection_when_called_then_shared_helper_result(host):
    state = marked_font(host, MARKS, ["c"])
    tool = load(host, "Select by Mark.py", state)
    assert tool.font_window_selection() == ["c"], "font window selection when called then shared helper result: expected tool.font_window_selection() == ['c']"


@pytest.mark.parametrize(
    ("mark", "label"),
    [
        (0, "Unmarked"),
        (1, "Red (hue 0°)"),
        (50, "Yellow (hue 49°)"),
        (160, "Green (hue 159°)"),
        (360, "Red (hue 359°)"),
        (1100, "Grey 100"),
    ],
)
def test_mark_label_when_mark_then_hue_name_or_grey(host, mark, label):
    tool = load(host, "Select by Mark.py")
    assert tool.mark_label(mark) == label, f"mark {mark}"


def test_mark_color_when_mark_then_none_hsl_or_grey(host):
    tool = load(host, "Select by Mark.py")
    assert tool.mark_color(0) is None and tool.mark_color(-3) is None, 'mark color when mark then none hsl or grey: expected tool.mark_color(0) is None and tool.mark_color(-3) is None'
    assert tool.mark_color(10).init_args == ("hsl", 9, 200, 150), "mark color when mark then none hsl or grey: expected tool.mark_color(10).init_args == ('hsl', 9, 200, 150)"
    assert tool.mark_color(10, lightness=90).init_args == ("hsl", 9, 200, 90), "mark color when mark then none hsl or grey: expected tool.mark_color(10, lightness=90).init_args == ('hsl', 9, 200, 90)"
    assert tool.mark_color(1100).init_args == (125, 125, 125), 'mark color when mark then none hsl or grey: expected tool.mark_color(1100).init_args == (125, 125, 125)'
    assert tool.mark_color(5000).init_args == (255, 255, 255), "Grey is capped at 255"


def test_groups_when_marks_then_hue_order_with_unmarked_last(host):
    tool = load(host, "Select by Mark.py")
    assert tool.groups([("a", 5), ("b", 0), ("c", 1), ("d", 5)]) == [(1, ["c"]), (5, ["a", "d"]), (0, ["b"])], "groups when marks then hue order with unmarked last: unexpected result"


def test_swatch_when_unmarked_or_marked_then_icon_made_and_painter_ended(host):
    tool = load(host, "Select by Mark.py")
    ended: list[bool] = []

    class Painter:
        Antialiasing = 1

        def __init__(self, target: Any) -> None:
            self.calls: list[str] = []

        def __getattr__(self, name: str) -> Any:
            return lambda *a: self.calls.append(name) if name != "end" else ended.append(True)

    tool.QtGui.QPainter = Painter
    tool.swatch(0)
    tool.swatch(7, size=24)
    assert ended == [True, True], "The painter is released for both swatches"


def test_select_by_mark_dialog_when_opened_then_group_rows_and_status(host):
    state = marked_font(host, MARKS + [(f"x{i}", 1) for i in range(5)])
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    assert dialog.table.rowCount == 4, 'select by mark dialog when opened then group rows and status: expected dialog.table.rowCount == 4'
    first = dialog.table.row_texts(0)
    assert first[:2] == ["Red (hue 0°)", "7"] and first[2] == "a b x0 x1 x2 x3 …", "Long lists end with an ellipsis"
    assert dialog.table.row_texts(3)[0] == "Unmarked", "select by mark dialog when opened then group rows and status: expected dialog.table.row_texts(3)[0] == 'Unmarked'"
    assert dialog.subtitle.text.startswith("9 of 11 glyphs carry a mark."), "select by mark dialog when opened then group rows and status: expected dialog.subtitle.text.startswith('9 of 11 glyphs carry a mark.')"
    assert dialog.status.text == "4 mark values" and dialog.select_button.isEnabled(), "select by mark dialog when opened then group rows and status: unexpected result"


def test_select_by_mark_dialog_when_rows_picked_then_their_glyphs_selected(host):
    state = marked_font(host, MARKS)
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    dialog.table.selected_rows = [0, 1]
    dialog.select_button.clicked.emit()
    assert state.selects == [(["a", "b", "c"], PACKAGE_ID, False)], "select by mark dialog when rows picked then their glyphs selected: expected state.selects == [(['a', 'b', 'c'], PACKAGE_ID, False)]"
    assert dialog.last_result == {"marks": [1, 160], "names": ["a", "b", "c"], "selected": 3}, "select by mark dialog when rows picked then their glyphs selected: unexpected result"
    assert dialog.status.text == "Selected 3 glyphs", "select by mark dialog when rows picked then their glyphs selected: expected dialog.status.text == 'Selected 3 glyphs'"


def test_select_by_mark_dialog_when_add_checked_then_selection_extended(host):
    state = marked_font(host, MARKS)
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    dialog.add.setChecked(True)
    dialog.table.cellDoubleClicked.emit(1, 0)
    assert state.selects == [(["c"], PACKAGE_ID, True)], "Double-click selects one mark group, adding"
    assert dialog.status.text == "Selected 1 glyph", "select by mark dialog when add checked then selection extended: expected dialog.status.text == 'Selected 1 glyph'"


def test_select_by_mark_dialog_when_nothing_picked_then_hint_and_no_selection(host):
    state = marked_font(host, MARKS)
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    dialog.select_button.clicked.emit()
    assert dialog.status.text == "Pick at least one row first." and state.selects == [], "select by mark dialog when nothing picked then hint and no selection: unexpected result"
    dialog.select_rows([99])
    assert state.selects == [], "A row beyond the groups selects nothing"


def test_select_by_mark_dialog_when_reload_then_new_marks_listed(host):
    state = marked_font(host, MARKS)
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    host.font = NS(glyphs=[NS(name="z", mark=300)])
    dialog.reload_button.clicked.emit()
    assert [g[0] for g in dialog.groups] == [300] and dialog.status.text == "1 mark value", "select by mark dialog when reload then new marks listed: unexpected result"


def test_select_by_mark_dialog_when_no_font_then_open_font_message(host):
    state = marked_font(host, [])
    host.package = None
    host.font = None
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    assert dialog.subtitle.text == "Open a font first." and not dialog.select_button.isEnabled(), "select by mark dialog when no font then open font message: unexpected result"
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.select_rows([0])


def test_select_by_mark_close_button_when_clicked_then_closes(host):
    state = marked_font(host, MARKS)
    tool = load(host, "Select by Mark.py", state)
    dialog = tool.SelectByMark(None)
    dialog.close_button.clicked.emit()
    assert dialog.closed, 'select by mark close button when clicked then closes: expected dialog.closed'


def test_select_by_mark_main_when_run_as_script_then_window_opens(host):
    state = marked_font(host, MARKS)
    load(host, "Select by Mark.py", state)
    runpy.run_path(str(ROOT / "Scripts/Names/Select by Mark.py"), run_name="__main__")
    assert "names_select_by_mark" in host.windows(), "select by mark main when run as script then window opens: expected 'names_select_by_mark' in host.windows()"


# ---- Character Set Compare -------------------------------------------------------


def charset_font(host: Host, glyphs: list[tuple[str, list[int]]]) -> NS:
    state = state_for(host, [])
    host.font = NS(glyphs=[NS(name=n, unicodes=c) for n, c in glyphs])
    return state


CHARSET = [("a", [97]), ("b", [98]), ("c", [99, 0x1D41A]), ("space", [32]), ("z", [122])]


def test_text_chars_when_text_then_distinct_nonspace_sorted_by_code(host):
    tool = load(host, "Character Set Compare.py")
    assert tool.text_chars("ba b\n\ta") == ["a", "b"], "text chars when text then distinct nonspace sorted by code: expected tool.text_chars('ba b\\n\\ta') == ['a', 'b']"
    assert tool.text_chars("") == [], "text chars when text then distinct nonspace sorted by code: expected tool.text_chars('') == []"


def test_compare_when_text_and_font_then_missing_and_extra(host):
    tool = load(host, "Character Set Compare.py")
    missing, extra = tool.compare("abx", {"a": "a", "b": "b", "z": "z", " ": "space"})
    assert missing == ["x"] and extra == ["z"], "Whitespace glyphs are never 'extra'"


def test_describe_when_char_then_code_point_and_title_case_name(host):
    tool = load(host, "Character Set Compare.py")
    assert tool.describe("a") == "a   U+0061   Latin Small Letter A", "describe when char then code point and title case name: expected tool.describe('a') == 'a   U+0061   Latin Small Letter A'"
    assert tool.describe("").endswith("U+E000   "), "Unnamed characters get an empty name"


def test_font_chars_when_font_then_first_glyph_per_character_and_none_without_font(host):
    state = charset_font(host, CHARSET + [("a.alt", [97])])
    tool = load(host, "Character Set Compare.py", state)
    chars = tool.font_chars()
    assert chars["a"] == "a" and chars["\U0001d41a"] == "c" and len(chars) == 6, "font chars when font then first glyph per character and none without font: expected chars['a'] == 'a' and chars['𝐚'] == 'c' and (len(chars) == 6)"
    host.font = None
    assert tool.font_chars() == {}, 'font chars when font then first glyph per character and none without font: expected tool.font_chars() == {}'


def test_charset_dialog_when_text_pasted_then_missing_extra_and_coverage(host):
    state = charset_font(host, CHARSET)
    tool = load(host, "Character Set Compare.py", state)
    dialog = tool.CharsetCompare(None)
    assert dialog.status.text == "Coverage 0/0" and not dialog.copy_button.isEnabled(), "charset dialog when text pasted then missing extra and coverage: unexpected result"
    dialog.text.setPlainText("abxy")
    assert dialog.missing == ["x", "y"], "charset dialog when text pasted then missing extra and coverage: expected dialog.missing == ['x', 'y']"
    assert dialog.missing_list.entries[0] == "x   U+0078   Latin Small Letter X", "charset dialog when text pasted then missing extra and coverage: expected dialog.missing_list.entries[0] == 'x   U+0078   Latin Small Letter X'"
    assert dialog.extra_list.entries[0].endswith("· c"), "Extra rows name the glyph"
    assert dialog.missing_label.text == "Missing from the font (2)", "charset dialog when text pasted then missing extra and coverage: expected dialog.missing_label.text == 'Missing from the font (2)'"
    assert dialog.extra_label.text == "In the font, not in the text (3)", "charset dialog when text pasted then missing extra and coverage: expected dialog.extra_label.text == 'In the font, not in the text (3)'"
    assert dialog.status.text == "Coverage 2/4 · 50%", "charset dialog when text pasted then missing extra and coverage: expected dialog.status.text == 'Coverage 2/4 · 50%'"
    assert dialog.subtitle.text == "The font encodes 6 characters; the text uses 4.", "charset dialog when text pasted then missing extra and coverage: unexpected result"
    assert dialog.copy_button.isEnabled() and dialog.select_button.isEnabled(), 'charset dialog when text pasted then missing extra and coverage: expected dialog.copy_button.isEnabled() and dialog.select_button.isEnabled()'


def test_charset_dialog_when_copy_clicked_then_missing_characters_on_clipboard(host):
    state = charset_font(host, CHARSET)
    tool = load(host, "Character Set Compare.py", state)
    copied = clipboard(tool)
    dialog = tool.CharsetCompare(None)
    dialog.text.setPlainText("abxy")
    dialog.copy_button.clicked.emit()
    assert copied == ["xy"] and dialog.status.text == "Copied 2 characters", "charset dialog when copy clicked then missing characters on clipboard: expected copied == ['xy'] and dialog.status.text == 'Copied 2 characters'"


def test_charset_dialog_when_select_extra_then_their_glyph_names_selected(host):
    state = charset_font(host, CHARSET)
    tool = load(host, "Character Set Compare.py", state)
    dialog = tool.CharsetCompare(None)
    dialog.text.setPlainText("ab")
    dialog.select_button.clicked.emit()
    assert state.selects == [(["c", "z", "c"], PACKAGE_ID, False)], "charset dialog when select extra then their glyph names selected: expected state.selects == [(['c', 'z', 'c'], PACKAGE_ID, False)]"
    assert dialog.last_result == {"selected": ["c", "z", "c"]}, "charset dialog when select extra then their glyph names selected: expected dialog.last_result == {'selected': ['c', 'z', 'c']}"
    assert dialog.status.text == "Selected 3 extra glyphs in the Font window", "charset dialog when select extra then their glyph names selected: expected dialog.status.text == 'Selected 3 extra glyphs in the Font window'"
    state.select_return = ["z"]
    dialog.select_extra()
    assert dialog.status.text == "Selected 1 extra glyph in the Font window", "charset dialog when select extra then their glyph names selected: expected dialog.status.text == 'Selected 1 extra glyph in the Font window'"


def test_charset_dialog_when_preset_chosen_then_text_filled_and_index_zero_ignored(host):
    state = charset_font(host, CHARSET)
    tool = load(host, "Character Set Compare.py", state)
    dialog = tool.CharsetCompare(None)
    assert dialog.preset.items[0] == "Paste your own text…", "charset dialog when preset chosen then text filled and index zero ignored: expected dialog.preset.items[0] == 'Paste your own text…'"
    dialog.preset.setCurrentIndex(3)
    assert "Ł" in dialog.text.toPlainText(), "The Polish preset is typed into the text box"
    before = dialog.text.toPlainText()
    dialog.use_preset(0)
    dialog.use_preset(99)
    assert dialog.text.toPlainText() == before, "Index 0 and unknown indexes leave the text alone"


def test_charset_dialog_when_text_only_whitespace_then_select_extra_disabled(host):
    state = charset_font(host, CHARSET)
    tool = load(host, "Character Set Compare.py", state)
    dialog = tool.CharsetCompare(None)
    dialog.text.setPlainText("   ")
    assert not dialog.select_button.isEnabled(), "No text means no 'extra' selection"


def test_charset_dialog_when_no_font_then_open_font_message(host):
    state = charset_font(host, [])
    host.package = None
    host.font = None
    tool = load(host, "Character Set Compare.py", state)
    dialog = tool.CharsetCompare(None)
    assert dialog.subtitle.text == "Open a font with encoded glyphs first.", "charset dialog when no font then open font message: expected dialog.subtitle.text == 'Open a font with encoded glyphs first.'"
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.copy_missing()
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.select_extra()


def test_charset_close_button_when_clicked_then_closes(host):
    state = charset_font(host, CHARSET)
    tool = load(host, "Character Set Compare.py", state)
    dialog = tool.CharsetCompare(None)
    dialog.close_button.clicked.emit()
    assert dialog.closed, 'charset close button when clicked then closes: expected dialog.closed'


def test_charset_main_when_run_as_script_then_window_opens(host):
    state = charset_font(host, CHARSET)
    load(host, "Character Set Compare.py", state)
    runpy.run_path(str(ROOT / "Scripts/Names/Character Set Compare.py"), run_name="__main__")
    assert "names_charset_compare" in host.windows(), "charset main when run as script then window opens: expected 'names_charset_compare' in host.windows()"


# ---- Character Info --------------------------------------------------------------


def glyph_package(host: Host, glyph: Any, layer: Any = "default") -> NS:
    """A package whose findName knows one glyph; wires FontLab's workspace double."""
    if layer == "default":
        layer = NS(shapes=[], advanceWidth=500)
    glyph_obj = NS(fgGlyph=NS(unicodes=glyph[1]), findLayer=lambda master: layer) if glyph else None
    package = NS(
        id=PACKAGE_ID,
        isNull=False,
        master="Regular",
        descender_value=-200,
        ascender_value=800,
        findName=lambda name: glyph_obj if glyph and name == glyph[0] else None,
    )
    host.package = package
    host.native.flWorkspace = NS(instance=lambda: NS(currentPackage=host.package))
    return package


def info_state(host: Host, glyph: Any, selection: list[str], layer: Any = "default") -> NS:
    glyph_package(host, glyph, layer)
    return NS(glyphs=[], selection=selection, selects=[], select_return=None, copied=[])


@pytest.mark.parametrize(
    ("code", "expect"),
    [
        (0x61, {"Code point": "U+0061", "Case pair": "A U+0041", "UTF-8": "61", "UTF-16": "0061", "Escape": "\\u0061"}),
        (0xE9, {"Decomposition": "0065 0301", "Category": "Ll · Letter, lowercase", "UTF-8": "C3 A9"}),
        (0x1D41A, {"UTF-16": "D835 DC1A", "Escape": "\\U0001d41a", "Case pair": "–"}),
        (0xE000, {"Unicode name": "(no name)", "Category": "Co · Private use"}),
        (0x41, {"Case pair": "a U+0061"}),
        (0x31, {"Case pair": "–", "Decomposition": "–", "Category": "Nd · Number, decimal"}),
    ],
)
def test_describe_when_code_point_then_expected_fields(host, code, expect):
    tool = load(host, "Character Info.py")
    result = tool.describe(code)
    for key, value in expect.items():
        assert result[key] == value, f"U+{code:04X} {key}"


def test_character_info_dialog_when_glyph_selected_then_fields_and_status_filled(host):
    state = info_state(host, ("e", [0xE9, 0x65]), ["e", "x"])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    assert dialog.fields["Glyph"].text == "e" and dialog.fields["Code point"].text == "U+00E9", "character info dialog when glyph selected then fields and status filled: unexpected result"
    assert dialog.fields["Decomposition"].text == "0065 0301", "character info dialog when glyph selected then fields and status filled: expected dialog.fields['Decomposition'].text == '0065 0301'"
    assert dialog.others.text == "Also encoded: U+0065", "character info dialog when glyph selected then fields and status filled: expected dialog.others.text == 'Also encoded: U+0065'"
    assert dialog.subtitle.text == "Follows the Font window selection · master Regular", "character info dialog when glyph selected then fields and status filled: unexpected result"
    assert dialog.status.text == "e · 2 code points" and dialog.copy_button.isEnabled(), "character info dialog when glyph selected then fields and status filled: unexpected result"
    assert dialog.specimen.char == "é" and dialog.specimen.advance == 500, "character info dialog when glyph selected then fields and status filled: expected dialog.specimen.char == 'é' and dialog.specimen.advance == 500"
    assert dialog.specimen.frame == (-200, 800), 'character info dialog when glyph selected then fields and status filled: expected dialog.specimen.frame == (-200, 800)'
    dialog.timer.setInterval.assert_called_once_with(500)
    dialog.timer.start.assert_called_once_with()


def test_character_info_dialog_when_timer_ticks_then_follows_selection_change(host):
    state = info_state(host, ("e", [0xE9]), [])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    assert dialog.subtitle.text == "Select a glyph in the Font window.", "character info dialog when timer ticks then follows selection change: expected dialog.subtitle.text == 'Select a glyph in the Font window.'"
    assert not dialog.copy_button.isEnabled() and dialog.specimen.char == "", "character info dialog when timer ticks then follows selection change: expected not dialog.copy_button.isEnabled() and dialog.specimen.char == ''"
    state.selection = ["e"]
    dialog.timer.timeout.emit()
    assert dialog.shown_name == "e" and dialog.status.text == "e · 1 code point", "character info dialog when timer ticks then follows selection change: expected dialog.shown_name == 'e' and dialog.status.text == 'e · 1 code point'"


def test_character_info_dialog_when_glyph_unencoded_then_placeholder_and_copy_disabled(host):
    state = info_state(host, ("g.alt", []), ["g.alt"])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    assert dialog.fields["Code point"].text == "– (unencoded)" and dialog.fields["UTF-8"].text == "–", "character info dialog when glyph unencoded then placeholder and copy disabled: unexpected result"
    assert dialog.others.text == "" and not dialog.copy_button.isEnabled(), "character info dialog when glyph unencoded then placeholder and copy disabled: expected dialog.others.text == '' and (not dialog.copy_button.isEnabled())"
    assert dialog.status.text == "g.alt · 0 code points", "character info dialog when glyph unencoded then placeholder and copy disabled: expected dialog.status.text == 'g.alt · 0 code points'"


def test_character_info_dialog_when_layer_missing_then_no_outline_and_zero_advance(host):
    state = info_state(host, ("a", [97]), ["a"], layer=None)
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    assert dialog.specimen.path is None and dialog.specimen.advance == 0, 'character info dialog when layer missing then no outline and zero advance: expected dialog.specimen.path is None and dialog.specimen.advance == 0'
    assert dialog.specimen.char == "a", "character info dialog when layer missing then no outline and zero advance: expected dialog.specimen.char == 'a'"


def test_character_info_dialog_when_no_font_then_open_font_message(host):
    state = info_state(host, None, [])
    host.package = None
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    assert dialog.subtitle.text == "Open a font and select a glyph in the Font window.", "character info dialog when no font then open font message: unexpected result"
    assert tool.current_package() is None and tool.focused_name() is None, 'character info dialog when no font then open font message: expected tool.current_package() is None and tool.focused_name() is None'


def test_character_info_current_package_when_null_package_then_none(host):
    state = info_state(host, None, [])
    host.package.isNull = True
    tool = load(host, "Character Info.py", state)
    assert tool.current_package() is None, "A null native package is treated as no font"


def test_character_info_refresh_when_name_given_then_that_glyph_shown(host):
    state = info_state(host, ("a", [97]), ["zzz"])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    assert dialog.subtitle.text == "Select a glyph in the Font window.", "Unknown selected glyph"
    dialog.refresh("a")
    assert dialog.shown_name == "a" and dialog.fields["Glyph"].text == "a", "character info refresh when name given then that glyph shown: expected dialog.shown_name == 'a' and dialog.fields['Glyph'].text == 'a'"


def test_character_info_copy_when_encoded_then_character_on_clipboard(host):
    state = info_state(host, ("a", [97]), ["a"])
    tool = load(host, "Character Info.py", state)
    copied = clipboard(tool)
    dialog = tool.CharacterInfo(None)
    dialog.copy_button.clicked.emit()
    assert copied == ["a"] and dialog.status.text == "Copied a", "character info copy when encoded then character on clipboard: expected copied == ['a'] and dialog.status.text == 'Copied a'"


def test_character_info_copy_when_unencoded_then_nothing_copied(host):
    state = info_state(host, ("g", []), ["g"])
    tool = load(host, "Character Info.py", state)
    copied = clipboard(tool)
    dialog = tool.CharacterInfo(None)
    dialog.copy()
    assert copied == [], 'character info copy when unencoded then nothing copied: expected copied == []'


def test_character_info_copy_when_font_closed_then_refused(host):
    state = info_state(host, ("a", [97]), ["a"])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    host.package = None
    with pytest.raises(ValueError, match="Results are stale"):
        dialog.copy()


def test_layer_path_when_parts_empty_or_missing_then_only_real_parts_added(host):
    tool = load(host, "Character Info.py")
    added: list[Any] = []

    class Path:
        def setFillRule(self, rule: Any) -> None:
            pass

        def addPath(self, part: Any) -> None:
            added.append(part)

    tool.QtGui.QPainterPath = Path
    real, empty = NS(isEmpty=lambda: False), NS(isEmpty=lambda: True)
    mapped = NS(map=lambda part: ("mapped", part))
    tool.layer_path(NS(shapes=[NS(closedPath=real, openedPath=empty, transform=mapped), NS(closedPath=None, openedPath=real, transform=mapped)]))
    assert added == [("mapped", real), ("mapped", real)], "layer path when parts empty or missing then only real parts added: expected added == [('mapped', real), ('mapped', real)]"


class Brush:
    """QPainter double recording its operations by name."""

    Antialiasing = 1

    def __init__(self, *_: Any) -> None:
        self.calls: list[tuple[str, tuple]] = []
        self.ended = False

    def font(self) -> Any:
        return NS()

    def end(self) -> None:
        self.ended = True

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a: self.calls.append((name, a))

    def names(self) -> list[str]:
        return [c[0] for c in self.calls]


def specimen_for(host: Host, tool: Any) -> Any:
    specimen = tool.Specimen()
    specimen.width, specimen.height = 400, 200
    return specimen


def test_specimen_when_set_content_then_state_replaced_and_repainted(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    path = NS(boundingRect=lambda: NS(left=lambda: 0, right=lambda: 400, top=lambda: -50, bottom=lambda: 700))
    specimen.set_content(path, 420.0, "é", (-250, 750))
    assert (specimen.path, specimen.advance, specimen.char, specimen.frame) == (path, 420.0, "é", (-250, 750)), 'specimen when set content then state replaced and repainted: unexpected result'
    assert specimen.update.called, 'specimen when set content then state replaced and repainted: expected specimen.update.called'


def test_specimen_draw_when_outline_and_char_then_proofs_on_both_sides(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    path = NS(boundingRect=lambda: NS(left=lambda: -20, right=lambda: 450, top=lambda: -50, bottom=lambda: 900))
    specimen.set_content(path, 420.0, "é", (-250, 750))
    painter = Brush()
    specimen.draw(painter)
    names = painter.names()
    assert names.count("drawRoundedRect") == 2 and "fillPath" in names and "drawLine" in names, "specimen draw when outline and char then proofs on both sides: unexpected result"
    assert names.count("drawText") == 3, "Two captions plus the system-font character"
    assert painter.calls[names.index("translate")][1][0] > 0, "The outline is centred horizontally"


def test_specimen_draw_when_empty_then_only_frames_and_captions(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    painter = Brush()
    specimen.draw(painter)
    assert painter.names().count("drawText") == 2 and "fillPath" not in painter.names(), "specimen draw when empty then only frames and captions: unexpected result"


def test_specimen_paint_event_when_ok_then_error_cleared_and_painter_ended(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    instances: list[Brush] = []
    tool.QtGui.QPainter = lambda target: instances.append(Brush()) or instances[-1]
    tool.QtGui.QPainter.Antialiasing = 1
    specimen.paint_error = "old"
    specimen.paintEvent(None)
    assert specimen.paint_error == "" and instances[0].ended, "specimen paint event when ok then error cleared and painter ended: expected specimen.paint_error == '' and instances[0].ended"


def test_specimen_paint_event_when_draw_fails_then_hook_receives_error(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    instances: list[Brush] = []
    tool.QtGui.QPainter = lambda target: instances.append(Brush()) or instances[-1]
    specimen.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("bad paint"))
    seen: list[str] = []
    specimen.on_error = seen.append
    specimen.paintEvent(None)
    assert seen == ["RuntimeError('bad paint')"] and instances[0].ended, 'specimen paint event when draw fails then hook receives error: expected seen == ["RuntimeError(\'bad paint\')"] and instances[0].ended'


def test_specimen_paint_event_when_hook_also_fails_then_both_errors_kept(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    tool.QtGui.QPainter = lambda target: Brush()
    specimen.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("bad paint"))
    specimen.on_error = lambda text: (_ for _ in ()).throw(ValueError("hook broke"))
    specimen.paintEvent(None)
    assert specimen.paint_error.startswith("RuntimeError('bad paint'); error hook: ValueError("), 'specimen paint event when hook also fails then both errors kept: unexpected result'


def test_specimen_paint_event_when_no_hook_then_error_recorded(host):
    tool = load(host, "Character Info.py")
    specimen = specimen_for(host, tool)
    tool.QtGui.QPainter = lambda target: Brush()
    specimen.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("x"))
    specimen.paintEvent(None)
    assert specimen.paint_error == "RuntimeError('x')", 'specimen paint event when no hook then error recorded: expected specimen.paint_error == "RuntimeError(\'x\')"'


def test_character_info_dialog_when_drawing_fails_then_status_reports(host):
    state = info_state(host, ("a", [97]), ["a"])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    tool.QtGui.QPainter = lambda target: Brush()
    dialog.specimen.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("nope"))
    dialog.specimen.paintEvent(None)
    assert dialog.status.text == "Drawing failed: RuntimeError('nope')", 'character info dialog when drawing fails then status reports: expected dialog.status.text == "Drawing failed: RuntimeError(\'nope\')"'


def test_character_info_close_button_when_clicked_then_closes(host):
    state = info_state(host, ("a", [97]), ["a"])
    tool = load(host, "Character Info.py", state)
    dialog = tool.CharacterInfo(None)
    dialog.close_button.clicked.emit()
    assert dialog.closed, 'character info close button when clicked then closes: expected dialog.closed'


def test_character_info_main_when_run_as_script_then_window_opens(host):
    state = info_state(host, ("a", [97]), ["a"])
    load(host, "Character Info.py", state)
    runpy.run_path(str(ROOT / "Scripts/Names/Character Info.py"), run_name="__main__")
    assert "names_character_info" in host.windows(), "character info main when run as script then window opens: expected 'names_character_info' in host.windows()"
