# this_file: tests/test_crossfont_anchors_menu.py
"""Actual Fly facade entry and explicit independent source/licence provenance."""

import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MENU = ROOT / "Scripts/Anchors/Copy Anchors Between Fonts.py"


def test_crossfont_anchor_menu_calls_actual_lazy_fly_facade(monkeypatch):
    import fontlabapp.crossfont_anchors as api

    calls = []
    monkeypatch.setattr(api, "show", lambda: calls.append("complete dialog") or "owned")
    namespace = runpy.run_path(str(MENU))
    assert (
        calls == [] and namespace["main"]() == "owned" and calls == ["complete dialog"]
    )
    runpy.run_path(str(MENU), run_name="__main__")
    assert calls == ["complete dialog", "complete dialog"]


def test_crossfont_provenance_pins_entire_original_and_mpl_without_body_redistribution():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    row = next(r for r in rows if r["key"] == "crossfont_anchors")
    assert (
        row["source_sha256"]
        == "60e2fd0c872276538d8d21a443a06e9a0282ada5b8a90b96c81da8e52bf19cdf"
    )
    assert (
        row["source_license"] == "MPL-2.0" and row["source_body_redistributed"] is False
    )
    assert row["destination_sha256"] == hashlib.sha256(MENU.read_bytes()).hexdigest()
    assert (
        row["native_acceptance"] == "pending"
        and row["counted_in_130_sample_migration"] is False
    )
    assert "Mozilla Public License Version 2.0" in (ROOT / "NOTICE").read_text()
