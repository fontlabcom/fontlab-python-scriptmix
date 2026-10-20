# this_file: tests/test_layer_compatibility.py
"""Run only first-party menu/core code; source originals remain read-only."""

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
MENU = ROOT / "Scripts/Reports/Why You Not Compatible.py"


def test_menu_when_imported_then_lazy_and_exact_shared_dispatch(monkeypatch):
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.layer_compatibility"):
        mod = ModuleType(name)
        monkeypatch.setitem(sys.modules, name, mod)
    sys.modules["fly.ap.layer_compatibility"].show = lambda: calls.append("show")
    ns = runpy.run_path(str(MENU), run_name="inspection")
    assert not calls
    ns["main"]()
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == ["show", "show"]
    tree = ast.parse(MENU.read_text(), feature_version=(3, 11))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    assert main.returns.value is None


def test_actual_core_when_later_path_differs_after_anchors_then_full_report(
    monkeypatch,
):
    p = resolve_app_sources(("layer_compatibility",)) / "layer_compatibility.py"
    spec = importlib.util.spec_from_file_location("owned_compatibility_core", p)
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, mod)
    spec.loader.exec_module(mod)
    layers = (
        mod.Layer("A", (("line",),), frozenset({"top"})),
        mod.Layer("B", (("line",),)),
        mod.Layer("C", (("curve",),)),
    )
    text = mod.render((mod.GlyphLayers("second", layers),))
    assert "anchors differ:" in text and "B has line" in text and "C has curve" in text


def test_new_provenance_when_added_then_hash_license_and_original_denominator():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(v for v in rows if v["key"] == "layer_compatibility")
    assert row["license"] == "MIT" and row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
