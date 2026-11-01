# this_file: tests/test_migration_history_sources.py
"""Historical-byte lookup respects the external archive and rejects corruption."""
import hashlib
import json
import pytest
import _migration_history as history


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    root, original, archive = (tmp_path / name for name in ("repo", "original", "archive"))
    for path in (root, original, archive):
        path.mkdir()
    source, rescued, payload = "examples/old.py", "rescued/old.py", b"# historical bytes\n"
    (root / "rescue-index.json").write_text(json.dumps({"preserved_sources": {source: {"path": rescued, "sha256": hashlib.sha256(payload).hexdigest()}}}))
    monkeypatch.setattr(history, "ROOT", root)
    monkeypatch.delenv("FONTLAB_PRESERVED_ROOT", raising=False)
    return root, original, archive, source, rescued, payload


def put(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


@pytest.mark.parametrize("route", ["original", "legacy", "external"])
def test_preserved_source_resolves_exact_bytes_for_each_layout(inputs, monkeypatch, route):
    root, original, archive, source, rescued, payload = inputs
    target = {"original": original / source, "legacy": root / rescued, "external": archive / rescued}[route]
    put(target, payload)
    if route == "external":
        monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(archive))
        put(original / source, b"wrong direct bytes")
    assert history.preserved_source(original, source) == target
    assert target.read_bytes() == payload


@pytest.mark.parametrize("route", ["original", "legacy", "external"])
def test_preserved_source_rejects_changed_original_bytes(inputs, monkeypatch, route):
    root, original, archive, source, rescued, _ = inputs
    target = {"original": original / source, "legacy": root / rescued, "external": archive / rescued}[route]
    put(target, b"changed")
    if route == "external":
        monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(archive))
    with pytest.raises(AssertionError, match=source):
        history.preserved_source(original, source)


def test_explicit_missing_archive_never_falls_back_to_another_copy(inputs, monkeypatch):
    root, original, archive, source, rescued, payload = inputs
    put(original / source, payload)
    put(root / rescued, payload)
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(archive))
    with pytest.raises(FileNotFoundError):
        history.preserved_source(original, source)
