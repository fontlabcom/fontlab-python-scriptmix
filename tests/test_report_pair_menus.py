# this_file: tests/test_report_pair_menus.py
"""Complete lazy dispatch and pinned originals; never execute third-party code."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parents[1]


@pytest.mark.parametrize(
    "title,key",
    [
        ("Master Node Compatibility Report", "master_node_report"),
        ("Dump to Svg Path Commands", "svg_path_commands"),
    ],
)
def test_menus_when_inspected_then_lazy_and_when_run_then_shared_show(
    monkeypatch, title, key
):
    calls = []
    for name in ("fly", "fly.ap"):
        mod = ModuleType(name)
        mod.__path__ = []
        monkeypatch.setitem(sys.modules, name, mod)
    mod = ModuleType("fly.ap." + key)
    mod.show = lambda: calls.append(key)
    monkeypatch.setitem(sys.modules, mod.__name__, mod)
    path = ROOT / f"Scripts/Reports/{title}.py"
    loaded = runpy.run_path(str(path), run_name="inspection")
    assert calls == []
    loaded["main"]()
    assert calls == [key]
    calls.clear()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [key]
    row = next(
        r
        for r in json.loads((ROOT / "additional-tools.json").read_text())
        if r["key"] == key
    )
    assert row["destination_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert (
        row["native_acceptance"] == "pending"
        and row["counted_in_130_sample_migration"] is False
    )
