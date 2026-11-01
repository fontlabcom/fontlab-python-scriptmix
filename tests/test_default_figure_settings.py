# this_file: tests/test_default_figure_settings.py
"""The original saved figure family uses only owned injected settings."""

# Imported pytest fixtures are also named test parameters.
# ruff: noqa: F811
from typing import Any
import pytest
import test_issue122_G2 as g2
from test_issue122_G2 import components, components_world  # noqa: F401 - shared host fixture
from _figure_settings_support import Settings


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, 0),
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        ("3", 3),
        (-1, 0),
        (4, 0),
        (True, 0),
        (1.5, 0),
        ("garbage", 0),
    ],
)
def test_saved_family_when_loaded_then_valid_index_or_lining(
    components: Any, value, expected
):
    tool = g2.load(g2.PATHS[3])
    store = Settings({} if value is None else {"optionFigures": value})
    assert tool["load_family"](store) == expected
    assert not store.writes, "Restoring defaults must not rewrite saved data"


@pytest.mark.parametrize("family", range(4))
def test_family_when_changed_then_reopened_instances_restore_without_writes(
    components: Any, family
):
    tool = g2.load(g2.PATHS[3])
    store = Settings({"unrelated": "keep"})
    panel = tool["panel_type"](store)()
    assert store.fallbacks is False and panel.figure_family.currentIndex == 0
    assert not store.writes
    if family == 0:
        panel.figure_family.setCurrentIndex(1)
    panel.figure_family.setCurrentIndex(family)
    assert store.data == {"unrelated": "keep", "optionFigures": family}
    assert not panel.apply_button.enabled, (
        "Missing family refuses preview but still saves choice"
    )
    panel.replace_contours.setChecked(True)
    panel.close()
    writes = list(store.writes)
    reopened = tool["panel_type"](store)()
    assert reopened.figure_family.currentIndex == family
    assert not reopened.replace_contours.isChecked(), (
        "Destructive option is never persisted"
    )
    assert store.writes == writes, "Restoration must precede signal connection"
    reopened.close()
    assert not panel._connections and not reopened._connections


@pytest.mark.parametrize("stage", ["readonly", "setValue", "sync", "status"])
def test_family_when_save_fails_then_preview_is_current_and_error_is_visible(
    components: Any, monkeypatch, stage
):
    tool = g2.load(g2.PATHS[3])
    store = Settings()
    panel = tool["panel_type"](store)()
    seen = []
    monkeypatch.setattr(
        panel, "refresh", lambda: seen.append(panel.figure_family.currentIndex)
    )

    def fail(*args):
        raise RuntimeError("settings unavailable")

    if stage == "readonly":
        store.writable = False
    elif stage == "status":
        store.error = 1
    else:
        monkeypatch.setattr(store, stage, fail)
    panel.figure_family.setCurrentIndex(2)
    assert seen == [2], "Refresh current family before any saving failure"
    assert "Error:" in panel.status.text and "settings" in panel.status.text.lower()
    assert panel.figure_family.currentIndex == 2
    assert not components.notifications(), "A choice callback never writes a font"
    panel.close()


@pytest.mark.parametrize("value", [-1, 4, True, None, "2"])
def test_family_when_save_index_invalid_then_no_settings_write(components: Any, value):
    tool = g2.load(g2.PATHS[3])
    store = Settings()
    with pytest.raises(ValueError):
        tool["save_family"](store, value)
    assert not store.writes


def test_family_when_store_read_fails_then_no_panel_or_font_write(components: Any):
    tool = g2.load(g2.PATHS[3])
    store = Settings()
    store.error = 2
    with pytest.raises(RuntimeError, match="settings"):
        tool["load_family"](store)
    assert not store.writes and not components.notifications()


@pytest.mark.parametrize("stage", ["sync", "status", "value"])
def test_family_when_restore_fails_then_panel_opens_and_recovers(
    components: Any, monkeypatch, stage
):
    tool = g2.load(g2.PATHS[3])
    store = Settings({"optionFigures": 3, "unrelated": "keep"})
    original = getattr(store, stage)

    def fail(*args):
        raise RuntimeError("settings unavailable")

    monkeypatch.setattr(store, stage, fail)
    panel = tool["panel_type"](store)()
    assert panel.figure_family.currentIndex == 0
    assert "settings unavailable" in panel.status.text
    assert not store.writes, "Failed restoration must not overwrite the saved family"
    assert not components.notifications()
    monkeypatch.setattr(store, stage, original)
    panel.figure_family.setCurrentIndex(2)
    assert store.data == {"optionFigures": 2, "unrelated": "keep"}
    panel.close()
    assert not panel._connections, (
        "A failed settings read must leave a fully owned, closable panel"
    )
