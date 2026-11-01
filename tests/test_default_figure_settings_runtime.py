# this_file: tests/test_default_figure_settings_runtime.py
"""Real settings round trips use isolated INI files and fresh child processes."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("family", range(4))
def test_family_when_saved_then_fresh_process_restores_owned_ini(tmp_path, family):
    binding = "PyQt5" if os.environ.get("FONTLABAPP_TEST_QT5") else "PySide6"
    pytest.importorskip(binding + ".QtCore")
    path = tmp_path / "figures.ini"
    program = """
import importlib,json,runpy,sys
C=importlib.import_module(sys.argv[1]+'.QtCore')
menu=runpy.run_path(sys.argv[2])
settings=C.QSettings(sys.argv[3],C.QSettings.IniFormat)
if len(sys.argv)>4:
    assert menu['load_family'](settings)==0
    settings.setValue('unrelated','keep')
    menu['save_family'](settings,int(sys.argv[4]))
else:
    print(json.dumps({'family':menu['load_family'](settings),'unrelated':settings.value('unrelated'),'keys':sorted(settings.allKeys()),'fallbacks':settings.fallbacksEnabled()}))
"""
    command = [
        sys.executable,
        "-B",
        "-c",
        program,
        binding,
        str(ROOT / "Scripts/Components/Set Default Figures.py"),
        str(path),
    ]
    subprocess.run(
        [*command, str(family)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        timeout=20,
    )
    before = path.read_bytes()
    result = subprocess.run(
        command, check=True, stdout=subprocess.PIPE, text=True, timeout=20
    )
    assert json.loads(result.stdout) == {
        "family": family,
        "unrelated": "keep",
        "keys": ["optionFigures", "unrelated"],
        "fallbacks": False,
    }
    assert path.read_bytes() == before, (
        "Restoration does not rewrite the owned INI file"
    )
