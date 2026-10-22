# this_file: tests/test_guide_rewrite.py
"""Complete editable guide controls with owned Qt-shaped widget doubles."""

import importlib.util
import sys
from copy import deepcopy
from types import SimpleNamespace as NS

import pytest
from menu_layout import released_bytes
from test_components import components  # noqa: F401
from test_guides import guides  # noqa: F401
from test_masters import masters  # noqa: F401

TOOLS = [
    ("Clear Glyph Guides", "ClearGuides"),
    ("Copy Guides Between Masters", "CopyGuides"),
    ("Guide List Editor", "ListEditor"),
]


@pytest.fixture
def rewrite(guides, monkeypatch, app_sources):  # noqa: F811
    base = guides

    class Combo(base.qt.QtGui.QComboBox):
        def clear(self):
            self.items = []
            self.currentIndex = 0

    base.qt.QtGui.QComboBox = Combo

    class Table(base.qt.QtGui.QTableWidget):
        def setCurrentCell(self, row, column):
            self.current_row = row

        def currentRow(self):
            return getattr(self, "current_row", -1)

        def removeRow(self, row):
            self.cells = {
                (r - (r > row), c): v for (r, c), v in self.cells.items() if r != row
            }
            self.rowCount -= 1

    base.qt.QtGui.QTableWidget = Table

    class Item(base.qt.QtGui.QTableWidgetItem):
        def flags(self):
            return 31

    base.qt.QtGui.QTableWidgetItem = Item
    base.qt.QtCore.Qt.ItemIsEditable = 2
    base.qt.QtCore.Qt.AlignTop = 32
    for name in [
        "edit_guards",
        "guide_records",
        "guide_rewrite",
        "_guide_rewrite_dialog",
        "_guide_editor_dialog",
    ]:
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
        base.modules[name] = module
    native = base.modules["scripting"]._native("fontlab")
    create = native.flGuideLine
    native.flGuideLine = lambda *a: deepcopy(a[0]) if len(a) == 1 else create(*a)
    font = base.font

    def setup():
        p, layers = font()
        for group in layers.values():
            for layer in group.values():
                layer.removeGuides = lambda h, v, layer=layer: setattr(
                    layer, "guidelines", [g for g in layer.guidelines if g.isHint]
                )
                layer.appendGuidelines = lambda values, layer=layer: (
                    layer.guidelines.extend(values)
                )
        return p, layers

    base.font = setup
    return base


@pytest.mark.parametrize("title,klass", TOOLS)
def test_no_font_keeps_actual_diagnosis_close_and_registry_cleanup(
    rewrite, monkeypatch, title, klass
):
    monkeypatch.setattr(sys, "_fontlab_samples", {}, raising=False)
    dialog = rewrite.module(title).main()
    assert not dialog._snapshot_valid and not dialog.apply_button.enabled
    assert "font" in dialog.subtitle.text.lower()
    dialog.close_button.clicked.emit()
    assert dialog.deleted and not dialog._connections and not sys._fontlab_samples


def test_list_editor_preserves_add_edit_delete_revert_and_single_glyph_scope(rewrite):
    _p, layers = rewrite.font()
    dialog = rewrite.module("Guide List Editor").ListEditor()
    assert dialog._snapshot_valid and dialog.glyph.name == "H"
    dialog.add_button.clicked.emit()
    assert dialog.table.rowCount == 1 and dialog.table.item(0, 0).text() == "Bold"
    dialog.table.item(0, 2).setText("321")
    dialog.table.item(0, 4).setText("Owned edited")
    dialog.apply_button.clicked.emit()
    assert dialog.last_result == {"layers": 1} and len(rewrite.state.history) == 1
    assert [g.name for g in layers["H"]["Bold"].guidelines] == ["Owned edited"]
    assert not layers["O"]["Bold"].guidelines
    dialog.add_row()
    dialog.reload_button.clicked.emit()
    assert dialog.table.rowCount == 1, "Revert must discard unapplied guide rows"
    dialog.table.setCurrentCell(0, 1)
    dialog.delete_button.clicked.emit()
    dialog.apply_button.clicked.emit()
    assert not layers["H"]["Bold"].guidelines and dialog.last_result == {"layers": 1}


@pytest.mark.parametrize("bad", ["nan", "inf", "bad"])
def test_list_editor_invalid_row_refuses_complete_write(rewrite, bad):
    _p, layers = rewrite.font()
    dialog = rewrite.module("Guide List Editor").ListEditor()
    dialog.add_row()
    dialog.table.item(0, 1).setText(bad)
    dialog.apply_button.clicked.emit()
    assert not rewrite.state.history and not layers["H"]["Bold"].guidelines
    assert "row 1:" in dialog.last_error and not dialog._snapshot_valid


def test_all64_released_rows_and_menus_remain_immutable():
    import hashlib
    import json
    from pathlib import Path

    root = Path(__file__).parents[1]
    rows = json.loads((root / "migration.json").read_text())
    assert len(rows) == 69
    assert (
        hashlib.sha256(
            json.dumps(rows[:64], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        == "2685650af3e45013fd9c63a0718fc64c8b13c16f80f65b11cbd65c21893e5f1c"
    )
    for row in rows[:64]:
        assert (
            hashlib.sha256(released_bytes(root, row)).hexdigest()
            == row["destination_sha256"]
        )


def test_clear_keeps_all_original_filters_and_native_hint_guides(rewrite):
    _p, layers = rewrite.font()
    api = rewrite.modules["guides"]
    layer = layers["H"]["Bold"]
    h = api.new_guide((0, 321, 0, "C1 seed"))
    v = api.new_guide((250, 0, 90, "keep me"))
    hint = NS(isHint=True)
    layer.guidelines.extend([h, v, hint])
    dialog = rewrite.module("Clear Glyph Guides").ClearGuides()
    assert dialog.direction.items == [
        "Any direction",
        "Horizontal",
        "Vertical",
        "Angled",
    ]
    dialog.name_filter.setText("c1")
    assert dialog.table.rowCount == 1
    dialog.apply_button.clicked.emit()
    assert dialog.last_result == {"layers": 1, "removed": 1, "left": 0}
    assert [g.name for g in layer.guidelines if not g.isHint] == [
        "keep me"
    ] and hint in layer.guidelines
    dialog.apply()
    assert (
        dialog.last_result == {"layers": 0, "removed": 0, "left": 0}
        and len(rewrite.state.history) == 1
    )


def test_copy_preserves_source_target_mode_scaling_controls_and_close(rewrite):
    _p, layers = rewrite.font()
    api = rewrite.modules["guides"]
    guide = api.new_guide((250, 0, 90, "Copied vertical"))
    layers["H"]["Bold"].guidelines.append(guide)
    dialog = rewrite.module("Copy Guides Between Masters").CopyGuides()
    assert dialog._snapshot_valid and dialog.source.items == ["Bold", "Light"]
    assert dialog.mode.items == [
        "Add to the target guides",
        "Replace the target guides",
    ]
    assert (
        not dialog.target_checks["Bold"].enabled
        and dialog.target_checks["Light"].enabled
    )
    assert dialog.follow_width.isChecked()
    dialog.apply_button.clicked.emit()
    assert dialog.last_result == {"layers": 1}
    ratio = layers["H"]["Light"].advanceWidth / layers["H"]["Bold"].advanceWidth
    assert api.guide_record(layers["H"]["Light"].guidelines[0]) == (
        round(250 * ratio, 2),
        0.0,
        90.0,
        "Copied vertical",
    )
    assert layers["H"]["Bold"].guidelines == [guide]
    dialog.close_button.clicked.emit()
    assert dialog.package is None and not dialog.glyphs and not dialog._connections


def test_list_unknown_master_refuses_and_stale_row_actions_release_handles(rewrite):
    _p, layers = rewrite.font()
    dialog = rewrite.module("Guide List Editor").ListEditor()
    dialog.add_row()
    dialog.table.item(0, 0).setText("Owned unknown master")
    dialog.apply_button.clicked.emit()
    assert "master changed" in dialog.last_error and not rewrite.state.history
    assert (
        dialog.glyph is None
        and not dialog.table.enabled
        and not dialog.add_button.enabled
    )
    assert not layers["H"]["Bold"].guidelines
    dialog.initial_refresh()
    assert dialog._snapshot_valid
    rewrite.state.selected.clear()
    dialog.add_button.clicked.emit()
    assert (
        not dialog._snapshot_valid
        and dialog.glyph is None
        and bool(dialog._connections)
    )
    assert not dialog.delete_button.enabled and not rewrite.state.history


def test_copy_changed_target_width_refuses_stale_scaled_plan(rewrite):
    _p, layers = rewrite.font()
    api = rewrite.modules["guides"]
    layers["H"]["Bold"].guidelines.append(api.new_guide((250, 0, 90, "Owned vertical")))
    dialog = rewrite.module("Copy Guides Between Masters").CopyGuides()
    assert dialog.apply_button.enabled
    layers["H"]["Light"].advanceWidth += 20
    dialog.apply_button.clicked.emit()
    assert not rewrite.state.history and not layers["H"]["Light"].guidelines, (
        "A width change must invalidate the displayed scale ratio before writing"
    )
    assert not dialog._snapshot_valid and bool(dialog.last_error)
