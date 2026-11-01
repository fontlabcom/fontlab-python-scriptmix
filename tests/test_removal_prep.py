# this_file: tests/test_removal_prep.py
"""Absent external archives skip byte audits; partial restores still fail."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from conftest import original_source

ROOT = Path(__file__).parents[1]
SOURCE, RECORD = next(iter(json.loads((ROOT / "rescue-index.json").read_text())["preserved_sources"].items()))


def test_original_source_when_external_archive_absent_then_clear_skip(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(tmp_path))
    with pytest.raises(pytest.skip.Exception, match="External historical sources absent"):
        original_source(ROOT, SOURCE)


def test_original_source_when_partial_archive_then_missing_file_fails(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(tmp_path))
    (tmp_path / "rescued").mkdir()
    with pytest.raises(AssertionError, match="Missing requested original"):
        original_source(ROOT, SOURCE)


def test_original_source_when_external_file_exists_then_resolves_only_that_file(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(tmp_path))
    target = tmp_path / RECORD["path"]
    target.parent.mkdir(parents=True)
    target.write_bytes(b"owned audit fixture")
    assert original_source(ROOT, SOURCE) == target, "The override must never fall back to a canonical checkout"


def test_original_source_when_override_has_no_record_then_refuses_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(tmp_path))
    with pytest.raises(AssertionError, match="No historical source record"):
        original_source(ROOT, "unknown/original.py")


def test_archive_when_one_file_deleted_and_one_corrupted_then_reports_both(tmp_path, monkeypatch):
    import test_rescued_menus as audit

    pristine = tmp_path / "pristine"
    records = []
    for name in ("missing.py", "corrupted.py"):
        relative = f"rescued/samples/{name}"
        source = pristine / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"# owned archive regression fixture\n")
        records.append({"target": relative, "target_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    archive = tmp_path / "copy"
    shutil.copytree(pristine, archive)
    monkeypatch.setattr(audit, "MENUS", records)
    monkeypatch.setattr(audit, "INDEX", {"preserved_sources": {}})
    audit.test_external_rescued_source_bytes_match_records(archive)
    (archive / records[0]["target"]).unlink()
    (archive / records[1]["target"]).write_bytes(b"corrupted copy\n")
    with pytest.raises(AssertionError) as failure:
        audit.test_external_rescued_source_bytes_match_records(archive)
    message = str(failure.value)
    assert "Missing requested archived original: rescued/samples/missing.py" in message
    assert "Source hash mismatch: rescued/samples/corrupted.py" in message
