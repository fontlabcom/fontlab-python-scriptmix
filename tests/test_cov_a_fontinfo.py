# this_file: tests/test_cov_a_fontinfo.py
# SPDX-License-Identifier: Apache-2.0
"""Coverage round A: the four Font Info dialogs on the real App panel shell."""

from __future__ import annotations

import runpy
from types import SimpleNamespace as NS
from typing import Any

import pytest
from _cov_a_support import ROOT, Host, host  # noqa: F401

FONT_INFO = "Font Info/"


class MasterPackage:
    """Package double: per-master Font Info records and a switchable master."""

    def __init__(self, masters: tuple[str, ...] = ("Regular", "Bold"), package_id: int = 11, **fields: Any) -> None:
        self.id = package_id
        self.fgId = 100 + package_id
        self.masters = list(masters)
        self.master = self.masters[0]
        self.infos = {m: NS(**fields) for m in self.masters}
        self.switches: list[str] = []

    @property
    def info(self) -> Any:
        return self.infos[self.master]

    @property
    def versionMajor(self) -> int:  # noqa: N802 - FontLab property name
        return self.info.versionMajor

    @property
    def versionMinor(self) -> int:  # noqa: N802 - FontLab property name
        return self.info.versionMinor

    def setMaster(self, name: str) -> None:  # noqa: N802 - FontLab method name
        self.switches.append(name)
        self.master = name


def recorder(host: Host, writes: list) -> dict:
    """``write_font_info`` double that records the plan and applies it to the package."""

    def write(package: Any, changes: list, *, undo_name: str) -> dict:
        writes.append((list(changes), undo_name))
        for master, key, _old, new in changes:
            for name, info in package.infos.items():
                if master is None or master == name:
                    setattr(info, key, new)
        return {"changed": len(changes)}

    return {"write_font_info": write}


def open_package(host: Host, **fields: Any) -> MasterPackage:
    host.package = MasterPackage(**fields)
    return host.package


# ---- Bump Font Version -----------------------------------------------------------

BUMP = dict(versionMajor=1, versionMinor=5, openTypeNameVersion="Version 1.005", note="")


def bump_tool(host: Host, writes: list) -> Any:
    return host.load(FONT_INFO + "Bump Font Version.py", scripting=recorder(host, writes))


@pytest.mark.parametrize(
    ("major", "minor", "mode", "expected"),
    [(1, 5, "minor", (1, 6)), (1, 999, "minor", (2, 0)), (1, 5, "major", (2, 0)), (0, 0, "minor", (0, 1))],
)
def test_bumped_when_valid_then_expected_version(host, major, minor, mode, expected):
    tool = bump_tool(host, [])
    assert tool.bumped(major, minor, mode) == expected, f"{major}.{minor} {mode}"


@pytest.mark.parametrize(
    ("major", "minor", "mode", "message"),
    [
        (65535, 999, "minor", "exceed 65535"),
        (65535, 0, "major", "exceed 65535"),
        (1, 1000, "minor", "major 0–65535"),
        (-1, 0, "minor", "major 0–65535"),
        (1, 0, "patch", "major 0–65535"),
        (1.5, 0, "minor", "major 0–65535"),
    ],
)
def test_bumped_when_out_of_range_then_refused(host, major, minor, mode, message):
    tool = bump_tool(host, [])
    with pytest.raises(ValueError, match=message):
        tool.bumped(major, minor, mode)


def test_bump_dialog_when_opened_then_preview_lists_version_and_dated_notes(host):
    writes: list = []
    tool = bump_tool(host, writes)
    package = open_package(host, **BUMP)
    package.infos["Bold"].note = "Existing"
    dialog = tool.Dialog(None)
    assert dialog.table.rowCount == 5, "Three version fields plus one dated note per master"
    assert dialog.table.row_texts(0) == ["Major version", "1", "1"], "bump dialog when opened then preview lists version and dated notes: expected dialog.table.row_texts(0) == ['Major version', '1', '1']"
    assert dialog.table.row_texts(1) == ["Minor version", "5", "6"], "bump dialog when opened then preview lists version and dated notes: expected dialog.table.row_texts(1) == ['Minor version', '5', '6']"
    assert dialog.table.row_texts(2)[2] == "Version 1.006", "bump dialog when opened then preview lists version and dated notes: expected dialog.table.row_texts(2)[2] == 'Version 1.006'"
    assert dialog.table.row_texts(3)[0] == "Note · Regular", "bump dialog when opened then preview lists version and dated notes: expected dialog.table.row_texts(3)[0] == 'Note · Regular'"
    assert dialog.table.row_texts(4)[2].startswith("Existing\n"), "Existing note text is kept"
    assert dialog.apply_button.isEnabled() and dialog._preview_valid, 'bump dialog when opened then preview lists version and dated notes: expected dialog.apply_button.isEnabled() and dialog._preview_valid'
    assert dialog.status.text == "Minor uses three digits; existing notes are preserved.", "bump dialog when opened then preview lists version and dated notes: unexpected result"
    assert package.master == "Regular" and package.switches[-1] == "Regular", "Master is restored"


def test_bump_dialog_when_mode_major_then_minor_resets(host):
    tool = bump_tool(host, [])
    open_package(host, **BUMP)
    dialog = tool.Dialog(None)
    dialog.mode.setCurrentIndex(1)
    assert dialog.table.row_texts(0) == ["Major version", "1", "2"], "bump dialog when mode major then minor resets: expected dialog.table.row_texts(0) == ['Major version', '1', '2']"
    assert dialog.table.row_texts(1) == ["Minor version", "5", "0"], "bump dialog when mode major then minor resets: expected dialog.table.row_texts(1) == ['Minor version', '5', '0']"


def test_bump_dialog_when_dated_note_off_then_only_version_rows(host):
    tool = bump_tool(host, [])
    package = open_package(host, **BUMP)
    dialog = tool.Dialog(None)
    package.switches.clear()
    dialog.date_note.setChecked(False)
    assert dialog.table.rowCount == 3, "Without notes only the three version fields remain"
    assert package.switches == [], "Notes off means no master switching"


def test_bump_dialog_when_apply_then_plan_written_and_next_bump_previewed(host):
    writes: list = []
    tool = bump_tool(host, writes)
    package = open_package(host, **BUMP)
    dialog = tool.Dialog(None)
    dialog.apply()
    changes, undo = writes[0]
    assert undo == "Bump Font Version" and len(changes) == 5, "bump dialog when apply then plan written and next bump previewed: expected undo == 'Bump Font Version' and len(changes) == 5"
    assert ("versionMinor" in [c[1] for c in changes]) and package.infos["Regular"].versionMinor == 6, "bump dialog when apply then plan written and next bump previewed: unexpected result"
    assert dialog.last_result == {"changed": 5}, "bump dialog when apply then plan written and next bump previewed: expected dialog.last_result == {'changed': 5}"
    assert dialog.table.row_texts(1) == ["Minor version", "6", "7"], "Preview moves on to the next bump"
    assert dialog.status.text == "Version applied; preview now shows the next bump.", "bump dialog when apply then plan written and next bump previewed: unexpected result"


def test_bump_dialog_when_version_cannot_grow_then_status_explains_and_apply_disabled(host):
    tool = bump_tool(host, [])
    open_package(host, versionMajor=65535, versionMinor=999, openTypeNameVersion="v", note="")
    dialog = tool.Dialog(None)
    assert dialog.status.text == "The major version would exceed 65535.", "bump dialog when version cannot grow then status explains and apply disabled: expected dialog.status.text == 'The major version would exceed 65535.'"
    assert not dialog.apply_button.isEnabled() and not dialog._preview_valid, 'bump dialog when version cannot grow then status explains and apply disabled: expected not dialog.apply_button.isEnabled() and (not dialog._preview_valid)'


def test_bump_dialog_when_no_font_then_nothing_to_apply(host):
    tool = bump_tool(host, [])
    dialog = tool.Dialog(None)
    assert not dialog.apply_button.isEnabled(), 'bump dialog when no font then nothing to apply: expected not dialog.apply_button.isEnabled()'
    assert dialog.subtitle.text == "Open a font, then reopen this tool.", "bump dialog when no font then nothing to apply: expected dialog.subtitle.text == 'Open a font, then reopen this tool.'"


def test_bump_dialog_when_font_switched_then_apply_refused(host):
    writes: list = []
    tool = bump_tool(host, writes)
    open_package(host, **BUMP)
    dialog = tool.Dialog(None)
    host.package = MasterPackage(package_id=99, **BUMP)
    with pytest.raises(ValueError, match="Activate the original font"):
        dialog.apply()
    assert writes == [], "A foreign font is never written"


def test_bump_run_when_called_then_plan_applied_in_one_write(host):
    writes: list = []
    tool = bump_tool(host, writes)
    package = open_package(host, **BUMP)
    assert tool.run(package, "minor", False, "2026-01-02") == {"changed": 3}, "bump run when called then plan applied in one write: expected tool.run(package, 'minor', False, '2026-01-02') == {'changed': 3}"
    assert [c[1] for c in writes[0][0]] == ["versionMajor", "versionMinor", "openTypeNameVersion"], "bump run when called then plan applied in one write: unexpected result"


def test_bump_version_plan_when_dated_then_note_line_uses_day_and_name(host):
    tool = bump_tool(host, [])
    package = open_package(host, **BUMP)
    package.infos["Bold"].note = "Old"
    plan = tool.version_plan(package, "minor", True, "2026-01-02")
    notes = {c[0]: c[3] for c in plan if c[1] == "note"}
    assert notes == {"Regular": "2026-01-02: Version 1.006", "Bold": "Old\n2026-01-02: Version 1.006"}, "bump version plan when dated then note line uses day and name: unexpected result"


def test_bump_main_when_run_as_script_then_window_opens(host):
    bump_tool(host, [])
    open_package(host, **BUMP)
    runpy.run_path(str(ROOT / "Scripts/Font Info/Bump Font Version.py"), run_name="__main__")
    assert "fontinfo_version_bumper" in host.windows(), "bump main when run as script then window opens: expected 'fontinfo_version_bumper' in host.windows()"


# ---- Names and Credits -----------------------------------------------------------

NAMES = dict(
    familyName="Acme",
    styleName="Regular",
    openTypeNameDesigner="Ann",
    copyright="(c) Acme",
    openTypeNameVersion="Version 1.005",
)


def names_tool(host: Host, writes: list) -> Any:
    return host.load(FONT_INFO + "Names and Credits.py", scripting=recorder(host, writes))


def test_validate_names_when_blank_or_control_or_bad_version_then_refused(host):
    tool = names_tool(host, [])
    assert tool.validate_names(dict(NAMES)) == NAMES, 'validate names when blank or control or bad version then refused: expected tool.validate_names(dict(NAMES)) == NAMES'
    with pytest.raises(ValueError, match="must not be blank"):
        tool.validate_names({**NAMES, "styleName": "  "})
    with pytest.raises(ValueError, match="control characters"):
        tool.validate_names({**NAMES, "copyright": "a\nb"})
    with pytest.raises(ValueError, match="Version major.minor"):
        tool.validate_names({**NAMES, "openTypeNameVersion": "1.005"})
    assert tool.validate_names({**NAMES, "openTypeNameVersion": "Version 2.1; build 3"}), "validate names when blank or control or bad version then refused: unexpected result"


def test_names_run_when_values_valid_then_style_scoped_to_current_master(host):
    writes: list = []
    tool = names_tool(host, writes)
    package = open_package(host, **NAMES)
    tool.run(package, {**NAMES, "styleName": "Book"})
    scopes = {c[1]: c[0] for c in writes[0][0]}
    assert scopes["styleName"] == "Regular" and scopes["familyName"] is None, "names run when values valid then style scoped to current master: expected scopes['styleName'] == 'Regular' and scopes['familyName'] is None"
    assert writes[0][1] == "Names & Credits", "names run when values valid then style scoped to current master: expected writes[0][1] == 'Names & Credits'"


def test_names_dialog_when_opened_then_fields_prefilled_and_nothing_changed(host):
    tool = names_tool(host, [])
    open_package(host, **NAMES)
    dialog = tool.Dialog(None)
    assert {k: e.text for k, e in dialog.fields.items()} == NAMES, 'names dialog when opened then fields prefilled and nothing changed: expected {k: e.text for k, e in dialog.fields.items()} == NAMES'
    assert dialog.table.rowCount == 0 and not dialog.apply_button.isEnabled(), 'names dialog when opened then fields prefilled and nothing changed: expected dialog.table.rowCount == 0 and (not dialog.apply_button.isEnabled())'
    assert dialog.status.text == "0 fields changed · style name applies to the current master only", "names dialog when opened then fields prefilled and nothing changed: unexpected result"


def test_names_dialog_when_field_edited_then_changed_row_and_apply_enabled(host):
    writes: list = []
    tool = names_tool(host, writes)
    package = open_package(host, **NAMES)
    dialog = tool.Dialog(None)
    dialog.fields["familyName"].setText("Acme Sans")
    dialog.fields["styleName"].setText("Book")
    assert dialog.table.rowCount == 2, 'names dialog when field edited then changed row and apply enabled: expected dialog.table.rowCount == 2'
    assert dialog.table.row_texts(0) == ["Family", "Acme", "Acme Sans"], "names dialog when field edited then changed row and apply enabled: expected dialog.table.row_texts(0) == ['Family', 'Acme', 'Acme Sans']"
    assert dialog.apply_button.isEnabled(), 'names dialog when field edited then changed row and apply enabled: expected dialog.apply_button.isEnabled()'
    dialog.apply()
    assert package.infos["Regular"].familyName == "Acme Sans", "names dialog when field edited then changed row and apply enabled: expected package.infos['Regular'].familyName == 'Acme Sans'"
    assert dialog.status.text == "Applied 5 fields", "All five planned fields are written"
    assert dialog.table.rowCount == 0, "After apply nothing differs any more"


def test_names_dialog_when_invalid_edit_then_error_status_and_apply_disabled(host):
    tool = names_tool(host, [])
    open_package(host, **NAMES)
    dialog = tool.Dialog(None)
    dialog.fields["styleName"].setText("")
    assert dialog.status.text == "Family and style must not be blank.", "names dialog when invalid edit then error status and apply disabled: expected dialog.status.text == 'Family and style must not be blank.'"
    assert not dialog.apply_button.isEnabled(), 'names dialog when invalid edit then error status and apply disabled: expected not dialog.apply_button.isEnabled()'


def test_names_dialog_when_master_changed_then_apply_refused(host):
    writes: list = []
    tool = names_tool(host, writes)
    package = open_package(host, **NAMES)
    dialog = tool.Dialog(None)
    dialog.fields["familyName"].setText("Other")
    package.master = "Bold"
    with pytest.raises(ValueError, match="Master changed since preview"):
        dialog.apply()
    assert writes == [], 'names dialog when master changed then apply refused: expected writes == []'


def test_names_dialog_when_no_font_then_empty_form(host):
    tool = names_tool(host, [])
    dialog = tool.Dialog(None)
    assert all(edit.text == "" for edit in dialog.fields.values()), "names dialog when no font then empty form: expected all((edit.text == '' for edit in dialog.fields.values()))"
    assert not dialog.apply_button.isEnabled(), 'names dialog when no font then empty form: expected not dialog.apply_button.isEnabled()'


def test_names_main_when_run_as_script_then_window_opens(host):
    names_tool(host, [])
    open_package(host, **NAMES)
    runpy.run_path(str(ROOT / "Scripts/Font Info/Names and Credits.py"), run_name="__main__")
    assert "fontinfo_names_editor" in host.windows(), "names main when run as script then window opens: expected 'fontinfo_names_editor' in host.windows()"


# ---- Master Metrics Table --------------------------------------------------------

METRICS = dict(ascender=800.0, descender=-200.0, xHeight=500.0, capHeight=700.0)


def metrics_tool(host: Host, writes: list) -> Any:
    return host.load(FONT_INFO + "Master Metrics Table.py", scripting=recorder(host, writes))


def metrics_package(host: Host) -> MasterPackage:
    package = open_package(host, **METRICS)
    package.infos["Bold"].ascender = 820.0
    return package


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ([1, 2, 3], "finite metrics"),
        ([float("nan"), 0, 0, 0], "finite metrics"),
        ([800, -200, 500, 40000], "finite metrics"),
        ([800, 10, 500, 700], "Expected descender"),
        ([800, -200, 750, 700], "Expected descender"),
        ([600, -200, 500, 700], "Expected descender"),
    ],
)
def test_validate_metrics_when_invalid_then_refused(host, values, message):
    tool = metrics_tool(host, [])
    with pytest.raises(ValueError, match=message):
        tool.validate_metrics(values)


def test_validate_metrics_when_ordered_then_returned_unchanged(host):
    tool = metrics_tool(host, [])
    assert tool.validate_metrics([800, -200, 500, 700]) == [800, -200, 500, 700], 'validate metrics when ordered then returned unchanged: expected tool.validate_metrics([800, -200, 500, 700]) == [800, -200, 500, 700]'


def test_master_values_when_read_then_each_master_listed_and_master_restored(host):
    tool = metrics_tool(host, [])
    package = metrics_package(host)
    assert tool.master_values(package) == [
        ("Regular", [800.0, -200.0, 500.0, 700.0]),
        ("Bold", [820.0, -200.0, 500.0, 700.0]),
    ], "master values when read then each master listed and master restored: unexpected result"
    assert package.master == "Regular", "master values when read then each master listed and master restored: expected package.master == 'Regular'"


def test_metrics_run_when_rows_given_then_single_plan_written(host):
    writes: list = []
    tool = metrics_tool(host, writes)
    package = metrics_package(host)
    result = tool.run(package, [("Regular", [810, -210, 510, 710])])
    assert result == {"changed": 4}, "metrics run when rows given then single plan written: expected result == {'changed': 4}"
    assert [c[:2] for c in writes[0][0]] == [
        ("Regular", "ascender"),
        ("Regular", "descender"),
        ("Regular", "xHeight"),
        ("Regular", "capHeight"),
    ], "metrics run when rows given then single plan written: unexpected result"
    assert writes[0][0][0][2] == 800.0, "The previous value comes from the font"


def test_metrics_run_when_row_invalid_then_nothing_written(host):
    writes: list = []
    tool = metrics_tool(host, writes)
    package = metrics_package(host)
    with pytest.raises(ValueError, match="Expected descender"):
        tool.run(package, [("Regular", [700, 10, 500, 700])])
    assert writes == [], 'metrics run when row invalid then nothing written: expected writes == []'


def edit_cell(dialog: Any, row: int, column: int, text: str) -> None:
    """Edit a table cell the way a user would, then notify the view."""
    dialog.table.item(row, column).setText(text)
    dialog.table.itemChanged.emit(dialog.table.item(row, column))


def test_metrics_dialog_when_opened_then_one_row_per_master_and_apply_disabled(host):
    tool = metrics_tool(host, [])
    metrics_package(host)
    dialog = tool.Dialog(None)
    assert dialog.table.rowCount == 2 and dialog.table.row_texts(1)[:2] == ["Bold", "820.0"], "metrics dialog when opened then one row per master and apply disabled: unexpected result"
    assert dialog.table.current == 0, "The first master row is current"
    assert not dialog.apply_button.isEnabled(), "Unedited metrics have nothing to apply"
    assert dialog.status.text == "Double-click a number to edit. All rows are validated before Apply.", "metrics dialog when opened then one row per master and apply disabled: unexpected result"


def test_metrics_dialog_when_value_edited_then_plan_ready_and_apply_writes(host):
    writes: list = []
    tool = metrics_tool(host, writes)
    package = metrics_package(host)
    dialog = tool.Dialog(None)
    edit_cell(dialog, 0, 1, "810")
    assert dialog.apply_button.isEnabled(), "A changed number enables Apply"
    assert dialog._plan[0] == ("Regular", "ascender", 800.0, 810.0), "metrics dialog when value edited then plan ready and apply writes: expected dialog._plan[0] == ('Regular', 'ascender', 800.0, 810.0)"
    dialog.apply()
    assert package.infos["Regular"].ascender == 810.0 and dialog.last_result == {"changed": 8}, "metrics dialog when value edited then plan ready and apply writes: unexpected result"
    assert dialog.status.text == "Applied 8 metric fields", "metrics dialog when value edited then plan ready and apply writes: expected dialog.status.text == 'Applied 8 metric fields'"
    assert not dialog.apply_button.isEnabled(), "After apply the table equals the font"


@pytest.mark.parametrize("text", ["abc", "9000000", "50"])
def test_metrics_dialog_when_bad_number_then_error_and_apply_disabled(host, text):
    tool = metrics_tool(host, [])
    metrics_package(host)
    dialog = tool.Dialog(None)
    edit_cell(dialog, 0, 2, text)
    assert not dialog.apply_button.isEnabled() and not dialog._preview_valid, 'metrics dialog when bad number then error and apply disabled: expected not dialog.apply_button.isEnabled() and (not dialog._preview_valid)'
    assert dialog.status.text, f"Bad value {text!r} is explained in the status"
    assert dialog.status.text != "Double-click a number to edit. All rows are validated before Apply.", "metrics dialog when bad number then error and apply disabled: unexpected result"


def test_metrics_dialog_when_no_font_then_empty_table(host):
    tool = metrics_tool(host, [])
    dialog = tool.Dialog(None)
    assert dialog.initial == [] and dialog.table.rowCount == 0, 'metrics dialog when no font then empty table: expected dialog.initial == [] and dialog.table.rowCount == 0'


def test_metrics_dialog_when_row_selected_then_diagram_repainted(host):
    tool = metrics_tool(host, [])
    metrics_package(host)
    dialog = tool.Dialog(None)
    dialog.diagram.update.reset_mock()
    dialog.table.setCurrentCell(1, 1)
    assert dialog.diagram.update.called, "Changing the current cell repaints the diagram"


class InkPainter:
    """QPainter double that records the diagram's drawing operations."""

    Antialiasing = 1
    instances: list[InkPainter] = []

    def __init__(self, *_: Any) -> None:
        InkPainter.instances.append(self)
        self.texts: list[str] = []
        self.lines = 0
        self.rects = 0
        self.ended = False

    def setRenderHint(self, flag: Any) -> None:
        pass

    def setPen(self, pen: Any) -> None:
        pass

    def fillRect(self, rect: Any, brush: Any) -> None:
        self.rects += 1

    def drawLine(self, a: Any, b: Any) -> None:
        self.lines += 1

    def drawText(self, point: Any, text: str) -> None:
        self.texts.append(text)

    def end(self) -> None:
        self.ended = True


def paint(dialog: Any, tool: Any) -> InkPainter:
    InkPainter.instances = []
    tool.QtGui.QPainter = InkPainter
    dialog.diagram.width, dialog.diagram.height = 400, 200
    dialog.diagram.paintEvent(None)
    return InkPainter.instances[0]


def test_metrics_diagram_when_painted_then_five_guides_labelled_for_current_row(host):
    tool = metrics_tool(host, [])
    metrics_package(host)
    dialog = tool.Dialog(None)
    dialog.table.selectRow(1)
    painter = paint(dialog, tool)
    assert painter.lines == 5 and painter.rects == 1, 'metrics diagram when painted then five guides labelled for current row: expected painter.lines == 5 and painter.rects == 1'
    assert "Ascender 820" in painter.texts and "Baseline 0" in painter.texts, "metrics diagram when painted then five guides labelled for current row: expected 'Ascender 820' in painter.texts and 'Baseline 0' in painter.texts"
    assert "Bold master" in painter.texts, "The diagram names the selected master"
    assert painter.ended and dialog.diagram._paint_error == "", "metrics diagram when painted then five guides labelled for current row: expected painter.ended and dialog.diagram._paint_error == ''"


def test_metrics_diagram_when_no_rows_then_nothing_drawn_but_painter_ended(host):
    tool = metrics_tool(host, [])
    dialog = tool.Dialog(None)
    painter = paint(dialog, tool)
    assert painter.texts == [] and painter.ended, 'metrics diagram when no rows then nothing drawn but painter ended: expected painter.texts == [] and painter.ended'


def test_metrics_diagram_when_table_invalid_then_error_contained_in_status(host):
    tool = metrics_tool(host, [])
    metrics_package(host)
    dialog = tool.Dialog(None)
    dialog.table.item(0, 1).setText("bad")
    painter = paint(dialog, tool)
    assert painter.ended, "The painter is ended even when the diagram fails"
    assert "ValueError" in dialog.diagram._paint_error and dialog.status.text == dialog.diagram._paint_error, "metrics diagram when table invalid then error contained in status: unexpected result"


def test_metrics_main_when_run_as_script_then_window_opens(host):
    metrics_tool(host, [])
    metrics_package(host)
    runpy.run_path(str(ROOT / "Scripts/Font Info/Master Metrics Table.py"), run_name="__main__")
    assert "fontinfo_master_metrics_table" in host.windows(), "metrics main when run as script then window opens: expected 'fontinfo_master_metrics_table' in host.windows()"


# ---- Glyph Order Preview and Export ----------------------------------------------

ORDER_PATH = FONT_INFO + "Glyph Order Preview and Export.py"
GLYPHS = [(".notdef", []), ("z", []), ("a", [97]), ("alpha", [0x3B1]), ("Ж", [0x416])]


def order_tool(host: Host, closes: list | None = None) -> Any:
    scripting = {}
    if closes is not None:
        scripting["close_script_dialog"] = lambda *a, **k: closes.append((a, k))
    return host.load(ORDER_PATH, scripting=scripting)


def order_font(host: Host, glyphs: list = GLYPHS) -> MasterPackage:
    """Open a package whose legacy font lists ``glyphs`` with their Unicodes."""
    package = open_package(host)
    by_name = {name: NS(fgGlyph=NS(unicodes=codes)) for name, codes in glyphs}
    package.findName = lambda name: by_name[name]
    host.FL.fl.font = [NS(name=name) for name, _ in glyphs]
    return package


def test_glyph_records_when_font_open_then_names_and_unicodes_in_font_order(host):
    tool = order_tool(host)
    package = order_font(host)
    assert tool.glyph_records(package) == GLYPHS, 'glyph records when font open then names and unicodes in font order: expected tool.glyph_records(package) == GLYPHS'


def test_glyph_records_when_other_font_active_then_refused(host):
    tool = order_tool(host)
    package = order_font(host)
    host.package = MasterPackage(package_id=77)
    with pytest.raises(ValueError, match="Activate the original font"):
        tool.glyph_records(package)


def test_glyph_records_when_no_font_active_then_refused(host):
    tool = order_tool(host)
    package = order_font(host)
    host.package = None
    with pytest.raises(ValueError, match="Activate the original font"):
        tool.glyph_records(package)


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("Unicode", [".notdef", "a", "alpha", "Ж", "z"]),
        ("Name", [".notdef", "a", "alpha", "z", "Ж"]),
        ("Script", [".notdef", "Ж", "alpha", "a", "z"]),
    ],
)
def test_sorted_order_when_mode_then_notdef_first_and_key_order(host, mode, expected):
    tool = order_tool(host)
    names = [name for name, _ in tool.sorted_order(GLYPHS, mode)]
    assert names == expected, f"{mode} order"


def test_run_when_records_empty_then_empty_text(host):
    tool = order_tool(host)
    assert tool.run([], "Unicode") == "", "run when records empty then empty text: expected tool.run([], 'Unicode') == ''"


def test_order_dialog_when_opened_then_preview_rows_show_old_and_new_index(host):
    tool = order_tool(host)
    order_font(host)
    dialog = tool.Dialog(None)
    assert dialog.table.rowCount == 5, 'order dialog when opened then preview rows show old and new index: expected dialog.table.rowCount == 5'
    assert dialog.table.row_texts(0) == [".notdef", "0", "0", "Unencoded"], "order dialog when opened then preview rows show old and new index: expected dialog.table.row_texts(0) == ['.notdef', '0', '0', 'Unencoded']"
    assert dialog.table.row_texts(1) == ["a", "2", "1", "Latin"], "order dialog when opened then preview rows show old and new index: expected dialog.table.row_texts(1) == ['a', '2', '1', 'Latin']"
    assert dialog.last_result["order"] == [".notdef", "a", "alpha", "Ж", "z"], "order dialog when opened then preview rows show old and new index: expected dialog.last_result['order'] == ['.notdef', 'a', 'alpha', 'Ж', 'z']"
    assert dialog.last_result["text"].startswith(".notdef\na\n"), "order dialog when opened then preview rows show old and new index: expected dialog.last_result['text'].startswith('.notdef\\na\\n')"
    assert dialog.apply_button.isEnabled() and dialog.apply_button.text == "Export order…", "order dialog when opened then preview rows show old and new index: unexpected result"


def test_order_dialog_when_sort_mode_changed_then_order_follows(host):
    tool = order_tool(host)
    order_font(host)
    dialog = tool.Dialog(None)
    dialog.mode.setCurrentIndex(1)
    assert dialog.last_result["order"] == [".notdef", "a", "alpha", "z", "Ж"], "order dialog when sort mode changed then order follows: expected dialog.last_result['order'] == ['.notdef', 'a', 'alpha', 'z', 'Ж']"
    dialog.mode.setCurrentIndex(2)
    assert dialog.last_result["order"] == [".notdef", "Ж", "alpha", "a", "z"], "order dialog when sort mode changed then order follows: expected dialog.last_result['order'] == ['.notdef', 'Ж', 'alpha', 'a', 'z']"


def test_order_dialog_when_no_font_then_apply_disabled(host):
    tool = order_tool(host)
    dialog = tool.Dialog(None)
    assert dialog.records == [] and not dialog.apply_button.isEnabled(), 'order dialog when no font then apply disabled: expected dialog.records == [] and (not dialog.apply_button.isEnabled())'


def test_order_dialog_when_empty_font_then_nothing_to_export(host):
    tool = order_tool(host)
    order_font(host, glyphs=[])
    dialog = tool.Dialog(None)
    assert not dialog.apply_button.isEnabled(), "An empty font has no order to export"


def test_order_dialog_when_apply_then_save_chooser_opened_once_and_reused(host):
    tool = order_tool(host)
    order_font(host)
    dialog = tool.Dialog(None)
    dialog.apply()
    chooser = dialog.chooser
    assert chooser.init_args[1:] == ("Export glyph order", "glyph-order.txt", "Text files (*.txt)"), "order dialog when apply then save chooser opened once and reused: unexpected result"
    chooser.setDefaultSuffix.assert_called_once_with("txt")
    chooser.open.assert_called_once_with()
    dialog.apply()
    assert dialog.chooser is chooser and chooser.open.call_count == 2, "The chooser is reused"


def test_order_dialog_when_file_selected_then_utf8_text_written_and_status_names_file(host, tmp_path):
    tool = order_tool(host)
    order_font(host)
    dialog = tool.Dialog(None)
    dialog.apply()
    target = tmp_path / "order.txt"
    dialog.chooser.fileSelected.emit(str(target))
    assert target.read_text(encoding="utf-8") == ".notdef\na\nalpha\nЖ\nz\n", "order dialog when file selected then utf8 text written and status names file: expected target.read_text(encoding='utf-8') == '.notdef\\na\\nalpha\\nЖ\\nz\\n'"
    assert dialog.status.text == "Exported 5 names to order.txt", "order dialog when file selected then utf8 text written and status names file: expected dialog.status.text == 'Exported 5 names to order.txt'"


def test_order_dialog_when_font_switched_before_export_then_nothing_written(host, tmp_path):
    tool = order_tool(host)
    order_font(host)
    dialog = tool.Dialog(None)
    host.package = MasterPackage(package_id=5)
    with pytest.raises(ValueError, match="Activate the original font"):
        dialog.export_order(tmp_path / "x.txt")
    assert not (tmp_path / "x.txt").exists(), "order dialog when font switched before export then nothing written: expected not (tmp_path / 'x.txt').exists()"


def test_order_dialog_when_closed_then_chooser_released_with_shared_cleanup(host):
    closes: list = []
    tool = order_tool(host, closes)
    order_font(host)
    dialog = tool.Dialog(None)
    dialog.apply()
    chooser = dialog.chooser
    event = object()
    dialog.closeEvent(event)
    args, kwargs = closes[0]
    assert args == (dialog, event, "fontinfo_glyph_order_tool") and kwargs == {"children": (chooser,)}, "order dialog when closed then chooser released with shared cleanup: unexpected result"
    assert dialog.chooser is None and not dialog._preview_valid, 'order dialog when closed then chooser released with shared cleanup: expected dialog.chooser is None and (not dialog._preview_valid)'


def test_order_dialog_when_closed_without_chooser_then_no_children(host):
    closes: list = []
    tool = order_tool(host, closes)
    order_font(host)
    dialog = tool.Dialog(None)
    dialog.closeEvent(object())
    assert closes[0][1] == {"children": ()}, "order dialog when closed without chooser then no children: expected closes[0][1] == {'children': ()}"


def test_order_main_when_run_as_script_then_window_opens(host):
    order_tool(host)
    order_font(host)
    runpy.run_path(str(ROOT / "Scripts" / ORDER_PATH), run_name="__main__")
    assert "fontinfo_glyph_order_tool" in host.windows(), "order main when run as script then window opens: expected 'fontinfo_glyph_order_tool' in host.windows()"
