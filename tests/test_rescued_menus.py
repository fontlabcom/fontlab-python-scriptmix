# this_file: tests/test_rescued_menus.py
"""Keep every unported source while excluding archived dispatchers from menus."""

import hashlib
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
INDEX = json.loads((ROOT / "rescue-index.json").read_text())
MENUS = INDEX["menus"]


@pytest.mark.parametrize("entry", MENUS, ids=lambda row: row["menu"])
def test_unported_source_is_preserved_without_an_active_dispatcher(entry):
    target = ARCHIVE / entry["target"]
    assert target.is_file(), "Every unfinished port retains its original source"
    assert hashlib.sha256(target.read_bytes()).hexdigest() == entry["target_sha256"]
    assert not (ROOT / entry["menu"]).exists(), "An archived launcher is not a practical port"


def test_complete_preserved_inventory_stays_unchanged():
    assert len(MENUS) == INDEX["new_menu_count"] == 61
    assert len({row["menu"] for row in MENUS}) == 61
    assert len(INDEX["preserved_sources"]) == 69
    for row in INDEX["preserved_sources"].values():
        target = ARCHIVE / row["path"]
        assert hashlib.sha256(target.read_bytes()).hexdigest() == row["sha256"]
