# this_file: tests/test_mark_colour_menu.py
"""Run the real facade through Fly and retain the exact original identity."""

import hashlib
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Names/Select Different Mark Colours.py"


@pytest.mark.parametrize("result", [(), ("a", "b")])
def test_menu_delegates_exact_original_action(monkeypatch, result):
    calls = []

    def select():
        calls.append(True)
        return result

    monkeypatch.setitem(
        sys.modules,
        "fly.ap.glyphs.selection.mark_colors",
        NS(select_different_mark_colours=select),
    )
    spec = importlib.util.spec_from_file_location("owned_mark_colour_menu", MENU)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main() == result and calls == [True]
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == [True, True]


def test_menu_provenance_keeps_source_and_denominator():
    records = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(r for r in records if r["key"] == "select_different_mark_colours")
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["source_sha256"]
        == "cd7e0618b70cc82ef6b0e8b67f575fd12a4f4660070bab49bd01f3cbccad852c"
    )
    assert row["source_path"] == "Labels/Select different colour.py"
    assert row["counted_in_130_sample_migration"] is False
    assert row["native_acceptance"] == "pending"
    assert "Rainer Erich Scheichelbauer" in (ROOT / "NOTICE").read_text()
    assert (
        (ROOT / "LICENSE")
        .read_text()
        .startswith("                                 Apache License")
    )
