# this_file: tests/test_issue122_G3.py
# SPDX-License-Identifier: Apache-2.0
"""Check prose proof generation and lazy FontLab dispatch without a native host."""

import ast
import importlib.util
import inspect
import runpy
import sys
from importlib.metadata import distribution
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Real English Text", "Real Spanish Text")
PATHS = [ROOT / "Scripts" / "Proof" / f"{title}.py" for title in TITLES]


def load(title: str) -> ModuleType:
    """Load one menu without running its entry point."""
    spec = importlib.util.spec_from_file_location(
        "prose_proof", ROOT / "Scripts" / "Proof" / f"{title}.py"
    )
    assert spec is not None and spec.loader is not None, "Menu needs a loader"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    """Provide only the two App APIs allowed for this read-only action."""
    state = SimpleNamespace(package=SimpleNamespace(id=37), calls=[], failure=None)
    for name in ("fly", "fly.ap", "fly.ap.scripting", "fly.ap.text_tab"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)

    def open_tab(text: str, *, expected_id: int) -> None:
        state.calls.append((text, expected_id))
        if state.failure is not None:
            raise state.failure
        if state.package is None or expected_id != state.package.id:
            raise ValueError("The source font changed or closed")

    sys.modules["fly.ap.scripting"].current_package = lambda: state.package
    sys.modules["fly.ap.text_tab"].open_text_tab = open_tab
    return state


@pytest.mark.parametrize("title", TITLES)
def test_five_draws_when_sampled_then_no_replacement_and_exact_trailing_space(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    calls = []

    def sample(pool: tuple[str, ...], count: int) -> list[str]:
        calls.append((pool, count))
        return list(pool[:count])

    monkeypatch.setattr(module.random, "sample", sample)
    assert module.proof_text() == " ".join(module.PASSAGES[:5]) + " "
    assert calls == [(module.PASSAGES, 5)], "Sample five passages without replacement"


@pytest.mark.parametrize("title", TITLES)
def test_draw_order_when_sampled_then_no_case_or_punctuation_loss(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    selected = [module.PASSAGES[i] for i in (7, 3, 19, 0, 11)]
    monkeypatch.setattr(module.random, "sample", lambda pool, count: selected)
    assert module.proof_text() == " ".join(selected) + " "


@pytest.mark.parametrize("title", TITLES)
def test_real_sample_when_generated_then_five_distinct_passages(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    monkeypatch.setattr(module, "PASSAGES", tuple(f"passage{i}" for i in range(24)))
    # Fix the seed on a private generator; do not change global random state.
    monkeypatch.setattr(module.random, "sample", module.random.Random(83).sample)
    words = module.proof_text().split()
    assert len(words) == len(set(words)) == 5, "One proof must never repeat a passage"


@pytest.mark.parametrize("title", TITLES)
def test_menu_when_run_twice_then_two_new_tabs_bound_to_source(
    title: str, host: Any
) -> None:
    module = load(title)
    assert host.calls == [], "Import must perform no native work"
    module.main()
    module.main()
    assert len(host.calls) == 2, "Each menu action opens one tab"
    for text, package_id in host.calls:
        assert package_id == 37 and text.endswith(" "), "Keep source and final space"


@pytest.mark.parametrize("title", TITLES)
def test_run_when_no_font_then_no_draw_or_tab(
    title: str, host: Any, monkeypatch: Any, capsys: Any
) -> None:
    module = load(title)
    host.package = None

    def unexpected(pool: tuple[str, ...], count: int) -> list[str]:
        pytest.fail("No font must refuse before random draws")

    monkeypatch.setattr(module.random, "sample", unexpected)
    module.main()
    assert "Open a font" in capsys.readouterr().out
    assert host.calls == [], "Refusal must open no tab"


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("error_type", [ValueError, RuntimeError, TimeoutError])
def test_main_when_tab_fails_then_one_attempt_and_visible_error(
    title: str, error_type: type[Exception], host: Any, capsys: Any
) -> None:
    host.failure = error_type("Proof could not open")
    load(title).main()
    assert f"{title}: Proof could not open" in capsys.readouterr().out
    assert len(host.calls) == 1, "Never retry native tab creation"


@pytest.mark.parametrize("title", TITLES)
def test_run_when_font_changes_during_generation_then_captured_id_is_used(
    title: str, host: Any, monkeypatch: Any
) -> None:
    module = load(title)

    def generate() -> str:
        host.package = SimpleNamespace(id=99)
        return "Bound proof. "

    monkeypatch.setattr(module, "proof_text", generate)
    with pytest.raises(ValueError, match="source font changed"):
        module.run()
    assert host.calls == [("Bound proof. ", 37)], "Do not bind to the replacement font"


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("bad", ["\0", "\u00a0", "\u2028", "\u2029"])
def test_proof_when_corpus_has_lossy_character_then_refused_before_tab(
    title: str, bad: str, host: Any, monkeypatch: Any
) -> None:
    module = load(title)
    monkeypatch.setattr(module, "PASSAGES", ("Safe text.", "Bad" + bad + "text."))
    with pytest.raises(ValueError, match="Unsupported proof character"):
        module.run()
    assert host.calls == [], "Check the whole corpus before sampling"


@pytest.mark.parametrize("title", TITLES)
def test_proof_when_empty_corpus_then_clear_refusal(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    monkeypatch.setattr(module, "PASSAGES", ())
    with pytest.raises(ValueError, match="No proof passages"):
        module.proof_text()


@pytest.mark.parametrize("title", TITLES)
def test_corpus_when_loaded_then_varied_original_prose_and_python311(title: str) -> None:
    module = load(title)
    assert len(module.PASSAGES) == len(set(module.PASSAGES)) == 24
    assert all(len(text) >= 60 for text in module.PASSAGES), "Use connected prose"
    joined = " ".join(module.PASSAGES)
    assert any(c.isdigit() for c in joined), "Include figures"
    if title == "Real Spanish Text":
        assert set("áéíóúüñ¿¡«»") <= set(joined), "Include Spanish proof characters"
        assert "sólo" not in joined and "solo habían cambiado" in joined
    path = ROOT / "Scripts" / "Proof" / f"{title}.py"
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert not any(isinstance(node, ast.ClassDef) for node in tree.body), "Use native tab UI"
    assert "Independent" in ast.get_docstring(tree)


@pytest.mark.parametrize("title", TITLES)
def test_main_guard_when_executed_then_opens_one_tab(title: str, host: Any) -> None:
    runpy.run_path(str(ROOT / "Scripts" / "Proof" / f"{title}.py"), run_name="__main__")
    assert len(host.calls) == 1


def test_real_app_names_when_imported_from_installed_app_then_all_exist() -> None:
    """Import actual App APIs with the same Fly route used by the menus.

    The App is the one the gate installs; no App-source override (G1 form).
    """
    app_src = Path(distribution("fontlab-fontlabapp").locate_file("fontlabapp"))
    used = app_names_used(PATHS)
    assert used == {
        "fly.ap.scripting": {"current_package"},
        "fly.ap.text_tab": {"open_text_tab"},
    }, "Use public shared helpers for all native work"
    check_real_app_names(used)
    saved = {k: v for k, v in sys.modules.items() if k.split(".")[0] in {"fly", "fontlabapp"}}
    for name in saved:
        del sys.modules[name]
    try:
        real_tabs = importlib.import_module("fly.ap.text_tab")
        assert Path(real_tabs.__file__).resolve().is_relative_to(app_src.resolve())
        signature = inspect.signature(real_tabs.open_text_tab)
        assert "expected_id" in signature.parameters, "Real App needs expected_id"
        bound = signature.bind("Proof text.", expected_id=37)
        assert bound.arguments["expected_id"] == 37, "App must accept the keyword"
    finally:
        for name in list(sys.modules):
            if name.split(".")[0] in {"fly", "fontlabapp"}:
                del sys.modules[name]
        sys.modules.update(saved)
