# this_file: tests/test_issue122_G17.py
# SPDX-License-Identifier: Apache-2.0
"""Selection navigation tests with owned FontLab/Qt doubles; no native proof."""

import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Masters/Selection Layer Navigator.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("navigator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stub(patch: Any, name: str, **members: Any) -> Any:
    module = ModuleType(name)
    module.__dict__.update(members)
    patch.setitem(sys.modules, name, module)
    if "." in name:
        parent, _, child = name.rpartition(".")
        if parent not in sys.modules:
            stub(patch, parent, __path__=[])
        patch.setitem(vars(sys.modules[parent]), child, module)
    return module


@pytest.mark.parametrize(
    "current,step,want", [("A", 1, "B"), ("B", 1, "A"), ("A", -1, "B")]
)
def test_order_wraps(current: str, step: int, want: str) -> None:
    assert load().ordered_target(["A", "B"], current, step) == want


@pytest.mark.parametrize(
    "names,current,step",
    [
        ([], "A", 1),
        (["A"], "A", 1),
        (["A", "A"], "A", 1),
        (["A", "B"], "C", 1),
        (["A", "B"], "A", 0),
    ],
)
def test_bad_order_is_refused(names: list, current: str, step: int) -> None:
    with pytest.raises(ValueError):
        load().ordered_target(names, current, step)


@pytest.mark.parametrize(
    "axis,step,want", [(0, 1, "Heavy"), (0, -1, "Heavy"), (1, 1, "Wide")]
)
def test_axis_keeps_other_coordinates(axis: int, step: int, want: str) -> None:
    rows = [
        ("Wide", (0.0, 100.0)),
        ("Heavy", (900.0, 0.0)),
        ("Light", (0.0, 0.0)),
        ("HeavyWide", (900.0, 100.0)),
    ]
    assert load().axis_target(rows, "Light", axis, step) == want


def test_axis_sorts_and_wraps() -> None:
    rows = [("A", (100.0,)), ("C", (900.0,)), ("B", (500.0,))]
    mod = load()
    assert mod.axis_target(rows, "A", 0, 1) == "B"
    assert mod.axis_target(rows, "C", 0, 1) == "A"
    assert mod.axis_target(rows, "A", 0, -1) == "C"


@pytest.mark.parametrize(
    "rows,current,axis",
    [
        ([("A", (0.0,))], "A", 0),
        ([("A", (0.0,)), ("B", (float("nan"),))], "A", 0),
        ([("A", (0.0,)), ("B", (1.0, 2.0))], "A", 0),
        ([("A", (0.0,)), ("B", (1.0,))], "A", 1),
        ([("A", (0.0,)), ("B", (1.0,)), ("C", (1.0,))], "A", 0),
    ],
)
def test_axis_refuses_missing_or_ambiguous_locations(
    rows: list, current: str, axis: int
) -> None:
    with pytest.raises(ValueError):
        load().axis_target(rows, current, axis, 1)


class Body:
    def __init__(self, name: str, weight: float | None, **flags: Any) -> None:
        self.name, self.isNull = name, False
        self.isService = flags.get("service", False)
        self.isLocked = flags.get("locked", False)
        self.owner = None
        self.isMaskLayer = flags.get("mask", False)
        self.position = None if weight is None else {"wt": weight, "it": 0.0}

    def setActive(self) -> None:
        self.owner.activeLayer = self

    def getMasterPosition(self) -> dict | None:
        return self.position


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    package = NS(
        id=7,
        fgId=700,
        master="Light",
        masters=["Light", "Bold"],
        axes=[NS(shortName="wt", tag="wght"), NS(shortName="it", tag="ital")],
    )
    package.location = lambda name: {"wt": 0.0 if name == "Light" else 900.0, "it": 0.0}
    calls = []
    package.setMaster = lambda name, notify: (
        calls.append((name, notify)),
        setattr(package, "master", name),
    )
    glyph = NS(
        id=8,
        name="A",
        layers=[
            Body("Light", 0.0),
            Body("Middle", 500.0),
            Body("Bold", 900.0),
            Body("mask.Light", None, mask=True),
        ],
    )
    glyph.findLayer = lambda name: next(
        (layer for layer in glyph.layers if layer.name == name), None
    )
    glyph.activeLayer = glyph.layers[0]
    glyph.updateActiveLayer = lambda assign: glyph.activeLayer
    for layer in glyph.layers:
        layer.owner = glyph
    infos = [
        NS(glyph=glyph, symbol=NS(layerName=""), isSelected=True, isActive=False),
        NS(glyph=glyph, symbol=NS(layerName="Bold"), isSelected=True, isActive=False),
    ]
    rows = tuple(
        NS(
            package=package,
            glyph=glyph,
            glyph_id=8,
            glyph_name="A",
            layer=glyph.findLayer(name),
            layer_name=name,
            index=i,
            block_id=11,
        )
        for i, name in enumerate(["Light", "Bold"])
    )
    block = NS(
        id=11, getGlyphAt=lambda i: infos[i], changed=lambda: calls.append("changed")
    )
    selection = NS(
        context=(7, "Light", "editor"),
        occurrences=rows,
        carriers=(NS(textBlocks=[block]),),
    )
    stub(
        monkeypatch,
        "fly.ap.layer_selection",
        capture=lambda deadline: selection,
        document_context=lambda deadline: selection.context,
    )
    stub(monkeypatch, "fly.ap.scripting", current_package=lambda: package)
    stub(monkeypatch, "fly.ap.qtsafe", qt_list=list)
    stub(
        monkeypatch,
        "fly.ap.master_switcher",
        switch=lambda p, name: p.setMaster(name, True),
    )
    return NS(
        package=package,
        selection=selection,
        infos=infos,
        glyph=glyph,
        calls=calls,
        patch=monkeypatch,
    )


def test_same_name_sync_uses_first_occurrence_and_keeps_missing(host: Any) -> None:
    other = NS(id=9, name="V", layers=[Body("Light", 0.0)])
    row = NS(
        package=host.package,
        glyph=other,
        glyph_id=9,
        glyph_name="V",
        layer=other.layers[0],
        layer_name="Light",
        index=2,
        block_id=11,
    )
    host.selection.occurrences += (row,)
    messages = load().navigate(None, 1, 7)
    assert [x.symbol.layerName for x in host.infos] == ["", "Middle"]
    assert any("kept V" in line for line in messages)
    assert host.calls == ["changed", "changed"]


def test_axis_handles_intermediate_and_repeated_glyph_slots(host: Any) -> None:
    messages = load().navigate("wt", 1, 7)
    assert [x.symbol.layerName for x in host.infos] == ["", "Light"]
    assert len(messages) == 2
    assert host.package.master == "Light"


def test_font_window_axis_switches_master_with_readback(host: Any) -> None:
    host.selection.context = (7, "Light", "font")
    host.selection.occurrences = ()
    assert "Bold" in load().navigate("wt", 1, 7)[0]
    assert host.calls == [("Bold", True)]


@pytest.mark.parametrize(
    "change,match",
    [
        ("font", "current font"),
        ("none", "Open a font"),
        ("empty", "Select"),
        ("font-order", "Glyph window"),
        ("axis", "axis"),
    ],
)
def test_context_refusals(host: Any, change: str, match: str) -> None:
    mode = None
    if change == "font":
        host.package.id = 99
    elif change == "none":
        stub(host.patch, "fly.ap.scripting", current_package=lambda: None)
    elif change == "empty":
        host.selection.occurrences = ()
    elif change == "font-order":
        host.selection.context = (7, "Light", "font")
    else:
        mode = "missing"
    with pytest.raises(ValueError, match=match):
        load().navigate(mode, 1, 7)
    assert not host.calls


def test_bad_occurrence_does_not_stop_other_slots(host: Any) -> None:
    host.selection.occurrences[0].layer_name = "sketch"
    result = load().navigate("wt", 1, 7)
    assert "kept A" in result[0]
    assert host.infos[1].symbol.layerName == "Light"


def test_document_change_stops_before_display_writes(host: Any) -> None:
    stub(
        host.patch,
        "fly.ap.layer_selection",
        capture=lambda deadline: host.selection,
        document_context=lambda deadline: (99, "Light", "editor"),
    )
    with pytest.raises(ValueError, match="changed"):
        load().navigate("wt", 1, 7)
    assert not host.calls


def test_axis_selection_uses_italic_tag(host: Any) -> None:
    assert load().axis_index(host.package, "italic") == 1
    host.package.axes = [NS(shortName="sl", tag="slnt")]
    assert load().axis_index(host.package, "italic") == 0
    host.package.axes = []
    with pytest.raises(ValueError, match="axis"):
        load().axis_index(host.package, "italic")


def test_real_installed_app_public_names() -> None:
    assert SCRIPT.is_file(), "Navigator must exist before checking imports"
    used = app_names_used([SCRIPT])
    assert used, "The script must use public App helpers"
    check_real_app_names(used)


def test_public_script_has_no_font_writers_or_native_member_collisions() -> None:
    tree = ast.parse(SCRIPT.read_text())
    banned = {"render", "size", "layout", "update", "font", "move", "statusBar"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert (
                not {
                    child.name
                    for child in node.body
                    if isinstance(child, ast.FunctionDef)
                }
                & banned
            )
        if isinstance(node, ast.Attribute):
            assert node.attr not in {
                "notifyChangesApplied",
                "initHistoryState",
                "fgGlyph",
                "fgPackage",
                "addGlyph",
            }
    assert "slobzheninov/Glyphs-Scripts" in ast.get_docstring(tree)


@pytest.mark.parametrize(
    "field,value",
    [("isSelected", False), ("glyph", NS(id=99)), ("symbol", NS(layerName="Bold"))],
)
def test_changed_slot_is_kept_and_other_occurrence_continues(
    host: Any, field: str, value: Any
) -> None:
    setattr(host.infos[0], field, value)
    result = load().navigate("wt", 1, 7)
    assert "kept A" in result[0]
    assert host.infos[1].symbol.layerName == "Light"


def test_write_failure_reports_possible_display_change(host: Any) -> None:
    count = []

    def fail_once() -> None:
        count.append(1)
        if len(count) == 1:
            raise RuntimeError("paint failed")

    host.selection.carriers[0].textBlocks[0].changed = fail_once
    result = load().navigate("wt", 1, 7)
    assert "Display may have changed" in result[0]
    assert not result[0].startswith("kept")
    assert host.infos[1].symbol.layerName == "Light"


def test_master_write_readback_failure_is_reported(host: Any) -> None:
    host.selection.context = (7, "Light", "font")
    stub(host.patch, "fly.ap.master_switcher", switch=lambda *a: None)
    with pytest.raises(RuntimeError, match="did not switch"):
        load().navigate("wt", 1, 7)


def test_capture_timeout_is_reported(host: Any) -> None:
    def expire(deadline: float) -> None:
        raise TimeoutError("capture expired")

    stub(host.patch, "fly.ap.layer_selection", capture=expire)
    with pytest.raises(TimeoutError, match="expired"):
        load().navigate("wt", 1, 7)
    assert not host.calls


class Signal:
    def __init__(self) -> None:
        self.slots = []

    def connect(self, callback: Any) -> None:
        self.slots.append(callback)

    def disconnect(self, callback: Any) -> None:
        self.slots.remove(callback)

    def emit(self, *args: Any) -> None:
        for callback in tuple(self.slots):
            callback(*args)


class Widget:
    FORBIDDEN = frozenset(
        {"render", "size", "layout", "update", "font", "move", "statusBar"}
    )

    def __init__(self, *args: Any) -> None:
        self.clicked = Signal()
        self.text_value = str(args[0]) if args and isinstance(args[0], str) else ""
        self.currentIndex = 0
        self.items = []
        self.children = []
        self.closed = False
        self.modal = True

    def __setattr__(self, key: str, value: Any) -> None:
        assert key not in self.FORBIDDEN, f"Native widget member collision: {key}"
        object.__setattr__(self, key, value)

    def setWindowTitle(self, value: str) -> None:
        self.caption = value

    def setModal(self, value: bool) -> None:
        self.modal = value

    def resize(self, *args: Any) -> None:
        pass

    def setReadOnly(self, value: bool) -> None:
        self.read_only = value

    def setPlainText(self, value: str) -> None:
        self.text_value = value

    def addWidget(self, widget: Any) -> None:
        self.children.append(widget)

    def addLayout(self, widget: Any) -> None:
        self.children.append(widget)

    def clear(self) -> None:
        self.items.clear()
        self.currentIndex = 0

    def addItem(self, value: str) -> None:
        self.items.append(value)

    def close(self) -> bool:
        self.closeEvent(NS())
        return True


@pytest.fixture
def ui(host: Any) -> Any:
    def connect(dialog: Any, signal: Any, callback: Any) -> None:
        signal.connect(callback)
        dialog._connections.append((signal, callback))

    def close(dialog: Any, event: Any, key: str) -> None:
        for signal, callback in dialog._connections:
            signal.disconnect(callback)
        dialog._connections.clear()
        dialog.closed = True

    module = sys.modules["fly.ap.scripting"]
    module.connect_guarded = connect
    module.close_script_dialog = close
    module.show_script_dialog = lambda cls, key: cls()
    stub(
        host.patch,
        "fly.qt",
        QtGui=NS(
            **{
                name: Widget
                for name in (
                    "QDialog",
                    "QVBoxLayout",
                    "QHBoxLayout",
                    "QComboBox",
                    "QLabel",
                    "QPlainTextEdit",
                    "QPushButton",
                )
            }
        ),
    )
    return NS(host=host, module=load())


def test_modeless_panel_binds_axes_and_close_disconnects_owned_slots(ui: Any) -> None:
    panel = ui.module.main()
    assert panel.modal is False
    assert panel.options == [None, "wt", "it", "italic"]
    assert panel.results.read_only is True
    assert len(panel._connections) == 4
    signals = [signal for signal, _ in panel._connections]
    panel.close()
    assert panel.closed and not panel._connections
    assert all(not signal.slots for signal in signals)


def test_panel_buttons_accept_native_clicked_boolean(ui: Any) -> None:
    panel = ui.module.main()
    panel.mode_box.currentIndex = 1
    panel._connections[2][0].emit(False)
    assert "Middle" in panel.results.text_value
    panel._connections[3][0].emit(False)
    assert panel.closed


def test_panel_retains_current_font_binding_and_rebinds_explicitly(ui: Any) -> None:
    panel = ui.module.main()
    ui.host.package.id = 99
    panel.travel(1)
    assert "Use Current Font" in panel.results.text_value
    panel.bind_font()
    assert panel.bound_id == 99


def test_panel_no_font_and_axis_refusal_show_actionable_text(ui: Any) -> None:
    sys.modules["fly.ap.scripting"].current_package = lambda: None
    panel = ui.module.main()
    assert "Open a font" in panel.results.text_value
    panel.travel(1)
    assert "Open a font" in panel.results.text_value


def test_main_reports_lifecycle_runtime_error(ui: Any, capsys: Any) -> None:
    def fail(*args: Any) -> None:
        raise RuntimeError("cannot open panel")

    sys.modules["fly.ap.scripting"].show_script_dialog = fail
    assert ui.module.main() is None
    assert "cannot open panel" in capsys.readouterr().out


@pytest.mark.parametrize("axis", range(4))
def test_each_of_first_four_axes_is_independent(axis: int) -> None:
    origin = (0.0, 0.0, 0.0, 0.0)
    target = tuple(100.0 if i == axis else 0.0 for i in range(4))
    wrong = (200.0, 200.0, 200.0, 200.0)
    assert (
        load().axis_target([("A", origin), ("B", target), ("C", wrong)], "A", axis, 1)
        == "B"
    )


def test_body_layer_filter_keeps_auto_and_excludes_masks_and_services(
    host: Any,
) -> None:
    host.glyph.layers += [Body("service", None, service=True)]
    host.glyph.layers[1].autoLayer = True
    assert [x.name for x in load().body_layers(host.glyph)] == [
        "Light",
        "Middle",
        "Bold",
    ]


def test_incomplete_intermediate_positions_are_omitted_without_guessing(
    host: Any,
) -> None:
    host.glyph.layers[1].position = {"wt": 500.0}
    assert load().positioned(host.package, load().body_layers(host.glyph)) == [
        ("Light", (0.0, 0.0)),
        ("Bold", (900.0, 0.0)),
    ]


def test_malformed_master_location_is_an_actionable_refusal(host: Any) -> None:
    host.selection.context = (7, "Light", "font")
    host.package.location = lambda name: {"wt": None}
    with pytest.raises(ValueError, match="incomplete"):
        load().navigate("wt", 1, 7)


def test_selection_capture_and_package_must_name_same_master(host: Any) -> None:
    host.selection.context = (7, "Different", "editor")
    with pytest.raises(ValueError, match="master changed"):
        load().navigate("wt", 1, 7)
    assert not host.calls


def test_missing_block_is_kept_and_display_readback_failure_is_not_called_kept(
    host: Any,
) -> None:
    host.selection.occurrences[0].block_id = 99
    result = load().navigate("wt", 1, 7)
    assert "kept A" in result[0] and "block changed" in result[0]
    assert host.infos[1].symbol.layerName == "Light"


def test_display_readback_failure_reports_possible_change(host: Any) -> None:
    class Ignored:
        @property
        def layerName(self) -> str:
            return "Light"

        @layerName.setter
        def layerName(self, value: str) -> None:
            pass

    host.infos[0].symbol = Ignored()
    result = load().navigate("wt", 1, 7)
    assert "Display may have changed" in result[0]
    assert host.infos[1].symbol.layerName == "Light"


def test_deadline_keeps_each_remaining_occurrence_by_name(
    host: Any, monkeypatch: Any
) -> None:
    mod = load()
    ticks = iter([0.0, 3.0, 3.0])
    monkeypatch.setattr(mod, "monotonic", lambda: next(ticks))
    result = mod.navigate("wt", 1, 7)
    assert len(result) == 2 and all(
        "kept A" in line and "time limit" in line for line in result
    )
    assert not host.calls


def test_public_source_is_python311_and_has_no_process_wording() -> None:
    source = SCRIPT.read_text()
    ast.parse(source, feature_version=(3, 11))
    for term in ("issue 122", "G17", "G1-style", "archived", "unresolved", "draft"):
        assert term not in source, term


@pytest.mark.parametrize("step", [-1, 1])
def test_layer_order_skips_locked_targets(host: Any, step: int) -> None:
    host.glyph.layers[1].isLocked = True
    result = load().navigate(None, step, 7)
    assert "Light -> Bold" in result[0], (
        "Locked Middle must be skipped in both directions"
    )
    assert all("-> Middle" not in line for line in result)


def test_default_follow_slot_stays_implicit_and_updates_active_layer(host: Any) -> None:
    result = load().navigate("wt", 1, 7)
    assert "Light -> Middle" in result[0]
    assert host.infos[0].symbol.layerName == "", (
        "Default-follow slots must remain implicit"
    )
    assert host.glyph.activeLayer.name == "Middle", (
        "Following slot must show the new active layer"
    )


@pytest.mark.parametrize("layers", [[], ["Light"], ["Light", "Light"]])
def test_unusable_reference_is_named_and_next_reference_moves_selection(
    host: Any, layers: list[str]
) -> None:
    bad = NS(id=9, name="V", layers=[Body(name, 0.0) for name in layers])
    first = host.selection.occurrences[0]
    first.glyph = bad
    first.glyph_id = 9
    first.glyph_name = "V"
    host.infos[0].glyph = bad
    result = load().navigate(None, 1, 7)
    assert result[0].startswith("kept V:"), "Reference refusal must name its glyph"
    assert "reference" in result[0]
    assert host.infos[1].symbol.layerName == "Light", (
        "Next usable reference must still navigate"
    )


def test_all_unusable_references_produce_named_kept_rows(host: Any) -> None:
    host.glyph.layers = [host.glyph.layers[0]]
    result = load().navigate(None, 1, 7)
    assert len(result) == 2 and all(line.startswith("kept A:") for line in result)
    assert not host.calls


def test_native_navigation_scope_and_shortcuts_are_documented() -> None:
    doc = ast.get_docstring(ast.parse(SCRIPT.read_text()))
    assert "Layer > Next" in doc and "Alt+." in doc and "Alt+," in doc
    assert "active glyph only" in doc


def test_locked_target_in_another_glyph_is_kept_while_reference_moves(
    host: Any,
) -> None:
    other = NS(
        id=9, name="V", layers=[Body("Light", 0.0), Body("Middle", 500.0, locked=True)]
    )
    second = host.selection.occurrences[1]
    second.glyph, second.glyph_id, second.glyph_name = other, 9, "V"
    second.layer_name = "Light"
    host.infos[1].glyph = other
    host.infos[1].symbol.layerName = "Light"
    result = load().navigate(None, 1, 7)
    assert host.glyph.activeLayer.name == "Middle"
    assert result[1].startswith("kept V:")
    assert host.infos[1].symbol.layerName == "Light"


def test_default_follow_readback_failure_is_reported_without_fixing_the_slot(
    host: Any,
) -> None:
    host.glyph.layers[1].setActive = lambda: None
    result = load().navigate("wt", 1, 7)
    assert "Display may have changed" in result[0]
    assert host.infos[0].symbol.layerName == ""
    assert host.infos[1].symbol.layerName == "Light"
