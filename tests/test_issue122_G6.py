# this_file: tests/test_issue122_G6.py
# SPDX-License-Identifier: Apache-2.0
"""Font-bound export workflows with real binary and installed-App checks."""

import ast
import builtins
import importlib.util
import inspect
from collections.abc import Callable, Iterable
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
TITLES = ("Trial Font Maker",)
FILES = [ROOT / "Scripts" / "Font Info" / f"{name}.py" for name in TITLES]


def load(index: int) -> Any:
    """Load a script without launching its UI."""
    spec = importlib.util.spec_from_file_location(f"g6_{index}", FILES[index])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_installed_app_names_exist() -> None:
    check_real_app_names(app_names_used(FILES))


def test_headers_and_public_text() -> None:
    for path in FILES:
        text = path.read_text()
        tree = ast.parse(text, feature_version=(3, 11))
        assert text.startswith(f"# this_file: {path.relative_to(ROOT)}\n")
        doc = ast.get_docstring(tree)
        assert "Fernando Díaz" in doc and "Apache-2.0" in doc
        assert "https://github.com/Reset-Type-Studio/Glyphs-Scripts" in doc
        assert not any(
            word in doc.lower()
            for word in ("archived", "unresolved", "draft", "issue 122")
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assert node.returns is not None, node.name
                assert all(
                    a.annotation is not None
                    for a in node.args.args
                    if a.arg not in ("self", "cls")
                ), node.name
        forbidden = {"render", "size", "layout", "update", "font", "move", "statusBar"}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert not forbidden & {
                    n.name for n in node.body if isinstance(n, ast.FunctionDef)
                }


def binary(path: Path) -> None:
    """Build a real TTF with a liga rule and unrelated feature for filtering."""
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    builder = FontBuilder(1000, isTTF=True)
    order = [".notdef", "space", "f", "i", "f_i", "A", "A.alt"]
    builder.setupGlyphOrder(order)
    builder.setupCharacterMap({32: "space", 102: "f", 105: "i", 65: "A"})
    drawings = {}
    for name in order:
        pen = TTGlyphPen(None)
        if name != "space":
            pen.moveTo((25, 0))
            pen.lineTo((225, 0))
            pen.lineTo((225, 600))
            pen.lineTo((25, 600))
            pen.closePath()
        drawings[name] = pen.glyph()
    builder.setupGlyf(drawings)
    builder.setupHorizontalMetrics({name: (500, 0) for name in order})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable(
        {
            "familyName": "Example",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Example Regular",
            "fullName": "Example Regular",
            "psName": "Example-Regular",
            "version": "Version 1.000",
            "copyright": "Source copyright",
        }
    )
    builder.setupOS2(
        sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200
    )
    builder.setupPost(keepGlyphNames=True)
    builder.setupMaxp()
    addOpenTypeFeaturesFromString(
        builder.font,
        "feature liga {sub f i by f_i;} liga; feature salt {sub A by A.alt;} salt; feature kern {pos f i -35;} kern;",
    )
    builder.save(path)


def test_trial_subset_real_saved_binary(tmp_path: Path) -> None:
    from fontTools.ttLib import TTFont

    source, target = tmp_path / "source.ttf", tmp_path / "trial.ttf"
    binary(source)
    before = source.read_bytes()
    result = load(0).make_trial(source, target, ["space", "f", "i", "A"], "TRIAL")
    assert result["path"] == str(target)
    assert source.read_bytes() == before, "Source binary must stay byte-identical"
    with TTFont(target) as font:
        assert set(font.getGlyphOrder()) == {".notdef", "space", "f", "i", "A"}
        assert font["name"].getDebugName(1) == "TRIAL Example"
        assert font["name"].getDebugName(6) == "TRIAL-Example-Regular"
        assert font["name"].getDebugName(0) == "Source copyright"
        assert list(font["glyf"]["A"].coordinates) == [
            (25, 0),
            (225, 0),
            (225, 600),
            (25, 600),
        ]
        assert font["hmtx"].metrics["A"] == (500, 0)
        if "GSUB" in font:
            assert not font["GSUB"].table.LookupList.Lookup, (
                "Unselected ligature lookups must be pruned"
            )
        assert set(font.getBestCmap()) == {32, 65, 102, 105}
    assert result["glyphs"] == 5


def test_trial_missing_names_and_overwrite_refuse_before_write(tmp_path: Path) -> None:
    tool = load(0)
    source, target = tmp_path / "source.ttf", tmp_path / "trial.ttf"
    binary(source)
    with pytest.raises(ValueError, match="missing"):
        tool.make_trial(source, target, ["absent"], "TRIAL")
    assert not target.exists()
    target.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        tool.make_trial(source, target, ["A"], "TRIAL")
    assert target.read_bytes() == b"keep"


@pytest.mark.parametrize(
    "prefix", ["", " ", "A\x00", "A\u00a0", "A\u2028", "A\u2029", "A/", "é"]
)
def test_trial_invalid_prefix(prefix: str) -> None:
    with pytest.raises(ValueError):
        load(0).prefix_text(prefix)


def test_trial_variable_binary_refused(tmp_path: Path) -> None:
    from fontTools.ttLib import TTFont, newTable

    source = tmp_path / "variable.ttf"
    binary(source)
    with TTFont(source) as font:
        font["fvar"] = newTable("fvar")
        font["fvar"].axes, font["fvar"].instances = [], []
        font.save(source)
    with pytest.raises(ValueError, match="static"):
        load(0).make_trial(source, tmp_path / "trial.ttf", ["A"], "TRIAL")


def test_no_native_write_paths() -> None:
    for path in FILES:
        text = path.read_text()
        assert "notifyChangesApplied" not in text and "fontpr.call" not in text


def test_trial_cff_names_survive_reopen(tmp_path: Path) -> None:
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.t2CharStringPen import T2CharStringPen
    from fontTools.ttLib import TTFont

    source, target = tmp_path / "source.otf", tmp_path / "trial.otf"
    builder = FontBuilder(1000, isTTF=False)
    builder.setupGlyphOrder([".notdef", "A"])
    builder.setupCharacterMap({65: "A"})
    builder.setupHorizontalMetrics({".notdef": (500, 0), "A": (500, 0)})
    builder.setupHorizontalHeader(ascent=800, descent=-200)
    builder.setupNameTable(
        {
            "familyName": "Example",
            "styleName": "Regular",
            "psName": "Example-Regular",
            "fullName": "Example Regular",
        }
    )
    builder.setupOS2(
        sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200
    )
    builder.setupPost()
    strings = {
        name: T2CharStringPen(500, None).getCharString() for name in (".notdef", "A")
    }
    builder.setupCFF(
        "Example-Regular",
        {"FullName": "Example Regular", "FamilyName": "Example", "Weight": "Regular"},
        strings,
        {},
    )
    builder.save(source)
    load(0).make_trial(source, target, ["A"], "TRIAL")
    with TTFont(target) as font:
        assert font["CFF "].cff.fontNames == ["TRIAL-Example-Regular"]
        assert font["CFF "].cff.topDictIndex[0].FamilyName == "TRIAL Example"
        assert font["CFF "].cff.topDictIndex[0].FullName == "TRIAL Example Regular"
        assert font["name"].getDebugName(6) == "TRIAL-Example-Regular"


def test_trial_preview_keeps_unrelated_and_existing_files(tmp_path: Path) -> None:
    source_dir, output_dir = tmp_path / "input", tmp_path / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    binary(source_dir / "one.ttf")
    binary(source_dir / "two.ttf")
    (output_dir / "TRIAL-one.ttf").write_bytes(b"preserve")
    rows = load(0).preview(source_dir, output_dir, ["A"], "TRIAL", "Example", 1000)
    assert [r.note for r in rows] == ["kept: destination exists", ""]
    wrong = load(0).preview(source_dir, output_dir, ["A"], "TRIAL", "Other", 1000)
    assert "family name or UPM" in wrong[1].note
    assert (output_dir / "TRIAL-one.ttf").read_bytes() == b"preserve"


class Signal:
    """Owned fake PythonQt signal with explicit disconnection."""

    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, callback: Any) -> None:
        self.slots.append(callback)

    def disconnect(self, callback: Any) -> None:
        self.slots.remove(callback)


class Widget:
    """Reject assignment to names of native members; record table contents."""

    NoEditTriggers = 0

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.currentIndex = 0
        self.items: list[Any] = []
        self.values: dict[Any, Any] = {}
        self.enabled, self.checked = True, False
        self.changed = Signal()
        self.clicked, self.textChanged = Signal(), Signal()
        self.toggled, self.currentIndexChanged = Signal(), Signal()

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"render", "size", "layout", "update", "font", "move", "statusBar"}:
            raise AttributeError(f"native member {name}")
        object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> Any:
        if name == "font":
            return NS(
                pointSizeF=lambda: 12,
                setPointSizeF=lambda v: None,
                setBold=lambda v: None,
            )
        if name.startswith(("set", "add")) or name in {
            "resize",
            "close",
            "deleteLater",
        }:
            return lambda *a: None
        raise AttributeError(name)

    def setText(self, value: str) -> None:
        self.text = value

    def setEnabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def setChecked(self, checked: bool) -> None:
        self.checked = checked

    def isChecked(self) -> bool:
        return self.checked

    def addItems(self, items: list[Any]) -> None:
        self.items.extend(items)

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.values[row, column] = item

    def verticalHeader(self) -> Any:
        return Widget()

    def horizontalHeader(self) -> Any:
        return Widget()


@pytest.fixture
def panels(monkeypatch: pytest.MonkeyPatch, real_app: Any) -> Any:
    """Use real installed SelectionPanel logic above owned native and Qt fakes."""
    gui = NS(
        **{
            name: Widget
            for name in (
                "QDialog",
                "QLabel",
                "QVBoxLayout",
                "QHBoxLayout",
                "QGridLayout",
                "QComboBox",
                "QCheckBox",
                "QLineEdit",
                "QTableWidget",
                "QPushButton",
                "QTableWidgetItem",
            )
        }
    )
    gui.QHeaderView = NS(Stretch=1)
    gui.QAbstractItemView = NS(NoEditTriggers=0)
    qt = NS(QtGui=gui, QtCore=NS(Qt=NS(AlignRight=1, AlignVCenter=2)))
    package = NS(
        id=10,
        fgId=100,
        master="Regular",
        masters=["Regular"],
        info=NS(familyName="Example", unitsPerEm=1000, postscriptStemSnapV=[80]),
    )
    package.setMaster = lambda master: setattr(package, "master", master)
    closed: list[str] = []
    state = NS(active=package, selection=["A"], shown=[])
    import importlib

    original = importlib.import_module("fontlabapp.scripting")
    app_names = (
        "current_package",
        "names_selected_names",
        "connect_guarded",
        "close_script_dialog",
        "show_script_dialog",
    )
    signatures = {
        name: inspect.signature(getattr(original, name)) for name in app_names
    }

    def current_package(expected_id: int | None = None) -> Any | None:
        active = state.active
        return (
            active
            if active is not None and (expected_id is None or active.id == expected_id)
            else None
        )

    def names_selected_names() -> list[str]:
        return list(state.selection)

    def connect_guarded(dialog: Any, signal: Any, callback: Callable[..., Any]) -> None:
        signal.connect(callback)
        dialog._connections.append((signal, callback))

    def close_script_dialog(
        dialog: Any,
        event: Any,
        key: str,
        *,
        timers: Iterable[Any] = (),
        children: Iterable[Any] = (),
    ) -> None:
        for signal, slot in dialog._connections:
            signal.disconnect(slot)
        dialog._connections.clear()
        closed.append(key)

    def show_script_dialog(dialog_type: Callable[[Any], Any], key: str) -> Any:
        state.shown.append(key)
        return dialog_type(None)

    fakes = {
        "current_package": current_package,
        "names_selected_names": names_selected_names,
        "connect_guarded": connect_guarded,
        "close_script_dialog": close_script_dialog,
        "show_script_dialog": show_script_dialog,
    }
    app = real_app(
        qt=qt,
        fontlab=NS(CurrentFont=lambda: NS(glyphs=[])),
        scripting=fakes,
        modules=["selection_panel", "qt_literal_text"],
    )
    import fly

    monkeypatch.setattr(fly, "qt", qt)
    return NS(
        package=package,
        app=app,
        closed=closed,
        state=state,
        fakes=fakes,
        signatures=signatures,
    )


@pytest.mark.parametrize("index", [0])
def test_panel_binds_font_refuses_switched_font_and_disconnects(
    index: int, panels: Any
) -> None:
    panel = load(index).panel_type()()
    assert panel.package_id == 10
    assert panel._connections, "Signals must have owned callbacks"
    panels.package.id = 11
    panel.refresh()
    assert not panel.apply_button.enabled
    assert "font changed" in panel.subtitle.text.lower()
    panel.closeEvent(NS())
    assert not panel._connections
    assert panels.closed


def test_trial_panel_writes_selected_glyph_binary(panels: Any, tmp_path: Path) -> None:
    source, target = tmp_path / "input", tmp_path / "output"
    source.mkdir()
    target.mkdir()
    binary(source / "regular.ttf")
    panel = load(0).panel_type()()
    panel.input_edit.setText(str(source))
    panel.target_edit.setText(str(target))
    panel.refresh()
    assert panel.apply_button.enabled, (panel.status.text, panel.subtitle.text)
    panel.apply()
    assert len(panel.last_result["files"]) == 1
    assert (target / "TRIAL-regular.ttf").is_file()


@pytest.mark.parametrize("index", [0])
@pytest.mark.parametrize("text", ["x\0", "x\u00a0", "x\u2028", "x\u2029"])
def test_qt_field_refuses_lossy_text(index: int, text: str, panels: Any) -> None:
    with pytest.raises(ValueError, match="PythonQt"):
        load(index).read_field(NS(text=text))


def test_trial_preview_keeps_bad_binary_while_valid_file_stays_ready(
    tmp_path: Path,
) -> None:
    target = tmp_path / "output"
    target.mkdir()
    (tmp_path / "bad.ttf").write_bytes(b"not an OpenType font")
    binary(tmp_path / "valid.ttf")
    rows = load(0).preview(tmp_path, target, ["A"], "TRIAL", "Example", 1000)
    assert len(rows) == 2
    assert rows[0].note.startswith("kept:") and rows[1].note == ""


def test_every_app_fake_has_the_installed_signature(panels: Any) -> None:
    assert set(panels.fakes) == set(panels.signatures)
    for name, fake in panels.fakes.items():
        assert inspect.signature(fake) == panels.signatures[name], name


def test_main_and_absent_font_or_selection(panels: Any) -> None:
    tool = load(0)
    assert tool.main().package_id == 10
    assert panels.state.shown == [tool.KEY]
    panels.state.active = None
    panel = tool.panel_type()()
    assert not panel.apply_button.enabled and "Open a font" in panel.subtitle.text
    panels.state.active = panels.package
    panels.state.selection = []
    panel = tool.panel_type()()
    assert not panel.apply_button.enabled and "Select glyphs" in panel.subtitle.text


def test_ttfautohint_menu_is_removed() -> None:
    assert not (ROOT / "Scripts/Font Info/TTFAutohint Options From Stems.py").exists()


@pytest.mark.parametrize(
    "field",
    [
        "TtaHintingRangeMin",
        "TtaHintingRangeMax",
        "TtaHintingLimit",
        "TtaIncreaseXHeight",
        "TtaHintComposites",
        "TtaSharpGray",
        "TtaSharpGdi",
        "TtaSharpDw",
        "TtaNoClipping",
    ],
)
def test_public_font_info_writer_refuses_ttfautohint_keys(
    field: str, panels: Any
) -> None:
    with pytest.raises(ValueError, match="Unsupported Font Info field"):
        panels.app["scripting"].write_font_info(
            panels.package, [("Regular", field, 0, 1)], undo_name="TTFAutohint"
        )


def test_ligature_expansion_is_explicit_and_preview_lists_extra(tmp_path: Path) -> None:
    from fontTools.ttLib import TTFont

    source_dir, output_dir = tmp_path / "input", tmp_path / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    source = source_dir / "source.ttf"
    binary(source)
    tool = load(0)
    rows = tool.preview(
        source_dir,
        output_dir,
        ["f", "i"],
        "TRIAL",
        "Example",
        1000,
        keep_ligatures=True,
    )
    assert rows[0].extra == ("f_i",), "Preview must name every additional liga glyph"
    result = tool.make_trial(
        source, output_dir / "trial.ttf", ["f", "i"], "TRIAL", keep_ligatures=True
    )
    assert result["extra"] == ["f_i"]
    with TTFont(output_dir / "trial.ttf") as font:
        assert set(font.getGlyphOrder()) == {".notdef", "f", "i", "f_i"}
        assert [r.FeatureTag for r in font["GSUB"].table.FeatureList.FeatureRecord] == [
            "liga"
        ]


@pytest.mark.parametrize("remove", [False, True])
def test_positioning_is_preserved_unless_requested(
    tmp_path: Path, remove: bool
) -> None:
    from fontTools.ttLib import TTFont

    source, target = tmp_path / "source.ttf", tmp_path / "trial.ttf"
    binary(source)
    load(0).make_trial(source, target, ["f", "i"], "TRIAL", remove_positioning=remove)
    with TTFont(target) as font:
        assert ("GPOS" in font) is not remove
        if not remove:
            records = (
                font["GPOS"]
                .table.LookupList.Lookup[0]
                .SubTable[0]
                .PairSet[0]
                .PairValueRecord
            )
            assert records[0].Value1.XAdvance == -35


def test_identical_or_symlinked_folders_are_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="different"):
        load(0).preview(tmp_path, tmp_path, ["A"], "TRIAL", "Example", 1000)
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="different"):
        load(0).preview(tmp_path, alias, ["A"], "TRIAL", "Example", 1000)


@pytest.mark.parametrize("entrypoint", ["preview", "make_trial"])
def test_missing_fonttools_has_install_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, entrypoint: str
) -> None:
    real_import = builtins.__import__

    def without_fonttools(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "fontTools" or name.startswith("fontTools."):
            raise ModuleNotFoundError("fontTools is missing", name="fontTools")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_fonttools)
    tool = load(0)
    with pytest.raises(ValueError, match="Install fontTools.*Settings > Python"):
        if entrypoint == "preview":
            tool.preview(tmp_path, tmp_path / "out", ["A"], "TRIAL", "Example", 1000)
        else:
            tool.make_trial(
                tmp_path / "source.ttf", tmp_path / "trial.ttf", ["A"], "TRIAL"
            )


def test_unknown_name_encoding_is_a_named_kept_row(tmp_path: Path) -> None:
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.tables._n_a_m_e import NameRecord

    source_dir, output_dir = tmp_path / "input", tmp_path / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    source = source_dir / "unknown.ttf"
    binary(source)
    with TTFont(source) as font:
        record = NameRecord()
        record.nameID, record.platformID, record.platEncID, record.langID = 4, 99, 99, 0
        record.string = b"unknown encoding"
        font["name"].names.append(record)
        font.save(source)
    rows = load(0).preview(source_dir, output_dir, ["A"], "TRIAL", "Example", 1000)
    assert rows[0].note.startswith("kept:") and "encoding" in rows[0].note
    assert not list(output_dir.iterdir())


def test_prefix_and_checkbox_changes_reuse_source_scan(
    panels: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_dir, output_dir = tmp_path / "input", tmp_path / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    binary(source_dir / "source.ttf")
    tool = load(0)
    scans: list[Path] = []
    original = tool.scan_exports

    def count(*args: Any, **kwargs: Any) -> Any:
        scans.append(args[0])
        return original(*args, **kwargs)

    monkeypatch.setattr(tool, "scan_exports", count)
    panel = tool.panel_type()()
    panel.input_edit.setText(str(source_dir))
    panel.target_edit.setText(str(output_dir))
    panel.refresh()
    assert scans == [source_dir]
    for prefix in ("T", "TR", "TRIAL"):
        panel.prefix_edit.setText(prefix)
        panel.refresh()
    panel.ligature_box.setChecked(True)
    panel.position_box.setChecked(True)
    panel.refresh()
    assert scans == [source_dir], (
        "Prefix and checkbox changes must not reopen source fonts"
    )
    panel.refresh_exports()
    assert scans == [source_dir, source_dir]
    panel.reselect()
    assert scans == [source_dir, source_dir, source_dir]


def test_changed_source_is_kept_until_preview_is_refreshed(tmp_path: Path) -> None:
    source_dir, output_dir = tmp_path / "input", tmp_path / "output"
    source_dir.mkdir()
    output_dir.mkdir()
    source = source_dir / "source.ttf"
    binary(source)
    tool = load(0)
    rows = tool.preview(source_dir, output_dir, ["A"], "TRIAL", "Example", 1000)
    source.write_bytes(b"changed after preview")
    with pytest.raises(ValueError, match="changed"):
        tool.make_trial(
            source, rows[0].target, ["A"], "TRIAL", expected_digest=rows[0].digest
        )
    assert not rows[0].target.exists()
