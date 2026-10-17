# this_file: tests/test_names.py
"""Verify complete Names tools, calculations and selection safety without FontLab."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TITLES = [
    "Case Pairs",
    "Character Info",
    "Character Set Compare",
    "Glyph Finder",
    "Select by Mark",
]


@pytest.mark.parametrize("title", TITLES)
def test_requested_names_tool_exists(title):
    assert (ROOT / "Scripts/Names" / (title + ".py")).is_file(), (
        "Requested Names tool missing"
    )


import importlib.util
import sys
from types import SimpleNamespace as NS


@pytest.fixture
def load(monkeypatch, app_sources):
    assert (app_sources / "_names_dialog.py").is_file(), (
        "Current Names helper required; set SCRIPTMIX_APP_SOURCE or install the updated App wheel"
    )
    state = NS(package=NS(id=7), glyphs=[], selected=set(), clears=0)
    native = NS(
        CurrentFont=lambda: NS(glyphs=state.glyphs),
        flWorkspace=NS(instance=lambda: NS(currentPackage=state.package)),
        UpdateAll=lambda: None,
    )

    class Font:
        def __len__(self):
            return len(state.glyphs)

        def __getitem__(self, i):
            return state.glyphs[i]

    def clear():
        state.clears += 1
        state.selected.clear()

    fl = NS(
        font=Font(),
        Unselect=clear,
        Select=lambda i: state.selected.add(i),
        Selected=lambda i: i in state.selected,
    )
    qt = NS(QtCore=NS(), QtGui=NS(QDialog=object, QWidget=object))
    modules = {"fontlab": native, "PythonQt": qt, "FL": NS(fl=fl)}
    monkeypatch.setitem(sys.modules, "fontlabapp", NS(_native=modules.__getitem__))
    for name in ("scripting", "_names_dialog"):
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
    scripting = sys.modules["fontlabapp.scripting"]
    shared = sys.modules["fontlabapp._names_dialog"]
    monkeypatch.setitem(sys.modules, "fly", NS(ap=NS(fontlab=native), qt=qt))
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", scripting)
    for name, value in modules.items():
        monkeypatch.setitem(sys.modules, name, value)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Names" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    return module, state, scripting, shared


def test_case_counterparts_use_unicode_first_suffix_fallback_and_single_character(load):
    module, _, _, _ = load
    case = module("Case Pairs")
    codes, by_code = case.index(
        [
            ("A", [65]),
            ("a", [97]),
            ("a.alt", []),
            ("A.alt", []),
            ("duplicate", [97]),
            ("sharp", [223]),
            ("one", [49]),
        ]
    )
    assert case.counterpart("A", codes, by_code)[0] == "a"
    assert case.counterpart("a.alt", codes, by_code) == ("A.alt", "via a → A")
    assert case.counterpart("sharp", codes, by_code) == (None, "no case")
    assert case.counterpart("one", codes, by_code)[0] is None
    assert case.counterpart("unknown", codes, by_code) == (None, "unencoded")


def test_unicode_description_non_bmp_encodings_decomposition_and_case(load):
    module, _, _, _ = load
    info = module("Character Info")
    assert info.describe(0x1F600)["UTF-16"] == "D83D DE00"
    assert info.describe(0x1F600)["UTF-8"] == "F0 9F 98 80"
    assert info.describe(0x1F600)["Escape"] == "\\U0001f600"
    assert info.describe(0xE9)["Decomposition"] == "0065 0301"
    assert info.describe(223)["Case pair"] == "S U+0053 S U+0053"
    assert info.describe(0x378)["Unicode name"] == "(no name)"


@pytest.mark.parametrize(
    "query,expected",
    [
        ("U+00E9", ["eacute"]),
        ("0x00E9", ["eacute"]),
        ("uni00E9", ["eacute"]),
        ("é", ["eacute"]),
        ("*.ss0?", ["A.ss01"]),
        ("?acute", ["eacute"]),
        ("ACUTE", ["eacute"]),
        ("", ["A", "eacute", "A.ss01"]),
        ("missing", []),
    ],
)
def test_finder_queries_match_actual_names_and_codes(load, query, expected):
    module, _, _, _ = load
    assert [
        name
        for name, _ in module("Glyph Finder").find(
            [("A", [65]), ("eacute", [233]), ("A.ss01", [])], query
        )[1]
    ] == expected


def test_charset_set_difference_and_presets_preserve_language_data(load):
    module, _, _, _ = load
    charset = module("Character Set Compare")
    assert charset.compare("éé A\n\tŻ", {"A": "A", "B": "B", " ": "space"}) == (
        ["é", "Ż"],
        ["B"],
    )
    assert charset.compare("", {}) == ([], [])
    assert "Ł" in dict(charset.PRESETS)["Polish"]
    assert "ı" in dict(charset.PRESETS)["Turkish"]
    assert len(dict(charset.PRESETS)["Basic Latin (ASCII)"]) == 94


def test_mark_group_order_and_labels(load):
    module, _, _, _ = load
    marks = module("Select by Mark")
    assert marks.groups([("a", 0), ("b", 113), ("c", 113), ("d", 1005), ("e", 1)]) == [
        (1, ["e"]),
        (113, ["b", "c"]),
        (1005, ["d"]),
        (0, ["a"]),
    ]
    assert marks.mark_label(0) == "Unmarked"
    assert marks.mark_label(1) == "Red (hue 0°)"
    assert marks.mark_label(1005) == "Grey 5"


def test_actual_selection_validates_all_names_and_identity_before_clearing(load):
    _, state, scripting, _ = load
    state.package.isNull = False
    state.glyphs = [NS(name=n) for n in ("A", "a", "b")]
    state.selected = {2}
    assert scripting.select_glyphs(["a"], package_id=7, add=True) == ["a", "b"]
    assert state.clears == 1
    with pytest.raises(ValueError, match="Unknown"):
        scripting.select_glyphs(["missing"], package_id=7)
    assert state.selected == {1, 2} and state.clears == 1
    state.package.id = 8
    with pytest.raises(ValueError, match="no longer current"):
        scripting.select_glyphs(["A"], package_id=7)
    assert state.clears == 1


def panel(shared, dialog=None):
    dialog = dialog if dialog is not None else object.__new__(shared.NamesDialog)
    dialog._snapshot_valid = True
    dialog._scanned_id = 7
    dialog._connections = []
    dialog.last_result = {"old": True}
    dialog.pairs = [("old", "other", "")]
    dialog.matches = [("old", [])]
    dialog.groups = [(113, ["old"])]
    dialog.missing = ["x"]
    dialog.extra = ["y"]
    dialog.select_button = NS(
        setEnabled=lambda value: setattr(dialog, "enabled", value)
    )
    dialog.table = NS(setRowCount=lambda value: setattr(dialog, "row_count", value))
    return dialog


def test_failed_render_clears_partial_rows_and_refuses_direct_selection(load):
    _, state, _, shared = load
    state.package.isNull = False
    dialog = panel(shared)

    @shared.snapshot_refresh
    def broken(self):
        self.matches = [("partial", [])]
        self.table.setRowCount(1)
        raise RuntimeError("table failed")

    with pytest.raises(RuntimeError, match="table failed"):
        broken(dialog)
    assert dialog.matches == [] and dialog.pairs == [] and dialog.groups == []
    assert (
        dialog.row_count == 0 and dialog.enabled is False and dialog.last_result is None
    )
    with pytest.raises(ValueError, match="stale"):
        dialog.select_names(["A"])
    assert state.clears == 0


@pytest.mark.parametrize("kind", ["switched", "closed"])
def test_stale_panel_refuses_actual_selection_and_clears_actions(load, kind):
    _, state, _, shared = load
    state.package.isNull = False
    dialog = panel(shared)
    state.package = NS(id=8, isNull=False) if kind == "switched" else None
    with pytest.raises(ValueError, match="stale"):
        dialog.select_names(["A"])
    assert not dialog._snapshot_valid and dialog.matches == [] and state.clears == 0


def test_complete_scan_publishes_only_original_font_identity(load):
    _, state, _, shared = load
    state.package.isNull = False
    dialog = panel(shared)

    @shared.snapshot_refresh
    def scan(self):
        self.matches = [("A", [65])]

    scan(dialog)
    assert dialog._snapshot_valid and dialog._scanned_id == 7

    @shared.snapshot_refresh
    def switched(self):
        self.matches = [("A", [65])]
        state.package = NS(id=8, isNull=False)

    with pytest.raises(ValueError, match="during refresh"):
        switched(dialog)
    assert dialog.matches == [] and not dialog._snapshot_valid


def test_original_actions_pass_exact_names_keep_and_add(load):
    module, _state, _, _ = load
    case = object.__new__(module("Case Pairs").CasePairs)
    case.ensure_snapshot = lambda: None
    case.pairs = [("A", "a", ""), ("one", None, "")]
    case.selection = ["A", "one"]
    case.keep = NS(isChecked=lambda: True)
    calls = []
    case.select_names = lambda names: calls.append(names) or names
    case.status = NS(setText=lambda value: None)
    case.select_counterparts()
    assert calls == [["a", "A", "one"]]
    mark = object.__new__(module("Select by Mark").SelectByMark)
    mark.ensure_snapshot = lambda: None
    mark.groups = [(113, ["b", "c"]), (0, ["a"])]
    mark.add = NS(isChecked=lambda: True)
    mark.status = case.status
    mark.select_names = lambda names, **kw: calls.append((names, kw)) or names
    mark.select_rows([0])
    assert calls[-1] == (["b", "c"], {"add": True})


def test_specimen_ends_painter_and_contains_failing_error_hook(load, monkeypatch):
    module, _, _, _ = load
    info = module("Character Info")
    ended = []
    monkeypatch.setattr(
        info.QtGui,
        "QPainter",
        lambda widget: NS(end=lambda: ended.append(True)),
        raising=False,
    )
    specimen = object.__new__(info.Specimen)

    def fail(*args):
        raise RuntimeError("paint failed")

    specimen.draw = fail
    specimen.on_error = fail
    specimen.paintEvent(None)
    assert ended == [True] and "paint failed" in specimen.paint_error


def test_poll_always_refreshes_same_name_after_font_or_master_changes(load):
    module, _, _, _ = load
    info = module("Character Info")
    dialog = object.__new__(info.CharacterInfo)
    calls = []
    dialog.refresh = lambda: calls.append(True)
    dialog.poll()
    assert calls == [True]


def test_shared_close_stops_timer_disconnects_and_defers_delete(load, monkeypatch):
    _, _, _scripting, shared = load
    calls = []
    dialog = panel(shared)
    dialog._key = "owned"
    dialog.timer = NS(stop=lambda: calls.append("stop"))
    signal = NS(disconnect=lambda slot: calls.append("disconnect"))
    dialog._connections = [(signal, object())]
    dialog.deleteLater = lambda: calls.append("delete")
    monkeypatch.setattr(
        shared.QtGui, "QDialog", NS(closeEvent=lambda *args: calls.append("close"))
    )
    monkeypatch.setattr(sys, "_fontlab_samples", {"owned": dialog}, raising=False)
    shared.NamesDialog.closeEvent(dialog, None)
    assert calls == ["stop", "disconnect", "close", "delete"]
    assert not dialog._connections and "owned" not in sys._fontlab_samples


@pytest.mark.parametrize(
    "title,cls,method,reader",
    [
        ("Case Pairs", "CasePairs", "reload", "font_glyphs"),
        ("Character Info", "CharacterInfo", "refresh", "current_package"),
        ("Character Set Compare", "CharsetCompare", "refresh", "font_chars"),
        ("Glyph Finder", "Finder", "refresh", "font_glyphs"),
        ("Select by Mark", "SelectByMark", "reload", "font_marks"),
    ],
)
def test_actual_failed_refresh_invalidates_prior_selection(
    load, monkeypatch, title, cls, method, reader
):
    module, state, _, shared = load
    state.package.isNull = False
    tool = module(title)
    dialog = object.__new__(getattr(tool, cls))
    panel(shared, dialog)

    def fail():
        raise RuntimeError("scan failure")

    monkeypatch.setattr(tool, reader, fail)
    with pytest.raises(RuntimeError, match="scan failure"):
        getattr(dialog, method)()
    assert not dialog._snapshot_valid and dialog.matches == []
    assert dialog.row_count == 0 and dialog.enabled is False
    with pytest.raises(ValueError, match="stale"):
        dialog.select_names(["A"])
    assert state.clears == 0


def test_outline_path_contains_transformed_closed_and_open_parts(load, monkeypatch):
    module, _, _, _ = load
    info = module("Character Info")
    paths = []

    class Path:
        def setFillRule(self, value):
            pass

        def addPath(self, value):
            paths.append(value)

    monkeypatch.setattr(info.QtGui, "QPainterPath", Path, raising=False)
    monkeypatch.setattr(info.QtCore, "Qt", NS(WindingFill=1), raising=False)
    closed = NS(isEmpty=lambda: False)
    opened = NS(isEmpty=lambda: False)
    shape = NS(
        closedPath=closed,
        openedPath=opened,
        transform=NS(map=lambda part: ("transformed", part)),
    )
    info.layer_path(NS(shapes=[shape]))
    assert paths == [("transformed", closed), ("transformed", opened)]


def test_finder_rows_and_charset_extra_use_actual_names(load):
    module, _, _, _ = load
    finder = object.__new__(module("Glyph Finder").Finder)
    finder.ensure_snapshot = lambda: None
    finder.matches = [("A", [65]), ("eacute", [233]), ("a.alt", [])]
    finder.table = NS(
        selectionModel=lambda: NS(selectedRows=lambda: [NS(row=lambda: 2)])
    )
    calls = []
    finder.select_names = lambda names: calls.append(names) or names
    finder.status = NS(setText=lambda text: None)
    finder.select_matches()
    finder.select_row(1)
    assert calls == [["a.alt"], ["eacute"]]
    compare = object.__new__(module("Character Set Compare").CharsetCompare)
    compare.ensure_snapshot = lambda: None
    compare.available = {"A": "A", "é": "eacute"}
    compare.extra = ["é"]
    compare.select_names = finder.select_names
    compare.status = finder.status
    compare.select_extra()
    assert calls[-1] == ["eacute"]


def test_copy_actions_use_validated_snapshot_and_actual_unicode(load, monkeypatch):
    module, _, _, _ = load
    info = module("Character Info")
    copies = []
    monkeypatch.setattr(
        info.QtGui,
        "QApplication",
        NS(clipboard=lambda: NS(setText=copies.append)),
        raising=False,
    )
    dialog = object.__new__(info.CharacterInfo)
    validated = []
    dialog.ensure_snapshot = lambda: validated.append(True)
    dialog.specimen = NS(char="é")
    dialog.status = NS(setText=lambda text: None)
    dialog.copy()
    charset = module("Character Set Compare")
    other = object.__new__(charset.CharsetCompare)
    other.ensure_snapshot = dialog.ensure_snapshot
    other.missing = ["Ł", "Ż"]
    other.status = dialog.status
    other.copy_missing()
    assert copies == ["é", "ŁŻ"] and validated == [True, True]


@pytest.mark.parametrize("bounds", [(0, -200, 600, 1500), (-900, -250, 2000, 750)])
def test_specimen_draw_fits_tall_accents_and_side_overhang_inside_proof(
    load, monkeypatch, bounds
):
    module, _, _, _ = load
    info = module("Character Info")

    class Style:
        def __init__(self, *args):
            pass

        def setAlpha(self, value):
            pass

        def pointSizeF(self):
            return 10

        def setPointSizeF(self, value):
            pass

        def setPixelSize(self, value):
            pass

    for name in ("QColor", "QPen", "QBrush", "QFont"):
        monkeypatch.setattr(info.QtGui, name, Style, raising=False)
    monkeypatch.setattr(info.QtGui, "QPalette", NS(Text=1), raising=False)
    monkeypatch.setattr(info.QtGui, "QPainter", NS(Antialiasing=1), raising=False)
    monkeypatch.setattr(
        info.QtCore, "Qt", NS(AlignLeft=1, AlignCenter=2), raising=False
    )
    monkeypatch.setattr(info.QtCore, "QRectF", lambda *args: args, raising=False)
    monkeypatch.setattr(info.QtCore, "QPointF", lambda *args: args, raising=False)
    specimen = object.__new__(info.Specimen)
    specimen.width, specimen.height = 500, 150
    specimen.palette = NS(color=lambda role: None)
    specimen.advance, specimen.char, specimen.frame = 600, "W", (-250, 750)
    left, low, right, high = bounds
    rect = NS(
        left=lambda: left, right=lambda: right, top=lambda: low, bottom=lambda: high
    )
    specimen.path = NS(boundingRect=lambda: rect)
    transforms, lines, labels = {}, [], []
    noop = lambda *args: None
    painter = NS(
        setRenderHint=noop,
        setPen=noop,
        drawRoundedRect=noop,
        font=lambda: Style(),
        setFont=noop,
        drawText=lambda rect, alignment, text: labels.append(text),
        drawLine=lambda start, end: lines.append((start, end)),
        save=noop,
        restore=noop,
        fillPath=noop,
        translate=lambda x, y: transforms.update(x=x, y=y),
        scale=lambda x, y: transforms.update(sx=x, sy=y),
    )
    specimen.draw(painter)
    xs = [transforms["x"] + x * transforms["sx"] for x in (left, right)]
    ys = [transforms["y"] + y * transforms["sy"] for y in (low, high)]
    assert min(xs) >= 8 - 1e-8 and max(xs) <= 236 + 1e-8, (
        "Side overhang must stay inside padded left proof"
    )
    assert min(ys) >= 8 - 1e-8 and max(ys) <= 120 + 1e-8, (
        "Full accent must fit above labels with padding"
    )
    assert transforms["sx"] == -transforms["sy"] > 0, (
        "Keep outline aspect and font y direction"
    )
    assert 8 <= lines[0][0][1] <= 120, "Keep baseline inside proof frame"
    assert labels == ["Font outline", "System font", "W"], (
        "Keep both proof labels and system character"
    )


def test_mark_selection_reader_has_no_current_glyph_fallback(load):
    module, state, _, _ = load
    state.glyphs = [NS(name="A")]
    state.selected = set()
    assert module("Select by Mark").font_window_selection() == []
    state.selected = {0}
    assert module("Select by Mark").font_window_selection() == ["A"]
