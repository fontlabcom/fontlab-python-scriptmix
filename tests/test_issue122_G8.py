# this_file: tests/test_issue122_G8.py
# SPDX-License-Identifier: Apache-2.0
"""Check insertion, FontLab encoding output and installed App names without a host."""

import ast
import importlib.util
import inspect
from collections.abc import Callable, Iterable
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names
from fontlabapp.layer_selection import LayerSelection

SCRIPT = Path(__file__).parents[1] / "Scripts/Font Info/Paste Glyph Order Encoding.py"


def fake_catalog(*, deadline: float | None = None) -> Any:
    """Match the installed glyph catalog signature and retain actual call args."""
    fake_catalog.calls.append(((), {"deadline": deadline}))
    return fake_catalog.result


def fake_selection(deadline: float) -> LayerSelection:
    """Require the native selection deadline instead of hiding missing arguments."""
    fake_selection.calls.append(((), {"deadline": deadline}))
    return fake_selection.result


def fake_show(dialog_type: Callable[[Any], Any], key: str) -> Any:
    """Build the panel without creating a native parent."""
    return dialog_type()


def fake_close(
    dialog: Any,
    event: Any,
    key: str,
    *,
    timers: Iterable[Any] = (),
    children: Iterable[Any] = (),
) -> None:
    """Record the owned child list using the real cleanup signature."""
    dialog.closed_children = tuple(children)


APP_FAKES = (
    ("glyph_catalog", "capture", fake_catalog),
    ("layer_selection", "capture", fake_selection),
    ("scripting", "show_script_dialog", fake_show),
    ("scripting", "close_script_dialog", fake_close),
)


@pytest.mark.parametrize("module_name,name,fake", APP_FAKES)
def test_app_fake_signature_matches_installed(
    module_name: str, name: str, fake: Any
) -> None:
    module = __import__("fontlabapp." + module_name, fromlist=[name])
    assert inspect.signature(fake) == inspect.signature(getattr(module, name)), (
        f"Fake signature drift: {module_name}.{name}"
    )


def install_captures(
    monkeypatch: pytest.MonkeyPatch, rows: tuple, occurrences: tuple
) -> None:
    import fly.ap.glyph_catalog as catalog
    import fly.ap.layer_selection as selection

    fake_catalog.result, fake_catalog.calls = NS(rows=rows), []
    fake_selection.result, fake_selection.calls = NS(occurrences=occurrences), []
    for module, fake in ((catalog, fake_catalog), (selection, fake_selection)):
        assert inspect.signature(module.capture) == inspect.signature(fake), (
            "Keep App call contracts"
        )
        monkeypatch.setattr(module, "capture", fake)


def load() -> Any:
    """Load the lazy script without importing FontLab or Qt."""
    spec = importlib.util.spec_from_file_location("g8_order", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_installed_app_names() -> None:
    assert SCRIPT.exists(), "The menu script must exist"
    check_real_app_names(app_names_used([SCRIPT]))


@pytest.mark.parametrize(
    ("text", "anchor", "expected", "missing"),
    [
        ("D B", "C", ("A", "D", "B", "C"), ()),
        ("B B unknown D", "A", ("B", "D", "A", "C"), ("unknown",)),
        ("A C", "C", ("B", "A", "C", "D"), ()),
        ("D", "D", ("A", "B", "C", "D"), ()),
        ("B\nD\t", "C", ("A", "B", "D", "C"), ()),
    ],
)
def test_insert_exact_order(
    text: str, anchor: str, expected: tuple, missing: tuple
) -> None:
    assert load().insert_names(("A", "B", "C", "D"), text, anchor) == (
        expected,
        missing,
    ), "Insertion must keep each current glyph exactly once"


@pytest.mark.parametrize(
    "text", ["", "unknown", "A\x00", "A\u00a0B", "A\u2028B", "A\u2029B"]
)
def test_refuse_empty_unknown_and_lossy_text(text: str) -> None:
    with pytest.raises(ValueError):
        load().insert_names(("A", "B"), text, "B")


@pytest.mark.parametrize("names,anchor", [((), "A"), (("A", "A"), "A"), (("A",), "B")])
def test_refuse_invalid_font_order(names: tuple, anchor: str) -> None:
    with pytest.raises(ValueError):
        load().insert_names(names, "A", anchor)


def test_encoding_exact_and_no_overwrite(tmp_path: Path) -> None:
    module = load()
    path = tmp_path / "order.enc"
    module.save_encoding(path, (".notdef", "A", "A.alt"))
    assert path.read_text() == (
        "%%FONTLAB ENCODING: -1; order\n%%GROUP:Custom\n.notdef\nA\nA.alt\n"
    ), "Use the native encoding reader's header and one name per line"
    with pytest.raises(FileExistsError):
        module.save_encoding(path, ("B",))
    assert path.read_text().endswith("A.alt\n"), "Keep existing files intact"


@pytest.mark.parametrize("name", ["A B", "%comment", "A\x00", "é", "A" * 512])
def test_unsupported_encoding_names_are_kept(name: str, tmp_path: Path) -> None:
    path = tmp_path / "mixed.enc"
    assert load().save_encoding(path, ("A", name, "B")) == (name,), (
        "Name every kept row"
    )
    assert path.read_text().splitlines()[2:] == ["A", "B"], "Other rows still save"
    with pytest.raises(ValueError, match="No supported"):
        load().save_encoding(tmp_path / "bad.enc", (name,))
    assert not (tmp_path / "bad.enc").exists(), "Do not create an empty encoding"


def test_encoding_names_use_each_file_stem(tmp_path: Path) -> None:
    module = load()
    for stem in ("first", "second", "épreuve"):
        path = tmp_path / (stem + ".enc")
        module.save_encoding(path, ("A",))
        assert (
            path.read_text(encoding="utf-8").splitlines()[0]
            == f"%%FONTLAB ENCODING: -1; {stem}"
        ), "Unique chooser names"


def test_capture_current_font_and_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    import fontlabapp.glyph_catalog as catalog
    import fontlabapp.layer_selection as selection

    originals = (catalog.capture, selection.capture)
    install_captures(monkeypatch, (("A", "", ""), ("B", "", "")), (NS(glyph_name="B"),))
    module = load()
    ticks = iter((10.0, 11.0, 12.0))
    monkeypatch.setattr(module, "monotonic", lambda: next(ticks))
    assert module.capture_order() == (("A", "B"), "B"), "Use the first selected glyph"
    deadlines = []
    for real, fake in zip(originals, (fake_catalog, fake_selection), strict=True):
        for args, kwargs in fake.calls:
            bound = inspect.signature(real).bind(*args, **kwargs)
            deadlines.append(bound.arguments["deadline"])
    assert len(deadlines) == 3 and all(isinstance(d, float) for d in deadlines), (
        "Give every capture a deadline"
    )
    assert fake_catalog.calls[0][1]["deadline"] == 12.0, "Fresh first catalog budget"
    assert fake_selection.calls[0][1]["deadline"] == 13.0, "Fresh selection budget"
    assert fake_catalog.calls[1][1]["deadline"] == 14.0, "Fresh second catalog budget"


def test_capture_refuses_no_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    install_captures(monkeypatch, (("A", "", ""),), ())
    with pytest.raises(ValueError, match="Select"):
        load().capture_order()


def test_widget_names_and_no_font_writes() -> None:
    tree = ast.parse(SCRIPT.read_text())
    reserved = {"render", "size", "layout", "update", "font", "move", "statusBar"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert not reserved.intersection(
                child.name for child in node.body if isinstance(child, ast.FunctionDef)
            ), "Do not shadow native widget methods"
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            assert node.attr not in reserved, "Do not shadow native widget attributes"
    assert "status.text" not in SCRIPT.read_text(), (
        "Never read the Qt status text property"
    )
    assert "notifyChangesApplied" not in SCRIPT.read_text(), (
        "File output must not edit the font"
    )


@pytest.mark.parametrize("clear_selection", [False, True])
def test_panel_preview_save_error_and_close(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, clear_selection: bool
) -> None:
    """Exercise panel actions against strict native-member and signal fakes."""
    import fly
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly module alias

    reserved = {"render", "size", "layout", "update", "font", "move", "statusBar"}

    class Widget:
        AcceptSave = 1

        def __init__(self, *args: Any) -> None:
            self.text_value = ""
            self.text_writes = 0
            self.clicked = NS(connect=lambda slot: setattr(self, "button_slot", slot))
            self.fileSelected = NS(
                connect=lambda slot: setattr(self, "file_slot", slot)
            )
            self.children = []
            if args and isinstance(args[0], Widget):
                args[0].children.append(self)

        def __setattr__(self, name: str, value: Any) -> None:
            assert name not in reserved, f"Native member collision: {name}"
            object.__setattr__(self, name, value)

        def setText(self, text: str) -> None:
            self.text_value = text
            self.text_writes += 1

        setPlainText = setText

        def toPlainText(self) -> str:
            return self.text_value

        def __getattr__(self, name: str) -> Any:
            assert name in {
                "setWindowTitle",
                "setMinimumWidth",
                "setWordWrap",
                "addWidget",
                "addLayout",
                "setPlaceholderText",
                "setReadOnly",
                "setAcceptMode",
                "setNameFilter",
                "setDefaultSuffix",
                "show",
                "close",
            }, f"Unknown Qt API: {name}"
            return lambda *args: None

    gui = NS(
        **dict.fromkeys(
            (
                "QDialog",
                "QVBoxLayout",
                "QLabel",
                "QPlainTextEdit",
                "QHBoxLayout",
                "QPushButton",
                "QFileDialog",
            ),
            Widget,
        )
    )
    monkeypatch.setitem(fly.__dict__, "qt", NS(QtGui=gui))
    monkeypatch.setattr(scripting, "show_script_dialog", fake_show)
    monkeypatch.setattr(scripting, "close_script_dialog", fake_close)
    module = load()
    names = tuple(f"g{i}" for i in range(250))
    install_captures(
        monkeypatch, tuple((n, "", "") for n in names), (NS(glyph_name="g1"),)
    )
    panel = module.main()
    panel.pasted_names.setPlainText("g249 unknown g2")
    order = panel.preview_order()
    assert order[:4] == ("g0", "g249", "g2", "g1"), "Preview must insert exact names"
    assert len(panel.order_preview.toPlainText().splitlines()) == 200, (
        "Bound display only"
    )
    panel.choose_file()
    assert len(panel._connections) == 4, "Three buttons and one owned file chooser"
    if clear_selection:
        fake_selection.result = NS(occurrences=())
    selection_reads = len(fake_selection.calls)
    panel.write_file(str(tmp_path / "full.enc"))
    assert len(fake_selection.calls) == selection_reads, (
        "Saving reads names without selection"
    )
    if clear_selection:
        with pytest.raises(ValueError, match="Select"):
            module.capture_order()
    assert len((tmp_path / "full.enc").read_text().splitlines()) == 252, (
        "Save all names"
    )
    panel.safe_action(lambda: panel.write_file(str(tmp_path / "full.enc")))
    assert "exists" in panel.status.text_value, "Report no-overwrite errors"
    fake_catalog.result = NS(rows=tuple((n, "", "") for n in (*names, "added")))
    panel.safe_action(lambda: panel.write_file(str(tmp_path / "stale.enc")))
    assert "reopen" in panel.status.text_value, "Refuse stale font output"
    assert not (tmp_path / "stale.enc").exists(), "Refuse before creating output"
    fake_catalog.result = NS(rows=tuple((n, "", "") for n in names))
    panel.pasted_names.setPlainText("é g2")
    panel.source_names = (*names, "é")
    writes_before = panel.status.text_writes
    panel.preview_order()
    assert panel.status.text_writes == writes_before + 1, "Set the complete status once"
    assert "kept 'é'" in panel.order_preview.toPlainText(), (
        "Show each non-ASCII kept row"
    )
    panel.source_names = names

    def unexpected() -> None:
        raise LookupError("unexpected button error")

    panel.safe_action = lambda action: unexpected()
    panel._connections[0][1]()
    assert "unexpected button error" in panel.status.text_value, (
        "Real guard must report unexpected exceptions visibly"
    )
    panel.closeEvent(None)
    assert panel.closed_children == (panel.file_chooser,), "Shared cleanup owns chooser"

    def timeout() -> None:
        raise TimeoutError("capture timed out")

    monkeypatch.setattr(module, "capture_order", timeout)
    failed_panel = module.main()
    assert failed_panel.status.text_value == "capture timed out", (
        "Contain capture errors"
    )
    failed_panel.safe_action(failed_panel.preview_order)
    assert "reopen" in failed_panel.status.text_value, (
        "Refuse incomplete source captures"
    )
