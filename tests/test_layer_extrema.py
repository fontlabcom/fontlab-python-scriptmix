# this_file: tests/test_layer_extrema.py
"""Only first-party menu wrappers and reviewed helper code execute here."""

import ast
import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest
from conftest import resolve_app_sources

ROOT = Path(__file__).resolve().parents[1]
MENUS = {"current": "Tallest and Shortest.py", "all": "Highest & Lowest Glyphs.py"}


@pytest.mark.parametrize("mode", ["current", "all"])
def test_each_menu_uses_its_complete_shared_scope_without_eager_host_access(
    monkeypatch, mode
):
    calls = []
    fly, ap, helper = (
        ModuleType(name) for name in ("fly", "fly.ap", "fly.ap.extrema_proof")
    )
    helper.run = lambda mode: calls.append(mode)
    helper.show_all = lambda: calls.append("all")
    for module in (fly, ap, helper):
        monkeypatch.setitem(sys.modules, module.__name__, module)
    path = ROOT / "Scripts/Proof" / MENUS[mode]
    imported = runpy.run_path(str(path), run_name="inspection")
    assert calls == []
    imported["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [mode, mode]
    assert len(ast.parse(path.read_text()).body) < 6


def test_both_actual_helper_winners_keep_first_zero_and_nonmaster_layer(monkeypatch):
    source = resolve_app_sources(("layer_extrema",)) / "layer_extrema.py"
    spec = importlib.util.spec_from_file_location("owned_layer_extrema", source)
    helper = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, helper)
    spec.loader.exec_module(helper)
    rows = (
        helper.LayerExtent("a", "Thin", -10, 0),
        helper.LayerExtent("b", "Sketch", -20, -1),
    )
    result = helper.choose(rows)
    assert result.layers == (("a", "Thin"), ("b", "Sketch"))


def test_new_extrema_provenance_preserves_the_original_sample_denominator():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    new = [
        row
        for row in rows
        if row["kind"] == "practical-layer-extrema-workflow-candidate"
    ]
    assert len(new) == 2 and {row["license"] for row in new} == {"MIT", "Apache-2.0"}
    for row in new:
        assert (
            row["destination_sha256"]
            == hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
        )
        assert (
            row["native_acceptance"] == "pending"
            and row["counted_in_130_sample_migration"] is False
        )
