# this_file: tests/test_crossfont_reports.py
"""Two complete report menus dispatch source-distinct profiles through Fly."""
from pathlib import Path
from types import ModuleType
import runpy,sys,json
import pytest
ROOT=Path(__file__).resolve().parents[1]
@pytest.mark.parametrize('title,flag',[('Report Composite Differences',True),('Report Glyph Set Differences',False)])
def test_complete_crossfont_menu_dispatch(monkeypatch,title,flag):
 calls=[];module=ModuleType('fly.ap.crossfont_reports');module.show=lambda **kw:calls.append(kw);monkeypatch.setitem(sys.modules,'fly.ap.crossfont_reports',module)
 runpy.run_path(str(ROOT/'Scripts/Reports'/f'{title}.py'),run_name='__main__');assert calls==[{'composites':flag}]
 row=next(r for r in json.loads((ROOT/'additional-tools.json').read_text()) if r['title']==title);assert row['source_license']=='MIT' and row['native_acceptance']=='pending' and not row['counted_in_130_sample_migration']
