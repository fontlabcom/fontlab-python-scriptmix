# this_file: tests/test_wp08_context_menu.py
"""Candidate menus retain pending provenance and lazy Context Proof dispatch."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("route", ["inspection", "__main__"])
def test_context_menu_when_invoked_then_dispatches_once(monkeypatch, route):
    module = ModuleType("fly.ap.studios.proof_studio.practical")
    calls = []
    module.show_context = lambda: calls.append("show")
    monkeypatch.setitem(sys.modules, module.__name__, module)
    namespace = runpy.run_path(
        str(ROOT / "Scripts/Proof/Context Proof.py"), run_name=route
    )
    if route == "inspection":
        assert calls == []
        namespace["main"]()
    assert calls == ["show"]


def test_candidates_when_indexed_then_do_not_promote_committed_transitions():
    ledger = json.loads((ROOT / "menu-consolidations.json").read_text())
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    candidates = ledger["candidates"]
    assert {row["path"] for row in candidates} == {
        "Scripts/Proof/Context Proof.py", "Scripts/Reports/Font Audit.py",
        "Scripts/Utilities/Reference Image Viewer App.py",
        "Scripts/Reports/Geometry Audit.py",
        "Scripts/Reports/Master Structure Audit.py",
        "Scripts/Reports/Font Revision Comparison.py", "Scripts/Reports/Metric Reports.py", "Scripts/Reports/Open Contours App.py", "Scripts/Reports/Nodes Near Zones App.py",
    }
    assert len(candidates) == 9
    assert ledger["source_count"] == len(ledger["transitions"]) == 279
    assert ledger["source_commit"] == "8022be9c4fc59e87bfcb8ca21724be55ea79ebb5"
    for candidate in candidates:
        row, = [row for row in rows if row["destination"] == candidate["path"]]
        digest = hashlib.sha256((ROOT / candidate["path"]).read_bytes()).hexdigest()
        assert digest == candidate["sha256"] == row["destination_sha256"]
        assert candidate["state"] == "candidate"
        assert candidate["containing_commit"] is None
        assert candidate["behavior_parity"] is candidate["native"] is False
        assert candidate["test_routes"]
        assert all((ROOT / path).is_file() for path in candidate["test_routes"])
        assert row["kind"] == "candidate-consolidation"
        assert row["native_acceptance"] == "pending"
        assert row["counted_in_130_sample_migration"] is False
        assert row["source_body_redistributed"] is False
        assert "reviewed commit" in row["provenance_pending"]
        assert "source_url" not in row and "app_minimum" not in row
