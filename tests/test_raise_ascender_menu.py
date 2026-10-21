# this_file: tests/test_raise_ascender_menu.py
"""Practical one-category Fly facade, exact original attribution, no eager action."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Contours/Raise Ascender.py"


def test_menu_import_and_public_main_each_lazy_forward_once(monkeypatch):
    calls = []
    module = ModuleType("fly.ap.raise_ascender")
    module.show = lambda: calls.append(True) or "owned"
    monkeypatch.setitem(sys.modules, module.__name__, module)
    namespace = runpy.run_path(str(MENU))
    assert not calls
    assert namespace["main"]() == "owned"
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]


def test_original_scope_and_provenance_are_not_native_completion():
    row = next(
        row
        for row in json.loads((ROOT / "additional-tools.json").read_text())
        if row["key"] == "raise_ascender"
    )
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["source_sha256"]
        == "a6bba363ea8c22660f3f3a02f67a2cd14748afc7a683303c9acffacd85d671f2"
    )
    assert row["source_license"] == "MIT" and row["native_acceptance"] == "pending"
    assert row["counted_in_130_sample_migration"] is False
    assert "per-occurrence Undo" in row["scope"] and "incomplete" in row["scope"]
