# this_file: tests/test_random_proof_menus.py
"""Check seven complete lazy proof entrypoints and fail-before-tab behavior."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS

import pytest

ROOT = Path(__file__).parents[1]
MENUS = (
    ("Random Numbers", "numbers"),
    ("Random Lowercase Nontext", "lowercase-nontext"),
    ("Random Title Nontext", "title-nontext"),
    ("Random Uppercase Nontext", "uppercase-nontext"),
    ("Random Lowercase Words", "lowercase-words"),
    ("Random Title Words", "title-words"),
    ("Random Uppercase Words", "uppercase-words"),
)


@pytest.fixture
def host(monkeypatch):
    state = NS(font=NS(id=7), calls=[], failure=None)
    for name in ("fly", "fly.ap"):
        mod = ModuleType(name)
        mod.__path__ = []
        monkeypatch.setitem(sys.modules, name, mod)
    for name in ("random_proof", "scripting", "text_tab"):
        monkeypatch.setitem(sys.modules, "fly.ap." + name, ModuleType("fly.ap." + name))

    def generate(mode):
        state.calls.append(("generate", mode))
        if state.failure == "generate":
            raise OSError("owned resource failure")
        return "Aa 🙂 "

    def open_tab(text, *, expected_id):
        state.calls.append(("tab", text, expected_id))
        if state.failure == "tab":
            raise RuntimeError("owned native failure")

    sys.modules["fly.ap.random_proof"].generate = generate
    sys.modules["fly.ap.scripting"].current_package = lambda: state.font
    sys.modules["fly.ap.text_tab"].open_text_tab = open_tab
    return state


@pytest.mark.parametrize("title,mode", MENUS)
def test_lazy_main_and_menu_execution_generate_once_then_open_exact_text(
    host, title, mode
):
    path = ROOT / "Scripts/Proof" / f"{title}.py"
    mod = runpy.run_path(str(path), run_name="inspection")
    assert not host.calls
    mod["main"]()
    assert host.calls == [("generate", mode), ("tab", "Aa 🙂 ", 7)]
    host.calls.clear()
    runpy.run_path(str(path), run_name="__main__")
    assert host.calls == [("generate", mode), ("tab", "Aa 🙂 ", 7)]
    main = next(
        n
        for n in ast.parse(path.read_text(), feature_version=(3, 11)).body
        if isinstance(n, ast.FunctionDef)
    )
    assert main.returns.value is None


@pytest.mark.parametrize("title,mode", MENUS)
@pytest.mark.parametrize("failure", ["no_font", "generate", "tab"])
def test_failure_refuses_generation_or_tab_before_incomplete_text_can_open(
    host, title, mode, failure
):
    host.failure = failure
    if failure == "no_font":
        host.font = None
    main = runpy.run_path(str(ROOT / "Scripts/Proof" / f"{title}.py"))["main"]
    with pytest.raises((ValueError, OSError, RuntimeError)):
        main()
    assert host.calls == (
        []
        if failure == "no_font"
        else [("generate", mode)]
        if failure == "generate"
        else [("generate", mode), ("tab", "Aa 🙂 ", 7)]
    )
