# this_file: tests/test_text_filter.py
"""First-party menu and source-helper controls; reference bodies stay unread here."""

import ast
import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

from conftest import resolve_app_sources

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Proof/Text Filter.py"


def test_text_filter_menu_dispatch_is_lazy_and_uses_shared_fly_panel(monkeypatch):
    calls = []
    fly, ap, helper = (
        ModuleType(name) for name in ("fly", "fly.ap", "fly.ap.text_filter")
    )
    helper.show = lambda: calls.append("complete panel") or "panel"
    for module in (fly, ap, helper):
        monkeypatch.setitem(sys.modules, module.__name__, module)
    imported = runpy.run_path(str(MENU), run_name="inspection")
    assert calls == [] and imported["main"]() == "panel"
    assert calls == ["complete panel"]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == ["complete panel", "complete panel"]
    assert not any(
        isinstance(n, (ast.With, ast.Try, ast.For))
        for n in ast.parse(MENU.read_text()).body
    )


def test_text_filter_calls_actual_reviewed_host_free_filter(monkeypatch):
    source = resolve_app_sources(("text_filter",)) / "text_filter.py"
    spec = importlib.util.spec_from_file_location("owned_text_filter", source)
    helper = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, helper)
    spec.loader.exec_module(helper)
    assert helper.filter_text("A1é🙂 Z", "A-Zé🙂 ") == "Aé🙂 Z"
    assert helper.filter_text("a1b2", "a-z") == "ab"


def test_text_filter_provenance_is_separate_from_original_sample_denominator():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(row for row in rows if row["key"] == "text_filter")
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["source_sha256"]
        == "44e0ac6f376518937449bd92470683ffc45ed059e8ddeafb3d4c0518188c4d46"
    )
    assert row["native_acceptance"] == "pending" and row["license"] == "Apache-2.0"
    assert row["counted_in_130_sample_migration"] is False
