# this_file: tests/test_menu_layout.py
"""Keep immutable release metadata while validating only reviewed header moves."""

import hashlib
import json

import pytest
from menu_layout import current_rows, released_bytes


def fixture(tmp_path):
    old = b"# this_file: Scripts/Old/One.py\n# license\n# FLM: Old\nvalue=1\n"
    new = old.replace(b"Scripts/Old/", b"Scripts/New/").replace(
        b"# FLM: Old", b"# FLM: New"
    )

    def sha(value):
        return hashlib.sha256(value).hexdigest()

    row = {
        "destination": "Scripts/Old/One.py",
        "destination_sha256": sha(old),
        "source_sha256": "a" * 64,
    }
    move = {
        "original": row["destination"],
        "destination": "Scripts/New/One.py",
        "original_sha256": sha(old),
        "destination_sha256": sha(new),
        "original_header": b"".join(old.splitlines(keepends=True)[:3]).decode(),
        "destination_header": b"".join(new.splitlines(keepends=True)[:3]).decode(),
    }
    path = tmp_path / move["destination"]
    path.parent.mkdir(parents=True)
    path.write_bytes(new)
    (tmp_path / "migration.json").write_text(json.dumps([row]))
    (tmp_path / "menu-moves.json").write_text(json.dumps({"moves": [move]}))
    return old, new, row, move, path


def test_move_retains_exact_historical_bytes_rows_and_actual_destination(tmp_path):
    old, new, row, move, path = fixture(tmp_path)
    before = (tmp_path / "migration.json").read_bytes()
    assert released_bytes(tmp_path, row) == old
    assert current_rows(tmp_path) == [
        {
            **row,
            "destination": move["destination"],
            "destination_sha256": move["destination_sha256"],
        }
    ]
    assert (
        path.read_bytes() == new
        and (tmp_path / "migration.json").read_bytes() == before
    )


@pytest.mark.parametrize(
    "failure",
    ["row_hash", "new_hash", "prefix", "body", "unknown", "escape", "duplicate"],
)
def test_invalid_or_non_header_change_is_rejected(tmp_path, failure):
    _old, new, _row, move, path = fixture(tmp_path)
    if failure == "row_hash":
        move["original_sha256"] = "b" * 64
    if failure == "new_hash":
        move["destination_sha256"] = "b" * 64
    if failure == "prefix":
        move["destination_header"] = "wrong"
    if failure == "body":
        path.write_bytes(new.replace(b"value=1", b"value=2"))
        move["destination_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    if failure == "unknown":
        move["original"] = "Scripts/Other/Absent.py"
    if failure == "escape":
        move["destination"] = "../outside.py"
    (tmp_path / "menu-moves.json").write_text(
        json.dumps({"moves": [move] * (2 if failure == "duplicate" else 1)})
    )
    with pytest.raises(ValueError):
        current_rows(tmp_path)


def test_unmoved_and_old_release_snapshots_require_no_overlay(tmp_path):
    path = tmp_path / "Scripts/Plain/One.py"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"value=1\n")
    row = {
        "destination": str(path.relative_to(tmp_path)),
        "destination_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    assert released_bytes(tmp_path, row) == path.read_bytes()
    (tmp_path / "menu-moves.json").write_text('{"moves":[]}')
    (tmp_path / "migration.json").write_text(json.dumps([row]))
    assert current_rows(tmp_path) == [row]


@pytest.mark.parametrize("corrupt", [False, True])
def test_additional_revision_when_import_path_changes_then_exact_bytes_recover(tmp_path, corrupt):
    old = b"import old.module\n"
    new = b"import new.module\n"
    destination = "Scripts/Plain/One.py"
    path = tmp_path / destination
    path.parent.mkdir(parents=True)
    path.write_bytes(new)

    def digest(value):
        return hashlib.sha256(value).hexdigest()

    row = {"destination": destination, "destination_sha256": digest(new)}
    revision = {"destination": destination, "historical_sha256": digest(old),
                "current_sha256": digest(new),
                "edits": [{"kind": "issue-205-import-path-update",
                           "historical": old.decode(), "current": new.decode()}]}
    if corrupt:
        revision["edits"][0]["historical"] = "wrong bytes"
    (tmp_path / "migration.json").write_text("[]")
    (tmp_path / "menu-moves.json").write_text('{"moves": []}')
    (tmp_path / "additional-tools.json").write_text(json.dumps([row]))
    (tmp_path / "menu-revisions.json").write_text(json.dumps({"revisions": [revision]}))
    if corrupt:
        with pytest.raises(ValueError, match="changed more"):
            current_rows(tmp_path)
    else:
        assert current_rows(tmp_path) == []
        assert released_bytes(tmp_path, row) == new
        assert released_bytes(tmp_path, {**row, "destination_sha256": digest(old)}) == old


def test_current_manifest_representation_retains_exact_routes_and_owner_bytes(tmp_path):
    old, new, original, move, path = fixture(tmp_path)
    expected = current_rows(tmp_path)
    assert expected[0]["destination"] == move["destination"]
    (tmp_path / "migration.json").write_text(json.dumps(expected))
    owner_manifest = (tmp_path / "migration.json").read_bytes()
    assert current_rows(tmp_path) == expected
    assert current_rows(tmp_path) == expected, "Already current routes must be idempotent"
    assert (tmp_path / "migration.json").read_bytes() == owner_manifest
    assert expected[0]["source_sha256"] == original["source_sha256"]
    assert path.read_bytes() == new
    assert released_bytes(tmp_path, original) == old


@pytest.mark.parametrize("failure", ["current_hash", "body", "unknown_route", "both_routes"])
def test_current_manifest_representation_rejects_unknown_or_changed_routes(tmp_path, failure):
    old, new, original, move, path = fixture(tmp_path)
    current = current_rows(tmp_path)[0]
    rows = [current]
    if failure == "current_hash":
        current["destination_sha256"] = "0" * 64
    if failure == "body":
        path.write_bytes(new.replace(b"value=1", b"value=2"))
    if failure == "unknown_route":
        current["destination"] = "Scripts/Unknown/One.py"
    if failure == "both_routes":
        rows.append(original)
    (tmp_path / "migration.json").write_text(json.dumps(rows))
    with pytest.raises(ValueError):
        current_rows(tmp_path)


@pytest.mark.parametrize("corrupt", [False, True])
def test_moved_menu_when_docstring_overlay_then_recovers_frozen_bytes(tmp_path, corrupt):
    old, moved, row, move, path = fixture(tmp_path)
    current = moved.replace(b"value=1", b'"""Documented menu."""\nvalue=1')
    path.write_bytes(current)

    def digest(data):
        return hashlib.sha256(data).hexdigest()

    move["destination_sha256"] = digest(current)
    revision = {
        "destination": move["destination"], "historical_sha256": digest(moved),
        "current_sha256": digest(current), "source_sha256": row["source_sha256"],
        "edits": [{"historical": "value=1", "current": '"""Documented menu."""\nvalue=1'}],
    }
    if corrupt:
        revision["edits"][0]["historical"] = "value=2"
    (tmp_path / "menu-moves.json").write_text(json.dumps({"moves": [move]}))
    (tmp_path / "menu-revisions.json").write_text(json.dumps({"revisions": [revision]}))
    if corrupt:
        with pytest.raises(ValueError, match="changed more"):
            released_bytes(tmp_path, row)
    else:
        assert released_bytes(tmp_path, row) == old, "Recover exact released bytes"
        assert current_rows(tmp_path)[0]["destination_sha256"] == digest(current)


@pytest.fixture
def consolidation(tmp_path, monkeypatch):
    import menu_layout

    payload = b"# this_file: Scripts/Old/One.py\nvalue=1\n"
    source = {"path": "Scripts/Old/One.py", "commit": "a" * 40,
              "sha256": hashlib.sha256(payload).hexdigest()}
    path = tmp_path / source["path"]
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_route.py").write_text("# route oracle\n")
    row = {"source": source, "disposition": "absorbed",
           "destination": {"path": "Scripts/New/Studio.py", "tab": "One", "sha256": None},
           "retirement_reason": None, "test_routes": ["tests/test_route.py"],
           "acceptance": {"state": "proposed", "date": "2026-11-11",
                          "behavior_parity": False, "native": False}}
    ledger = {"schema_version": 1, "source_count": 1,
              "source_commit": source["commit"], "transitions": [row]}
    monkeypatch.setattr(menu_layout, "_committed_menu_paths", lambda *_: {"Scripts/Old/One.py"})
    real_source_bytes = menu_layout.source_bytes
    monkeypatch.setattr(menu_layout, "source_bytes", lambda root, item, **kw: payload if kw.get("committed") and item["sha256"] == source["sha256"] else real_source_bytes(root, item, **kw))
    return tmp_path, path, payload, ledger, row


def save_consolidation(root, ledger):
    (root / "menu-consolidations.json").write_text(json.dumps(ledger))


@pytest.mark.parametrize("state,disposition", [
    ("proposed", "absorbed"), ("proposed", "retired"),
    ("implemented", "absorbed"), ("implemented", "retired"),
    ("implemented", "retained"),
])
def test_active_menu_paths_preserves_later_additions_and_historical_rows(consolidation, monkeypatch, state, disposition):
    from menu_layout import active_menu_paths

    root, path, payload, ledger, row = consolidation
    archive = root / "archive"
    archive.mkdir()
    (archive / (row["source"]["sha256"] + ".bin")).write_bytes(payload)
    monkeypatch.setenv("FONTLAB_MENU_ARCHIVE", str(archive))
    old = row["source"]["path"]
    later = "Scripts/New/Later.py"
    historical = [{"destination": old, "destination_sha256": row["source"]["sha256"]}]
    (root / "migration.json").write_text(json.dumps(historical))
    (root / "menu-moves.json").write_text('{"moves": []}')
    (root / "additional-tools.json").write_text(json.dumps([{"destination": later}]))
    row["acceptance"]["state"] = state
    row["disposition"] = disposition
    expected = {old, later}
    if disposition == "retired":
        row.update(destination=None, retirement_reason="Teaching only")
    elif state == "implemented":
        if disposition == "retained":
            row["destination"]["path"] = old
        target = root / row["destination"]["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        row["destination"]["sha256"] = hashlib.sha256(payload).hexdigest()
    if state == "implemented":
        expected.remove(old)
        if disposition != "retired":
            expected.add(row["destination"]["path"])
        if disposition != "retained":
            path.unlink()
    save_consolidation(root, ledger)
    before = (root / "migration.json").read_bytes()
    assert active_menu_paths(root) == expected
    assert current_rows(root) == historical
    assert (root / "migration.json").read_bytes() == before


def test_active_menu_paths_refuses_unvalidated_implementation(consolidation):
    from menu_layout import active_menu_paths

    root, _, _, ledger, row = consolidation
    (root / "migration.json").write_text("[]")
    (root / "menu-moves.json").write_text('{"moves": []}')
    (root / "additional-tools.json").write_text("[]")
    row["acceptance"]["state"] = "implemented"
    save_consolidation(root, ledger)
    with pytest.raises(ValueError):
        active_menu_paths(root)


def test_active_menu_paths_merges_two_actions_without_losing_historical_identities(consolidation, monkeypatch):
    import copy
    import menu_layout

    root, path, payload, ledger, first = consolidation
    second = copy.deepcopy(first)
    second["source"]["path"] = "Scripts/Old/Two.py"
    second["destination"]["tab"] = "Two"
    path.with_name("Two.py").write_bytes(payload)
    ledger["transitions"].append(second)
    ledger["source_count"] = 2
    sources = {row["source"]["path"] for row in ledger["transitions"]}
    monkeypatch.setattr(menu_layout, "_committed_menu_paths", lambda *_: sources)
    target = root / first["destination"]["path"]
    target.parent.mkdir()
    target.write_bytes(b"# shared launcher\n")
    for row in ledger["transitions"]:
        row["acceptance"]["state"] = "implemented"
        row["destination"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    historical = [{"destination": source, "destination_sha256": first["source"]["sha256"]}
                  for source in sorted(sources)]
    (root / "migration.json").write_text(json.dumps(historical))
    (root / "menu-moves.json").write_text('{"moves": []}')
    (root / "additional-tools.json").write_text("[]")
    save_consolidation(root, ledger)
    assert menu_layout.active_menu_paths(root) == {first["destination"]["path"]}
    assert current_rows(root) == historical


def test_consolidation_when_proposed_then_no_retirement_or_parity(consolidation):
    from menu_layout import consolidation_rows, source_bytes

    root, path, payload, ledger, row = consolidation
    save_consolidation(root, ledger)
    assert consolidation_rows(root) == [row]
    assert path.read_bytes() == source_bytes(root, row["source"]) == payload
    row.update(disposition="retired", destination=None, retirement_reason="Teaching only")
    save_consolidation(root, ledger)
    assert consolidation_rows(root) == [row]
    assert path.is_file() and not row["acceptance"]["behavior_parity"]


@pytest.mark.parametrize("failure", [
    "duplicate", "missing", "unknown", "escape", "destination", "tab", "hash",
    "commit", "count", "state", "date", "parity", "native", "reason", "route",
    "retired_parity", "retained_path", "proposed_hash", "changed_source", "missing_source",
])
def test_consolidation_when_invalid_then_refused(consolidation, failure):
    from menu_layout import consolidation_rows

    root, path, _, ledger, row = consolidation
    if failure == "duplicate":
        ledger["transitions"].append(row)
    elif failure == "missing":
        ledger["transitions"] = []
    elif failure == "unknown":
        row["source"]["path"] = "Scripts/Other/Unknown.py"
    elif failure == "escape":
        row["destination"]["path"] = "Scripts/../Outside.py"
    elif failure == "destination":
        row["destination"] = None
    elif failure == "tab":
        row["destination"]["tab"] = ""
    elif failure == "hash":
        row["source"]["sha256"] = "unknown"
    elif failure == "commit":
        row["source"]["commit"] = "main"
    elif failure == "count":
        ledger["source_count"] = 2
    elif failure in {"state", "date", "parity", "native"}:
        key = {"parity": "behavior_parity"}.get(failure, failure)
        row["acceptance"][key] = True if failure in {"parity", "native"} else "invalid"
    elif failure == "reason":
        row.update(disposition="retired", destination=None)
    elif failure == "route":
        row["test_routes"] = ["../other.py"]
    elif failure == "retired_parity":
        row.update(disposition="retired", destination=None, retirement_reason="Teaching only")
        row["acceptance"].update(state="implemented", behavior_parity=True)
    elif failure == "retained_path":
        row["disposition"] = "retained"
    elif failure == "proposed_hash":
        row["destination"]["sha256"] = "a" * 64
    elif failure == "changed_source":
        path.write_bytes(b"unreviewed")
    elif failure == "missing_source":
        path.unlink()
    save_consolidation(root, ledger)
    with pytest.raises(ValueError):
        consolidation_rows(root)


def test_consolidation_when_implemented_then_destination_hash_required(consolidation):
    from menu_layout import consolidation_rows

    root, _, _, ledger, row = consolidation
    row["acceptance"]["state"] = "implemented"
    save_consolidation(root, ledger)
    with pytest.raises(ValueError):
        consolidation_rows(root)
    target = root / row["destination"]["path"]
    target.parent.mkdir(parents=True)
    target.write_bytes(b"# studio\n")
    row["destination"]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    save_consolidation(root, ledger)
    assert consolidation_rows(root) == [row]
    target.write_bytes(b"changed studio")
    with pytest.raises(ValueError):
        consolidation_rows(root)


def test_source_bytes_when_git_missing_then_verified_external_archive(consolidation, monkeypatch):
    import menu_layout

    root, path, payload, _, row = consolidation
    path.unlink()
    monkeypatch.setattr(menu_layout.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
    archive = root / "archive"
    archive.mkdir()
    monkeypatch.setenv("FONTLAB_MENU_ARCHIVE", str(archive))
    preserved = archive / (row["source"]["sha256"] + ".bin")
    preserved.write_bytes(payload)
    assert menu_layout.source_bytes(root, row["source"]) == payload
    preserved.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash"):
        menu_layout.source_bytes(root, row["source"])
    preserved.unlink()
    with pytest.raises(ValueError):
        menu_layout.source_bytes(root, row["source"])


def test_source_bytes_when_commit_is_real_then_recovers_without_worktree_file():
    from pathlib import Path
    from menu_layout import source_bytes

    root = Path(__file__).parents[1]
    source = json.loads((root / "menu-consolidations.json").read_text())["transitions"][0]["source"]
    assert hashlib.sha256(source_bytes(root, source, committed=True)).hexdigest() == source["sha256"]
    with pytest.raises(ValueError, match="hash"):
        source_bytes(root, {**source, "sha256": "0" * 64}, committed=True)


def test_released_bytes_when_consolidation_unknown_hash_then_refused(tmp_path):
    path = tmp_path / "Scripts/Plain/One.py"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"value=1\n")
    (tmp_path / "menu-consolidations.json").write_text('{"transitions": []}')
    with pytest.raises(ValueError, match="hash"):
        released_bytes(tmp_path, {"destination": "Scripts/Plain/One.py", "destination_sha256": "0" * 64})


def test_implemented_removed_menu_when_reversible_revision_then_recovers_older_release(tmp_path, monkeypatch):
    import menu_layout

    old, current = b"value=1\n", b"value=2\n"
    destination = "Scripts/Old/One.py"
    current_sha = hashlib.sha256(current).hexdigest()
    old_sha = hashlib.sha256(old).hexdigest()
    (tmp_path / "menu-consolidations.json").write_text(json.dumps({"transitions": [
        {"source": {"path": destination, "commit": "a" * 40, "sha256": current_sha},
         "acceptance": {"state": "implemented"}},
    ]}))
    (tmp_path / "menu-revisions.json").write_text(json.dumps({"revisions": [
        {"destination": destination, "historical_sha256": old_sha, "current_sha256": current_sha,
         "edits": [{"historical": old.decode(), "current": current.decode()}]},
    ]}))
    monkeypatch.setattr(menu_layout, "source_bytes", lambda *a, **kw: current)
    assert released_bytes(tmp_path, {"destination": destination, "destination_sha256": old_sha}) == old


def test_source_bytes_when_git_and_archive_missing_then_clear_refusal(tmp_path, monkeypatch):
    import menu_layout

    monkeypatch.delenv("FONTLAB_MENU_ARCHIVE", raising=False)
    source = {"path": "Scripts/Old/One.py", "commit": "a" * 40, "sha256": "b" * 64}
    with pytest.raises(ValueError, match="unavailable"):
        menu_layout.source_bytes(tmp_path, source)
    with pytest.raises(ValueError, match="inventory"):
        menu_layout._committed_menu_paths(tmp_path, source["commit"])


def test_source_bytes_when_worktree_and_declared_hash_change_then_commit_refuses(tmp_path):
    from pathlib import Path
    import menu_layout

    root = Path(__file__).parents[1]
    source = json.loads((root / "menu-consolidations.json").read_text())["transitions"][0]["source"]
    source = {**source, "sha256": hashlib.sha256(b"forged").hexdigest()}
    with pytest.raises(ValueError, match="hash"):
        menu_layout.source_bytes(root, source, committed=True)


@pytest.mark.parametrize("relative", ["/absolute.py", "Scripts//Old/One.py", "Scripts/Old/../One.py", "Scripts\\Old\\One.py", "", "Scripts/Old/One.txt"])
def test_source_paths_when_not_canonical_then_refused(tmp_path, relative):
    import menu_layout

    with pytest.raises(ValueError, match="path"):
        menu_layout._inside(tmp_path, relative)


def test_consolidation_when_duplicate_target_action_then_refused(consolidation, monkeypatch):
    import copy
    import menu_layout

    root, path, payload, ledger, row = consolidation
    second = copy.deepcopy(row)
    second["source"]["path"] = "Scripts/Old/Two.py"
    (path.parent / "Two.py").write_bytes(payload)
    ledger["transitions"].append(second)
    ledger["source_count"] = 2
    monkeypatch.setattr(menu_layout, "_committed_menu_paths", lambda *_: {r["source"]["path"] for r in ledger["transitions"]})
    save_consolidation(root, ledger)
    with pytest.raises(ValueError, match="Duplicate consolidation destination"):
        menu_layout.consolidation_rows(root)
    second["destination"]["action"] = "Second profile"
    save_consolidation(root, ledger)
    assert len(menu_layout.consolidation_rows(root)) == 2


def test_released_bytes_when_removed_without_git_then_verified_archive(consolidation, monkeypatch):
    import menu_layout

    root, path, payload, ledger, row = consolidation
    row["acceptance"]["state"] = "implemented"
    save_consolidation(root, ledger)
    path.unlink()
    archive = root / "archive"
    archive.mkdir()
    preserved = archive / (row["source"]["sha256"] + ".bin")
    preserved.write_bytes(payload)
    monkeypatch.setenv("FONTLAB_MENU_ARCHIVE", str(archive))

    def unavailable(*args, **kwargs):
        raise FileNotFoundError("Git unavailable")

    monkeypatch.setattr(menu_layout.subprocess, "run", unavailable)
    # Restore the real implementation replaced by the inventory fixture.
    import importlib.util
    spec = importlib.util.spec_from_file_location("real_menu_layout", menu_layout.__file__)
    real = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(real)
    requested = {"destination": row["source"]["path"], "destination_sha256": row["source"]["sha256"]}
    assert real.released_bytes(root, requested) == payload
    with pytest.raises(ValueError, match="hash"):
        real.released_bytes(root, {**requested, "destination_sha256": "0" * 64})
    preserved.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash"):
        real.released_bytes(root, requested)


@pytest.mark.parametrize("key,value", [("tab", " "), ("tab", 3), ("action", ""), ("action", False)])
def test_consolidation_when_blank_or_nontext_route_then_refused(consolidation, key, value):
    from menu_layout import consolidation_rows

    root, _, _, ledger, row = consolidation
    row["destination"][key] = value
    save_consolidation(root, ledger)
    with pytest.raises(ValueError, match="tab"):
        consolidation_rows(root)


def test_consolidation_when_blank_retirement_reason_then_refused(consolidation):
    from menu_layout import consolidation_rows

    root, _, _, ledger, row = consolidation
    row.update(disposition="retired", destination=None, retirement_reason="  ")
    save_consolidation(root, ledger)
    with pytest.raises(ValueError, match="Retirement"):
        consolidation_rows(root)
