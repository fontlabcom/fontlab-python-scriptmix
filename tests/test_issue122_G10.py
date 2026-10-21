# this_file: tests/test_issue122_G10.py
# SPDX-License-Identifier: Apache-2.0
"""Check independent master proofs and cross-font name reports with owned fakes."""

import ast
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any
from unittest.mock import create_autospec

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Master Text Comparison", "Common Glyphs")


def load(title: str) -> ModuleType:
    """Load a menu without running its entry point."""
    spec = importlib.util.spec_from_file_location(
        title, ROOT / "Scripts/Masters" / f"{title}.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None, "A source loader is required"
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def menus() -> tuple[ModuleType, ModuleType]:
    return tuple(load(title) for title in TITLES)


@pytest.fixture
def host(monkeypatch: Any) -> NS:
    """Install explicit Fly doubles; no native module is imported."""
    import fly.ap.named_tab as real_named_tab
    import fly.ap.proof as real_proof

    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    fly.ap = ap
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", ap)
    state = NS(package=None, requests=[], opened=[], reports=[])

    def module(name: str, **values: Any) -> ModuleType:
        result = ModuleType("fly.ap." + name)
        result.__dict__.update(values)
        setattr(ap, name, result)
        monkeypatch.setitem(sys.modules, result.__name__, result)
        return result

    def current_package(expected_id: int | None = None) -> Any:
        p = state.package
        return (
            p
            if p is not None and (expected_id is None or p.id == expected_id)
            else None
        )

    def open_tab(layers: tuple, **kwargs: Any) -> None:
        assert kwargs["expected_id"] == state.package.id, "Fence the source font"
        assert kwargs["master"] == state.package.master, "Fence the source master"
        state.opened.append((layers, kwargs))

    module("scripting", current_package=current_package)
    module(
        "proof",
        parse_text=real_proof.parse_text,
        font_maps=lambda: ({97: "a", 98: "b", 32: "space"}, {"a", "b", "space"}),
    )
    opening = create_autospec(real_named_tab.open_layer_rows, side_effect=open_tab)
    assert inspect.signature(opening) == inspect.signature(real_named_tab.open_layer_rows)
    module("named_tab", open_layer_rows=opening)
    module(
        "reports", show_report=lambda report, **kw: state.reports.append((report, kw))
    )
    fly.fl = NS()
    state.fly, state.module = fly, module
    return state


def package() -> NS:
    """Two master layers for each of two glyphs."""
    return NS(
        id=17,
        master="Regular",
        masters=("Regular", "Bold"),
        findName=lambda name: NS(
            isNull=False, findLayer=lambda layer: NS(isNull=False)
        ),
    )


def test_layout_exact_master_order_and_word_grouping(menus: Any) -> None:
    tool, _ = menus
    rows = tool.comparison_rows(
        "ab,a", {97: "a", 98: "b"}, {"a", "b"}, ("Regular", "Bold"), False
    )
    assert rows == (
        (("a", "Regular"), ("b", "Regular"), (None, ""), ("a", "Bold"), ("b", "Bold")),
        (("a", "Regular"), (None, ""), ("a", "Bold")),
    ), "Each word must retain master order"


def test_layout_stacked_keeps_unencoded_names_and_repeats(menus: Any) -> None:
    rows = menus[0].comparison_rows("/a.alt /a.alt", {}, {"a.alt"}, ("R", "B"), True)
    assert rows == (
        (("a.alt", "R"), ("a.alt", "R")),
        (("a.alt", "B"), ("a.alt", "B")),
    ), "Named glyphs need no Unicode"


def test_stacked_word_groups_have_blank_separator(menus: Any) -> None:
    rows = menus[0].comparison_rows(
        "a,b", {97: "a", 98: "b"}, {"a", "b"}, ("R", "B"), True
    )
    assert rows == ((("a", "R"),), (("a", "B"),), (), (("b", "R"),), (("b", "B"),)), (
        "Keep a blank row between word groups"
    )


@pytest.mark.parametrize(
    "text", ["", " , ", "a\0", "a\u00a0", "a\u2028", "a\u2029", "x", "/missing"]
)
def test_layout_refuses_empty_lossy_or_missing_input(menus: Any, text: str) -> None:
    with pytest.raises(ValueError):
        menus[0].comparison_rows(text, {97: "a"}, {"a"}, ("R",), False)


@pytest.mark.parametrize("masters", [(), ("",), ("R", "R")])
def test_layout_refuses_invalid_master_domain(menus: Any, masters: tuple) -> None:
    with pytest.raises(ValueError):
        menus[0].comparison_rows("a", {97: "a"}, {"a"}, masters, False)


def test_presets_read_bom_newlines_and_no_silent_conversion(
    menus: Any, tmp_path: Path
) -> None:
    path = tmp_path / "words.txt"
    path.write_bytes(b"\xef\xbb\xbfa,b\r\nc,d\r\n\r\n")
    assert menus[0].read_presets(str(path)) == ("a,b", "c,d"), (
        "Normalize UTF-8 BOM and line endings"
    )
    path.write_text("a\u00a0b", encoding="utf-8")
    with pytest.raises(ValueError):
        menus[0].read_presets(str(path))


def test_presets_missing_empty_and_bad_utf8(menus: Any, tmp_path: Path) -> None:
    with pytest.raises(OSError):
        menus[0].read_presets(str(tmp_path / "missing"))
    path = tmp_path / "empty"
    path.write_bytes(b"")
    with pytest.raises(ValueError):
        menus[0].read_presets(str(path))
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        menus[0].read_presets(str(path))


def test_proof_uses_fenced_tab_and_exact_native_symbols(menus: Any, host: NS) -> None:
    host.package = package()
    menus[0].open_comparison("ab,a", False, 17)
    assert len(host.opened) == 1, "Keep all comparison rows in one exact-layer tab"
    assert host.opened[0][0] == ((
        ("a", "Regular"),
        ("b", "Regular"),
        (None, ""),
        ("a", "Bold"),
        ("b", "Bold"),
    ), (
        ("a", "Regular"),
        (None, ""),
        ("a", "Bold"),
    )), "No Unicode substitution for proof glyphs"


def test_proof_refuses_switched_font_missing_layer_and_timeout(
    menus: Any, host: NS, monkeypatch: Any
) -> None:
    host.package = package()
    with pytest.raises(ValueError):
        menus[0].open_comparison("a", False, 999)
    host.package.findName = lambda name: NS(
        isNull=False, findLayer=lambda layer: NS(isNull=True)
    )
    with pytest.raises(ValueError):
        menus[0].open_comparison("a", False, 17)
    host.package = package()
    ticks = iter([0, 3])
    monkeypatch.setattr(menus[0], "monotonic", lambda: next(ticks))
    with pytest.raises(TimeoutError):
        menus[0].open_comparison("a", False, 17)
    assert not host.opened and not host.requests, "Refuse before opening any tab"


def test_common_intersection_keeps_unencoded_and_per_font_unicode(menus: Any) -> None:
    fonts = (
        (17, "First", (("z", ()), ("a", (97, 65)), ("only", (1,)))),
        (18, "Second", (("a", (98,)), ("z", ()), ("other", ()))),
    )
    report = menus[1].common_report(fonts, 17)
    assert report["count"] == 2
    assert report["glyph_names"] == ["a", "z"]
    assert report["slash_text"] == "/a/z"
    assert report["unicode_by_font"] == [
        {
            "font": "First",
            "package_id": 17,
            "glyphs": {"a": ["U+0061", "U+0041"], "z": []},
        },
        {"font": "Second", "package_id": 18, "glyphs": {"a": ["U+0062"], "z": []}},
    ], "Name equality must not imply equal encoding"


def test_common_single_font_empty_intersection_and_no_font(menus: Any) -> None:
    tool = menus[1]
    assert tool.common_report(((1, "One", (("a", (97,)),)),), 1)["glyph_names"] == ["a"]
    assert (
        tool.common_report(((1, "One", ()), (2, "Two", (("a", ()),))), 1)["count"] == 0
    )
    for fonts, current in [((), 1), (((1, "One", ()),), 2)]:
        with pytest.raises(ValueError):
            tool.common_report(fonts, current)


def test_registered_cross_font_capture_and_report(menus: Any, host: NS) -> None:
    host.package = package()
    records = [
        NS(
            id=i,
            fgId=i + 100,
            isNull=False,
            title_name=lambda: "Font",
        )
        for i in (17, 18)
    ]
    workspace = NS(packages=lambda: records)
    host.fly.fl.flWorkspace = NS(instance=lambda: workspace)
    host.fly.fl.flPackage = lambda value: value
    host.fly.fl.AllFonts = lambda: [
        NS(id=row.fgId, glyphs=[NS(name="a", unicodes=[97])]) for row in records
    ]
    menus[1].main()
    assert host.reports[0][0]["count"] == 1, "Main must publish captured font results"
    assert host.reports[0][1]["title"] == "Common Glyphs"


def test_capture_refuses_changed_domain_and_deadline(
    menus: Any, host: NS, monkeypatch: Any
) -> None:
    host.package = package()
    reads = iter([((17, "One", ()),), ((18, "Two", ()),)])
    monkeypatch.setattr(menus[1], "read_fonts", lambda deadline: next(reads))
    with pytest.raises(ValueError):
        menus[1].capture_common()
    monkeypatch.undo()
    monkeypatch.setattr(menus[1], "monotonic", lambda: 10)
    with pytest.raises(TimeoutError):
        menus[1].read_fonts(9)


def test_real_app_imports_use_installed_distribution() -> None:
    check_real_app_names(
        app_names_used([ROOT / "Scripts/Masters" / f"{title}.py" for title in TITLES])
    )


def test_public_files_are_python311_and_read_only(menus: Any) -> None:
    for title, module in zip(TITLES, menus, strict=True):
        path = ROOT / "Scripts/Masters" / f"{title}.py"
        text = path.read_text()
        ast.parse(text, feature_version=(3, 11))
        assert "Independent rewrite" in module.__doc__ and "MIT" in module.__doc__, (
            "Credit source behaviour"
        )
        assert not any(
            word in text.lower()
            for word in ("archived", "unresolved", "issue 122", "batch g10")
        ), "Public language only"
        assert not any(
            word in text
            for word in (
                "notifyChangesApplied",
                "initHistoryState",
                "set_glyph",
                "UpdateAll",
            )
        ), "Read-only tools must not write history"


def test_panel_widgets_callbacks_and_cleanup(
    menus: Any, host: NS, tmp_path: Path, monkeypatch: Any
) -> None:
    """Reject native member collisions and exercise each owned panel action."""
    forbidden = {
        "font",
        "size",
        "layout",
        "update",
        "move",
        "render",
        "statusBar",
        "windowTitle",
    }

    class Signal:
        def __init__(self) -> None:
            self.slots: list = []

        def connect(self, slot: Any) -> None:
            self.slots.append(slot)

        def disconnect(self, slot: Any) -> None:
            self.slots.remove(slot)

        def emit(self, *args: Any) -> None:
            for slot in self.slots:
                slot(*args)

    class Widget:
        def __init__(self, *args: Any) -> None:
            self.text = args[0] if args and isinstance(args[0], str) else ""
            self.currentIndex = 0
            self.currentText = ""
            self.items: list = []
            self.clicked, self.currentIndexChanged = Signal(), Signal()

        def __setattr__(self, key: str, value: Any) -> None:
            assert key not in forbidden, f"Native member collision: {key}"
            object.__setattr__(self, key, value)

        def setText(self, value: str) -> None:
            self.text = value

        def setPlaceholderText(self, value: str) -> None:
            self.placeholder = value

        def setWindowTitle(self, value: str) -> None:
            self.caption = value

        def setMinimumWidth(self, value: int) -> None:
            self.minimum = value

        def setWordWrap(self, value: bool) -> None:
            self.wrap = value

        def addWidget(self, widget: Any) -> None:
            self.items.append(widget)

        def addLayout(self, layout: Any) -> None:
            self.items.append(layout)

        def addItems(self, values: list) -> None:
            self.items.extend(values)
            self.currentText = values[0]
            self.currentIndexChanged.emit(0)

        def clear(self) -> None:
            self.items.clear()
            self.currentText = ""

        def close(self) -> None:
            self.closeEvent("event")

    gui = NS(
        **{
            key: Widget
            for key in (
                "QDialog",
                "QVBoxLayout",
                "QHBoxLayout",
                "QLabel",
                "QLineEdit",
                "QComboBox",
                "QPushButton",
            )
        }
    )
    host.fly.qt = NS(QtGui=gui)
    host.package = package()
    closed = []

    def connect_guarded(dialog: Any, signal: Any, callback: Any) -> None:
        signal.connect(callback)
        dialog._connections.append((signal, callback))

    def close_dialog(dialog: Any, event: Any, key: str) -> None:
        for signal, slot in dialog._connections:
            signal.disconnect(slot)
        dialog._connections.clear()
        closed.append((event, key))

    scripting = sys.modules["fly.ap.scripting"]
    scripting.connect_guarded = connect_guarded
    scripting.close_script_dialog = close_dialog
    scripting.show_script_dialog = lambda cls, key: cls()
    tool = menus[0]
    panel = tool.main()
    assert not forbidden.intersection(type(panel).__dict__), (
        "No class member may shadow a native method"
    )
    assert len(panel._connections) == 4
    path = tmp_path / "presets.txt"
    path.write_bytes(b"\xef\xbb\xbfa,b\r\nab\r\n")
    panel.path_edit.setText(str(path))
    panel.load_presets()
    assert panel.words_edit.text == "a,b" and "normalized" in panel.status.text
    panel.words_edit.setText("a")
    panel.open_proof()
    assert "Opened 1 comparison tabs" in panel.status.text
    host.package = None
    panel.open_proof()
    assert "changed or closed" in panel.status.text
    panel.path_edit.setText(str(tmp_path / "missing"))
    panel.load_presets()
    assert panel.status.text, "Show file errors in the panel"
    monkeypatch.setattr(
        tool,
        "open_comparison",
        lambda *args: (_ for _ in ()).throw(TimeoutError("deadline")),
    )
    panel.open_proof()
    assert panel.status.text == "deadline"
    signals = [signal for signal, _ in panel._connections]
    panel.close()
    assert closed == [("event", tool.KEY)] and all(
        not signal.slots for signal in signals
    ), "Disconnect before panel deletion"
    assert tool.main() is None, "No font must refuse before constructing a panel"


@pytest.mark.parametrize(
    "bad", ["null", "backing", "duplicate", "empty", "unicode", "repeat_font"]
)
def test_common_capture_refuses_bad_records(menus: Any, host: NS, bad: str) -> None:
    glyphs = [NS(name="a", unicodes=[97])]
    record = NS(
        id=17,
        fgId=19,
        isNull=False,
        title_name=lambda: "Font",
    )
    records = [record]
    if bad == "null":
        record.isNull = True
    elif bad == "backing":
        record.fgId = 0
    elif bad == "duplicate":
        glyphs.append(glyphs[0])
    elif bad == "empty":
        glyphs[0].name = ""
    elif bad == "unicode":
        glyphs[0].unicodes = [0x110000]
    else:
        records.append(record)
    host.fly.fl.flWorkspace = NS(instance=lambda: NS(packages=lambda: records))
    host.fly.fl.flPackage = lambda value: value
    host.fly.fl.AllFonts = lambda: [NS(id=19, glyphs=glyphs)]
    with pytest.raises(ValueError):
        menus[1].read_fonts(float("inf"))


def test_common_characters_serialize_with_real_report_formatter(menus: Any) -> None:
    import fly.ap.reports as reports  # noqa: PLR0402

    report = menus[1].common_report(((17, "Font", (("a", (97, 65)), ("z", ()))),), 17)
    assert report["text"] == "aA", "Offer all encoded characters from the current font"
    assert '"text": "aA"' in reports.format_report(report), (
        "Use the installed strict JSON formatter"
    )


def test_common_capture_refuses_unregistered_font(menus: Any, host: NS) -> None:
    host.fly.fl.flWorkspace = NS(instance=lambda: NS(packages=list))
    host.fly.fl.flPackage = lambda value: value
    host.fly.fl.AllFonts = lambda: [NS(id=99, glyphs=[])]
    with pytest.raises(ValueError, match="registered"):
        menus[1].read_fonts(float("inf"))


def test_stacked_rows_keep_blank_separators_in_one_tab(menus: Any, host: NS) -> None:
    host.package = package()
    assert menus[0].open_comparison("a,b", True, 17) == 1
    assert host.opened[0][0] == (
        (("a", "Regular"),),
        (("a", "Bold"),),
        (),
        (("b", "Regular"),),
        (("b", "Bold"),),
    )


def test_public_rows_propagate_failure_and_need_no_encoded_space(
    menus: Any, host: NS
) -> None:
    host.package = package()
    helper = sys.modules["fly.ap.named_tab"]
    opening = helper.open_layer_rows
    opening.side_effect = ValueError("source changed")
    with pytest.raises(ValueError, match="source changed"):
        menus[0].open_comparison("a,b", False, 17)
    assert not host.opened
    opening.side_effect = lambda rows, **kwargs: host.opened.append((rows, kwargs))
    sys.modules["fly.ap.proof"].font_maps = lambda: ({97: "a"}, {"a"})
    assert menus[0].open_comparison("a", False, 17) == 1
    assert host.opened[0][0] == ((("a", "Regular"), (None, ""), ("a", "Bold")),)
    with pytest.raises(TypeError):
        opening((), 17, "Regular")


def test_scripts_use_only_public_app_attributes() -> None:
    used = app_names_used(
        [ROOT / "Scripts/Masters" / f"{title}.py" for title in TITLES]
    )
    assert all(not part.startswith("_") for module in used for part in module.split(".")), used
    assert all(not name.startswith("_") for names in used.values() for name in names), (
        "Keep App implementation details behind public helpers"
    )


def test_real_font_maps_duplicate_unicode_uses_first_name(
    menus: Any, real_app: Any
) -> None:
    modules = real_app(
        qt=NS(),
        fontlab=NS(),
        scripting={"names_font_glyphs": lambda: [("a", [97]), ("a.alt", [97])]},
        modules=("proof",),
    )
    cmap, names = modules["proof"].font_maps()
    assert cmap == {97: "a"} and names == {"a", "a.alt"}
    assert menus[0].comparison_rows("a", cmap, names, ("R",), False) == ((("a", "R"),),)


@pytest.mark.parametrize("failure", [ValueError, RuntimeError, TimeoutError])
def test_report_main_contains_refusals(
    menus: Any, host: NS, monkeypatch: Any, capsys: Any, failure: type
) -> None:
    monkeypatch.setattr(
        menus[1], "capture_common", lambda: (_ for _ in ()).throw(failure("stop"))
    )
    assert menus[1].main() is None
    assert "stop" in capsys.readouterr().out and not host.reports, (
        "Never publish partial data"
    )


def test_explicit_fly_app_paths_have_no_private_names() -> None:
    """Also catch full fly.ap.module._member paths without import aliases."""
    for path in [ROOT / "Scripts/Masters" / f"{title}.py" for title in TITLES]:
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Attribute):
                continue
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name) and current.id == "fly" and parts[0] == "ap":
                assert all(not part.startswith("_") for part in parts), (path, parts)
