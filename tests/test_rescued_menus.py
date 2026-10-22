# this_file: tests/test_rescued_menus.py
"""Keep historical source identities while excluding archived dispatchers from menus."""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
INDEX = json.loads((ROOT / "rescue-index.json").read_text())
MENUS = INDEX["menus"]


@pytest.mark.parametrize("entry", MENUS, ids=lambda row: row["menu"])
def test_historical_source_is_recorded_without_an_active_dispatcher(entry):
    assert entry["target"].startswith("rescued/samples/")
    assert len(entry["target_sha256"]) == 64
    assert set(entry["target_sha256"]) <= set("0123456789abcdef")
    candidates = {r.get("rescued_original_menu"): r for r in json.loads((ROOT / "additional-tools.json").read_text()) if r.get("rescued_original_menu")}
    if entry["menu"] in candidates:
        candidate = candidates[entry["menu"]]
        assert candidate["destination"] == entry["menu"]
        assert candidate["source_sha256"] == entry["target_sha256"]
        assert candidate["native_acceptance"] == "pending"
        assert candidate["counted_in_130_sample_migration"] is False
        assert candidate["kind"] == "complete-original-writer-candidate"
    else:
        assert not (ROOT / entry["menu"]).exists(), "An archived launcher is not a practical port"


def test_complete_preserved_inventory_stays_unchanged():
    assert len(MENUS) == INDEX["new_menu_count"] == 61
    assert len({row["menu"] for row in MENUS}) == 61
    assert len(INDEX["preserved_sources"]) == 69
    identities = {key: INDEX[key] for key in ("menus", "preserved_sources")}
    assert hashlib.sha256(json.dumps(identities, sort_keys=True).encode()).hexdigest() == "49b44b74e03cf0c8a624d70cc4f63ae4d3400d0b77d27ff994648fd521ac83f0", "All 130 historical path/hash identities must stay unchanged"
    migration = json.loads((ROOT / "migration.json").read_text())
    assert {row["source"]: row["source_sha256"] for row in migration} == {
        source: row["sha256"] for source, row in INDEX["preserved_sources"].items()
    }, "Migration and rescue records must name the same 69 source identities"


def test_external_rescued_source_bytes_match_records(rescued_source_root):
    rows = [{"path": row["target"], "sha256": row["target_sha256"]} for row in MENUS]
    rows += list(INDEX["preserved_sources"].values())
    failures = []
    for row in rows:
        target = rescued_source_root / row["path"]
        if not target.is_file():
            failures.append(f"Missing requested archived original: {row['path']}")
            continue
        if hashlib.sha256(target.read_bytes()).hexdigest() != row["sha256"]:
            failures.append(f"Source hash mismatch: {row['path']}")
    assert not failures, "External source-byte audit failed:\n" + "\n".join(failures)
