# this_file: tests/test_fontui_master_width_comparison_menu.py
"""The actual menu uses the same real capture-once entry acceptance."""
import importlib
from pathlib import Path
import sys

import pytest
from conftest import resolve_app_sources
APP_SOURCE = resolve_app_sources(("fontui.master_width_comparison",))
APP_TESTS = APP_SOURCE.parents[1] / "tests"
sys.path.insert(0, str(APP_TESTS))
try:
    importlib.import_module("_feature_source_qt")
    from test_fontui_master_width_comparison_demo import (
        actual_qt as _qt_fixture, native_model as _native_fixture,
        dispatch_entry, cold_import)
finally:
    sys.path.pop(0)
actual_qt, native_model = _qt_fixture, _native_fixture
del _qt_fixture, _native_fixture
ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "Scripts/Font UI Lab/Master Width Comparison.py"


@pytest.mark.parametrize("dispatch", ["main", "script", "none"])
def test_menu_when_invoked_then_actual_capture_once_comparison(actual_qt, native_model, monkeypatch, dispatch):
    dispatch_entry(ENTRY, actual_qt, native_model, monkeypatch, dispatch)


def test_menu_when_host_unavailable_then_cold_import():
    cold_import(APP_SOURCE / "fontui/master_width_comparison.py", ENTRY)
