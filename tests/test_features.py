# this_file: tests/test_features.py
"""Independent checks for the six complete feature tools and safe writes."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
TITLES = [
    "Alternate Preview",
    "Build Suffix Substitution",
    "Classes Browser",
    "Feature Code Viewer",
    "Ligature Finder",
    "Suffix Report",
]


@pytest.mark.parametrize("title", TITLES)
def test_requested_tool_exists(title):
    assert (ROOT / "Scripts/Features" / (title + ".py")).is_file(), (
        "Requested complete feature tool missing"
    )


import importlib.util
import os
import sys
from importlib.metadata import PackageNotFoundError, distribution
from types import SimpleNamespace as NS


def fontport_sources() -> Path:
    """Locate the installed Fontport package. Feature source helpers live there.

    ``SCRIPTMIX_FONTPORT_SOURCE`` overrides the installed distribution. Supply
    Fontport to ``test.sh`` with ``SCRIPTMIX_EXTRA_REQUIREMENTS``.
    """
    override = os.environ.get("SCRIPTMIX_FONTPORT_SOURCE")
    if override:
        return Path(override)
    try:
        located = distribution("fontlab-fontport").locate_file("fontlab_fontport")
    except PackageNotFoundError:
        pytest.fail(
            "Fontport is missing: set SCRIPTMIX_EXTRA_REQUIREMENTS to a Fontport "
            "wheel or checkout (fly.fp.feature_blocks)"
        )
    return Path(located)


@pytest.fixture
def load(monkeypatch, app_sources):
    state = NS(
        package=None,
        names=[],
        blocks={"prefix": "languagesystem DFLT dflt;\n", "features": []},
        writes=[],
        failure=None,
    )
    native = NS(CurrentFont=lambda: NS(glyphs=[NS(name=n) for n in state.names]))
    qt = NS(QtCore=NS(), QtGui=NS(QDialog=object, QWidget=object))
    app = NS(_native=lambda name: native if name == "fontlab" else qt)
    monkeypatch.setitem(sys.modules, "fontlabapp", app)
    monkeypatch.setitem(sys.modules, "fontlab", native)
    spec = importlib.util.spec_from_file_location(
        "fontlabapp.scripting",
        app_sources / "scripting.py",
    )
    scripting = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fontlabapp.scripting", scripting)
    spec.loader.exec_module(scripting)
    # Fontport calls App through the module object ``fontlabapp.scripting``.
    app.scripting = scripting
    monkeypatch.setattr(
        scripting,
        "current_package",
        lambda expected_id=None: (
            state.package
            if expected_id is None
            or (state.package and state.package.id == expected_id)
            else None
        ),
    )

    class Backend:
        def __init__(self, font_id):
            assert state.package and font_id == state.package.fgId

        def get_feature_blocks(self):
            return {
                "prefix": state.blocks["prefix"],
                "features": list(state.blocks["features"]),
            }

        def set_feature_blocks(self, values, *, undo_name):
            state.writes.append((values, undo_name))
            if state.failure:
                raise state.failure
            state.blocks = values

    monkeypatch.setitem(
        sys.modules, "fontlab_fontport.host", NS(NativeFontBackend=Backend)
    )
    for leaf in ("_font_info_dialog", "_features_dialog"):
        spec = importlib.util.spec_from_file_location(
            "fontlabapp." + leaf,
            app_sources / (leaf + ".py"),
        )
        shared = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, "fontlabapp." + leaf, shared)
        spec.loader.exec_module(shared)
    # The real Fontport module, loaded under its canonical name so that its
    # relative ``from .host import NativeFontBackend`` finds the Backend double.
    spec = importlib.util.spec_from_file_location(
        "fontlab_fontport.feature_blocks",
        fontport_sources() / "feature_blocks.py",
    )
    blocks = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fontlab_fontport.feature_blocks", blocks)
    spec.loader.exec_module(blocks)
    monkeypatch.setitem(sys.modules, "fly", NS(ap=NS(fontlab=native), qt=qt))
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", scripting)
    # A Fly alias is the canonical module object itself.
    monkeypatch.setitem(sys.modules, "fly.fp.feature_blocks", blocks)
    spec = importlib.util.spec_from_file_location(
        "fly.ap.feature_code",
        app_sources / "feature_code.py",
    )
    calculations = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "fly.ap.feature_code", calculations)
    spec.loader.exec_module(calculations)

    def module(title):
        spec = importlib.util.spec_from_file_location(
            title, ROOT / "Scripts/Features" / (title + ".py")
        )
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result

    return module, state, blocks


def test_independent_feature_calculations(load):
    module, _, _ = load
    build = module(TITLES[1])
    names = ["z", "z.sc", "A", "A.sc", "bad name", "bad name.sc", "missing.sc", "A.sc"]
    assert build.suffix_pairs(names, ".sc") == [("A", "A.sc"), ("z", "z.sc")]
    assert build.suffix_pairs(names, "") == []
    assert build.safe_name(".notdef") and build.safe_name("a-b.alt")
    assert not build.safe_name("a; sub x by y")
    assert module(TITLES[0]).run(set(names), "A") == ["A", "A.sc"]
    ligature = module(TITLES[4])
    rows = ligature.run(["f", "i", "f_i", "f_i.sc", "f.sc", "i.sc", "x_y", "f__i"])
    assert rows == [
        ("f__i", "f  i", "Missing / invalid input: (empty)"),
        ("f_i", "f i", "Ready"),
        ("f_i.sc", "f.sc i.sc", "Ready"),
        ("x_y", "x y", "Missing / invalid input: x, y"),
    ]
    assert (
        ligature.liga_text(rows)
        == "feature liga {\n    sub f i by f_i;\n    sub f.sc i.sc by f_i.sc;\n} liga;"
    )
    suffix = module(TITLES[5])
    assert suffix.run(["a", "a.sc", "b.sc", "a.ss20", ".notdef"]) == [
        ("sc", 2, 1, "smcp"),
        ("ss20", 1, 1, "ss20"),
    ]
    assert suffix.suggested_tag("loclPLK") == "locl"
    assert suffix.suggested_tag("ss00") == "salt"


@pytest.mark.parametrize("tag", ["", "liga;", "äalt", "abc", "a_bc"])
def test_invalid_tag_refused(load, tag):
    module, _, _ = load
    with pytest.raises(ValueError, match="four ASCII"):
        module(TITLES[1]).feature_text(tag, [("a", "a.sc")])


def test_append_preserves_existing_and_rejects_conflicts(load):
    module, _, _ = load
    build = module(TITLES[1])
    old = "feature smcp {\n # sub a by ignored;\n    sub b by b.sc;\n} smcp;\n"
    assert (
        build.append_code(old, "smcp", [("a", "a.sc")])
        == "feature smcp {\n # sub a by ignored;\n    sub b by b.sc;\n    sub a by a.sc;\n} smcp;\n"
    )
    with pytest.raises(ValueError, match="already substitutes"):
        build.append_code(old, "smcp", [("b", "b.sc")])
    with pytest.raises(ValueError, match="closing"):
        build.append_code("lookup x {} x;", "smcp", [("a", "a.sc")])
    with pytest.raises(ValueError, match="No valid"):
        build.append_code("", "smcp", [])


@pytest.mark.parametrize("title", [TITLES[1], TITLES[3]])
def test_feature_scripts_read_and_write_source_through_fly_fp(load, title):
    module, _, blocks = load
    tool = module(title)
    assert blocks.__name__ == "fontlab_fontport.feature_blocks"
    assert tool.read_feature_blocks is blocks.read_feature_blocks, (
        "Feature scripts must read source through fly.fp.feature_blocks"
    )
    if title == TITLES[1]:
        assert tool.write_feature_blocks is blocks.write_feature_blocks, (
            "Build Suffix Substitution must write through fly.fp.feature_blocks"
        )


def test_shared_writer_reuses_backend_preserves_blocks_and_noop(load):
    _, state, blocks = load
    state.package = NS(id=11, fgId=101, master="Regular")
    state.names = ["a", "a.sc"]
    old = {
        "prefix": "languagesystem DFLT dflt;\n",
        "features": [("liga", "feature liga {} liga;\n")],
    }
    state.blocks = old
    new = {
        "prefix": old["prefix"],
        "features": old["features"]
        + [("smcp", "feature smcp { sub a by a.sc; } smcp;")],
    }
    assert blocks.write_feature_blocks(
        state.package, old, new, references=["a", "a.sc"], undo_name="Build"
    ) == {"changed": 1}
    assert state.writes == [(new, "Build")]
    assert blocks.write_feature_blocks(
        state.package, new, new, references=[], undo_name="Build"
    ) == {"changed": 0}
    assert len(state.writes) == 1


@pytest.mark.parametrize("failure", ["font", "source", "reference"])
def test_shared_writer_stale_preflight_does_not_write(load, failure):
    _, state, blocks = load
    package = NS(id=11, fgId=101, master="Regular")
    state.package = package if failure != "font" else NS(id=12)
    state.names = ["a"]
    expected = {"prefix": "languagesystem DFLT dflt;\n", "features": []}
    state.blocks = (
        expected if failure != "source" else {"prefix": "changed", "features": []}
    )
    with pytest.raises(ValueError):
        blocks.write_feature_blocks(
            package,
            expected,
            {"prefix": expected["prefix"], "features": [("smcp", "new")]},
            references=["a.sc"] if failure == "reference" else ["a"],
            undo_name="Build",
        )
    assert not state.writes


def test_shared_writer_reports_partial_failure(load):
    _, state, blocks = load
    state.package = NS(id=11, fgId=101, master="Regular")
    state.failure = RuntimeError("native assignment failed")
    expected = state.blocks
    with pytest.raises(RuntimeError, match="may be partial"):
        blocks.write_feature_blocks(
            state.package,
            expected,
            {"prefix": expected["prefix"], "features": [("smcp", "new")]},
            references=[],
            undo_name="Build",
        )


@pytest.mark.parametrize("pairs", [[("a", "a.sc"), ("a", "a.alt")], [("a;", "a.sc")]])
def test_invalid_or_duplicate_pairs_refused(load, pairs):
    module, _, _ = load
    with pytest.raises(ValueError):
        module(TITLES[1]).feature_text("smcp", pairs)


def test_existing_source_whitespace_and_run_order_preserved(load):
    module, state, _ = load
    build = module(TITLES[1])
    old = "feature smcp {\n    # keep whitespace  \n  \n} smcp;\n\n"
    new = build.append_code(old, "smcp", [("a", "a.sc")])
    assert new == old.replace("} smcp;", "    sub a by a.sc;\n} smcp;")
    state.package = NS(id=11, fgId=101, master="Regular")
    state.names = ["a", "a.sc"]
    state.blocks = {
        "prefix": "languagesystem DFLT dflt;\n",
        "features": [("smcp", old), ("liga", "unrelated")],
    }
    build.run(
        state.package,
        None,
        "smcp",
        old,
        new,
        expected_blocks=state.blocks,
        references=["a", "a.sc"],
    )
    assert state.blocks["features"] == [("smcp", new), ("liga", "unrelated")]
    assert state.blocks["prefix"] == "languagesystem DFLT dflt;\n"


def test_feature_preview_failure_invalidates_apply_and_copy(load):
    module, state, _ = load
    tool = module(TITLES[1])
    dialog = object.__new__(tool.Dialog)
    enabled, statuses = [], []
    dialog.status = NS(setText=statuses.append)
    dialog.apply_button = NS(setEnabled=enabled.append)
    dialog._preview_valid = dialog._copy_preview_valid = True
    dialog.safe(lambda: (_ for _ in ()).throw(RuntimeError("owned preview failure")))
    assert dialog._preview_valid is dialog._copy_preview_valid is False
    assert enabled == [False] and statuses == ["owned preview failure"]
    with pytest.raises(ValueError):
        dialog.apply()
    assert not state.writes


def test_readonly_original_class_and_source_calculations(load):
    module, _, _ = load

    class Groups(dict):
        def getAsClassRecords(self):
            return ["Uppercase:A' B", "kernLeft:A B", "Empty:"]

    groups = Groups(
        Uppercase=NS(isFeaGroup=lambda: True),
        kernLeft=NS(isFeaGroup=lambda: False),
        Empty=NS(isFeaGroup=lambda: True),
    )
    assert module(TITLES[2]).run(groups) == [("Empty", 0, ""), ("Uppercase", 2, "A B")]

    assert module(TITLES[3]).run(
        iter([("smcp", "# Å feature"), ("liga", "sub f i by f_i;")])
    ) == [
        ("smcp", "# Å feature"),
        ("liga", "sub f i by f_i;"),
    ]


def test_copy_uses_owned_clipboard_double_and_original_receipt(load):
    module, state, _ = load
    tool = module(TITLES[5])
    state.package = NS(id=11, fgId=101)
    copied, statuses = [], []
    tool.QtGui.QApplication = NS(clipboard=lambda: NS(setText=copied.append))
    dialog = object.__new__(tool.Dialog)
    dialog.package_id = 11
    dialog._preview_valid = True
    dialog.status = NS(setText=statuses.append)
    dialog.snippet = "feature smcp {\n sub a by a.sc;\n} smcp;"
    dialog.apply()
    assert copied == [dialog.snippet]
    assert dialog.last_result == {"copied": dialog.snippet}


def test_proof_painter_contains_errors_and_always_ends(load):
    module, _, _ = load
    tool = module(TITLES[0])
    events, statuses = [], []
    tool.QtGui.QPainter = lambda widget: NS(
        setRenderHint=lambda flag: None, end=lambda: events.append("end")
    )
    # QPainter's enum is an attribute of its constructor in native PythonQt.
    tool.QtGui.QPainter.Antialiasing = 1
    proof = object.__new__(tool.Proof)
    proof.owner = NS(status=NS(setText=statuses.append))
    proof.draw_proof = lambda painter: (_ for _ in ()).throw(
        ValueError("owned paint failure")
    )
    proof.paintEvent(None)
    assert proof._error == "owned paint failure"
    assert statuses == ["Proof error: owned paint failure"] and events == ["end"]


def test_suffix_consumers_use_same_actual_shared_calculations(load):
    module, _, _ = load
    build, report = module(TITLES[1]), module(TITLES[5])
    shared = sys.modules["fly.ap.feature_code"]
    assert build.suffix_pairs is report.suffix_pairs is shared.suffix_pairs
    assert build.feature_text is report.feature_text is shared.feature_text
    assert build.safe_name is module(TITLES[4]).safe_name is shared.safe_name


def test_viewer_uses_exact_ordered_feature_snapshot(load):
    module, state, _ = load
    viewer = module(TITLES[3])
    state.package = NS(id=11, fgId=101)
    state.blocks = {
        "prefix": "languagesystem DFLT dflt;\n# exact prefix\n",
        "features": [
            ("smcp", "feature smcp { sub a by a.sc; } smcp;\n"),
            ("liga", "feature liga { sub f i by f_i; } liga;\n"),
        ],
    }

    class BrokenNativeLayout:
        def __iter__(self):
            return iter([0, 1])

        def get_feature(self, raw):
            return ""

        def get_prefix(self):
            return "@Uppercase = [synthesized];"

    class Control:
        def __init__(self, *args):
            self.currentIndexChanged = self.textChanged = None

        def __getattr__(self, name):
            return lambda *args: None

    viewer.QtGui.QComboBox = viewer.QtGui.QLineEdit = viewer.QtGui.QTextEdit = Control
    dialog = object.__new__(viewer.Dialog)
    dialog.package = state.package

    def prepare():
        dialog.font_data = NS(features=BrokenNativeLayout())
        return NS(addWidget=lambda *args: None)

    dialog.prepare = prepare
    dialog.apply_button = Control()
    dialog._connect = lambda *args: None
    dialog.setup()
    assert dialog.sources == [
        ("Prefix / languagesystems", state.blocks["prefix"]),
        *state.blocks["features"],
    ], (
        "Viewer must not interpret native iterator positions as feature tags or synthesize raw prefix classes"
    )
