# this_file: tests/test_issue122_G1.py
# SPDX-License-Identifier: Apache-2.0
"""Seven Masters scripts, host-free with owned fakes.

The tests load each script from disk and check exact names, matrices and
notification shapes. Font, selection and Qt access are small fakes; the shared
App helpers (history, masters, edit guards) are the real installed App modules
loaded over those fakes. No FontLab or Qt is imported, so none of this proves
native behaviour.
"""

import ast
import importlib.util
import inspect
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
FOLDER = ROOT / "Scripts" / "Masters"
SCRIPTS = [
    "Display Next Layer",
    "Display Previous Layer",
    "Duplicate Current Layer",
    "Use Layer As Master",
    "Transform Background",
    "Selection To All Backgrounds",
    "Select Different Colour",
]
STAMP = "14:05:09, 21/10/26"


def load(title: str) -> ModuleType:
    """Execute one script file as a module without touching sys.modules."""
    spec = importlib.util.spec_from_file_location(
        "g1_" + title.replace(" ", "_"), FOLDER / f"{title}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- native fakes
class Layer:
    """Fake flLayer. Names go through a property so tests can break renames."""

    def __init__(self, name: str, glyph: Any = None, **flags: Any) -> None:
        self.id = flags.pop("id", id(self))
        self._name = name
        self.glyph = glyph
        self.isMaskLayer = flags.pop("mask", name.lower().startswith("mask"))
        self.isService = flags.pop("service", self.isMaskLayer)
        self.autoLayer = flags.pop("auto", False)
        self.isLocked = flags.pop("locked", False)
        self.isNull, self.isValid = False, True
        self.masks: dict[bool, Any] = {}
        self.image = None
        self.fail_name: str | None = None
        self.ignore_rename = False
        self.shapes: list[Any] = []
        self.calls: list[Any] = []
        self.history: list[int] = []
        self.clones = 0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if self.fail_name == value:
            raise RuntimeError("rename refused")
        if not self.ignore_rename:
            self._name = value

    def getMaskLayer(self, create: bool) -> Any:
        if create and True not in self.masks and self.glyph is not None:
            mask = Layer("mask." + self.name, self.glyph)
            self.glyph.layers.append(mask)
            self.masks[True] = mask
        return self.masks.get(True)

    def getImgLayer(self, create: bool) -> Any:
        return self.image

    def clone(self) -> "Layer":
        self.clones += 1
        copy = Layer(self.name, None)
        copy.shapes = [shape.clone() for shape in self.shapes]
        return copy

    def setActive(self) -> None:
        self.glyph.active = self

    def checkInitHistoryState(self, index: int) -> None:
        self.history.append(index)

    def changed(self) -> None:
        self.calls.append("changed")

    def update(self) -> Any:
        self.calls.append("update")
        return getattr(self, "update_result", True)

    def applyTransform(self, *args: Any) -> None:
        self.calls.append(("applyTransform", args))

    def removeAllShapes(self) -> None:
        self.calls.append("removeAllShapes")
        self.shapes = []

    def removeShape(self, shape: Any) -> None:
        self.calls.append(("removeShape", shape))
        self.shapes.remove(shape)

    def addShape(self, shape: Any) -> None:
        self.calls.append(("addShape", shape))
        self.shapes.append(shape)


class Glyph:
    """Fake flGlyph with an ordered layer list."""

    def __init__(self, name: str, layer_names: list[str], gid: int = 0, **flags: Any) -> None:
        self.name, self.id = name, gid or abs(hash(name)) % 10**6
        self.isNull = False
        self.layers = [Layer(n, self, **flags.get(n, {})) for n in layer_names]
        self.active = self.layers[0] if self.layers else None
        self.lastModified: Any = None
        self.history: list[int] = []
        self.bound = 0

    def layer(self, name: str) -> Layer:
        return next(x for x in self.layers if x.name == name)

    def findLayer(self, name: str) -> Any:
        return next((x for x in self.layers if x.name.lower() == name.lower()), None)

    def updateActiveLayer(self, assign: bool) -> Any:
        return self.active

    def addLayer(self, layer: Layer) -> None:
        layer.glyph = self
        self.layers.append(layer)

    def bindDependencies(self) -> None:
        self.bound += 1

    def checkInitHistoryState(self, index: int) -> None:
        self.history.append(index)


class FakeWidget:
    """Accept any Qt call; remember texts and signal slots."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args, self.texts, self.slots = args, [], []

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        if name in ("clicked", "returnPressed"):
            signal = NS(connect=lambda cb: self.slots.append(cb))
            self.__dict__[name] = signal
            return signal
        if name == "text":
            return self.__dict__.get("value", self.args[0] if self.args else "")
        if name in ("font", "palette"):
            return FakeWidget()
        if name == "pointSizeF":
            return lambda: 10.0
        def call(*a: Any, **k: Any) -> Any:
            if name == "setText" and a:
                self.texts.append(a[0])
            if name == "setEnabled":
                self.enabled = a[0]
            return FakeWidget()

        return call


def fake_gui() -> Any:
    """A QtGui whose every class is a FakeWidget."""

    class Gui:
        QPalette = NS(WindowText=0)
        QColor = type("Color", (FakeWidget,), {"HexArgb": 0})
        QDialog = type("Dialog", (FakeWidget,), {})
        QTransform = staticmethod(lambda *a: ("QTransform", a))

        def __getattr__(self, name: str) -> Any:
            return FakeWidget

    return Gui()


class Notifier:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[Any]]] = []

    def notifyChangesApplied(self, title: str, objects: list[Any], deep: bool = False) -> None:
        self.deep = deep
        if getattr(self, "fail", False):
            raise RuntimeError("notify failed")
        self.calls.append((title, list(objects)))


class World:
    """One fake `fly` universe: selection, package, native module, Qt."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, real_app: Any) -> None:
        self.notifier = Notifier()
        self.pending: tuple = ()
        self.occurrences: list[Any] = []
        self.context: tuple = (1, "Regular", "editor", 7, ())
        self.carriers: tuple = ()
        self.package = NS(id=1, masters=("Regular", "Bold"), master="Regular")
        self.glyphs: list[Glyph] = []
        self.selected_calls: list[Any] = []
        self.font_selection: list[str] = []
        self.marks: list[tuple[str, int]] = []
        native = NS(
            flGlyph=NS(updatedFgGlyphs=lambda: self.pending),
            flItems=lambda: self.notifier,
            CurrentFont=lambda: NS(glyphs=[NS(name=n, mark=m) for n, m in self.marks or
                                           [(g.name, 0) for g in self.glyphs]]),
        )
        scripting = ModuleType("fly.ap.scripting")
        scripting.current_package = lambda *a: self.package
        scripting.names_font_window_selection = lambda: list(self.font_selection)
        scripting.select_glyphs = lambda names, **kw: self.selected_calls.append((list(names), kw))
        scripting.connect_guarded = lambda dialog, signal, cb: signal.connect(cb)
        scripting.close_script_dialog = lambda *a: self.selected_calls.append(("close", a[2]))
        scripting.show_script_dialog = lambda kind, key: (key, kind)
        selection = ModuleType("fly.ap.layer_selection")
        self.capture_error: Exception | None = None

        def capture(deadline: float) -> Any:
            if self.capture_error is not None:
                raise self.capture_error
            return NS(context=self.context, occurrences=self.occurrences, carriers=self.carriers)

        selection.capture = capture
        qtsafe = ModuleType("fly.ap.qtsafe")
        qtsafe.qt_list = lambda call, *a: list(call(*a))
        self.records: tuple = ()  # (glyph name, is auto layer, base names)
        ap = ModuleType("fly.ap")
        ap.__path__ = []
        ap.fontlab, ap.scripting = native, scripting
        ap.layer_selection = selection
        qt = ModuleType("fly.qt")
        qt.QtCore = NS(QDateTime=NS(currentDateTimeUtc=lambda: "UTC-STAMP"))
        qt.QtGui = fake_gui()
        fly = ModuleType("fly")
        fly.__path__ = []
        fly.ap, fly.qt = ap, qt
        for name, module in {
            "fly": fly, "fly.ap": ap, "fly.qt": qt, "fly.ap.scripting": scripting,
            "fly.ap.layer_selection": selection, "fly.ap.qtsafe": qtsafe,
        }.items():
            monkeypatch.setitem(sys.modules, name, module)
        # The real App helpers, over the same fakes; the auto-layer facts read `records`.
        self.app = real_app(
            qt=qt,
            fontlab=native,
            scripting={name: getattr(scripting, name) for name in SCRIPTING_FAKES},
            modules=APP_MODULES,
        )
        monkeypatch.setattr(self.app["guides"], "dependency_values", lambda package: tuple(self.records))
        ap.scripting = self.app["scripting"]

    def occupy(self, glyph: Glyph, layer_name: str | None = None, block: int = 0, index: int = 0) -> Any:
        layer = glyph.layer(layer_name) if layer_name else glyph.layers[0]
        item = NS(
            glyph=glyph, layer=layer, glyph_id=glyph.id, layer_id=layer.id,
            glyph_name=glyph.name, layer_name=layer.name, block_id=block, index=index,
        )
        self.occurrences.append(item)
        return item


SCRIPTING_FAKES = (
    "current_package", "names_font_window_selection", "select_glyphs",
    "connect_guarded", "close_script_dialog", "show_script_dialog",
)
APP_MODULES = ("guides", "history", "masters", "edit_guards", "contour_copy")


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch, real_app: Any) -> World:
    return World(monkeypatch, real_app)


# ---------------------------------------------------------------- generic checks
@pytest.mark.parametrize("title", SCRIPTS)
def test_script_when_parsed_then_py311_typed_headed_and_lazy(title: str) -> None:
    text = (FOLDER / f"{title}.py").read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    assert text.startswith(f"# this_file: Scripts/Masters/{title}.py\n# SPDX-License-Identifier: Apache-2.0\n")
    doc = ast.get_docstring(tree) or ""
    for word in ("What it does", "How it works", "Why this design", "How to use", "Benefit", "Credit"):
        assert word in doc, f"{title}: docstring lacks '{word}'"
    assert "Pedro Arilla" in doc and "Apache-2.0" in doc
    for node in tree.body:
        assert not (isinstance(node, ast.ImportFrom) and (node.module or "").startswith("fly")), title
        assert not (isinstance(node, ast.Import) and any(a.name.startswith("fly") for a in node.names)), title
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a for a in node.args.args + node.args.kwonlyargs if a.arg not in ("self", "cls")]
            assert node.returns is not None, f"{title}.{node.name}: no return type"
            assert all(a.annotation is not None for a in args), f"{title}.{node.name}: untyped argument"


def test_select_different_colour_when_credited_then_names_mekkablue() -> None:
    doc = ast.get_docstring(ast.parse((FOLDER / "Select Different Colour.py").read_text()))
    assert "Scheichelbauer" in doc and "mekkablue" in doc


# ---------------------------------------------------------------- next / previous
LAYERS = [
    ("Light", True), ("Regular", True), ("Regular@ a", True), ("mask.Regular", False),
    ("Regular#b", True), ("Bold", True),
]


@pytest.mark.parametrize(
    "name,expected",
    [("Regular", "Regular"), ("Regular@ x", "Regular"), ("Regular#y", "Regular"),
     ("|temp|Bold", "Bold"), ("Regular@a#b", "Regular"), ("Bolder", None), ("@x", None),
     ("mask.Regular", None), ("", None)],
)
def test_associated_master_when_name_given_then_follows_fontlab_rule(world: World, name: str, expected: Any) -> None:
    assert world.app["masters"].associated_master(name, ("Regular", "Bold")) == expected


@pytest.mark.parametrize(
    "title",
    ["Display Next Layer", "Display Previous Layer", "Duplicate Current Layer", "Use Layer As Master"],
)
def test_scripts_when_parsed_then_associated_master_comes_from_the_app(title: str) -> None:
    tree = ast.parse((FOLDER / f"{title}.py").read_text())
    defined = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "fly.ap.masters"
        for alias in node.names
    }
    assert "associated_master" not in defined and "associated_master" in imported, title


@pytest.mark.parametrize("title,step", [("Display Next Layer", 1), ("Display Previous Layer", -1)])
def test_layer_cycle_when_listing_then_only_same_master_body_layers(world: World, title: str, step: int) -> None:
    module = load(title)
    assert module.STEP == step
    cycle = module.layer_cycle(LAYERS, "Regular@ a", ("Regular", "Bold"))
    assert cycle == ["Regular", "Regular@ a", "Regular#b"]
    assert module.pick_layer(cycle, "Regular", 1) == "Regular@ a"
    assert module.pick_layer(cycle, "Regular#b", 1) == "Regular"  # wrap forward
    assert module.pick_layer(cycle, "Regular", -1) == "Regular#b"  # wrap backward


def test_layer_cycle_when_no_master_or_single_then_value_error(world: World) -> None:
    module = load("Display Next Layer")
    with pytest.raises(ValueError, match="belongs to no master"):
        module.layer_cycle(LAYERS, "mask.Regular", ("Regular", "Bold"))
    with pytest.raises(ValueError, match="not a body layer"):
        module.layer_cycle([("Regular", False)], "Regular", ("Regular",))
    with pytest.raises(ValueError, match="only layer"):
        module.pick_layer(["Bold"], "Bold", 1)


def editor(world: World, glyph: Glyph, layer_name: str, symbol_layer: str) -> Any:
    """Wire one editor slot whose symbol shows `symbol_layer` ('' = follows active)."""
    symbol = NS(layerName=symbol_layer)
    info = NS(symbol=symbol)
    block = NS(id=7, getGlyphAt=lambda index: info, changed=lambda: setattr(block, "refreshed", True))
    world.carriers = (NS(textBlocks=lambda: [block]),)
    world.occupy(glyph, layer_name, block=7)
    return symbol, block


@pytest.mark.parametrize(
    "title,expected", [("Display Next Layer", "Regular#b"), ("Display Previous Layer", "Regular")]
)
def test_run_when_explicit_slot_then_symbol_layer_name_changes(world: World, title: str, expected: str) -> None:
    glyph = Glyph("a", ["Light", "Regular", "Regular@ a", "mask.Regular", "Regular#b", "Bold"])
    symbol, block = editor(world, glyph, "Regular@ a", "Regular@ a")
    messages = load(title).run()
    assert symbol.layerName == expected and block.refreshed is True
    assert messages == [f"a: 'Regular@ a' -> '{expected}'"]


def test_run_when_slot_follows_active_then_active_layer_changes(world: World) -> None:
    glyph = Glyph("a", ["Regular", "Regular@ a", "Bold"])
    editor(world, glyph, "Regular", "")
    load("Display Next Layer").run()
    assert glyph.active.name == "Regular@ a"


def test_run_when_fontlab_ignores_write_then_runtime_error(world: World) -> None:
    glyph = Glyph("a", ["Regular", "Regular@ a"])
    symbol = NS()
    symbol.layerName = "Regular"
    info = NS(symbol=NS(layerName="Regular"))
    info.symbol = type("Stuck", (), {"layerName": property(lambda s: "Regular", lambda s, v: None)})()
    block = NS(id=7, getGlyphAt=lambda index: info, changed=lambda: None)
    world.carriers = (NS(textBlocks=lambda: [block]),)
    world.occupy(glyph, "Regular", block=7)
    with pytest.raises(RuntimeError, match="did not switch"):
        load("Display Next Layer").run()


def test_run_when_not_editor_or_nothing_selected_then_refused(world: World, capsys: Any) -> None:
    module = load("Display Next Layer")
    world.context = (1, "Regular", "font")
    with pytest.raises(ValueError, match="Glyph window"):
        module.run()
    world.context = (1, "Regular", "editor", 7, ())
    with pytest.raises(ValueError, match="Select a glyph"):
        module.run()
    module.main()
    assert "Display Next Layer: Select a glyph" in capsys.readouterr().out


def test_run_when_one_slot_invalid_then_no_slot_changes(world: World) -> None:
    good, bad = Glyph("a", ["Regular", "Regular@ a"]), Glyph("b", ["Regular"])
    symbol, _ = editor(world, good, "Regular", "Regular")
    world.occupy(bad, "Regular", block=7, index=1)
    with pytest.raises(ValueError, match="only layer"):
        load("Display Next Layer").run()
    assert symbol.layerName == "Regular"


# ---------------------------------------------------------------- duplicate
def fixed_clock(module: ModuleType) -> None:
    moment = datetime(2026, 10, 21, 14, 5, 9, tzinfo=UTC)
    module.datetime = NS(now=lambda: NS(astimezone=lambda: moment))


def test_backup_name_when_taken_then_counts_up_without_case() -> None:
    module = load("Duplicate Current Layer")
    assert module.backup_name("Regular", [], STAMP, ["Regular"]) == f"Regular backup {STAMP}"
    taken = [f"regular backup {STAMP}", f"Regular backup {STAMP} (2)"]
    assert module.backup_name("Regular", taken, STAMP, ["Regular"]) == f"Regular backup {STAMP} (3)"


def test_run_when_duplicating_then_clone_named_added_and_one_notification(world: World) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = Glyph("a", ["Regular", "Regular@ old"])
    world.occupy(glyph, "Regular@ old")
    messages = module.run()
    new = glyph.layers[-1]
    assert new.name == f"Regular backup {STAMP}"
    assert messages == [f"a: new layer 'Regular backup {STAMP}'"]
    assert glyph.layers[1].clones == 1 and glyph.bound == 1
    assert world.notifier.calls == [("Duplicate Current Layer", [new, glyph])]
    assert glyph.history == [0] and glyph.lastModified == "UTC-STAMP"


def test_run_when_same_layer_selected_twice_then_one_copy_and_two_glyphs_two_copies(world: World) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    a, b = Glyph("a", ["Regular"]), Glyph("b", ["Regular"])
    for glyph in (a, b, a):
        world.occupy(glyph, "Regular")
    module.run()
    assert [len(a.layers), len(b.layers)] == [2, 2]
    (_title, objects), = world.notifier.calls
    assert objects == [a.layers[1], b.layers[1], a, b]


def test_run_when_stamp_already_used_then_suffix(world: World) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = Glyph("a", ["Regular", f"Regular backup {STAMP}"])
    world.occupy(glyph, "Regular")
    module.run()
    assert glyph.layers[-1].name == f"Regular backup {STAMP} (2)"


@pytest.mark.parametrize("flag", ["mask", "service", "auto"])
def test_run_when_layer_not_plain_body_then_refused_without_change(world: World, flag: str) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = Glyph("a", ["Regular"], Regular={flag: True})
    world.occupy(glyph, "Regular")
    with pytest.raises(ValueError, match="mask, service or automatic"):
        module.run()
    assert len(glyph.layers) == 1 and world.notifier.calls == []


def test_run_when_add_fails_then_notification_still_sent_and_undo_hint(world: World) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = Glyph("a", ["Regular"])
    glyph.addLayer = lambda layer: (_ for _ in ()).throw(RuntimeError("full"))
    world.occupy(glyph, "Regular")
    with pytest.raises(world.app["history"].PartialWriteError, match="did not finish: full.*Edit > Undo"):
        module.run()
    assert len(world.notifier.calls) == 1


def test_run_when_pending_updates_or_no_selection_then_value_error(world: World, capsys) -> None:
    module = load("Duplicate Current Layer")
    with pytest.raises(ValueError, match="Select a glyph"):
        module.run()
    glyph = Glyph("a", ["Regular"])
    world.occupy(glyph, "Regular")
    world.pending = (3,)
    result = module.run()
    assert len(glyph.layers) == 2 and world.pending == (3,) and world.notifier.calls
    output = capsys.readouterr().out
    assert "(3,)" in output and "Queued glyph ids:" in output and "8537" in output and "modification dates" in output


# ---------------------------------------------------------------- use layer as master
def test_mask_name_for_when_single_master_then_master_layer_uses_plain_mask() -> None:
    module = load("Use Layer As Master")
    assert module.mask_name_for("Regular", ("Regular",)) == "mask"
    assert module.mask_name_for("Regular@ a", ("Regular",)) == "mask.Regular@ a"
    assert module.mask_name_for("Regular", ("Regular", "Bold")) == "mask.Regular"


def test_plan_swap_when_both_masks_then_order_and_names_exact() -> None:
    module = load("Use Layer As Master")
    taken = ["Regular", "Regular@ a", "mask.Regular", "mask.Regular@ a", "Bold"]
    assert module.plan_swap("Regular", "Regular@ a", taken, STAMP, ("Regular", "Bold"), (True, True)) == [
        ("master mask", "mask.Regular", f"mask.Regular@ {STAMP}"),
        ("master", "Regular", f"Regular@ {STAMP}"),
        ("chosen mask", "mask.Regular@ a", "mask.Regular"),
        ("chosen", "Regular@ a", "Regular"),
    ]


def test_plan_swap_when_single_master_then_plain_mask_follows_master() -> None:
    module = load("Use Layer As Master")
    taken = ["Regular", "Regular@ a", "mask", "mask.Regular@ a"]
    steps = module.plan_swap("Regular", "Regular@ a", taken, STAMP, ("Regular",), (True, True))
    assert steps[2] == ("chosen mask", "mask.Regular@ a", "mask")
    assert steps[0] == ("master mask", "mask", f"mask.Regular@ {STAMP}")


def test_plan_swap_when_no_masks_then_two_renames_and_backup_counts_up() -> None:
    module = load("Use Layer As Master")
    taken = ["Regular", "Regular@ a", f"Regular@ {STAMP}"]
    steps = module.plan_swap("Regular", "Regular@ a", taken, STAMP, ("Regular", "Bold"), (False, False))
    assert steps == [("master", "Regular", f"Regular@ {STAMP} (2)"), ("chosen", "Regular@ a", "Regular")]


def test_plan_swap_when_chosen_mask_would_clash_then_value_error() -> None:
    module = load("Use Layer As Master")
    taken = ["Regular", "Regular@ a", "mask.Regular@ a", "mask.Regular"]
    with pytest.raises(ValueError, match="chosen mask cannot take the name 'mask.Regular'"):
        module.plan_swap("Regular", "Regular@ a", taken, STAMP, ("Regular", "Bold"), (False, True))


def master_glyph(world: World, with_masks: bool = True) -> tuple[Glyph, Layer, Layer]:
    glyph = Glyph("a", ["Regular", "Regular@ a"] + (["mask.Regular", "mask.Regular@ a"] if with_masks else []))
    master, chosen = glyph.layer("Regular"), glyph.layer("Regular@ a")
    if with_masks:
        master.masks[True], chosen.masks[True] = glyph.layer("mask.Regular"), glyph.layer("mask.Regular@ a")
    world.occupy(glyph, "Regular@ a")
    return glyph, master, chosen


def test_run_when_promoting_then_names_swap_masks_follow_and_one_notification(world: World) -> None:
    module = load("Use Layer As Master")
    fixed_clock(module)
    glyph, master, chosen = master_glyph(world)
    old_master_mask, old_chosen_mask = master.masks[True], chosen.masks[True]
    messages = module.run()
    assert (master.name, chosen.name) == (f"Regular@ {STAMP}", "Regular")
    assert old_master_mask.name == f"mask.Regular@ {STAMP}" and old_chosen_mask.name == "mask.Regular"
    assert messages == ["a: 'Regular@ a' is now the master layer"]
    (title, objects), = world.notifier.calls
    assert title == "Use Layer As Master" and objects[-1] is glyph
    assert {id(x) for x in objects[:-1]} == {id(master), id(chosen), id(old_master_mask), id(old_chosen_mask)}
    assert glyph.history == [0] and master.history == [0]


def test_run_when_rename_fails_midway_then_old_names_restored(world: World) -> None:
    module = load("Use Layer As Master")
    fixed_clock(module)
    glyph, _master, chosen = master_glyph(world)
    chosen.fail_name = "Regular"
    with pytest.raises(world.app["history"].PartialWriteError, match="rename refused.*Edit > Undo"):
        module.run()
    assert [x.name for x in glyph.layers] == ["Regular", "Regular@ a", "mask.Regular", "mask.Regular@ a"]
    assert len(world.notifier.calls) == 1


def test_run_when_fontlab_keeps_old_name_then_runtime_error_and_restore(world: World) -> None:
    module = load("Use Layer As Master")
    fixed_clock(module)
    glyph, _master, chosen = master_glyph(world, with_masks=False)
    chosen.ignore_rename = True
    with pytest.raises(RuntimeError, match="kept the name"):
        module.run()
    assert [x.name for x in glyph.layers] == ["Regular", "Regular@ a"]


@pytest.mark.parametrize(
    "setup,message",
    [
        (lambda g, m, c: setattr(c, "locked_flag", None) or setattr(c, "isLocked", True), "locked"),
        (lambda g, m, c: setattr(m, "autoLayer", True), "locked, automatic"),
        (lambda g, m, c: setattr(c, "image", NS(isNull=False, isValid=True)), "image layer"),
        (lambda g, m, c: setattr(c.masks[True], "_name", "mask.odd"), "not 'mask.Regular@ a'"),
    ],
)
def test_run_when_unsafe_then_refused_before_any_rename(world: World, setup: Any, message: str) -> None:
    module = load("Use Layer As Master")
    fixed_clock(module)
    glyph, master, chosen = master_glyph(world)
    setup(glyph, master, chosen)
    names = [x.name for x in glyph.layers]
    with pytest.raises(ValueError, match=message):
        module.run()
    assert [x.name for x in glyph.layers] == names and world.notifier.calls == []


def test_run_when_already_master_or_no_master_or_twice_then_value_error(world: World) -> None:
    module = load("Use Layer As Master")
    fixed_clock(module)
    glyph = Glyph("a", ["Regular", "Regular@ a", "Odd"])
    world.occupy(glyph, "Regular")
    with pytest.raises(ValueError, match="already the master layer"):
        module.run()
    world.occupy(glyph, "Regular@ a")
    with pytest.raises(ValueError, match="already the master"):
        module.run()  # first occurrence is the master layer
    world.occurrences.clear()
    world.occupy(glyph, "Regular@ a")
    world.occupy(glyph, "Regular@ a")
    with pytest.raises(ValueError, match="selected twice"):
        module.run()
    world.occurrences.clear()
    world.occupy(glyph, "Odd")
    with pytest.raises(ValueError, match="belongs to no master"):
        module.run()


# ---------------------------------------------------------------- transform background
def test_parse_number_when_text_then_float_or_value_error() -> None:
    module = load("Transform Background")
    assert module.parse_number("10") == 10 and module.parse_number(" 1,5 ") == 1.5
    assert module.parse_number("-12.25") == -12.25
    for bad in ("", "  ", "abc", "nan", "inf", "1e999"):
        with pytest.raises(ValueError):
            module.parse_number(bad)


def test_matrices_when_built_then_exact_and_scale_must_be_positive() -> None:
    module = load("Transform Background")
    assert module.scale_matrix(50) == (0.5, 0.0, 0.0, 0.5, 0.0, 0.0)
    assert module.scale_matrix(125) == (1.25, 0.0, 0.0, 1.25, 0.0, 0.0)
    assert module.shift_matrix(-12.5) == (1.0, 0.0, 0.0, 1.0, -12.5, 0.0)
    for bad in (0, -5):
        with pytest.raises(ValueError, match="above 0%"):
            module.scale_matrix(bad)


def with_backgrounds(world: World, names: tuple[str, ...], plain: tuple[str, ...] = ()) -> list[Glyph]:
    glyphs = []
    for name in names + plain:
        glyph = Glyph(name, ["Regular", "mask.Regular"] if name in names else ["Regular"])
        if name in names:
            glyph.layer("Regular").masks[True] = glyph.layer("mask.Regular")
        world.occupy(glyph, "Regular")
        glyphs.append(glyph)
    return glyphs


def test_transform_backgrounds_when_selected_then_mask_transformed_and_one_step(world: World) -> None:
    module = load("Transform Background")
    a, b, c = with_backgrounds(world, ("a", "b"), ("c",))
    matrix = module.scale_matrix(50)
    message = module.transform_backgrounds("Scale", matrix)
    assert message == "Scale: 2 background(s) in 2 glyph(s)."
    for glyph in (a, b):
        mask = glyph.layer("mask.Regular")
        assert mask.calls == [("applyTransform", (("QTransform", matrix), True, False, False, True)),
                              "changed", "update"]
    (title, objects), = world.notifier.calls
    assert title == "Scale background"
    assert objects == [a.layer("mask.Regular"), b.layer("mask.Regular"), a, b]
    assert c.layer("Regular").calls == [] and c.history == []


def test_transform_backgrounds_when_none_or_mask_selected_then_value_error(world: World) -> None:
    module = load("Transform Background")
    with pytest.raises(ValueError, match="Select a glyph"):
        module.transform_backgrounds("Shift", module.shift_matrix(5))
    with_backgrounds(world, (), ("c",))
    with pytest.raises(ValueError, match="no background|None of the selected"):
        module.transform_backgrounds("Shift", module.shift_matrix(5))
    glyph = Glyph("m", ["mask.Regular"])
    world.occupy(glyph, "mask.Regular")
    with pytest.raises(ValueError, match="not a body layer"):
        module.transform_backgrounds("Shift", module.shift_matrix(5))
    assert world.notifier.calls == []


def test_transform_backgrounds_when_update_fails_then_runtime_error_after_notification(world: World) -> None:
    module = load("Transform Background")
    (a,) = with_backgrounds(world, ("a",))
    a.layer("mask.Regular").update_result = False
    with pytest.raises(world.app["history"].PartialWriteError, match="could not update.*Edit > Undo"):
        module.transform_backgrounds("Scale", module.scale_matrix(90))
    assert len(world.notifier.calls) == 1


def make_panel(module: ModuleType) -> Any:
    """Build the script's panel on the fake Qt widgets."""
    return module.panel_type(fake_gui())()


def test_panel_when_buttons_pressed_then_actions_run_and_errors_show_in_status(world: World, monkeypatch: Any) -> None:
    module = load("Transform Background")
    panel = make_panel(module)
    calls = []
    monkeypatch.setattr(module, "transform_backgrounds", lambda action, matrix, **kwargs: calls.append((action, matrix)) or "ok")
    panel.scale_edit.__dict__["value"] = "50"
    panel.shift_edit.__dict__["value"] = "-3,5"
    panel.apply("scale")
    panel.apply("shift")
    assert calls == [("Scale", module.scale_matrix(50)), ("Shift", module.shift_matrix(-3.5))]
    panel.scale_edit.__dict__["value"] = "zero"
    panel.apply("scale")
    assert panel.status.texts[-1] == "'zero' is not a number." and len(calls) == 2
    assert len(panel.scale_button.slots) == 1 and len(panel.shift_edit.slots) == 1
    panel.closeEvent("event")
    assert ("close", "masters_transform_background") in world.selected_calls


def test_main_when_called_then_registry_gets_panel_class(world: World) -> None:
    key, kind = load("Transform Background").main()
    assert key == "masters_transform_background" and isinstance(kind, type)


# ---------------------------------------------------------------- selection to all backgrounds
def test_selected_indexes_when_flags_then_only_fully_selected_nonempty() -> None:
    module = load("Selection To All Backgrounds")
    assert module.selected_indexes([(True, True), (True, False), (), (True,)]) == [0, 3]
    assert module.selected_indexes([]) == []


SELECTED_BIT = 0x0020


class Contour:
    """Fake contour. Nodes carry selection, raw state and a name."""

    def __init__(self, flags: tuple[bool, ...], states: Any = None, names: Any = None) -> None:
        self.name = "contour-name"
        self.flags = flags
        self.states = tuple(states or (0x0100 | (SELECTED_BIT if f else 0) for f in flags))
        self.names = tuple(names or (f"n{i}" for i in range(len(flags))))
        self._nodes = [NS(selected=f, nodeState=s, name=n, x=10.0 * i, y=0.0, type="on")
                       for i, (f, s, n) in enumerate(zip(flags, self.states, self.names))]

    def nodes(self) -> list[Any]:
        return list(self._nodes)

    def lossy_copy(self) -> "Contour":
        """What FontLab's clone does: keeps selection, drops raw state and names."""
        copy = Contour(self.flags, states=[0] * len(self.flags), names=[""] * len(self.flags))
        copy.name = ""
        return copy


class Shape:
    _ids = iter(range(1000, 9999))

    def __init__(self, contours: list[Contour], component: bool = False) -> None:
        self.id, self.isComponent, self.contours = next(Shape._ids), component, list(contours)
        self.clone_count = 0
        self.shapeData = NS(note="", name="")
        self.active = self.selected = False

    def clone(self) -> "Shape":
        """Clone like FontLab 9.0.9787: note, names, flags and node states are lost."""
        self.clone_count += 1
        return Shape([c.lossy_copy() for c in self.contours], self.isComponent)

    def removeContour(self, contour: Contour) -> None:
        self.contours.remove(contour)


def font_world(world: World) -> dict[str, Glyph]:
    """Source glyph 's' with 2 selected of 3 contours, plus five other glyphs."""
    source = Glyph("s", ["Regular", "Bold", "mask.Regular"], gid=11)
    layer = source.layer("Regular")
    layer.masks[True] = source.layer("mask.Regular")
    keep1, keep2, partial = Contour((True, True)), Contour((True,)), Contour((True, False))
    layer.shapes = [Shape([keep1, partial]), Shape([], component=True), Shape([keep2])]
    world.occupy(source, "Regular")
    other = Glyph("b", ["Regular"], gid=12)                          # no mask: created
    withmask = Glyph("c", ["Regular", "mask.Regular"], gid=13)       # mask: replaced
    withmask.layer("Regular").masks[True] = withmask.layer("mask.Regular")
    auto = Glyph("d", ["Regular", "Bold"], gid=14, Bold={"auto": True})  # skipped
    locked = Glyph("e", ["Regular"], gid=15, Regular={"locked": True})   # skipped
    nomaster = Glyph("f", ["Bold"], gid=16)                          # skipped
    glyphs = {g.name: g for g in (source, other, withmask, auto, locked, nomaster)}
    world.glyphs = list(glyphs.values())
    world.package.findName = lambda name: glyphs.get(name)
    world.window_calls, world.glyph_window_active = [], False

    def font_window_guard(package_id: int) -> None:
        """Stand-in for edit_guards.require_selection_window (Font window active?)."""
        world.window_calls.append(package_id)
        if world.glyph_window_active:
            raise ValueError("Activate the Font window before selecting glyphs.")

    world.app["edit_guards"].require_selection_window = font_window_guard
    return glyphs


def in_font_window(world: World, glyphs: dict[str, Glyph]) -> None:
    """Leave the Glyph window: no editor occurrence, and node selection reads as cleared."""
    world.context, world.glyph_window_active = (1, "Regular", "font"), False
    world.occurrences.clear()
    for shape in glyphs["s"].layer("Regular").shapes:
        for contour in shape.contours:
            for node in contour.nodes():
                node.selected = False


def test_make_plan_when_selection_then_counts_and_skips_exact(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    plan = module.make_plan()
    assert (plan.glyph, plan.master, plan.contours) == ("s", "Regular", 2)
    assert (plan.replaced, plan.created, plan.skipped) == (2, 1, 3)
    assert [g.name for g, _ in plan.targets] == ["s", "b", "c"]
    assert "2 selected contour(s) of 's'" in plan.summary() and "3 glyph(s) are skipped" in plan.summary()
    assert module.make_plan() == plan  # equality ignores native handles
    assert glyphs["s"].history == []   # planning writes nothing


@pytest.mark.parametrize("context,message", [((1, "Regular", "font"), "Glyph window"), ((1, "Regular", "editor", 7, ()), "Glyph window")])
def test_make_plan_when_no_editor_or_selection_then_value_error(world: World, context: tuple, message: str) -> None:
    world.context = context
    with pytest.raises(ValueError, match=message):
        load("Selection To All Backgrounds").make_plan()


def test_make_plan_when_no_full_contour_or_mask_layer_selected_then_value_error(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyph = Glyph("s", ["Regular", "mask.Regular"])
    glyph.layer("Regular").shapes = [Shape([Contour((True, False))])]
    world.occupy(glyph, "Regular")
    with pytest.raises(ValueError, match="No fully selected contour"):
        module.make_plan()
    world.occurrences.clear()
    world.occupy(glyph, "mask.Regular")
    with pytest.raises(ValueError, match="not on a background"):
        module.make_plan()


def test_replace_backgrounds_when_confirmed_then_all_targets_replaced_in_one_step(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    shown = module.make_plan()
    in_font_window(world, glyphs)  # the user switches to the Font window; selection is not read again
    message = module.replace_backgrounds(shown)
    assert message == "Background set in 3 glyph(s)."
    assert world.window_calls == [1]  # Font-window guard checked with the planned package id
    for name in ("s", "c"):
        mask = glyphs[name].layer("mask.Regular")
        assert "removeAllShapes" not in mask.calls
        assert [len(s.contours) for s in mask.shapes] == [1, 1]  # partial contour dropped
    created = glyphs["b"].layer("Regular").masks[True]
    assert [len(s.contours) for s in created.shapes] == [1, 1]
    (title, objects), = world.notifier.calls
    assert title == "Selection To All Backgrounds"
    old = [glyphs["s"].layer("mask.Regular"), glyphs["c"].layer("mask.Regular")]
    assert objects == [*old, created, glyphs["s"], glyphs["b"], glyphs["c"]]
    assert all(g.lastModified == "UTC-STAMP" for g in (glyphs["s"], glyphs["b"], glyphs["c"]))
    assert glyphs["d"].history == [] and glyphs["d"].lastModified is None  # skipped glyphs untouched
    assert glyphs["s"].layer("Regular").shapes[0].contours[1].flags == (True, False)  # source intact


def test_replace_backgrounds_when_glyph_window_active_then_wrong_window_and_nothing_read_or_written(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    shown = module.make_plan()
    world.glyph_window_active = True
    with pytest.raises(module.WrongWindow, match="Switch to the Font window"):
        module.replace_backgrounds(shown)
    assert issubclass(module.WrongWindow, ValueError)
    assert world.notifier.calls == [] and glyphs["c"].layer("mask.Regular").calls == []
    assert all(g.history == [] for g in glyphs.values())


def test_replace_backgrounds_when_planned_contour_edited_then_nothing_written(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    shown = module.make_plan()
    in_font_window(world, glyphs)
    glyphs["s"].layer("Regular").shapes[2].contours[0].nodes()[0].x = 999.0
    with pytest.raises(ValueError, match="changed"):
        module.replace_backgrounds(shown)
    assert world.notifier.calls == []


def test_replan_when_source_glyph_or_layer_gone_then_value_error(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    shown = module.make_plan()
    glyphs["s"].layer("Regular")._name = "Renamed"
    with pytest.raises(ValueError, match="changed"):
        module.replan(shown)
    world.package.findName = lambda name: None
    with pytest.raises(ValueError, match="changed"):
        module.replan(shown)


def test_replace_backgrounds_when_font_changed_since_preview_then_nothing_written(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    shown = module.make_plan()
    glyphs["b"].layers.append(Layer("x", glyphs["b"]))
    glyphs["c"].layer("Regular").isLocked = True
    with pytest.raises(ValueError, match="changed"):
        module.replace_backgrounds(shown)
    assert world.notifier.calls == [] and glyphs["c"].layer("mask.Regular").calls == []


def test_replace_backgrounds_when_mask_update_fails_then_error_and_history_closed(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    glyphs["c"].layer("mask.Regular").update_result = False
    shown = module.make_plan()
    with pytest.raises(RuntimeError, match="could not update the background of 'c'.*Edit > Undo"):
        module.replace_backgrounds(shown)
    assert len(world.notifier.calls) == 1


def test_replace_backgrounds_when_time_limit_hit_then_runtime_error(world: World, monkeypatch: Any) -> None:
    module = load("Selection To All Backgrounds")
    font_world(world)
    shown = module.make_plan()
    monkeypatch.setattr(module, "WRITE_SECONDS", -1.0)
    with pytest.raises(RuntimeError, match="time limit"):
        module.replace_backgrounds(shown)


def test_selection_panel_when_opened_then_preview_and_single_replace(world: World, monkeypatch: Any) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    panel = make_panel(module)
    assert panel.plan is not None and "2 selected contour(s)" in panel.preview.texts[-1]
    assert "Switch to the Font window" in panel.preview.texts[-1]
    world.glyph_window_active = True
    panel.replace()  # refused in the Glyph window: preview and button stay
    assert "Switch to the Font window" in panel.status.texts[-1] and panel.plan is not None
    assert world.notifier.calls == []
    in_font_window(world, glyphs)
    panel.refresh()  # no editor any more: the planned contours are read again
    assert panel.plan is not None and "2 selected contour(s)" in panel.preview.texts[-1]
    panel.replace()
    assert panel.status.texts[-1] == "Background set in 3 glyph(s)." and panel.plan is None
    panel.replace()  # second click does nothing
    assert len(world.notifier.calls) == 1
    world.occurrences.clear()
    panel.refresh()
    assert panel.plan is None and "Glyph window" in panel.status.texts[-1]


def test_selection_panel_when_glyph_window_selection_cleared_then_refresh_clears_plan(world: World) -> None:
    """Refresh in a Glyph window reads the selection again; it never falls back to the old plan."""
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    panel = make_panel(module)
    assert panel.plan is not None and panel.go.enabled is True
    for shape in glyphs["s"].layer("Regular").shapes:  # the user deselects in the Glyph window
        for contour in shape.contours:
            for node in contour.nodes():
                node.selected = False
    assert world.context[2] == "editor"
    panel.refresh()
    assert panel.plan is None and panel.go.enabled is False
    assert "No fully selected contour" in panel.status.texts[-1] and panel.preview.texts[-1] == ""
    panel.replace()  # nothing to write
    assert world.notifier.calls == []


def test_selection_panel_when_font_window_then_refresh_rereads_planned_contours(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    panel = make_panel(module)
    shown = panel.plan
    in_font_window(world, glyphs)
    with pytest.raises(module.NotInGlyphWindow):
        module.make_plan()
    panel.refresh()
    assert panel.plan == shown and panel.go.enabled is True and panel.status.texts[-1] == ""


def test_replace_backgrounds_when_font_closed_then_font_gone_not_wrong_window(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    panel = make_panel(module)
    in_font_window(world, glyphs)
    world.app["scripting"].current_package = lambda *a: None  # font closed
    with pytest.raises(ValueError, match="closed or another font") as raised:
        module.replace_backgrounds(panel.plan)
    assert not isinstance(raised.value, module.WrongWindow) and world.window_calls == []
    panel.replace()
    assert "closed or another font" in panel.status.texts[-1]
    assert panel.plan is None and panel.go.enabled is False and world.notifier.calls == []


# ---------------------------------------------------------------- select different colour
MARKS = [("a", 0), ("b", 45), ("c", 45), ("d", 200), ("e", 0)]


def test_different_colour_when_selection_then_other_marks_in_font_order() -> None:
    module = load("Select Different Colour")
    assert module.different_colour(MARKS, ["b"]) == ["a", "d", "e"]
    assert module.different_colour(MARKS, ["a", "d"]) == ["b", "c"]
    assert module.different_colour(MARKS, ["b", "c", "a", "d", "e"]) == []
    assert module.different_colour(MARKS, ["zzz", "e"]) == ["b", "c", "d"]


@pytest.mark.parametrize("selected", [[], ["unknown"]])
def test_different_colour_when_no_listed_glyph_selected_then_value_error(selected: list[str]) -> None:
    with pytest.raises(ValueError, match="Select at least one glyph"):
        load("Select Different Colour").different_colour(MARKS, selected)


def test_run_when_selection_then_select_glyphs_adds_with_package_id(world: World) -> None:
    module = load("Select Different Colour")
    world.marks, world.font_selection = list(MARKS), ["b"]
    assert module.run() == "Added 3 glyph(s) of a different colour."
    assert world.selected_calls == [(["a", "d", "e"], {"package_id": 1, "add": True})]


def test_run_when_all_share_colour_then_nothing_added_and_main_prints(world: World, capsys: Any) -> None:
    module = load("Select Different Colour")
    world.marks, world.font_selection = [("a", 3), ("b", 3)], ["a"]
    assert "nothing to add" in module.run()
    assert world.selected_calls == []
    world.font_selection = []
    module.main()
    assert "Select Different Colour: Select at least one glyph" in capsys.readouterr().out


def test_run_when_no_package_then_value_error(world: World) -> None:
    world.package = None
    with pytest.raises(ValueError, match="Open a font"):
        load("Select Different Colour").run()


# ================================================================ clone repair, errors
# ---- clone repair (FontLab clone drops note, names, flags, node state; fl#8516, fl#8538)
def rich_source(world: World) -> Any:
    """A glyph whose layer holds one shape with every field the clone loses."""
    glyph = Glyph("a", ["Regular"])
    shape = Shape([Contour((False, True), states=(0x0111, 0x0131), names=("start", "top"))])
    shape.shapeData.note, shape.shapeData.name = "keep me", "body"
    shape.active = shape.selected = True
    glyph.layer("Regular").shapes = [shape]
    world.occupy(glyph, "Regular")
    return glyph


DUPLICATE_FIELDS = [
    ("note", lambda s: s.shapeData.note, "keep me"),
    ("shape name", lambda s: s.shapeData.name, "body"),
    ("active flag", lambda s: s.active, True),
    ("selected flag", lambda s: s.selected, True),
    ("node raw state", lambda s: [n.nodeState for n in s.contours[0].nodes()], [0x0111, 0x0131]),
    ("node names", lambda s: [n.name for n in s.contours[0].nodes()], ["start", "top"]),
]


@pytest.mark.parametrize("field,read,expected", DUPLICATE_FIELDS, ids=[f[0] for f in DUPLICATE_FIELDS])
def test_run_when_duplicating_then_clone_loss_is_repaired(world: World, field: str, read: Any, expected: Any) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = rich_source(world)
    module.run()
    assert read(glyph.layers[-1].shapes[0]) == expected, f"copy lost the {field}"
    assert read(glyph.layer("Regular").shapes[0]) == expected  # source untouched


def test_run_when_clone_changes_shape_count_then_refused_before_adding(world: World) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = rich_source(world)
    glyph.layer("Regular").clone = lambda: NS(shapes=[], name="Regular", isNull=False, isValid=True)
    with pytest.raises(RuntimeError, match="shape count"):
        module.run()
    assert len(glyph.layers) == 1


BACKGROUND_FIELDS = [
    ("note", lambda s: s.shapeData.note, "keep me"),
    ("shape name", lambda s: s.shapeData.name, "body"),
    ("node raw state without selection bit", lambda s: [n.nodeState for n in s.contours[0].nodes()], [0x0111, 0x0111]),
    ("node names", lambda s: [n.name for n in s.contours[0].nodes()], ["start", "top"]),
    ("shape not active", lambda s: s.active, False),
    ("shape not selected", lambda s: s.selected, False),
]


@pytest.mark.parametrize("field,read,expected", BACKGROUND_FIELDS, ids=[f[0] for f in BACKGROUND_FIELDS])
def test_replace_backgrounds_when_cloning_then_clone_loss_is_repaired(world: World, field: str, read: Any, expected: Any) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    shape = glyphs["s"].layer("Regular").shapes[0]
    shape.contours[0] = Contour((True, True), states=(0x0131, 0x0131), names=("start", "top"))
    shape.shapeData.note, shape.shapeData.name = "keep me", "body"
    shape.active = shape.selected = True
    module.replace_backgrounds(module.make_plan())
    mask = glyphs["b"].layer("Regular").masks[True]
    assert read(mask.shapes[0]) == expected, f"background copy: {field}"


# ---- panels and mains survive RuntimeError
def test_transform_panel_when_runtime_error_then_status_shows_message(world: World, monkeypatch: Any) -> None:
    module = load("Transform Background")
    panel = make_panel(module)

    def boom(action: str, matrix: Any, **kwargs: Any) -> str:
        raise RuntimeError("boom: Edit > Undo")

    monkeypatch.setattr(module, "transform_backgrounds", boom)
    panel.apply("scale")
    assert panel.status.texts[-1] == "boom: Edit > Undo"


def test_selection_panel_when_runtime_error_then_status_plan_cleared_and_button_disabled(world: World, monkeypatch: Any) -> None:
    module = load("Selection To All Backgrounds")
    font_world(world)
    panel = make_panel(module)

    def boom(plan: Any, **kwargs: Any) -> str:
        raise RuntimeError("boom: Edit > Undo")

    monkeypatch.setattr(module, "replace_backgrounds", boom)
    panel.replace()
    assert panel.status.texts[-1] == "boom: Edit > Undo"
    assert panel.plan is None and panel.go.enabled is False


def test_selection_panel_when_stale_preview_then_also_cleared(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    panel = make_panel(module)
    glyphs["c"].layer("Regular").isLocked = True
    panel.replace()
    assert "changed" in panel.status.texts[-1] and panel.plan is None and panel.go.enabled is False


@pytest.mark.parametrize(
    "title",
    ["Display Next Layer", "Display Previous Layer", "Use Layer As Master", "Select Different Colour"],
)
def test_main_when_runtime_error_then_printed_not_raised(world: World, monkeypatch: Any, capsys: Any, title: str) -> None:
    module = load(title)
    monkeypatch.setattr(module, "run", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom")))
    module.main()
    assert f"{title}: boom" in capsys.readouterr().out


# ---- never edit a glyph that is, or is a base of, an automatic layer
def auto_world(world: World, name: str = "a") -> Glyph:
    """Glyph `name` is a base of automatic glyph 'aacute'."""
    world.records = (("aacute", True, (name,)), (name, False, ()))
    glyph = Glyph(name, ["Regular", "Regular@ old", "mask.Regular", "mask.Regular@ old"])
    glyph.layer("Regular").masks[True] = glyph.layer("mask.Regular")
    glyph.layer("Regular@ old").masks[True] = glyph.layer("mask.Regular@ old")
    world.occupy(glyph, "Regular@ old")
    return glyph


@pytest.mark.parametrize("title", ["Duplicate Current Layer", "Use Layer As Master"])
def test_layer_scripts_when_glyph_is_base_of_auto_layer_then_refused_untouched(world: World, title: str) -> None:
    module = load(title)
    fixed_clock(module)
    glyph = auto_world(world)
    names = [x.name for x in glyph.layers]
    with pytest.raises(ValueError, match="a: base of auto aacute"):
        module.run()
    assert [x.name for x in glyph.layers] == names and world.notifier.calls == [] and glyph.history == []


@pytest.mark.parametrize("title", ["Duplicate Current Layer", "Use Layer As Master"])
def test_layer_scripts_when_base_reaches_auto_through_manual_composite_then_refused(world: World, title: str) -> None:
    module = load(title)
    fixed_clock(module)
    glyph = auto_world(world)
    # a -> manual composite "ab" -> automatic "abacute"
    world.records = (("ab", False, ("a",)), ("abacute", True, ("ab",)), ("a", False, ()))
    with pytest.raises(ValueError, match="a: base of auto abacute"):
        module.run()
    assert world.notifier.calls == [] and glyph.history == []


def test_duplicate_when_glyph_owns_auto_layer_then_refused_before_history(world: World) -> None:
    module = load("Duplicate Current Layer")
    fixed_clock(module)
    glyph = Glyph("aacute", ["Regular", "Bold"], Bold={"auto": True})
    world.records = (("aacute", False, ()), ("aacute", True, ("a", "acute")))
    world.occupy(glyph, "Regular")
    with pytest.raises(ValueError, match="aacute: has auto layers"):
        module.run()
    assert len(glyph.layers) == 2 and world.notifier.calls == [] and glyph.history == []


def test_transform_backgrounds_when_glyph_is_base_of_auto_layer_then_refused(world: World) -> None:
    module = load("Transform Background")
    glyph = auto_world(world)
    world.occurrences[0].layer = glyph.layer("Regular")
    world.occurrences[0].layer_name = "Regular"
    with pytest.raises(ValueError, match="a: base of auto aacute"):
        module.transform_backgrounds("Scale", module.scale_matrix(50))
    assert world.notifier.calls == [] and glyph.history == []


def test_transform_backgrounds_when_pending_updates_then_writes_and_keeps_queue(world: World, capsys) -> None:
    module = load("Transform Background")
    (a,) = with_backgrounds(world, ("a",))
    world.pending = (9,)
    result = module.transform_backgrounds("Scale", module.scale_matrix(90))
    assert world.pending == (9,) and world.notifier.calls
    output = capsys.readouterr().out
    assert "(9,)" in output and "Queued glyph ids:" in output and "8537" in output and "modification dates" in output


def test_selection_to_all_backgrounds_when_glyph_is_base_of_auto_layer_then_skipped(world: World) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    world.records = (("d", True, ("b",)), ("b", False, ()))  # b is a base of automatic d
    plan = module.make_plan()
    assert [g.name for g, _ in plan.targets] == ["s", "c"] and plan.skipped == 4
    module.replace_backgrounds(plan)
    assert glyphs["b"].history == [] and glyphs["b"].lastModified is None
    objects = world.notifier.calls[0][1]
    assert glyphs["b"] not in objects and glyphs["d"] not in objects


def test_selection_to_all_backgrounds_when_base_through_manual_composite_then_skipped(world: World) -> None:
    module = load("Selection To All Backgrounds")
    font_world(world)
    # automatic "y" uses manual "x", which uses "c"
    world.records = (("x", False, ("c",)), ("y", True, ("x",)), ("c", False, ()))
    plan = module.make_plan()
    assert "c" in plan.skipped_names and "c" not in [g.name for g, _ in plan.targets]


# ---- minors
def test_transform_panel_hint_when_shown_then_names_the_origin() -> None:
    text = (FOLDER / "Transform Background.py").read_text()
    assert "origin (0, 0)" in text.split("def panel_type")[1]


# ================================================================ real App names
def test_used_app_names_when_parsed_then_cover_the_real_modules() -> None:
    names = app_names_used([FOLDER / f"{title}.py" for title in SCRIPTS])
    assert set(names) == {
        "fly.ap.history", "fly.ap.masters", "fly.ap.layer_selection", "fly.ap.qtsafe", "fly.ap.scripting",
        "fly.ap.selection_panel", "fly.ap.contour_copy", "fly.ap.edit_guards",
    }
    assert {"commit", "scan_auto_facts", "refusal"} <= names["fly.ap.history"]
    assert names["fly.ap.masters"] == {"associated_master", "backup_master", "backup_layer_name", "default_suffix"}
    assert "capture" in names["fly.ap.layer_selection"] and "qt_list" in names["fly.ap.qtsafe"]


def test_real_app_names_when_imported_from_installed_app_then_all_exist() -> None:
    used = app_names_used([FOLDER / f"{title}.py" for title in SCRIPTS])
    check_real_app_names(used)


def test_scripts_when_parsed_then_no_private_commit_or_guard_copy() -> None:
    for title in SCRIPTS:
        tree = ast.parse((FOLDER / f"{title}.py").read_text())
        defined = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        assert not defined & {"commit", "require_no_auto_dependants", "auto_related"}, title


# ---- TimeoutError from capture() never escapes
@pytest.mark.parametrize(
    "title",
    ["Display Next Layer", "Display Previous Layer", "Use Layer As Master"],
)
def test_main_when_capture_times_out_then_printed_not_raised(world: World, capsys: Any, title: str) -> None:
    world.capture_error = TimeoutError("capture expired")
    load(title).main()
    assert f"{title}: capture expired" in capsys.readouterr().out


def test_transform_panel_when_capture_times_out_then_status_shows_message(world: World) -> None:
    module = load("Transform Background")
    panel = make_panel(module)
    world.capture_error = TimeoutError("capture expired")
    panel.apply("scale")
    assert panel.status.texts[-1] == "capture expired"


def test_selection_panel_when_capture_times_out_in_init_then_status_shows_message(world: World) -> None:
    module = load("Selection To All Backgrounds")
    world.capture_error = TimeoutError("capture expired")
    panel = make_panel(module)
    assert panel.plan is None and panel.status.texts[-1] == "capture expired" and panel.go.enabled is False


# ---- preview lists skipped glyphs; public docstrings carry no acceptance status
def test_make_plan_when_glyphs_skipped_then_names_listed_in_preview(world: World) -> None:
    module = load("Selection To All Backgrounds")
    font_world(world)
    plan = module.make_plan()
    assert plan.skipped_names == ("d", "e", "f")
    assert "Skipped: d, e, f." in plan.summary()


def test_summary_when_more_than_ten_skipped_then_ten_names_and_count() -> None:
    module = load("Selection To All Backgrounds")
    names = tuple(f"g{i}" for i in range(13))
    plan = module.Plan("s", "Regular", 1, (), 0, 0, 13, skipped_names=names)
    text = plan.summary()
    assert "g9" in text and "g10" not in text and "and 3 more" in text


@pytest.mark.parametrize("title", SCRIPTS)
def test_docstring_when_public_then_no_native_acceptance_sentence(title: str) -> None:
    doc = ast.get_docstring(ast.parse((FOLDER / f"{title}.py").read_text())) or ""
    assert "acceptance is pending" not in doc, title


def test_all_master_backup_when_suffix_given_then_inventory_and_active_preserved(world: World) -> None:
    module = load("Duplicate Current Layer")
    glyph = Glyph("a", ["Regular", "Bold", "Regular old"])
    world.occupy(glyph, "Regular")
    world.package.masters = ["Regular", "Bold"]
    active = glyph.active
    jobs = module.plan(all_masters=True, suffix="before")
    assert [name for _, _, name in jobs] == ["Regular backup before", "Bold backup before"]
    module.duplicate(jobs)
    assert glyph.active is active
    assert module.backups_of(glyph, world.package.masters) == ["Regular old", "Regular backup before", "Bold backup before"]
    assert len(world.notifier.calls) == 1
    assert world.notifier.calls[0][1] == [glyph.layers[-2], glyph.layers[-1], glyph]


def test_backup_when_native_add_changes_active_then_shown_layer_restored(world: World) -> None:
    module = load("Duplicate Current Layer")
    glyph = Glyph("a", ["Regular", "Bold"])
    world.occupy(glyph, "Regular")
    def add(layer: Any) -> None:
        layer.glyph = glyph
        glyph.layers.append(layer)
        glyph.active = layer
    glyph.addLayer = add
    module.duplicate(module.plan(all_masters=True, suffix="before"))
    assert glyph.active.name == "Regular"
    assert len(world.notifier.calls) == 1


def test_backup_when_added_layer_disappears_at_read_back_then_reported(world: World) -> None:
    module = load("Duplicate Current Layer")
    glyph = Glyph("a", ["Regular"])
    world.occupy(glyph, "Regular")
    original = world.notifier.notifyChangesApplied
    def notify(title: str, objects: list[Any]) -> None:
        original(title, objects)
        glyph.layers.pop()
    world.notifier.notifyChangesApplied = notify
    with pytest.raises(RuntimeError, match="did not store"):
        module.run()
    assert len(world.notifier.calls) == 1


@pytest.mark.parametrize("error", [RuntimeError("boom"), ValueError("bad font"), TimeoutError("capture expired")])
def test_duplicate_main_when_panel_startup_fails_then_printed_not_raised(
    world: World, monkeypatch: Any, capsys: Any, app_sources: Path, error: Exception,
) -> None:
    module = load("Duplicate Current Layer")
    spec = importlib.util.spec_from_file_location("c5_installed_scripting", app_sources / "scripting.py")
    real = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(real)
    def refuse(dialog_type: Callable[[Any], Any], key: str) -> Any:
        raise error
    assert inspect.signature(refuse) == inspect.signature(real.show_script_dialog)
    monkeypatch.setattr(world.app["scripting"], "show_script_dialog", refuse)
    monkeypatch.setattr(module, "panel_type", lambda: object)
    assert module.main() is None
    assert f"Duplicate Current Layer: {error}" in capsys.readouterr().out


def test_background_component_when_replaced_then_history_is_retained(world: World, monkeypatch: Any) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    mask = glyphs["c"].layer("mask.Regular")
    component = Shape([], component=True)
    mask.shapes = [component]
    import fly.ap.history as history
    component.shapeData.builder = object()
    retained = [component, component.shapeData, component.shapeData.builder]
    real_component_history = history.component_history
    reads = []
    def component_history(shape: Any) -> tuple[Any, ...]:
        assert shape in mask.shapes, "Read component history before detachment"
        reads.append(shape)
        return real_component_history(shape)
    monkeypatch.setattr(history, "component_history", component_history)
    seen = {}
    real_commit = history.commit
    def commit(*args: Any, **kwargs: Any) -> Any:
        seen.update(kwargs)
        return real_commit(*args, **kwargs)
    monkeypatch.setattr(history, "commit", commit)
    module.replace_backgrounds(module.make_plan())
    assert reads == [component] and seen["retain"] == retained
    assert world.notifier.deep, "Retained components require deep native history"
    assert world.notifier.calls[0][1][:3] == retained
    assert ("removeShape", component) in mask.calls
    assert "removeAllShapes" not in mask.calls



def test_backup_when_clone_drops_view_and_contour_names_then_shared_repair_keeps_them(world: World) -> None:
    module = load("Duplicate Current Layer")
    glyph = Glyph("a", ["Regular"])
    shape = Shape([Contour((True, False), states=(0x123, 0x100))])
    shape.contours[0].name = "named-contour"
    shape.shapeData.note, shape.shapeData.name = "note", "shape-name"
    shape.active = shape.selected = True
    glyph.layer("Regular").shapes = [shape]
    world.occupy(glyph, "Regular")
    created = module.duplicate(module.plan(suffix="trial"))
    copy = created[0].shapes[0]
    assert copy.contours[0].name == "named-contour", "Repair contour names on backups"
    assert copy.active and copy.selected, "Keep the source shape view state"
    assert [n.nodeState for n in copy.contours[0].nodes()] == [0x123, 0x100]
    assert (copy.shapeData.note, copy.shapeData.name) == ("note", "shape-name")


@pytest.mark.parametrize("failure", ["component", "outline", "add", "missing"])
def test_background_write_when_native_silently_loses_plan_then_reports_read_back(world: World, failure: str) -> None:
    module = load("Selection To All Backgrounds")
    glyphs = font_world(world)
    layer = glyphs["c"].layer("Regular")
    mask = glyphs["c"].layer("mask.Regular")
    if failure in ("component", "outline"):
        old = Shape([] if failure == "component" else [Contour((False,))], component=failure == "component")
        old.shapeData.builder = object()
        mask.shapes = [old]
        mask.removeShape = lambda shape: None
    elif failure == "add":
        mask.addShape = lambda shape: None
    else:
        original = world.notifier.notifyChangesApplied
        def notify(title: str, objects: list[Any], deep: bool = False) -> None:
            original(title, objects, deep)
            layer.masks.clear()
        world.notifier.notifyChangesApplied = notify
    reason = {"component": "component", "outline": "contours", "add": "contours", "missing": "missing background"}[failure]
    with pytest.raises(RuntimeError, match=rf"did not store.*c.*{reason}.*Edit > Undo"):
        module.replace_backgrounds(module.make_plan())
    assert len(world.notifier.calls) == 1, "Close history before reporting a silent native mismatch"
