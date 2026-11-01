# this_file: tests/test_context_proof_menus.py
"""Exercise all eight lazy proof menu entrypoints without executing references."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parents[1]
MENUS = (
    ("Glyphs Between Lowercase", "lowercase"),
    ("Glyphs Between Uppercase", "uppercase"),
    ("Glyphs Between Lining Figures", "lining"),
    ("Glyphs Between Oldstyle Figures", "oldstyle"),
    ("Glyphs Surrounded by H", "H"),
    ("Glyphs Surrounded by I", "I"),
    ("Glyphs Surrounded by HHOHH", "HHOHH"),
    ("Glyphs Surrounded by Nnonn", "nnonn"),
)


@pytest.mark.parametrize("title,mode", MENUS)
@pytest.mark.parametrize("failure", [False, True])
def test_menu_defers_all_host_work_and_runs_one_complete_source_mode(
    monkeypatch, title, mode, failure
):
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    module = ModuleType("fly.ap.context_proofs")
    calls = []

    def run(value):
        calls.append(value)
        if failure:
            raise ValueError("owned source failure")

    module.run = run
    monkeypatch.setitem(sys.modules, module.__name__, module)
    path = ROOT / "Scripts/Proof" / f"{title}.py"
    namespace = runpy.run_path(str(path), run_name="inspection")
    assert calls == []
    if failure:
        with pytest.raises(ValueError, match="owned source"):
            namespace["main"]()
    else:
        namespace["main"]()
        assert calls == [mode]
        calls.clear()
        runpy.run_path(str(path), run_name="__main__")
    assert calls == [mode]
    main = next(
        n
        for n in ast.parse(path.read_text(), feature_version=(3, 11)).body
        if isinstance(n, ast.FunctionDef)
    )
    assert main.returns.value is None
