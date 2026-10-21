# this_file: tests/test_background_clear_menu.py
"""Both full-font scopes dispatch to shared App without importing native APIs."""
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as S
import pytest
ROOT=Path(__file__).parents[1]


@pytest.mark.parametrize('title,method',[('Clear All Layer Backgrounds','show_all'),('Clear Master Backgrounds','show_masters')])
def test_complete_scope_dispatch_and_original_pins(monkeypatch,title,method):
    calls=[]
    monkeypatch.setitem(sys.modules,'fly.ap.background_clear',S(**{method:lambda:calls.append(method) or 'owned'}))
    destination=f'Scripts/Cleaning/{title}.py'
    module=runpy.run_path(str(ROOT/destination));assert not calls
    assert module['main']()=='owned'
    runpy.run_path(str(ROOT/destination),run_name='__main__')
    assert calls==[method,method]
    row=next(row for row in json.loads((ROOT/'additional-tools.json').read_text()) if row['destination']==destination)
    assert row['destination_sha256']==hashlib.sha256((ROOT/destination).read_bytes()).hexdigest()
    assert row['app_minimum']=='0.2.150.dev0'
    assert row['native_acceptance']=='pending' and row['counted_in_130_sample_migration'] is False
    assert row['source_sha256'] in {'efdddf6895ee001bb96e9a744a62b4cc31bb7d8f28045b367df7d6bc42d4c0d0','f4664b72409bf7a0a198dc0cc3c708f179415021b42bcbbd974ca9d5c8bad73a'}
