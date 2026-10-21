# this_file: tests/test_text_holder_menu.py
"""Lazy public Fly facade and exact independently implemented source provenance."""

import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Utilities/Text Holder.py"


def test_menu_is_lazy_and_direct_and_script_paths_open_complete_app_editor(monkeypatch):
    calls = []
    result = object()
    monkeypatch.setitem(
        sys.modules, "fly.ap.text_holder", NS(show=lambda: calls.append(True) or result)
    )
    spec = importlib.util.spec_from_file_location("owned_text_holder", MENU)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert calls == [] and module.main() is result and calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]


def test_source_identity_no_licence_copy_and_goal_denominator_are_preserved():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(r for r in rows if r["key"] == "text_holder")
    assert (
        row["source_sha256"]
        == "182c1c2486d79729632ea08ddc45c4c3aab8ccb19508ddb0276498a43c8c1410"
    )
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["source_license"] == "not declared in inspected source tree"
        and row["source_body_redistributed"] is False
    )
    assert row["license"] == "Apache-2.0" and row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
