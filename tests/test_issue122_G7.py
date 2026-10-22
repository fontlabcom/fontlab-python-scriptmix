# this_file: tests/test_issue122_G7.py
"""Owned FontLab doubles; real installed App writers and history, without a host."""

import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    ROOT / "Scripts/Utilities/Magic Remover.py",
    ROOT / "Scripts/Masters/Set Intermediate Layer.py",
)
NATIVE_MEMBERS = {"render", "size", "layout", "update", "font", "move", "statusBar"}


class Owned:
    """A native object with observable history initialization."""

    serial = 0

    def __init__(self) -> None:
        Owned.serial += 1
        self.id = Owned.serial
        self.history: list[int] = []
        self.isNull = False

    def checkInitHistoryState(self, index: int) -> None:
        self.history.append(index)


class Node:
    def __init__(self, x: float = 0, y: float = 0, *, nodeType: str = "on") -> None:
        self.x, self.y, self.type = x, y, nodeType
        self.selected = False

    def isOn(self) -> bool:
        return self.type == "on"


class Contour(Owned):
    def __init__(self, nodes: list[Node], *, closed: bool = True) -> None:
        super().__init__()
        self._nodes, self.closed, self.isTT = nodes, closed, False

    def nodes(self) -> list[Node]:
        return list(self._nodes)

    def removeAt(self, index: int) -> None:
        self._nodes.pop(index)


class Matrix:
    def m11(self) -> int:
        return 1

    m22 = m11

    def m12(self) -> int:
        return 0

    m21 = dx = dy = m12


class Shape(Owned):
    def __init__(self, contours: list[Contour], base: str = "") -> None:
        super().__init__()
        self.contours, self.isComponent, self.selected = contours, bool(base), False
        self.contentLocked = False
        self.transform = Matrix()
        self.shapeData = NS(
            referenceCount=1, componentGlyph=base, componentLayer="", builder=Owned()
        )

    def removeContour(self, contour: Contour) -> None:
        self.contours.remove(contour)

    def changed(self) -> None:
        pass


class Layer(Owned):
    def __init__(self, name: str, shapes: list[Shape] | None = None) -> None:
        super().__init__()
        self.name, self.shapes, self.anchors = name, shapes or [], []
        self.autoLayer = self.isLocked = self.isService = self.isMaskLayer = (
            self.isImg
        ) = False
        self.isMasterLayer = True
        self.position = {"wt": 0.0 if name == "Light" else 1000.0}
        self.advanceWidth = 500.0
        self.fail_update = False

    def removeShape(self, shape: Shape) -> None:
        self.shapes.remove(shape)

    def removeAnchor(self, pin: Any) -> None:
        self.anchors.remove(pin)

    def getMasterPosition(self) -> Any:
        return NativeLocation(self.position)

    def isCompatible(self, other: Any, strong: bool) -> bool:
        return len(self.shapes) == len(other.shapes)

    def changed(self) -> None:
        pass

    def update(self) -> bool:
        return not self.fail_update


class NativeLocation:
    """The binding exposes subscripting; do not assume mapping iteration."""

    def __init__(self, values: dict[str, float]) -> None:
        self.values = values

    def __getitem__(self, key: str) -> float | None:
        assert isinstance(key, str), "Native locations accept string keys"
        return self.values.get(key)

    def __contains__(self, key: str) -> bool:
        raise TypeError("Native location is not iterable")


class Glyph(Owned):
    def __init__(self, name: str, layers: list[Layer]) -> None:
        super().__init__()
        self.name, self.layers, self.lastModified = name, layers, None
        self.fail_interpolation = False

    def findLayer(self, name: str) -> Layer | None:
        return next((x for x in self.layers if x.name == name), None)

    def addLayer(self, layer: Layer) -> None:
        self.layers.append(layer)

    def interpolateInstance(
        self, location: dict[str, float], rounding: bool
    ) -> Layer | None:
        assert rounding is False, "Interpolation must keep fractional coordinates"
        if self.fail_interpolation:
            return None
        result = Layer("")
        result.position = dict(location)
        result.advanceWidth = 500 + location["wt"] / 10
        return result


class PanelBase:
    """Reject QWidget member collisions even when the panel base is doubled."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in NATIVE_MEMBERS:
            raise AssertionError(f"Native member collision: {name}")
        object.__setattr__(self, name, value)


class Pin:
    """Only a bound pin name; reading a selection member must fail."""

    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


class QtWidget(PanelBase):
    """Minimal Qt below the real SelectionPanel; no App panel replacement."""

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.clicked, self.valueChanged = Signal(), Signal()
        self.value, self.enabled, self.visible = 0.0, True, False
        self.row_count = 0
        self.items: dict[tuple[int, int], Any] = {}

    @property
    def font(self) -> Any:
        return NS(
            pointSizeF=lambda: 12,
            setPointSizeF=lambda value: None,
            setBold=lambda value: None,
        )

    def __getattr__(self, name: str) -> Any:
        if name in {
            "setWindowTitle",
            "setMinimumWidth",
            "setContentsMargins",
            "setSpacing",
            "addWidget",
            "addLayout",
            "setFont",
            "setWordWrap",
            "setHorizontalSpacing",
            "setHorizontalHeaderLabels",
            "setVisible",
            "setEditTriggers",
            "setSectionResizeMode",
            "setMinimumHeight",
            "setDefault",
            "setTextAlignment",
            "raise_",
            "deleteLater",
        }:
            return lambda *args: None
        raise AttributeError(name)

    def setText(self, text: str) -> None:
        self.text = text

    def setEnabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def setRowCount(self, count: int) -> None:
        self.row_count = count
        self.items.clear()

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.items[row, column] = item

    def verticalHeader(self) -> Any:
        return self

    horizontalHeader = verticalHeader

    def setDecimals(self, decimals: int) -> None:
        self.decimals = decimals

    def setRange(self, low: float, high: float) -> None:
        self.bounds = low, high

    def setValue(self, value: float) -> None:
        self.value = value

    def show(self) -> None:
        self.visible = True

    def close(self) -> bool:
        self.visible = False
        return True


@pytest.fixture
def world(monkeypatch: Any, real_app: Any) -> Any:
    calls: list[Any] = []
    state = NS(
        glyphs=[],
        pending=(),
        records=(),
        occurrences=[],
        context=(7, "Light", "editor"),
    )
    package = NS(id=7, fgId=77, master="Light", masters=["Light", "Bold"])
    package.axes = [
        NS(shortName="wt", name="Weight", designMin=0.0, designMax=1000.0, default=0.0)
    ]
    package.findName = lambda name: next(
        (g for g in state.glyphs if g.name == name), None
    )
    state.package = package
    native = NS(
        flGlyph=NS(updatedFgGlyphs=lambda: state.pending),
        flItems=lambda: NS(notifyChangesApplied=lambda *args: calls.append(args)),
        flLocation=dict,
        MainWindow=lambda: None,
    )
    qt = ModuleType("PythonQt")
    qt.QtCore = NS(QDateTime=NS(currentDateTimeUtc=lambda: "STAMP"))
    qt.QtGui = NS(
        QMessageBox=NS(warning=lambda *args: calls.append(args)),
        QDialog=QtWidget,
        QVBoxLayout=QtWidget,
        QHBoxLayout=QtWidget,
        QGridLayout=QtWidget,
        QLabel=QtWidget,
        QTableWidget=QtWidget,
        QTableWidgetItem=QtWidget,
        QPushButton=QtWidget,
        QDoubleSpinBox=QtWidget,
        QAbstractItemView=NS(NoEditTriggers=0),
        QHeaderView=NS(Stretch=1),
    )
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    fly.ap, fly.fl, fly.qt = ap, native, qt
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", ap)
    import fontlabapp.scripting as real_scripting

    def current_package(expected_id: int | None = None) -> Any | None:
        return (
            state.package
            if state.package is not None
            and (expected_id is None or state.package.id == expected_id)
            else None
        )

    def names_selected_names() -> list[str]:
        return [g.name for g in state.glyphs]

    def show_script_dialog(dialog_type: Any, key: str) -> Any:
        return dialog_type, key

    replacements = {
        "current_package": current_package,
        "names_selected_names": names_selected_names,
        "show_script_dialog": show_script_dialog,
    }
    signatures = [
        (
            name,
            inspect.signature(getattr(real_scripting, name)),
            inspect.signature(fake),
        )
        for name, fake in replacements.items()
    ]
    modules = real_app(
        qt=qt,
        fontlab=native,
        scripting=replacements,
        modules=(
            "guides",
            "history",
            "edit_guards",
            "outline_writer",
            "anchor_writer",
            "selection_panel",
            "layer_selection",
        ),
    )

    def dependency_values(package: Any) -> tuple:
        return state.records

    def capture(deadline: float) -> Any:
        return NS(context=state.context, occurrences=state.occurrences)

    for mod, name, fake in [
        (modules["guides"], "dependency_values", dependency_values),
        (modules["layer_selection"], "capture", capture),
    ]:
        signatures.append(
            (name, inspect.signature(getattr(mod, name)), inspect.signature(fake))
        )
        monkeypatch.setattr(mod, name, fake)

    def load(index: int) -> Any:
        spec = importlib.util.spec_from_file_location(f"g7_{index}", PATHS[index])
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
        return module

    state.load, state.calls, state.app, state.signatures = (
        load,
        calls,
        modules,
        signatures,
    )
    return state


def polygon(count: int = 5) -> Shape:
    return Shape([Contour([Node(i, i * 2) for i in range(count)])])


def test_removal_when_one_polygon_node_selected_then_all_compatible_layers_change_once(
    world: Any,
) -> None:
    module = world.load(0)
    layers = [Layer("Light", [polygon()]), Layer("Bold", [polygon()])]
    glyph = Glyph("a", layers)
    layers[0].shapes[0].contours[0]._nodes[2].selected = True
    rows = module.survey(glyph, layers[0], world.app["history"].auto_facts(()))
    result = module.write_rows(rows, world.app["history"].auto_facts(()))
    assert result["layers"] == 2
    assert [[n.x for n in layer.shapes[0].contours[0].nodes()] for layer in layers] == [
        [0, 1, 3, 4]
    ] * 2
    assert world.calls == [(module.TITLE, [*layers, glyph])]


def test_intermediate_when_coordinate_is_fractional_then_adds_interpolation_with_one_notification(
    world: Any,
) -> None:
    module = world.load(1)
    glyph = Glyph("a", [Layer("Light"), Layer("Bold")])
    world.glyphs = [glyph]
    facts = world.app["history"].auto_facts(())
    rows = module.survey(world.package, ["a"], {"wt": 512.5}, facts)
    result = module.write_rows(world.package, rows, facts)
    layer = glyph.findLayer(":wt=512.5")
    assert result["layers"] == 1 and layer.advanceWidth == 551.25
    assert world.calls == [(module.TITLE, [layer, glyph])]
    assert glyph.history == [0]


def test_real_app_names_when_imported_then_all_script_dependencies_exist() -> None:
    check_real_app_names(app_names_used(PATHS))


def facts(world: Any, records: tuple = ()) -> Any:
    return world.app["history"].auto_facts(records)


@pytest.mark.parametrize("index", [0, 1])
def test_panels_when_loaded_then_no_native_members_are_shadowed(
    world: Any, index: int
) -> None:
    module = world.load(index)
    panel = module.MagicPanel if index == 0 else module.IntermediatePanel
    assert not NATIVE_MEMBERS.intersection(vars(panel)), (
        "Panel shadows a native Qt member"
    )
    assert module.main() == (panel, module.KEY)
    with pytest.raises(AssertionError, match="Native member collision"):
        PanelBase().layout = None


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("error_type", [ValueError, RuntimeError, TimeoutError])
def test_main_when_opening_fails_then_warning_is_shown(
    world: Any, monkeypatch: Any, index: int, error_type: type
) -> None:
    module = world.load(index)

    def fail(dialog_type: Any, key: str) -> None:
        raise error_type("fixture refusal")

    expected = next(
        real for name, real, _ in world.signatures if name == "show_script_dialog"
    )
    assert signature_shape(inspect.signature(fail)) == signature_shape(expected)
    monkeypatch.setattr(world.app["scripting"], "show_script_dialog", fail)
    assert module.main() is None
    assert world.calls[-1][-1] == "fixture refusal"


def test_native_constructors_when_optional_arguments_are_positional_then_rejected() -> (
    None
):
    with pytest.raises(TypeError):
        Node(0, 0, "on")
    with pytest.raises(TypeError):
        Contour([], True)


def test_removal_when_component_selected_then_retains_history_and_preserves_pins(
    world: Any,
) -> None:
    module = world.load(0)
    layers = [Layer(n, [polygon(), Shape([], "acute")]) for n in ("Light", "Bold")]
    glyph = Glyph("aacute", layers)
    for layer in layers:
        layer.anchors = [
            Pin("top"),
            Pin("bottom"),
        ]
    layers[0].shapes[1].selected = True
    removed = [
        s
        for layer in layers
        for s in world.app["history"].component_history(layer.shapes[1])
    ]
    rows = module.survey(glyph, layers[0], facts(world))
    assert module.write_rows(rows, facts(world)) == {"pending_note": "", "edits": 2, "layers": 2, "pending_updates": ()}
    assert world.calls == [(module.TITLE, [*removed, *layers, glyph], True)]
    assert [[p.name for p in layer.anchors] for layer in layers] == [
        ["top", "bottom"],
        ["top", "bottom"],
    ]


@pytest.mark.parametrize(
    "variant", ["locked", "auto", "incompatible", "mask", "service", "backup"]
)
def test_removal_when_layer_scope_differs_then_compatibility_controls_writes(
    world: Any, variant: str
) -> None:
    module = world.load(0)
    source, other = Layer("Light", [polygon()]), Layer("Bold", [polygon()])
    source.shapes[0].contours[0]._nodes[2].selected = True
    if variant == "locked":
        other.isLocked = True
    elif variant == "auto":
        other.autoLayer = True
    elif variant == "incompatible":
        other.shapes[0].contours[0]._nodes.append(Node())
    elif variant == "mask":
        other.isMaskLayer = True
    elif variant == "service":
        other.isService = True
    else:
        other.isMasterLayer = False
    glyph = Glyph("a", [source, other])
    rows = module.survey(glyph, source, facts(world))
    assert any(row.layer is other and "kept" in row.note for row in rows)
    if variant in {"locked", "auto"}:
        assert module.write_rows(rows, facts(world))["layers"] == 0
        assert not world.calls
        return
    assert module.write_rows(rows, facts(world))["layers"] == 1
    assert len(other.shapes[0].contours[0].nodes()) == (
        6 if variant == "incompatible" else 5
    )
    assert world.calls[0][1] == [source, glyph]


@pytest.mark.parametrize("owner", [True, False])
def test_removal_when_glyph_owns_auto_or_is_its_base_then_no_history(
    world: Any, owner: bool
) -> None:
    module = world.load(0)
    source = Layer("Light", [polygon()])
    source.shapes[0].contours[0]._nodes[1].selected = True
    glyph = Glyph("a", [source])
    auto = facts(world, (("a", True, ()),) if owner else (("aacute", True, ("a",)),))
    rows = module.survey(glyph, source, auto)
    assert all(row.note for row in rows)
    assert module.write_rows(rows, auto)["layers"] == 0
    assert world.calls == [] and glyph.history == []


@pytest.mark.parametrize(
    "variant", ["curve", "few", "endpoint", "shared", "shape_locked", "transform"]
)
def test_removal_when_selected_nodes_are_unsafe_then_kept(
    world: Any, variant: str
) -> None:
    module = world.load(0)
    shape = polygon(3 if variant == "few" else 5)
    contour = shape.contours[0]
    contour._nodes[1].selected = True
    if variant == "curve":
        contour._nodes[2].type = "curve"
    elif variant == "endpoint":
        contour.closed = False
        contour._nodes[0].selected = True
    elif variant == "shared":
        shape.shapeData.referenceCount = 2
    elif variant == "shape_locked":
        shape.contentLocked = True
    elif variant == "transform":
        shape.transform = NS(m11=lambda: 2)
    layer = Layer("Light", [shape])
    rows = module.survey(Glyph("a", [layer]), layer, facts(world))
    assert all(row.note for row in rows), variant
    assert module.write_rows(rows, facts(world))["edits"] == 0
    assert not world.calls


def test_removal_when_all_curve_nodes_selected_then_whole_contour_is_removed(
    world: Any,
) -> None:
    module = world.load(0)
    shape = polygon()
    for node in shape.contours[0]._nodes:
        node.selected = True
    shape.contours[0]._nodes[2].type = "curve"
    layer = Layer("Light", [shape])
    glyph = Glyph("a", [layer])
    module.write_rows(module.survey(glyph, layer, facts(world)), facts(world))
    assert shape.contours == []
    assert layer.shapes == [], "The empty outline shape must also be removed"
    assert len(world.calls) == 1


def test_removal_when_no_items_selected_then_clear_refusal(world: Any) -> None:
    module = world.load(0)
    layer = Layer("Light", [polygon()])
    with pytest.raises(ValueError, match="Select nodes"):
        module.survey(Glyph("a", [layer]), layer, facts(world))


def test_removal_when_native_node_delete_is_ignored_then_readback_fails(
    world: Any,
) -> None:
    module = world.load(0)
    layer = Layer("Light", [polygon()])
    contour = layer.shapes[0].contours[0]
    contour._nodes[1].selected = True
    contour.removeAt = lambda index: None
    with pytest.raises(RuntimeError, match="Undo"):
        module.write_rows(
            module.survey(Glyph("a", [layer]), layer, facts(world)), facts(world)
        )


@pytest.mark.parametrize("index", [0, 1])
def test_writers_when_updates_are_pending_then_write_and_report_ids(
    world: Any, index: int
) -> None:
    module = world.load(index)
    source = Layer("Light", [polygon()])
    source.shapes[0].contours[0]._nodes[1].selected = True
    glyph = Glyph("a", [source, Layer("Bold", [polygon()])])
    world.glyphs = [glyph]
    world.pending = (100,)
    if index == 0:
        result = module.write_rows(module.survey(glyph, source, facts(world)), facts(world))
    else:
        rows = module.survey(world.package, ["a"], {"wt": 500}, facts(world))
        result = module.write_rows(world.package, rows, facts(world))
    assert glyph.history and world.calls and world.pending == (100,)
    assert result["pending_updates"] == (100,)


@pytest.mark.parametrize("number", [float("nan"), float("inf"), -1, 1001])
def test_intermediate_when_coordinate_invalid_then_refuses_before_history(
    world: Any, number: float
) -> None:
    module = world.load(1)
    with pytest.raises(ValueError, match="finite coordinate"):
        module.location_values(world.package, {"wt": number})
    assert not world.calls


@pytest.mark.parametrize("values", [{}, {"wght": 500}, {"wt": 500, "wd": 90}])
def test_intermediate_when_axes_missing_or_unknown_then_refuses(
    world: Any, values: dict
) -> None:
    with pytest.raises(ValueError, match="each declared axis"):
        world.load(1).location_values(world.package, values)


def test_intermediate_when_no_axes_then_clear_refusal(world: Any) -> None:
    world.package.axes = []
    with pytest.raises(ValueError, match="Declare axes"):
        world.load(1).location_values(world.package, {})


def test_intermediate_when_multi_axis_then_name_uses_short_names_and_full_precision(
    world: Any,
) -> None:
    module = world.load(1)
    world.package.axes.append(
        NS(shortName="Wd", name="Width", designMin=50, designMax=200)
    )
    values, name = module.location_values(
        world.package, {"wt": 512.1234567891234, "Wd": 87.5}
    )
    assert float(name.split(",")[0].split("=")[1]) == values["wt"], (
        "Name must round-trip its location"
    )
    assert name.endswith(",wd=87.5")


@pytest.mark.parametrize(
    "variant",
    [
        "same_name",
        "same_location",
        "locked",
        "incompatible",
        "missing_master",
        "auto_owner",
        "auto_base",
        "missing_glyph",
    ],
)
def test_intermediate_when_one_glyph_refused_then_the_other_is_added(
    world: Any, variant: str
) -> None:
    module = world.load(1)
    a, b = [Glyph(name, [Layer("Light"), Layer("Bold")]) for name in ("a", "b")]
    world.glyphs = [a, b]
    auto = facts(world)
    if variant == "same_name":
        a.layers.append(Layer(":wt=500"))
    elif variant == "same_location":
        a.layers.append(Layer("Custom"))
        a.layers[-1].position = {"wt": 500}
    elif variant == "locked":
        a.layers[0].isLocked = True
    elif variant == "incompatible":
        a.layers[1].shapes = [polygon()]
    elif variant == "missing_master":
        a.layers.pop()
    elif variant == "auto_owner":
        auto = facts(world, (("a", True, ()),))
    elif variant == "auto_base":
        auto = facts(world, (("aacute", True, ("a",)),))
    else:
        world.glyphs = [b]
    rows = module.survey(world.package, ["a", "b", "b"], {"wt": 500}, auto)
    assert len(rows) == 2 and "kept" in rows[0].note
    assert module.write_rows(world.package, rows, auto)["layers"] == 1
    assert b.findLayer(":wt=500") is not None
    assert a.history == [] and len(world.calls) == 1


def test_intermediate_when_interpolation_refuses_one_glyph_then_rest_still_added(
    world: Any,
) -> None:
    module = world.load(1)
    a, b = [Glyph(name, [Layer("Light"), Layer("Bold")]) for name in ("a", "b")]
    a.fail_interpolation = True
    world.glyphs = [a, b]
    rows = module.survey(world.package, ["a", "b"], {"wt": 500}, facts(world))
    result = module.write_rows(world.package, rows, facts(world))
    assert result["layers"] == 1 and "a" in result["kept"][0]
    assert b.findLayer(":wt=500") is not None


def test_intermediate_when_second_add_raises_then_partial_layer_is_in_final_notification(
    world: Any,
) -> None:
    module = world.load(1)
    a, b = [Glyph(name, [Layer("Light"), Layer("Bold")]) for name in ("a", "b")]
    world.glyphs = [a, b]

    def fail(layer: Any) -> None:
        raise RuntimeError("injected add failure")

    b.addLayer = fail
    rows = module.survey(world.package, ["a", "b"], {"wt": 500}, facts(world))
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        module.write_rows(world.package, rows, facts(world))
    assert a.findLayer(":wt=500") in world.calls[0][1]


def test_magic_panel_when_captured_editor_selection_then_plans_and_keeps_carrier(
    world: Any,
) -> None:
    module = world.load(0)
    source = Layer("Light", [polygon()])
    glyph = Glyph("a", [source])
    source.shapes[0].contours[0]._nodes[1].selected = True
    world.occurrences = [NS(package=world.package, glyph=glyph, layer=source)]
    panel = module.MagicPanel()
    panel.font_package = lambda: world.package
    rows = panel.plan()
    assert (
        panel.names == ["a"] and panel.editor_carrier.occurrences == world.occurrences
    )
    assert "remove" in panel.cells(rows[0])[1]
    assert panel.write(world.package, rows)["layers"] == 1
    assert "Removed" in panel.result_text({"edits": 1, "layers": 1})


@pytest.mark.parametrize("context, count", [("font", 1), ("editor", 0), ("editor", 2)])
def test_magic_panel_when_no_unique_editor_slot_then_refuses(
    world: Any, context: str, count: int
) -> None:
    module = world.load(0)
    panel = module.MagicPanel()
    panel.font_package = lambda: world.package
    world.context = (7, "Light", context)
    world.occurrences = [None] * count
    with pytest.raises(ValueError, match="exactly one"):
        panel.plan()


def test_intermediate_panel_when_values_are_set_then_survey_and_write(
    world: Any,
) -> None:
    module = world.load(1)
    world.glyphs = [Glyph("a", [Layer("Light"), Layer("Bold")])]
    panel = module.IntermediatePanel()
    panel.names = ["a"]
    panel.axis_controls = {"wt": NS(value=612.25)}
    rows = panel.plan_rows(world.package, world.package.masters)
    assert panel.cells(rows[0]) == ["a", ":wt=612.25", "add interpolated layer"]
    result = panel.write(world.package, rows)
    assert panel.result_text(result) == "Added 1 intermediate layer(s)"


def test_intermediate_when_location_binding_has_only_subscripts_then_can_match(
    world: Any,
) -> None:
    module = world.load(1)
    assert module.position_matches(NativeLocation({"wt": 500}), {"wt": 500})
    assert not module.position_matches(NativeLocation({}), {"wt": 500})
    assert not module.position_matches({"wt": (500, 600)}, {"wt": 500})


@pytest.mark.parametrize("role", ["isMaskLayer", "isService", "isImg"])
def test_removal_when_source_is_not_foreground_then_refuses(
    world: Any, role: str
) -> None:
    module = world.load(0)
    source = Layer("Light", [polygon()])
    source.shapes[0].contours[0]._nodes[1].selected = True
    setattr(source, role, True)
    with pytest.raises(ValueError, match="foreground"):
        module.survey(Glyph("a", [source]), source, facts(world))
    assert not world.calls


def test_coordinate_controls_when_built_then_one_spin_per_axis_and_guarded_watch(
    world: Any, monkeypatch: Any
) -> None:
    module = world.load(1)

    class Spin(PanelBase):
        def __init__(self) -> None:
            self.valueChanged = Signal()

        def setDecimals(self, value: int) -> None:
            self.decimals = value

        def setRange(self, low: float, high: float) -> None:
            self.bounds = low, high

        def setValue(self, value: float) -> None:
            self.value = value

    monkeypatch.setattr(module.qt.QtGui, "QDoubleSpinBox", Spin, raising=False)
    panel = module.IntermediatePanel()
    watched, added = [], []
    panel.watch = lambda signal: watched.append(signal)
    panel.add_row = lambda *args: added.append(args)
    panel.build_controls()
    assert list(panel.axis_controls) == ["wt"]
    spin = panel.axis_controls["wt"]
    assert spin.value == 500 and spin.bounds == (0, 1000) and spin.decimals == 6
    assert watched == [spin.valueChanged] and added == [("Weight (wt)", spin)]


def test_magic_panel_when_reselecting_then_refreshes_and_font_switch_refuses(
    world: Any,
) -> None:
    module = world.load(0)
    panel = module.MagicPanel()
    calls = []
    panel.refresh = lambda: calls.append("refresh")
    panel.reselect()
    assert calls == ["refresh"]
    panel.font_package = lambda: world.package
    world.occurrences = [NS(package=NS(id=99))]
    with pytest.raises(ValueError, match="font changed"):
        panel.plan()


def test_removal_when_layer_update_fails_then_partial_write_has_undo_guidance(
    world: Any,
) -> None:
    module = world.load(0)
    layer = Layer("Light", [polygon()])
    layer.fail_update = True
    layer.shapes[0].contours[0]._nodes[1].selected = True
    glyph = Glyph("a", [layer])
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        module.write_rows(module.survey(glyph, layer, facts(world)), facts(world))
    assert world.calls[0][1] == [layer, glyph]


def signature_shape(signature: inspect.Signature) -> inspect.Signature:
    """Compare call contracts, including names, kinds and defaults, not annotations."""
    return signature.replace(
        parameters=[
            p.replace(annotation=inspect.Signature.empty)
            for p in signature.parameters.values()
        ],
        return_annotation=inspect.Signature.empty,
    )


def test_app_fakes_when_compared_with_installed_functions_then_signatures_match(
    world: Any,
) -> None:
    assert len(world.signatures) == 5, (
        "Every replaced App function needs a contract check"
    )
    for name, real, fake in world.signatures:
        assert signature_shape(fake) == signature_shape(real), name
    assert world.app["scripting"].current_package(expected_id=99) is None


def test_intermediate_when_two_glyphs_ready_and_add_returns_none_then_both_added(
    world: Any,
) -> None:
    module = world.load(1)
    world.glyphs = [Glyph(name, [Layer("Light"), Layer("Bold")]) for name in ("a", "b")]
    rows = module.survey(world.package, ["a", "b"], {"wt": 500}, facts(world))
    assert module.write_rows(world.package, rows, facts(world))["layers"] == 2
    layers = [glyph.findLayer(":wt=500") for glyph in world.glyphs]
    assert all(layer is not None for layer in layers)
    assert world.calls == [(module.TITLE, [*layers, *world.glyphs])]


@pytest.mark.parametrize(
    "variant", ["shared", "transformed", "shape_locked", "component_locked"]
)
def test_removal_when_one_master_keeps_an_item_then_every_master_keeps_it(
    world: Any, variant: str
) -> None:
    module = world.load(0)
    layers = [
        Layer(name, [polygon(), Shape([], "acute")]) for name in ("Light", "Bold")
    ]
    if variant == "component_locked":
        layers[0].shapes[1].selected = True
        layers[1].shapes[1].contentLocked = True
    else:
        layers[0].shapes[0].contours[0]._nodes[1].selected = True
        if variant == "shared":
            layers[1].shapes[0].shapeData.referenceCount = 2
        elif variant == "shape_locked":
            layers[1].shapes[0].contentLocked = True
        else:
            layers[1].shapes[0].transform = NS(m11=lambda: 2)
    glyph = Glyph("aacute", layers)
    rows = module.survey(glyph, layers[0], facts(world))
    assert len(rows) == 1 and "Bold" in rows[0].note and "all masters" in rows[0].note
    assert module.write_rows(rows, facts(world))["edits"] == 0
    assert all(len(layer.shapes[0].contours[0].nodes()) == 5 for layer in layers)
    assert not world.calls


@pytest.mark.parametrize("index", [0, 1])
def test_panels_when_using_real_selection_panel_then_open_plan_and_apply(
    world: Any, index: int
) -> None:
    module = world.load(index)
    layers = [Layer(name, [polygon()]) for name in ("Light", "Bold")]
    world.glyphs = [Glyph("a", layers)]
    layers[0].shapes[0].contours[0]._nodes[1].selected = True
    layers[0].anchors = [Pin("top")]
    world.occurrences = [
        NS(package=world.package, glyph=world.glyphs[0], layer=layers[0])
    ]
    panel_type = module.MagicPanel if index == 0 else module.IntermediatePanel
    panel = panel_type()
    assert isinstance(panel, world.app["selection_panel"].panel_type())
    assert type(panel).__mro__[1].__module__ == "fontlabapp._selection_panel"
    panel.show()
    assert panel.visible and panel.rows and panel.apply_button.enabled
    assert panel.table.row_count == len(panel.rows)
    panel.apply_button.clicked.emit(False)
    assert not hasattr(panel, "slot_error"), "Guarded callbacks must complete"
    assert panel.last_result["layers"] == (2 if index == 0 else 1)
    assert len(world.calls) == 1
    assert panel.status.text.startswith("Removed" if index == 0 else "Added")


def test_intermediate_when_axis_short_name_has_case_then_interpolation_uses_declared_key(
    world: Any,
) -> None:
    module = world.load(1)
    world.package.axes[0].shortName = "Wt"
    glyph = Glyph("a", [Layer("Light"), Layer("Bold")])
    world.glyphs = [glyph]
    calls = []

    def interpolate(location: Any, rounding: bool) -> Any:
        calls.append(dict(location))
        result = Layer("")
        result.position = {"wt": location["Wt"]}
        return result

    glyph.interpolateInstance = interpolate
    rows = module.survey(world.package, ["a"], {"Wt": 500}, facts(world))
    assert module.write_rows(world.package, rows, facts(world))["layers"] == 1
    assert calls == [{"Wt": 500}] and rows[0].name == ":wt=500"
    glyph.layers[0].position = {"Wt": 600}
    assert (
        "location already exists"
        in module.survey(world.package, ["a"], {"Wt": 600}, facts(world))[0].note
    )


def test_removal_when_one_item_is_held_then_other_items_still_match_on_all_masters(
    world: Any,
) -> None:
    module = world.load(0)
    layers = [
        Layer(name, [polygon(), Shape([], "acute")]) for name in ("Light", "Bold")
    ]
    layers[0].shapes[0].contours[0]._nodes[1].selected = True
    layers[0].shapes[1].selected = True
    layers[1].shapes[0].contentLocked = True
    glyph = Glyph("aacute", layers)
    rows = module.survey(glyph, layers[0], facts(world))
    assert len([row for row in rows if row.note]) == 1
    assert module.write_rows(rows, facts(world)) == {"pending_note": "", "edits": 2, "layers": 2, "pending_updates": ()}
    assert all(
        len(layer.shapes) == 1 and len(layer.shapes[0].contours[0].nodes()) == 5
        for layer in layers
    )


def test_removal_when_empty_shape_removal_is_ignored_then_readback_reports_it(
    world: Any,
) -> None:
    module = world.load(0)
    layer = Layer("Light", [polygon()])
    for node in layer.shapes[0].contours[0]._nodes:
        node.selected = True
    layer.removeShape = lambda shape: None
    with pytest.raises(RuntimeError, match="Undo"):
        module.write_rows(
            module.survey(Glyph("a", [layer]), layer, facts(world)), facts(world)
        )


def test_intermediate_when_add_is_ignored_then_readback_refuses(world: Any) -> None:
    module = world.load(1)
    glyph = Glyph("a", [Layer("Light"), Layer("Bold")])
    world.glyphs = [glyph]
    glyph.addLayer = lambda layer: None
    rows = module.survey(world.package, ["a"], {"wt": 500}, facts(world))
    with pytest.raises(RuntimeError, match="did not add the layer"):
        module.write_rows(world.package, rows, facts(world))
    assert glyph.findLayer(":wt=500") is None


@pytest.mark.parametrize("native_fault", [False, True])
def test_removal_when_shape_has_an_unselected_contour_then_it_must_survive(
    world: Any, native_fault: bool
) -> None:
    module = world.load(0)
    shape = polygon()
    survivor = polygon().contours[0]
    shape.contours.append(survivor)
    for node in shape.contours[0]._nodes:
        node.selected = True
    layer = Layer("Light", [shape])
    if native_fault:
        shape.removeContour = lambda contour: shape.contours.clear()
        with pytest.raises(RuntimeError, match="Undo"):
            module.write_rows(
                module.survey(Glyph("a", [layer]), layer, facts(world)), facts(world)
            )
    else:
        module.write_rows(
            module.survey(Glyph("a", [layer]), layer, facts(world)), facts(world)
        )
        assert layer.shapes == [shape] and shape.contours == [survivor]


@pytest.mark.parametrize("interpolate", [False, True])
def test_intermediate_when_no_layer_added_then_result_without_history_and_queue_kept(
    world: Any, interpolate: bool,
) -> None:
    module = world.load(1)
    world.pending = (100,)
    glyph = Glyph("a", [Layer("Light"), Layer("Bold")])
    glyph.fail_interpolation = True
    world.glyphs = [glyph]
    rows = module.survey(world.package, ["a"], {"wt": 500}, facts(world)) if interpolate else []
    result = module.write_rows(world.package, rows, facts(world))
    assert result["layers"] == 0 and not world.calls and not glyph.history
    assert result["pending_updates"] == ((100,) if interpolate else ())
    assert world.pending == (100,), "An empty or refused plan must not clear queued ids"
