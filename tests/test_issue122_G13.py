# this_file: tests/test_issue122_G13.py
# SPDX-License-Identifier: Apache-2.0
"""Behaviour tests with owned data; these do not certify the native host."""

import ast
import importlib.util
import inspect
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any
from unittest.mock import create_autospec, patch

import pytest
from conftest import app_module_name, app_names_used, check_real_app_names
from menu_layout import _menu_bytes

ROOT = Path(__file__).parents[1]
FILES = {
    "report": ROOT / "Scripts/Kerning/Kerning Energy Report.py",
    "punctuation": ROOT / "Scripts/Kerning/Unbundle Punctuation Kerning.py",
    "sans": ROOT / "Scripts/Contours/Sansomatic.py",
}

FAKED_APP_NAMES: dict[str, set[str]] = {}


def patch_app(monkeypatch: Any, module: Any, name: str, action: Any) -> Any:
    """Enforce the real callable signature on every replaced App function."""
    current = getattr(module, name)
    original = getattr(current, "_g13_original", current)
    assert parameter_shape(action) == parameter_shape(original), (
        f"{module.__name__}.{name}"
    )
    replacement = create_autospec(original, spec_set=True, side_effect=action)
    replacement._g13_original = original
    FAKED_APP_NAMES.setdefault(module.__name__, set()).add(name)
    monkeypatch.setattr(module, name, replacement)
    return replacement


def load(key: str) -> Any:
    """Run the retained Sansomatic menu or the production consolidated kerning module."""
    if key != "sans":
        from PySide6 import QtCore, QtGui, QtWidgets

        gui = NS(**{name: getattr(QtGui, name) for name in dir(QtGui) if name.startswith("Q")})
        vars(gui).update({name: getattr(QtWidgets, name) for name in dir(QtWidgets) if name.startswith("Q")})
        with patch.dict(sys.modules, {"PythonQt": NS(QtCore=QtCore, QtGui=gui)}):
            path = "kerning_browser.energy" if key == "report" else "kerning_batch.punctuation"
            return importlib.import_module("fontlabapp.studios." + path)
    source = ROOT.parent / "fontlab-fontlabapp/src/fontlabapp/studios/shape_generators/sansomatic.py"
    spec = importlib.util.spec_from_file_location("g13_" + key, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def historical_source(key: str) -> str:
    """Read exact source data for licence/metadata assertions; never execute archives."""
    from menu_layout import source_bytes

    if key == "sans":
        return _menu_bytes(ROOT, str(FILES[key].relative_to(ROOT))).decode()
    rows = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
    source = next(row["source"] for row in rows if row["source"]["path"] == str(FILES[key].relative_to(ROOT)))
    return source_bytes(ROOT, source).decode()


def test_installed_app_names(tmp_path: Path) -> None:
    sources = []
    for key in FILES:
        target = tmp_path / (key + ".txt")
        target.write_text(historical_source(key))
        sources.append(target)
    check_real_app_names(app_names_used(sources))
    assert load("report").EnergyPanel and load("punctuation").PunctuationPanel


@pytest.mark.parametrize("key", FILES)
def test_public_structure(key: str) -> None:
    tree = ast.parse(historical_source(key))
    doc = ast.get_docstring(tree)
    assert "Simon Cozens" in doc and "MIT" in doc
    assert "https://github.com/simoncozens/GlyphsScripts" in doc
    forbidden = {
        "render",
        "size",
        "layout",
        "update",
        "font",
        "move",
        "statusBar",
        "palette",
        "parent",
        "style",
        "width",
        "height",
        "geometry",
        "pos",
        "windowTitle",
        "objectName",
        "children",
        "cursor",
        "locale",
        "mask",
    }
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                defined.update(
                    n.attr
                    for n in ast.walk(target)
                    if isinstance(n, ast.Attribute)
                    and isinstance(n.value, ast.Name)
                    and n.value.id == "self"
                )
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    targets = (
                        item.targets if isinstance(item, ast.Assign) else [item.target]
                    )
                    defined.update(
                        n.id
                        for target in targets
                        for n in ast.walk(target)
                        if isinstance(n, ast.Name)
                    )
    assert not forbidden.intersection(defined)
    assert "# SPDX-License-Identifier: MIT" in historical_source(key).splitlines()[:3]
    assert not any(
        isinstance(n, ast.ImportFrom) and n.module == "fly.ap" for n in ast.walk(tree)
    )


def test_report_exact_zero_and_exception_precedence() -> None:
    tool = load("report")
    group = {"L": (("A", "Aacute"), "KernLeft"), "R": (("V",), "KernRight")}
    pairs = {
        (("L", "groupMode"), ("R", "groupMode")): -80,
        (("A", "glyphMode"), ("V", "glyphMode")): 0,
    }
    assert tool.effective("A", "V", pairs, group) == 0
    assert tool.effective("Aacute", "V", pairs, group) == -80
    assert tool.energy([[-80, 0], [0, -40]]) == 8000


def test_report_rejects_ambiguous_groups() -> None:
    tool = load("report")
    groups = {"one": (("A",), "KernLeft"), "two": (("A",), "KernLeft")}
    with pytest.raises(ValueError, match="Ambiguous"):
        tool.effective("A", "V", {}, groups)


def test_unbundle_keeps_overrides_and_materializes_zero() -> None:
    tool = load("punctuation")
    left, right = ("L", "groupMode"), ("R", "groupMode")
    groups = {"L": (("period", "comma"), "KernLeft"), "R": (("A", "V"), "KernRight")}
    pairs = {(left, right): -60, (("period", "glyphMode"), ("V", "glyphMode")): 0}
    changes = tool.expand(pairs, groups, {"period"})
    assert changes == {(("period", "glyphMode"), ("A", "glyphMode")): -60}
    assert pairs[left, right] == -60
    assert groups["L"][0] == ("period", "comma")
    assert tool.expand({(left, right): 0}, groups, {"period"}) == {
        (("period", "glyphMode"), ("A", "glyphMode")): 0,
        (("period", "glyphMode"), ("V", "glyphMode")): 0,
    }


def test_unbundle_both_sides_and_one_sided_override() -> None:
    tool = load("punctuation")
    groups = {
        "L": (("period", "comma"), "KernLeft"),
        "R": (("period", "A"), "KernRight"),
    }
    pairs = {
        (("L", "groupMode"), ("R", "groupMode")): -60,
        (("period", "glyphMode"), ("R", "groupMode")): -20,
    }
    result = tool.expand(pairs, groups, {"period"})
    assert result[(("period", "glyphMode"), ("period", "glyphMode"))] == -20
    assert result[(("comma", "glyphMode"), ("period", "glyphMode"))] == -60


def test_punctuation_uses_unicode_categories() -> None:
    tool = load("punctuation")
    assert tool.is_punctuation([0x2019])
    assert tool.is_punctuation([0x2A])  # asterisk belongs to punctuation
    assert not tool.is_punctuation([0x3A9])
    assert not tool.is_punctuation([])


@pytest.mark.parametrize("letter", list("AEFHILNOSTVXYZ"))
def test_sans_all_supported_letters(letter: str) -> None:
    tool = load("sans")
    commands, advance = tool.design(letter, 700, 450, 70, 55, 45)
    assert commands and advance > 0
    assert all(math.isfinite(v) for op in commands for v in op[1:])
    assert any(op[0] == "Z" for op in commands)


def test_sans_exact_H_geometry() -> None:
    commands, advance = load("sans").design("H", 700, 450, 70, 50, 40)
    assert advance == 530
    assert commands[0] == ("R", 40, 0, 70, 700)
    assert ("R", 110, 325, 310, 50) in commands


@pytest.mark.parametrize(
    "args",
    [
        ("B", 700, 450, 70, 55, 45),
        ("H", 0, 450, 70, 55, 45),
        ("O", 700, 100, 70, 55, 45),
    ],
)
def test_sans_invalid_design(args: tuple) -> None:
    with pytest.raises(ValueError):
        load("sans").design(*args)


def test_sans_keeps_existing_and_unsafe_layers() -> None:
    tool = load("sans")
    assert "kept" in tool.layer_reason(
        NS(
            shapes=[object()],
            isLocked=False,
            metricsLeft="",
            metricsRight="",
            metricsWidth="",
        )
    )
    assert "kept" in tool.layer_reason(NS(shapes=[], isLocked=True))


def test_main_contains_host_failures(monkeypatch: Any, capsys: Any) -> None:
    for key in ("sans",):
        tool = load(key)
        monkeypatch.setattr(
            tool, "run", lambda: (_ for _ in ()).throw(TimeoutError("capture expired"))
        )
        tool.main()
        assert "capture expired" in capsys.readouterr().out


class HistoryItem:
    """A glyph/layer with an observable native history boundary."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.id = id(self)
        self.history = []
        self.lastModified = None
        self.autoLayer = False
        self.isNull = False

    def checkInitHistoryState(self, index: int) -> None:
        self.history.append(index)


class Layer(HistoryItem):
    def __init__(self, name: str = "Regular") -> None:
        super().__init__(name)
        self.shapes = []
        self.advanceWidth = 0
        self.isLocked = False
        self.metricsLeft = self.metricsRight = self.metricsWidth = ""
        self.updated = 0

    def addShape(self, shape: Any) -> None:
        self.shapes.append(shape)

    def changed(self) -> None:
        self.updated += 1

    def update(self) -> bool:
        return True


class Shape:
    def addContours(self, contours: list, flag: bool) -> None:
        self.contours = contours


@pytest.fixture
def host(real_app: Any, monkeypatch: Any) -> Any:
    """Load installed App writers over owned native history records."""
    import fly

    notifications = []

    class Items:
        def __call__(self) -> Any:
            return self

        def notifyChangesApplied(self, *args: Any) -> None:
            notifications.append(args)

    native = NS(flItems=Items(), flGlyph=NS(updatedFgGlyphs=list), flShape=Shape)
    qt = NS(
        QtCore=NS(QDateTime=NS(currentDateTimeUtc=lambda: "UTC")),
        QtGui=NS(QDialog=type("HostDialog", (), {})),
    )
    monkeypatch.setitem(vars(fly), "qt", qt)
    monkeypatch.setitem(vars(fly), "fl", native)
    modules = real_app(
        qt=qt,
        fontlab=native,
        modules=(
            "history",
            "outline_writer",
            "outline_panel",
            "contour_copy",
            "metrics_panel",
            "selection_panel",
            "kerning_batch",
            "guides",
            "proof",
            "qtsafe",
            "reports",
        ),
    )
    return NS(modules=modules, native=native, qt=qt, notifications=notifications)


def test_sans_real_outline_history_and_noop(host: Any, monkeypatch: Any) -> None:
    tool = load("sans")
    monkeypatch.setattr(tool, "build_path", lambda commands: commands)
    patch_app(
        monkeypatch,
        host.modules["contour_copy"],
        "path_contours",
        lambda path: [NS(nodes=path)],
    )
    glyph, layer = HistoryItem("H"), Layer()
    payload = tool.design("H", 700, 450, 70, 50, 40)
    writer, history = host.modules["outline_writer"], host.modules["history"]
    result = writer.apply_work(
        [(glyph, layer, [payload])],
        tool.TITLE,
        history.auto_facts([]),
        tool.editor_type()(),
    )
    assert result["layers"] == 1
    assert layer.advanceWidth == 530
    assert len(layer.shapes) == 1
    assert glyph.history == layer.history == [0]
    assert host.notifications == [(tool.TITLE, [layer, glyph])]
    assert glyph.lastModified == "UTC"
    writer.apply_work([], tool.TITLE, history.auto_facts([]), tool.editor_type()())
    assert len(host.notifications) == 1


def test_sans_partial_failure_keeps_undo_diagnosis(host: Any, monkeypatch: Any) -> None:
    tool = load("sans")
    monkeypatch.setattr(tool, "build_path", lambda commands: commands)
    patch_app(
        monkeypatch,
        host.modules["contour_copy"],
        "path_contours",
        lambda path: [object()],
    )
    first, second = Layer(), Layer("Bold")
    second.addShape = lambda shape: (_ for _ in ()).throw(RuntimeError("cannot insert"))
    glyph = HistoryItem("H")
    payload = tool.design("H", 700, 450, 70, 50, 40)
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        host.modules["outline_writer"].apply_work(
            [(glyph, first, [payload]), (glyph, second, [payload])],
            tool.TITLE,
            host.modules["history"].auto_facts([]),
            tool.editor_type()(),
        )
    assert len(first.shapes) == 1 and not second.shapes
    assert host.notifications == [(tool.TITLE, [first, second, glyph])]


def test_sans_auto_refusal_before_history(host: Any, monkeypatch: Any) -> None:
    tool = load("sans")
    monkeypatch.setattr(tool, "build_path", lambda commands: commands)
    patch_app(
        monkeypatch,
        host.modules["contour_copy"],
        "path_contours",
        lambda path: [object()],
    )
    glyph, layer = HistoryItem("H"), Layer()
    layer.autoLayer = True
    payload = tool.design("H", 700, 450, 70, 50, 40)
    with pytest.raises(ValueError):
        host.modules["outline_writer"].apply_work(
            [(glyph, layer, [payload])],
            tool.TITLE,
            host.modules["history"].auto_facts([("H", True, ())]),
            tool.editor_type()(),
        )
    assert not layer.shapes and not host.notifications and not glyph.history


class Box:
    """Minimal control that rejects QWidget member collisions on panel objects."""

    def __init__(self, *args: Any) -> None:
        self.value = 0
        self.checked = False
        self.toggled = object()

    def setChecked(self, value: bool) -> None:
        self.checked = value

    def isChecked(self) -> bool:
        return self.checked


class SelectionBase:
    """Only the shared panel hook contract; no invented native API fallback."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {
            "layout",
            "font",
            "render",
            "size",
            "update",
            "controls",
            "statusBar",
        }:
            raise AttributeError(name)
        object.__setattr__(self, name, value)

    def add_row(self, label: str, *widgets: Any) -> None:
        self.control_rows.append((label, widgets))

    def watch(self, signal: Any, callback: Any = None) -> None:
        self.watched.append(signal)


class OutlineBase(SelectionBase):
    """Separate OutlinePanel double, with its exact numeric-control signature."""

    def spin(
        self, low: float, high: float, value: float, suffix: str = "", decimals: int = 0
    ) -> Any:
        return NS(value=value)


def test_sans_controls_planner_and_kept_rows(host: Any, monkeypatch: Any) -> None:
    patch_app(
        monkeypatch, host.modules["outline_panel"], "panel_type", lambda: OutlineBase
    )
    tool = load("sans")
    panel = tool.panel_type()()
    panel.control_rows, panel.watched = [], []
    panel.build_controls()
    assert len(panel.control_rows) == 5
    layer = Layer()
    glyph = NS(name="H", unicodes=[72])
    row = panel.planner()(glyph, "Regular", layer)[0]
    assert row.edit[1] == 540 and row.key == ("capital", "H")
    layer.shapes = [object()]
    kept = panel.planner()(glyph, "Regular", layer)[0]
    assert kept.edit is None and "kept" in kept.new
    assert (
        panel.planner()(NS(name="Q", unicodes=[81]), "Regular", Layer())[0].edit is None
    )


def punctuation_panel(module: Any) -> Any:
    panel = object.__new__(module.PunctuationPanel)
    panel.names, panel.found = [], []
    panel.punctuation_only = NS(isChecked=lambda: True)
    panel.scope = NS(currentIndex=lambda: 1)
    panel.subtitle = NS(setText=lambda text: None)
    panel.edits = {}
    panel.grid = NS(set_rows=lambda rows: setattr(panel, "visible_rows", rows))
    panel.count = NS(setText=lambda text: setattr(panel, "count_text", text))
    panel.apply_button = NS(setEnabled=lambda enabled: setattr(panel, "apply_enabled", enabled))
    return panel


def planned(panel: Any, package: Any, masters: list[str], host: Any) -> list:
    from fontlabapp.studios._kerning import Tool

    names = list(dict.fromkeys([*panel.names, *(name.split(".", 1)[0] for name in panel.names)]))
    font = {name: NS(unicodes=package.findName(name).fgGlyph.unicodes)
            for name in names if package.findName(name) is not None}
    panel.tool = Tool(NS(package=lambda: package, set_status=lambda text: None), "Kerning Studio", font=lambda: font)
    panel.tool.package = package
    panel.tool.masters, panel.tool.current = masters, masters[0]
    panel.snapshot = panel.source_snapshot = host.modules["kerning_batch"].snapshot_kerning(package, typed=True)
    panel.edits, panel.rows, _ = panel.plan(panel.source_snapshot)
    return panel.found


def write_rows(panel: Any, package: Any, rows: list) -> bool:
    from fontlabapp.studios._kerning import Tool
    from fontlabapp.studios.kerning_batch.punctuation import row_edits

    if not hasattr(panel, "tool"):
        panel.tool = Tool(NS(package=lambda: package, set_status=lambda text: None), "Kerning Studio")
        panel.tool.package = package
    panel.edits = row_edits(rows)
    return panel.tool.write(panel.UNDO, panel.subject(), panel.edits, panel.source_snapshot)


def test_punctuation_panel_stages_one_complete_multimaster_batch(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("punctuation")
    panel = punctuation_panel(tool)
    panel.names = ["period", "A", "missing"]
    glyphs = {
        "period": NS(isNull=False, fgGlyph=NS(unicodes=[46])),
        "A": NS(isNull=False, fgGlyph=NS(unicodes=[65])),
    }
    package = NS(findName=glyphs.get, masters=("Regular", "Bold"), upm=1000)
    source = NS(pairs={}, groups={})
    for master in ("Regular", "Bold"):
        source.pairs[master] = {(("L", "groupMode"), ("A", "glyphMode")): -50}
        source.groups[master] = {"L": (("period",), "KernLeft")}
    batch = host.modules["kerning_batch"]
    patch_app(
        monkeypatch, batch, "snapshot_kerning", lambda package, *, typed=False: source
    )
    captured = []
    patch_app(
        monkeypatch,
        batch,
        "write_kerning",
        lambda package, edits, undo_name, *, expected=None: (
            captured.append(((package, edits, undo_name), {"expected": expected}))
            or True
        ),
    )
    rows = planned(panel, package, ["Regular", "Bold"], host)
    assert len(rows) == 4
    assert len([row for row in rows if row.note]) == 2
    assert [panel.rows[-1][0], *panel.rows[-1][2]] == ["Bold", "period", "A", "-50"]
    result = write_rows(panel, package, rows)
    assert result and panel.changed() == 2
    assert len(captured) == 1
    assert set(captured[0][0][1]) == {"Regular", "Bold"}
    assert captured[0][1] == {"expected": source}
    assert "2" in panel.result(panel.edits)


def test_report_main_report_no_font_refusal_and_exact_report(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("report")
    scripting, batch, reports = (
        host.modules[name] for name in ("scripting", "kerning_batch", "reports")
    )
    from fontlabapp.studios._kerning import Tool
    from fontlabapp.studios import _kerning

    package = NS(master="Regular")
    state = Tool(NS(package=lambda: package, set_status=lambda text: None), "Kerning Browser")
    state.package, state.current = None, "Regular"
    panel = object.__new__(tool.EnergyPanel)
    panel.tool = state
    captions = []
    panel.subtitle = NS(setText=captions.append)
    panel.grid = NS(set_rows=lambda rows: None)
    panel.open_button = NS(setEnabled=lambda value: None)
    panel.refresh()
    assert panel.result is None and captions[-1] == "Open a font first."
    with pytest.raises(ValueError, match="Select glyphs"):
        panel.open_report()
    state.package = package
    monkeypatch.setattr(_kerning, "names_selected_names", lambda: ["A", "V", "A"])
    source = NS(
        pairs={"Regular": {(("A", "glyphMode"), ("V", "glyphMode")): -80}},
        groups={"Regular": {}},
    )
    patch_app(
        monkeypatch, batch, "snapshot_kerning", lambda package, *, typed=False: source
    )
    patch_app(monkeypatch, batch, "ensure_snapshot", lambda package, expected: source)
    # Preserve the real signature, including optional report budget parameters.
    shown = create_autospec(
        reports.show_report, spec_set=True, side_effect=lambda report, **kwargs: report
    )
    monkeypatch.setattr(reports, "show_report", shown)
    with pytest.raises(TypeError):
        shown({}, unsupported_option=True)
    panel.refresh()
    report = panel.open_report()
    assert report["energy"] == 6400
    assert report["read_only"] is True and "effective_values" not in report
    assert shown.call_args.kwargs == {
        "title": "Kerning Energy Report — Read-only",
        "key": tool.KEY,
    }
    assert report["glyphs"] == ["A", "V"]
    assert (
        report["independent_spacing_suggestions"][0]["right_sidebearing_delta"] == -40
    )
    assert not host.notifications


@pytest.mark.parametrize("key", ["sans"])
def test_panel_launch_uses_owned_key(host: Any, monkeypatch: Any, key: str) -> None:
    tool = load(key)
    sentinel = object()
    monkeypatch.setattr(tool, "panel_type", lambda: sentinel)
    patch_app(
        monkeypatch,
        host.modules["scripting"],
        "show_script_dialog",
        lambda dialog_type, key: (dialog_type, key),
    )
    assert tool.run() == (sentinel, tool.KEY)


class PathFake:
    """Strict path-operation surface, retaining subtraction and curve commands."""

    def __init__(self) -> None:
        self.ops = []

    def addRect(self, *values: float) -> None:
        self.ops.append(("rect", *values))

    def addEllipse(self, *values: float) -> None:
        self.ops.append(("ellipse", *values))

    def moveTo(self, *values: float) -> None:
        self.ops.append(("move", *values))

    def lineTo(self, *values: float) -> None:
        self.ops.append(("line", *values))

    def cubicTo(self, *values: float) -> None:
        self.ops.append(("cubic", *values))

    def closeSubpath(self) -> None:
        self.ops.append(("close",))

    def united(self, other: Any) -> Any:
        self.ops.extend(other.ops)
        return self

    def subtracted(self, other: Any) -> Any:
        self.ops.append(("subtract", other.ops))
        return self


@pytest.mark.parametrize("letter", list("HANOXS"))
def test_sans_path_builder_routes_each_operation(host: Any, letter: str) -> None:
    host.qt.QtGui.QPainterPath = PathFake
    tool = load("sans")
    commands, _ = tool.design(letter, 700, 450, 70, 55, 45)
    result = tool.build_path(commands)
    assert result.ops
    if letter == "O":
        assert any(op[0] == "subtract" for op in result.ops)
    if letter == "S":
        assert sum(op[0] == "cubic" for op in result.ops) == 8


def test_punctuation_ambiguous_glyph_kept_while_other_selection_plans(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("punctuation")
    panel = punctuation_panel(tool)
    panel.names = ["period", "comma"]
    package = NS(
        findName=lambda name: NS(isNull=False, fgGlyph=NS(unicodes=[46])),
        masters=("Regular",),
        upm=1000,
    )
    source = NS(
        pairs={"Regular": {(("L", "groupMode"), ("A", "glyphMode")): -50}},
        groups={
            "Regular": {
                "L": (("period", "comma"), "KernLeft"),
                "ambiguous": (("period",), "KernLeft"),
            }
        },
    )
    patch_app(
        monkeypatch,
        host.modules["kerning_batch"],
        "snapshot_kerning",
        lambda package, *, typed=False: source,
    )
    rows = planned(panel, package, ["Regular"], host)
    assert any(row.note and row.pair[0][0] == "period" for row in rows)
    assert any(not row.note and row.pair[0][0] == "comma" for row in rows)


def test_punctuation_writer_failure_has_native_undo_hint(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("punctuation")
    panel = punctuation_panel(tool)
    panel.source_snapshot = object()
    patch_app(
        monkeypatch,
        host.modules["kerning_batch"],
        "write_kerning",
        lambda package, edits, undo_name, *, expected=None: (_ for _ in ()).throw(
            RuntimeError("partial write")
        ),
    )
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        write_rows(
            panel, object(),
            [tool.Row("Regular", (("period", "glyphMode"), ("A", "glyphMode")), -50)],
        )


class NativeKerning:
    """Typed native keys, including explicit zeros and global scaling."""

    def __init__(self) -> None:
        self.groups = {"L": (("period", "comma"), "KernLeft")}
        self.values = {
            (("L", "groupMode"), ("A", "glyphMode")): 0,
            (("A", "glyphMode"), ("V", "glyphMode")): -70,
        }

    def items(self) -> list:
        return [
            (NS(left=NS(id=a[0], mode=a[1]), right=NS(id=b[0], mode=b[1])), value)
            for (a, b), value in self.values.items()
        ]

    def set(self, key: tuple, value: float) -> None:
        self.values[key] = value

    def remove(self, key: tuple) -> None:
        self.values.pop(key, None)

    def scale(self, factor: float) -> None:
        self.values = {key: value * factor for key, value in self.values.items()}


def test_punctuation_real_batch_writer_preserves_classes_and_explicit_zero(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("punctuation")

    containers = {master: NativeKerning() for master in ("Regular", "Bold")}
    package = HistoryItem("test font")
    package.master, package.masters, package.upm = "Regular", tuple(containers), 1000
    package.kerning = containers.__getitem__
    package.findName = lambda name: NS(
        isNull=False, fgGlyph=NS(unicodes=[46] if name == "period" else [65])
    )
    master_container, kerning_container = object(), object()
    package.mastersContainer = lambda: master_container
    package.kerningContainer = lambda: kerning_container
    batch = host.modules["kerning_batch"]
    patch_app(
        monkeypatch,
        batch,
        "current_package",
        lambda expected_id=None: package if expected_id in (None, package.id) else None,
    )
    panel = punctuation_panel(tool)
    panel.names = ["period"]
    rows = planned(panel, package, list(containers), host)
    assert write_rows(panel, package, rows) and panel.changed() == 2
    for native in containers.values():
        assert native.values[(("period", "glyphMode"), ("A", "glyphMode"))] == 0
        assert native.values[(("A", "glyphMode"), ("V", "glyphMode"))] == -70
        assert native.groups == {"L": (("period", "comma"), "KernLeft")}
    # The public kerning writer uses matching before/after package checkpoints.
    assert (
        host.notifications
        == [("Kerning Studio: Add exceptions for 1 glyph on Regular, Bold", [package, master_container, kerning_container])] * 2
    )
    assert package.history == [0]
    panel.source_snapshot = batch.snapshot_kerning(package, typed=True)
    panel.edits = tool.row_edits([])
    panel.snapshot = panel.source_snapshot
    assert panel.edits == {} and not panel.apply()
    assert len(host.notifications) == 2, "A no-op must add no checkpoint"


@pytest.mark.parametrize("letter", list("AEFHILNOSTVXYZ"))
@pytest.mark.parametrize("dimensions", [(700, 450, 70, 55, 45), (900, 600, 90, 65, 30)])
def test_sans_outline_bounds_reach_baseline_and_cap_height(
    letter: str, dimensions: tuple
) -> None:
    from fontTools.pens.boundsPen import BoundsPen

    pen = BoundsPen(None)
    commands, _ = load("sans").design(letter, *dimensions)
    for op, *values in commands:
        if op in ("R", "E"):
            x, y, width, height = values
            pen.moveTo((x, y))
            pen.lineTo((x + width, y + height))
            pen.endPath()
        elif op == "M":
            pen.moveTo(tuple(values))
        elif op == "L":
            pen.lineTo(tuple(values))
        elif op == "C":
            pen.curveTo(tuple(values[:2]), tuple(values[2:4]), tuple(values[4:]))
        elif op == "Z":
            pen.closePath()
    assert pen.bounds[1] == pytest.approx(0), f"{letter}: lower outline bound"
    assert pen.bounds[3] == pytest.approx(dimensions[0]), (
        f"{letter}: upper outline bound"
    )


def parameter_shape(function: Any) -> tuple:
    return tuple(
        (p.name, p.kind, p.default)
        for p in inspect.signature(function).parameters.values()
    )


def test_fakes_match_real_app_signatures(host: Any) -> None:
    import importlib

    host.qt.QtGui.QDialog = type("HostDialog", (), {})
    selection = importlib.import_module("fontlabapp.contours.selection.panel.ui").SelectionPanel
    outline = importlib.import_module("fontlabapp.contours.panel.ui").OutlinePanel
    for double, real in ((SelectionBase, selection), (OutlineBase, outline)):
        for name in ("watch", "add_row"):
            assert parameter_shape(getattr(double, name)) == parameter_shape(
                getattr(real, name)
            )
    assert parameter_shape(OutlineBase.spin) == parameter_shape(outline.spin)
    targets = {
        "kerning_batch": {
            "snapshot_kerning",
            "ensure_snapshot",
            "write_kerning",
            "current_package",
        },
        "scripting": {"current_package", "names_selected_names", "show_script_dialog"},
        "reports": {"show_report"},
        "contour_copy": {"path_contours"},
        "outline_panel": {"panel_type"},
        "selection_panel": {"panel_type"},
    }
    for module_name, names in FAKED_APP_NAMES.items():
        targets.setdefault(module_name.removeprefix("fontlabapp."), set()).update(names)
    for module_name, names in targets.items():
        module = importlib.import_module(app_module_name(module_name))
        for name in names:
            real = getattr(module, name)
            fake = create_autospec(real, spec_set=True)
            with pytest.raises(TypeError):
                fake(unexpected_argument=True)


@pytest.mark.parametrize(
    "value,upm",
    [
        (2.5, 1000),
        (math.nan, 1000),
        (math.inf, 1000),
        (-math.inf, 1000),
        (2**31, 2**31),
        (True, 1000),
        (2001, 1000),
        (-2001, 1000),
    ],
)
def test_master_problem_names_invalid_numeric_pair(
    host: Any, value: float, upm: float
) -> None:
    tool = load("punctuation")
    package = NS(masters=("Bold",), upm=upm, findName=lambda name: NS(isNull=False))
    pair = (("L", "groupMode"), ("V", "glyphMode"))
    message = tool.master_problem(
        package, "Bold", {pair: value}, {"L": (("A",), "KernLeft")}
    )
    assert all(
        text in message for text in ("Bold", "@L", "V", str(value), "master kept")
    ), message


@pytest.mark.parametrize("upm", [0, -1, True, math.nan, math.inf, "1000", 10**400])
def test_master_problem_rejects_invalid_upm(host: Any, upm: Any) -> None:
    package = NS(masters=("Regular",), upm=upm, findName=lambda name: NS(isNull=False))
    pair = (("A", "glyphMode"), ("V", "glyphMode"))
    message = load("punctuation").master_problem(package, "Regular", {pair: -20}, {})
    assert "UPM" in message and "Regular" in message and "master kept" in message


@pytest.mark.parametrize("value", [-2000, 0, 2000])
def test_master_problem_accepts_inclusive_twice_upm_limit(
    host: Any, value: int
) -> None:
    package = NS(masters=("Regular",), upm=1000, findName=lambda name: NS(isNull=False))
    pair = (("A", "glyphMode"), ("V", "glyphMode"))
    assert (
        load("punctuation").master_problem(package, "Regular", {pair: value}, {}) == ""
    )


@pytest.mark.parametrize("chosen", [("Regular",), ("Regular", "Bold")])
@pytest.mark.parametrize("value", [2.5, math.nan, math.inf, 2001])
def test_numeric_problem_blocks_package_write_even_on_unchosen_master(
    host: Any, monkeypatch: Any, chosen: tuple, value: float
) -> None:
    tool = load("punctuation")
    panel = punctuation_panel(tool)
    panel.names = ["period"]
    pair = (("L", "groupMode"), ("A", "glyphMode"))
    source = NS(
        pairs={"Regular": {pair: -50}, "Bold": {pair: value}},
        groups={
            master: {"L": (("period",), "KernLeft")} for master in ("Regular", "Bold")
        },
    )
    package = NS(
        masters=("Regular", "Bold"),
        upm=1000,
        findName=lambda name: NS(isNull=False, fgGlyph=NS(unicodes=[46])),
    )
    batch = host.modules["kerning_batch"]
    patch_app(
        monkeypatch, batch, "snapshot_kerning", lambda package, *, typed=False: source
    )
    writes = patch_app(
        monkeypatch,
        batch,
        "write_kerning",
        lambda package, edits, undo_name, *, expected=None: True,
    )
    rows = planned(panel, package, list(chosen), host)
    assert any(
        row.master == "Bold" and "@L" in row.note and "master kept" in row.note
        for row in rows
    )
    assert any("Font-wide" in row.note for row in rows)
    assert rows and all(row.note for row in rows), (
        "No row may promise a write the App will refuse"
    )
    assert tool.row_edits(rows) == {} and not panel.apply()
    assert writes.call_count == 0 and not host.notifications
    assert panel.apply_enabled is False


def test_stale_class_master_is_named_and_other_master_writes(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("punctuation")
    containers = {master: NativeKerning() for master in ("Regular", "Bold")}
    containers["Bold"].groups["L"] = (("period", "comma", "missing_member"), "KernLeft")
    package = HistoryItem("test font")
    package.master, package.masters, package.upm = "Regular", tuple(containers), 1000
    package.kerning = containers.__getitem__
    package.findName = lambda name: (
        None
        if name == "missing_member"
        else NS(isNull=False, fgGlyph=NS(unicodes=[46] if name == "period" else [65]))
    )
    package.mastersContainer, package.kerningContainer = object, object
    batch = host.modules["kerning_batch"]
    patch_app(
        monkeypatch,
        batch,
        "current_package",
        lambda expected_id=None: package if expected_id in (None, package.id) else None,
    )
    panel = punctuation_panel(tool)
    panel.names = ["period"]
    original_write = batch.write_kerning
    calls = patch_app(monkeypatch, batch, "write_kerning", original_write)
    before_bold = dict(containers["Bold"].values)
    rows = planned(panel, package, list(containers), host)
    kept = [row for row in rows if row.master == "Bold"]
    assert len(kept) == 1 and "@L" in kept[0].note and "missing_member" in kept[0].note
    assert "master kept" in kept[0].note
    assert write_rows(panel, package, rows) and panel.changed() == 1
    assert calls.call_count == 1 and set(calls.call_args.args[1]) == {"Regular"}
    assert containers["Bold"].values == before_bold
    assert (("period", "glyphMode"), ("A", "glyphMode")) in containers["Regular"].values
    assert len(host.notifications) == 2


def test_ambiguous_partner_keeps_only_affected_pair() -> None:
    tool = load("punctuation")
    groups = {"R": (("A", "V"), "KernRight"), "other": (("V",), "KernRight")}
    pairs = {(("period", "glyphMode"), ("R", "groupMode")): -50}
    kept = []
    changes = tool.expand(pairs, groups, {"period"}, kept=kept)
    assert changes == {(("period", "glyphMode"), ("A", "glyphMode")): -50}
    assert len(kept) == 1 and kept[0][0] == (
        ("period", "glyphMode"),
        ("V", "glyphMode"),
    )
    assert "V" in kept[0][1]


def test_report_ambiguity_is_pair_local_and_explicit_zero_wins() -> None:
    tool = load("report")
    groups = {"L": (("A",), "KernLeft"), "other": (("A",), "KernLeft")}
    pairs = {
        (("L", "groupMode"), ("V", "glyphMode")): -80,
        (("A", "glyphMode"), ("V", "glyphMode")): 0,
    }
    result = tool.analyze(["A", "V"], pairs, groups)
    assert result["evaluated_pairs"] == 3 and result["kept_pair_count"] == 1
    assert result["kept_pairs"][0]["left"] == result["kept_pairs"][0]["right"] == "A"
    assert result["energy"] == 0


def test_unencoded_punctuation_alternate_uses_base_unicode(
    host: Any, monkeypatch: Any
) -> None:
    tool = load("punctuation")
    panel = punctuation_panel(tool)
    panel.names = ["period.case"]
    glyphs = {
        name: NS(isNull=False, fgGlyph=NS(unicodes=codes))
        for name, codes in (("period", [46]), ("period.case", []), ("A", [65]))
    }
    package = NS(findName=glyphs.get, masters=("Regular",), upm=1000)
    source = NS(
        pairs={"Regular": {(("L", "groupMode"), ("A", "glyphMode")): -40}},
        groups={"Regular": {"L": (("period.case",), "KernLeft")}},
    )
    patch_app(
        monkeypatch,
        host.modules["kerning_batch"],
        "snapshot_kerning",
        lambda package, *, typed=False: source,
    )
    rows = planned(panel, package, ["Regular"], host)
    assert len(rows) == 1 and not rows[0].note and rows[0].pair[0][0] == "period.case"


def test_sans_unsupported_glyph_is_named(host: Any, monkeypatch: Any) -> None:
    tool = load("sans")
    patch_app(
        monkeypatch, host.modules["outline_panel"], "panel_type", lambda: OutlineBase
    )
    panel = tool.panel_type()()
    panel.control_rows, panel.watched = [], []
    panel.build_controls()
    row = panel.planner()(NS(name="Aacute", unicodes=[193]), "Regular", Layer())[0]
    assert row.edit is None and "Aacute" in row.new and "kept" in row.new


@pytest.mark.parametrize("key", ["report", "punctuation"])
def test_consolidated_actions_contain_original_host_failures(key: str) -> None:
    module = load(key)
    panel_type = module.EnergyPanel if key == "report" else module.PunctuationPanel
    panel = object.__new__(panel_type)
    messages = []
    panel.tool = NS(app="Kerning Studio", shell=NS(package=lambda: object()), say=messages.append)
    assert panel.run(lambda: (_ for _ in ()).throw(TimeoutError("capture expired"))) is None
    assert "capture expired" in messages[-1]


def test_punctuation_launch_uses_consolidated_owned_studio(monkeypatch: Any) -> None:
    import importlib
    import fly

    owner = object()
    studio = importlib.import_module("fontlabapp.studios.kerning_studio")
    calls = []
    monkeypatch.setattr(studio, "show", lambda **kwargs: calls.append(kwargs) or owner)
    monkeypatch.setitem(vars(fly), "ap", importlib.import_module("fontlabapp"))
    monkeypatch.setitem(sys.modules, "fly.ap.studios.kerning_studio", studio)
    spec = importlib.util.spec_from_file_location("g13_consolidated", ROOT / "Scripts/Kerning/Kerning Studio.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() is owner and calls == [{"consolidated": True}]
