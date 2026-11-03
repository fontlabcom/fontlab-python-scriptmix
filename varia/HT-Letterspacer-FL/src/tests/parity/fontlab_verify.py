"""Drive FontLab comparison in bounded native Python calls, on disposable copies."""

from pathlib import Path
import os

PROJECT = Path(__file__).resolve().parents[2]
UPSTREAM = Path(os.environ.get("HTLS_UPSTREAM", PROJECT.parent / "HTLetterspacer"))
OUTPUT = Path(os.environ.get("HTLS_PARITY_DIR", PROJECT / ".test-output" / "parity"))
OUTPUT.mkdir(parents=True, exist_ok=True)

import sys, json, shutil, time
from pathlib import Path

sys.path.insert(
    0,
    os.environ.get(
        "FONTLAB_MCP_CLIENT_DIR", str(PROJECT.parent / "Proteus" / "docs" / "mcp")
    ),
)
from client import Client

base = OUTPUT
flavor = sys.argv[1] if len(sys.argv) > 1 else "upright"
reference = json.loads((base / ("glyphs-" + flavor + ".json")).read_text())
source = (
    base / "italic.glyphs"
    if flavor == "italic"
    else UPSTREAM / "Examples" / "ExampleFont-Glyphs3.glyphs"
)
names = [
    "A",
    "H",
    "i",
    "o",
    "colon",
    "florin",
    "Omega",
    "mu",
    "parenleft",
    "T",
    "pi",
    "n",
]
allrows = []
with Client("/Applications/FontLab 9.app/Contents/MacOS/fontlab-mcp") as c:
    existing = c.call("list_fonts")["fonts"]
    original = c.call("get_active_font")["id"] if existing else None
    c.call(
        "run_python",
        code="import sys\nfor k in list(sys.modules):\n if k.startswith('htls_fontlab') and k not in ('htls_fontlab.compact','htls_fontlab.ui','htls_fontlab.reporter'):del sys.modules[k]",
    )
    try:
        for scenario in reference["scenarios"]:
            testpath = base / (flavor + "-" + scenario["id"] + ".glyphs")
            shutil.copyfile(source, testpath)
            c.call("open_font", path=str(testpath))
            testid = c.call("get_active_font")["id"]
            try:
                rows = []
                for offset in range(0, len(names), 12):
                    code = """from pathlib import Path
PROJECT=Path(%r)
UPSTREAM=Path(%r)
OUTPUT=Path(%r)
import sys,json,os
sys.path.insert(0,str(PROJECT))
from htls_fontlab.service import Session
s=Session.current()
mapping=dict(zip(['Light','Regular','Bold'],list(s.font.master_by_name)))
s.import_setup(str(UPSTREAM/'Examples'/'LetterspacerTestFont_Export.json'),master_map=mapping)
scenario=%r
if scenario.get('rules')=='legacy':s.rules=s.upstream.config.parse_config_text(open(str(OUTPUT/'legacy-default.yml')).read())
if not scenario.get('rules'):s.rules={}
for m in s.font.masters:m.customParameters['paramFreq']=5
results=s.apply(names=%r,all_masters=True,params=scenario.get('params'),manual=scenario.get('manual',{}) if not scenario.get('rules') else None)
rows=[]
for r in results:
    row={k:r[k] for k in ('name','master','before') if k in r};row['glyph']=row.pop('name');row['scenario']=scenario['id'];row['master']={v:k for k,v in mapping.items()}[row['master']]
    row['computed_after']=r.get('after');row['skip']=r.get('skip')
    e=r.get('engine')
    if e:
        layer=e.layer
        row['bounds']=list(layer.bounds)
        row['computed']=[e.newL,e.newR] if r.get('after') else None
        row['classification']=[layer.parent.category,layer.parent.subCategory,layer.parent.script,layer.parent.case]
        row['params']=[e.paramArea,e.paramDepth,e.paramOver,e.xHeight,e.angle,e.upm]
        row['resolved']=[e.effectiveArea,e.effectiveDepth,e.reference_layer.parent.name]
        if r.get('after'):
            layer.refresh();row['after']=[layer.LSB,layer.RSB,layer.width]
    rows.append(row)
print(json.dumps(rows))
""" % (
                        str(PROJECT),
                        str(UPSTREAM),
                        str(OUTPUT),
                        scenario,
                        names[offset : offset + 12],
                    )
                    result = c.call("run_python", code=code)
                    assert "Traceback" not in result["output"], result["output"]
                    rows += json.loads(result["output"])
                assert len(rows) == len(names) * 3, (scenario["id"], len(rows))
                allrows += rows
                print(flavor, scenario["id"], len(rows), flush=True)
            finally:
                c.call("close_font", font_id=testid, save=False)
            (base / ("fontlab-live-verified-" + flavor + ".json")).write_text(
                json.dumps(
                    {"host": "FontLab 9", "flavor": flavor, "rows": allrows}, indent=2
                )
            )
    finally:
        if original is not None:
            c.call("set_active_font", font_id=original)
