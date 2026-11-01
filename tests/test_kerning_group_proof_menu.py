# this_file: tests/test_kerning_group_proof_menu.py
"""Complete facade delegation and original/source redistribution disposition."""

import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Kerning/Same Kerning Groups.py"


@pytest.mark.parametrize("result", [None, ("current", "left.peer", "right.peer")])
def test_facade_direct_and_script_paths_use_shared_action(monkeypatch, result):
    calls = []

    def run():
        calls.append(True)
        return result

    monkeypatch.setitem(sys.modules, "fly.ap.kerning_group_proof", NS(run=run))
    spec = importlib.util.spec_from_file_location("owned_same_groups", MENU)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() == result and calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]


def test_source_identity_licence_disposition_and_denominator_are_explicit():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(r for r in rows if r["key"] == "same_kerning_groups")
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["source_sha256"]
        == "fc2e6b144d53388b7105498f9debf55edf2c65986c3f559683b106623fbb9544"
    )
    assert (
        row["source_body_redistributed"] is False
        and row["source_license"] == "not declared in inspected source tree"
    )
    assert (
        row["license"] == "Apache-2.0"
        and row["counted_in_130_sample_migration"] is False
    )
    assert row["native_acceptance"] == "pending"
    assert "Reza Bohloul" in (ROOT / "NOTICE").read_text()
