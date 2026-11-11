# this_file: tests/test_wp08_reference_image_menu.py
"""The S64 launcher opens the shared App image shell lazily; the original menu is untouched."""

import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Utilities/Reference Image Viewer App.py"
ORIGINAL = ROOT / "Scripts/Utilities/Reference Image Viewer.py"


def stub(monkeypatch):
    calls, sentinel = [], object()
    fake = ModuleType("fly.ap.fontui.reference_images")
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
    sys.modules["fly.ap.fontui.reference_images"].show = lambda: (_ for _ in ()).throw(
        RuntimeError("Open reference image viewers on the main UI thread.")
    )
    with pytest.raises(RuntimeError, match="main UI thread"):
        runpy.run_path(str(SCRIPT), run_name="inspection")["main"]()


def test_original_menu_when_s64_added_then_still_uses_the_unconsolidated_viewer():
    assert "qt.images.viewer.model" in ORIGINAL.read_text()
