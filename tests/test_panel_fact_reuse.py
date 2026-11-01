# this_file: tests/test_panel_fact_reuse.py
"""Run real planning hooks with changing controls and a forbidden whole-font scan."""

import ast
import importlib.metadata
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest

ROOT = Path(__file__).parents[1]
TOOLS = ["Contours/Shadow Copy", "Contours/Outline Effect", "Contours/Autohint Selected Layers",
         "Contours/Remove PostScript Hints", "Masters/Duplicate Current Layer",
         "Masters/Set Intermediate Layer", "Contours/Tabular Figure Copies"]


@pytest.mark.parametrize("tool", TOOLS)
def test_controls_when_changed_then_planning_reuses_captured_facts(tool: str) -> None:
    source = ROOT / "Scripts" / (tool + ".py")
    tree = ast.parse(source.read_text())
    if tool.endswith("Tabular Figure Copies"):
        # Tabular uses the installed App CopiesPanel hook without an override.
        assert not any(isinstance(n, ast.FunctionDef) and n.name == "plan_rows" for n in ast.walk(tree))
        path = importlib.metadata.distribution("fontlab-fontlabapp").locate_file("fontlabapp/_selection_panel.py")
        tree = ast.parse(Path(path).read_text())
        tree = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "CopiesPanel")
    hook = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "plan_rows")
    hook.decorator_list = []
    captured = object()
    seen = []
    def scan(*args: Any) -> Any:
        pytest.fail("A control change must not scan the whole font")
    def survey(*args: Any) -> list[Any]:
        assert any(arg is captured for arg in args), "Use the panel's captured facts"
        seen.append(args)
        return []
    def refusal(facts: Any, *args: Any) -> str:
        assert facts is captured, "Backup preview must reuse captured facts"
        seen.append(args)
        return ""
    ns = {"survey": survey, "history": NS(scan_auto_facts=scan, refusal=refusal),
          "backup_name": lambda *args: "Regular backup draft", "backups_of": lambda *args: []}
    module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), hook], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), ns)
    layer = NS(name="Regular", isNull=False, autoLayer=False, isMaskLayer=False, isService=False)
    glyph = NS(isNull=False, layers=[layer], findLayer=lambda master: layer)
    package = NS(masters=["Regular"], findName=lambda name: glyph)
    control = NS(value=0)
    panel = NS(facts=captured, names=["A"], suffix=NS(text="draft"),
               axis_controls={"wt": control}, consented=lambda: bool(control.value),
               directions=lambda: (True, bool(control.value)), survey=survey)
    ns["plan_rows"](panel, package, ["Regular"])
    control.value = 1
    ns["plan_rows"](panel, package, ["Regular"])
    assert len(seen) == 2, "Both previews must plan using the captured snapshot"
