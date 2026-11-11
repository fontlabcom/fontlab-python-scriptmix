# this_file: tests/test_wp08_open_contours_menu.py
"""The S65 launcher opens the shared App shell lazily; the original menus are untouched."""

import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Reports/Open Contours App.py"
ORIGINALS = ["Open Contours"]


def stub(monkeypatch):
    calls, sentinel = [], object()
    fake = ModuleType("fly.ap.fontui.open_contours")
    fake.show = lambda *args: calls.append(args) or sentinel
    monkeypatch.setitem(sys.modules, fake.__name__, fake)
    return calls, sentinel


def test_main_when_called_then_opens_the_app_shell_once_and_import_is_inert(monkeypatch):
    calls, sentinel = stub(monkeypatch)
    namespace = runpy.run_path(str(SCRIPT), run_name="inspection")
    assert calls == []
    assert namespace["main"]() is sentinel and calls == [()]


def test_script_when_run_as_main_then_opens_once(monkeypatch):
    calls, _ = stub(monkeypatch)
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert calls == [()]


def test_main_when_app_refuses_then_error_propagates(monkeypatch):
    stub(monkeypatch)
    sys.modules["fly.ap.fontui.open_contours"].show = lambda: (_ for _ in ()).throw(
        RuntimeError("Open report windows on the main UI thread.")
    )
    with pytest.raises(RuntimeError, match="main UI thread"):
        runpy.run_path(str(SCRIPT), run_name="inspection")["main"]()


def test_original_menus_when_launcher_added_then_still_exist():
    assert all((ROOT / "Scripts/Reports" / (n + ".py")).is_file() for n in ORIGINALS)
