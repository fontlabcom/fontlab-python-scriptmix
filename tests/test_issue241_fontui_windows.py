# this_file: tests/test_issue241_fontui_windows.py
"""The TMetrics and TGlyph menu demos open one App fontui window each, lazily."""

import builtins
import hashlib
import html
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]

# script -> (App module under fly.ap, entry point it must call)
DEMOS = {
    "Scripts/Metrics/TMetrics Window.py": ("fontui.tmetrics", "show_tmetrics"),
    "Scripts/Contours/TGlyph Window.py": ("fontui.tglyph", "show_tglyph"),
}


@pytest.mark.parametrize("script", DEMOS)
def test_requirements_when_published_then_name_the_required_app_module(script):
    module = "fontlabapp." + DEMOS[script][0]
    page = str(Path(script).relative_to("Scripts").with_suffix("")).lower().replace(" ", "-")
    for relative in (
        script,
        f"src_docs/md/scripts/{page}.md",
        f"docs/scripts/{page}.html",
    ):
        text = html.unescape((ROOT / relative).read_text())
        assert "App>=1.2.0" not in text, f"{relative}: no unproved numeric floor"
        assert module in text, f"{relative}: name the App module this tool requires"
        assert hashlib.sha256((ROOT / script).read_bytes()).hexdigest() in text or relative == script
    row = next(r for r in json.loads((ROOT / "additional-tools.json").read_text()) if r["destination"] == script)
    assert "app_minimum" not in row, "These module requirements have no verified release floor"
    assert module in row["scope"]
    assert module in runpy.run_path(str(ROOT / script), run_name="inspection")["INSTALL_HINT"]
    for relative in ("README.md", "src_docs/md/install.md", "docs/install.html"):
        assert module in (ROOT / relative).read_text(), f"{relative}: retain the window exception"


def stub_entry(monkeypatch, module: str, entry: str) -> tuple[list, object]:
    """Install a fake App module; return its call log and the window it returns."""
    calls, window = [], object()
    fake = ModuleType("fly.ap." + module)
    setattr(fake, entry, lambda *args, **kwargs: calls.append((args, kwargs)) or window)
    monkeypatch.setitem(sys.modules, "fly.ap." + module, fake)
    return calls, window


def block_import(monkeypatch, prefix: str) -> None:
    """Make every import of ``prefix`` fail as it does when the package is missing."""
    real = builtins.__import__

    def fake(name, *args, **kwargs):
        if name.startswith(prefix):
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake)


@pytest.mark.parametrize("script", DEMOS)
def test_main_when_called_then_opens_the_window_with_defaults(monkeypatch, script):
    calls, window = stub_entry(monkeypatch, *DEMOS[script])
    namespace = runpy.run_path(str(ROOT / script), run_name="inspection")
    assert calls == [], "importing the script must not open a window"
    assert namespace["main"]() is window, "main returns the window the App opened"
    assert calls == [((), {})], "the current font and glyph come from the App defaults"


@pytest.mark.parametrize("script", DEMOS)
def test_script_when_run_as_main_then_opens_once(monkeypatch, script):
    calls, _ = stub_entry(monkeypatch, *DEMOS[script])
    runpy.run_path(str(ROOT / script), run_name="__main__")
    assert calls == [((), {})]


@pytest.mark.parametrize("script", DEMOS)
def test_main_when_app_missing_then_prints_install_hint_without_traceback(monkeypatch, capsys, script):
    namespace = runpy.run_path(str(ROOT / script), run_name="inspection")
    monkeypatch.delitem(sys.modules, "fly.ap." + DEMOS[script][0], raising=False)
    block_import(monkeypatch, "fly.ap")
    assert namespace["main"]() is None
    out = capsys.readouterr().out
    assert "fontlab-fontlabapp[fontport]" in out and "fontlab-fly" in out, out


@pytest.mark.parametrize("script", DEMOS)
def test_main_when_fontport_missing_then_prints_install_hint(monkeypatch, capsys, script):
    """An ImportError from the App module (as require_fontport raises) is reported."""
    module, _ = DEMOS[script]
    namespace = runpy.run_path(str(ROOT / script), run_name="inspection")
    monkeypatch.delitem(sys.modules, "fly.ap." + module, raising=False)
    real = builtins.__import__

    def fake(name, *args, **kwargs):
        if name == "fly.ap." + module:
            raise ImportError("needs fontlab-fontport; install it with: pip install 'fontlab-fontlabapp[fontport]'")
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake)
    assert namespace["main"]() is None
    assert "needs fontlab-fontport" in capsys.readouterr().out


@pytest.mark.parametrize("script", DEMOS)
def test_row_when_indexed_then_matches_the_final_script_bytes(script):
    rows = [r for r in json.loads((ROOT / "additional-tools.json").read_text()) if r["destination"] == script]
    assert len(rows) == 1, f"{script}: exactly one additional-tools row"
    row = rows[0]
    assert row["destination_sha256"] == hashlib.sha256((ROOT / script).read_bytes()).hexdigest()
    assert row["kind"] == "independent-original-workflow-implementation"
    assert row["native_acceptance"] == "pending" and row["license"] == "Apache-2.0"
    assert row["counted_in_130_sample_migration"] is False and row["source_body_redistributed"] is False


@pytest.mark.parametrize("script", DEMOS)
def test_module_level_when_parsed_then_imports_only_the_standard_library(script):
    import ast

    for node in ast.parse((ROOT / script).read_text(), feature_version=(3, 11)).body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            assert {n.split(".")[0] for n in names} <= sys.stdlib_module_names, f"{script}: lazy imports only"


@pytest.mark.parametrize("script", DEMOS)
def test_entry_point_when_app_scanned_then_it_is_defined(script):
    import ast

    from conftest import app_names_used, app_source_path, resolve_app_sources

    module, entry = DEMOS[script]
    assert app_names_used([ROOT / script]) == {"fly.ap." + module: {entry}}
    path = app_source_path(resolve_app_sources(), module)
    assert path.is_file(), f"App has no module fly.ap.{module} ({path})"
    defined = {n.name for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef)}
    assert entry in defined, f"{path} does not define {entry}"
