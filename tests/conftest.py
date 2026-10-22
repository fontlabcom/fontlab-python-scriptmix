# this_file: tests/conftest.py
"""Resolve helper sources without importing FontLab or Qt binaries."""

import os
from importlib.metadata import distribution
from pathlib import Path

import pytest


def original_source(root: Path, relative: str) -> Path:
    """Resolve an opt-in byte audit; absent external sources skip only that audit."""
    import json

    archive = os.environ.get("FONTLAB_PRESERVED_ROOT")
    if archive:
        records = json.loads((Path(__file__).parents[1] / "rescue-index.json").read_text())
        record = records["preserved_sources"].get(relative)
        assert record is not None, f"No historical source record: {relative}"
        current = Path(archive) / record["path"]
    else:
        current = root / relative
        if not current.is_file():
            current = root / relative.replace("/_old/", "/rescued/", 1)
    source_folder = Path(*current.parts[:current.parts.index("rescued") + 1]) if "rescued" in current.parts else current.parent
    if not source_folder.is_dir():
        pytest.skip(f"External historical sources absent: {source_folder}; restore the archive for this opt-in byte audit")
    assert current.is_file(), f"Missing requested original: {current}"
    return current


def pytest_addoption(parser):
    parser.addoption(
        "--original-source-root",
        type=Path,
        default=None,
        help="Opt in to original-byte comparisons; absent external source folders skip those audits",
    )

    parser.addoption(
        "--audit-rescued-sources", action="store_true",
        help="Opt in to hashing the external rescued archive (FONTLAB_PRESERVED_ROOT)",
    )


@pytest.fixture(scope="session")
def rescued_source_root(request):
    """Only explicit source-byte audits need an externally restored archive."""
    if not request.config.getoption("--audit-rescued-sources"):
        pytest.skip("External source-byte audit requires --audit-rescued-sources")
    root = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(Path(__file__).parents[1])))
    if not (root / "rescued").is_dir():
        pytest.skip("External rescued/ archive absent; restore it at FONTLAB_PRESERVED_ROOT for the opt-in byte audit")
    return root


def resolve_app_sources(required_helpers=None):
    """Resolve before per-test module doubles replace fontlabapp."""
    override = os.environ.get("SCRIPTMIX_APP_SOURCE")
    root = (
        Path(override)
        if override
        else Path(distribution("fontlab-fontlabapp").locate_file("fontlabapp"))
    )
    required_helpers = required_helpers or (
        "scripting",
        "_font_info_dialog",
        "_features_dialog",
        "feature_code",
        "_names_dialog",
        "_kerning_dialog",
        "kerning_edit",
        "kerning_batch",
        "_kerning_edit_dialog",
        "_kerning_value_dialog",
        "kerning_selection",
        "proof",
        "_proof_dialog",
        "_proof_views",
        "masters",
        "_masters_dialog",
        "_masters_views",
        "inspectors",
        "_inspectors_dialog",
        "_inspectors_views",
        "components",
        "_components_dialog",
        "_components_views",
        "anchors",
        "_anchors_dialog",
        "_anchors_views",
        "unreferenced",
        "interpolation",
        "_review_dialog",
        "_interpolation_view",
        "node_coordinates",
        "master_switcher",
        "_switcher_dialog",
        "guides",
        "_guides_sources",
        "_guides_dialog",
        "_guides_views",
        "guide_records",
        "guide_rewrite",
        "_guide_rewrite_dialog",
        "_guide_editor_dialog",
        "anchor_copy",
        "_anchor_copy_dialog",
        "script_completion",
    )
    for name in required_helpers:
        assert (root / f"{name}.py").is_file(), f"Missing App helper: {root / name}"
    return root


@pytest.fixture(scope="session")
def app_sources():
    """Load the real host-free completion helper before replacing package namespaces."""
    import importlib
    import importlib.util
    import sys

    root = resolve_app_sources()
    importlib.import_module("fontlabapp")
    name = "fontlabapp.script_completion"
    spec = importlib.util.spec_from_file_location(name, root / "script_completion.py")
    module = importlib.util.module_from_spec(spec)
    with pytest.MonkeyPatch.context() as patch:
        patch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        yield root


def app_names_used(paths) -> dict[str, set[str]]:
    """Return ``{"fly.ap.<module>": {names}}`` for every App name the scripts use.

    Count both import forms: ``from fly.ap.x import name`` and
    ``import fly.ap.x as alias`` followed by ``alias.name``.
    """
    import ast

    found: dict[str, set[str]] = {}
    for path in paths:
        tree = ast.parse(Path(path).read_text())
        aliases: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("fly.ap."):
                found.setdefault(node.module, set()).update(a.name for a in node.names)
            elif isinstance(node, ast.Import):
                for item in node.names:
                    if item.name.startswith("fly.ap.") and item.asname:
                        aliases[item.asname] = item.name
                        found.setdefault(item.name, set())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                found[aliases[node.value.id]].add(node.attr)
    return found


def check_real_app_names(used: dict[str, set[str]]) -> None:
    """Import the real Fly and the installed App, with no fakes; check every name.

    Each ``fly.ap.<module>`` must be the very ``fontlabapp.<module>`` object
    from the installed App (or ``SCRIPTMIX_APP_SOURCE``), and must have every
    name in ``used``. Fly comes from the environment (``PYTHONPATH`` or an
    installed wheel). All ``fly`` and ``fontlabapp`` modules are restored after.
    """
    import importlib
    import importlib.util
    import sys

    app_root = resolve_app_sources()
    roots = {"fly", "fontlabapp"}
    saved = {k: v for k, v in sys.modules.items() if k.split(".")[0] in roots}
    for key in saved:
        del sys.modules[key]
    try:
        assert importlib.util.find_spec("fly") is not None, (
            "Put Fly on PYTHONPATH or install it to check the real App names"
        )
        fly = importlib.import_module("fly")
        assert fly.ALIASES["ap"] == "fontlabapp"
        for module_name, wanted in used.items():
            module = importlib.import_module(module_name)
            canonical = "fontlabapp." + module_name.removeprefix("fly.ap.")
            assert module is sys.modules[canonical], module_name
            assert Path(module.__file__).resolve().is_relative_to(app_root.resolve()), (
                module_name,
                module.__file__,
            )
            for attribute in wanted:
                assert hasattr(module, attribute), f"{module_name}.{attribute}"
    finally:
        for key in [k for k in sys.modules if k.split(".")[0] in roots]:
            del sys.modules[key]
        sys.modules.update(saved)


@pytest.fixture
def real_app(monkeypatch):
    """Load the real installed App helpers over owned FontLab and Qt fakes.

    Scripts reach shared code as ``fly.ap.<module>``. This fixture returns
    ``load(qt=..., fontlab=..., scripting={...}, completion=..., modules=[...])``.
    ``load`` imports fresh ``fontlabapp`` submodules after it registers the
    fakes as ``PythonQt`` and ``fontlab``, so App modules that bind Qt or
    scripting names at import see the fakes. ``scripting`` replaces named
    ``fontlabapp.scripting`` functions (font and selection access, panel
    lifecycle). Each loaded module is also registered as ``fly.ap.<module>``,
    the same object, as Fly does. It returns ``{name: module}``.

    After the test, every ``fontlabapp`` submodule and package attribute is
    restored exactly, so other tests see the App as before.
    """
    import importlib
    import sys

    package = importlib.import_module("fontlabapp")
    saved = {k: v for k, v in sys.modules.items() if k.startswith("fontlabapp.")}
    attributes = dict(vars(package))

    def load(*, qt, fontlab, scripting=None, completion=None, modules=()):
        for key in [k for k in sys.modules if k.startswith("fontlabapp.")]:
            del sys.modules[key]
        monkeypatch.setitem(sys.modules, "PythonQt", qt)
        monkeypatch.setitem(sys.modules, "fontlab", fontlab)
        shared = importlib.import_module("fontlabapp.scripting")
        for name, value in (scripting or {}).items():
            assert hasattr(shared, name), f"fontlabapp.scripting has no {name}"
            setattr(shared, name, value)
        helper = importlib.import_module("fontlabapp.script_completion")
        if completion is not None:
            helper.install = completion
        loaded = {"scripting": shared, "script_completion": helper}
        for name in modules:
            loaded[name] = importlib.import_module(f"fontlabapp.{name}")
        for name, module in loaded.items():
            monkeypatch.setitem(sys.modules, f"fly.ap.{name}", module)
        return loaded

    yield load
    for key in [k for k in sys.modules if k.startswith("fontlabapp.")]:
        del sys.modules[key]
    sys.modules.update(saved)
    for key in [k for k in vars(package) if k not in attributes]:
        delattr(package, key)
    for key, value in attributes.items():
        setattr(package, key, value)
