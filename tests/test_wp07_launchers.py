# this_file: tests/test_wp07_launchers.py
"""The nine identity/feature studio menus reach the tabbed App tools lazily; the consolidated originals are retired."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUDIOS = {'Feature Authoring': 'feature_authoring', 'Feature Explorer': 'feature_explorer', 'Nastaliq Connections': 'nastaliq_connections', 'Font Identity': 'font_identity', 'Encoding and Order': 'encoding_order', 'Glyph Identity': 'glyph_identity', 'Glyph Labels': 'glyph_labels', 'Glyph Browser': 'glyph_browser', 'Character Consistency': 'character_consistency'}
ROWS = [row for row in json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
        if row["destination"] and Path(row["destination"]["path"]).stem in STUDIOS]
ROUTES = [(path, STUDIOS[Path(path).stem], None)
          for path in sorted({row["destination"]["path"] for row in ROWS})]


@pytest.mark.parametrize("path,studio,tab", ROUTES)
def test_menu_when_imported_then_lazy_and_when_run_then_exact_tab(monkeypatch, path, studio, tab):
    calls = []
    def show(**kwargs):
        calls.append(kwargs)
        return "owner"
    monkeypatch.setitem(sys.modules, "fly.ap.studios." + studio + ".app", SimpleNamespace(show=show))
    module = runpy.run_path(str(ROOT / path))
    assert calls == []
    assert module["main"]() == "owner"
    runpy.run_path(str(ROOT / path), run_name="__main__")
    assert calls == [{}] * 2


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["source"]["path"])
def test_old_menu_when_consolidated_then_file_retired_and_studio_tab_named(row):
    assert not (ROOT / row["source"]["path"]).exists()
    assert (ROOT / row["destination"]["path"]).is_file() and row["destination"]["tab"]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["source"]["path"])
def test_transition_when_implemented_then_current_destination_hash_and_native_hold(row):
    assert row["acceptance"]["state"] == "implemented"
    assert row["acceptance"]["native"] is False
    assert row["acceptance"]["behavior_parity"] is False
    assert hashlib.sha256((ROOT / row["destination"]["path"]).read_bytes()).hexdigest() == row["destination"]["sha256"]
    assert "tests/test_wp07_launchers.py" in row["test_routes"]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["source"]["path"])
def test_old_route_when_consolidated_then_exact_historical_bytes_remain_available(row):
    from menu_layout import source_bytes

    source = source_bytes(ROOT, row["source"], committed=True)
    assert hashlib.sha256(source).hexdigest() == row["source"]["sha256"]
    assert ("# this_file: " + row["source"]["path"]).encode() in source.splitlines()[:5]
