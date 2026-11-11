# this_file: tests/test_wp08_retirement_evidence.py
"""Retired product decisions retain exact source data and behavioral obligations."""

import hashlib
import json
from pathlib import Path

import pytest

from menu_layout import source_bytes

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("path", [
    "Scripts/Reports/Event Log.py",
    "Scripts/Utilities/Find Font Files.py",
])
def test_retirement_when_documented_then_source_and_oracles_are_preserved(path):
    records = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
    record = next(row for row in records if row["source"]["path"] == path)
    raw = source_bytes(ROOT, record["source"], committed=True)
    assert hashlib.sha256(raw).hexdigest() == record["source"]["sha256"]
    assert b"SPDX-License-Identifier: Apache-2.0" in raw
    assert record["disposition"] == "retired"
    assert record["acceptance"]["behavior_parity"] is False
    document = (ROOT / "src_docs/md/retirement-decisions.md").read_text()
    assert path in document and record["source"]["sha256"] in document
    assert record["source"]["commit"] in document
    assert "tests/test_event_log.py" in document
    assert "tests/test_issue208_app_reach_tools.py" in document
