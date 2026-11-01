# this_file: tests/test_names_editors.py
"""Exercise complete Names editing menus using owned host doubles only."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TITLES = [
    "Batch Rename",
    "Duplicate Unicodes",
    "Glyph Notes",
    "Glyph Tags",
    "Mark Color Palette",
    "Suffix Tool",
    "Unicode From Names",
]


@pytest.mark.parametrize("title", TITLES)
def test_requested_names_editor_exists(title):
    assert (ROOT / "Scripts/Names" / (title + ".py")).is_file(), (
        "Complete Names editor missing"
    )


import importlib.util
import sys
from types import SimpleNamespace as NS
from typing import ClassVar


class Signal:
    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)

    def disconnect(self, slot):
        self.slots.remove(slot)

    def emit(self, *args):
        for slot in list(self.slots):
            slot(*args)


class Color:
    HexArgb = 1

    def __init__(self, *args):
        pass

    def __getattr__(self, name):
        return lambda *args: None

    def name(self, *args):
        return "#202020"

    def darker(self, amount):
        return self

    def lightness(self):
        return 150

    @staticmethod
    def fromHsl(*args):
        return Color()


class Widget:
    """Owned controls execute real constructors and original signal actions."""

    instances: ClassVar[list] = []

    def __init__(self, *args):
        self.instances.append(self)
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.items, self.cells, self.children = [], {}, []
        self.enabled, self.blocked, self.checked, self.deleted = (
            True,
            False,
            False,
            False,
        )
        self.currentIndex, self.rowCount, self.width, self.height = 0, 0, 600, 400
        self.font = NS(
            pointSizeF=lambda: 12, setPointSizeF=lambda x: None, setBold=lambda b: None
        )
        self.palette = NS(color=lambda role: Color(), setColor=lambda *args: None)
        self._flags, self.state = 1, 0
        for name in (
            "clicked",
            "textChanged",
            "editTextChanged",
            "returnPressed",
            "toggled",
            "currentIndexChanged",
            "itemChanged",
            "cellClicked",
            "cellDoubleClicked",
        ):
            setattr(self, name, Signal())

    def __getattr__(self, name):
        if name.startswith("set") or name in (
            "addWidget",
            "addLayout",
            "addStretch",
            "show",
            "raise_",
            "fill",
            "drawEllipse",
            "end",
            "verticalHeader",
            "horizontalHeader",
            "header",
        ):
            return lambda *args: self
        raise AttributeError(name)

    def setText(self, *args):
        self.text = args[-1]
        if not self.blocked:
            self.textChanged.emit()

    def setPlainText(self, text):
        self.setText(text)

    def toPlainText(self):
        return self.text

    def setEditText(self, text):
        self.text = text
        if not self.blocked:
            self.editTextChanged.emit()

    def isChecked(self):
        return self.checked

    def setChecked(self, value):
        self.checked = value
        if not self.blocked:
            self.toggled.emit()

    def setEnabled(self, value):
        self.enabled = value

    def setCurrentIndex(self, value):
        self.currentIndex = value
        if not self.blocked:
            self.currentIndexChanged.emit()

    @property
    def currentText(self):
        return self.text or (self.items[self.currentIndex] if self.items else "")

    @property
    def count(self):
        return len(self.items)

    def addItem(self, item):
        self.items.append(item)

    def setItemText(self, index, text):
        self.items[index] = text

    def setStringList(self, values):
        self.items = list(values)

    def stringList(self):
        return self.items

    def blockSignals(self, value):
        old, self.blocked = self.blocked, value
        return old

    def clear(self):
        self.items, self.cells, self.children, self.text, self.rowCount = (
            [],
            {},
            [],
            "",
            0,
        )

    def setRowCount(self, value):
        self.rowCount = value
        self.cells = {key: item for key, item in self.cells.items() if key[0] < value}

    def setItem(self, row, column, item):
        self.cells[row, column] = item
        item.owner = self

    def item(self, row, column):
        return self.cells[row, column]

    def addTopLevelItem(self, item):
        self.items.append(item)

    def addChild(self, item):
        self.children.append(item)

    def flags(self):
        return self._flags

    def setFlags(self, value):
        self._flags = value

    def checkState(self, *args):
        return self.state

    def setCheckState(self, *args):
        self.state = args[-1]
        owner = getattr(self, "owner", None)
        if owner is not None and not owner.blocked:
            owner.itemChanged.emit(self)

    def heightForWidth(self, width):
        return 30

    def resize(self, width, height):
        self.width, self.height = width, height

    def close(self):
        self.closeEvent(None)

    def closeEvent(self, event):
        pass

    def deleteLater(self):
        self.deleted = True


class TreeItem(Widget):
    def font(self, column):
        return NS(setBold=lambda value: None)

    def __init__(self, *args):
        super().__init__(*args)
        del self.font


class Painter(Widget):
    Antialiasing = 1


class Glyph:
    def __init__(self, name, codes=()):
        self.name, self.unicodes, self.note, self.tags, self.mark = (
            name,
            list(codes),
            "",
            [],
            0,
        )
        self.id, self.isNull, self.fgGlyph = id(self), False, self
        self.layers = [
            NS(
                id=id(self) + 1,
                autoLayer=False,
                isMasterLayer=True,
                shapes=[],
                note="",
                mark=0,
            )
        ]


@pytest.fixture
def load(monkeypatch, app_sources):
    monkeypatch.setattr(Widget, "instances", [])
    state = NS(
        package=None,
        glyphs=[Glyph("A", [65]), Glyph("B", [66]), Glyph("Wacute")],
        selected={0, 1},
        history=[],
        updates=0,
    )
    package = NS(id=7, isNull=False, masters=["Regular", "Bold"], master="Regular")
    package.findName = lambda name: next(
        (g for g in state.glyphs if g.name == name), None
    )
    package.checkInitHistoryState = lambda n: state.history.append(("init", n))

    def rename(glyph, name, replace):
        glyph.name = name
        return True

    package.renameGlyph = rename
    state.groups = {master: {"Left": (["A"], "KernLeft")} for master in package.masters}
    package.kerning = lambda master: NS(groups=state.groups[master])
    state.package = package

    def update():
        state.updates += 1

    native = NS(
        CurrentFont=lambda: NS(glyphs=state.glyphs),
        CurrentGlyph=lambda: None,
        MainWindow=lambda: None,
        UpdateAll=update,
        flWorkspace=NS(instance=lambda: NS(currentPackage=state.package)),
        flItems=lambda: NS(
            notifyChangesApplied=lambda title, objects: state.history.append(
                (title, tuple(objects))
            )
        ),
    )

    class Font:
        def __len__(self):
            return len(state.glyphs)

        def __getitem__(self, i):
            return state.glyphs[i]

    fl = NS(
        font=Font(),
        Selected=lambda i: i in state.selected,
        Unselect=lambda: state.selected.clear(),
        Select=state.selected.add,
    )
    gui = NS(
        **{
            name: Widget
            for name in (
                "QDialog",
                "QWidget",
                "QVBoxLayout",
                "QHBoxLayout",
                "QGridLayout",
                "QLabel",
                "QLineEdit",
                "QComboBox",
                "QCheckBox",
                "QPushButton",
                "QPlainTextEdit",
                "QTableWidget",
                "QTableWidgetItem",
                "QTreeWidget",
                "QListWidget",
                "QListWidgetItem",
                "QCompleter",
                "QStringListModel",
                "QPixmap",
                "QIcon",
            )
        }
    )
    gui.QTreeWidgetItem, gui.QColor, gui.QPainter = TreeItem, Color, Painter
    gui.QBrush = gui.QPen = lambda *args: args
    gui.QPalette = NS(Text=1, WindowText=2, Link=3, Mid=4, ButtonText=5)
    gui.QHeaderView = NS(Stretch=1, ResizeToContents=2)
    gui.QAbstractItemView = NS(
        NoEditTriggers=0, NoSelection=0, SelectRows=1, SingleSelection=2
    )
    gui.QListView = NS(IconMode=1, LeftToRight=2, Adjust=3)
    core = NS(
        Qt=NS(
            ScrollBarAlwaysOff=0,
            Checked=2,
            Unchecked=0,
            ItemIsEnabled=1,
            ItemIsUserCheckable=2,
            AlignRight=4,
            AlignVCenter=8,
            CaseInsensitive=0,
            NoPen=0,
            transparent=0,
        ),
        QSize=lambda *args: args,
    )
    qt = NS(QtCore=core, QtGui=gui)
    modules = {"fontlab": native, "PythonQt": qt, "FL": NS(fl=fl)}
    monkeypatch.setitem(sys.modules, "fontlabapp", NS(_native=modules.__getitem__))
    for name, value in modules.items():
        monkeypatch.setitem(sys.modules, name, value)
    for name in (
        "scripting",
        "names_edit",
        "names_unicode",
        "names_batch",
        "names_editor",
        "_names_dialog",
        "_names_edit_dialog",
    ):
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + name, app_sources / (name + ".py")
        )
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + name, module)
        spec.loader.exec_module(module)
    scripting = sys.modules["fontlabapp.scripting"]
    monkeypatch.setitem(sys.modules, "fly", NS(ap=NS(scripting=scripting)))
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", scripting)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Names" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    return module, state, native, scripting


CLASSES = dict(
    zip(
        TITLES,
        [
            "Renamer",
            "DuplicateUnicodes",
            "GlyphNotes",
            "GlyphTags",
            "Palette",
            "SuffixTool",
            "UnicodeFromNames",
        ],
        strict=True,
    )
)


@pytest.mark.parametrize("title", TITLES)
def test_actual_constructor_has_complete_controls_and_owned_close(
    load, monkeypatch, title
):
    module, state, _native, _ = load
    tool = module(title)
    dialog = tool.main()
    assert dialog._snapshot_valid, getattr(dialog, "slot_error", "")
    assert dialog.close_button.text == "Close"
    assert dialog._connections and sys._fontlab_samples[tool.KEY] is dialog
    dialog.close_button.clicked.emit()
    assert (
        dialog.deleted
        and not dialog._connections
        and tool.KEY not in sys._fontlab_samples
    )
    assert state.history == []


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "phase", ["package", "id", "selection", "names", "masters", "references"]
)
def test_actual_opening_read_failures_leave_empty_diagnosed_closable_panel(
    load, monkeypatch, title, phase
):
    module, state, native, _scripting = load
    tool = module(title)
    original_package = state.package

    def fail(*args):
        assert any(w.text == "Close" for w in Widget.instances), (
            "Close must precede native reads"
        )
        assert sum(w.text == "" for w in Widget.instances) >= 1, (
            "Empty status must already exist"
        )
        raise RuntimeError("early " + phase)

    if phase == "package":
        native.flWorkspace.instance = fail
    elif phase == "id":

        class Broken:
            isNull = False

            @property
            def id(self):
                return fail()

        state.package = Broken()
    elif phase == "selection":
        sys.modules["FL"].fl.Selected = fail
    elif phase == "names":
        native.CurrentFont = fail
    elif phase == "masters":

        class Broken:
            def __getattr__(self, key):
                if key == "masters":
                    return fail()
                return getattr(original_package, key)

        state.package = Broken()
    else:
        original_package.findName = fail
    dialog = tool.main()
    assert not dialog._snapshot_valid and "early " + phase in dialog.status.text, (
        dialog.status.text
    )
    assert dialog.rows == [] and dialog.entries == [] and dialog.groups == []
    assert not getattr(dialog, "apply_button", NS(enabled=False)).enabled
    dialog.close_button.clicked.emit()
    assert dialog.deleted and tool.KEY not in sys._fontlab_samples
    assert state.history == []


@pytest.mark.parametrize("title", TITLES)
def test_known_opening_binding_cannot_automatically_adopt_switched_font(load, title):
    module, state, native, _ = load
    tool = module(title)
    original = native.CurrentFont

    def fail():
        raise RuntimeError("opening scan failed")

    native.CurrentFont = fail
    dialog = tool.main()
    native.CurrentFont = original
    state.package = NS(id=8, isNull=False)
    refresh = getattr(dialog, "refresh", getattr(dialog, "reload_list", None))
    if refresh is None:
        dialog.tree.itemChanged.emit()
    else:
        refresh()
    assert not dialog._snapshot_valid and dialog._bound_id == 7
    assert (
        "original font" in dialog.status.text.lower()
        or "font changed" in dialog.status.text.lower()
    )
    dialog.close()


def test_exact_rename_plan_plain_regex_invalid_collision_duplicates_and_auto(load):
    module, *_ = load
    tool = module("Batch Rename")
    links = ({"aacute"}, {"a": ["aacute", "abreve", "amacron"]})
    assert tool.plan(
        ["a", "aacute", "quoteleft"],
        ["a", "aacute", "quoteleft"],
        "a",
        "x",
        False,
        links,
    ) == [
        ("a", "x", "base of auto aacute, abreve…"),
        ("aacute", "xxcute", "has auto layers"),
    ]
    assert tool.plan(["A", "B"], ["A", "B"], ".*", "X", True) == [
        ("A", "XX", "duplicate target"),
        ("B", "XX", "duplicate target"),
    ]
    assert tool.plan(["A"], ["A", "a"], "A", "a", False)[0][2] == "exists in font"
    assert tool.plan(["A"], ["A"], "A", "a", False) == [("A", "a", "ok")]
    assert tool.plan(["A"], ["A"], "A", "1bad", False)[0][2] == "invalid name"
    assert tool.plan(["quoteleft"], ["quoteleft"], r"^quote(left)$", r"qt\1", True) == [
        ("quoteleft", "qtleft", "ok")
    ]
    with pytest.raises(Exception, match="unterminated"):
        tool.plan(["A"], ["A"], "[", "x", True)


def test_suffix_modes_numberednames_dotleading_and_exact_defaults(load):
    module, *_ = load
    tool = module("Suffix Tool")
    assert tool.suffixed("braceleft.001", "add", "sc") == "braceleft.001.sc"
    assert tool.suffixed("braceleft.001", "remove", "") == "braceleft"
    assert tool.suffixed(".notdef", "remove", "") == ".notdef"
    assert tool.suffixed("a.alt", "replace", ".alt", "ss01") == "a.ss01"
    assert tool.suffixed("a.alt", "remove", ".ss01") == "a.alt"
    dialog = tool.main()
    assert dialog.clear_unicode.isChecked() and dialog.mode.currentIndex == 0
    assert (
        dialog.suffix.currentText == ".ss01"
        and dialog.replacement.currentText == ".ss01"
    )
    assert tool.PRESETS == [
        ".ss01",
        ".ss02",
        ".sc",
        ".alt",
        ".case",
        ".sups",
        ".lf",
        ".osf",
        ".tf",
        ".001",
    ]
    dialog.close()


@pytest.mark.parametrize(
    "name,expected",
    [
        ("uni0141", (0x141, "uni")),
        ("u1F600", (0x1F600, "u")),
        ("Wacute", (0x1E82, "derived")),
        ("nbspace", (0xA0, "AGL")),
        ("fi", (0xFB01, "AGL")),
        ("u110000", (None, "")),
        ("uni00410042", (None, "")),
        ("f_i", (None, "")),
        ("A.alt", (None, "")),
        ("unknown", (None, "")),
    ],
)
def test_unicode_exact_aliases_derivation_multicodepoint_unknowns(load, name, expected):
    assert load[0]("Unicode From Names").code_for_name(name) == expected


def test_unicode_plans_conflicts_overwrite_same_and_primary_keeper(load):
    tool = load[0]("Unicode From Names")
    values = {"A": [65, 66], "B": [], "Wacute": [99], "fi": [0xFB01]}
    rows = tool.plan(list(values), values, False)
    assert [r[-1] for r in rows] == ["same", "used by A", "encoded differently", "same"]
    assert tool.plan(["Wacute"], values, True)[0][-1] == "assign"
    dup = load[0]("Duplicate Unicodes")
    assert dup.duplicates([("alias", [66, 65]), ("A", [65]), ("other", [65])]) == [
        (65, "A", ["alias", "A", "other"])
    ]
    assert dup.duplicates([]) == [] and dup.printable(32) == ""


def test_actual_rename_callbacks_and_suffix_clear_have_real_editing_behavior(load):
    module, state, _, _ = load
    dialog = module("Batch Rename").main()
    dialog.find.setText("A")
    dialog.replace.setText("AA")
    assert dialog.rows == [("A", "AA", "ok")]
    dialog.apply_button.clicked.emit()
    assert state.glyphs[0].name == "AA" and dialog.last_result["renamed"] == [
        ("A", "AA")
    ]
    assert state.glyphs[0].unicodes == [65]
    dialog.close()
    dialog = module("Suffix Tool").main()
    dialog.suffix.setEditText("sc")
    dialog.apply()
    assert [g.name for g in state.glyphs] == ["AA.sc", "B.sc", "Wacute"]
    assert [g.unicodes for g in state.glyphs] == [[], [], []]
    dialog.close()


def test_actual_duplicate_ticks_remove_only_chosen_aliases(load):
    module, state, *_ = load
    state.glyphs[1].unicodes = [66, 65]
    state.glyphs[2].unicodes = [0x1E82, 65]
    dialog = module("Duplicate Unicodes").main()
    assert dialog.groups == [(65, "A", ["A", "B", "Wacute"])]
    dialog.items["B", 65].setCheckState(0, 0)
    dialog.update_actions()
    assert dialog.removals() == [("Wacute", 65)]
    dialog.apply()
    assert state.glyphs[1].unicodes == [66, 65] and state.glyphs[2].unicodes == [0x1E82]
    assert dialog.last_result == {"changed": ["Wacute"]}
    dialog.close()


def test_actual_notes_seeded_undisplayed_note_load_select_and_empty_save(load):
    module, state, *_ = load
    dialog = module("Glyph Notes").main()
    state.glyphs[1].note = "Seeded note"
    dialog.editor.setPlainText("Line1\nLine2")
    assert dialog.apply_button.enabled
    dialog.apply()
    assert dialog.entries == [("A", "Line1\nLine2"), ("B", "Seeded note")]
    assert dialog.last_result == {"glyph": "A", "changed": True}
    dialog.load_row(1, select=True)
    assert dialog.glyph_name == "B" and dialog.editor.toPlainText() == "Seeded note"
    assert state.selected == {1}
    dialog.editor.setPlainText("")
    dialog.apply()
    assert state.glyphs[1].note == "" and dialog.entries == [("A", "Line1\nLine2")]
    dialog.close()


def test_actual_tag_completion_counts_add_remove_and_noop_history(load):
    module, state, *_ = load
    state.glyphs[0].tags = ["keep"]
    dialog = module("Glyph Tags").main()
    dialog.tag.setText("review")
    dialog.add_tag()
    dialog.tag.setText("spacing")
    dialog.add_tag()
    assert dialog.counts == [("review", 2), ("spacing", 2), ("keep", 1)]
    dialog.table.item(1, 0).setCheckState(2)
    assert dialog.ticked() == ["spacing"]
    dialog.remove_ticked()
    assert state.glyphs[0].tags == ["keep", "review"] and state.glyphs[1].tags == [
        "review"
    ]
    assert dialog.completer_model.stringList() == ["keep", "review"]
    history = len(state.history)
    dialog.tag.setText("review")
    dialog.add_tag()
    assert len(state.history) == history
    dialog.close()


def test_actual_palette_selected_counts_switch_reload_and_clear(load):
    module, state, *_ = load
    dialog = module("Mark Color Palette").main()
    dialog.swatches[1].clicked.emit()
    assert [g.mark for g in state.glyphs] == [1, 1, 0]
    assert dialog.swatches[1].text.endswith("2 · 2 sel")
    state.selected = {1}
    dialog.reload()
    dialog.apply(121)
    assert [g.mark for g in state.glyphs] == [1, 121, 0]
    dialog.apply(0)
    assert [g.mark for g in state.glyphs] == [1, 0, 0]
    dialog.close()


def test_actual_unicode_menu_uses_full_preview_and_overwrite_controls(load):
    module, state, *_ = load
    dialog = module("Unicode From Names").main()
    assert dialog.scope.currentIndex == 0 and not dialog.overwrite.isChecked()
    dialog.scope.setCurrentIndex(1)
    assert any(r[0] == "Wacute" and r[-1] == "assign" for r in dialog.rows)
    dialog.apply()
    assert state.glyphs[2].unicodes == [0x1E82] and dialog.last_result == {
        "changed": ["Wacute"]
    }
    assert not dialog.apply_button.enabled
    dialog.close()


def make_action(dialog, title):
    """Stage a real changing plan and return its public mutation method."""
    if title == "Batch Rename":
        dialog.find.setText("A")
        dialog.replace.setText("AA")
    elif title == "Glyph Notes":
        dialog.editor.setPlainText("new note")
    elif title == "Glyph Tags":
        dialog.tag.setText("review")
        return dialog.add_tag
    elif title == "Mark Color Palette":
        return lambda: dialog.apply(1)
    return dialog.apply


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "change",
    [
        "closed",
        "switched",
        "names",
        "values",
        "masters",
        "selection",
        "references",
        "classes",
    ],
)
def test_actual_apply_refuses_stale_full_source_before_writes(load, title, change):
    module, state, *_ = load
    if title == "Duplicate Unicodes":
        state.glyphs[1].unicodes.append(65)
    dialog = module(title).main()
    action = make_action(dialog, title)
    old = [
        (g.name, list(g.unicodes), g.note, list(g.tags), g.mark) for g in state.glyphs
    ]
    if change == "closed":
        state.package = None
    elif change == "switched":
        state.package = NS(id=8, isNull=False)
    elif change == "names":
        state.glyphs[2].name = "external"
    elif change == "masters":
        state.package.masters.reverse()
    elif change == "selection":
        state.selected.clear()
    elif change == "classes":
        state.groups["Regular"]["Left"] = (["B"], "KernLeft")
    elif change == "references":
        state.glyphs[1].layers[0].shapes.append(
            NS(isComponent=True, shapeData=NS(componentGlyph="A"))
        )
    elif title == "Glyph Notes":
        state.glyphs[0].note = "external"
    elif title == "Glyph Tags":
        state.glyphs[0].tags = ["external"]
    elif title == "Mark Color Palette":
        state.glyphs[0].mark = 121
    else:
        state.glyphs[0].unicodes.append(77)
    external = [
        (g.name, list(g.unicodes), g.note, list(g.tags), g.mark) for g in state.glyphs
    ]
    with pytest.raises(ValueError, match="stale|current"):
        action()
    assert not dialog._snapshot_valid and not state.history
    assert external == [
        (g.name, list(g.unicodes), g.note, list(g.tags), g.mark) for g in state.glyphs
    ]
    assert not any(
        getattr(dialog, name, NS(enabled=False)).enabled
        for name in ("apply_button", "add_button", "remove_button")
    )
    assert old or external
    dialog.close()


@pytest.mark.parametrize("title", TITLES)
def test_updateall_failure_preserves_completed_outcome_and_honest_status(load, title):
    module, state, native, _ = load
    if title == "Duplicate Unicodes":
        state.glyphs[1].unicodes.append(65)
    dialog = module(title).main()
    if title == "Unicode From Names":
        dialog.scope.setCurrentIndex(1)
    action = make_action(dialog, title)

    def fail():
        raise RuntimeError("UpdateAll unavailable")

    native.UpdateAll = fail
    with pytest.raises(
        RuntimeError, match="Names were applied.*Undo.*UpdateAll unavailable"
    ):
        action()
    assert dialog._batch_written and dialog.last_result is not None
    assert "applied" in dialog.status.text and "Undo" in dialog.status.text
    assert not dialog._snapshot_valid
    assert len(state.history) == 3
    dialog.close()


@pytest.mark.parametrize("title", TITLES)
def test_preview_failure_after_writing_cannot_publish_success(load, monkeypatch, title):
    module, state, native, _ = load
    if title == "Duplicate Unicodes":
        state.glyphs[1].unicodes.append(65)
    dialog = module(title).main()
    if title == "Unicode From Names":
        dialog.scope.setCurrentIndex(1)
    action = make_action(dialog, title)

    def update():
        native.CurrentFont = lambda: (_ for _ in ()).throw(
            RuntimeError("postwrite scan failed")
        )

    native.UpdateAll = update
    with pytest.raises(
        RuntimeError, match="Names were applied.*Undo.*postwrite scan failed"
    ):
        action()
    assert not dialog._snapshot_valid and "Undo" in dialog.status.text
    assert dialog.last_result is not None
    dialog.close()


@pytest.mark.parametrize(
    "title",
    ["Duplicate Unicodes", "Glyph Tags", "Mark Color Palette", "Unicode From Names"],
)
def test_only_original_explicit_reload_adopts_new_font(load, title):
    module, state, *_ = load
    dialog = module(title).main()
    new = NS(**vars(state.package))
    new.id = 8
    state.package = new
    dialog.reload()
    assert dialog._snapshot_valid and dialog._bound_id == 8
    dialog.close()


def test_noop_and_refused_direct_apply_have_no_history(load):
    module, state, *_ = load
    dialog = module("Batch Rename").main()
    dialog.find.setText("A")
    dialog.replace.setText("B")
    assert dialog.rows == [("A", "B", "exists in font")]
    dialog.apply()
    assert not state.history and dialog.last_result["renamed"] == []
    dialog.close()
    dialog = module("Glyph Notes").main()
    dialog.apply()
    assert not state.history and not dialog.last_result["changed"]
    dialog.close()


@pytest.mark.parametrize("title", TITLES)
def test_failed_initial_scan_recovers_only_against_known_original_font(load, title):
    module, state, native, _ = load
    original = native.CurrentFont
    native.CurrentFont = lambda: (_ for _ in ()).throw(
        RuntimeError("initial maps unavailable")
    )
    dialog = module(title).main()
    assert not dialog._snapshot_valid
    native.CurrentFont = original
    if title == "Glyph Notes":
        dialog.initialize_notes()
    elif title in {"Duplicate Unicodes", "Glyph Tags", "Unicode From Names"}:
        dialog.reload()
    else:
        dialog.refresh()
    assert dialog._snapshot_valid and dialog._bound_id == 7
    assert not state.history
    dialog.close()


@pytest.mark.parametrize("title", TITLES)
def test_first_checkpoint_failure_never_calls_native_setters(load, title):
    module, state, native, _ = load
    if title == "Duplicate Unicodes":
        state.glyphs[1].unicodes.append(65)
    dialog = module(title).main()
    if title == "Unicode From Names":
        dialog.scope.setCurrentIndex(1)
    action = make_action(dialog, title)
    before = [
        (g.name, list(g.unicodes), g.note, list(g.tags), g.mark) for g in state.glyphs
    ]
    native.flItems = lambda: NS(
        notifyChangesApplied=lambda *args: (_ for _ in ()).throw(
            RuntimeError("before checkpoint failed")
        )
    )
    with pytest.raises(RuntimeError, match="before checkpoint failed"):
        action()
    assert before == [
        (g.name, list(g.unicodes), g.note, list(g.tags), g.mark) for g in state.glyphs
    ]
    assert not dialog._snapshot_valid and "Error:" in dialog.status.text
    dialog.close()


def test_invalid_unicode_preview_cannot_partially_assign_valid_earlier_row(load):
    module, state, *_ = load
    state.glyphs = [Glyph("uni0041"), Glyph("u110000"), Glyph("uniD800")]
    dialog = module("Unicode From Names").main()
    dialog.scope.setCurrentIndex(1)
    assert dialog.rows == [
        ("uni0041", [], 65, "uni", "assign"),
        ("uniD800", [], 0xD800, "uni", "assign"),
    ]
    with pytest.raises(ValueError, match="scalar"):
        dialog.apply()
    assert not state.history and all(g.unicodes == [] for g in state.glyphs)
    dialog.close()


def test_menu_partial_write_retains_confirmed_names_and_native_cause(load):
    module, state, *_ = load
    dialog = module("Batch Rename").main()
    dialog.scope.setCurrentIndex(1)
    dialog.regex.setChecked(True)
    dialog.find.setText("^[AB]$")
    dialog.replace.setText("X\\g<0>")

    def rename(glyph, name, replace):
        if glyph.name == "B":
            raise RuntimeError("second native write failed")
        glyph.name = name
        return True

    state.package.renameGlyph = rename
    with pytest.raises(
        RuntimeError, match="partially.*Undo.*second native write failed"
    ):
        dialog.apply()
    assert dialog.last_result == {
        "partial": True,
        "confirmed": ["A"],
        "cause": "second native write failed",
    }
    assert [g.name for g in state.glyphs] == ["XA", "B", "Wacute"]
    assert len(state.history) == 3 and not dialog._snapshot_valid
    dialog.close()


@pytest.mark.parametrize("title", TITLES)
def test_no_font_panel_stays_empty_and_closes_without_history(load, title):
    module, state, *_ = load
    state.package = None
    dialog = module(title).main()
    assert not dialog._snapshot_valid and dialog.close_button.text == "Close"
    assert dialog.subtitle.text == "Open a font first."
    assert state.history == []
    dialog.close()


@pytest.mark.parametrize("title", ["Batch Rename", "Suffix Tool"])
def test_refresh_updates_auto_refusal_from_complete_current_references(load, title):
    module, state, *_ = load
    dialog = module(title).main()
    if title == "Batch Rename":
        dialog.find.setText("A")
        dialog.replace.setText("AA")
    state.glyphs[2].layers[0].autoLayer = True
    state.glyphs[2].layers[0].shapes.append(
        NS(isComponent=True, shapeData=NS(componentGlyph="A"))
    )
    dialog.refresh()
    assert [r[2] for r in dialog.rows if r[0] == "A"] == ["base of auto Wacute"]
    assert not state.history
    dialog.close()


@pytest.mark.parametrize("title", TITLES)
def test_postwrite_font_switch_preserves_applied_diagnostic_without_adopting_new_font(
    load, title
):
    module, state, native, _ = load
    if title == "Duplicate Unicodes":
        state.glyphs[1].unicodes.append(65)
    dialog = module(title).main()
    if title == "Unicode From Names":
        dialog.scope.setCurrentIndex(1)
    action = make_action(dialog, title)
    native.UpdateAll = lambda: setattr(state, "package", NS(id=88, isNull=False))
    with pytest.raises(RuntimeError, match="applied.*Undo"):
        action()
    assert dialog._bound_id == 7 and not dialog._snapshot_valid
    assert "applied" in dialog.status.text and dialog.last_result is not None
    dialog.close()


@pytest.mark.parametrize(
    "title,widget",
    [
        ("Duplicate Unicodes", "tree"),
        ("Glyph Tags", "table"),
        ("Unicode From Names", "scope"),
    ],
)
def test_failed_population_restores_owned_signal_block_state_and_recovers(
    load, monkeypatch, title, widget
):
    module, state, _native, _ = load
    tool = module(title)
    if title == "Duplicate Unicodes":
        state.glyphs[1].unicodes.append(65)
        attr = "QTreeWidgetItem"
        original = getattr(tool.QtGui, attr)

        def broken(*args):
            raise RuntimeError("render failed")

        monkeypatch.setattr(tool.QtGui, attr, broken)
    elif title == "Glyph Tags":
        state.glyphs[0].tags = ["keep"]
        attr = "QTableWidgetItem"
        original = getattr(tool.QtGui, attr)

        def broken(*args):
            raise RuntimeError("render failed")

        monkeypatch.setattr(tool.QtGui, attr, broken)
    else:
        original = Widget.addItem

        def broken(*args):
            raise RuntimeError("render failed")

        monkeypatch.setattr(Widget, "addItem", broken)
    dialog = tool.main()
    assert not dialog._snapshot_valid and "render failed" in dialog.status.text
    assert not getattr(dialog, widget).blocked, (
        "Population failure left owned signals blocked"
    )
    if title == "Unicode From Names":
        monkeypatch.setattr(Widget, "addItem", original)
    else:
        monkeypatch.setattr(tool.QtGui, attr, original)
    dialog.reload()
    assert dialog._snapshot_valid and not getattr(dialog, widget).blocked
    dialog.close()
