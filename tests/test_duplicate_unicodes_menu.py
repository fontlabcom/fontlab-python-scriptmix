# this_file: tests/test_duplicate_unicodes_menu.py
"""The complete cleanup menu is lazy and exactly source-pinned, not an archive dispatcher."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).parents[1]


def test_facade_invokes_shared_writer_only_when_run(monkeypatch):
    calls = []
    monkeypatch.setitem(
        sys.modules,
        "fly.ap.duplicate_unicodes",
        NS(show=lambda: calls.append("show") or "owned"),
    )
    module = runpy.run_path(str(ROOT / "Scripts/Names/Duplicate Unicodes.py"))
    assert not calls
    assert module["main"]() == "owned"
    runpy.run_path(
        str(ROOT / "Scripts/Names/Duplicate Unicodes.py"), run_name="__main__"
    )
    assert calls == ["show", "show"]


def test_full_original_provenance_and_rescued_source_are_retained():
    row = next(
        x
        for x in json.loads((ROOT / "additional-tools.json").read_text())
        if x["key"] == "names_duplicate_unicodes"
    )
    assert row["destination"] == "Scripts/Names/Duplicate Unicodes.py"
    assert row["app_minimum"] == "0.2.121.dev0"
    assert (
        row["native_acceptance"] == "pending"
        and row["counted_in_130_sample_migration"] is False
    )
    assert (
        row["source_sha256"]
        == "b42ab5f9a4bead19a4a0a042d9fe9fcffbfadfe650da6551b4f9ea3819ba865e"
    )
    assert (
        hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
        == row["destination_sha256"]
    )
