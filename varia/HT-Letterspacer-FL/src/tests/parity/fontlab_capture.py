from pathlib import Path
import os

PROJECT = Path(__file__).resolve().parents[2]
UPSTREAM = Path(os.environ.get("HTLS_UPSTREAM", PROJECT.parent / "HTLetterspacer"))
OUTPUT = Path(os.environ.get("HTLS_PARITY_DIR", PROJECT / ".test-output" / "parity"))
OUTPUT.mkdir(parents=True, exist_ok=True)
import sys, json, shutil
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
ref = json.loads((base / ("glyphs-" + flavor + ".json")).read_text())
names = list(dict.fromkeys(r["glyph"] for r in ref["rows"]))
source = (
    base / "italic.glyphs"
    if flavor == "italic"
    else UPSTREAM / "Examples" / "ExampleFont-Glyphs3.glyphs"
)
path = base / (flavor + "-capture.glyphs")
shutil.copyfile(source, path)
rows = []
with Client("/Applications/FontLab 9.app/Contents/MacOS/fontlab-mcp") as c:
    existing = c.call("list_fonts")["fonts"]
    original = c.call("get_active_font")["id"] if existing else None
    c.call("open_font", path=str(path))
    testid = c.call("get_active_font")["id"]
    try:
        for offset in range(0, len(names), 16):
            code = """from pathlib import Path
PROJECT=Path(%r)
UPSTREAM=Path(%r)
OUTPUT=Path(%r)
import sys,json
sys.path.insert(0,str(PROJECT))
from htls_fontlab.service import Session
s=Session.current();s.import_setup(str(UPSTREAM/'Examples'/'LetterspacerTestFont_Export.json'))
rows=[]
for name in %r:
 g=s.font.glyphs[name]
 for m in s.font.masters:
  l=g.layers[m.name]
  assert l is not None,(name,m.name)
  rows.append({'glyph':name,'unicodes':list(g.raw.fgGlyph.unicodes),'master':m.name,'bounds':l.bounds,'segments':l.outline.segments,'before':[l.LSB,l.RSB,l.width],
    'classification':[g.category,g.subCategory,g.script,g.case],'master_params':dict(m.customParameters),'master_data':dict(m.userData),
    'xh':m.xHeight,'angle':m.italicAngle,'upm':s.font.upm,'left_key':l.raw.metricsLeft,'right_key':l.raw.metricsRight,'width_key':l.raw.metricsWidth,'auto':l.hasAlignedWidth()})
json.dump(rows,open(str(OUTPUT/'capture-chunk.json'),"w"));print(len(rows))
""" % (
                str(PROJECT),
                str(UPSTREAM),
                str(OUTPUT),
                names[offset : offset + 16],
            )
            result = c.call("run_python", code=code)
            part = json.loads((base / "capture-chunk.json").read_text())
            assert len(part) == len(names[offset : offset + 16]) * 3, (
                offset,
                len(part),
            )
            rows += part
        (base / ("fontlab-outlines-" + flavor + ".json")).write_text(json.dumps(rows))
        print("CAPTURED", len(rows), flavor)
    finally:
        c.call("close_font", font_id=testid, save=False)
        if original is not None:
            c.call("set_active_font", font_id=original)
