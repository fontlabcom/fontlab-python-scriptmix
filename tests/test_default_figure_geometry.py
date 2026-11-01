# this_file: tests/test_default_figure_geometry.py
"""Geometry persistence must never prevent owned panel cleanup."""

# Imported pytest fixtures are also named test parameters.
# ruff: noqa: F811
import pytest
import test_issue122_G2 as g2
from test_issue122_G2 import components, components_world  # noqa: F401
from _figure_settings_support import Settings


@pytest.fixture
def geometry(monkeypatch):
    def restore(panel, value):
        if value != b"owned":
            return False
        panel.restored = value
        return True

    monkeypatch.setattr(g2.Dialog, "restoreGeometry", restore, raising=False)
    monkeypatch.setattr(g2.Dialog, "saveGeometry", lambda self: b"owned", raising=False)


def test_geometry_when_reopened_then_owned_values_restore(components, geometry):
    tool = g2.load(g2.PATHS[3])
    store = Settings({"optionFigures": 3, "geometry": b"owned", "unrelated": "keep"})
    panel = tool["panel_type"](store)()
    assert panel.restored == b"owned"
    assert panel.figure_family.currentIndex == 3
    assert not store.writes
    panel.close()
    assert store.data == {"optionFigures": 3, "geometry": b"owned", "unrelated": "keep"}
    assert panel._completion_lifetime.closed
    assert not panel._connections and panel.deleted
    assert not components.notifications()


def test_geometry_when_invalid_then_diagnosed_panel_still_closes(components, geometry):
    tool = g2.load(g2.PATHS[3])
    panel = tool["panel_type"](Settings({"geometry": b"invalid"}))()
    assert "geometry" in panel.status.text.lower()
    panel.close()
    assert panel.deleted and not panel._connections


@pytest.mark.parametrize(
    "stage", ["saveGeometry", "readonly", "setValue", "sync", "status"]
)
def test_geometry_when_save_fails_then_cleanup_still_runs(
    components, geometry, monkeypatch, stage
):
    tool = g2.load(g2.PATHS[3])
    store = Settings()
    panel = tool["panel_type"](store)()

    def fail(*args):
        raise RuntimeError("geometry unavailable")

    if stage == "readonly":
        store.writable = False
    elif stage == "status":
        store.error = 1
    else:
        monkeypatch.setattr(panel if stage == "saveGeometry" else store, stage, fail)
    panel.close()
    assert panel.slot_error
    assert panel.deleted and not panel._connections
    assert panel._completion_lifetime.closed
    assert not components.notifications()
