# this_file: tests/test_issue122_C5.py
"""Backup names and legacy discovery; installed-App import checks."""

import ast
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from conftest import app_names_used, check_real_app_names

ROOT = Path(__file__).parents[1]
TOOLS = [
    "Masters/Duplicate Current Layer",
    "Masters/Copy Layer Between Masters",
    "Masters/Restore Backup Layer",
    "Contours/Round Coordinates",
    "Masters/Display Next Layer",
    "Masters/Display Previous Layer",
    "Masters/Layer Cleanup",
]


def load(title: str) -> ModuleType:
    relative = title if "/" in title else next(name for name in TOOLS if name.endswith("/" + title))
    spec = importlib.util.spec_from_file_location("c5_" + title.replace(" ", "_"),
                                               ROOT / "Scripts" / f"{relative}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("base,suffix", [("Regular", "@ old"), ("Regular", "# old"),
                                         ("|temp|Regular", " backup"), ("Regular", "draft |temp| note"), ("Regular", "")])
def test_new_backup_name_when_reserved_or_empty_then_refused(base: str, suffix: str) -> None:
    module = load("Duplicate Current Layer")
    with pytest.raises(ValueError):
        module.backup_name(base, [], suffix, [base])


def test_backup_name_when_plain_suffix_taken_then_case_insensitive_numbering() -> None:
    module = load("Duplicate Current Layer")
    assert module.backup_name("Light", ["LIGHT backup before", "Light backup before (2)"], "before", ["Light"]) == "Light backup before (3)"


@pytest.mark.parametrize("name,expected", [("Light backup", "Light"), ("Light Text backup", "Light Text"),
                                           ("Light", None), ("Light#alt", None),
                                           ("|temp|Light backup", None), ("Light Other@ old", None)])
def test_legacy_backup_discovery_when_space_prefix_then_longest_master(name: str, expected: str | None) -> None:
    module = load("Restore Backup Layer")
    assert module.backup_master(name, ["Light", "Light Text"]) == expected


def test_all_used_app_names_when_imported_from_installed_distribution_then_exist() -> None:
    check_real_app_names(app_names_used([ROOT / "Scripts" / f"{name}.py" for name in TOOLS]))


@pytest.mark.parametrize("suffix", ["Italic", "Italic draft"])
def test_new_backup_when_master_names_overlap_then_resolves_to_own_master(suffix: str) -> None:
    duplicate = load("Duplicate Current Layer")
    restore = load("Restore Backup Layer")
    masters = ["Light", "Light Italic"]
    name = duplicate.backup_name("Light", [], suffix, masters)
    assert name == f"Light backup {suffix}"
    assert name not in masters and restore.backup_master(name, masters) == "Light"


@pytest.mark.parametrize("masters,message", [(["Light", "Light backup Italic"], "master name"),
                                            (["Light", "Light backup"], "read as master")])
def test_new_backup_when_candidate_is_master_or_wrong_prefix_then_refused(masters: list[str], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        load("Duplicate Current Layer").backup_name("Light", [], "Italic", masters)


@pytest.mark.parametrize("title", ["Display Next Layer", "Display Previous Layer"])
def test_navigation_when_new_and_legacy_backups_then_all_in_own_cycle(title: str) -> None:
    module = load(title)
    names = ["Light", "Light backup Italic", "Light old", "Light@ old", "Light Italic", "Light Italic backup draft"]
    cycle = module.layer_cycle([(name, True) for name in names], "Light", ["Light", "Light Italic"])
    assert cycle == names[:4]
    assert module.pick_layer(cycle, "Light", module.STEP) == cycle[module.STEP]


@pytest.mark.parametrize("name", ["Light backup Italic", "Light old", "Light@ old"])
def test_cleanup_when_new_or_legacy_backup_then_classified_as_backup(name: str) -> None:
    layer = SimpleNamespace(name=name, isMaskLayer=False, isService=False, isImgLayer=False)
    assert load("Layer Cleanup").kind(layer, ["Light", "Light Italic"]) == "backup"


def test_backup_rule_when_copied_between_tools_then_identical_source() -> None:
    bodies = []
    for title in ["Duplicate Current Layer", "Restore Backup Layer", "Display Next Layer", "Display Previous Layer", "Layer Cleanup"]:
        module = load(title)
        tree = ast.parse(Path(module.__file__).read_text())
        helper = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_backup_master")
        bodies.append(ast.dump(helper, include_attributes=False))
    assert len(set(bodies)) == 1, "Companion tools must share one backup-name rule"
