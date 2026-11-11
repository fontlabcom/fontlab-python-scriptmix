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


def test_previous_payload_when_current_menu_removed_then_recovers_archived_header(tmp_path, monkeypatch):
    import menu_layout

    destination = "Scripts/Contours/One.py"
    payload = b"# this_file: Scripts/Contours/One.py\n# FLM: Contours One\nvalue=1\n"
    digest = hashlib.sha256(payload).hexdigest()
    (tmp_path / "menu-consolidations.json").write_text(json.dumps({"transitions": [
        {"source": {"path": destination, "commit": "a" * 40, "sha256": digest},
         "acceptance": {"state": "implemented"}},
    ]}))
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / (digest + ".bin")).write_bytes(payload)
    monkeypatch.setenv("FONTLAB_MENU_ARCHIVE", str(archive))

    def no_git(*args, **kwargs):
        raise FileNotFoundError("Git unavailable")

    monkeypatch.setattr(menu_layout.subprocess, "run", no_git)
    expected = payload.replace(b"Contours", b"Outlines")
    assert history.previous_payload("Scripts/Outlines/One.py", tmp_path) == expected
    assert history.before_contours_rename([
        {"destination": destination, "destination_sha256": digest},
    ], tmp_path) == [{
        "destination": "Scripts/Outlines/One.py",
        "destination_sha256": hashlib.sha256(expected).hexdigest(),
    }]
