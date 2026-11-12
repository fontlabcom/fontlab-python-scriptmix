# this_file: tests/test_issue241_fontui_windows.py
"""The TMetrics and TGlyph menu demos open one App fontui window each, lazily."""

import builtins
import hashlib
import html
import json
import runpy
import sys
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]

# script -> (App module under fly.ap, entry point it must call)
DEMOS = {
    "Scripts/Metrics/TMetrics Window.py": ("fontui.tmetrics", "show_tmetrics"),
    "Scripts/Contours/TGlyph Window.py": ("fontui.tglyph", "show_tglyph"),
}


def active_path(script):
    return ROOT / ("Scripts/Metrics/Spacing Studio.py" if "TMetrics Window" in script else script)


def active_entry(script):
    return ("studios.spacing_studio", "show") if "TMetrics Window" in script else DEMOS[script]


def historical_bytes(script):
    import importlib.util

    spec = importlib.util.spec_from_file_location("wp03_menu_layout", ROOT / "menu_layout.py")
    resolver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resolver)
    rows = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
    source = next(row["source"] for row in rows if row["source"]["path"] == script)
    return resolver.source_bytes(ROOT, source)


@pytest.mark.parametrize("script", DEMOS)
def test_requirements_when_published_then_name_the_required_app_module(script):
    module = "fontlabapp." + DEMOS[script][0]
    page = str(Path(script).relative_to("Scripts").with_suffix("")).lower().replace(" ", "-")
    for relative in (
        script,
        f"src_docs/md/scripts/{page}.md",
        f"docs/scripts/{page}.html",
    ):
        if relative == script:
            text = historical_bytes(script).decode()
        elif "TMetrics Window" in script and relative.endswith(".md"):
            # The active catalogue removes absorbed menus. Preserve the exact
            # original documentation oracle at its recorded source commit.
            transitions = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
            source = next(row["source"] for row in transitions if row["source"]["path"] == script)
            text = subprocess.check_output(["git", "show", source["commit"] + ":" + relative], cwd=ROOT).decode()
        else:
            text = (ROOT / relative).read_text()
        text = html.unescape(text)
        assert "App>=1.2.0" not in text, f"{relative}: no unproved numeric floor"
        assert module in text, f"{relative}: name the App module this tool requires"
        assert hashlib.sha256(historical_bytes(script)).hexdigest() in text or relative == script
    row = next(r for r in json.loads((ROOT / "additional-tools.json").read_text()) if r["destination"] == script)
    assert "app_minimum" not in row, "These module requirements have no verified release floor"
    assert module in row["scope"]
    assert module in runpy.run_path(str(active_path(script)), run_name="inspection")["INSTALL_HINT"]
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
    calls, window = stub_entry(monkeypatch, *active_entry(script))
    namespace = runpy.run_path(str(active_path(script)), run_name="inspection")
    assert calls == [], "importing the script must not open a window"
    assert namespace["main"]() is window, "main returns the window the App opened"
    assert calls == [((), {})], "the current font and glyph come from the App defaults"


@pytest.mark.parametrize("script", DEMOS)
def test_script_when_run_as_main_then_opens_once(monkeypatch, script):
    calls, _ = stub_entry(monkeypatch, *active_entry(script))
    runpy.run_path(str(active_path(script)), run_name="__main__")
    assert calls == [((), {})]


@pytest.mark.parametrize("script", DEMOS)
def test_main_when_app_missing_then_prints_install_hint_without_traceback(monkeypatch, capsys, script):
    namespace = runpy.run_path(str(active_path(script)), run_name="inspection")
    monkeypatch.delitem(sys.modules, "fly.ap." + active_entry(script)[0], raising=False)
    block_import(monkeypatch, "fly.ap")
    assert namespace["main"]() is None
    out = capsys.readouterr().out
    assert "fontlab-fontlabapp[fontport]" in out and "fontlab-fly" in out, out


@pytest.mark.parametrize("script", DEMOS)
def test_main_when_fontport_missing_then_prints_install_hint(monkeypatch, capsys, script):
    """An ImportError from the App module (as require_fontport raises) is reported."""
    module, _ = active_entry(script)
    namespace = runpy.run_path(str(active_path(script)), run_name="inspection")
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
    assert row["destination_sha256"] == hashlib.sha256(historical_bytes(script)).hexdigest()
    assert row["kind"] == "independent-original-workflow-implementation"
    assert row["native_acceptance"] == "pending" and row["license"] == "Apache-2.0"
    assert row["counted_in_130_sample_migration"] is False and row["source_body_redistributed"] is False


@pytest.mark.parametrize("script", DEMOS)
def test_module_level_when_parsed_then_imports_only_the_standard_library(script):
    import ast

    for node in ast.parse(active_path(script).read_text(), feature_version=(3, 11)).body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            assert {n.split(".")[0] for n in names} <= sys.stdlib_module_names, f"{script}: lazy imports only"


@pytest.mark.parametrize("script", DEMOS)
def test_entry_point_when_app_scanned_then_it_is_defined(script):
    import ast

    from conftest import app_names_used, app_source_path, resolve_app_sources

    module, entry = active_entry(script)
    assert app_names_used([active_path(script)]) == {"fly.ap." + module: {entry}}
    path = app_source_path(resolve_app_sources(), module)
    if not path.is_file():
        path = path.with_suffix("") / "__init__.py"
    assert path.is_file(), f"App has no module fly.ap.{module} ({path})"
    defined = {n.name for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef)}
    assert entry in defined, f"{path} does not define {entry}"
