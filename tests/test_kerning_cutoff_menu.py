# this_file: tests/test_kerning_cutoff_menu.py
"""Lazy public route, direct dispatch and truthful independent-source provenance."""

import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Kerning/Kerning Cutoff.py"


def test_lazy_public_route_preserves_complete_action_result(monkeypatch):
    calls = []
    result = {"Light": 1, "Bold": 0}
    monkeypatch.setitem(
        sys.modules,
        "fly.ap.kerning_cutoff",
        NS(run=lambda: calls.append(True) or result),
    )
    spec = importlib.util.spec_from_file_location("owned_kerning_cutoff", MENU)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert calls == []
    assert module.main() is result and calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]


def test_exact_source_pin_without_original_licence_or_acceptance_claim():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(row for row in rows if row["key"] == "kerning_cutoff")
    assert (
        row["source_sha256"]
        == "b77e6799e748121e751f63ad01e8c0d5da881a71c4378684c92d45626636f8d5"
    )
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert row["source_license"] == "not declared in inspected source tree"
    assert row["source_body_redistributed"] is False
    assert row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
