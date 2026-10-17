# this_file: tests/test_font_info.py
"""Owned tests for complete Font Info migrations and safe edit plans."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).parents[1]
TITLES = [
    "Glyph Order Preview and Export",
    "Master Metrics Table",
    "Names and Credits",
    "Unicode Ranges and Codepages",
    "Bump Font Version",
    "Calculate Vertical Metrics",
]


@pytest.mark.parametrize("title", TITLES)
def test_requested_tool_exists(title):
    assert (ROOT / "Scripts/Font Info" / (title + ".py")).is_file(), (
        "Complete requested Font Info tool missing"
    )


@pytest.fixture
def load(monkeypatch):
    state = NS(package=None)
    native = NS()
    helpers = NS(
        current_package=lambda: state.package,
        write_font_info=lambda *a, **k: None,
        connect_guarded=lambda *a: None,
        close_script_dialog=lambda *a, **k: None,
        show_script_dialog=lambda *a: None,
    )
    monkeypatch.setitem(
        sys.modules,
        "fly",
        NS(
            ap=NS(fontlab=native, FL=NS()),
            qt=NS(QtCore=NS(), QtGui=NS(QDialog=object, QWidget=object)),
        ),
    )
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", helpers)
    # Exercise the actual shared panel methods against owned import doubles.
    shared_path = (
        ROOT.parent / ".worktrees/issue111-app/src/fontlabapp/_font_info_dialog.py"
    )
    qt = sys.modules["fly"].qt
    monkeypatch.setitem(sys.modules, "fontlabapp", NS(_native=lambda name: qt))
    monkeypatch.setitem(sys.modules, "fontlabapp.scripting", helpers)
    spec = importlib.util.spec_from_file_location(
        "fontlabapp._font_info_dialog", shared_path
    )
    shared = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shared)
    helpers.font_info_dialog_type = lambda: shared.FontInfoDialog

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Font Info" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    return module, state, native


def test_calculations_and_real_export(load, tmp_path):
    module, state, _ = load
    order = module(TITLES[0])
    records = [("z", []), ("a", [97]), (".notdef", []), ("A", [65])]
    assert order.run(records, "Unicode") == ".notdef\nA\na\nz\n"
    assert order.script_group([0x410]) == "Cyrillic"
    assert order.script_group([]) == "Unencoded"
    assert order.script_group([-1]) == "Unknown"
    dialog = object.__new__(order.Dialog)
    state.package = NS(id=1)
    dialog.package = state.package
    dialog.package_id = 1
    dialog.preview_master = "Regular"
    dialog._preview_valid = True
    dialog.refresh = lambda: None
    dialog.records = records
    dialog.last_result = {"text": order.run(records, "Name")}
    statuses = []
    dialog.status = NS(setText=statuses.append)
    path = tmp_path / "order.txt"
    dialog.export_order(path)
    assert path.read_text() == ".notdef\nA\na\nz\n"
    assert statuses == ["Exported 4 names to order.txt"], (
        "Export status should retain the count and filename without the long directory path"
    )
    unicode = module(TITLES[3])
    bits, rows = unicode.run([("A", [65, 0x10400, -1, 0x110000])])
    assert 0 in bits and 57 in bits
    assert any(row[3] == "Multibyte: review manually" for row in rows)
    version = module(TITLES[4])
    assert version.bumped(1, 999, "minor") == (2, 0)
    assert version.bumped(1, 42, "major") == (2, 0)
    for args in [(65535, 999, "minor"), (-1, 0, "major"), (1, 0, "invalid")]:
        with pytest.raises(ValueError):
            version.bumped(*args)
    metrics = module(TITLES[5])
    assert metrics.enclosing_metrics(-200.2, 700.2, 10, 5) == [
        711,
        -211,
        5,
        711,
        -211,
        5,
        711,
        211,
    ]
    for values in [
        (0, float("nan"), 0, 0),
        (0, 40000, 0, 0),
        (0, 1, -1, 0),
        (0, 1, 0, 32768),
    ]:
        with pytest.raises(ValueError):
            metrics.enclosing_metrics(*values)


def test_export_chooser_when_reopened_then_reuses_owned_dialog_and_checks_font(
    load, tmp_path
):
    module, state, _ = load
    tool = module(TITLES[0])
    dialog, _ = bare_dialog(tool, state)
    dialog._preview_valid = True
    dialog.chooser = None
    dialog.refresh = lambda: None
    selected = []
    opened = []

    class Chooser:
        AcceptSave = 1

        def __init__(self, parent, *args):
            self.fileSelected = object()
            self.parent = parent

        def setAcceptMode(self, mode):
            assert mode == self.AcceptSave

        def setDefaultSuffix(self, suffix):
            assert suffix == "txt"

        def open(self):
            opened.append(self)

    tool.QtGui.QFileDialog = Chooser
    dialog._connect = lambda signal, slot: selected.append(slot)
    exports = []
    dialog.export_order = exports.append
    dialog.apply()
    dialog.apply()
    assert len(selected) == 1 and opened == [dialog.chooser, dialog.chooser]
    assert dialog.chooser.parent is dialog
    selected[0](str(tmp_path / "order.txt"))
    assert exports == [str(tmp_path / "order.txt")]


@pytest.mark.parametrize("title", TITLES)
def test_failed_preview_and_stale_font_refuse_apply(load, title):
    module, state, _ = load
    tool = module(title)
    dialog = object.__new__(tool.Dialog)
    dialog.package_id = 1
    dialog.package = NS(id=1, master="Regular")
    dialog.preview_master = "Regular"
    dialog._preview_valid = False
    dialog.apply_button = NS(setEnabled=lambda value: None)
    dialog.status = NS(setText=lambda value: None)
    for package in [None, NS(id=2, master="Regular"), dialog.package]:
        state.package = package
        with pytest.raises(ValueError):
            dialog.apply()
    dialog.safe(lambda: (_ for _ in ()).throw(ValueError("failed preview")))
    assert not dialog._preview_valid


def test_names_and_metrics_validate_entire_input(load):
    module, _, _ = load
    names = module(TITLES[2])
    valid = {
        "familyName": "Family",
        "styleName": "Regular",
        "openTypeNameDesigner": "",
        "copyright": "",
        "openTypeNameVersion": "Version 1.002",
    }
    assert names.validate_names(valid) == valid
    for field, value in [
        ("familyName", " "),
        ("copyright", "bad\n"),
        ("openTypeNameVersion", "1.2"),
    ]:
        with pytest.raises(ValueError):
            names.validate_names({**valid, field: value})
    metrics = module(TITLES[1])
    assert metrics.validate_metrics([800, -200, 500, 700]) == [800, -200, 500, 700]
    for values in [[], [800, -200, 900, 700], [float("inf"), -200, 500, 700]]:
        with pytest.raises(ValueError):
            metrics.validate_metrics(values)


def metric_package():
    """Own separate master dictionaries and a dynamic native-info-like view."""
    values = {
        "Regular": {
            "ascender": 800,
            "descender": -200,
            "xHeight": 500,
            "capHeight": 700,
            "note": "regular note",
        },
        "Bold": {
            "ascender": 900,
            "descender": -250,
            "xHeight": 550,
            "capHeight": 750,
            "note": "bold note",
        },
    }
    package = NS(
        id=1, master="Bold", masters=list(values), versionMajor=1, versionMinor=999
    )
    for row in values.values():
        row.update(
            versionMajor=1, versionMinor=999, openTypeNameVersion="Version 1.999"
        )
        row.update(
            {
                field: 0
                for field in [
                    "openTypeOS2TypoAscender",
                    "openTypeOS2TypoDescender",
                    "openTypeOS2TypoLineGap",
                    "openTypeHheaAscender",
                    "openTypeHheaDescender",
                    "openTypeHheaLineGap",
                    "openTypeOS2WinAscent",
                    "openTypeOS2WinDescent",
                ]
            }
        )

    class Info:
        def __getattr__(self, field):
            return values[package.master][field]

    package.info = Info()
    package.setMaster = lambda master: setattr(package, "master", master)
    return package, values


def bare_dialog(tool, state):
    """Build only the owned UI state needed to exercise real dialog methods."""
    dialog = object.__new__(tool.Dialog)
    package, values = metric_package()
    state.package = package
    dialog.package = package
    dialog.package_id = package.id
    dialog.preview_master = package.master
    dialog._preview_valid = False
    dialog._plan = []
    dialog.apply_button = NS(setEnabled=lambda flag: setattr(dialog, "enabled", flag))
    dialog.status = NS(setText=lambda text: setattr(dialog, "message", text))
    dialog.rows = lambda headings, rows: setattr(dialog, "display", rows)
    return dialog, values


def test_master_reads_plans_and_failures_restore_current_master(load):
    module, _state, _ = load
    metrics = module(TITLES[1])
    package, _values = metric_package()
    rows = metrics.master_values(package)
    assert rows == [("Regular", [800, -200, 500, 700]), ("Bold", [900, -250, 550, 750])]
    assert package.master == "Bold"
    version = module(TITLES[4])
    plan = version.version_plan(package, "minor", True, "2026-01-01")
    assert package.master == "Bold"
    assert plan[-2:] == [
        ("Regular", "note", "regular note", "regular note\n2026-01-01: Version 2.000"),
        ("Bold", "note", "bold note", "bold note\n2026-01-01: Version 2.000"),
    ]
    vertical = module(TITLES[5])
    plan = vertical.metric_plan(
        package,
        {"Regular": (-200.2, 700.2, 10)},
        ["Regular", "Bold"],
        10,
        5,
        vertical.METRIC_FIELDS[3:],
    )
    assert len(plan) == 5 and all(row[0] == "Regular" for row in plan)
    assert package.master == "Bold"
    with pytest.raises(ValueError):
        vertical.metric_plan(package, {"Regular": (-40000, 700, 10)}, ["Regular"], 0, 0)
    assert package.master == "Bold"


def test_master_ui_preview_validation_and_noop(load):
    module, state, _ = load
    tool = module(TITLES[1])
    dialog, _values = bare_dialog(tool, state)
    dialog.edited_rows = lambda: [
        ("Regular", [800, -200, 500, 700]),
        ("Bold", [900, -250, 550, 750]),
    ]
    dialog.diagram = NS(update=lambda: None)
    dialog.refresh()
    assert dialog._preview_valid and not dialog.enabled
    dialog.edited_rows = lambda: [
        ("Regular", [810, -200, 500, 700]),
        ("Bold", [900, -250, 550, 750]),
    ]
    dialog.refresh()
    assert dialog.enabled and dialog._plan[0] == ("Regular", "ascender", 800, 810)

    def failed_display(*args):
        raise RuntimeError("owned diagram failed")

    dialog.diagram.update = failed_display
    with pytest.raises(RuntimeError):
        dialog.refresh()
    assert not dialog._preview_valid
    with pytest.raises(ValueError):
        dialog.apply()


def test_version_apply_consumes_preview_instead_of_recomputing(load):
    module, state, _ = load
    tool = module(TITLES[4])
    dialog, _ = bare_dialog(tool, state)
    dialog.changes = lambda: [("Regular", "note", "regular note", "new note")]
    dialog.refresh()
    assert dialog._preview_valid and dialog.enabled
    captured = []
    tool.write_changes = lambda package, plan: captured.append(plan) or {"changed": 1}
    dialog.changes = lambda: [("Regular", "note", "external", "unpreviewed")]
    dialog.apply()
    assert captured == [[("Regular", "note", "regular note", "new note")]]


@pytest.mark.parametrize("title", [TITLES[2], TITLES[5]])
def test_current_master_switch_refuses_preview_apply(load, title):
    module, state, _ = load
    tool = module(title)
    dialog, _ = bare_dialog(tool, state)
    dialog._preview_valid = True
    state.package.master = "Regular"
    with pytest.raises(ValueError, match="Master changed"):
        dialog.apply()
    assert not dialog._preview_valid


def test_unicode_refresh_rereads_encodings_and_display_failure_invalidates(load):
    module, state, _ = load
    tool = module(TITLES[3])
    dialog, _ = bare_dialog(tool, state)
    tool.glyph_records = lambda package: [("A", [65])]
    dialog.refresh()
    assert dialog.last_result["bits"] == [0] and dialog._preview_valid
    tool.glyph_records = lambda package: [("Smile", [0x1F600])]
    dialog.apply()
    assert 57 in dialog.last_result["bits"] and 0 not in dialog.last_result["bits"]
    dialog.rows = lambda *args: (_ for _ in ()).throw(
        RuntimeError("owned display failed")
    )
    with pytest.raises(RuntimeError):
        dialog.refresh()
    assert not dialog._preview_valid


def test_bounds_empty_and_deadline_and_painter_containment(load):
    module, _state, _ = load
    tool = module(TITLES[5])
    package, _ = metric_package()
    tool.glyph_records = lambda package: [("A", [65])]
    empty = NS(isNull=False, boundingBox=NS(width=lambda: 0, height=lambda: 0))
    package.findName = lambda name: NS(findLayer=lambda master: empty)
    assert tool.scan_bounds(package) == {}
    ticks = iter([0, 3])
    tool.time = NS(monotonic=lambda: next(ticks))
    with pytest.raises(ValueError, match="too large"):
        tool.scan_bounds(package)
    painter_tool = module(TITLES[1])
    ended = []
    painter_tool.QtGui.QPainter = lambda widget: NS(end=lambda: ended.append(True))
    diagram = object.__new__(painter_tool.Diagram)
    diagram.owner = NS(
        edited_rows=lambda: (_ for _ in ()).throw(ValueError("invalid cells")),
        status=NS(setText=lambda value: None),
    )
    diagram.paintEvent(None)
    assert ended == [True] and "invalid cells" in diagram._paint_error


@pytest.mark.parametrize("title", TITLES)
def test_panel_uses_shared_shell_instead_of_repeating_safety_methods(title):
    import ast

    source = (ROOT / "Scripts/Font Info" / (title + ".py")).read_text()
    tree = ast.parse(source)
    dialog = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Dialog"
    )
    repeated = {"safe", "_connect", "ensure_font", "ensure_preview", "rows"}
    assert not repeated.intersection(
        node.name for node in dialog.body if isinstance(node, ast.FunctionDef)
    ), "Safety and shell methods belong to shared App panel"
    assert "font_info_dialog_type" in source
