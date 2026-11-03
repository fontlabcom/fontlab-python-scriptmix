"""Replay the unchanged HTLS engine over captured native FontLab outlines."""

from pathlib import Path
import os

PROJECT = Path(__file__).resolve().parents[2]
UPSTREAM = Path(os.environ.get("HTLS_UPSTREAM", PROJECT.parent / "HTLetterspacer"))
OUTPUT = Path(os.environ.get("HTLS_PARITY_DIR", PROJECT / ".test-output" / "parity"))
OUTPUT.mkdir(parents=True, exist_ok=True)

import json, sys, io, contextlib, os
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, os.environ.get("HTLS_ADAPTER_ROOT", str(PROJECT)))
from htls_fontlab.geometry import Outline
from htls_fontlab.upstream import load, Point
from htls_fontlab.model import UserData
from htls_fontlab.classification import classify

base = OUTPUT
flavor = sys.argv[1] if len(sys.argv) > 1 else "upright"
u = load()
raw = json.loads((base / ("fontlab-outlines-" + flavor + ".json")).read_text())
ref = json.loads((base / ("glyphs-" + flavor + ".json")).read_text())
font = NS(upm=1000, glyphs=UserData(), userData=UserData())
masters = {}


class Layer:
    def hasAlignedWidth(self):
        return self.data["auto"]

    def copyDecomposedLayer(self):
        return self

    def calculateIntersectionsStartPoint_endPoint_(self, a, b):
        return (
            [a] + [Point(x, a.y) for x in self.outline.glyphs_intersections(a.y)] + [b]
        )


for r in raw:
    r["fontlab_master"] = r["master"]
    r["master"] = {
        "LightItalic": "Light",
        "Italic": "Regular",
        "BoldItalic": "Bold",
    }.get(r["master"], r["master"])
    c = classify(r["glyph"], r["unicodes"])
    r["classification"] = [c["category"], c["subCategory"], c["script"], c["case"]]
    m = masters.setdefault(
        r["master"],
        NS(
            name=r["master"],
            id=r["master"],
            xHeight=r["xh"],
            italicAngle=r["angle"],
            customParameters=UserData(r["master_params"]),
            userData=UserData(r["master_data"]),
        ),
    )
    m.customParameters["paramFreq"] = 5
    if font.glyphs[r["glyph"]] is None:
        c = r["classification"]
        font.glyphs[r["glyph"]] = NS(
            name=r["glyph"],
            parent=font,
            category=c[0],
            subCategory=c[1],
            script=c[2],
            case=c[3],
            layers=UserData(),
        )
    g = font.glyphs[r["glyph"]]
    l = Layer()
    l.parent = g
    l.master = m
    l.name = m.name
    l.layerId = m.id
    l.associatedMasterId = m.id
    l.data = r
    l.outline = Outline(r["segments"])
    l.bounds = r["bounds"]
    l.LSB, l.RSB, l.width = r["before"]
    l.paths = [l.outline] if r["segments"] else []
    l.components = []
    l.attributes = {}
    g.layers[m.id] = l
setup = json.load(open(str(UPSTREAM / "Examples" / "LetterspacerTestFont_Export.json")))
setup_rules = {r["id"]: u.config.make_rule(**r) for r in setup["rules"]}
legacy_rules = u.config.parse_config_text((base / "legacy-default.yml").read_text())
rows = []
for scenario in ref["scenarios"]:
    for r in raw:
        l = font.glyphs[r["glyph"]].layers[r["master"]]
        g = l.parent
        g.leftMetricsKey = r["left_key"] or None
        g.rightMetricsKey = r["right_key"] or None
        rules = (
            setup_rules
            if scenario.get("rules") == "setup"
            else legacy_rules if scenario.get("rules") == "legacy" else {}
        )
        e = u.engine.HTLSEngine(
            l, font_rules=rules, param_overrides=scenario.get("params")
        )
        flags = scenario.get("manual", {})
        if not scenario.get("rules"):
            e.LSB = flags.get("LSB", True)
            e.RSB = flags.get("RSB", True)
            e.tabVersion = flags.get("tabular", False)
            e.width = flags.get("width")
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            sb = e.current_layer_sidebearings()
        assert not captured.getvalue(), captured.getvalue()
        row = {
            "scenario": scenario["id"],
            "master": r["master"],
            "glyph": r["glyph"],
            "before": r["before"],
            "bounds": r["bounds"],
            "classification": r["classification"],
            "params": [
                e.paramArea,
                e.paramDepth,
                e.paramOver,
                e.xHeight,
                e.angle,
                e.upm,
            ],
            "resolved": [
                e.effectiveArea,
                e.effectiveDepth,
                e.reference_layer.parent.name,
            ],
            "computed": list(sb) if sb is not None else None,
        }
        if sb is not None:
            width = (
                e.newWidth
                if e.tabVersion
                else l.width + (sb[0] - l.LSB) + (sb[1] - l.RSB)
            )
            right = l.RSB + width - l.width - (sb[0] - l.LSB) if e.tabVersion else sb[1]
            row["after"] = [sb[0], right, width]
        rows.append(row)
json.dump(
    {
        "host": "FontLab 9 rendered outlines / adapter engine replay",
        "flavor": flavor,
        "rows": rows,
    },
    open(base / ("fontlab-" + flavor + ".json"), "w"),
    indent=2,
)
print("REPLAYED", flavor, len(rows))
