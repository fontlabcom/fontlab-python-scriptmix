# this_file: tests/test_issue122_G18.py
"""Exercise independent tools with strict host fakes; no native acceptance claim."""

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
PATHS = [
    "Kerning/Delete Kerning Pair From All Masters",
    "Kerning/Kern To Max",
    "Features/Generate Random Alternates Feature",
    "Masters/Reorder Shapes",
    "Masters/Show All Layers",
    "Kerning/Steal Kerning From Next Pair",
]


def load(index: int) -> ModuleType:
    """Load a menu without running its entry point."""
    spec = importlib.util.spec_from_file_location(
        f"g18_{index}", ROOT / "Scripts" / (PATHS[index] + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stub(monkeypatch: Any, name: str, **members: Any) -> ModuleType:
    """Install a module double at the actual Fly boundary."""
    module = ModuleType(name)
    module.__dict__.update(members)
    monkeypatch.setitem(sys.modules, name, module)
    if "." in name:
        parent, _, child = name.rpartition(".")
        if parent not in sys.modules:
            stub(monkeypatch, parent, __path__=[])
        monkeypatch.setitem(sys.modules[parent].__dict__, child, module)
    return module


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    """A current font and two adjacent master-layer occurrences."""
    package = NS(id=7, master="Regular", masters=["Regular", "Bold"])
    rows = []
    for index, (name, width) in enumerate((("A", 601), ("V", 501))):
        layer = NS(name="Regular", isMasterLayer=True, advanceWidth=width)
        rows.append(
            NS(
                package=package,
                glyph_name=name,
                layer=layer,
                layer_name="Regular",
                block_id=11,
                index=index,
            )
        )
    selection = NS(context=(7, "Regular", "editor"), occurrences=tuple(rows))
    stub(monkeypatch, "fly.ap.layer_selection", capture=lambda deadline: selection)
    stub(monkeypatch, "fly.ap.scripting", current_package=lambda: package)
    groups = {"AGroup": (("A",), "KernLeft"), "VGroup": (("V",), "KernRight")}
    pair = (("AGroup", "groupMode"), ("VGroup", "groupMode"))
    snapshot = NS(
        groups={m: groups for m in package.masters},
        pairs={m: {pair: -80} for m in package.masters},
    )
    writes = []
    stub(
        monkeypatch,
        "fly.ap.kerning_batch",
        snapshot_kerning=lambda p, typed: snapshot,
        write_kerning=lambda *a, **k: writes.append((a, k)) or True,
    )
    return NS(
        package=package,
        rows=rows,
        selection=selection,
        snapshot=snapshot,
        writes=writes,
    )


def test_delete_all_masters_one_shared_batch(host: Any) -> None:
    load(0).run()
    assert len(host.writes) == 1
    args, kwargs = host.writes[0]
    pair = (("AGroup", "groupMode"), ("VGroup", "groupMode"))
    assert args[1] == {"Regular": {pair: None}, "Bold": {pair: None}}
    assert kwargs["expected"] is host.snapshot


def test_kern_half_narrower_width_truncates(host: Any) -> None:
    load(1).run()
    assert len(host.writes) == 1
    assert list(host.writes[0][0][1]["Regular"].values()) == [-250]


@pytest.mark.parametrize("index", [0, 1])
@pytest.mark.parametrize("failure", ["empty", "font", "gap", "block", "aux", "master"])
def test_pair_context_refuses_before_write(host: Any, index: int, failure: str) -> None:
    if failure == "empty":
        host.selection.occurrences = ()
    elif failure == "font":
        host.selection.context = (7, "Regular", "font")
    elif failure == "gap":
        host.rows[1].index = 3
    elif failure == "block":
        host.rows[1].block_id = 12
    elif failure == "aux":
        host.rows[1].layer.isMasterLayer = False
    else:
        host.rows[1].layer.name = "Bold"
    with pytest.raises(ValueError):
        load(index).run()
    assert host.writes == []


@pytest.mark.parametrize("width", [-1, float("nan"), float("inf")])
def test_invalid_width_refuses(host: Any, width: float) -> None:
    host.rows[0].layer.advanceWidth = width
    with pytest.raises(ValueError):
        load(1).run()
    assert host.writes == []


def test_ambiguous_group_refuses(host: Any) -> None:
    host.snapshot.groups["Regular"]["Second"] = (("A",), "KernLeft")
    with pytest.raises(ValueError, match="multiple"):
        load(0).run()
    assert host.writes == []


def test_literal_at_name_keeps_glyph_mode(host: Any) -> None:
    host.rows[0].glyph_name = "@literal"
    for records in host.snapshot.pairs.values():
        records[(("@literal", "glyphMode"), ("VGroup", "groupMode"))] = -30
    load(0).run()
    pair = next(iter(host.writes[0][0][1]["Regular"]))
    assert pair[0] == ("@literal", "glyphMode")


def test_feature_generator_deterministic_complete_and_compiles() -> None:
    from io import StringIO

    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.feaLib.parser import Parser
    from fontTools.ttLib import TTFont

    tool = load(2)
    names = ["a", "a.ss01", "b", "b.ss01", "period"]
    options = ("a a.ss01\nb b.ss01", names, names, "calt", 20, 3, 4, 5, 19)
    text = tool.generate(*options)
    assert text == tool.generate(*options)
    assert text.count("    sub ") == 80
    assert text.count("lookup G18") == 0, "No batch labels in public code"
    Parser(StringIO(text), glyphNames=names).parse()
    font = TTFont()
    font.setGlyphOrder([".notdef", *names])
    addOpenTypeFeaturesFromString(font, text)
    assert "GSUB" in font, "Generated contextual rules must compile to GSUB"


@pytest.mark.parametrize("text", ["", "a", "a missing", "a a", "a a.ss01\na b"])
def test_feature_invalid_alternates_refuse(text: str) -> None:
    with pytest.raises(ValueError):
        load(2).generate(text, ["a", "a.ss01", "b"], ["a"], "calt", 2, 3, 1, 1, 0)


@pytest.mark.parametrize("tag", ["", "longtag", "a{xx", "éabc"])
def test_feature_invalid_tag_refuses(tag: str) -> None:
    with pytest.raises(ValueError):
        load(2).generate("a a.ss01", ["a", "a.ss01"], ["a"], tag, 2, 3, 1, 1, 0)


def shape(ident: int, count: int, x: float, y: float, base: str = "") -> Any:
    """Shape carrier; no native clone or detach API exists on purpose."""
    return NS(
        id=ident,
        isComponent=bool(base),
        base=base,
        contours=[NS(nodesCount=count)],
        boundingBox=NS(x=lambda: x, y=lambda: y),
    )


def test_order_keeps_groups_and_components(monkeypatch: Any) -> None:
    stub(monkeypatch, "fly.ap.component_writer", base_of=lambda s: s.base)
    items = [
        shape(4, 0, 0, 0, "z"),
        shape(3, 8, 0, 0),
        shape(2, 4, 25, 15),
        shape(1, 4, 0, 0),
    ]
    assert load(3).ordered_ids(items) == [1, 2, 3, 4]


def test_show_layers_preserves_occurrences_and_exact_names(
    host: Any, monkeypatch: Any
) -> None:
    layers = [
        NS(name="Regular", isMaskLayer=False, isService=False),
        NS(name="Bold@backup", isMaskLayer=False, isService=False),
        NS(name="mask.Regular", isMaskLayer=True, isService=True),
    ]
    for row in host.rows:
        row.glyph = NS(layers=layers)
    calls = []
    stub(
        monkeypatch,
        "fly.ap.named_tab",
        open_layer_tab=lambda *a, **k: calls.append((a, k)),
    )
    load(4).run()
    assert calls[0][0][0] == (
        ("A", "Regular"),
        ("A", "Bold@backup"),
        ("V", "Regular"),
        ("V", "Bold@backup"),
    )
    assert calls[0][1]["expected_id"] == 7


def test_real_app_names_resolve() -> None:
    paths = [ROOT / "Scripts" / (name + ".py") for name in PATHS]
    check_real_app_names(app_names_used(paths))


def test_panel_names_do_not_shadow_native_members() -> None:
    banned = {"render", "size", "layout", "update", "font", "move", "statusBar"}
    for name in PATHS:
        tree = ast.parse((ROOT / "Scripts" / (name + ".py")).read_text())
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            assert not banned.intersection(
                n.name for n in cls.body if isinstance(n, ast.FunctionDef)
            )
            for node in ast.walk(cls):
                if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                    assert node.attr not in banned


@pytest.fixture
def reorder_host(host: Any, monkeypatch: Any, real_app: Any) -> Any:
    """Real App history over owned layer/glyph/notification fakes."""
    notifications = []
    native = NS(
        flGlyph=NS(updatedFgGlyphs=list),
        flItems=lambda: NS(notifyChangesApplied=lambda *a: notifications.append(a)),
    )
    qt = NS(QtCore=NS(QDateTime=NS(currentDateTimeUtc=lambda: "STAMP")))
    modules = real_app(
        qt=qt,
        fontlab=native,
        scripting={"current_package": lambda: host.package},
        modules=("history", "edit_guards"),
    )
    facts = modules["history"].auto_facts([])
    monkeypatch.setattr(modules["history"], "scan_auto_facts", lambda p: facts)
    stub(monkeypatch, "fly.ap.history", **vars(modules["history"]))
    stub(monkeypatch, "fly.ap.component_writer", base_of=lambda s: s.base)
    shapes = [shape(2, 8, 0, 0), shape(1, 4, 0, 0)]
    layer = NS(
        name="Regular",
        shapes=shapes,
        isMaskLayer=False,
        isService=False,
        autoLayer=False,
        isLocked=False,
        checkInitHistoryState=lambda n: None,
        changed=lambda: None,
    )

    def reorder(ids: list[int]) -> None:
        layer.shapes = sorted(layer.shapes, key=lambda s: ids.index(s.id))

    layer.reorderShapes = reorder
    glyph = NS(
        id=19,
        name="A",
        layers=[layer],
        lastModified="OLD",
        checkInitHistoryState=lambda n: None,
    )
    host.rows[0].glyph = glyph
    host.selection.occurrences = (host.rows[0],)
    return NS(host=host, layer=layer, glyph=glyph, calls=notifications, facts=facts)


def test_reorder_real_history_one_notification_shape(reorder_host: Any) -> None:
    state = reorder_host
    changed = []
    state.layer.changed = lambda: changed.append(True)
    assert load(3).run()["changed"] == 1
    assert [s.id for s in state.layer.shapes] == [1, 2]
    assert state.calls == [("Reorder Shapes", [state.layer, state.glyph])]
    assert state.glyph.lastModified == "STAMP"
    assert changed == [True]
    assert load(3).run()["changed"] == 0, "Already ordered layers must not add history"
    assert len(state.calls) == 1
    assert changed == [True]


@pytest.mark.parametrize("flag", ["autoLayer", "isLocked"])
def test_reorder_unsafe_layer_refuses_before_history(
    reorder_host: Any, flag: str
) -> None:
    setattr(reorder_host.layer, flag, True)
    result = load(3).run()
    assert result["changed"] == 0
    assert result["skipped"]
    assert reorder_host.calls == []
    assert [s.id for s in reorder_host.layer.shapes] == [2, 1]


def test_reorder_readback_failure_has_undo_hint(reorder_host: Any) -> None:
    reorder_host.layer.reorderShapes = lambda ids: None
    with pytest.raises(RuntimeError, match="use Edit > Undo"):
        load(3).run()
    assert len(reorder_host.calls) == 1


def test_reorder_partial_failure_has_undo_hint(reorder_host: Any) -> None:
    def fail(ids: list[int]) -> None:
        raise RuntimeError("native write failed")

    reorder_host.layer.reorderShapes = fail
    with pytest.raises(RuntimeError, match="use Edit > Undo"):
        load(3).run()
    assert len(reorder_host.calls) == 1


@pytest.mark.parametrize("count", [0, -1, 1.5])
def test_feature_invalid_counts_refuse(count: Any) -> None:
    with pytest.raises(ValueError):
        load(2).generate("a a.ss01", ["a", "a.ss01"], ["a"], "calt", count, 3, 1, 1, 0)


@pytest.mark.parametrize("separator", ["\x00", "\u00a0", "\u2028", "\u2029"])
def test_feature_lossy_text_refuses(separator: str) -> None:
    with pytest.raises(ValueError):
        load(2).generate(
            "a" + separator + "a.ss01", ["a", "a.ss01"], ["a"], "calt", 2, 3, 1, 1, 0
        )


def test_feature_category_inheritance_and_unknown_refusal() -> None:
    tool = load(2)
    rows = (
        ("a", "U+0061", ""),
        ("a.ss01", "", ""),
        ("period", "U+002E", ""),
        ("unencoded", "", ""),
    )
    assert tool.category_members(rows, "Letter") == ["a", "a.ss01"]
    assert tool.category_members(rows, "All") == [r[0] for r in rows]
    with pytest.raises(ValueError):
        tool.category_members(rows, "Unknown")


def test_feature_panel_preview_invalidation_and_copy(
    host: Any, monkeypatch: Any
) -> None:
    """Use strict widget fakes to exercise source controls and Copy lifecycle."""
    forbidden = {"render", "size", "layout", "update", "font", "move", "statusBar"}

    class Widget:
        def __init__(self, text: str = "") -> None:
            self.text = text
            self.textChanged = object()
            self.clicked = object()

        def __setattr__(self, name: str, value: Any) -> None:
            if name in forbidden:
                raise AttributeError(name)
            object.__setattr__(self, name, value)

        def setText(self, text: str) -> None:
            self.text = text

        def setPlainText(self, text: str) -> None:
            self.text = text

        def toPlainText(self) -> str:
            return self.text

        def setEnabled(self, enabled: bool) -> None:
            self.enabled = enabled

        def setChecked(self, checked: bool) -> None:
            self.checked = checked

        def isChecked(self) -> bool:
            return getattr(self, "checked", False)

        def setReadOnly(self, enabled: bool) -> None:
            pass

        def setPlaceholderText(self, text: str) -> None:
            pass

        def addWidget(self, *args: Any) -> None:
            pass

        def addLayout(self, *args: Any) -> None:
            pass

    class PanelBase(Widget):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()
            self.apply_button = Widget()
            self.status = Widget()
            self.package = host.package
            self.setup()

        def prepare(self) -> Any:
            return Widget()

        def _connect(self, signal: Any, slot: Any) -> None:
            pass

        def ensure_font(self) -> None:
            pass

        def ensure_preview(self) -> None:
            if not self._preview_valid:
                raise ValueError("No preview")

        def copy_text(self, text: str) -> None:
            self.copied_text = text

    stub(
        monkeypatch,
        "fly.qt",
        QtGui=NS(
            QLineEdit=Widget,
            QPlainTextEdit=Widget,
            QGridLayout=Widget,
            QHBoxLayout=Widget,
            QVBoxLayout=Widget,
            QCheckBox=Widget,
            QLabel=Widget,
            QPushButton=Widget,
        ),
    )
    sys.modules["fly.ap.scripting"].features_dialog_type = lambda: PanelBase
    rows = (("a", "U+0061", ""), ("a.ss01", "", ""))
    table = NS(rows=rows)
    stub(monkeypatch, "fly.ap.glyph_catalog", capture=lambda: table)
    feature_writes = []
    feature_state = {"blocks": {"prefix": "", "features": []}}

    def write_blocks(*args: Any, **kwargs: Any) -> dict:
        feature_writes.append((args, kwargs))
        changed = int(feature_state["blocks"] != args[2])
        feature_state["blocks"] = args[2]
        return {"changed": changed}

    stub(
        monkeypatch,
        "fly.fp.feature_blocks",
        read_feature_blocks=lambda p: feature_state["blocks"],
        write_feature_blocks=write_blocks,
    )
    panel = load(2).panel_type()()
    panel.source_edit.text = "a a.ss01"
    panel.option_edits["Classes"].text = "2"
    panel.refresh()
    assert panel.apply_button.enabled
    panel.copy_preview()
    assert panel.copied_text == panel.preview_code
    assert panel.apply_button.text == "Write feature"
    panel.apply()
    assert feature_writes[0][0][2]["features"] == [("calt", panel.preview_code)]
    old = "feature calt {\n# Keep this code until consent.\n} calt;\n"
    feature_state["blocks"] = {"prefix": "", "features": [("calt", old)]}
    panel.refresh()
    assert panel.existing_edit.text == old
    assert panel.output_edit.text == panel.preview_code
    assert not panel.replace_check.isChecked()
    assert "3 lines" in panel.status.text
    panel.apply()
    assert len(feature_writes) == 1, (
        "A differing existing feature needs explicit consent"
    )
    assert "already exists" in panel.status.text
    assert panel._preview_valid and panel.copy_button.enabled
    panel.replace_check.setChecked(True)
    panel.apply()
    assert len(feature_writes) == 2
    assert not panel.replace_check.isChecked(), "Consent must reset after writing"
    assert panel.existing_edit.text == panel.preview_code
    panel.replace_check.setChecked(True)
    panel.option_edits["Feature"].text = "salt"
    panel.refresh()
    assert not panel.replace_check.isChecked(), "Changing the tag must reset consent"
    panel.replace_check.setChecked(True)
    feature_state["blocks"] = {"prefix": "# Source changed", "features": []}
    panel.refresh()
    assert not panel.replace_check.isChecked(), "Changing source must reset consent"
    panel.option_edits["Feature"].text = "calt"
    panel.option_edits["Lines"].text = "not a number"
    with pytest.raises(ValueError, match="must be whole numbers"):
        panel.refresh()
    assert not panel.copy_button.enabled
    panel.option_edits["Lines"].text = "20"
    panel.refresh()
    panel.invalidate_preview()
    assert not panel.apply_button.enabled
    with pytest.raises(ValueError):
        panel.copy_preview()
    panel.refresh()
    table.rows = rows + (("b", "U+0062", ""),)
    with pytest.raises(ValueError, match="catalogue changed"):
        panel.copy_preview()


@pytest.mark.parametrize("index", [0, 1, 3, 4])
def test_menu_entry_contains_timeout(index: int, monkeypatch: Any, capsys: Any) -> None:
    tool = load(index)

    def fail() -> None:
        raise TimeoutError("capture deadline")

    monkeypatch.setattr(tool, "run", fail)
    tool.main()
    assert "capture deadline" in capsys.readouterr().out


def test_feature_entry_contains_panel_failure(host: Any, capsys: Any) -> None:
    def fail(*args: Any) -> None:
        raise TimeoutError("panel deadline")

    sys.modules["fly.ap.scripting"].show_script_dialog = fail
    tool = load(2)
    tool.panel_type = lambda: object
    assert tool.main() is None
    assert "panel deadline" in capsys.readouterr().out


def test_show_empty_selection_opens_no_tab(host: Any, monkeypatch: Any) -> None:
    host.selection.occurrences = ()
    calls = []
    stub(
        monkeypatch, "fly.ap.named_tab", open_layer_tab=lambda *a, **k: calls.append(a)
    )
    with pytest.raises(ValueError):
        load(4).run()
    assert calls == []


def test_reorder_auto_dependant_refuses_before_history(
    reorder_host: Any, monkeypatch: Any
) -> None:
    history = sys.modules["fly.ap.history"]
    facts = history.auto_facts([("Aacute", True, ("A",))])
    monkeypatch.setattr(history, "scan_auto_facts", lambda p: facts)
    result = load(3).run()
    assert result["changed"] == 0
    assert "base of auto" in str(result["skipped"])
    assert reorder_host.calls == []


def test_reorder_same_permutation_when_master_positions_flip(reorder_host: Any) -> None:
    state = reorder_host
    first = [shape(2, 4, 0, 20), shape(1, 4, 0, 0)]
    second = [shape(4, 4, 0, 0), shape(3, 4, 0, 20)]
    state.layer.shapes = first
    other = NS(**vars(state.layer))
    other.name, other.shapes = "Bold", second
    other.reorderShapes = lambda ids: setattr(
        other, "shapes", sorted(other.shapes, key=lambda s: ids.index(s.id))
    )
    state.glyph.layers.append(other)
    result = load(3).run()
    assert result["changed"] == 2
    assert [s.id for s in state.layer.shapes] == [1, 2]
    assert [s.id for s in other.shapes] == [3, 4], (
        "Must follow the reference index permutation"
    )


def test_reorder_lists_mismatched_master(reorder_host: Any) -> None:
    state = reorder_host
    other = NS(**vars(state.layer))
    other.name, other.shapes = "Bold", [shape(3, 9, 0, 0)]
    state.glyph.layers.append(other)
    result = load(3).run()
    assert result["changed"] == 1
    assert "Bold" in str(result["skipped"])
    assert [s.id for s in other.shapes] == [3]


def test_reorder_skips_one_glyph_and_writes_another(reorder_host: Any) -> None:
    state = reorder_host
    locked_layer = NS(**vars(state.layer))
    locked_layer.isLocked = True
    refused = NS(id=20, name="V", layers=[locked_layer])
    state.host.selection.occurrences += (NS(glyph=refused),)
    result = load(3).run()
    assert result["changed"] == 1
    assert "V" in str(result["skipped"])
    assert state.calls == [("Reorder Shapes", [state.layer, state.glyph])]


@pytest.mark.parametrize("has_target", [False, True])
def test_feature_writer_replaces_only_target_with_exact_references(
    host: Any, monkeypatch: Any, has_target: bool
) -> None:
    tool = load(2)
    before = {
        "prefix": "# keep prefix",
        "features": [("liga", "KEEP")] + ([("calt", "OLD")] if has_target else []),
    }
    code = tool.generate("a a.ss01", ["a", "a.ss01"], ["a"], "calt", 1, 1, 1, 1, 3)
    writes = []
    stub(
        monkeypatch,
        "fly.fp.feature_blocks",
        read_feature_blocks=lambda p: before,
        write_feature_blocks=lambda *a, **k: writes.append((a, k)) or {"changed": 1},
    )
    tool.write_feature(host.package, before, "calt", code, replace=has_target)
    args, kwargs = writes[0]
    assert args == (
        host.package,
        before,
        {"prefix": "# keep prefix", "features": [("liga", "KEEP"), ("calt", code)]},
    )
    assert kwargs == {"references": ["a", "a.ss01"], "undo_name": tool.TITLE}
    assert before["features"] == [("liga", "KEEP")] + (
        [("calt", "OLD")] if has_target else []
    )


def test_feature_writer_refuses_stale_source(host: Any, monkeypatch: Any) -> None:
    writes = []
    stub(
        monkeypatch,
        "fly.fp.feature_blocks",
        read_feature_blocks=lambda p: {"prefix": "changed", "features": []},
        write_feature_blocks=lambda *a, **k: writes.append(a),
    )
    with pytest.raises(ValueError, match="source changed"):
        load(2).write_feature(
            host.package,
            {"prefix": "", "features": []},
            "calt",
            "feature calt {} calt;",
        )
    assert writes == []


def test_feature_writer_refuses_replacement_without_consent(
    host: Any, monkeypatch: Any
) -> None:
    before = {"prefix": "", "features": [("calt", "OLD")]}
    writes = []
    stub(
        monkeypatch,
        "fly.fp.feature_blocks",
        read_feature_blocks=lambda p: before,
        write_feature_blocks=lambda *a, **k: writes.append(a),
    )
    with pytest.raises(
        ValueError, match="Feature calt already exists; tick Replace existing feature"
    ):
        load(2).write_feature(host.package, before, "calt", "NEW")
    assert writes == []


@pytest.mark.parametrize("identical", [False, True])
def test_feature_append_and_identical_need_no_consent(
    host: Any, monkeypatch: Any, identical: bool
) -> None:
    code = "feature calt {\n} calt;\n"
    before = {"prefix": "", "features": [("calt", code)] if identical else []}
    writes = []
    stub(
        monkeypatch,
        "fly.fp.feature_blocks",
        read_feature_blocks=lambda p: before,
        write_feature_blocks=lambda *a, **k: (
            writes.append(a) or {"changed": int(not identical)}
        ),
    )
    result = load(2).write_feature(host.package, before, "calt", code)
    assert result["changed"] == int(not identical)
    assert len(writes) == 1


def test_delete_only_counts_existing_records(host: Any) -> None:
    host.snapshot.pairs["Bold"] = {}
    assert load(0).run()["removed"] == 1


def test_kern_narrower_left_and_noop_message(host: Any, capsys: Any) -> None:
    host.rows[0].layer.advanceWidth = 301
    assert load(1).run()["value"] == -150
    key = (("AGroup", "groupMode"), ("VGroup", "groupMode"))
    host.snapshot.pairs["Regular"][key] = -150
    load(1).main()
    assert "unchanged" in capsys.readouterr().out.lower()


@pytest.fixture
def four_slots(host: Any, monkeypatch: Any) -> Any:
    """Four same-master slots with rectangular decomposed outline polygons."""
    names = ["A", "V", "V", "A"]
    for index in range(4):
        if index >= len(host.rows):
            host.rows.append(NS(**vars(host.rows[0])))
        row = host.rows[index]
        row.index, row.glyph_name = index, names[index]
        row.layer = NS(
            name="Regular",
            isMasterLayer=True,
            advanceWidth=500,
            edges=(50, 450) if index < 2 else (75, 425),
        )
    host.selection.occurrences = tuple(host.rows)
    host.package.kerning = lambda master: NS(get=lambda pair: -25)
    sys.modules["fly.ap.scripting"].kerning_pair_value = lambda kern, left, right: (
        kern.get((left, right))
    )
    for row in host.rows:
        row.layer.shapes = [NS(contours=[NS(isTT=False, closed=True)])]
    stub(
        monkeypatch,
        "fly.ap.masters",
        layer_contours=lambda layer: [
            [
                (layer.edges[0], 0, True),
                (layer.edges[1], 0, True),
                (layer.edges[1], 500, True),
                (layer.edges[0], 500, True),
            ]
        ],
        polygon=lambda points: [(x, y) for x, y, _ in points],
    )
    return host


@pytest.mark.parametrize("group_record_exists", [False, True])
def test_steal_equalizes_measured_gaps(
    four_slots: Any, group_record_exists: bool
) -> None:
    key = (("AGroup", "groupMode"), ("VGroup", "groupMode"))
    if not group_record_exists:
        four_slots.snapshot.pairs["Regular"].pop(key)
    result = load(5).run(250)
    assert result["value"] == 25, "Reference gap 150 - target gap 100 - 25 kerning"
    assert list(four_slots.writes[0][0][1]["Regular"].values()) == [25]
    assert next(iter(four_slots.writes[0][0][1]["Regular"])) == (
        ("AGroup", "groupMode"),
        ("VGroup", "groupMode"),
    )


@pytest.mark.parametrize("kind", ["group", "glyph", "mixed"])
def test_steal_computed_zero_removes_record(four_slots: Any, kind: str) -> None:
    four_slots.package.kerning = lambda master: NS(get=lambda pair: -50)
    key = (("AGroup", "groupMode"), ("VGroup", "groupMode"))
    if kind == "glyph":
        key = (("A", "glyphMode"), ("V", "glyphMode"))
    elif kind == "mixed":
        key = (("A", "glyphMode"), ("VGroup", "groupMode"))
    four_slots.snapshot.pairs["Regular"][key] = -70
    result = load(5).run(250)
    assert result["value"] == 0
    assert four_slots.writes[0][0][1] == {"Regular": {key: None}}


def test_steal_open_contours_are_skipped_and_named(
    four_slots: Any, monkeypatch: Any
) -> None:
    four_slots.rows[0].layer.shapes[0].contours.append(NS(isTT=False, closed=False))
    masters = sys.modules["fly.ap.masters"]
    original = masters.layer_contours
    monkeypatch.setattr(
        masters,
        "layer_contours",
        lambda layer: original(layer) * len(layer.shapes[0].contours),
    )
    result = load(5).run(250)
    assert result["value"] == 25
    assert result["notices"] == ["A: skipped 1 open contour."]
    assert len(four_slots.writes) == 1


def test_steal_keeps_existing_target_exception(four_slots: Any) -> None:
    pair = (("A", "glyphMode"), ("V", "glyphMode"))
    four_slots.snapshot.pairs["Regular"][pair] = -40
    load(5).run(250)
    assert next(iter(four_slots.writes[0][0][1]["Regular"])) == pair


@pytest.mark.parametrize("height", [-1, 501, float("nan"), float("inf")])
def test_steal_bad_height_or_no_crossing_refuses(
    four_slots: Any, height: float
) -> None:
    with pytest.raises(ValueError):
        load(5).run(height)
    assert four_slots.writes == []


@pytest.mark.parametrize("one_master", [False, True])
def test_delete_real_kerning_writer_preserves_exception(
    host: Any, monkeypatch: Any, real_app: Any, one_master: bool, capsys: Any
) -> None:
    """Exercise actual snapshot, staging, removal and readback over native containers."""
    group = (("AGroup", "groupMode"), ("VGroup", "groupMode"))
    exception = (("A", "glyphMode"), ("V", "glyphMode"))

    class Kerning:
        def __init__(self) -> None:
            self.groups = {
                "AGroup": (("A",), "KernLeft"),
                "VGroup": (("V",), "KernRight"),
            }
            self.values = {group: -80, exception: -45}
            self.removed = []

        def items(self) -> list:
            return [
                (
                    NS(
                        left=NS(id=pair[0][0], mode=pair[0][1]),
                        right=NS(id=pair[1][0], mode=pair[1][1]),
                    ),
                    value,
                )
                for pair, value in self.values.items()
            ]

        def remove(self, pair: tuple) -> None:
            self.removed.append(pair)
            self.values.pop(pair, None)

        def set(self, pair: tuple, value: int) -> None:
            self.values[pair] = value

        def scale(self, factor: float) -> None:
            self.values = {pair: value * factor for pair, value in self.values.items()}

    containers = {name: Kerning() for name in ("Regular", "Bold")}
    if one_master:
        containers["Bold"].values.pop(group)
    masters, kerning, calls, initialized = object(), object(), [], []
    package = NS(
        id=7,
        master="Regular",
        masters=["Regular", "Bold"],
        upm=1000,
        kerning=lambda master: containers[master],
        findName=lambda name: NS(isNull=False) if name in {"A", "V"} else None,
        mastersContainer=lambda: masters,
        kerningContainer=lambda: kerning,
        checkInitHistoryState=lambda index: initialized.append(index),
    )
    native = NS(flItems=NS(notifyChangesApplied=lambda *a: calls.append(a)))
    modules = real_app(
        qt=NS(),
        fontlab=native,
        scripting={"current_package": lambda *a: package},
        modules=("kerning_batch",),
    )
    stub(monkeypatch, "fly.ap.kerning_batch", **vars(modules["kerning_batch"]))
    stub(monkeypatch, "fly.ap.scripting", current_package=lambda: package)
    result = load(0).run()
    assert result["removed"] == (1 if one_master else 2)
    for name, container in containers.items():
        assert container.removed == ([] if one_master and name == "Bold" else [group])
        assert container.values == {exception: -45}
    assert initialized == [0]
    assert (
        calls
        == [("Delete Kerning Pair From All Masters", [package, masters, kerning])] * 2
    )
    load(0).main()
    assert "No kerning to delete" in capsys.readouterr().out
    assert len(calls) == 2, "No-op must add no history checkpoints"


def test_delete_three_glyphs_deletes_two_pairs(host: Any) -> None:
    third = NS(**vars(host.rows[0]))
    third.index = 2
    host.selection.occurrences += (third,)
    reverse = (("V", "glyphMode"), ("A", "glyphMode"))
    for records in host.snapshot.pairs.values():
        records[reverse] = -20
    result = load(0).run()
    assert result["removed"] == 4
    assert all(len(edits) == 2 for edits in host.writes[0][0][1].values())


@pytest.mark.parametrize("index", [0, 1])
def test_class_actions_list_overriding_exceptions(
    host: Any, index: int, capsys: Any
) -> None:
    exception = (("A", "glyphMode"), ("V", "glyphMode"))
    host.snapshot.pairs["Regular"][exception] = -55
    load(index).main()
    output = capsys.readouterr().out
    assert "Overriding exception kept" in output and "-55" in output


def test_steal_refuses_stale_geometry(four_slots: Any) -> None:
    tool = load(5)
    preview = tool.plan(250)
    four_slots.rows[0].layer.edges = (70, 440)
    with pytest.raises(ValueError, match="preview changed"):
        tool.write(preview)
    assert four_slots.writes == []


def test_steal_transformed_components_and_quadratic_crossings(
    monkeypatch: Any, real_app: Any
) -> None:
    class Point:
        def __init__(self, x: float, y: float) -> None:
            self.coords = (x, y)

        def x(self) -> float:
            return self.coords[0]

        def y(self) -> float:
            return self.coords[1]

    qt = NS(QtCore=NS(QPointF=Point))
    modules = real_app(qt=qt, fontlab=NS(), modules=("masters",))
    stub(monkeypatch, "fly.ap.masters", **vars(modules["masters"]))

    def layer(points: list, quadratic: bool, offset: float) -> Any:
        contour = NS(
            isTT=quadratic,
            closed=True,
            nodes=lambda: [NS(x=x, y=y, isOn=lambda on=on: on) for x, y, on in points],
        )
        transform = NS(
            isIdentity=lambda: False, map=lambda p: Point(p.x() + offset, p.y())
        )
        return NS(
            name="Regular",
            shapes=[NS(contours=[contour], transform=transform, isComponent=True)],
        )

    rectangle = layer(
        [(50, 0, True), (450, 0, True), (450, 500, True), (50, 500, True)], False, 100
    )
    tool = load(5)
    assert tool.extents(rectangle, 250) == (150, 550)
    assert tool.extents(rectangle, 500) == (150, 550), "Top flat edge must be included"
    assert tool.extents(rectangle, 0) == (150, 550), "Bottom flat edge must be included"
    arc = layer([(0, 0, True), (50, 100, False), (100, 0, True)], True, 0)
    left, right = tool.extents(arc, 25)
    assert 14 < left < 16 and 84 < right < 86
    assert tool.quadratic_cubics([]) == []
    implied = tool.quadratic_cubics([(0, 0, False), (100, 0, False)])
    assert implied[0] == (50, 0, True)
    arc.shapes[0].contours[0].closed = False
    notices = []
    rectangle.shapes.extend(arc.shapes)
    assert tool.extents(rectangle, 250, glyph_name="A", notices=notices) == (150, 550)
    assert notices == ["A: skipped 1 open contour."]
    with pytest.raises(ValueError, match="A.*No closed outline crossing"):
        tool.extents(arc, 25, glyph_name="A")


def test_steal_panel_half_xheight_preview_and_apply(
    four_slots: Any, monkeypatch: Any
) -> None:
    forbidden = {"render", "size", "layout", "update", "font", "move", "statusBar"}

    class Widget:
        def __init__(self, text: str = "") -> None:
            self.text = text
            self.textChanged, self.clicked = object(), object()

        def __setattr__(self, name: str, value: Any) -> None:
            if name in forbidden:
                raise AttributeError(name)
            object.__setattr__(self, name, value)

        def addWidget(self, *args: Any) -> None:
            pass

        def setEnabled(self, enabled: bool) -> None:
            self.enabled = enabled

        def setText(self, text: str) -> None:
            self.text = text

    class Panel(Widget):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__()
            self.package = four_slots.package
            self.package_id = self.package.id
            self.form, self.apply_button, self.status = Widget(), Widget(), Widget()
            self.setup()

        def _connect(self, signal: Any, callback: Any) -> None:
            pass

        def ensure_font(self) -> None:
            pass

        def ensure_preview(self) -> None:
            if not self._preview_valid:
                raise ValueError("No preview")

        def rows(self, headings: list[str], rows: list) -> None:
            self.visible_headings = headings
            self.visible_rows = rows

    metrics_calls = []
    four_slots.package.master = "Bold"
    stub(
        monkeypatch,
        "fly.fl",
        FontMetrics=lambda p, m: metrics_calls.append(m) or NS(xHeight=550),
    )
    stub(
        monkeypatch,
        "fly.qt",
        QtGui=NS(QLineEdit=Widget, QLabel=Widget, QPushButton=Widget),
    )
    sys.modules["fly.ap.scripting"].font_info_dialog_type = lambda: Panel
    panel = load(5).panel_type()()
    assert panel.height_edit.text == "275"
    assert metrics_calls == ["Regular"], "Default must use the shown master"
    panel.refresh()
    assert panel.visible_rows[0][-1] == 25
    assert "Record" in panel.visible_headings
    assert (
        panel.visible_rows[0][panel.visible_headings.index("Record")]
        == "@AGroup · @VGroup"
    )
    panel.apply()
    assert len(four_slots.writes) == 1
    panel.height_edit.text = "bad"
    with pytest.raises(ValueError, match="finite number"):
        panel.refresh()
    assert not panel.apply_button.enabled


@pytest.mark.parametrize("failure", ["count", "gap", "block", "master"])
def test_steal_bad_selection_refuses(four_slots: Any, failure: str) -> None:
    if failure == "count":
        four_slots.selection.occurrences = tuple(four_slots.rows[:3])
    elif failure == "gap":
        four_slots.rows[3].index = 10
    elif failure == "block":
        four_slots.rows[3].block_id = 12
    else:
        four_slots.rows[3].layer.name = "Bold"
    with pytest.raises(ValueError):
        load(5).run(250)
    assert four_slots.writes == []


def test_reorder_budget_is_per_glyph(reorder_host: Any, monkeypatch: Any) -> None:
    state = reorder_host
    other = NS(**vars(state.layer))
    other.reorderShapes = lambda ids: setattr(
        other, "shapes", sorted(other.shapes, key=lambda s: ids.index(s.id))
    )
    glyph = NS(
        id=20,
        name="V",
        layers=[other],
        lastModified="OLD",
        checkInitHistoryState=lambda n: None,
    )
    state.host.selection.occurrences += (NS(glyph=glyph),)
    tool = load(3)
    clock = [0.0]
    original = tool.ordered_ids

    def slow_sort(shapes: list) -> list[int]:
        clock[0] += 1.5
        return original(shapes)

    monkeypatch.setattr(tool, "monotonic", lambda: clock[0])
    monkeypatch.setattr(tool, "ordered_ids", slow_sort)
    assert tool.run()["changed"] == 2
    assert clock[0] == 3, "A total over two seconds must not reject independent glyphs"


def test_layer_proof_budget_is_per_glyph(host: Any, monkeypatch: Any) -> None:
    clock, calls = [0.0], []
    layers = [NS(name="Regular", isMaskLayer=False, isService=False)]

    class SlowLayers:
        def __iter__(self) -> Any:
            clock[0] += 1.5
            return iter(layers)

    for row in host.rows:
        row.glyph = NS(layers=SlowLayers())
    stub(
        monkeypatch,
        "fly.ap.named_tab",
        open_layer_tab=lambda *a, **k: calls.append((a, k)),
    )
    tool = load(4)
    monkeypatch.setattr(tool, "monotonic", lambda: clock[0])
    assert tool.run() == 2
    assert clock[0] == 3
    assert calls[0][1]["deadline"] == 7
