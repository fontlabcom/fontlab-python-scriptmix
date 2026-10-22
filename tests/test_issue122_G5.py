# this_file: tests/test_issue122_G5.py
# SPDX-License-Identifier: Apache-2.0
"""Named component decomposition on owned fakes and real installed App helpers."""

import ast
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names

SCRIPT = Path(__file__).parents[1] / "Scripts/Components/Decompose Named Components.py"
LOCATIONS = SCRIPT.with_name("Set Component Locations.py")


def replace_app(monkeypatch: Any, module: Any, name: str, fake: Any) -> None:
    """Check actual parameter shapes, then retain the real type annotations."""
    real = getattr(module, name)

    def untyped(function: Any) -> Any:
        signature = inspect.signature(function)
        return signature.replace(
            return_annotation=inspect.Signature.empty,
            parameters=[
                p.replace(annotation=inspect.Parameter.empty)
                for p in signature.parameters.values()
            ],
        )

    assert untyped(fake) == untyped(real), f"Fake signature differs: {name}"
    fake.__annotations__ = dict(real.__annotations__)
    assert inspect.signature(fake) == inspect.signature(real), name
    monkeypatch.setattr(module, name, fake)


class Item:
    """Owned history carrier; record the exact initialization calls."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.history: list[int] = []
        self.isNull = False

    def checkInitHistoryState(self, value: int) -> None:
        self.history.append(value)


class Shape:
    """Affine component fake whose eject operation composes placement."""

    def __init__(
        self, name: str = "", parts: tuple | None = None, x: float = 0
    ) -> None:
        self.id = id(self)
        self.name = "element"
        self.isComponent = bool(name)
        self.isComposite = self.isComponent
        self.transform = NS(isAffine=lambda: True)
        self.x = x
        self.contentLocked = True
        self.contours: list[Any] = [] if name else [NS(nodes=list)]
        self.selected = False
        self.shapeData = NS(
            componentGlyph=name,
            componentLayer="",
            note="note",
            builder=NS(update=lambda: True),
            referenceCount=1,
        )
        self.includesList = (Shape(),) if name and parts is None else (parts or ())

    def ejectTo(self) -> list[Any]:
        return [
            Shape(p.shapeData.componentGlyph, p.includesList, self.x + p.x)
            for p in self.includesList
        ]


class Layer(Item):
    def __init__(self, name: str, shapes: list[Any], **flags: Any) -> None:
        super().__init__(name)
        self.shapes = shapes
        for shape in shapes:
            if shape.isComponent and not shape.shapeData.componentLayer:
                shape.shapeData.componentLayer = name
        self.autoLayer = flags.get("auto", False)
        self.isLocked = flags.get("locked", False)
        self.isMaskLayer = False
        self.isService = False

    def removeShape(self, shape: Shape) -> None:
        self.shapes.remove(shape)

    def insertShape(self, index: int, shape: Shape) -> Shape:
        self.shapes.insert(index, shape)
        return shape

    def changed(self) -> None:
        pass

    def update(self) -> bool:
        return True


class Glyph(Item):
    def __init__(self, name: str, layers: list[Layer]) -> None:
        super().__init__(name)
        self.layers = layers
        self.lastModified = None

    def findLayer(self, name: str) -> Any:
        return next((layer for layer in self.layers if layer.name == name), None)

    def updateActiveLayer(self, assign: bool) -> Any:
        return self.layers[0] if self.layers else None


class Widget:
    """Controls reject instance fields that shadow QWidget members."""

    forbidden = frozenset(
        {"render", "size", "layout", "update", "font", "move", "statusBar"}
    )

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in self.forbidden, name
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args else ""
        self.textChanged = NS()

    def setPlaceholderText(self, value: str) -> None:
        self.placeholder = value

    def setText(self, value: str) -> None:
        self.text = value

    def setEnabled(self, value: bool) -> None:
        self.enabled = value


class Control(Widget):
    """Small property-based Qt controls for the location panel's own form."""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.currentIndex = 0
        self.value = 0.0
        self.currentIndexChanged, self.valueChanged = NS(), NS()
        self.itemChanged = NS()
        self.entries: list[str] = []
        self.cells: dict[tuple[int, int], Any] = {}

    def addItems(self, items: list[str]) -> None:
        self.entries.extend(items)

    def setCurrentIndex(self, value: int) -> None:
        self.currentIndex = value

    def setValue(self, value: float) -> None:
        self.value = value

    def setRange(self, minimum: float, maximum: float) -> None:
        self.bounds = (minimum, maximum)

    def setDecimals(self, count: int) -> None:
        self.decimals = count

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        self.columns = labels

    def setVerticalHeaderLabels(self, labels: list[str]) -> None:
        self.labels = labels

    def setMinimumHeight(self, value: int) -> None:
        self.minimum = value

    def setMaximumHeight(self, value: int) -> None:
        self.maximum = value

    def setCellWidget(self, row: int, column: int, widget: Any) -> None:
        self.cells[row, column] = widget

    def setRowCount(self, count: int) -> None:
        self.cells = {}

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.cells[row, column] = item

    def item(self, row: int, column: int) -> Any:
        return self.cells[row, column]

    def blockSignals(self, flag: bool) -> bool:
        return False


class TableItem:
    def __init__(self, text: str) -> None:
        self.value = text

    def text(self) -> str:
        return self.value

    def setText(self, text: str) -> None:
        self.value = text


@pytest.fixture
def env(monkeypatch: Any, real_app: Any) -> Any:
    notifications: list[Any] = []
    native = NS(
        flGlyph=NS(updatedFgGlyphs=lambda: ()),
        flItems=lambda: NS(notifyChangesApplied=lambda *a: notifications.append(a)),
        flNode=NS(NodeKind={"SmoothMask": 0x30}),
    )
    qt = NS(
        QtCore=NS(QDateTime=NS(currentDateTimeUtc=lambda: "stamp")),
        QtGui=NS(
            QLineEdit=Widget,
            QLabel=Widget,
            QComboBox=Control,
            QDoubleSpinBox=Control,
            QTableWidget=Control,
            QTableWidgetItem=TableItem,
        ),
    )
    modules = real_app(
        qt=qt,
        fontlab=native,
        modules=("history", "component_writer", "component_panel", "edit_guards"),
    )

    class Base(Widget):
        pass

    def panel_type() -> type:
        return Base

    replace_app(monkeypatch, modules["component_panel"], "panel_type", panel_type)
    fly = ModuleType("fly")
    fly.__path__ = []
    fly.ap = sys.modules["fontlabapp"]
    fly.qt = qt
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", fly.ap)
    spec = importlib.util.spec_from_file_location("g5_owned", SCRIPT)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    location_script = None
    if LOCATIONS.exists():
        spec = importlib.util.spec_from_file_location("g5_locations", LOCATIONS)
        location_script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(location_script)
    return NS(
        script=script,
        locations=location_script,
        modules=modules,
        notifications=notifications,
    )


def test_real_app_imports() -> None:
    check_real_app_names(app_names_used([SCRIPT, LOCATIONS]))


def test_named_subtree_and_siblings_across_masters(env: Any) -> None:
    named = Shape("part", (Shape(x=2),))
    other = Shape("other")
    glyph = Glyph("host", [Layer(m, [named, other]) for m in ("Regular", "Bold")])
    package = NS(
        findName=lambda n: Glyph(
            "part", [Layer(m, [Shape()]) for m in ("Regular", "Bold")]
        )
    )
    plan = env.script.make_plan(
        package,
        [glyph],
        ["Regular", "Bold"],
        "part",
        env.modules["history"].auto_facts(()),
    )
    assert plan.edits == 2
    assert [[edit[0] for edit in work[2]] for work in plan.work] == [
        [named.id],
        [named.id],
    ]
    assert all("other" != change.name for _, change in plan.rows)


@pytest.mark.parametrize("kind", ["auto", "dependant", "locked", "missing", "loop"])
def test_refused_item_is_kept_and_other_glyph_still_writes(
    env: Any, kind: str, monkeypatch: Any
) -> None:
    bad = Glyph("bad", [Layer("Regular", [Shape("part")], locked=kind == "locked")])
    good = Glyph("good", [Layer("Regular", [Shape("part")])])
    if kind == "missing":
        bad.layers = [Layer("Bold", [Shape("part")])]
    records = [("bad", kind == "auto", ()), ("autoUser", kind == "dependant", ("bad",))]
    facts = env.modules["history"].auto_facts(records)
    real_check = env.modules["component_writer"].copy_problem
    if kind == "loop":

        def copy_problem(
            package: Any, owner: tuple[str, str], shape: Any, master: str
        ) -> str:
            return "components loop" if owner[0] == "bad" else ""

        replace_app(
            monkeypatch, env.modules["component_writer"], "copy_problem", copy_problem
        )
    package = NS(findName=lambda n: Glyph(n, [Layer("Regular", [Shape()])]))
    try:
        plan = env.script.make_plan(package, [bad, good], ["Regular"], "part", facts)
    finally:
        env.modules["component_writer"].copy_problem = real_check
    assert [g.name for g, _, _ in plan.work] == ["good"]
    assert any("bad" in label and "kept" in row.new for label, row in plan.rows)
    assert not plan.problems


def test_recursive_detached_copies_exact_offsets_and_one_notification(env: Any) -> None:
    nested = Shape("inner", (Shape(x=3),), x=7)
    root = Shape("part", (nested, Shape(x=5)), x=100)
    sibling = Shape("inner", x=900)
    layer = Layer("Regular", [sibling, root])
    glyph = Glyph("host", [layer])
    result = env.modules["component_writer"].apply_work(
        [(glyph, layer, [(root.id, env.script.flatten_parts(root))])],
        "Named",
        env.modules["history"].auto_facts(()),
        env.script.NamedEditor(unlock=True),
    )
    assert result == {"pending_note": "", "edits": 1, "layers": 1, "pending_updates": ()}
    assert layer.shapes[0] is sibling
    assert [s.x for s in layer.shapes[1:]] == [110, 105]
    assert all(not s.isComponent and not s.contentLocked for s in layer.shapes[1:])
    assert len(env.notifications) == 1
    title, notified, deep = env.notifications[0]
    assert title == "Named" and deep is True
    assert notified == [root, root.shapeData, root.shapeData.builder, layer, glyph]
    assert glyph.history == layer.history == [0]
    assert glyph.lastModified == "stamp"


def test_depth_guard(env: Any) -> None:
    root = Shape("part")
    root.includesList = (root,)
    with pytest.raises(ValueError, match="nest"):
        env.script.flatten_parts(root)


@pytest.mark.parametrize(
    "value", ["", " ", "a\x00b", "a\u00a0b", "a\u2028b", "a\u2029b"]
)
def test_invalid_name(env: Any, value: str) -> None:
    panel = env.script.NamedDecomposition()
    panel.source_edit = Widget(value)
    with pytest.raises(ValueError):
        panel.planner()


def test_panel_controls_and_all_masters_default(env: Any) -> None:
    panel = env.script.NamedDecomposition()
    added: list[Any] = []
    panel.form = NS(addWidget=lambda *a: added.append(a))
    panel.watch = lambda *a: None
    box = NS(setCurrentIndex=lambda n: added.append(n), currentIndexChanged=NS())
    panel.scope_box = lambda: box
    panel.build_controls()
    assert 1 in added
    assert panel.editor().unlock is True


def test_empty_selection_makes_no_work(env: Any) -> None:
    plan = env.script.make_plan(
        None, [], [], "part", env.modules["history"].auto_facts(())
    )
    assert not plan.work and not plan.rows


def test_panel_native_member_collisions() -> None:
    for path in (SCRIPT, LOCATIONS):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in {
                "NamedDecomposition",
                "LocationPanel",
            }:
                names = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                names.update(
                    n.attr
                    for n in ast.walk(node)
                    if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
                )
                assert not names & Widget.forbidden


def panel_for(env: Any) -> Any:
    """Create only owned controls; native shared panel layout is not exercised."""
    panel = env.script.NamedDecomposition()
    panel.source_edit = Widget("part")
    panel.subtitle, panel.status, panel.apply_button = Widget(), Widget(), Widget()
    panel.intro = lambda: "Selected hosts"
    panel.chosen_masters = lambda: ["Regular"]
    panel.facts = env.modules["history"].auto_facts(())
    panel.fill = lambda plan: setattr(panel, "preview", plan)
    panel.summary = lambda plan: str(plan.edits)
    panel.glyphs = []
    panel.package = None
    return panel


def test_no_font_disables_apply(env: Any) -> None:
    panel = panel_for(env)
    panel.refresh()
    assert panel.apply_button.enabled is False
    assert not panel.preview.work


@pytest.mark.parametrize(
    "error", [ValueError("stale"), RuntimeError("host"), TimeoutError("scan")]
)
def test_apply_refusal_reports_error_without_history(
    env: Any, error: Exception
) -> None:
    panel = panel_for(env)

    def fail() -> Any:
        raise error

    panel.live_glyphs = fail
    panel.apply()
    assert panel.status.text == str(error)
    assert env.notifications == []


def test_apply_mixed_selection_only_notifies_eligible_layer(
    env: Any, monkeypatch: Any
) -> None:
    root = Shape("part", (Shape(x=5),), x=20)
    good = Glyph("good", [Layer("Regular", [root])])
    bad = Glyph("bad", [Layer("Regular", [Shape("part")], auto=True)])
    base = Glyph("part", [Layer("Regular", [Shape(x=5)])])
    package = NS(findName=lambda name: base)
    panel = panel_for(env)
    panel.package, panel.glyphs = package, [bad, good]
    panel.live_glyphs = lambda: (package, panel.glyphs)
    facts = env.modules["history"].auto_facts((("bad", True, ()),))

    def scan_auto_facts(package: Any) -> Any:
        return facts

    replace_app(monkeypatch, env.modules["history"], "scan_auto_facts", scan_auto_facts)
    panel.apply()
    assert panel.last_result == {"pending_note": "", "edits": 1, "layers": 1, "pending_updates": ()}
    assert good.layers[0].shapes[0].x == 25
    assert len(env.notifications) == 1
    assert env.notifications[0][1][-2:] == [good.layers[0], good]
    assert bad.history == bad.layers[0].history == []
    assert any(
        "bad" in label and "kept" in row.new for label, row in panel.preview.rows
    )


def test_no_match_creates_no_history(env: Any) -> None:
    glyph = Glyph("host", [Layer("Regular", [Shape("other")])])
    facts = env.modules["history"].auto_facts(())
    plan = env.script.make_plan(None, [glyph], ["Regular"], "part", facts)
    result = env.modules["component_writer"].apply_work(
        plan.work, "Named", facts, env.script.NamedEditor(True)
    )
    assert result == {"edits": 0, "layers": 0, "pending_updates": (), "pending_note": ""}
    assert not env.notifications


def test_readback_error_keeps_app_text_without_undo_hint(
    env: Any, monkeypatch: Any
) -> None:
    panel = panel_for(env)
    root = Shape("part", (Shape(),))
    glyph = Glyph("host", [Layer("Regular", [root])])
    base = Glyph("part", [Layer("Regular", [Shape()])])
    package = NS(findName=lambda name: base)
    panel.live_glyphs = lambda: (package, [glyph])

    def scan_auto_facts(package: Any) -> Any:
        return panel.facts

    replace_app(monkeypatch, env.modules["history"], "scan_auto_facts", scan_auto_facts)

    def fail(
        work: Any, title: str, facts: Any, edit: Any, *, allow_bases: bool = False
    ) -> Any:
        raise RuntimeError("FontLab did not store a change.")

    replace_app(monkeypatch, env.modules["component_writer"], "apply_work", fail)
    panel.apply()
    assert panel.status.text == "FontLab did not store a change."
    assert env.modules["history"].UNDO_HINT not in panel.status.text


def test_write_failure_after_removal_has_one_notification_and_undo_hint(
    env: Any,
) -> None:
    root = Shape("part", (Shape(),))
    layer = Layer("Regular", [root])
    glyph = Glyph("host", [layer])

    def fail(*args: Any) -> Any:
        raise RuntimeError("native insertion failed")

    layer.insertShape = fail
    with pytest.raises(
        env.modules["history"].PartialWriteError,
        match="Native changes may remain; use Edit > Undo",
    ):
        env.modules["component_writer"].apply_work(
            [(glyph, layer, [(root.id, env.script.flatten_parts(root))])],
            "Named",
            env.modules["history"].auto_facts(()),
            env.script.NamedEditor(True),
        )
    assert len(env.notifications) == 1


@pytest.mark.parametrize(
    "error", [ValueError("font"), RuntimeError("host"), TimeoutError("scan")]
)
def test_main_reports_host_failures(
    env: Any, monkeypatch: Any, capsys: Any, error: Exception
) -> None:
    def fail(dialog_type: Any, key: str) -> Any:
        raise error

    replace_app(monkeypatch, env.modules["scripting"], "show_script_dialog", fail)
    assert env.script.main() is None
    assert str(error) in capsys.readouterr().out


def test_main_uses_shared_dialog_lifecycle(env: Any, monkeypatch: Any) -> None:
    calls: list[Any] = []

    def show_script_dialog(dialog_type: Any, key: str) -> Any:
        calls.append((dialog_type, key))
        return "panel"

    replace_app(
        monkeypatch, env.modules["scripting"], "show_script_dialog", show_script_dialog
    )
    assert env.script.main() == "panel"
    assert calls == [(env.script.NamedDecomposition, "components_decompose_named")]


def test_empty_detached_nested_part_is_kept_before_history(
    env: Any, monkeypatch: Any
) -> None:
    nested = Shape("inner", (Shape(),))
    root = Shape("part", (nested,))
    host = Glyph("host", [Layer("Regular", [root])])
    bases = {
        "part": Glyph("part", [Layer("Regular", [nested])]),
        "inner": Glyph("inner", [Layer("Regular", [Shape()])]),
    }

    def empty_nested(self: Any) -> list[Any]:
        return [Shape("inner", ())] if self is root else []

    monkeypatch.setattr(Shape, "ejectTo", empty_nested)
    plan = env.script.make_plan(
        NS(findName=bases.get),
        [host],
        ["Regular"],
        "part",
        env.modules["history"].auto_facts(()),
        copy=True,
    )
    assert not plan.work
    assert "kept" in plan.rows[0][1].new and "count" in plan.rows[0][1].new
    assert host.history == [] and env.notifications == []


def test_unrelated_refused_glyph_produces_no_named_row(env: Any) -> None:
    glyph = Glyph("unrelated", [Layer("Regular", [Shape("other")], auto=True)])
    plan = env.script.make_plan(
        None,
        [glyph],
        ["Regular", "Missing"],
        "part",
        env.modules["history"].auto_facts((("unrelated", True, ()),)),
    )
    assert not plan.rows


def test_unlock_setting_is_used(env: Any) -> None:
    root = Shape("part", (Shape(),))
    layer = Layer("Regular", [root])
    parts = env.script.flatten_parts(root)
    env.script.NamedEditor(False).prepare(layer, [(root.id, parts)])
    assert parts[0].contentLocked is True
    env.script.NamedEditor(True).prepare(layer, [(root.id, parts)])
    assert parts[0].contentLocked is False


def test_prewrite_prepare_failure_has_no_undo_hint_and_refreshes(
    env: Any, monkeypatch: Any
) -> None:
    panel = panel_for(env)
    root = Shape("part", (Shape(),))
    glyph = Glyph("host", [Layer("Regular", [root])])
    base = Glyph("part", [Layer("Regular", [Shape()])])
    package = NS(findName=lambda name: base)
    panel.live_glyphs = lambda: (package, [glyph])
    refreshed: list[bool] = []
    panel.refresh = lambda: refreshed.append(True)

    def scan_auto_facts(package: Any) -> Any:
        return panel.facts

    class PrepareFailure(env.script.NamedEditor):
        def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
            raise RuntimeError("FontLab could not refresh component part.")

    replace_app(monkeypatch, env.modules["history"], "scan_auto_facts", scan_auto_facts)
    panel.editor = lambda: PrepareFailure(True)
    panel.apply()
    assert refreshed == [True]
    assert "could not refresh" in panel.status.text and "Undo" not in panel.status.text
    assert not env.notifications and glyph.history == glyph.layers[0].history == []


def axes_package() -> Any:
    axes = [
        NS(
            shortName="wt",
            name="Weight",
            designMin=100.0,
            designMax=900.0,
            designDef=400.0,
        ),
        NS(
            shortName="wd",
            name="Width",
            designMin=50.0,
            designMax=200.0,
            designDef=100.0,
        ),
    ]
    return NS(
        axes=axes,
        masters=["Regular", "Bold"],
        findName=lambda name: Glyph(name, []),
        location=lambda master: {
            "wt": 800.0 if master == "Bold" else 400.0,
            "wd": 100.0,
        },
    )


def test_location_exact_text_and_declared_axis_order(env: Any) -> None:
    assert (
        env.locations.encode_location(axes_package(), {"wd": 100.0, "wt": 650.125})
        == "#wt=650.125,wd=100"
    )


@pytest.mark.parametrize(
    "values",
    [
        {"wt": 901, "wd": 100},
        {"wt": float("nan"), "wd": 100},
        {"wrong": 400},
        {"wt": 400},
        {"wt": 400, "wd": float("inf")},
    ],
)
def test_bad_locations_are_refused(env: Any, values: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        env.locations.encode_location(axes_package(), values)


def test_shared_location_data_is_kept_other_components_write(env: Any) -> None:
    shared, good = Shape("part"), Shape("part")
    shared.shapeData.referenceCount = 2
    glyph = Glyph("host", [Layer("Regular", [shared, good])])
    plan = env.locations.location_plan(
        axes_package(),
        [glyph],
        ["Regular"],
        {"Regular": {"wt": 600, "wd": 100}},
        env.modules["history"].auto_facts(()),
        selected_only=False,
    )
    assert plan.edits == 1
    assert "kept" in plan.rows[0][1].new and "shared" in plan.rows[0][1].new


def test_set_and_reset_locations_use_one_notification_and_readback(env: Any) -> None:
    shapes = [Shape("part"), Shape("part")]
    glyph = Glyph(
        "host",
        [Layer(m, [s]) for m, s in zip(["Regular", "Bold"], shapes, strict=True)],
    )
    facts = env.modules["history"].auto_facts(())
    package = axes_package()
    values = {"Regular": {"wt": 400, "wd": 100}, "Bold": {"wt": 800, "wd": 90}}
    plan = env.locations.location_plan(
        package, [glyph], package.masters, values, facts, selected_only=False
    )
    result = env.modules["component_writer"].apply_work(
        plan.work, "Locations", facts, env.locations.LocationEditor()
    )
    assert result == {"pending_note": "", "edits": 2, "layers": 2, "pending_updates": ()}
    assert [s.shapeData.componentLayer for s in shapes] == [
        "#wt=400,wd=100",
        "#wt=800,wd=90",
    ]
    assert len(env.notifications) == 1 and len(env.notifications[0]) == 2
    assert env.notifications[0][1] == [*glyph.layers, glyph]
    plan = env.locations.location_plan(
        package, [glyph], package.masters, {}, facts, reset=True, selected_only=False
    )
    env.modules["component_writer"].apply_work(
        plan.work, "Reset", facts, env.locations.LocationEditor()
    )
    assert [s.shapeData.componentLayer for s in shapes] == ["Regular", "Bold"]
    assert len(env.notifications) == 2
    plan = env.locations.location_plan(
        package, [glyph], package.masters, {}, facts, reset=True, selected_only=False
    )
    assert not plan.work
    env.modules["component_writer"].apply_work(
        plan.work, "Reset", facts, env.locations.LocationEditor()
    )
    assert len(env.notifications) == 2


def test_selected_components_match_by_position_and_base_across_masters(
    env: Any,
) -> None:
    selected, other = Shape("part"), Shape("other")
    selected.selected = True
    glyph = Glyph(
        "host",
        [
            Layer("Regular", [selected, other]),
            Layer("Bold", [Shape("part"), Shape("other")]),
        ],
    )
    package = axes_package()
    values = {m: {"wt": 500, "wd": 100} for m in package.masters}
    plan = env.locations.location_plan(
        package, [glyph], package.masters, values, env.modules["history"].auto_facts(())
    )
    assert plan.edits == 2
    assert all(change.name == "part" for _, change in plan.rows)
    glyph.layers[1].shapes[0] = Shape("different")
    plan = env.locations.location_plan(
        package, [glyph], package.masters, values, env.modules["history"].auto_facts(())
    )
    assert plan.edits == 1 and "kept" in plan.rows[-1][1].new


@pytest.mark.parametrize("kind", ["auto", "owner", "dependant", "locked"])
def test_location_refused_rows_allow_other_glyphs(env: Any, kind: str) -> None:
    bad = Glyph(
        "bad",
        [
            Layer(
                "Regular", [Shape("part")], auto=kind == "auto", locked=kind == "locked"
            )
        ],
    )
    good = Glyph("good", [Layer("Regular", [Shape("part")])])
    facts = env.modules["history"].auto_facts(
        (("bad", kind == "owner", ()), ("user", kind == "dependant", ("bad",)))
    )
    plan = env.locations.location_plan(
        axes_package(),
        [bad, good],
        ["Regular"],
        {"Regular": {"wt": 500, "wd": 100}},
        facts,
        selected_only=False,
    )
    assert plan.edits == 1 and plan.work[0][0] is good
    assert "kept" in plan.rows[0][1].new


def test_location_name_filter_and_noop(env: Any) -> None:
    part = Shape("part")
    glyph = Glyph("host", [Layer("Regular", [part, Shape("other")])])
    plan = env.locations.location_plan(
        axes_package(),
        [glyph],
        ["Regular"],
        {},
        env.modules["history"].auto_facts(()),
        reset=True,
        name="part",
        selected_only=False,
    )
    assert not plan.work and len(plan.rows) == 1


def test_faked_app_signature_checker_rejects_wrong_shape(
    env: Any, monkeypatch: Any
) -> None:
    with pytest.raises(AssertionError, match="signature"):
        replace_app(
            monkeypatch, env.modules["history"], "scan_auto_facts", lambda: None
        )


def test_partial_write_error_reaches_status_and_refreshes_preview(
    env: Any, monkeypatch: Any
) -> None:
    root = Shape("part", (Shape(),))
    glyph = Glyph("host", [Layer("Regular", [root])])
    base = Glyph("part", [Layer("Regular", [Shape()])])
    package = NS(findName=lambda name: base)
    panel = panel_for(env)
    panel.package, panel.glyphs = package, [glyph]
    panel.live_glyphs = lambda: (package, [glyph])

    def scan_auto_facts(package: Any) -> Any:
        return panel.facts

    replace_app(monkeypatch, env.modules["history"], "scan_auto_facts", scan_auto_facts)

    def insertShape(index: int, shape: Any) -> Any:
        raise RuntimeError("native insert failure")

    glyph.layers[0].insertShape = insertShape
    panel.apply()
    assert env.modules["history"].UNDO_HINT in panel.status.text
    assert len(env.notifications) == 1
    assert not panel.preview.work and not panel.apply_button.enabled


def location_panel(env: Any) -> Any:
    panel = env.locations.LocationPanel()
    panel.package = axes_package()
    panel.masters = panel.package.masters
    panel.form = NS(addWidget=lambda *args: None)
    panel.watch = lambda *args: None
    panel.scope_box = Control
    panel.build_controls()
    panel.facts = env.modules["history"].auto_facts(())
    panel.subtitle, panel.status, panel.apply_button = Widget(), Widget(), Widget()
    panel.glyphs = []
    panel.intro = lambda: "Selected glyphs"
    panel.fill = lambda plan: setattr(panel, "preview", plan)
    panel.summary = lambda plan: str(plan.edits)
    panel.chosen_masters = lambda: panel.masters
    return panel


def test_location_panel_builds_bounded_axis_table_and_reset_controls(env: Any) -> None:
    panel = location_panel(env)
    glyph = Glyph("host", [Layer(m, [Shape("part")]) for m in panel.masters])
    panel.current_plan(panel.package, [glyph], panel.facts)
    assert panel.master_scope.currentIndex == 1
    assert len(panel.axis_controls) == 4
    assert panel.axis_table.maximum == 200
    assert [
        panel.axis_controls[(key, "wt")].text() for key in panel.coordinate_rows
    ] == ["400.0", "800.0"]
    panel.mode_box.currentIndex = 1
    panel.current_plan(panel.package, [glyph], panel.facts)
    assert not panel.axis_table.enabled


def test_location_panel_revalidates_axes_and_ranges(env: Any) -> None:
    panel = location_panel(env)
    panel.package.axes[0].shortName = "other"
    with pytest.raises(ValueError, match="Axes or masters changed"):
        panel.current_plan(panel.package, [], panel.facts)


def test_location_panel_applies_previewed_batch_and_refreshes(
    env: Any, monkeypatch: Any
) -> None:
    panel = location_panel(env)
    root = Shape("part")
    glyph = Glyph("host", [Layer("Regular", [root])])
    panel.glyphs = [glyph]
    panel.chosen_masters = lambda: ["Regular"]
    panel.target_box.currentIndex = 1
    panel.live_glyphs = lambda: (panel.package, [glyph])

    def scan_auto_facts(package: Any) -> Any:
        return panel.facts

    replace_app(monkeypatch, env.modules["history"], "scan_auto_facts", scan_auto_facts)
    panel.refresh()
    assert panel.preview.edits == 0 and not panel.apply_button.enabled
    panel.apply()
    assert env.notifications == []
    key = panel.coordinate_rows[0]
    panel.axis_controls[key, "wt"].setText("650")
    panel.refresh()
    assert panel.preview.edits == 1 and panel.apply_button.enabled
    panel.apply()
    assert root.shapeData.componentLayer == "#wt=650,wd=100"
    assert panel.last_result == {"pending_note": "", "edits": 1, "layers": 1, "pending_updates": ()}
    assert len(env.notifications) == 1
    assert not panel.preview.work and not panel.apply_button.enabled


def test_location_readback_detects_lost_value(env: Any) -> None:
    shape = Shape("part")
    layer = Layer("Regular", [shape])
    assert env.locations.LocationEditor().check([(layer, [(shape, "#wt=700")])]) == [
        "Regular/part"
    ]


def test_location_missing_master_is_kept_and_bad_values_are_local(env: Any) -> None:
    glyph = Glyph("host", [Layer("Regular", [Shape("part")])])
    facts = env.modules["history"].auto_facts(())
    values = {"Regular": {"wt": 500, "wd": 100}, "Bold": {"wt": 999, "wd": 100}}
    plan = env.locations.location_plan(
        axes_package(), [glyph], ["Regular", "Bold"], values, facts, selected_only=False
    )
    assert plan.edits == 1 and "missing master layer" in plan.rows[-1][1].new
    glyph.layers.append(Layer("Bold", [Shape("part")]))
    plan = env.locations.location_plan(
        axes_package(), [glyph], ["Regular", "Bold"], values, facts, selected_only=False
    )
    assert plan.edits == 1 and "design range" in plan.rows[-1][1].new


def test_location_selection_empty_is_noop(env: Any) -> None:
    glyph = Glyph("host", [Layer("Regular", [Shape("part")])])
    plan = env.locations.location_plan(
        axes_package(),
        [glyph],
        ["Regular"],
        {"Regular": {"wt": 500, "wd": 100}},
        env.modules["history"].auto_facts(()),
    )
    assert not plan.work and not plan.rows


def test_location_main_uses_shared_lifecycle(env: Any, monkeypatch: Any) -> None:
    calls: list[Any] = []

    def show_script_dialog(dialog_type: Any, key: str) -> Any:
        calls.append((dialog_type, key))
        return "panel"

    replace_app(
        monkeypatch, env.modules["scripting"], "show_script_dialog", show_script_dialog
    )
    assert env.locations.main() == "panel"
    assert calls == [(env.locations.LocationPanel, "components_set_locations")]


@pytest.mark.parametrize(
    "error", [ValueError("font"), RuntimeError("host"), TimeoutError("scan")]
)
def test_location_apply_failure_refreshes_and_preserves_text(
    env: Any, error: Exception
) -> None:
    panel = location_panel(env)

    def fail() -> Any:
        raise error

    panel.live_glyphs = fail
    panel.apply()
    assert panel.status.text == str(error) and not panel.preview.work


def test_set_preserves_node_suffix_but_reset_uses_host_name(env: Any) -> None:
    shape = Shape("part")
    glyph = Glyph("host", [Layer("Bold", [shape])])
    shape.shapeData.componentLayer = "Bold@top"
    facts = env.modules["history"].auto_facts(())
    plan = env.locations.location_plan(
        axes_package(),
        [glyph],
        ["Bold"],
        {"Bold": {"wt": 650, "wd": 100}},
        facts,
        selected_only=False,
    )
    assert plan.work[0][2] == [(shape.id, "#wt=650,wd=100@top")]
    reset = env.locations.location_plan(
        axes_package(), [glyph], ["Bold"], {}, facts, reset=True, selected_only=False
    )
    assert reset.work[0][2] == [(shape.id, "Bold")]


def test_decompose_preview_never_copies_or_refreshes_builders(
    env: Any, monkeypatch: Any
) -> None:
    root = Shape("part")
    glyph = Glyph("host", [Layer("Regular", [root])])
    base = Glyph("part", [Layer("Regular", [Shape()])])
    calls: list[bool] = []

    def ejectTo(self: Any) -> Any:
        calls.append(True)
        raise AssertionError("Preview must not eject")

    monkeypatch.setattr(Shape, "ejectTo", ejectTo)
    root.shapeData.builder.update = lambda: (_ for _ in ()).throw(
        AssertionError("Preview must not update")
    )
    plan = env.script.make_plan(
        NS(findName=lambda name: base),
        [glyph],
        ["Regular"],
        "part",
        env.modules["history"].auto_facts(()),
    )
    assert plan.edits == 1 and not calls


def test_location_rows_use_existing_component_values_and_only_edited_occurrence(
    env: Any, monkeypatch: Any
) -> None:
    panel = location_panel(env)
    first, second = Shape("part"), Shape("part")
    first.shapeData.componentLayer = "#wt=550.125,wd=110@top"
    second.shapeData.componentLayer = "#wt=700,wd=90"
    glyph = Glyph("host", [Layer("Regular", [first, second])])
    panel.glyphs = [glyph]
    panel.chosen_masters = lambda: ["Regular"]
    panel.live_glyphs = lambda: (panel.package, [glyph])

    def scan_auto_facts(package: Any) -> Any:
        return panel.facts

    replace_app(monkeypatch, env.modules["history"], "scan_auto_facts", scan_auto_facts)
    panel.refresh()
    assert not panel.preview.work
    key = panel.coordinate_rows[0]
    assert panel.axis_controls[key, "wt"].text() == "550.125"
    panel.axis_controls[key, "wd"].setText("120")
    panel.refresh()
    assert panel.preview.edits == 1
    panel.apply()
    assert first.shapeData.componentLayer == "#wt=550.125,wd=120@top"
    assert second.shapeData.componentLayer == "#wt=700,wd=90"
    assert len(env.notifications) == 1


def test_selected_scope_guidance_and_stale_masters_are_actionable(env: Any) -> None:
    panel = location_panel(env)
    assert panel.target_box.currentIndex == 1
    panel.target_box.currentIndex = 0
    panel.refresh()
    assert "Glyph window" in panel.status.text
    panel.package.masters = ["Different"]
    with pytest.raises(ValueError, match="close this panel and run it again"):
        panel.current_plan(panel.package, [], panel.facts)
