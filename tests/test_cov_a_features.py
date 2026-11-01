# this_file: tests/test_cov_a_features.py
# SPDX-License-Identifier: Apache-2.0
"""Coverage round A: drive the six Features dialogs through the real App panel."""

from __future__ import annotations

import runpy
from types import SimpleNamespace as NS
from typing import Any

import pytest
from _cov_a_support import ROOT, Host, host  # noqa: F401

FEATURE_MODULES = ("feature_code",)
PACKAGE = NS(id=11, fgId=101, master="Regular", masters=["Regular", "Bold"])


def open_font(host: Host, names: list[str], **extra: Any) -> None:
    """Make an owned font with ``names`` current."""
    host.package = NS(**vars(PACKAGE))
    host.font = NS(glyphs=[NS(name=n) for n in names], **extra)


def make_blocks(state: NS) -> NS:
    """Return a ``fly.fp.feature_blocks`` double over ``state.blocks``."""

    def read(package: Any) -> dict:
        return {"prefix": state.blocks["prefix"], "features": list(state.blocks["features"])}

    def write(package: Any, expected: dict, new: dict, *, references: list, undo_name: str) -> dict:
        state.writes.append((new, references, undo_name))
        state.blocks = new
        return {"changed": 1}

    return NS(read_feature_blocks=read, write_feature_blocks=write)


@pytest.fixture
def blocks() -> NS:
    state = NS(blocks={"prefix": "languagesystem DFLT dflt;\n", "features": []}, writes=[])
    state.module = make_blocks(state)
    return state


def clipboard(tool: Any) -> list[str]:
    """Replace the double's QApplication with a recording clipboard."""
    copied: list[str] = []
    tool.QtGui.QApplication = NS(clipboard=lambda: NS(setText=copied.append))
    return copied


# ---- Suffix Report -------------------------------------------------------------


def test_suffix_report_when_font_has_suffixes_then_rows_and_first_preview_shown(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc", "b", "b.sc", "c.alt", "x.orphan"])
    dialog = tool.Dialog(None)
    assert dialog.rows == [
        ("alt", 1, 0, "salt"),
        ("orphan", 1, 0, "salt"),
        ("sc", 2, 2, "smcp"),
    ], "Rows must be sorted by suffix with orphan names counted but not paired"
    assert dialog.table.current == 0, "The first row is selected after a refresh"
    assert dialog.code.toPlainText() == "No matching base glyphs. Select a suffix with usable pairs.", "suffix report when font has suffixes then rows and first preview shown: unexpected result"
    assert not dialog.apply_button.isEnabled(), "No pairs means Copy stays disabled"
    assert dialog.status.text == "3 suffixes · 0 safe substitution pairs selected", "suffix report when font has suffixes then rows and first preview shown: unexpected result"


def test_suffix_report_when_pair_row_selected_then_snippet_copied(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc", "b", "b.sc"])
    copied = clipboard(tool)
    dialog = tool.Dialog(None)
    assert dialog.snippet.startswith("feature smcp {"), "Selected sc row builds smcp code"
    assert "sub a by a.sc;" in dialog.snippet and "sub b by b.sc;" in dialog.snippet, "suffix report when pair row selected then snippet copied: unexpected result"
    assert dialog.apply_button.isEnabled(), "Usable pairs enable the copy action"
    dialog.apply()
    assert copied == [dialog.snippet], "Apply copies exactly the previewed snippet"
    assert dialog.last_result == {"copied": dialog.snippet}, "suffix report when pair row selected then snippet copied: expected dialog.last_result == {'copied': dialog.snippet}"
    assert dialog.status.text == "Copied feature code to the clipboard.", "suffix report when pair row selected then snippet copied: expected dialog.status.text == 'Copied feature code to the clipboard.'"


def test_suffix_report_when_selection_changes_then_preview_follows_row(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc", "a.ss01", "a.zzz", "q.zzz"])
    dialog = tool.Dialog(None)
    names = [row[0] for row in dialog.rows]
    assert names == ["sc", "ss01", "zzz"], "Suffix order drives the table"
    dialog.table.selectRow(names.index("ss01"))
    assert dialog.snippet.startswith("feature ss01 {"), "ss01 keeps its own tag"
    dialog.table.clearSelection()
    assert dialog.snippet == "", "No current row means no snippet"
    assert dialog.code.toPlainText().startswith("No matching base glyphs"), "suffix report when selection changes then preview follows row: expected dialog.code.toPlainText().startswith('No matching base glyphs')"


def test_suffix_report_when_apply_has_no_snippet_then_nothing_copied(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "x.orphan"])
    copied = clipboard(tool)
    dialog = tool.Dialog(None)
    dialog.apply()
    assert copied == [] and dialog.last_result is None, "An empty preview must not copy"


def test_suffix_report_when_no_font_then_empty_report_and_disabled_copy(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    dialog = tool.Dialog(None)
    assert dialog.rows == [] and not dialog.apply_button.isEnabled(), 'suffix report when no font then empty report and disabled copy: expected dialog.rows == [] and (not dialog.apply_button.isEnabled())'
    assert dialog.status.text == "0 suffixes · 0 safe substitution pairs selected", "suffix report when no font then empty report and disabled copy: unexpected result"
    assert dialog.subtitle.text == "Open a font, then reopen this tool.", "suffix report when no font then empty report and disabled copy: expected dialog.subtitle.text == 'Open a font, then reopen this tool.'"


def test_suffix_report_when_font_switched_then_apply_refused(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc"])
    dialog = tool.Dialog(None)
    host.package = NS(**{**vars(PACKAGE), "id": 99})
    with pytest.raises(ValueError, match="Activate the original font"):
        dialog.apply()
    dialog.safe(dialog.refresh)
    assert not dialog.apply_button.isEnabled(), "A failed refresh disables copy"
    assert "Activate the original font" in dialog.status.text, "suffix report when font switched then apply refused: expected 'Activate the original font' in dialog.status.text"


def test_suffix_report_when_main_runs_then_window_registered_and_replaced(host):
    tool = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc"])
    first = tool.main()
    assert host.windows()[tool.KEY] is first and first.shown, 'suffix report when main runs then window registered and replaced: expected host.windows()[tool.KEY] is first and first.shown'
    second = tool.main()
    assert second is not first and host.windows()[tool.KEY] is second, (
        "A closed window is replaced, not duplicated"
    )


def test_suffix_report_when_run_as_script_then_window_opens(host):
    host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc"])
    runpy.run_path(str(ROOT / "Scripts/Features/Suffix Report.py"), run_name="__main__")
    assert "features_suffix_report" in host.windows(), "The main guard opens the tool"


# ---- Ligature Finder -----------------------------------------------------------


def test_ligature_finder_when_font_has_recipes_then_rows_status_and_snippet(host):
    tool = host.load("Features/Ligature Finder.py", modules=FEATURE_MODULES)
    open_font(host, ["f", "i", "f_i", "x_y", "f_i.sc", "f.sc", "i.sc"])
    dialog = tool.Dialog(None)
    assert [r[0] for r in dialog.rows] == ["f_i", "f_i.sc", "x_y"], "ligature finder when font has recipes then rows status and snippet: expected [r[0] for r in dialog.rows] == ['f_i', 'f_i.sc', 'x_y']"
    assert dialog.snippet.startswith("feature liga {") and "sub f i by f_i;" in dialog.snippet, "ligature finder when font has recipes then rows status and snippet: unexpected result"
    assert dialog.status.text == "3 candidates · 2 usable recipes", "ligature finder when font has recipes then rows status and snippet: expected dialog.status.text == '3 candidates · 2 usable recipes'"
    assert dialog.apply_button.isEnabled(), 'ligature finder when font has recipes then rows status and snippet: expected dialog.apply_button.isEnabled()'
    assert dialog.table.row_texts(2) == ["x_y", "x y", "Missing / invalid input: x, y"], "ligature finder when font has recipes then rows status and snippet: unexpected result"


def test_ligature_finder_when_filter_typed_then_rows_narrow_and_empty_shows_hint(host):
    tool = host.load("Features/Ligature Finder.py", modules=FEATURE_MODULES)
    open_font(host, ["f", "i", "f_i", "x_y"])
    dialog = tool.Dialog(None)
    dialog.search.setText("X Y")
    assert [r[0] for r in dialog.rows] == ["x_y"], "Filtering is case-insensitive over the row"
    assert dialog.snippet == "" and not dialog.apply_button.isEnabled(), "ligature finder when filter typed then rows narrow and empty shows hint: expected dialog.snippet == '' and (not dialog.apply_button.isEnabled())"
    assert dialog.code.toPlainText() == "No usable underscore recipes in this view.", "ligature finder when filter typed then rows narrow and empty shows hint: unexpected result"
    assert dialog.status.text == "1 candidates · 0 usable recipes", "ligature finder when filter typed then rows narrow and empty shows hint: expected dialog.status.text == '1 candidates · 0 usable recipes'"


def test_ligature_finder_when_apply_then_copies_snippet(host):
    tool = host.load("Features/Ligature Finder.py", modules=FEATURE_MODULES)
    open_font(host, ["f", "i", "f_i"])
    copied = clipboard(tool)
    dialog = tool.Dialog(None)
    dialog.apply()
    assert copied == ["feature liga {\n    sub f i by f_i;\n} liga;"], "ligature finder when apply then copies snippet: expected copied == ['feature liga {\\n    sub f i by f_i;\\n} liga;']"


def test_ligature_finder_when_apply_without_snippet_then_no_copy(host):
    tool = host.load("Features/Ligature Finder.py", modules=FEATURE_MODULES)
    open_font(host, ["x_y"])
    copied = clipboard(tool)
    dialog = tool.Dialog(None)
    dialog.apply()
    assert copied == [], "A recipe with missing inputs yields no liga code to copy"


def test_ligature_finder_when_main_runs_as_script_then_window_opens(host):
    host.load("Features/Ligature Finder.py", modules=FEATURE_MODULES)
    open_font(host, ["f", "i", "f_i"])
    runpy.run_path(str(ROOT / "Scripts/Features/Ligature Finder.py"), run_name="__main__")
    assert "features_ligature_finder" in host.windows(), "ligature finder when main runs as script then window opens: expected 'features_ligature_finder' in host.windows()"


def test_ligature_finder_when_main_called_then_dialog_returned(host):
    tool = host.load("Features/Ligature Finder.py", modules=FEATURE_MODULES)
    open_font(host, ["f", "i", "f_i"])
    assert tool.main() is host.windows()[tool.KEY], 'ligature finder when main called then dialog returned: expected tool.main() is host.windows()[tool.KEY]'


# ---- Classes Browser -----------------------------------------------------------


class Groups(dict):
    """fontgate group collection double."""

    def __init__(self, records: list[str], flags: dict[str, bool]) -> None:
        super().__init__({k: NS(isFeaGroup=lambda v=v: v) for k, v in flags.items()})
        self.records = records

    def getAsClassRecords(self) -> list[str]:
        return self.records


def class_font(host: Host) -> Groups:
    groups = Groups(
        ["Upper:A' B C", "Lower:a b", "kernLeft:A B", "Empty:"],
        {"Upper": True, "Lower": True, "kernLeft": False, "Empty": True},
    )
    open_font(host, ["A", "B", "C", "a", "b"], groups=groups)
    return groups



def test_classes_browser_when_font_has_classes_then_sorted_rows_and_class_snippet(host):
    tool = host.load("Features/Classes Browser.py", modules=FEATURE_MODULES)
    class_font(host)
    dialog = tool.Dialog(None)
    assert dialog.rows == [
        ("Empty", 0, ""),
        ("Lower", 2, "a b"),
        ("Upper", 3, "A B C"),
    ], "Kerning-only groups are excluded, rows sorted"
    assert dialog.table.current == 0, 'classes browser when font has classes then sorted rows and class snippet: expected dialog.table.current == 0'
    assert dialog.status.text == "3 of 3 feature classes", "classes browser when font has classes then sorted rows and class snippet: expected dialog.status.text == '3 of 3 feature classes'"
    assert dialog.snippet == "@Empty = [];", "classes browser when font has classes then sorted rows and class snippet: expected dialog.snippet == '@Empty = [];'"


def test_classes_browser_when_row_selected_then_snippet_is_class_definition(host):
    tool = host.load("Features/Classes Browser.py", modules=FEATURE_MODULES)
    class_font(host)
    dialog = tool.Dialog(None)
    dialog.table.selectRow(2)
    assert dialog.snippet == "@Upper = [A B C];", "Key-member apostrophe is stripped"
    assert dialog.members.toPlainText() == dialog.snippet, 'classes browser when row selected then snippet is class definition: expected dialog.members.toPlainText() == dialog.snippet'
    assert dialog.apply_button.isEnabled(), 'classes browser when row selected then snippet is class definition: expected dialog.apply_button.isEnabled()'
    copied = clipboard(tool)
    dialog.apply()
    assert copied == ["@Upper = [A B C];"] and dialog.last_result == {"copied": "@Upper = [A B C];"}, "classes browser when row selected then snippet is class definition: unexpected result"


def test_classes_browser_when_filter_matches_member_then_only_that_class(host):
    tool = host.load("Features/Classes Browser.py", modules=FEATURE_MODULES)
    class_font(host)
    dialog = tool.Dialog(None)
    dialog.search.setText("A B C")
    assert [r[0] for r in dialog.rows] == ["Upper"], "classes browser when filter matches member then only that class: expected [r[0] for r in dialog.rows] == ['Upper']"
    assert dialog.status.text == "1 of 3 feature classes", "classes browser when filter matches member then only that class: expected dialog.status.text == '1 of 3 feature classes'"
    dialog.search.setText("nothing-like-this")
    assert dialog.rows == [] and dialog.snippet == "", "classes browser when filter matches member then only that class: expected dialog.rows == [] and dialog.snippet == ''"
    assert dialog.members.toPlainText() == "No matching feature classes.", "classes browser when filter matches member then only that class: expected dialog.members.toPlainText() == 'No matching feature classes.'"
    assert not dialog.apply_button.isEnabled(), 'classes browser when filter matches member then only that class: expected not dialog.apply_button.isEnabled()'
    copied = clipboard(tool)
    dialog.apply()
    assert copied == [], "No snippet, nothing copied"


def test_classes_browser_when_no_font_then_no_classes(host):
    tool = host.load("Features/Classes Browser.py", modules=FEATURE_MODULES)
    dialog = tool.Dialog(None)
    assert dialog.all_rows == [] and dialog.status.text == "0 of 0 feature classes", "classes browser when no font then no classes: unexpected result"


def test_classes_browser_when_main_runs_as_script_then_window_opens(host):
    host.load("Features/Classes Browser.py", modules=FEATURE_MODULES)
    class_font(host)
    runpy.run_path(str(ROOT / "Scripts/Features/Classes Browser.py"), run_name="__main__")
    assert "features_classes_browser" in host.windows(), "classes browser when main runs as script then window opens: expected 'features_classes_browser' in host.windows()"


def test_classes_browser_run_when_groups_have_no_records_then_empty_rows(host):
    tool = host.load("Features/Classes Browser.py", modules=FEATURE_MODULES)
    groups = NS(items=lambda: [("A", NS(isFeaGroup=lambda: True))], getAsClassRecords=lambda: None)
    assert tool.run(groups) == [], "A missing record list is an empty browser, not an error"


# ---- Feature Code Viewer -------------------------------------------------------


def viewer_state(blocks: NS) -> None:
    blocks.blocks = {
        "prefix": "languagesystem DFLT dflt;\n",
        "features": [
            ("smcp", "feature smcp {\n sub a by a.sc;\n} smcp;\n"),
            ("liga", "feature liga { sub f i by f_i; } liga;\n"),
        ],
    }


def test_code_viewer_when_package_open_then_sources_include_prefix_and_features(host, blocks):
    tool = host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    viewer_state(blocks)
    open_font(host, ["a"])
    dialog = tool.Dialog(None)
    assert [t for t, _ in dialog.sources] == ["Prefix / languagesystems", "smcp", "liga"], "code viewer when package open then sources include prefix and features: unexpected result"
    assert dialog.feature.items == ["Prefix / languagesystems", "smcp", "liga"], "code viewer when package open then sources include prefix and features: expected dialog.feature.items == ['Prefix / languagesystems', 'smcp', 'liga']"
    assert dialog.code.plain == blocks.blocks["prefix"], "Prefix is the first view"
    assert dialog.status.text == "2 features · 0 search matches", "code viewer when package open then sources include prefix and features: expected dialog.status.text == '2 features · 0 search matches'"
    assert not dialog.apply_button.isEnabled(), "Find next needs a search term"


def test_code_viewer_when_search_typed_then_matches_highlighted_and_escaped(host, blocks):
    tool = host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    viewer_state(blocks)
    blocks.blocks["features"][0] = ("smcp", "feature smcp {\n sub a by a.sc; # <A>\n} smcp;\n")
    open_font(host, ["a"])
    dialog = tool.Dialog(None)
    dialog.feature.setCurrentIndex(1)
    dialog.search.setText("A")
    assert dialog.match_count == 4, "Every case-insensitive literal match counts"
    assert "&lt;" in dialog.code.html and "<span style=" in dialog.code.html, "code viewer when search typed then matches highlighted and escaped: expected '&lt;' in dialog.code.html and '<span style=' in dialog.code.html"
    assert dialog.status.text == "2 features · 4 search matches", "code viewer when search typed then matches highlighted and escaped: expected dialog.status.text == '2 features · 4 search matches'"
    assert dialog.apply_button.isEnabled(), "A term and a package enable Find next"


def test_code_viewer_when_apply_then_find_wraps_to_start(host, blocks):
    tool = host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    viewer_state(blocks)
    open_font(host, ["a"])
    dialog = tool.Dialog(None)
    dialog.feature.setCurrentIndex(1)
    dialog.search.setText("sub")
    dialog.code.find_results = [False, True]
    dialog.apply()
    assert dialog.code.found == ["sub", "sub"], "A failed find retries from the start"
    assert dialog.last_result == {"matches": 1}, "code viewer when apply then find wraps to start: expected dialog.last_result == {'matches': 1}"


def test_code_viewer_when_apply_without_term_then_no_search(host, blocks):
    tool = host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    viewer_state(blocks)
    open_font(host, ["a"])
    dialog = tool.Dialog(None)
    dialog.apply()
    assert dialog.code.found == [] and dialog.last_result is None, 'code viewer when apply without term then no search: expected dialog.code.found == [] and dialog.last_result is None'


def test_code_viewer_when_no_font_then_only_empty_prefix(host, blocks):
    tool = host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    dialog = tool.Dialog(None)
    assert dialog.sources == [("Prefix / languagesystems", "")], "code viewer when no font then only empty prefix: expected dialog.sources == [('Prefix / languagesystems', '')]"
    assert dialog.status.text == "0 features · 0 search matches", "code viewer when no font then only empty prefix: expected dialog.status.text == '0 features · 0 search matches'"


def test_code_viewer_run_when_features_given_then_copied_in_order(host, blocks):
    tool = host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    pairs = iter([("b", ""), ("a", "x")])
    assert tool.run(pairs) == [("b", ""), ("a", "x")], "Order and empty sources are kept"


def test_code_viewer_when_run_as_script_then_window_opens(host, blocks):
    host.load("Features/Feature Code Viewer.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    open_font(host, ["a"])
    runpy.run_path(str(ROOT / "Scripts/Features/Feature Code Viewer.py"), run_name="__main__")
    assert "features_code_viewer" in host.windows(), "code viewer when run as script then window opens: expected 'features_code_viewer' in host.windows()"


# ---- Build Suffix Substitution -------------------------------------------------


def build_dialog(host: Host, blocks: NS, names: list[str], **extra: Any) -> tuple[Any, Any]:
    tool = host.load("Features/Build Suffix Substitution.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    open_font(host, names, features=NS(), **extra)
    return tool, tool.Dialog(None)


def test_build_when_suffix_has_pairs_then_preview_and_apply_enabled(host, blocks):
    _, dialog = build_dialog(host, blocks, ["a", "a.sc", "b", "b.sc"])
    assert dialog.pairs == [("a", "a.sc"), ("b", "b.sc")], "build when suffix has pairs then preview and apply enabled: expected dialog.pairs == [('a', 'a.sc'), ('b', 'b.sc')]"
    assert dialog.new_code.startswith("feature smcp {") and dialog.new_code.endswith("\n"), "build when suffix has pairs then preview and apply enabled: unexpected result"
    assert dialog.apply_button.isEnabled() and dialog.copy_button.isEnabled(), 'build when suffix has pairs then preview and apply enabled: expected dialog.apply_button.isEnabled() and dialog.copy_button.isEnabled()'
    assert dialog.status.text == "2 pairs · font-wide, all masters · existing code preserved", "build when suffix has pairs then preview and apply enabled: unexpected result"
    assert dialog.table.row_texts(0) == ["a", "a.sc"], "build when suffix has pairs then preview and apply enabled: expected dialog.table.row_texts(0) == ['a', 'a.sc']"


def test_build_when_apply_then_blocks_written_and_preview_refreshed(host, blocks):
    _, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    preview = dialog.new_code
    assert preview.startswith("feature smcp {"), "A preview exists before apply"
    dialog.apply()
    new, references, undo = blocks.writes[0]
    assert dict(new["features"])["smcp"] == preview, "The written feature is exactly the previewed code"
    assert references == ["a", "a.sc"], "Both referenced glyphs are passed to the writer"
    assert undo == "Suffix Substitution Builder", "The undo step is named after the tool"
    assert dialog.last_result["tag"] == "smcp" and dialog.last_result["changed"] == 1, "Receipt names tag and count"
    assert dialog.status.text == "Feature source appended. Compile it in the Features panel to test.", "Status reports the append"


def test_build_when_feature_already_substitutes_glyph_then_apply_refused(host, blocks):
    blocks.blocks["features"] = [("smcp", "feature smcp {\n    sub q by q.sc;\n} smcp;\n")]
    _, dialog = build_dialog(host, blocks, ["a", "a.sc", "q", "q.sc"])
    # q already has a rule, so the whole preview is refused with a reason.
    assert not dialog.apply_button.isEnabled(), "A duplicated source glyph disables apply"
    assert dialog.status.text.startswith("Existing feature already substitutes"), "The refusal reason is shown"
    assert dialog.copy_button.isEnabled(), "The snippet stays copyable when append is refused"


def test_build_when_feature_has_odd_closing_then_copy_only(host, blocks):
    blocks.blocks["features"] = [("smcp", "lookup x { } x;")]
    _, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    assert dialog.status.text.startswith("Existing feature has no simple closing tag"), "build when feature has odd closing then copy only: unexpected result"
    assert not dialog.apply_button.isEnabled(), 'build when feature has odd closing then copy only: expected not dialog.apply_button.isEnabled()'


def test_build_when_no_pairs_then_status_reports_and_nothing_enabled(host, blocks):
    _, dialog = build_dialog(host, blocks, ["a", "b"])
    assert dialog.status.text == "No valid base / alternate pairs for this suffix.", "build when no pairs then status reports and nothing enabled: unexpected result"
    assert not dialog.copy_button.isEnabled() and not dialog.apply_button.isEnabled(), 'build when no pairs then status reports and nothing enabled: unexpected result'


def test_build_when_bad_tag_then_error_status_and_disabled(host, blocks):
    _, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    dialog.tag.setText("sm")
    assert "four ASCII" in dialog.status.text, "A malformed tag is explained in the status"
    assert not dialog.apply_button.isEnabled() and not dialog.copy_button.isEnabled(), 'build when bad tag then error status and disabled: unexpected result'


def test_build_when_no_font_then_open_font_message(host, blocks):
    tool = host.load("Features/Build Suffix Substitution.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    dialog = tool.Dialog(None)
    assert dialog.status.text == "Open a font first.", "build when no font then open font message: expected dialog.status.text == 'Open a font first.'"
    assert not dialog.apply_button.isEnabled() and dialog.new_code == "", "build when no font then open font message: expected not dialog.apply_button.isEnabled() and dialog.new_code == ''"


def test_build_when_glyphs_change_after_preview_then_apply_refused(host, blocks):
    _, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    host.font.glyphs.append(NS(name="a.sc.extra"))
    host.font.glyphs[:] = [NS(name="a")]
    with pytest.raises(ValueError, match="Referenced glyphs or controls changed"):
        dialog.apply()
    assert not dialog._preview_valid and blocks.writes == [], "Nothing is written on a stale preview"


def test_build_when_tag_property_assigned_then_preview_refreshed_for_new_tag(host, blocks):
    # In PythonQt a property assignment emits textChanged, so the preview follows at once.
    _, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    dialog.tag.text = "salt"
    assert dialog.new_code.startswith("feature salt {"), "The preview was rebuilt for the new tag"
    dialog.apply()
    assert [t for t, _ in blocks.writes[0][0]["features"]] == ["salt"], "The new tag is written"


def test_build_when_copy_clicked_then_preview_text_on_clipboard(host, blocks):
    tool, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    copied = clipboard(tool)
    dialog.copy_button.clicked.emit()
    assert copied == [dialog.code.toPlainText()], "Copy sends the visible preview"


def test_build_run_when_preview_does_not_match_source_then_refused(host, blocks):
    tool, _ = build_dialog(host, blocks, ["a", "a.sc"])
    expected = {"prefix": "p", "features": [("smcp", "OLD")]}
    with pytest.raises(ValueError, match="does not match its source snapshot"):
        tool.run(NS(), None, "smcp", "DIFFERENT", "new", expected_blocks=expected, references=[])


def test_build_run_when_tag_new_then_appended_after_existing(host, blocks):
    tool, _ = build_dialog(host, blocks, ["a", "a.sc"])
    expected = {"prefix": "p", "features": [("liga", "L")]}
    receipt = tool.run(NS(), None, "smcp", "", "S", expected_blocks=expected, references=["a"])
    assert blocks.writes[-1][0]["features"] == [("liga", "L"), ("smcp", "S")], "build run when tag new then appended after existing: expected blocks.writes[-1][0]['features'] == [('liga', 'L'), ('smcp', 'S')]"
    assert receipt == {"tag": "smcp", "code": "S", "changed": 1}, "build run when tag new then appended after existing: expected receipt == {'tag': 'smcp', 'code': 'S', 'changed': 1}"


def test_build_run_when_tag_exists_then_replaced_in_place(host, blocks):
    tool, _ = build_dialog(host, blocks, ["a", "a.sc"])
    expected = {"prefix": "p", "features": [("smcp", "OLD"), ("liga", "L")]}
    tool.run(NS(), None, "smcp", "OLD", "NEW", expected_blocks=expected, references=[])
    assert blocks.writes[-1][0]["features"] == [("smcp", "NEW"), ("liga", "L")], "build run when tag exists then replaced in place: expected blocks.writes[-1][0]['features'] == [('smcp', 'NEW'), ('liga', 'L')]"


def test_build_append_code_when_old_empty_then_snippet_only(host, blocks):
    tool, _ = build_dialog(host, blocks, ["a", "a.sc"])
    assert tool.append_code("  \n", "smcp", [("a", "a.sc")]) == tool.feature_text("smcp", [("a", "a.sc")]), "build append code when old empty then snippet only: unexpected result"


def test_build_when_run_as_script_then_window_opens(host, blocks):
    host.load("Features/Build Suffix Substitution.py", modules=FEATURE_MODULES, fp_blocks=blocks.module)
    open_font(host, ["a", "a.sc"], features=NS())
    runpy.run_path(str(ROOT / "Scripts/Features/Build Suffix Substitution.py"), run_name="__main__")
    assert "features_build_substitution" in host.windows(), "build when run as script then window opens: expected 'features_build_substitution' in host.windows()"


# ---- Alternate Preview ---------------------------------------------------------


class Box:
    """Bounding-box double with Qt-style accessors."""

    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self._v = (x, y, w, h)

    def x(self) -> float:
        return self._v[0]

    def y(self) -> float:
        return self._v[1]

    def width(self) -> float:
        return self._v[2]

    def height(self) -> float:
        return self._v[3]


def layer(box: Box | None = None, shapes: list | None = None) -> NS:
    return NS(isNull=False, boundingBox=box or Box(0, 0, 500, 700), shapes=shapes or [])


def alt_package(glyphs: dict[str, dict[str, Any]]) -> NS:
    """Package whose findName returns glyphs with per-master layers."""

    def find_name(name: str) -> Any:
        layers = glyphs.get(name)
        return None if layers is None else NS(findLayer=lambda master: layers.get(master))

    return NS(**{**vars(PACKAGE), "findName": find_name})


def test_alternate_preview_run_when_alternates_then_base_first_then_sorted(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    names = ["a", "a-cy", "a.sc", "a.alt", "b"]
    assert tool.run(names, "a") == ["a", "a.alt", "a.sc"], "a-cy is a different base"
    assert tool.run(["a.sc"], "a") == ["a.sc"], "A missing base is not invented"


def test_alternate_preview_when_current_glyph_then_base_filled_and_status_counts(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    open_font(host, ["g", "g.alt", "g.sc"])
    host.glyph = NS(name="g.alt")
    dialog = tool.Dialog(None)
    assert dialog.base.text == "g", "The base comes from the current glyph name"
    assert dialog.preview_names == ["g", "g.alt", "g.sc"], "alternate preview when current glyph then base filled and status counts: expected dialog.preview_names == ['g', 'g.alt', 'g.sc']"
    assert dialog.chosen_masters == ["Regular"], "Default scope is the current master"
    assert dialog.status.text == "3 glyphs × 1 masters · scroll to see every row", "alternate preview when current glyph then base filled and status counts: expected dialog.status.text == '3 glyphs × 1 masters · scroll to see every row'"
    assert dialog.apply_button.isEnabled(), 'alternate preview when current glyph then base filled and status counts: expected dialog.apply_button.isEnabled()'
    assert dialog.scope.items == ["Current master (Regular)", "All masters (2)"], "alternate preview when current glyph then base filled and status counts: expected dialog.scope.items == ['Current master (Regular)', 'All masters (2)']"


def test_alternate_preview_when_all_masters_chosen_then_rows_for_each_master(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc"])
    dialog = tool.Dialog(None)
    dialog.scope.setCurrentIndex(1)
    assert dialog.chosen_masters == ["Regular", "Bold"], "alternate preview when all masters chosen then rows for each master: expected dialog.chosen_masters == ['Regular', 'Bold']"
    assert dialog.status.text == "2 glyphs × 2 masters · scroll to see every row", "alternate preview when all masters chosen then rows for each master: expected dialog.status.text == '2 glyphs × 2 masters · scroll to see every row'"


def test_alternate_preview_when_base_unknown_then_nothing_to_proof(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    open_font(host, ["a"])
    dialog = tool.Dialog(None)
    dialog.base.setText("zzz")
    assert dialog.preview_names == [] and not dialog.apply_button.isEnabled(), 'alternate preview when base unknown then nothing to proof: expected dialog.preview_names == [] and (not dialog.apply_button.isEnabled())'
    dialog.base.setText("   ")
    assert dialog.preview_names == [], "A blank base shows no proof"


def test_alternate_preview_when_apply_then_result_records_names_and_masters(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    open_font(host, ["a", "a.sc"])
    dialog = tool.Dialog(None)
    dialog.apply()
    assert dialog.last_result == {"names": ["a", "a.sc"], "masters": ["Regular"]}, "alternate preview when apply then result records names and masters: expected dialog.last_result == {'names': ['a', 'a.sc'], 'masters': ['Regular']}"


def test_alternate_preview_when_no_font_then_empty_proof(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    dialog = tool.Dialog(None)
    assert dialog.chosen_masters == [] and dialog.scope.items[0] == "Current master (none)", "alternate preview when no font then empty proof: unexpected result"


class Painter:
    """Painter double recording text and fills."""

    Antialiasing = 1
    instances: list["Painter"] = []

    def __init__(self, *_: Any) -> None:
        Painter.instances.append(self)
        self.texts: list[tuple] = []
        self.fills: list[Any] = []
        self.ended = False

    def setRenderHint(self, flag: Any) -> None:
        pass

    def setPen(self, pen: Any) -> None:
        pass

    def drawText(self, x: int, y: int, text: str) -> None:
        self.texts.append((x, y, text))

    def fillPath(self, path: Any, brush: Any) -> None:
        self.fills.append(path)

    def end(self) -> None:
        self.ended = True


def proof_dialog(host: Host, tool: Any, glyphs: dict) -> Any:
    open_font(host, list(glyphs))
    host.package = alt_package(glyphs)
    dialog = tool.Dialog(None)
    dialog.canvas.width = 450
    return dialog


def test_alternate_preview_paint_when_names_empty_then_hint_text_drawn(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    tool.QtGui.QPainter = Painter
    tool.QtGui.QTransform = lambda *a: NS(map=lambda path: path)
    dialog = proof_dialog(host, tool, {})
    painter = Painter()
    dialog.canvas.draw_proof(painter)
    assert painter.texts == [(20, 45, "Enter an existing base glyph name to see its alternates.")], "alternate preview paint when names empty then hint text drawn: unexpected result"


def test_alternate_preview_paint_when_glyphs_have_layers_then_labels_and_fills(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    tool.QtGui.QTransform = lambda *a: NS(map=lambda path: path)
    tool.QtGui.QFontMetrics = lambda font: NS(elidedText=lambda name, mode, width: name + "!")
    closed = NS(isEmpty=lambda: False)
    shape = NS(closedPath=closed, openedPath=None, transform=NS(map=lambda part: part))
    glyphs = {
        "a": {"Regular": layer(shapes=[shape]), "Bold": layer()},
        "a.sc": {"Regular": layer(Box(10, -20, 300, 600))},
    }
    dialog = proof_dialog(host, tool, glyphs)
    dialog.chosen_masters = ["Regular", "Bold"]
    painter = Painter()
    dialog.canvas.draw_proof(painter)
    labels = [t[2] for t in painter.texts]
    assert "a!" in labels and "a.sc!" in labels, "Each glyph name is elided and drawn"
    assert "Regular" in labels and "Bold" in labels, "Each master row is labelled"
    assert "Missing layer" in labels, "a.sc has no Bold layer so the row says so"
    assert len(painter.fills) == 3, "Every available layer is filled once"


def test_alternate_preview_layer_path_when_parts_empty_or_missing_then_only_real_added(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    added: list[Any] = []

    class Path:
        def setFillRule(self, rule: Any) -> None:
            pass

        def addPath(self, part: Any) -> None:
            added.append(part)

    tool.QtGui.QPainterPath = Path
    real = NS(isEmpty=lambda: False)
    empty = NS(isEmpty=lambda: True)
    shapes = [
        NS(closedPath=real, openedPath=empty, transform=NS(map=lambda p: ("mapped", p))),
        NS(closedPath=None, openedPath=real, transform=NS(map=lambda p: ("mapped", p))),
    ]
    tool.layer_path(NS(shapes=shapes))
    assert added == [("mapped", real), ("mapped", real)], "Empty and absent parts are skipped"


def test_alternate_preview_paint_event_when_draw_fails_then_error_in_status_and_painter_ended(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    open_font(host, ["a"])
    dialog = tool.Dialog(None)
    Painter.instances = []
    tool.QtGui.QPainter = Painter
    dialog.canvas.draw_proof = lambda p: (_ for _ in ()).throw(RuntimeError("boom"))
    dialog.canvas.paintEvent(None)
    painter = Painter.instances[0]
    assert dialog.status.text == "Proof error: boom" and dialog.canvas._error == "boom", "alternate preview paint event when draw fails then error in status and painter ended: unexpected result"
    assert painter.ended, "The painter is always ended"


def test_alternate_preview_paint_event_when_ok_then_painter_ended_and_layer_filled(host):
    tool = host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    tool.QtGui.QTransform = lambda *a: NS(map=lambda path: path)
    tool.QtGui.QFontMetrics = lambda font: NS(elidedText=lambda name, mode, width: name)
    dialog = proof_dialog(host, tool, {"a": {"Regular": layer()}})
    Painter.instances = []
    tool.QtGui.QPainter = Painter
    dialog.canvas.paintEvent(None)
    painter = Painter.instances[0]
    assert painter.ended and dialog.canvas._error == "", "A clean paint records no error"
    assert len(painter.fills) == 1 and (10, 18, "Regular") in painter.texts, "alternate preview paint event when ok then painter ended and layer filled: expected len(painter.fills) == 1 and (10, 18, 'Regular') in painter.texts"


def test_alternate_preview_when_run_as_script_then_window_opens(host):
    host.load("Features/Alternate Preview.py", modules=FEATURE_MODULES)
    open_font(host, ["a"])
    runpy.run_path(str(ROOT / "Scripts/Features/Alternate Preview.py"), run_name="__main__")
    assert "features_alternate_preview" in host.windows(), "alternate preview when run as script then window opens: expected 'features_alternate_preview' in host.windows()"


def test_build_when_existing_feature_has_free_source_then_statements_inserted_before_closing(
    host, blocks
):
    old = "feature smcp {\n    sub q by q.sc;\n} smcp;\n"
    blocks.blocks["features"] = [("smcp", old)]
    _, dialog = build_dialog(host, blocks, ["a", "a.sc"])
    assert dialog.new_code == "feature smcp {\n    sub q by q.sc;\n    sub a by a.sc;\n} smcp;\n", "build when existing feature has free source then statements inserted before closing: unexpected result"
    assert dialog.apply_button.isEnabled(), "A clean append is allowed"
    dialog.apply()
    assert dict(blocks.blocks["features"])["smcp"].count("sub ") == 2, "Existing rule kept"


@pytest.mark.parametrize(
    ("suffix", "tag"),
    [
        ("ss05", "ss05"),
        ("cv12", "cv12"),
        ("locl", "salt"),
        ("loclPLK", "locl"),
        ("sc.alt", "smcp"),
        ("weird", "salt"),
    ],
)
def test_suffix_report_suggested_tag_when_suffix_then_conventional_tag(host, suffix, tag):
    report = host.load("Features/Suffix Report.py", modules=FEATURE_MODULES)
    assert report.suggested_tag(suffix) == tag, f"{suffix} should suggest {tag}"
