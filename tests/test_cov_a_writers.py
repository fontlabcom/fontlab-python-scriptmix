# this_file: tests/test_cov_a_writers.py
# SPDX-License-Identifier: Apache-2.0
"""Coverage round A: panel-style writers, layer switching and the cursive sampler."""

from __future__ import annotations

import json
import math
import runpy
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest
from _cov_a_support import ROOT, Host, host  # noqa: F401


class PanelBase:
    """Stand-in for the App panel base: records what a script's panel asks of it."""

    TITLE = KEY = ""
    current_master = "Regular"

    def __init__(self) -> None:
        self.package = NS(name="package")
        self.form = NS(added=[], addWidget=lambda *a: self.form.added.append(a))
        self.rows: list[tuple] = []
        self.watched: list[Any] = []
        self.scope_made = 0

    def scope_box(self) -> NS:
        self.scope_made += 1
        return NS(currentIndexChanged="scope-signal")

    def add_row(self, label: str, *widgets: Any) -> None:
        self.rows.append((label, widgets))

    def watch(self, signal: Any, callback: Any = None) -> None:
        self.watched.append(signal)


# ---- Decompose Serif Components --------------------------------------------------


def serif_tool(host: Host, **scripting: Any) -> Any:
    return host.load(
        "Components/Decompose Serif Components.py",
        modules=("component_panel", "component_writer"),
        patches={"component_panel": {"panel_type": lambda: PanelBase}},
        scripting=scripting,
    )


def component(base: str, shape_id: int, *, affine: bool = True) -> NS:
    """Component shape double referring to ``base`` on the master layer."""
    return NS(
        isComponent=True,
        isComposite=True,
        id=shape_id,
        transform=NS(isAffine=lambda: affine),
        shapeData=NS(componentGlyph=base, componentLayer=""),
    )


def test_serif_changes_when_mixed_components_then_only_serif_prefixed_rows(host):
    tool = serif_tool(host)
    plain_base = NS(
        findLayer=lambda master: NS(isNull=False, autoLayer=False, shapes=[]),
    )
    package = NS(findName=lambda name: plain_base)
    contour = NS(isComponent=False)
    layer = NS(shapes=[component("SerifLeft", 4), contour, component("A", 5), component("Serif.alt", 6)])
    rows = tool.changes(package, NS(name="n"), "Regular", layer)
    assert [(r.name, r.old, r.new, r.edit, r.problem) for r in rows] == [
        ("SerifLeft", "component", "editable parts", 4, ""),
        ("Serif.alt", "component", "editable parts", 6, ""),
    ], "Only bases starting with Serif are planned; contours and other parts stay"


def test_serif_changes_when_base_cannot_be_copied_then_problem_blocks_the_row(host):
    tool = serif_tool(host)
    package = NS(findName=lambda name: None)
    rows = tool.changes(package, NS(name="n"), "Regular", NS(shapes=[component("SerifLeft", 4)]))
    assert rows[0].problem == "base SerifLeft has no plain layer Regular", "serif changes when base cannot be copied then problem blocks the row: expected rows[0].problem == 'base SerifLeft has no plain layer Regular'"
    rows = tool.changes(package, NS(name="n"), "Regular", NS(shapes=[component("SerifLeft", 4, affine=False)]))
    assert rows[0].problem == "perspective transform: decompose it in FontLab", "serif changes when base cannot be copied then problem blocks the row: expected rows[0].problem == 'perspective transform: decompose it in FontLab'"


def test_serif_panel_when_built_then_masters_scope_added_and_watched(host):
    tool = serif_tool(host)
    panel = tool.SerifPanel()
    panel.build_controls()
    assert panel.scope_made == 1, "One master scope box is created"
    labels = [a for a in panel.form.added if getattr(a[0], "text", None) == "Masters"]
    assert len(labels) == 1 and labels[0][1:] == (0, 0), "The 'Masters' caption sits at row 0, column 0"
    assert panel.form.added[1][1:] == (0, 1) and panel.watched == ["scope-signal"], "serif panel when built then masters scope added and watched: unexpected result"
    assert (tool.SerifPanel.TITLE, tool.SerifPanel.ACTION, tool.SerifPanel.DONE) == (
        "Decompose Serif Components",
        "Decompose",
        "Decomposed",
    ), 'serif panel when built then masters scope added and watched: unexpected result'
    assert tool.SerifPanel.HEADERS == ("Glyph · master", "Component", "Becomes"), "serif panel when built then masters scope added and watched: expected tool.SerifPanel.HEADERS == ('Glyph · master', 'Component', 'Becomes')"


def test_serif_panel_planner_when_called_then_delegates_to_changes_with_package(host):
    tool = serif_tool(host)
    seen: list[tuple] = []
    tool.changes = lambda package, glyph, master, layer: seen.append((package, glyph, master, layer)) or ["row"]
    panel = tool.SerifPanel()
    plan = panel.planner()
    assert plan("glyph", "Bold", "layer") == ["row"], "serif panel planner when called then delegates to changes with package: expected plan('glyph', 'Bold', 'layer') == ['row']"
    assert seen == [(panel.package, "glyph", "Bold", "layer")], "serif panel planner when called then delegates to changes with package: expected seen == [(panel.package, 'glyph', 'Bold', 'layer')]"


def test_serif_panel_editor_when_requested_then_unlocking_eject_editor(host):
    tool = serif_tool(host)
    editor = tool.SerifPanel().editor()
    assert type(editor).__name__ == "EjectEditor" and editor.unlock is True, "Decomposing releases locks"


def test_serif_main_when_dialog_opens_then_returned(host):
    marker = object()
    tool = serif_tool(host, show_script_dialog=lambda dialog_type, key: (marker, dialog_type, key))
    result = tool.main()
    assert result == (marker, tool.SerifPanel, "components_decompose_serifs"), "serif main when dialog opens then returned: expected result == (marker, tool.SerifPanel, 'components_decompose_serifs')"


@pytest.mark.parametrize("error", [ValueError("bad"), RuntimeError("rt"), TimeoutError("slow")])
def test_serif_main_when_dialog_refused_then_warning_box_and_none(host, error):
    def refuse(dialog_type: Any, key: str) -> None:
        raise error

    tool = serif_tool(host, show_script_dialog=refuse)
    warned: list[tuple] = []
    host.qt.QtGui.QMessageBox = NS(warning=lambda *a: warned.append(a))
    assert tool.main() is None, 'serif main when dialog refused then warning box and none: expected tool.main() is None'
    assert warned == [(host.main_window, "Decompose Serif Components", str(error))], "serif main when dialog refused then warning box and none: unexpected result"


def test_serif_main_when_run_as_script_then_panel_shown(host):
    serif_tool(host, show_script_dialog=lambda dialog_type, key: host.windows().setdefault(key, dialog_type))
    runpy.run_path(str(ROOT / "Scripts/Components/Decompose Serif Components.py"), run_name="__main__")
    assert "components_decompose_serifs" in host.windows(), "serif main when run as script then panel shown: expected 'components_decompose_serifs' in host.windows()"


# ---- Retract Handles ---------------------------------------------------------------


class Node:
    def __init__(self, x: float, y: float, on: bool, selected: bool = False) -> None:
        self.x, self.y, self.selected = x, y, selected
        self._on = on

    def isOn(self) -> bool:  # noqa: N802 - FontLab name
        return self._on


class Contour:
    def __init__(self, nodes: list[Node], closed: bool = True, tt: bool = False) -> None:
        self._nodes, self.closed, self.isTT = nodes, closed, tt

    def nodes(self) -> list[Node]:
        return self._nodes


def cubic_loop(selected: tuple[int, ...] = ()) -> Contour:
    """Closed cubic contour: two on-curve nodes, each with two live handles."""
    points = [(0, 0, True), (10, 0, False), (20, 50, False), (30, 50, True), (40, 50, False), (0, 10, False)]
    return Contour([Node(x, y, on, i in selected) for i, (x, y, on) in enumerate(points)])


def shape_of(*contours: Contour, refs: int = 1, moved: bool = True, component: bool = False) -> NS:
    matrix = NS(m11=lambda: 1.0, m22=lambda: 1.0 if moved else 2.0, m12=lambda: 0.0, m21=lambda: 0.0, dx=lambda: 5, dy=lambda: 6)
    return NS(isComponent=component, contours=list(contours), shapeData=NS(referenceCount=refs), transform=matrix)


def retract_tool(host: Host, **scripting: Any) -> Any:
    return host.load(
        "Contours/Retract Handles.py",
        modules=("outline_panel", "outline_writer"),
        patches={"outline_panel": {"panel_type": lambda: PanelBase}},
        scripting=scripting,
    )


def test_moves_when_cubic_loop_then_all_four_handles_target_their_bases(host):
    tool = retract_tool(host)
    contour = cubic_loop()
    moves = tool.moves(contour, selected_only=False)
    nodes = contour.nodes()
    assert [(n, x, y) for n, x, y in moves] == [
        (nodes[1], 0.0, 0.0),
        (nodes[2], 30.0, 50.0),
        (nodes[4], 30.0, 50.0),
        (nodes[5], 0.0, 0.0),
    ], "Closing segment handles retract onto the first and last on-curve nodes"


def test_moves_when_selected_only_then_only_handles_of_selected_bases(host):
    tool = retract_tool(host)
    contour = cubic_loop(selected=(0,))
    moved = [n for n, _, _ in tool.moves(contour, selected_only=True)]
    assert moved == [contour.nodes()[1], contour.nodes()[5]], 'moves when selected only then only handles of selected bases: expected moved == [contour.nodes()[1], contour.nodes()[5]]'
    explicit = tool.moves(contour, True, selected_indices={3})
    assert [n for n, _, _ in explicit] == [contour.nodes()[2], contour.nodes()[4]], "Explicit indices win"


def test_moves_when_tt_open_or_degenerate_then_nothing_or_no_wrap(host):
    tool = retract_tool(host)
    assert tool.moves(Contour(cubic_loop().nodes(), tt=True), False) == [], "Quadratic contours are kept"
    open_contour = Contour(cubic_loop().nodes()[:4], closed=False)
    assert len(tool.moves(open_contour, False)) == 2, "An open contour does not wrap"
    flat = Contour([Node(0, 0, True), Node(0, 0, False), Node(4, 5, False), Node(5, 5, True)], closed=False)
    assert [(x, y) for _, x, y in tool.moves(flat, False)] == [(5.0, 5.0)], "Already-retracted handles are skipped"
    two_on = Contour([Node(0, 0, True), Node(9, 9, True)], closed=False)
    assert tool.moves(two_on, False) == [], "A line segment has no handles"


def test_changes_when_all_handles_then_one_row_with_count_and_targets(host):
    tool = retract_tool(host)
    layer = NS(shapes=[shape_of(cubic_loop())])
    rows = tool.changes(layer, selected_only=False)
    assert len(rows) == 1 and (rows[0].name, rows[0].old, rows[0].new) == ("handles", "4", "retracted"), "changes when all handles then one row with count and targets: unexpected result"
    assert len(rows[0].edit) == 4, "The row carries every planned move"


def test_changes_when_shared_or_scaled_shape_then_note_rows_and_no_edit(host):
    tool = retract_tool(host)
    layer = NS(shapes=[shape_of(cubic_loop(), refs=3), shape_of(cubic_loop(), moved=False), shape_of(cubic_loop(), component=True)])
    rows = tool.changes(layer, False)
    assert [r.new for r in rows] == ["shared outline, kept", "scaled or rotated shape, kept"], "changes when shared or scaled shape then note rows and no edit: unexpected result"
    assert all(r.edit is None for r in rows), "Notes are display-only rows"


def test_changes_when_selected_only_then_selection_read_from_reference_master(host):
    tool = retract_tool(host)
    target = NS(shapes=[shape_of(cubic_loop())])
    reference = NS(shapes=[shape_of(cubic_loop(selected=(3,)))])
    rows = tool.changes(target, True, reference)
    assert len(rows) == 1 and rows[0].old == "2", "Only handles at the reference master's selected node"
    none_selected = tool.changes(target, True, NS(shapes=[shape_of(cubic_loop())]))
    assert none_selected == [], "No selected nodes means no changes"


def test_changes_when_reference_structure_differs_then_blocking_row(host):
    tool = retract_tool(host)
    target = NS(shapes=[shape_of(cubic_loop())])
    fewer = NS(shapes=[])
    rows = tool.changes(target, True, fewer)
    assert rows[0].problem == "Master node structures differ.", "changes when reference structure differs then blocking row: expected rows[0].problem == 'Master node structures differ.'"
    shorter = Contour(cubic_loop().nodes()[:5])
    rows = tool.changes(target, True, NS(shapes=[shape_of(shorter)]))
    assert rows[0].problem == "Master node structures differ.", "Different node counts"
    retyped = cubic_loop()
    retyped.nodes()[1]._on = True
    rows = tool.changes(target, True, NS(shapes=[shape_of(retyped)]))
    assert rows[0].problem == "Master node structures differ.", "Different on/off pattern"


def test_retract_editor_when_write_and_check_then_coordinates_set_and_verified(host):
    tool = retract_tool(host)
    contour = cubic_loop()
    targets = tool.moves(contour, False)
    editor = tool.RetractEditor()
    layer = NS(name="Regular")
    editor.write(layer, [targets])
    assert (contour.nodes()[1].x, contour.nodes()[1].y) == (0.0, 0.0), 'retract editor when write and check then coordinates set and verified: expected (contour.nodes()[1].x, contour.nodes()[1].y) == (0.0, 0.0)'
    assert editor.check([(layer, [targets])]) == [], "Written handles read back exactly"
    contour.nodes()[2].x = 99
    assert editor.check([(layer, [targets])]) == ["Regular"], "A handle that did not hold is reported by layer name"


def test_retract_panel_when_built_then_filter_checkbox_added_and_watched(host):
    tool = retract_tool(host)
    panel = tool.RetractPanel()
    panel.build_controls()
    assert panel.selected_filter.label == "Only at selected on-curve nodes", "retract panel when built then filter checkbox added and watched: expected panel.selected_filter.label == 'Only at selected on-curve nodes'"
    assert panel.rows == [("", (panel.selected_filter,))], "retract panel when built then filter checkbox added and watched: expected panel.rows == [('', (panel.selected_filter,))]"
    assert panel.watched == [panel.selected_filter.toggled], 'retract panel when built then filter checkbox added and watched: expected panel.watched == [panel.selected_filter.toggled]'
    assert tool.RetractPanel.HEADERS == ("Glyph · master", "Item", "Handles", "After"), "retract panel when built then filter checkbox added and watched: unexpected result"
    assert tool.RetractPanel.UNIT == "contour", "retract panel when built then filter checkbox added and watched: expected tool.RetractPanel.UNIT == 'contour'"


def test_retract_panel_planner_when_filter_toggled_then_selection_read_from_current_master(host):
    tool = retract_tool(host)
    panel = tool.RetractPanel()
    panel.build_controls()
    calls: list[tuple] = []
    tool.changes = lambda layer, selected, reference: calls.append((layer, selected, reference)) or ["r"]
    glyph = NS(findLayer=lambda master: f"layer-of-{master}")
    plan = panel.planner()
    assert plan(glyph, "Bold", "L") == ["r"], "retract panel planner when filter toggled then selection read from current master: expected plan(glyph, 'Bold', 'L') == ['r']"
    panel.selected_filter.setChecked(True)
    plan = panel.planner()
    plan(glyph, "Bold", "L")
    assert calls == [("L", False, "layer-of-Regular"), ("L", True, "layer-of-Regular")], "retract panel planner when filter toggled then selection read from current master: unexpected result"


def test_retract_panel_editor_when_requested_then_retract_editor(host):
    tool = retract_tool(host)
    assert isinstance(tool.RetractPanel().editor(), tool.RetractEditor), 'retract panel editor when requested then retract editor: expected isinstance(tool.RetractPanel().editor(), tool.RetractEditor)'


@pytest.mark.parametrize("error", [ValueError("bad"), RuntimeError("rt"), TimeoutError("slow")])
def test_retract_main_when_dialog_refused_then_warning_box_and_none(host, error):
    def refuse(dialog_type: Any, key: str) -> None:
        raise error

    tool = retract_tool(host, show_script_dialog=refuse)
    warned: list[tuple] = []
    host.qt.QtGui.QMessageBox = NS(warning=lambda *a: warned.append(a))
    assert tool.main() is None, 'retract main when dialog refused then warning box and none: expected tool.main() is None'
    assert warned == [(host.main_window, "Retract Handles", str(error))], "retract main when dialog refused then warning box and none: expected warned == [(host.main_window, 'Retract Handles', str(error))]"


def test_retract_main_when_dialog_opens_then_returned_and_script_guard_runs(host):
    tool = retract_tool(host, show_script_dialog=lambda dialog_type, key: host.windows().setdefault(key, dialog_type))
    assert tool.main() is tool.RetractPanel, 'retract main when dialog opens then returned and script guard runs: expected tool.main() is tool.RetractPanel'
    host.windows().clear()
    runpy.run_path(str(ROOT / "Scripts/Contours/Retract Handles.py"), run_name="__main__")
    assert "contours_retract_handles" in host.windows(), "retract main when dialog opens then returned and script guard runs: expected 'contours_retract_handles' in host.windows()"


# ---- Display Previous Layer --------------------------------------------------------

LAYER_PATH = "Masters/Display Previous Layer.py"
MASTERS = ("Regular", "Bold")


def layer_tool(host: Host, **ap_modules: Any) -> Any:
    tool = host.load(LAYER_PATH, modules=("masters",))
    for name, attributes in ap_modules.items():
        host.fake_ap(name, **attributes)
    return tool


def glyph_with(*layers: tuple[str, bool]) -> NS:
    """Glyph whose layers are (name, is_body); masks and services are flagged."""
    return NS(
        layers=[NS(name=n, isMaskLayer=not body, isService=False) for n, body in layers],
        activated=[],
    )


def test_backup_master_when_backup_name_then_master_resolved_by_shared_rule(host):
    tool = layer_tool(host)
    assert tool.backup_master("Regular backup 1", MASTERS) == "Regular", "backup master when backup name then master resolved by shared rule: expected tool.backup_master('Regular backup 1', MASTERS) == 'Regular'"
    assert tool.backup_master("Mystery", MASTERS) is None, "backup master when backup name then master resolved by shared rule: expected tool.backup_master('Mystery', MASTERS) is None"


def test_layer_cycle_when_alternates_and_backups_then_same_master_body_layers_only(host):
    tool = layer_tool(host)
    layers = [("Regular", True), ("Bold", True), ("Regular#b", True), ("Regular backup 1", True), ("Regular@mask", False)]
    assert tool.layer_cycle(layers, "Regular#b", MASTERS) == ["Regular", "Regular#b", "Regular backup 1"], "layer cycle when alternates and backups then same master body layers only: unexpected result"


def test_layer_cycle_when_current_has_no_master_then_refused(host):
    tool = layer_tool(host)
    with pytest.raises(ValueError, match="Layer 'Orphan' belongs to no master."):
        tool.layer_cycle([("Regular", True)], "Orphan", MASTERS)


def test_layer_cycle_when_current_is_not_body_then_refused(host):
    tool = layer_tool(host)
    with pytest.raises(ValueError, match="Layer 'Regular#m' is not a body layer."):
        tool.layer_cycle([("Regular", True), ("Regular#m", False)], "Regular#m", MASTERS)


@pytest.mark.parametrize(
    ("current", "step", "expected"),
    [("a", -1, "c"), ("b", -1, "a"), ("c", 1, "a"), ("a", 1, "b")],
)
def test_pick_layer_when_step_then_wraps_around(host, current, step, expected):
    tool = layer_tool(host)
    assert tool.pick_layer(["a", "b", "c"], current, step) == expected, "pick layer when step then wraps around: expected tool.pick_layer(['a', 'b', 'c'], current, step) == expected"


def test_pick_layer_when_only_one_layer_then_refused(host):
    tool = layer_tool(host)
    with pytest.raises(ValueError, match="only layer of its master"):
        tool.pick_layer(["a"], "a", -1)


def occurrence(glyph: Any, layer_name: str = "Regular#b", index: int = 0, block_id: int = 7) -> NS:
    return NS(glyph=glyph, layer_name=layer_name, index=index, block_id=block_id, glyph_name="a")


def capture_with(occurrences: list, editor: bool = True, carriers: list | None = None) -> Any:
    selection = NS(
        context=(None, None, "editor" if editor else "font"),
        occurrences=occurrences,
        carriers=carriers or [],
    )
    return lambda deadline: selection


def plan_tool(host: Host, capture: Any, package: Any = "ok") -> Any:
    tool = layer_tool(host, layer_selection=dict(capture=capture))
    host.package = NS(id=1, masters=list(MASTERS)) if package == "ok" else package
    return tool


def test_plan_when_editor_selection_then_job_per_occurrence(host):
    glyph = glyph_with(("Regular", True), ("Regular#b", True), ("Bold", True), ("Regular#mask", False))
    tool = plan_tool(host, capture_with([occurrence(glyph)]))
    selection, jobs = tool.plan(-1)
    assert jobs == [(selection.occurrences[0], "Regular#b", "Regular")], "plan when editor selection then job per occurrence: expected jobs == [(selection.occurrences[0], 'Regular#b', 'Regular')]"
    selection, jobs = tool.plan(1)
    assert jobs[0][2] == "Regular", "Two body layers wrap in both directions"


def test_plan_when_not_in_glyph_window_then_refused(host):
    tool = plan_tool(host, capture_with([occurrence(glyph_with())], editor=False))
    with pytest.raises(ValueError, match="Activate a Glyph window"):
        tool.plan(-1)


def test_plan_when_no_font_or_no_slots_then_refused(host):
    tool = plan_tool(host, capture_with([occurrence(glyph_with())]), package=None)
    host.package = None
    with pytest.raises(ValueError, match="Select a glyph in a Glyph window first."):
        tool.plan(-1)
    tool = plan_tool(host, capture_with([]))
    with pytest.raises(ValueError, match="Select a glyph in a Glyph window first."):
        tool.plan(-1)


def test_plan_when_one_slot_cannot_cycle_then_whole_run_refused(host):
    good = occurrence(glyph_with(("Regular", True), ("Regular#b", True)), "Regular")
    lone = occurrence(glyph_with(("Bold", True)), "Bold")
    tool = plan_tool(host, capture_with([good, lone]))
    with pytest.raises(ValueError, match="only layer of its master"):
        tool.plan(-1)


class Symbol:
    def __init__(self, layer_name: str) -> None:
        self.layerName = layer_name


class Block:
    """Text block double holding one glyph slot."""

    def __init__(self, layer_name: str, block_id: int = 7) -> None:
        self.id = block_id
        self.symbol = Symbol(layer_name)
        self.changed_calls = 0

    def getGlyphAt(self, index: int) -> NS:  # noqa: N802
        return NS(symbol=self.symbol)

    def changed(self) -> None:
        self.changed_calls += 1


def show_tool(host: Host) -> Any:
    return layer_tool(host, qtsafe=dict(qt_list=lambda items: list(items)))


def test_show_layer_when_slot_has_explicit_layer_then_name_assigned_and_block_changed(host):
    tool = show_tool(host)
    block = Block("Regular#b")
    selection = NS(carriers=[NS(textBlocks=[Block("other", block_id=3), block])])
    tool.show_layer(selection, occurrence(NS()), "Regular")
    assert block.symbol.layerName == "Regular" and block.changed_calls == 1, "show layer when slot has explicit layer then name assigned and block changed: expected block.symbol.layerName == 'Regular' and block.changed_calls == 1"


def test_show_layer_when_slot_follows_active_layer_then_target_made_active(host):
    tool = show_tool(host)
    block = Block("")
    activated: list[str] = []
    glyph = NS(
        findLayer=lambda name: NS(setActive=lambda: activated.append(name)),
        updateActiveLayer=lambda flag: NS(name=activated[-1]),
    )
    selection = NS(carriers=[NS(textBlocks=[block])])
    tool.show_layer(selection, occurrence(glyph), "Regular")
    assert activated == ["Regular"] and block.changed_calls == 1, "show layer when slot follows active layer then target made active: expected activated == ['Regular'] and block.changed_calls == 1"


def test_show_layer_when_font_does_not_switch_then_runtime_error(host):
    tool = show_tool(host)

    class Stubborn(Block):
        @property
        def symbol(self) -> Symbol:
            return Symbol("Regular#b")

        @symbol.setter
        def symbol(self, value: Symbol) -> None:
            pass

    selection = NS(carriers=[NS(textBlocks=[Stubborn("x")])])
    with pytest.raises(RuntimeError, match="did not switch 'a' to layer 'Regular'"):
        tool.show_layer(selection, occurrence(NS()), "Regular")


def test_run_when_planned_then_each_slot_switched_and_reported(host):
    tool = show_tool(host)
    glyph = glyph_with(("Regular", True), ("Regular#b", True))
    block = Block("Regular#b")
    selection_fn = capture_with([occurrence(glyph)], carriers=[NS(textBlocks=[block])])
    host.fake_ap("layer_selection", capture=selection_fn)
    host.package = NS(id=1, masters=list(MASTERS))
    assert tool.run() == ["a: 'Regular#b' -> 'Regular'"], 'run when planned then each slot switched and reported: expected tool.run() == ["a: \'Regular#b\' -> \'Regular\'"]'
    assert block.symbol.layerName == "Regular", "run when planned then each slot switched and reported: expected block.symbol.layerName == 'Regular'"


def test_main_when_switch_succeeds_then_one_line_per_slot_printed(host, capsys):
    tool = show_tool(host)
    glyph = glyph_with(("Regular", True), ("Regular#b", True))
    host.fake_ap("layer_selection", capture=capture_with([occurrence(glyph)], carriers=[NS(textBlocks=[Block("Regular#b")])]))
    host.package = NS(id=1, masters=list(MASTERS))
    tool.main()
    assert capsys.readouterr().out == "Display Previous Layer: a: 'Regular#b' -> 'Regular'\n", 'main when switch succeeds then one line per slot printed: unexpected result'


@pytest.mark.parametrize("error", [ValueError("no slot"), RuntimeError("stuck"), TimeoutError("late")])
def test_main_when_run_refuses_then_reason_printed_not_raised(host, capsys, error):
    tool = show_tool(host)
    tool.run = lambda step=-1: (_ for _ in ()).throw(error)
    tool.main()
    assert capsys.readouterr().out == f"Display Previous Layer: {error}\n", "main when run refuses then reason printed not raised: expected capsys.readouterr().out == f'Display Previous Layer: {error}\\n'"


def test_layer_script_when_run_as_script_then_main_executes(host, capsys):
    show_tool(host)
    host.fake_ap("layer_selection", capture=capture_with([], editor=True))
    host.package = NS(id=1, masters=list(MASTERS))
    runpy.run_path(str(ROOT / "Scripts" / LAYER_PATH), run_name="__main__")
    assert "Select a glyph in a Glyph window first." in capsys.readouterr().out, "layer script when run as script then main executes: expected 'Select a glyph in a Glyph window first.' in capsys.readouterr().out"


# ---- Auto Cursive Attachment Get Sample --------------------------------------------

SAMPLE_PATH = "Anchors/Auto Cursive Attachment Get Sample.py"
SQUARE = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]


def sample_tool(host: Host) -> Any:
    return host.load(SAMPLE_PATH)


def point(x: float, y: float) -> NS:
    return NS(x=lambda: x, y=lambda: y)


def closed_shape(*polygons: list[tuple[float, float]], composite: bool = False, affine: bool = True, open_empty: bool = True) -> NS:
    return NS(
        isComposite=composite,
        transform=NS(isAffine=lambda: affine),
        openedPath=NS(isEmpty=lambda: open_empty),
        closedPath=NS(toSubpathPolygons=lambda transform: [[point(*p) for p in poly] for poly in polygons]),
    )


def test_outline_rings_when_polygon_not_closed_then_first_point_repeated(host):
    tool = sample_tool(host)
    rings = tool.outline_rings(NS(shapes=[closed_shape(SQUARE[:4])]))
    assert rings == [[(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0), (0.0, 0.0)]], 'outline rings when polygon not closed then first point repeated: unexpected result'


def test_outline_rings_when_already_closed_then_unchanged_and_tiny_rings_dropped(host):
    tool = sample_tool(host)
    rings = tool.outline_rings(NS(shapes=[closed_shape(SQUARE, [(0, 0), (1, 1)])]))
    assert rings == [[(float(x), float(y)) for x, y in SQUARE]], "A two-point ring is not an outline"


@pytest.mark.parametrize(
    "shape",
    [
        dict(composite=True),
        dict(affine=False),
        dict(open_empty=False),
    ],
)
def test_outline_rings_when_unsupported_shape_then_refused(host, shape):
    tool = sample_tool(host)
    with pytest.raises(ValueError, match="closed, decomposed outlines"):
        tool.outline_rings(NS(shapes=[closed_shape(SQUARE, **shape)]))


def test_outline_rings_when_non_finite_or_empty_then_refused(host):
    tool = sample_tool(host)
    with pytest.raises(ValueError, match="must be finite"):
        tool.outline_rings(NS(shapes=[closed_shape([(0, 0), (math.inf, 0), (5, 5)])]))
    with pytest.raises(ValueError, match="No closed outline"):
        tool.outline_rings(NS(shapes=[]))


def test_vertical_spans_when_square_then_single_span_between_edges(host):
    tool = sample_tool(host)
    spans = tool.vertical_spans([[(float(x), float(y)) for x, y in SQUARE]], 50.0)
    assert spans == [(0.0, 100.0, 0.0, 0.0)], 'vertical spans when square then single span between edges: expected spans == [(0.0, 100.0, 0.0, 0.0)]'
    assert tool.vertical_spans([[(float(x), float(y)) for x, y in SQUARE]], 150.0) == [], "Outside the ink"


def test_vertical_spans_when_hole_then_two_spans_around_counter(host):
    tool = sample_tool(host)
    outer = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0), (0.0, 0.0)]
    hole = [(30.0, 30.0), (30.0, 70.0), (70.0, 70.0), (70.0, 30.0), (30.0, 30.0)]
    spans = tool.vertical_spans([outer, hole], 50.0)
    assert [(lo, hi) for lo, hi, _, _ in spans] == [(0.0, 30.0), (70.0, 100.0)], 'vertical spans when hole then two spans around counter: expected [(lo, hi) for lo, hi, _, _ in spans] == [(0.0, 30.0), (70.0, 100.0)]'


def test_measure_sample_when_points_inside_then_mean_thickness_fractions(host):
    tool = sample_tool(host)
    rings = [[(float(x), float(y)) for x, y in SQUARE]]
    sample = tool.measure_sample(rings, [(50.0, 20.0), (50.0, 60.0)])
    assert sample["below"] == pytest.approx(40.0) and sample["above"] == pytest.approx(60.0), "measure sample when points inside then mean thickness fractions: unexpected result"
    assert sample["lower_angle"] == pytest.approx(0.0) and sample["upper_angle"] == pytest.approx(0.0), "measure sample when points inside then mean thickness fractions: unexpected result"


def test_measure_sample_when_no_points_or_point_in_counter_then_refused(host):
    tool = sample_tool(host)
    rings = [[(float(x), float(y)) for x, y in SQUARE]]
    with pytest.raises(ValueError, match="Create an entry or exit anchor"):
        tool.measure_sample(rings, [])
    with pytest.raises(ValueError, match="must lie inside closed ink"):
        tool.measure_sample(rings, [(500.0, 20.0)])


def test_validate_profile_when_valid_then_floats_returned(host):
    tool = sample_tool(host)
    profile = tool.validate_profile({"below": 1, "above": "2", "lower_angle": 0, "upper_angle": 0.5})
    assert profile == {"below": 1.0, "above": 2.0, "lower_angle": 0.0, "upper_angle": 0.5}, "validate profile when valid then floats returned: unexpected result"


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"below": 1}, "four numeric"),
        (None, "four numeric"),
        ({"below": "x", "above": 1, "lower_angle": 0, "upper_angle": 0}, "four numeric"),
        ({"below": math.nan, "above": 1, "lower_angle": 0, "upper_angle": 0}, "must be finite"),
        ({"below": -1, "above": 5, "lower_angle": 0, "upper_angle": 0}, "positive ink thickness"),
        ({"below": 0, "above": 0, "lower_angle": 0, "upper_angle": 0}, "positive ink thickness"),
    ],
)
def test_validate_profile_when_invalid_then_refused(host, data, message):
    tool = sample_tool(host)
    with pytest.raises(ValueError, match=message):
        tool.validate_profile(data)


def pin(name: str, x: float, y: float) -> NS:
    return NS(name=name, x=x, y=y)


def sample_layer(*pins: NS) -> NS:
    return NS(shapes=[closed_shape(SQUARE)], anchors=list(pins), name="Regular", isMaskLayer=False, isService=False)


def test_sample_document_when_entry_and_exit_then_portable_profile(host):
    tool = sample_tool(host)
    host.fake_ap("anchor_writer", raw_point=lambda p: (p.x, p.y))
    document = tool.sample_document(sample_layer(pin("entry", 50, 25), pin("exit", 50, 75), pin("other", 1, 1)), "Regular")
    assert document["format"] == "fontlab-cursive-sample-1" and document["master"] == "Regular", "sample document when entry and exit then portable profile: unexpected result"
    assert document["profile"]["below"] == pytest.approx(50.0), "Mean of 25 and 75"


def test_sample_document_when_duplicate_names_then_refused(host):
    tool = sample_tool(host)
    host.fake_ap("anchor_writer", raw_point=lambda p: (p.x, p.y))
    with pytest.raises(ValueError, match="names must be unique"):
        tool.sample_document(sample_layer(pin("entry", 50, 25), pin("entry", 50, 75)), "Regular")


def test_save_document_when_new_path_then_utf8_json_written_and_existing_refused(host, tmp_path):
    tool = sample_tool(host)
    target = tmp_path / "sample.json"
    tool.save_document(str(target), {"master": "Řegular"})
    assert json.loads(target.read_text(encoding="utf-8")) == {"master": "Řegular"}, "save document when new path then utf8 json written and existing refused: unexpected result"
    assert target.read_text(encoding="utf-8").endswith("}\n"), "save document when new path then utf8 json written and existing refused: expected target.read_text(encoding='utf-8').endswith('}\\n')"
    with pytest.raises(ValueError, match="Choose a new file name"):
        tool.save_document(str(target), {"master": "other"})
    assert json.loads(target.read_text(encoding="utf-8")) == {"master": "Řegular"}, "Existing file untouched"


class Dialogs:
    """qt_dialogs double: runs the script's chooser configuration and records message boxes."""

    def __init__(self, paths: list[str]) -> None:
        self.paths = paths
        self.configured: list[tuple] = []
        self.messages: list[tuple] = []

    def run_file_dialog(self, qt_gui: Any, configure: Any, title: str, start: str) -> list[str]:
        calls: list[tuple] = []
        recorder = NS(**{n: (lambda *a, n=n: calls.append((n, *a))) for n in (
            "setAcceptMode", "setOption", "setFileMode", "setNameFilter", "setDefaultSuffix")})
        kind = NS(AcceptSave=1, DontConfirmOverwrite=2, AnyFile=3)
        configure(kind, recorder)
        self.configured.append((title, start, calls))
        return self.paths

    def create_message_box(self, qt_gui: Any, title: str, text: str, icon: str) -> NS:
        box = NS(title=title, text=text, icon=icon)
        self.messages.append((title, text, icon))
        return box

    def run_message_box(self, box: Any, ok: Any) -> None:
        self.messages.append(("ran", box.text))


def sample_main(host: Host, paths: list[str], occurrences: list | None = None, layer: NS | None = None, package: Any = "ok") -> tuple[Any, Dialogs]:
    tool = host.load(SAMPLE_PATH, modules=("masters",))
    layer = layer or sample_layer(pin("entry", 50, 25))
    occ = [NS(layer=layer)] if occurrences is None else occurrences
    host.fake_ap("layer_selection", capture=lambda deadline: NS(occurrences=occ))
    host.fake_ap("anchor_writer", raw_point=lambda p: (p.x, p.y))
    dialogs = Dialogs(paths)
    host.fake_ap("qt_dialogs", run_file_dialog=dialogs.run_file_dialog, create_message_box=dialogs.create_message_box, run_message_box=dialogs.run_message_box)
    host.qt.QtGui.QMessageBox = NS(Ok=1)
    host.package = NS(id=1, masters=["Regular", "Bold"]) if package == "ok" else package
    return tool, dialogs


def test_main_when_layer_sampled_then_document_saved_and_returned(host, tmp_path, capsys):
    target = tmp_path / "out.json"
    tool, dialogs = sample_main(host, [str(target)])
    document = tool.main()
    assert document["master"] == "Regular" and json.loads(target.read_text())["format"] == "fontlab-cursive-sample-1", "main when layer sampled then document saved and returned: unexpected result"
    assert f"Saved cursive sample: {target}" in capsys.readouterr().out, "main when layer sampled then document saved and returned: expected f'Saved cursive sample: {target}' in capsys.readouterr().out"
    title, start, calls = dialogs.configured[0]
    assert title == "Auto Cursive Attachment Get Sample" and start == str(Path.home()), "main when layer sampled then document saved and returned: unexpected result"
    assert ("setNameFilter", "Cursive sample (*.json)") in calls and ("setDefaultSuffix", "json") in calls, "main when layer sampled then document saved and returned: unexpected result"
    assert ("setAcceptMode", 1) in calls and ("setOption", 2, True) in calls and ("setFileMode", 3) in calls, "main when layer sampled then document saved and returned: unexpected result"


def test_main_when_chooser_cancelled_then_nothing_saved(host, tmp_path):
    tool, dialogs = sample_main(host, [])
    assert tool.main() is None and dialogs.messages == [], "Cancel is silent"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (dict(occurrences=[]), "Select exactly one glyph layer in an open font."),
        (dict(occurrences=[NS(layer=None), NS(layer=None)]), "Select exactly one glyph layer in an open font."),
        (dict(package=None), "Select exactly one glyph layer in an open font."),
    ],
)
def test_main_when_selection_unusable_then_warning_box(host, kwargs, message):
    tool, dialogs = sample_main(host, ["unused"], **kwargs)
    if kwargs.get("package", "ok") is None:
        host.package = None
    assert tool.main() is None, 'main when selection unusable then warning box: expected tool.main() is None'
    assert dialogs.messages[0] == ("Auto Cursive Attachment Get Sample", message, "Warning"), "main when selection unusable then warning box: unexpected result"


def test_main_when_mask_or_service_layer_then_body_layer_requested(host):
    layer = sample_layer(pin("entry", 50, 25))
    layer.isMaskLayer = True
    tool, dialogs = sample_main(host, ["unused"], layer=layer)
    assert tool.main() is None and dialogs.messages[0][1] == "Choose a body layer for the sample.", "main when mask or service layer then body layer requested: unexpected result"
    layer.isMaskLayer, layer.isService = False, True
    tool.main()
    assert dialogs.messages[-2][1] == "Choose a body layer for the sample.", "main when mask or service layer then body layer requested: expected dialogs.messages[-2][1] == 'Choose a body layer for the sample.'"


def test_main_when_layer_has_no_master_then_warning_box(host):
    layer = sample_layer(pin("entry", 50, 25))
    layer.name = "Mystery"
    tool, dialogs = sample_main(host, ["unused"], layer=layer)
    assert tool.main() is None and dialogs.messages[0][1] == "The layer has no associated font master.", "main when layer has no master then warning box: unexpected result"


def test_main_when_target_exists_then_warning_box_and_file_untouched(host, tmp_path):
    target = tmp_path / "exists.json"
    target.write_text("keep")
    tool, dialogs = sample_main(host, [str(target)])
    assert tool.main() is None, 'main when target exists then warning box and file untouched: expected tool.main() is None'
    assert dialogs.messages[0][1].startswith("Choose a new file name") and target.read_text() == "keep", "main when target exists then warning box and file untouched: unexpected result"


def test_main_when_folder_missing_then_os_error_shown(host, tmp_path):
    tool, dialogs = sample_main(host, [str(tmp_path / "no" / "such" / "dir.json")])
    assert tool.main() is None and dialogs.messages[0][2] == "Warning", "main when folder missing then os error shown: expected tool.main() is None and dialogs.messages[0][2] == 'Warning'"
    assert "No such file" in dialogs.messages[0][1], "main when folder missing then os error shown: expected 'No such file' in dialogs.messages[0][1]"


def test_main_when_run_as_script_then_sampler_executes(host, tmp_path):
    target = tmp_path / "script.json"
    sample_main(host, [str(target)])
    runpy.run_path(str(ROOT / "Scripts" / SAMPLE_PATH), run_name="__main__")
    assert target.is_file(), "The main guard runs the whole flow"
