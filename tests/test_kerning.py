# this_file: tests/test_kerning.py
"""Owned kerning fixtures verify migrated inspection tools without a native host."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TITLES = [
    "Classes Browser",
    "Compare Masters",
    "Pair List Browser",
    "Missing Pairs",
    "Text Preview",
]


@pytest.mark.parametrize("title", TITLES)
def test_requested_kerning_tool_exists(title):
    assert (ROOT / "Scripts/Kerning" / (title + ".py")).is_file(), (
        "Requested complete kerning tool missing"
    )


import importlib.util
import sys
from types import SimpleNamespace as NS


@pytest.fixture
def load(monkeypatch, app_sources):
    state = NS(package=NS(id=7, isNull=False), glyphs=[], selected={0}, clears=0)
    native = NS(
        flWorkspace=NS(instance=lambda: NS(currentPackage=state.package)),
        UpdateAll=lambda: None,
    )

    def clear():
        state.clears += 1
        state.selected.clear()

    fl = NS(
        font=state.glyphs,
        Unselect=clear,
        Select=state.selected.add,
        Selected=lambda i: i in state.selected,
    )
    qt = NS(QtCore=NS(Qt=NS(DisplayRole=0)), QtGui=NS(QDialog=object, QWidget=object))
    modules = {"fontlab": native, "PythonQt": qt, "FL": NS(fl=fl)}
    monkeypatch.setitem(sys.modules, "fontlabapp", NS(_native=modules.__getitem__))
    for name in ("scripting", "_names_dialog", "_kerning_dialog"):
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
    scripting = sys.modules["fontlabapp.scripting"]
    shared = sys.modules["fontlabapp._kerning_dialog"]
    monkeypatch.setitem(
        sys.modules, "fly", NS(ap=NS(fontlab=native, scripting=scripting), qt=qt)
    )

    monkeypatch.setitem(sys.modules, "fly.ap.scripting", scripting)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Kerning" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    return module, state, scripting, shared, qt


def fixture_font():
    """Independent explicit data and native effective resolution oracle."""
    groups = {
        "L_A": (["A", "Aacute"], "KernLeft"),
        "R_V": (["V"], "KernRight"),
        "Both": (["X"], "KernBothSide"),
    }
    explicit = {
        ("@L_A", "@R_V"): -80,
        ("A", "@R_V"): -60,
        ("@L_A", "V"): -40,
        ("A", "V"): 0,
        ("T", "V"): 12.5,
    }

    def side(name):
        return NS(
            id=name.lstrip("@"),
            mode="groupMode" if name.startswith("@") else "glyphMode",
        )

    native_pairs = [
        (NS(left=side(a), right=side(b)), value) for (a, b), value in explicit.items()
    ]
    effective = {("A", "V"): 0, ("Aacute", "V"): -40, ("V", "A"): None}
    kern = NS(
        items=lambda: native_pairs, groups=groups, get=lambda pair: effective.get(pair)
    )
    widths = {"A": 600, "V": 650, "Aacute": 600, "T": 500, "X": 550}
    glyphs = {
        name: NS(
            name=name,
            isNull=False,
            findLayer=lambda master, width=width: NS(isNull=False, advanceWidth=width),
        )
        for name, width in widths.items()
    }
    font = NS(
        id=7,
        isNull=False,
        master="Bold",
        masters=["Regular", "Bold"],
        kerning=lambda master: kern,
        findName=glyphs.get,
        findUnicode=lambda code: glyphs.get(chr(code)),
    )
    return font, kern, explicit


def test_explicit_class_sides_zero_presence_and_effective_native_fallback(load):
    _, _, api, _, _ = load
    font, kern, explicit = fixture_font()
    assert api.kerning_pairs(font, "Regular") == explicit, (
        "Explicit zero and fractional pair must survive"
    )
    left, right, members = api.kerning_class_lists(font, "Bold")
    assert left == {"A": ["@L_A"], "Aacute": ["@L_A"], "X": ["@Both"]}
    assert right == {"V": ["@R_V"], "X": ["@Both"]}
    assert members["L_A"] == ["A", "Aacute"]
    assert api.kerning_pair_value(kern, "A", "V") == 0
    assert api.kerning_pair_value(kern, "Aacute", "V") == -40
    assert api.kerning_pair_value(kern, "V", "A") == 0
    assert font.master == "Bold", "Reads must not change the active master"


def test_class_filter_and_all_master_table_distinguish_zero_from_absent(load):
    module, _, _, _, _ = load
    browser = module("Classes Browser")
    assert browser.matches("L_ALPHA", ["Aacute"], "alpha")
    assert browser.matches("L_A", ["Aacute"], "Aacute")
    assert not browser.matches("L_A", ["Aacute"], "aacute")
    compare = module("Compare Masters")
    font, _, _ = fixture_font()
    assert compare.table(font, ["Regular", "Bold"])["A", "V"] == [0, 0]
    assert compare.flags([-10, None, 40], 40) == ["sign", "missing", "jump"]
    assert compare.flags([0, 40], 40) == []
    assert compare.flags([None, 0], 0) == ["missing"]
    assert browser.pairs_using(font, ["Regular", "Bold"], "R_V")["A", "@R_V"] == {
        "Regular": -60,
        "Bold": -60,
    }


def test_missing_pair_tokens_and_zero_cover_class_fallback(load):
    module, _, _, _, _ = load
    missing = module("Missing Pairs")
    font, _, _ = fixture_font()
    assert missing.parse_glyphs(
        "@L_A AV A /invalid", font, {"L_A": ["A", "Aacute"]}
    ) == ["A", "Aacute", "V"]
    assert missing.missing(font, "Regular", ["A", "Aacute", "V"], ["V", "A"]) == [
        ("A", "A"),
        ("Aacute", "A"),
        ("V", "V"),
        ("V", "A"),
    ]
    preview = module("Text Preview")
    assert preview.parse_text("AV/Aacute/V /missing /A", font) == [
        "A",
        "V",
        "Aacute",
        "V",
        "A",
    ]
    assert preview.layout(font, ["Aacute", "V", "A", "V"], "Regular") == [
        ("Aacute", 0, 600, 0),
        ("V", 560, 650, -40),
        ("A", 1210, 600, 0),
        ("V", 1810, 650, 0),
    ]
    assert preview.layout(font, ["Aacute", "V"], "Regular", False)[1] == (
        "V",
        600,
        650,
        0,
    )


def test_numeric_table_order_exports_exact_utf8_csv_bytes(load, tmp_path):
    module, _, _, _, _ = load
    browser = module("Pair List Browser")
    assert browser.matches(("T", "V"), "=T")
    assert not browser.matches(("T.alt", "V"), "=T")
    assert browser.filtered({("T", "V"): 10, ("A", "V"): 0}, "") == [
        ("A", "V", 0),
        ("T", "V", 10),
    ]
    rows = [("A", "V", -100), ("T", "V", -9), ("é,alt", "V", 0.5)]

    def item(value):
        return NS(text=lambda: value, data=lambda role: value)

    table = NS(rowCount=3, item=lambda r, c: item(rows[r][c]))
    dialog = NS(table=table)
    shown = browser.PairList.shown_rows(dialog)
    path = tmp_path / "pairs.csv"
    assert browser.export_csv(shown, "Bold", path) == 3
    assert (
        path.read_bytes()
        == b'left,right,value,master\r\nA,V,-100,Bold\r\nT,V,-9,Bold\r\n"\xc3\xa9,alt",V,0.5,Bold\r\n'
    )


def test_native_failures_propagate_missing_layer_does_not_partially_succeed(load):
    _, _, api, _, _ = load
    font, kern, _ = fixture_font()
    kern.get = lambda pair: (_ for _ in ()).throw(RuntimeError("broken native read"))
    with pytest.raises(RuntimeError, match="broken native"):
        api.kerning_layout(font, ["A", "V"], "Regular")
    with pytest.raises(ValueError, match="Missing glyph"):
        api.kerning_layout(font, ["A", "missing"], "Regular", False)


def test_shared_selection_refuses_switched_font_and_missing_names_before_clear(load):
    _, state, _, shared, _ = load
    dialog = shared.KerningDialog.__new__(shared.KerningDialog)
    dialog._snapshot_valid, dialog._scanned_id = True, 7
    dialog.paths, dialog.pairs = {}, {}
    state.glyphs.extend([NS(name="A"), NS(name="V")])
    with pytest.raises(ValueError, match="Unknown glyph"):
        dialog.select_names(["missing"])
    assert state.clears == 0 and state.selected == {0}
    dialog._snapshot_valid, dialog._scanned_id = True, 7
    state.package = NS(id=8, isNull=False)
    with pytest.raises(ValueError, match="stale"):
        dialog.select_names(["V"])
    assert state.clears == 0 and state.selected == {0}


def test_failed_refresh_clears_rows_proof_and_disables_actions(load):
    _, state, _, shared, _ = load
    calls = []
    dialog = shared.KerningDialog.__new__(shared.KerningDialog)
    dialog.package = state.package
    dialog.rows = [("partial", 1)]
    dialog.paths = {"partial": "outline"}
    dialog.export_button = NS(setEnabled=lambda value: calls.append(value))

    @shared.snapshot_refresh
    def broken(self):
        self.rows.append(("more", 2))
        raise RuntimeError("native failed")

    with pytest.raises(RuntimeError, match="native failed"):
        broken(dialog)
    assert dialog.rows == [] and dialog.paths == {} and calls == [False]
    assert not dialog._snapshot_valid


def test_proof_geometry_fits_tall_overhanging_wrapped_ink_and_all_rows(load):
    _, _, api, _, _ = load
    rows = [("A", 0, 600, 0), ("V", 500, 650, -100), ("A", 1150, 600, 0)]
    bounds = {"A": (-220, -350, 850, 1600), "V": (-100, -200, 900, 800)}
    scale, positions = api.kerning_proof_geometry(
        rows, bounds, 180, 130, 0.24, 800, -200, True
    )
    assert len(positions) == 3 and scale < 0.24, (
        "Overflow must fit rather than omit glyphs"
    )
    for name, x, baseline, kern in positions:
        left, bottom, right, top = bounds[name]
        assert x + left * scale >= 0 and x + right * scale <= 180
        assert baseline - top * scale >= 0 and baseline - bottom * scale <= 130


def test_canvas_contains_draw_and_error_hook_and_painter_end_exceptions(load):
    module, _, _, _, qt = load
    preview = module("Text Preview")
    calls = []
    painter = NS(end=lambda: calls.append("ended"))
    qt.QtGui.QPainter = lambda owner: painter
    canvas = preview.Canvas.__new__(preview.Canvas)
    canvas.owner = NS(invalidate=lambda: (_ for _ in ()).throw(RuntimeError("hook")))
    canvas.draw = lambda painter: (_ for _ in ()).throw(RuntimeError("draw"))
    canvas.paintEvent(None)
    assert canvas.paint_error == "RuntimeError('draw')" and calls == ["ended"]
    painter.end = lambda: (_ for _ in ()).throw(RuntimeError("end"))
    canvas.paintEvent(None)
    assert canvas.paint_error == "RuntimeError('end')"


def test_all_classes_reuse_exact_shared_callbacks_and_lifecycle(load):
    module, _, _, shared, _ = load
    for title, name in zip(
        TITLES,
        ["ClassesBrowser", "CompareMasters", "PairList", "MissingPairs", "TextPreview"],
    ):
        cls = getattr(module(title), name)
        assert cls._connect is shared.KerningDialog._connect
        assert cls.closeEvent is shared.KerningDialog.closeEvent


def test_stale_export_and_copy_refuse_before_writing_or_clipboard(load, tmp_path):
    module, _, _, _, _ = load

    def stale():
        raise ValueError("stale")

    target = tmp_path / "must-not-exist.csv"
    dialog = NS(ensure_snapshot=stale)
    with pytest.raises(ValueError, match="stale"):
        module("Pair List Browser").PairList.export(dialog, str(target))
    with pytest.raises(ValueError, match="stale"):
        module("Missing Pairs").MissingPairs.copy(dialog)
    assert not target.exists(), "A stale export must never create its destination"


def test_copy_keeps_actual_pair_order_and_reports_count(load):
    module, _, _, _, qt = load
    copied = []
    qt.QtGui.QApplication = NS(clipboard=lambda: NS(setText=copied.append))
    dialog = NS(
        ensure_snapshot=lambda: None,
        missing=[("Aacute", "V"), ("T", "o")],
        status=NS(setText=copied.append),
    )
    assert module("Missing Pairs").MissingPairs.copy(dialog) == "Aacute V\nT o"
    assert copied == ["Aacute V\nT o", "Copied 2 pairs to the clipboard"]


def test_owned_chooser_disconnects_before_child_deletion_and_dialog_deletion(
    load, monkeypatch
):
    _, _, _api, shared, qt = load
    calls = []
    qt.QtGui.QDialog = NS(closeEvent=lambda d, e: calls.append("native-close"))
    signal = NS(disconnect=lambda slot: calls.append(("disconnect", slot)))
    child = NS(
        close=lambda: calls.append("child-close"),
        deleteLater=lambda: calls.append("child-delete"),
    )
    dialog = NS(
        _connections=[(signal, "exact-wrapper")],
        _key="owned",
        file_dialog=child,
        deleteLater=lambda: calls.append("dialog-delete"),
    )
    windows = {"owned": dialog}
    monkeypatch.setattr(sys, "_fontlab_samples", windows, raising=False)
    shared.KerningDialog.closeEvent(dialog, None)
    assert calls == [
        ("disconnect", "exact-wrapper"),
        "child-close",
        "child-delete",
        "native-close",
        "dialog-delete",
    ]
    assert windows == {} and dialog._connections == []


def test_overflow_proof_never_discards_rows_even_with_many_wrapped_lines(load):
    _, _, api, _, _ = load
    rows = [("A", i * 600, 600, 0) for i in range(200)]
    bounds = {"A": (-200, -300, 900, 1900)}
    scale, positions = api.kerning_proof_geometry(
        rows, bounds, 160, 100, 0.2, 800, -200, True
    )
    assert len(positions) == 200
    for _, x, y, _ in positions:
        assert x - 200 * scale >= 0 and x + 900 * scale <= 160
        assert y - 1900 * scale >= 0 and y + 300 * scale <= 100
