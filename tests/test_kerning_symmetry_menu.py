# this_file: tests/test_kerning_symmetry_menu.py
"""Exact menu/provenance contract; actual Fly and writer route checked separately."""

import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Kerning/Symmetry.py"


def test_menu_import_has_no_action_and_both_entry_routes_forward_once(monkeypatch):
    calls = []
    alias = ModuleType("fly.ap.kerning_symmetry")
    alias.show = lambda: calls.append(True) or "owned-result"
    monkeypatch.setitem(sys.modules, alias.__name__, alias)
    spec = importlib.util.spec_from_file_location("symmetry_menu", MENU)
    menu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(menu)
    assert not calls
    assert menu.main() == "owned-result" and calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]


def test_exact_unlicensed_original_attribution_and_new_menu_hash():
    row = next(
        row
        for row in json.loads((ROOT / "additional-tools.json").read_text())
        if row["key"] == "kerning-symmetry"
    )
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["source_sha256"]
        == "6716be62ec46b469cab8959816a3a18def5addb26a9d3162e7b6a47ce217e36c"
    )
    assert row["source_license"] == "not declared in inspected source tree"
    assert row["source_body_redistributed"] is False
    assert row["native_acceptance"] == "pending"
    assert (
        MENU.read_text().splitlines()[0] == "# this_file: Scripts/Kerning/Symmetry.py"
    )
