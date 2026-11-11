# this_file: tests/test_literal_node_actions.py
"""Distinct original actions execute the real App policy/native-shaped pipeline."""

import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    (
        "Duplicate Nodes All Foreground Layers",
        "all",
        "Paths/Node Duplicator (all masters).py",
        "dff5c6f2d680956288f98c3492f0b617d8f92d1182bfea54d567256555b2bb77",
        1,
    ),
    (
        "Duplicate Nodes Current Layer",
        "current",
        "Paths/Node Duplicator (current layer).py",
        "f6b7bc79856f85611abc485a8df959486afdb76c50e400b5e82f19f2b794c2c7",
        1,
    ),
    (
        "Duplicate Nodes with Two Handles",
        "handles",
        "Paths/Node Duplicator + 2 Handles (all masters).py",
        "eccf4cef027becf7fca14f29de6fde68bea8e0aaeca513c08ba75b717556cddc",
        3,
    ),
)


def load_menu(title):
    path = ROOT / "Scripts/Contours" / (title + ".py")
    assert path.is_file(), "Expose each source policy as its own actionable menu file"
    spec = importlib.util.spec_from_file_location("owned_literal_menu", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="boundary")
def boundary(monkeypatch):
    path = ROOT.parent / "fontlab-fontlabapp/tests/test_node_duplicator_native.py"
    spec = importlib.util.spec_from_file_location("owned_node_fixtures", path)
    fixtures = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixtures)
    api = importlib.import_module("fontlabapp.node_duplicator_native")
    capture = importlib.import_module("fontlabapp._node_duplicator_capture")

    def prepare(mode):
        owned, native, qt, notifications, contour, provider, selected = fixtures.host(
            mode
        )
        monkeypatch.setattr(
            api, "_native", lambda name: native if name == "fontlab" else qt
        )
        monkeypatch.setattr(capture, "selected_layers", provider)
        return owned, native, qt, notifications, contour, selected

    prepare.host = fixtures.host
    return prepare


@pytest.mark.parametrize("title,mode,source,digest,count", CASES)
def test_action_when_run_then_actual_profile_preserves_target_node_copy_data(
    boundary, title, mode, source, digest, count
):
    owned, native, qt, notifications, contour, selected = boundary(mode)
    original = contour.nodes()[0]
    result = load_menu(title).main()
    assert result["profile"] == mode and result["inserted"] == count
    assert len(contour.nodes()) == count + 1 and len(notifications) == 1
    assert contour.nodes()[0] is original and original.nodeState == 0x1029
    copied = contour.nodes()[-1]
    assert copied.name == "n" and copied.getProperty("corner_smooth") == 0.375
    assert copied.getProperty("hoi_point_id") == "exact"
    assert (copied.position.x(), copied.position.y()) == (0.125, 0.375)
    assert [node.nodeState & 7 for node in contour.nodes()] == (
        [1, 4, 4, 1] if mode == "handles" else [1, 1]
    )
    assert result["native_acceptance"] is False


@pytest.mark.parametrize("title,mode,source,digest,count", CASES)
def test_action_when_selection_is_empty_then_refuses_without_history(
    boundary, title, mode, source, digest, count
):
    owned, native, qt, notifications, contour, selected = boundary(mode)
    selected.occurrences = ()
    with pytest.raises(ValueError, match="Select a glyph layer"):
        load_menu(title).main()
    assert len(contour.nodes()) == 1 and not notifications


def test_original_action_provenance_when_indexed_then_keeps_each_source_and_default_panel():
    rows = json.loads((ROOT / "additional-tools.json").read_text())
    indexed = {row["destination"]: row for row in rows}
    for title, mode, source, digest, count in CASES:
        destination = "Scripts/Contours/" + title + ".py"
        assert destination in indexed
        row = indexed[destination]
        assert row["source_path"] == source and row["source_sha256"] == digest
        assert row["source_body_redistributed"] is False
        assert row["native_acceptance"] == "pending"
        assert row["counted_in_130_sample_migration"] is False
        assert (
            row["destination_sha256"]
            == hashlib.sha256((ROOT / destination).read_bytes()).hexdigest()
        )
        assert row["execution_profile"] == mode
    default = indexed["Scripts/Contours/Node Duplicator.py"]
    assert (
        default["destination_sha256"]
        == "1bd5b65bd847d09160284b85597f51b77158e3a7d78707fb9b782b66518a3ad1"
    )
    assert (
        hashlib.sha256((ROOT / default["destination"]).read_bytes()).hexdigest()
        == default["destination_sha256"]
    )


@pytest.mark.parametrize("title,mode,source,digest,count", CASES)
def test_action_when_old_rescued_adapter_lacks_guarded_entrypoint_then_never_calls_it(
    monkeypatch, title, mode, source, digest, count
):
    api = importlib.import_module("fontlabapp.node_duplicator_native")
    monkeypatch.delattr(api, "duplicate_selected_nodes")
    monkeypatch.setattr(
        api, "execute", lambda *args: pytest.fail("Do not call stale guards")
    )
    with pytest.raises(AttributeError, match="duplicate_selected_nodes"):
        load_menu(title).main()


@pytest.mark.parametrize("title,mode,source,digest,count", CASES)
def test_menu_file_when_executed_as_main_then_runs_actual_owned_operation(
    boundary, title, mode, source, digest, count
):
    import runpy
    owned, native, qt, notifications, contour, selected = boundary(mode)
    runpy.run_path(str(ROOT / "Scripts/Contours" / (title + ".py")), run_name="__main__")
    assert len(contour.nodes()) == count + 1 and len(notifications) == 1
