# this_file: tests/test_issue122_S3.py
# SPDX-License-Identifier: Apache-2.0
"""The seven Names editors, against an in-memory FontLab and the real App helpers.

Each script keeps its algorithm at module level and builds its panel lazily.
The scan, refusal policy and one-step write are the real installed App module
`fly.ap.names_edit` (with `fly.ap.history` and `fly.ap.edit_guards`), loaded
over the fakes. So the tests load the script file, drive the core functions
with exact values, and drive the panel slots with Qt-shaped fakes. The fake
font logs every history call and every property write, so the one-Undo shape
is asserted exactly. Offline results do not prove native FontLab behaviour.
"""

import ast
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from unittest.mock import MagicMock

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
NAMES = ROOT / "Scripts" / "Names"
SCRIPTS = [
    "Glyph Tags",
    "Mark Color Palette",
    "Suffix Tool",
    "Batch Rename",
    "Batch Glyph Notes",
    "Glyph Notes",
    "Unicode From Names",
]
STAMP = "STAMP"


# ----------------------------------------------------------------- fake font
class Shape:
    def __init__(self, base: str) -> None:
        self.isComponent = True
        self.shapeData = NS(componentGlyph=base)


class Layer:
    def __init__(self, world: "World", owner: str, auto: bool, bases: tuple) -> None:
        self.world, self.owner, self.autoLayer = world, owner, auto
        self.shapes = [Shape(b) for b in bases]

    def checkInitHistoryState(self, level: int) -> None:
        self.world.log.append(("init", "layer", self.owner))


class Glyph:
    """FontLab glyph. The fgGlyph getter is a trap: S3 must never read it."""

    def __init__(self, world: "World", rec_id: int, name: str) -> None:
        self.world, self.fgGlyphId, self.id, self.name = (
            world,
            rec_id,
            rec_id + 1000,
            name,
        )
        self.isNull = False
        self.layers: list[Layer] = []
        self._note, self._tags, self._mark = "", [], 0
        self.sticky: set[str] = set()

    @property
    def fgGlyph(self) -> None:
        raise AssertionError("flGlyph.fgGlyph must never be read")

    def _set(self, field: str, value) -> None:
        self.world.log.append(("set", field, self.name, value))
        if field not in self.sticky:
            setattr(self, "_" + field, value)

    note = property(lambda s: s._note, lambda s, v: s._set("note", v))
    tags = property(lambda s: s._tags, lambda s, v: s._set("tags", list(v)))
    mark = property(lambda s: s._mark, lambda s, v: s._set("mark", v))
    lastModified = property(
        lambda s: STAMP, lambda s, v: s.world.log.append(("stamp", s.name))
    )

    def checkInitHistoryState(self, level: int) -> None:
        self.world.log.append(("init", "glyph", self.name))


class Record:
    """FontGate glyph record from font.glyphs."""

    def __init__(self, world: "World", rec_id: int, name: str, codes: tuple) -> None:
        self.world, self.id, self.name, self._codes = world, rec_id, name, list(codes)
        self.sticky = False

    @property
    def unicodes(self) -> list:
        return list(self._codes)

    @unicodes.setter
    def unicodes(self, value) -> None:
        self.world.log.append(("set", "unicodes", self.name, list(value)))
        if not self.sticky:
            self._codes = list(value)


class Package:
    def __init__(self, world: "World") -> None:
        self.world, self.id, self.isNull, self.master = world, 7, False, "Regular"
        self.rename_ok = True

    def findName(self, name: str):
        return self.world.glyphs.get(name)

    def findFgId(self, rec_id: int):
        return next(
            (g for g in self.world.glyphs.values() if g.fgGlyphId == rec_id), None
        )

    def renameGlyph(self, record, new: str, flag: bool) -> bool:
        assert isinstance(record, Record), "rename needs the font-owned record"
        self.world.log.append(("rename", record.name, new))
        if not self.rename_ok:
            return False
        glyph = self.world.glyphs.pop(record.name)
        glyph.name = record.name = new
        self.world.glyphs[new] = glyph
        return True


class World:
    """One font, its package, native namespace and an ordered event log."""

    def __init__(self) -> None:
        self.log: list = []
        self.glyphs: dict[str, Glyph] = {}
        self.records: list[Record] = []
        self.package = Package(self)
        self.pending: list = []
        self.glyph_window = False
        self.editors_open = False
        self.selected: list[str] = []
        self.font = NS(glyphs=self.records)
        self.has_font = True
        self.native = NS(
            CurrentFont=lambda: self.font if self.has_font else None,
            flWorkspace=NS(
                instance=lambda: NS(
                    currentPackage=self.package if self.has_font else None
                )
            ),
            flItems=lambda: NS(notifyChangesApplied=self.notify),
            flGlyph=NS(updatedFgGlyphs=lambda: tuple(self.pending)),
        )
        self.qtcore = NS(QDateTime=NS(currentDateTimeUtc=lambda: STAMP))

    def add(self, name, codes=(), note="", tags=(), mark=0, auto=False, bases=()):
        index = len(self.records)
        glyph = Glyph(self, index, name)
        glyph.layers = [Layer(self, name, False, ())]
        if auto:
            glyph.layers.append(Layer(self, name, True, bases))
        glyph._note, glyph._tags, glyph._mark = note, list(tags), mark
        self.glyphs[name] = glyph
        self.records.append(Record(self, index, name, codes))
        return glyph

    def notify(self, title: str, objects) -> None:
        shown = tuple(
            ("layer", o.owner) if isinstance(o, Layer) else ("glyph", o.name)
            for o in objects
        )
        self.log.append(("notify", title, shown))

    def edits(self) -> list:
        """Mutation events only, in order."""
        return [
            e for e in self.log if e[0] in {"set", "rename"} and e[1] != "lastModified"
        ]


def history(names: list[str], title: str, edits: list) -> list:
    """The exact App history order for glyphs NAMES (one manual layer each).

    history.commit starts the history of every layer first, then every glyph.
    """
    out: list = [("init", "layer", n) for n in names]
    out += [("init", "glyph", n) for n in names]
    out += edits
    out += [("stamp", n) for n in names]
    out.append(
        (
            "notify",
            title,
            tuple(("layer", n) for n in names) + tuple(("glyph", n) for n in names),
        )
    )
    out += [("stamp", n) for n in names]
    return out


@pytest.fixture
def world() -> World:
    w = World()
    for name in ("a", "b", "e"):
        w.add(name)
    w.add("ecircumflex", auto=True, bases=("e",))
    w.selected = ["a", "b"]
    return w


def load(name: str, monkeypatch) -> ModuleType:
    slug = "s3_" + re.sub(r"\W", "_", name.lower())
    spec = importlib.util.spec_from_file_location(slug, NAMES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, slug, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mods(monkeypatch):
    return {name: load(name, monkeypatch) for name in SCRIPTS}


def app(name: str) -> ModuleType:
    """The real App module that the scripts reach as fly.ap.NAME."""
    return sys.modules[f"fly.ap.{name}"]


def scan(world: "World"):
    """Scan the fake font with the real App names_edit.scan."""
    return app("names_edit").scan(world.native)


# ----------------------------------------------------------------- fake Qt
def widget(**attrs):
    item = MagicMock()
    item.configure_mock(**attrs)
    return item


class FakeBase:
    """Stand-in for fontlabapp NamesDialog: records connections, tolerates any Qt call."""

    def __init__(self, parent, title, key):
        self.title, self.key, self.parent = title, key, parent
        self.root, self.subtitle, self.palette = MagicMock(), MagicMock(), MagicMock()
        self.connected: list = []
        self.last_result = None
        self.stale = False

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        value = MagicMock()
        object.__setattr__(self, name, value)
        return value

    def make_table(self, headers):
        return widget(rowCount=0)

    def _connect(self, signal, slot):
        self.connected.append((signal, slot))

    def invalidate(self):
        self.stale = True


def fake_gui():
    gui = MagicMock()
    for cls in (
        "QPushButton",
        "QLabel",
        "QTableWidgetItem",
        "QListWidgetItem",
        "QGridLayout",
        "QHBoxLayout",
        "QFormLayout",
        "QPixmap",
        "QPainter",
        "QIcon",
        "QColor",
        "QBrush",
        "QPen",
        "QListWidget",
        "QStringListModel",
        "QCompleter",
    ):  # fresh object per call, so each button has its own signals
        getattr(gui, cls).side_effect = lambda *a, **k: widget()
    gui.QLineEdit.side_effect = lambda *a, **k: widget(text="")
    gui.QPlainTextEdit.side_effect = lambda *a, **k: widget(
        **{"toPlainText.return_value": ""}
    )
    gui.QComboBox.side_effect = lambda *a, **k: widget(currentIndex=0, currentText="")
    gui.QCheckBox.side_effect = lambda *a, **k: widget(
        **{"isChecked.return_value": False}
    )
    return gui


@pytest.fixture(autouse=True)
def env(world, monkeypatch, real_app):
    """Install fake fly.ap, fly.ap.scripting and fly.qt. Return the shown dialogs."""
    shown: list = []
    scripting = ModuleType("fly.ap.scripting")
    scripting.names_dialog_type = lambda: FakeBase
    scripting.names_selected_names = lambda: list(world.selected)
    scripting.select_glyphs = lambda names, *, package_id, add=False: world.log.append(
        ("select", tuple(names), package_id)
    )

    def show(dialog_type, key):
        dialog = dialog_type(None)
        shown.append((dialog, key))
        return dialog

    scripting.show_script_dialog = show

    def require_font_window(package_id: int) -> None:
        if world.glyph_window:
            raise ValueError("Activate the Font window before selecting glyphs.")

    scripting._require_selection_window = require_font_window
    capture = ModuleType("fly.ap.duplicate_unicodes_capture")

    def require_no_editors(qt, deadline) -> None:
        if world.editors_open:
            raise ValueError("Close all Glyph editors first.")

    capture.require_no_editors = require_no_editors
    ap = ModuleType("fly.ap")
    ap.fontlab, ap.scripting = world.native, scripting
    ap.duplicate_unicodes_capture = capture
    qt = NS(QtCore=MagicMock(), QtGui=fake_gui())
    qt.QtCore.QDateTime.currentDateTimeUtc.return_value = STAMP
    fly = ModuleType("fly")
    fly.ap, fly.qt = ap, qt
    for name, module in {
        "fly": fly,
        "fly.ap": ap,
        "fly.ap.scripting": scripting,
        "fly.ap.duplicate_unicodes_capture": capture,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    loaded = real_app(
        qt=qt,
        fontlab=world.native,
        scripting={
            "names_dialog_type": scripting.names_dialog_type,
            "names_selected_names": scripting.names_selected_names,
            "select_glyphs": scripting.select_glyphs,
            "show_script_dialog": show,
            "_require_selection_window": require_font_window,
        },
        modules=["names_edit", "history", "edit_guards", "duplicate_unicodes_capture"],
    )
    # The editor scan walks native widgets; the fake world answers instead.
    loaded["duplicate_unicodes_capture"].require_no_editors = require_no_editors
    return shown


def slot_of(dialog, signal):
    return next(slot for sig, slot in dialog.connected if sig is signal)


def open_panel(mods, name, env):
    mods[name].main()
    return env[-1][0]


# ----------------------------------------------------------------- source rules
@pytest.mark.parametrize("name", SCRIPTS)
def test_script_when_parsed_then_follows_house_rules(name):
    path = NAMES / f"{name}.py"
    text = path.read_text()
    tree = ast.parse(text)
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "fgGlyph" not in attrs, "S3 must never read flGlyph.fgGlyph"
    assert "UpdateAll" not in attrs, "S3 must never call UpdateAll (fl#8537)"
    assert text.startswith(f"# this_file: Scripts/Names/{name}.py\n")
    assert "SPDX-License-Identifier: Apache-2.0" in text.splitlines()[1]
    assert "Apache-2.0" in ast.get_docstring(tree), "docstring must credit the licence"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, f"{node.name} needs a return annotation"
            if node.name not in {"__init__", "mutate"}:
                assert ast.get_docstring(node), f"{node.name} needs a docstring"


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_when_imported_then_needs_no_qt_fontlab_or_scripting(name, monkeypatch):
    """Import needs only the stdlib-only App helper fly.ap.names_edit."""
    for key in ("fly.ap.scripting", "fly.ap.duplicate_unicodes_capture", "fly.qt"):
        monkeypatch.delitem(sys.modules, key, raising=False)
    monkeypatch.delitem(sys.modules, "PythonQt")
    monkeypatch.delitem(sys.modules, "fontlab")
    module = load(name, monkeypatch)
    assert callable(module.main), "import must not need FontLab, Qt or the panel helpers"
    assert module.names_edit is app("names_edit")
    assert "PythonQt" not in sys.modules and "fontlab" not in sys.modules


# ----------------------------------------------------------------- shared helpers
def test_scan_when_no_font_then_value_error(world):
    world.has_font = False
    with pytest.raises(ValueError, match="Open a font first"):
        scan(world)


def test_scan_when_mapping_differs_then_value_error(world):
    world.records[0].name = "zzz"
    with pytest.raises(ValueError, match="inconsistent"):
        scan(world)


def test_refusal_when_auto_layer_or_auto_base_then_reason(world):
    refusal = app("names_edit").refusal
    facts = scan(world)
    assert refusal(facts, "a", "rename") == ""
    assert refusal(facts, "ecircumflex", "rename") == "has auto layers"
    assert refusal(facts, "e", "rename") == "base of auto ecircumflex"
    assert refusal(facts, "e", "unicode") == "base of auto ecircumflex"
    assert refusal(facts, "nope", "rename") == "not in font"
    world.glyphs["b"].layers = []
    assert refusal(scan(world), "b", "rename") == "has no layers"


def test_refusal_when_many_users_then_names_two_and_ellipsis(world):
    for extra in ("x1", "x2", "x3"):
        world.add(extra, auto=True, bases=("a",))
    assert app("names_edit").refusal(scan(world), "a", "rename") == (
        "base of auto x1, x2…"
    )


def test_refusal_when_base_reaches_auto_glyph_through_composite_then_refused(world):
    """e -> manual ebar -> auto ebaracute: base detection follows the chain."""
    world.add("ebar").layers[0].shapes = [Shape("e")]
    world.add("ebaracute", auto=True, bases=("ebar",))
    refusal = app("names_edit").refusal
    facts = scan(world)
    assert refusal(facts, "ebar", "rename") == "base of auto ebaracute"
    assert refusal(facts, "e", "rename") == "base of auto ebaracute, ecircumflex"
    assert refusal(facts, "e", "metadata") == "", "metadata lets bases through"


def test_fresh_facts_when_font_switched_then_value_error(world):
    with pytest.raises(ValueError, match="no longer current"):
        app("names_edit").fresh_facts(99, native=world.native)


def test_fresh_facts_when_updates_pending_then_discloses(world):
    world.pending.append(1)
    assert not hasattr(app("names_edit").fresh_facts(7, native=world.native), "pending_updates")
    assert world.pending == [1]


def commit(world, title, entries, mutate):
    """Write through the real App names_edit.commit, as the scripts do."""
    return app("names_edit").commit(
        title,
        entries,
        mutate,
        operation="metadata",
        facts=scan(world),
        native=world.native,
        stamp=STAMP,
    )


def test_commit_when_mutation_fails_then_history_still_finalised(world):
    facts = scan(world)

    def boom() -> None:
        world.log.append(("set", "boom", "a", None))
        raise KeyError("x")

    with pytest.raises(app("history").PartialWriteError, match="use Edit > Undo"):
        commit(world, "T", [facts.entries["a"]], boom)
    assert world.log == history(["a"], "T", [("set", "boom", "a", None)])


def test_commit_when_second_entry_never_reached_then_it_is_still_notified(world):
    """One protocol: every declared glyph is stamped and notified after a failure."""
    facts = scan(world)
    entries = [facts.entries["a"], facts.entries["b"]]

    def boom() -> None:
        world.log.append(("set", "boom", "a", None))
        raise KeyError("x")

    with pytest.raises(RuntimeError, match="Edit > Undo"):
        commit(world, "T", entries, boom)
    assert world.log == history(["a", "b"], "T", [("set", "boom", "a", None)])


def test_commit_when_mutation_fails_at_once_then_history_closed_and_error_raised(
    world,
):
    facts = scan(world)

    def boom() -> None:
        raise KeyError("early")

    with pytest.raises(RuntimeError, match="early"):
        commit(world, "T", [facts.entries["a"]], boom)
    assert world.log == history(["a"], "T", [])


# ----------------------------------------------------------------- Glyph Tags
def test_edit_tags_when_remove_and_add_then_exact_order(mods):
    edit = mods["Glyph Tags"].edit_tags
    assert edit(["x", "y", "z"], ["n", "y"], ["x"]) == ["y", "z", "n"]
    assert edit([], ["a", "a"], []) == ["a"]
    assert edit(["q"], [], ["q"]) == []
    assert edit(["q"], ["q"], ["q"]) == ["q"]


def test_tag_counts_when_mixed_then_most_used_first(mods):
    counts = mods["Glyph Tags"].tag_counts([["b", "a"], ["a"], ["c", "a", "b"]])
    assert counts == [("a", 3), ("b", 2), ("c", 1)]


@pytest.mark.parametrize(
    ("tag", "ok"),
    [
        ("review", True),
        ("a b", False),
        ("a,b", False),
        ("", False),
        ("x" * 64, True),
        ("x" * 65, False),
    ],
)
def test_valid_tag_when_checked_then_expected(mods, tag, ok):
    assert mods["Glyph Tags"].valid_tag(tag) is ok


def test_apply_tags_when_add_then_one_undo_step_and_refusals_skipped(mods, world):
    m = mods["Glyph Tags"]
    world.glyphs["a"]._tags = ["old"]
    changed = m.apply_tags(
        world.native, world.qtcore, 7, ["a", "b", "e", "ecircumflex"], add=["done"]
    )
    assert changed == ["a", "b", "e"], "the auto glyph is refused, the base is not"
    assert world.log == history(
        ["a", "b", "e"],
        "Glyph Tags",
        [
            ("set", "tags", "a", ["old", "done"]),
            ("set", "tags", "b", ["done"]),
            ("set", "tags", "e", ["done"]),
        ],
    )


def test_apply_tags_when_remove_then_tags_dropped(mods, world):
    m = mods["Glyph Tags"]
    world.glyphs["a"]._tags = ["x", "y"]
    assert m.apply_tags(world.native, world.qtcore, 7, ["a", "b"], remove=["x"]) == [
        "a"
    ]
    assert world.glyphs["a"].tags == ["y"] and world.glyphs["b"].tags == []


def test_apply_tags_when_nothing_changes_then_no_history(mods, world):
    m = mods["Glyph Tags"]
    world.glyphs["a"]._tags = ["done"]
    assert m.apply_tags(world.native, world.qtcore, 7, ["a"], add=["done"]) == []
    assert (
        m.apply_tags(world.native, world.qtcore, 7, ["ecircumflex"], add=["done"]) == []
    )
    assert world.log == [], "no write, no history"


def test_apply_tags_when_refused_inputs_then_value_error_before_history(mods, world):
    m = mods["Glyph Tags"]
    with pytest.raises(ValueError, match="at least one glyph"):
        m.apply_tags(world.native, world.qtcore, 7, [], add=["x"])
    with pytest.raises(ValueError, match="Invalid tag"):
        m.apply_tags(world.native, world.qtcore, 7, ["a"], add=["a b"])
    with pytest.raises(ValueError, match="no longer current"):
        m.apply_tags(world.native, world.qtcore, 3, ["a"], add=["x"])
    world.has_font = False
    with pytest.raises(ValueError, match="Open a font first"):
        m.apply_tags(world.native, world.qtcore, 7, ["a"], add=["x"])
    assert world.log == []


def test_apply_tags_when_native_ignores_write_then_error_but_history_closed(
    mods, world
):
    m = mods["Glyph Tags"]
    world.glyphs["a"].sticky.add("tags")
    with pytest.raises(RuntimeError, match="differ from the plan|Edit > Undo"):
        m.apply_tags(world.native, world.qtcore, 7, ["a"], add=["x"])
    assert (
        world.log[-1] == ("stamp", "a")
        and ("notify", "Glyph Tags", (("layer", "a"), ("glyph", "a"))) in world.log
    )


def test_font_tags_when_tagged_then_sorted_union(mods, world):
    world.glyphs["a"]._tags = ["z", "m"]
    world.glyphs["e"]._tags = ["a"]
    m = mods["Glyph Tags"]
    assert m.font_tags(scan(world)) == ["a", "m", "z"]


def test_glyph_tags_panel_when_add_pressed_then_tag_written_and_reloaded(
    mods, world, env
):
    dialog = open_panel(mods, "Glyph Tags", env)
    assert dialog.targets == ["a", "b"] and env[-1][1] == "names_glyph_tags"
    dialog.tag.text = "review"
    slot_of(dialog, dialog.add_button.clicked)()
    assert world.glyphs["a"].tags == ["review"] and world.glyphs["b"].tags == ["review"]
    assert dialog.last_result["changed"] == ["a", "b"]
    dialog.status.setText.assert_called_with("Added 'review' on 2 glyphs")


def test_glyph_tags_panel_when_remove_pressed_then_ticked_removed(mods, world, env):
    world.glyphs["a"]._tags = ["x"]
    dialog = open_panel(mods, "Glyph Tags", env)
    dialog.ticked = lambda: ["x"]
    slot_of(dialog, dialog.remove_button.clicked)()
    assert world.glyphs["a"].tags == []
    assert dialog.last_result["removed"] == ["x"]


def test_glyph_tags_panel_when_selection_has_auto_then_refused_and_reported(
    mods, world, env
):
    world.selected = ["a", "ecircumflex"]
    dialog = open_panel(mods, "Glyph Tags", env)
    assert dialog.targets == ["a"] and dialog.refused == {
        "ecircumflex": "has auto layers"
    }
    assert (
        "1 refused (ecircumflex: has auto layers)"
        in dialog.status.setText.call_args[0][0]
    )


def test_glyph_tags_panel_when_font_switched_then_add_refuses(mods, world, env):
    dialog = open_panel(mods, "Glyph Tags", env)
    world.package.id = 8
    dialog.tag.text = "x"
    with pytest.raises(ValueError, match="no longer current"):
        slot_of(dialog, dialog.add_button.clicked)()
    assert world.edits() == []


def test_glyph_tags_panel_when_invalidated_then_edit_buttons_disabled(mods, world, env):
    dialog = open_panel(mods, "Glyph Tags", env)
    dialog.invalidate()
    dialog.add_button.setEnabled.assert_called_with(False)
    dialog.remove_button.setEnabled.assert_called_with(False)


# ----------------------------------------------------------------- Mark Color Palette
def test_mark_rgb_when_hue_grey_none_then_exact_values(mods):
    m = mods["Mark Color Palette"]
    assert m.mark_rgb(0) is None
    assert m.mark_rgb(1) == (232, 68, 68)
    assert m.mark_rgb(121) == (68, 232, 68)
    assert m.mark_rgb(1128) == (139, 139, 139)
    assert m.mark_rgb(361) == (75, 75, 75)
    assert m.mark_rgb(1200) == (175, 175, 175)
    assert m.mark_rgb(2000) == (255, 255, 255), "grey is capped at 255"


def test_hex_and_ink_when_rgb_then_exact_strings(mods):
    m = mods["Mark Color Palette"]
    assert m.hex_of((232, 68, 68)) == "#e84444"
    assert m.hex_of((200, 100, 10), 0.5) == "#643205"
    assert m.ink_for((232, 68, 68)) == "#111111"
    assert m.ink_for((75, 75, 75)) == "#ffffff"


@pytest.mark.parametrize(
    ("mark", "ok"),
    [
        (0, True),
        (1, True),
        (360, True),
        (361, False),
        (1000, False),
        (1001, True),
        (1255, True),
        (1256, False),
        (-1, False),
    ],
)
def test_valid_mark_when_checked_then_expected(mods, mark, ok):
    assert mods["Mark Color Palette"].valid_mark(mark) is ok


def test_mark_counts_when_marked_then_font_and_selection_counts(mods, world):
    world.glyphs["a"]._mark = 121
    world.glyphs["b"]._mark = 121
    m = mods["Mark Color Palette"]
    facts = scan(world)
    assert m.mark_counts(facts) == {121: 2, 0: 2}
    assert m.mark_counts(facts, ["a", "e"]) == {121: 1, 0: 1}


def test_apply_mark_when_set_then_one_undo_step_and_unchanged_untouched(mods, world):
    m = mods["Mark Color Palette"]
    world.glyphs["b"]._mark = 121
    changed = m.apply_mark(
        world.native, world.qtcore, 7, ["a", "b", "e", "ecircumflex"], 121
    )
    assert changed == ["a", "e"]
    assert world.log == history(
        ["a", "e"],
        "Mark Color Palette",
        [("set", "mark", "a", 121), ("set", "mark", "e", 121)],
    )


def test_apply_mark_when_bad_input_then_value_error_before_history(mods, world):
    m = mods["Mark Color Palette"]
    with pytest.raises(ValueError, match="at least one glyph"):
        m.apply_mark(world.native, world.qtcore, 7, [], 1)
    with pytest.raises(ValueError, match="outside"):
        m.apply_mark(world.native, world.qtcore, 7, ["a"], 500)
    with pytest.raises(ValueError, match="no longer current"):
        m.apply_mark(world.native, world.qtcore, 2, ["a"], 1)
    assert world.log == []


def test_apply_mark_when_native_ignores_write_then_runtime_error(mods, world):
    world.glyphs["a"].sticky.add("mark")
    with pytest.raises(RuntimeError):
        mods["Mark Color Palette"].apply_mark(world.native, world.qtcore, 7, ["a"], 31)
    assert (
        "notify",
        "Mark Color Palette",
        (("layer", "a"), ("glyph", "a")),
    ) in world.log


def test_swatch_style_when_none_or_colour_then_expected_rules(mods):
    m = mods["Mark Color Palette"]
    assert "1px dashed #777" in m.swatch_style(0, "#777")
    style = m.swatch_style(1, "#777")
    assert (
        "background: #e84444" in style
        and "color: #111111" in style
        and "QPushButton:pressed" in style
    )


def test_mark_panel_when_swatch_clicked_then_marks_written(mods, world, env):
    dialog = open_panel(mods, "Mark Color Palette", env)
    slot_of(dialog, dialog.swatches[121].clicked)()
    assert [world.glyphs[n].mark for n in ("a", "b")] == [121, 121]
    assert dialog.last_result == {"pending_note": "", "pending_updates": (), "mark": 121, "changed": ["a", "b"]}
    dialog.status.setText.assert_called_with("Green: changed 2 glyphs")


def test_mark_panel_when_font_switched_then_click_refuses(mods, world, env):
    dialog = open_panel(mods, "Mark Color Palette", env)
    world.package.id = 9
    with pytest.raises(ValueError, match="no longer current"):
        slot_of(dialog, dialog.swatches[1].clicked)()
    assert world.edits() == []


def test_mark_panel_when_no_font_then_swatches_disabled(mods, world, env):
    world.has_font = False
    dialog = open_panel(mods, "Mark Color Palette", env)
    assert dialog.facts is None and dialog.targets == []
    dialog.swatches[1].setEnabled.assert_called_with(False)


# ----------------------------------------------------------------- Suffix Tool
@pytest.mark.parametrize(
    ("name", "mode", "suffix", "replacement", "expected"),
    [
        ("a", "add", ".ss01", "", "a.ss01"),
        ("a", "add", "ss01", "", "a.ss01"),
        ("a.ss01", "add", ".ss01", "", "a.ss01"),
        ("a", "add", "", "", "a"),
        ("a.ss01", "remove", ".ss01", "", "a"),
        ("a.ss01", "remove", ".sc", "", "a.ss01"),
        ("a.b.ss01", "remove", "", "", "a.b"),
        ("a", "remove", ".ss01", "", "a"),
        (".notdef", "remove", "", "", ".notdef"),
        ("a.ss01", "replace", ".ss01", ".ss02", "a.ss02"),
        ("a.ss01", "replace", ".ss01", "ss02", "a.ss02"),
        ("a.ss01", "replace", ".sc", ".ss02", "a.ss01"),
        ("a.ss01", "replace", ".ss01", "", "a.ss01"),
    ],
)
def test_suffixed_when_operation_then_exact_name(
    mods, name, mode, suffix, replacement, expected
):
    assert mods["Suffix Tool"].suffixed(name, mode, suffix, replacement) == expected


def test_dotted_when_blank_or_bare_then_expected(mods):
    dotted = mods["Suffix Tool"].dotted
    assert (dotted(" sc "), dotted(".sc"), dotted("  ")) == (".sc", ".sc", "")


def test_plan_renames_when_conflicts_then_exact_statuses(mods, world):
    m = mods["Suffix Tool"]
    world.add("a.alt")
    world.add("c")
    world.add("d")
    facts = scan(world)
    pairs = [
        ("a", "a.alt"),
        ("b", "9b"),
        ("e", "e.alt"),
        ("ecircumflex", "ecircumflex.alt"),
        ("c", "x"),
        ("d", "x"),
        ("b", "b"),
    ]
    assert m.plan_renames(facts, pairs) == [
        ("a", "a.alt", "exists in font"),
        ("b", "9b", "invalid name"),
        ("e", "e.alt", "base of auto ecircumflex"),
        ("ecircumflex", "ecircumflex.alt", "has auto layers"),
        ("c", "x", "duplicate target"),
        ("d", "x", "duplicate target"),
    ]


def test_apply_suffix_when_add_then_one_undo_step_with_clear_unicode(mods, world):
    m = mods["Suffix Tool"]
    world.records[0]._codes = [97]
    renamed = m.apply_suffix(
        world.native,
        world.qtcore,
        7,
        ["a", "b", "e"],
        "add",
        ".ss01",
        clear_unicode=True,
    )
    assert renamed == [("a", "a.ss01"), ("b", "b.ss01")], (
        "e is the base of an auto composite"
    )
    assert world.log == [
        ("init", "layer", "a"),
        ("init", "layer", "b"),
        ("init", "glyph", "a"),
        ("init", "glyph", "b"),
        ("rename", "a", "a.ss01"),
        ("set", "unicodes", "a.ss01", []),
        ("rename", "b", "b.ss01"),
        ("set", "unicodes", "b.ss01", []),
        ("stamp", "a.ss01"),
        ("stamp", "b.ss01"),
        (
            "notify",
            "Suffix Tool",
            (("layer", "a"), ("layer", "b"), ("glyph", "a.ss01"), ("glyph", "b.ss01")),
        ),
        ("stamp", "a.ss01"),
        ("stamp", "b.ss01"),
    ]
    assert world.records[0].unicodes == []


def test_apply_suffix_when_remove_without_unicode_clear_then_codes_kept(mods, world):
    m = mods["Suffix Tool"]
    world.add("c.sc", codes=(99,))
    renamed = m.apply_suffix(
        world.native, world.qtcore, 7, ["c.sc"], "remove", ".sc", clear_unicode=False
    )
    assert renamed == [("c.sc", "c")]
    assert world.records[-1].unicodes == [99]
    assert not [e for e in world.log if e[:2] == ("set", "unicodes")]


def test_apply_suffix_when_rename_refused_by_native_then_error_and_history_closed(
    mods, world
):
    world.package.rename_ok = False
    with pytest.raises(RuntimeError, match="refused to rename"):
        mods["Suffix Tool"].apply_suffix(
            world.native, world.qtcore, 7, ["a"], "add", ".alt"
        )
    assert world.log[-1] == ("stamp", "a")


def test_apply_suffix_when_bad_input_then_value_error_before_history(mods, world, capsys):
    m = mods["Suffix Tool"]
    with pytest.raises(ValueError, match="at least one glyph"):
        m.apply_suffix(world.native, world.qtcore, 7, [], "add", ".alt")
    with pytest.raises(ValueError, match="no longer current"):
        m.apply_suffix(world.native, world.qtcore, 1, ["a"], "add", ".alt")
    world.pending.append(5)
    m.apply_suffix(world.native, world.qtcore, 7, ["a"], "add", ".alt")
    assert world.pending == [5] and world.log
    output = capsys.readouterr().out
    assert "(5,)" in output and "Queued glyph ids:" in output and "8537" in output and "modification dates" in output


def test_suffix_panel_when_apply_then_selected_glyphs_renamed(mods, world, env):
    dialog = open_panel(mods, "Suffix Tool", env)
    dialog.suffix.currentText = ".alt"
    dialog.replacement.currentText = ""
    dialog.mode.currentIndex = 0
    slot_of(dialog, dialog.apply_button.clicked)()
    assert sorted(world.glyphs) == ["a.alt", "b.alt", "e", "ecircumflex"]
    assert dialog.last_result["renamed"] == [("a", "a.alt"), ("b", "b.alt")]


def test_suffix_panel_when_preview_then_table_and_refusals(mods, world, env):
    world.selected = ["a", "e"]
    dialog = open_panel(mods, "Suffix Tool", env)
    dialog.suffix.currentText = ".alt"
    dialog.refresh()
    assert dialog.plan == [
        ("a", "a.alt", "ok"),
        ("e", "e.alt", "base of auto ecircumflex"),
    ]
    dialog.apply_button.setEnabled.assert_called_with(True)


# ----------------------------------------------------------------- Batch Rename
def test_replaced_when_plain_regex_or_empty_then_exact(mods):
    replaced = mods["Batch Rename"].replaced
    assert replaced("a.alt", ".alt", ".sc", False) == "a.sc"
    assert replaced("uni0041", r"^uni(\w+)$", r"u\1", True) == "u0041"
    assert replaced("abc", "", "x", False) == "abc"
    with pytest.raises(re.error):
        replaced("abc", "(", "x", True)


def test_plan_renames_when_rename_conflicts_then_exact_statuses(mods, world):
    m = mods["Batch Rename"]
    world.add("p")
    world.add("q")
    facts = scan(world)
    pairs = [
        ("a", "b"),
        ("p", "z"),
        ("q", "z"),
        ("e", "f"),
        ("ecircumflex", "g"),
        ("b", "bad name"),
        ("a", "a"),
    ]
    assert m.plan_renames(facts, pairs) == [
        ("a", "b", "exists in font"),
        ("p", "z", "duplicate target"),
        ("q", "z", "duplicate target"),
        ("e", "f", "base of auto ecircumflex"),
        ("ecircumflex", "g", "has auto layers"),
        ("b", "bad name", "invalid name"),
    ]


def test_plan_renames_when_two_glyphs_swap_names_then_both_refused(mods, world):
    m = mods["Batch Rename"]
    rows = m.plan_renames(scan(world), [("a", "b"), ("b", "a")])
    assert [r[2] for r in rows] == ["exists in font", "exists in font"]


def test_apply_renames_when_ok_then_record_used_and_one_undo_step(mods, world):
    m = mods["Batch Rename"]
    renamed = m.apply_renames(
        world.native, world.qtcore, 7, [("a", "aa"), ("e", "ee"), ("b", "bb")]
    )
    assert renamed == [("a", "aa"), ("b", "bb")]
    assert [e for e in world.log if e[0] == "rename"] == [
        ("rename", "a", "aa"),
        ("rename", "b", "bb"),
    ]
    kinds = [e[0] for e in world.log]
    assert kinds == ["init"] * 4 + [
        "rename",
        "rename",
        "stamp",
        "stamp",
        "notify",
        "stamp",
        "stamp",
    ]
    assert world.log[-3] == (
        "notify",
        "Batch Rename",
        (("layer", "a"), ("layer", "b"), ("glyph", "aa"), ("glyph", "bb")),
    )
    assert "e" in world.glyphs and "ecircumflex" in world.glyphs, "auto link untouched"


def test_apply_renames_when_nothing_passes_then_no_history(mods, world):
    assert (
        mods["Batch Rename"].apply_renames(
            world.native, world.qtcore, 7, [("e", "ee"), ("a", "b")]
        )
        == []
    )
    assert world.log == []


def test_apply_renames_when_font_switched_then_value_error(mods, world):
    with pytest.raises(ValueError, match="no longer current"):
        mods["Batch Rename"].apply_renames(world.native, world.qtcore, 4, [("a", "x")])


def test_apply_renames_when_stale_preview_name_gone_then_skipped(mods, world):
    assert (
        mods["Batch Rename"].apply_renames(
            world.native, world.qtcore, 7, [("gone", "x")]
        )
        == []
    )


def test_apply_renames_when_native_refuses_then_runtime_error(mods, world):
    world.package.rename_ok = False
    with pytest.raises(RuntimeError, match="refused to rename"):
        mods["Batch Rename"].apply_renames(world.native, world.qtcore, 7, [("a", "x")])


def test_rename_panel_when_find_replace_then_preview_and_apply(mods, world, env):
    dialog = open_panel(mods, "Batch Rename", env)
    dialog.find.text, dialog.replace.text = "a", "A"
    dialog.refresh()
    assert dialog.plan == [("a", "A", "ok")]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert "A" in world.glyphs and dialog.last_result["renamed"] == [("a", "A")]


def test_rename_panel_when_bad_pattern_then_error_status(mods, world, env):
    dialog = open_panel(mods, "Batch Rename", env)
    dialog.regex.isChecked.return_value = True
    dialog.find.text = "("
    dialog.refresh()
    assert dialog.plan == []
    assert dialog.status.setText.call_args[0][0].startswith("Pattern error")


def test_rename_panel_when_no_selection_then_all_scope_and_auto_refused(
    mods, world, env
):
    world.selected = []
    dialog = open_panel(mods, "Batch Rename", env)
    dialog.scope.setCurrentIndex.assert_called_with(1)
    dialog.scope.currentIndex = 1
    dialog.find.text, dialog.replace.text = "e", "E"
    dialog.refresh()
    assert dialog.plan == [
        ("e", "E", "base of auto ecircumflex"),
        ("ecircumflex", "EcircumflEx", "has auto layers"),
    ]
    dialog.apply_button.setEnabled.assert_called_with(False)


# ----------------------------------------------------------------- Batch Glyph Notes
def test_note_text_when_set_or_append_then_exact(mods):
    note = mods["Batch Glyph Notes"].note_text
    assert note("old", "new", False) == "new"
    assert note("old", "", False) == "", "empty Set clears the note"
    assert note("old", "new", True) == "old\nnew"
    assert note("", "new", True) == "new"
    assert note("old", "", True) == "old"


def test_plan_notes_when_mixed_then_exact_rows(mods, world):
    world.glyphs["a"]._note = "keep"
    world.glyphs["b"]._note = "other"
    m = mods["Batch Glyph Notes"]
    rows = m.plan_notes(
        scan(world), ["a", "b", "e", "ecircumflex"], "keep", False
    )
    assert rows == [
        ("a", "keep", "keep", "same"),
        ("b", "other", "keep", "change"),
        ("e", "", "keep", "change"),
        ("ecircumflex", "", "", "has auto layers"),
    ]


def test_apply_notes_when_set_then_layers_and_glyph_in_one_notify(mods, world):
    m = mods["Batch Glyph Notes"]
    changed = m.apply_notes(
        world.native, world.qtcore, 7, ["a", "b", "ecircumflex"], "todo", False
    )
    assert changed == ["a", "b"]
    assert world.log == history(
        ["a", "b"],
        "Batch Glyph Notes",
        [("set", "note", "a", "todo"), ("set", "note", "b", "todo")],
    )


def test_apply_notes_when_name_vanished_since_preview_then_not_in_font_row(mods, world):
    m = mods["Batch Glyph Notes"]
    assert m.plan_notes(scan(world), ["gone"], "x", False) == [
        ("gone", "", "", "not in font")
    ]
    assert m.apply_notes(world.native, world.qtcore, 7, ["gone"], "x", False) == []
    assert world.log == []


def test_apply_notes_when_append_then_newline_joined(mods, world):
    world.glyphs["a"]._note = "one"
    mods["Batch Glyph Notes"].apply_notes(
        world.native, world.qtcore, 7, ["a"], "two", True
    )
    assert world.glyphs["a"].note == "one\ntwo"


def test_apply_notes_when_bad_input_then_value_error_before_history(mods, world):
    m = mods["Batch Glyph Notes"]
    with pytest.raises(ValueError, match="at least one glyph"):
        m.apply_notes(world.native, world.qtcore, 7, [], "x", False)
    with pytest.raises(ValueError, match="no longer current"):
        m.apply_notes(world.native, world.qtcore, 3, ["a"], "x", False)
    assert m.apply_notes(world.native, world.qtcore, 7, ["a"], "", False) == []
    assert world.log == []


def test_apply_notes_when_native_ignores_write_then_runtime_error(mods, world):
    world.glyphs["a"].sticky.add("note")
    with pytest.raises(RuntimeError):
        mods["Batch Glyph Notes"].apply_notes(
            world.native, world.qtcore, 7, ["a"], "x", False
        )
    assert (
        "notify",
        "Batch Glyph Notes",
        (("layer", "a"), ("glyph", "a")),
    ) in world.log


def test_batch_notes_panel_when_apply_then_notes_written(mods, world, env):
    dialog = open_panel(mods, "Batch Glyph Notes", env)
    dialog.note_input.toPlainText.return_value = "check"
    dialog.refresh()
    assert [r[3] for r in dialog.plan] == ["change", "change"]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert [world.glyphs[n].note for n in ("a", "b")] == ["check", "check"]
    dialog.status.setText.assert_called_with("Updated notes on 2 glyphs")


def test_batch_notes_panel_when_font_switched_then_apply_refuses(mods, world, env):
    dialog = open_panel(mods, "Batch Glyph Notes", env)
    dialog.note_input.toPlainText.return_value = "check"
    world.package.id = 5
    with pytest.raises(ValueError, match="no longer current"):
        slot_of(dialog, dialog.apply_button.clicked)()
    assert world.edits() == []


# ----------------------------------------------------------------- Glyph Notes
def test_notes_in_font_when_blank_notes_then_only_real_notes_in_order(mods, world):
    world.glyphs["b"]._note = "second"
    world.glyphs["a"]._note = "first\nmore"
    world.glyphs["e"]._note = "   "
    m = mods["Glyph Notes"]
    assert m.notes_in_font(scan(world)) == [
        ("a", "first\nmore"),
        ("b", "second"),
    ]


def test_first_line_when_blank_leading_lines_then_first_text_line(mods):
    first = mods["Glyph Notes"].first_line
    assert (first("\n\n  hi  \nlater"), first(""), first("one")) == ("hi", "", "one")


def test_save_note_when_text_changes_then_one_undo_step(mods, world):
    assert (
        mods["Glyph Notes"].save_note(world.native, world.qtcore, 7, "a", "hello")
        is True
    )
    assert world.log == history(["a"], "Glyph Notes", [("set", "note", "a", "hello")])


def test_save_note_when_same_text_then_false_and_no_history(mods, world):
    world.glyphs["a"]._note = "same"
    assert (
        mods["Glyph Notes"].save_note(world.native, world.qtcore, 7, "a", "same")
        is False
    )
    assert world.log == []


def test_save_note_when_refused_or_unknown_then_value_error(mods, world):
    m = mods["Glyph Notes"]
    with pytest.raises(ValueError, match="Cannot edit ecircumflex: has auto layers"):
        m.save_note(world.native, world.qtcore, 7, "ecircumflex", "x")
    with pytest.raises(ValueError, match="not in the font"):
        m.save_note(world.native, world.qtcore, 7, "nope", "x")
    with pytest.raises(ValueError, match="no longer current"):
        m.save_note(world.native, world.qtcore, 6, "a", "x")
    assert world.log == []


def test_glyph_notes_panel_when_opened_then_first_selected_focused_and_list_built(
    mods, world, env
):
    world.glyphs["b"]._note = "remark"
    dialog = open_panel(mods, "Glyph Notes", env)
    assert dialog.glyph_name == "a" and dialog.entries == [("b", "remark")]
    dialog.editor_label.setText.assert_called_with("Note for a")


def test_glyph_notes_panel_when_save_then_note_written_and_focus_kept(mods, world, env):
    dialog = open_panel(mods, "Glyph Notes", env)
    dialog.load("b")
    dialog.editor.toPlainText.return_value = "kept"
    slot_of(dialog, dialog.apply_button.clicked)()
    assert world.glyphs["b"].note == "kept"
    assert dialog.glyph_name == "b", (
        "focus stays on the saved glyph, not the Font window selection"
    )
    assert dialog.last_result == {"pending_note": "", "pending_updates": (), "glyph": "b", "changed": True}


def test_glyph_notes_panel_when_double_click_then_selection_goes_through_app_helper(
    mods, world, env
):
    world.glyphs["b"]._note = "remark"
    dialog = open_panel(mods, "Glyph Notes", env)
    slot_of(dialog, dialog.list.cellDoubleClicked)(0)
    assert ("select", ("b",), 7) in world.log
    assert dialog.glyph_name == "b"


def test_glyph_notes_panel_when_refused_glyph_then_save_disabled(mods, world, env):
    world.selected = ["ecircumflex"]
    dialog = open_panel(mods, "Glyph Notes", env)
    dialog.apply_button.setEnabled.assert_called_with(False)
    assert "Cannot edit ecircumflex" in dialog.status.setText.call_args[0][0]


def test_glyph_notes_panel_when_no_glyph_then_save_refuses(mods, world, env):
    world.selected = []
    dialog = open_panel(mods, "Glyph Notes", env)
    assert dialog.glyph_name is None
    with pytest.raises(ValueError, match="Select a glyph first"):
        slot_of(dialog, dialog.apply_button.clicked)()


def test_glyph_notes_panel_when_font_switched_then_save_refuses(mods, world, env):
    dialog = open_panel(mods, "Glyph Notes", env)
    dialog.editor.toPlainText.return_value = "x"
    world.package.id = 11
    with pytest.raises(ValueError, match="no longer current"):
        slot_of(dialog, dialog.apply_button.clicked)()
    assert world.edits() == []


# ----------------------------------------------------------------- Unicode From Names
@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("uni0141", (0x141, "uni")),
        ("u1F600", (0x1F600, "u")),
        ("u110000", (None, "")),
        ("Lslash", (0x141, "AGL")),
        ("space", (0x20, "AGL")),
        ("Wacute", (0x1E82, "derived")),
        ("wcircumflex", (0x175, "AGL")),
        ("zdotbelow", (0x1E93, "derived")),
        ("a.ss01", (None, "")),
        ("f_i", (None, "")),
        ("xyzzy", (None, "")),
        ("1acute", (None, "")),
        (".notdef", (None, "")),
        ("acute", (0xB4, "AGL")),
    ],
)
def test_code_for_name_when_name_then_exact_code(mods, name, expected):
    assert mods["Unicode From Names"].code_for_name(name) == expected


def test_plan_unicodes_when_mixed_then_exact_rows(mods, world):
    world.add("uni0041", codes=())
    world.add("A", codes=(0x41,))
    world.add("uni0042")
    world.add("B")
    world.add("Lslash", codes=(0x142,))
    world.add("uni0043", codes=(0x43,))
    m = mods["Unicode From Names"]
    facts = scan(world)
    names = ["uni0041", "A", "uni0042", "B", "Lslash", "uni0043", "a", "e"]
    assert m.plan_unicodes(facts, names, False) == [
        ("uni0041", [], 0x41, "uni", "used by A"),
        ("A", [0x41], 0x41, "AGL", "same"),
        ("uni0042", [], 0x42, "uni", "assign"),
        ("B", [], 0x42, "AGL", "used by uni0042"),
        ("Lslash", [0x142], 0x141, "AGL", "encoded differently"),
        ("uni0043", [0x43], 0x43, "uni", "same"),
        ("a", [], 0x61, "AGL", "assign"),
        ("e", [], 0x65, "AGL", "base of auto ecircumflex"),
    ]
    assert m.plan_unicodes(facts, ["Lslash"], True)[0][4] == "assign"


def test_apply_unicodes_when_assign_then_one_undo_step_on_records(mods, world):
    world.add("uni0042")
    world.add("Lslash", codes=(0x142,))
    m = mods["Unicode From Names"]
    changed = m.apply_unicodes(
        world.native, world.qtcore, 7, ["uni0042", "a", "e", "Lslash"], False
    )
    assert changed == ["uni0042", "a"]
    assert world.log == history(
        ["uni0042", "a"],
        "Unicode from Names",
        [("set", "unicodes", "uni0042", [0x42]), ("set", "unicodes", "a", [0x61])],
    )
    assert next(r for r in world.records if r.name == "Lslash").unicodes == [0x142]


def test_apply_unicodes_when_overwrite_then_existing_code_replaced(mods, world):
    world.add("Lslash", codes=(0x142,))
    changed = mods["Unicode From Names"].apply_unicodes(
        world.native, world.qtcore, 7, ["Lslash"], True
    )
    assert changed == ["Lslash"]
    assert next(r for r in world.records if r.name == "Lslash").unicodes == [0x141]


def test_apply_unicodes_when_native_ignores_write_then_runtime_error_history_closed(
    mods, world
):
    world.records[0].sticky = True
    with pytest.raises(RuntimeError):
        mods["Unicode From Names"].apply_unicodes(
            world.native, world.qtcore, 7, ["a"], False
        )
    assert (
        "notify",
        "Unicode from Names",
        (("layer", "a"), ("glyph", "a")),
    ) in world.log


def test_apply_unicodes_when_bad_input_then_value_error_before_history(mods, world):
    m = mods["Unicode From Names"]
    with pytest.raises(ValueError, match="at least one glyph"):
        m.apply_unicodes(world.native, world.qtcore, 7, [], False)
    with pytest.raises(ValueError, match="no longer current"):
        m.apply_unicodes(world.native, world.qtcore, 2, ["a"], False)
    assert m.apply_unicodes(world.native, world.qtcore, 7, ["xyzzy_none"], False) == []
    assert world.log == []


def test_apply_unicodes_when_implying_name_vanished_then_not_in_font_row(mods, world):
    m = mods["Unicode From Names"]
    assert m.plan_unicodes(scan(world), ["uni0042"], False) == [
        ("uni0042", [], 0x42, "uni", "not in font")
    ]
    assert m.apply_unicodes(world.native, world.qtcore, 7, ["uni0042"], False) == []
    assert world.log == []


def test_hexes_when_codes_then_formatted(mods):
    hexes = mods["Unicode From Names"].hexes
    assert (hexes([0x41, 0x1F600]), hexes([])) == ("U+0041 U+1F600", "–")


def test_unicode_panel_when_assign_then_selected_glyphs_encoded(mods, world, env):
    dialog = open_panel(mods, "Unicode From Names", env)
    assert [r[4] for r in dialog.plan] == ["assign", "assign"]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert [r.unicodes for r in world.records[:2]] == [[0x61], [0x62]]
    dialog.status.setText.assert_called_with("Assigned 2 code points")


def test_unicode_panel_when_font_switched_then_assign_refuses(mods, world, env):
    dialog = open_panel(mods, "Unicode From Names", env)
    world.package.id = 21
    with pytest.raises(ValueError, match="no longer current"):
        slot_of(dialog, dialog.apply_button.clicked)()
    assert world.edits() == []


def test_unicode_panel_when_no_selection_then_all_glyphs_scope(mods, world, env):
    world.selected = []
    dialog = open_panel(mods, "Unicode From Names", env)
    dialog.scope.setCurrentIndex.assert_called_with(1)
    dialog.scope.currentIndex = 1
    dialog.refresh()
    assert [(r[0], r[4]) for r in dialog.plan] == [
        ("a", "assign"),
        ("b", "assign"),
        ("e", "base of auto ecircumflex"),
        ("ecircumflex", "has auto layers"),
    ]


# ----------------------------------------------------------------- menu wiring
@pytest.mark.parametrize(
    ("name", "key"),
    [
        ("Glyph Tags", "names_glyph_tags"),
        ("Mark Color Palette", "names_mark_color_palette"),
        ("Suffix Tool", "names_suffix_tool"),
        ("Batch Rename", "names_batch_rename"),
        ("Batch Glyph Notes", "utility_batch_glyph_notes"),
        ("Glyph Notes", "names_glyph_notes"),
        ("Unicode From Names", "names_unicode_from_names"),
    ],
)
def test_main_when_run_then_panel_built_lazily_under_rescued_key(
    mods, world, env, name, key
):
    assert env == [], "importing a script must not open a panel"
    dialog = open_panel(mods, name, env)
    assert env[-1][1] == key and isinstance(dialog, FakeBase)
    assert dialog.parent is None and dialog.title == mods[name].TITLE
    assert dialog.facts is not None and dialog.facts.package_id == 7


@pytest.mark.parametrize("name", SCRIPTS)
def test_panel_when_no_font_then_opens_with_diagnosis_and_no_edit(
    mods, world, env, name
):
    world.has_font = False
    dialog = open_panel(mods, name, env)
    assert dialog.facts is None
    assert world.edits() == []


@pytest.mark.parametrize(
    ("name", "operation"),
    [
        ("Glyph Tags", "metadata"),
        ("Mark Color Palette", "metadata"),
        ("Suffix Tool", "rename"),
        ("Batch Rename", "rename"),
        ("Batch Glyph Notes", "metadata"),
        ("Glyph Notes", "metadata"),
        ("Unicode From Names", "unicode"),
    ],
)
def test_script_when_loaded_then_uses_app_names_edit_and_keeps_no_copy(
    mods, name, operation
):
    module = mods[name]
    assert module.names_edit is app("names_edit"), name
    assert module.OPERATION == operation, name
    for moved in ("Entry", "Facts", "scan", "refusal", "editable", "fresh_facts", "commit"):
        assert moved not in vars(module), f"{name} still defines {moved}"


# ----------------------------------------------------------------- refusal policy
def test_refusal_when_metadata_then_base_allowed_but_auto_glyph_refused(world):
    names_edit = app("names_edit")
    facts = scan(world)
    assert names_edit.refusal(facts, "e", "metadata") == ""
    assert names_edit.refusal(facts, "ecircumflex", "metadata") == "has auto layers"
    assert names_edit.editable(facts, ["e", "ecircumflex"], "metadata") == (
        ["e"],
        {"ecircumflex": "has auto layers"},
    )
    assert names_edit.refusal(facts, "e", "rename") == "base of auto ecircumflex"


def test_plan_renames_when_base_reaches_auto_through_composite_then_refused(
    mods, world
):
    world.add("ebar").layers[0].shapes = [Shape("e")]
    world.add("ebaracute", auto=True, bases=("ebar",))
    rows = mods["Batch Rename"].plan_renames(scan(world), [("ebar", "ebar.alt")])
    assert rows == [("ebar", "ebar.alt", "base of auto ebaracute")]


@pytest.mark.parametrize(
    "write",
    [
        ("Glyph Tags", lambda m, w: m.apply_tags(w.native, w.qtcore, 7, ["e"], ["t"])),
        (
            "Mark Color Palette",
            lambda m, w: m.apply_mark(w.native, w.qtcore, 7, ["e"], 31),
        ),
        ("Glyph Notes", lambda m, w: m.save_note(w.native, w.qtcore, 7, "e", "n")),
        (
            "Batch Glyph Notes",
            lambda m, w: m.apply_notes(w.native, w.qtcore, 7, ["e"], "n", False),
        ),
    ],
    ids=lambda write: write[0],
)
def test_metadata_write_when_base_of_auto_composite_then_succeeds_without_auto_layer(
    mods, world, write
):
    name, do = write
    do(mods[name], world)
    assert world.edits(), "the base glyph was written"
    notifies = [e for e in world.log if e[0] == "notify"]
    assert notifies == [
        (notifies[0][0], notifies[0][1], (("layer", "e"), ("glyph", "e")))
    ]
    assert not any("ecircumflex" in str(e) for e in world.log), "no auto layer touched"


@pytest.mark.parametrize("flag", ["glyph_window", "editors_open"])
def test_apply_unicodes_when_glyph_window_or_editor_open_then_refused_before_history(
    mods, world, flag
):
    setattr(world, flag, True)
    with pytest.raises(ValueError):
        mods["Unicode From Names"].apply_unicodes(
            world.native, world.qtcore, 7, ["a"], False
        )
    assert world.log == []


@pytest.mark.parametrize("flag", ["glyph_window", "editors_open"])
def test_apply_suffix_when_clearing_unicode_and_editor_open_then_refused_before_history(
    mods, world, flag
):
    setattr(world, flag, True)
    with pytest.raises(ValueError):
        mods["Suffix Tool"].apply_suffix(
            world.native, world.qtcore, 7, ["a"], "add", ".alt", clear_unicode=True
        )
    assert world.log == []


def test_apply_suffix_when_not_clearing_unicode_then_open_editor_does_not_block(
    mods, world
):
    world.editors_open = True
    renamed = mods["Suffix Tool"].apply_suffix(
        world.native, world.qtcore, 7, ["a"], "add", ".alt"
    )
    assert renamed == [("a", "a.alt")]


@pytest.mark.parametrize("name", ["uniD800", "uniDFFF", "uD800", "u00DBFF"])
def test_code_for_name_when_surrogate_then_nothing(mods, name):
    assert mods["Unicode From Names"].code_for_name(name) == (None, "")


def test_code_for_name_when_just_outside_surrogates_then_code(mods):
    code = mods["Unicode From Names"].code_for_name
    assert code("uniD7FF") == (0xD7FF, "uni") and code("uniE000") == (0xE000, "uni")


@pytest.mark.parametrize("name", ["Batch Rename", "Suffix Tool"])
def test_plan_renames_when_notdef_or_space_then_reserved(mods, world, name):
    world.add(".notdef")
    world.add("space")
    m = mods[name]
    rows = m.plan_renames(scan(world), [(".notdef", "nd"), ("space", "sp")])
    assert rows == [
        (".notdef", "nd", "reserved glyph"),
        ("space", "sp", "reserved glyph"),
    ]


def test_apply_renames_when_notdef_then_nothing_written(mods, world):
    world.add(".notdef")
    m = mods["Batch Rename"]
    assert m.apply_renames(world.native, world.qtcore, 7, [(".notdef", "nd")]) == []
    assert world.log == []


def test_apply_suffix_when_notdef_then_nothing_written(mods, world):
    world.add(".notdef")
    assert (
        mods["Suffix Tool"].apply_suffix(
            world.native, world.qtcore, 7, [".notdef", "space"], "add", ".alt"
        )
        == []
    )
    assert world.log == []


def test_unicode_loss_when_rows_ok_then_codes_listed(mods, world):
    world.records[0]._codes = [97, 98]
    m = mods["Suffix Tool"]
    facts = scan(world)
    plan = m.plan_renames(facts, [("a", "a.alt"), ("e", "e.alt"), ("b", "b.alt")])
    assert m.unicode_loss(facts, plan) == {"a": [97, 98], "b": []}


def test_suffix_panel_when_opened_then_unicode_removal_is_off_by_default(
    mods, world, env
):
    dialog = open_panel(mods, "Suffix Tool", env)
    dialog.suffix.currentText = ".alt"
    slot_of(dialog, dialog.apply_button.clicked)()
    assert dialog.last_result["cleared_unicode"] is False


def test_suffix_panel_when_removal_ticked_then_codes_cleared(mods, world, env):
    world.records[0]._codes = [97]
    dialog = open_panel(mods, "Suffix Tool", env)
    dialog.suffix.currentText = ".alt"
    dialog.clear_unicode.isChecked.return_value = True
    slot_of(dialog, dialog.apply_button.clicked)()
    assert dialog.last_result["cleared_unicode"] is True
    assert world.records[0].unicodes == []


@pytest.mark.parametrize(
    ("name", "attr", "method", "args"),
    [
        ("Glyph Tags", "table", "setRowCount", (0,)),
        ("Suffix Tool", "table", "setRowCount", (0,)),
        ("Batch Rename", "table", "setRowCount", (0,)),
        ("Batch Glyph Notes", "table", "setRowCount", (0,)),
        ("Unicode From Names", "table", "setRowCount", (0,)),
        ("Glyph Notes", "list", "setRowCount", (0,)),
        ("Mark Color Palette", "list", "clear", ()),
    ],
)
def test_panel_when_reload_fails_then_result_table_is_cleared(
    mods, world, env, name, attr, method, args
):
    dialog = open_panel(mods, name, env)
    world.has_font = False
    slot_of(dialog, dialog.reload_button.clicked)()
    getattr(getattr(dialog, attr), method).assert_called_with(*args)
    assert dialog.facts is None


def test_panel_when_reload_raises_unexpectedly_then_glyph_notes_list_invalidated(
    mods, world, env
):
    world.glyphs["b"]._note = "remark"
    dialog = open_panel(mods, "Glyph Notes", env)
    assert dialog.entries
    dialog.invalidate()
    assert dialog.entries == []
    dialog.list.setRowCount.assert_called_with(0)


def test_glyph_notes_panel_when_unsaved_edit_then_reload_keeps_it(mods, world, env):
    dialog = open_panel(mods, "Glyph Notes", env)
    dialog.editor.toPlainText.return_value = "draft"
    dialog.editor.setPlainText.reset_mock()
    slot_of(dialog, dialog.reload_button.clicked)()
    dialog.editor.setPlainText.assert_not_called()
    assert "Unsaved" in dialog.status.setText.call_args[0][0]


def test_glyph_notes_panel_when_unsaved_edit_then_row_click_keeps_it(mods, world, env):
    world.glyphs["b"]._note = "remark"
    dialog = open_panel(mods, "Glyph Notes", env)
    dialog.editor.toPlainText.return_value = "draft"
    dialog.editor.setPlainText.reset_mock()
    slot_of(dialog, dialog.list.cellClicked)(0)
    dialog.editor.setPlainText.assert_not_called()
    assert dialog.glyph_name == "a"


def test_unicode_panel_when_opened_then_overwrite_text_warns_codes_are_dropped(
    mods, world, env
):
    open_panel(mods, "Unicode From Names", env)
    texts = [
        str(c.args[0]) for c in sys.modules["fly"].qt.QtGui.QCheckBox.call_args_list
    ]
    assert any("dropped" in t for t in texts), texts


def test_batch_notes_panel_when_one_glyph_then_singular_wording(mods, world, env):
    world.selected = ["a"]
    dialog = open_panel(mods, "Batch Glyph Notes", env)
    dialog.note_input.toPlainText.return_value = "x"
    dialog.refresh()
    dialog.status.setText.assert_called_with("1 of 1 glyph note changes")
    slot_of(dialog, dialog.apply_button.clicked)()
    dialog.status.setText.assert_called_with("Updated the note on 1 glyph")


def test_batch_notes_panel_when_two_glyphs_then_plural_wording(mods, world, env):
    dialog = open_panel(mods, "Batch Glyph Notes", env)
    dialog.note_input.toPlainText.return_value = "x"
    slot_of(dialog, dialog.apply_button.clicked)()
    dialog.status.setText.assert_called_with("Updated notes on 2 glyphs")


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_text_when_read_then_no_internal_jargon_and_no_overclaims(name):
    text = (NAMES / f"{name}.py").read_text()
    for banned in ("issue 122", "issue-122", "D22", "reviewed App", "batch fragment"):
        assert banned.lower() not in text.lower(), banned
    assert not re.search(r"\bS[0-9]\b", text), "no batch ids in public text"
    assert "Components follow" not in text and "and the components that use" not in text


def test_real_fontlabapp_when_imported_then_every_name_the_scripts_use_exists():
    """No fakes: the real Fly aliases give every App name that the scripts use."""
    used = app_names_used([NAMES / f"{name}.py" for name in SCRIPTS])
    assert {"fly.ap.names_edit", "fly.ap.edit_guards", "fly.ap.scripting"} <= set(used)
    assert {"scan", "fresh_facts", "editable", "refusal", "commit", "Facts"} <= used[
        "fly.ap.names_edit"
    ]
    check_real_app_names(used)


def test_real_names_dialog_when_parsed_then_has_the_hooks_the_panels_use():
    from importlib.metadata import distribution

    package = Path(distribution("fontlab-fontlabapp").locate_file("fontlabapp"))
    tree = ast.parse((package / "_names_dialog.py").read_text())
    cls = next(
        c for c in tree.body if isinstance(c, ast.ClassDef) and c.name == "NamesDialog"
    )
    have = {f.name for f in cls.body if isinstance(f, ast.FunctionDef)}
    assert {"__init__", "make_table", "_connect", "invalidate"} <= have, have


def test_suffix_panel_when_apply_then_selected_glyphs_renamed_with_queued_id_discloses_once(mods, world, env):
    dialog = open_panel(mods, "Suffix Tool", env)
    dialog.suffix.currentText = ".alt"
    dialog.replacement.currentText = ""
    dialog.mode.currentIndex = 0
    world.pending = [17]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert sorted(world.glyphs) == ["a.alt", "b.alt", "e", "ecircumflex"]
    assert dialog.last_result["renamed"] == [("a", "a.alt"), ("b", "b.alt")]
    assert dialog.last_result["pending_updates"] == (17,) and world.pending == [17]
    note = dialog.last_result["pending_note"]
    shown = dialog.status.setText.call_args[0][0]
    assert "8537" in note and note in shown and shown.count("8537") == 1
    assert world.edits(), "A queued id must allow the actual native write"


def test_rename_panel_when_find_replace_then_preview_and_apply_with_queued_id_discloses_once(mods, world, env):
    dialog = open_panel(mods, "Batch Rename", env)
    dialog.find.text, dialog.replace.text = "a", "A"
    dialog.refresh()
    assert dialog.plan == [("a", "A", "ok")]
    world.pending = [17]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert "A" in world.glyphs and dialog.last_result["renamed"] == [("a", "A")]
    assert dialog.last_result["pending_updates"] == (17,) and world.pending == [17]
    note = dialog.last_result["pending_note"]
    shown = dialog.status.setText.call_args[0][0]
    assert "8537" in note and note in shown and shown.count("8537") == 1
    assert world.edits(), "A queued id must allow the actual native write"


def test_glyph_tags_panel_when_add_pressed_then_tag_written_and_reloaded_with_queued_id_discloses_once(
    mods, world, env
):
    dialog = open_panel(mods, "Glyph Tags", env)
    assert dialog.targets == ["a", "b"] and env[-1][1] == "names_glyph_tags"
    dialog.tag.text = "review"
    world.pending = [17]
    slot_of(dialog, dialog.add_button.clicked)()
    assert world.glyphs["a"].tags == ["review"] and world.glyphs["b"].tags == ["review"]
    assert dialog.last_result["changed"] == ["a", "b"]
    assert dialog.last_result["pending_updates"] == (17,) and world.pending == [17]
    note = dialog.last_result["pending_note"]
    shown = dialog.status.setText.call_args[0][0]
    assert "8537" in note and note in shown and shown.count("8537") == 1
    assert world.edits(), "A queued id must allow the actual native write"


def test_batch_notes_panel_when_apply_then_notes_written_with_queued_id_discloses_once(mods, world, env):
    dialog = open_panel(mods, "Batch Glyph Notes", env)
    dialog.note_input.toPlainText.return_value = "check"
    dialog.refresh()
    assert [r[3] for r in dialog.plan] == ["change", "change"]
    world.pending = [17]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert [world.glyphs[n].note for n in ("a", "b")] == ["check", "check"]
    assert dialog.last_result["pending_updates"] == (17,) and world.pending == [17]
    note = dialog.last_result["pending_note"]
    shown = dialog.status.setText.call_args[0][0]
    assert "8537" in note and note in shown and shown.count("8537") == 1
    assert world.edits(), "A queued id must allow the actual native write"


def test_unicode_panel_when_assign_then_selected_glyphs_encoded_with_queued_id_discloses_once(mods, world, env):
    dialog = open_panel(mods, "Unicode From Names", env)
    assert [r[4] for r in dialog.plan] == ["assign", "assign"]
    world.pending = [17]
    slot_of(dialog, dialog.apply_button.clicked)()
    assert [r.unicodes for r in world.records[:2]] == [[0x61], [0x62]]
    assert dialog.last_result["pending_updates"] == (17,) and world.pending == [17]
    note = dialog.last_result["pending_note"]
    shown = dialog.status.setText.call_args[0][0]
    assert "8537" in note and note in shown and shown.count("8537") == 1
    assert world.edits(), "A queued id must allow the actual native write"
