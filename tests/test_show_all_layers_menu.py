# this_file: tests/test_show_all_layers_menu.py
"""Real Fly/App layer-aware proof route, no reference-source execution."""

import runpy
import sys
from pathlib import Path
from types import ModuleType


def test_menu_uses_complete_shared_proof_only_when_invoked(monkeypatch):
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.show_all_layers"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    sys.modules["fly.ap.show_all_layers"].run = lambda: calls.append("layer-proof")
    path = Path(__file__).parents[1] / "Scripts/Proof/Show All Layers.py"
    menu = runpy.run_path(str(path), run_name="inspect")
    assert not calls
    menu["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == ["layer-proof", "layer-proof"]
