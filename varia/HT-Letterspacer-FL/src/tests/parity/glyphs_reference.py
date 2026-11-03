"""Native Glyphs comparison. All calculations/writes use detached layer copies."""

from pathlib import Path
import os

PROJECT = Path(__file__).resolve().parents[2]
UPSTREAM = Path(os.environ.get("HTLS_UPSTREAM", PROJECT.parent / "HTLetterspacer"))
OUTPUT = Path(os.environ.get("HTLS_PARITY_DIR", PROJECT / ".test-output" / "parity"))
OUTPUT.mkdir(parents=True, exist_ok=True)

import sys, os, json, math, io, contextlib, importlib.util, hashlib

sys.path.insert(
    0,
    os.environ.get(
        "HTLS_VANILLA",
        str(
            Path.home()
            / "Library/Application Support/Glyphs 4/Repositories/vanilla/Lib"
        ),
    ),
)
ROOT = str(UPSTREAM)
sys.path.insert(0, ROOT + "/HTLetterspacer.glyphsPlugin/Contents/Resources")
from GlyphsApp import Glyphs
from Foundation import NSMinX, NSMinY, NSMaxX, NSMaxY
from htls import engine, config

spec = importlib.util.spec_from_file_location(
    "legacy", str(OUTPUT / "legacy_script.py")
)
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
font = Glyphs.font
output = str(OUTPUT)
flavor = "italic" if "--italic" in sys.argv else "upright"
if flavor == "italic":
    for master in font.masters:
        master.italicAngle = 12
        tangent = math.tan(math.radians(12))
        for glyph in font.glyphs:
            layer = glyph.layers[master.id]
            layer.applyTransform((1, 0, tangent, 1, -master.xHeight * tangent / 2, 0))
    font.save(output + "/italic.glyphs")
for master in font.masters:
    master.customParameters["paramFreq"] = 5
setup = json.load(open(ROOT + "/Examples/LetterspacerTestFont_Export.json"))
config.import_setup(
    font, setup, master_map={m.name: m.id for m in font.masters}, import_params=True
)
setup_rules = config.read_font_rules(font)
legacy_rules = config.parse_config_text(legacy.DEFAULT_CONFIG_FILE)
open(output + "/legacy-default.yml", "w").write(legacy.DEFAULT_CONFIG_FILE)
legacy_array = []
for line in legacy.DEFAULT_CONFIG_FILE.splitlines():
    if line and line[0] != "#" and len(line) > 5:
        row = line.split(",")
        del row[-1]
        row[3] = float(row[3])
        legacy_array.append(row)
scenarios = [
    {
        "id": "manual-default",
        "params": {"paramArea": 400, "paramDepth": 15, "paramOver": 0},
    },
    {
        "id": "manual-screenshot",
        "params": {"paramArea": 425, "paramDepth": 25, "paramOver": 5},
    },
    {
        "id": "manual-left",
        "params": {"paramArea": 425, "paramDepth": 25, "paramOver": 5},
        "manual": {"LSB": True, "RSB": False},
    },
    {
        "id": "manual-right",
        "params": {"paramArea": 425, "paramDepth": 25, "paramOver": 5},
        "manual": {"LSB": False, "RSB": True},
    },
    {
        "id": "manual-tabular",
        "params": {"paramArea": 425, "paramDepth": 25, "paramOver": 5},
        "manual": {"tabular": True, "width": 595},
    },
    {"id": "setup-rules", "rules": "setup"},
    {
        "id": "legacy-rules",
        "params": {"paramArea": 400, "paramDepth": 15, "paramOver": 0},
        "rules": "legacy",
    },
]


def bbox(layer):
    b = layer.bounds
    return [NSMinX(b), NSMinY(b), NSMaxX(b), NSMaxY(b)]


def metrics(layer):
    return [float(layer.LSB), float(layer.RSB), float(layer.width)]


rows = []
for scenario in scenarios:
    for master in font.masters:
        for glyph in font.glyphs:
            layer = glyph.layers[master.id]
            copy = layer.copy()
            copy.parent = glyph
            flags = scenario.get("manual", {})
            rules = (
                setup_rules
                if scenario.get("rules") == "setup"
                else legacy_rules if scenario.get("rules") == "legacy" else {}
            )
            e = engine.HTLSEngine(
                copy, font_rules=rules, param_overrides=scenario.get("params")
            )
            if not scenario.get("rules"):
                e.LSB = flags.get("LSB", True)
                e.RSB = flags.get("RSB", True)
                e.tabVersion = flags.get("tabular", False)
                e.width = flags.get("width")
            captured = io.StringIO()
            with contextlib.redirect_stdout(captured):
                sb = e.current_layer_sidebearings()
            row = {
                "scenario": scenario["id"],
                "master": master.name,
                "glyph": glyph.name,
                "before": metrics(layer),
                "bounds": bbox(layer),
                "classification": [
                    glyph.category,
                    glyph.subCategory,
                    glyph.script,
                    glyph.case,
                ],
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
                "errors": captured.getvalue(),
            }
            if sb is not None:
                copy.LSB, copy.RSB = sb
                if e.newWidth:
                    copy.width = e.newWidth
                row["after"] = metrics(copy)
            # Run actual historical standalone algorithm on a second scratch copy.
            if scenario.get("rules") != "setup":
                old = legacy.HTLetterspacerLib()
                old.upm = font.upm
                old.angle = master.italicAngle
                old.xHeight = master.xHeight
                for k, v in scenario["params"].items():
                    setattr(old, k, v)
                old.factor = 1.0
                old.LSB = flags.get("LSB", True)
                old.RSB = flags.get("RSB", True)
                old.tabVersion = flags.get("tabular", False)
                old.width = flags.get("width")
                old.newWidth = False
                oldcopy = layer.copy()
                oldcopy.parent = glyph
                reference = oldcopy
                captured = io.StringIO()
                with contextlib.redirect_stdout(captured):
                    if scenario.get("rules") == "legacy":
                        ctl = legacy.HTLetterspacerScript.__new__(
                            legacy.HTLetterspacerScript
                        )
                        ctl.font = font
                        ctl.output = ""
                        ctl.engine = old
                        ctl.config = legacy_array
                        ctl.setG(oldcopy)
                        reference = ctl.referenceLayer
                    polygons = old.spaceMain(oldcopy, reference)
                row["legacy_computed"] = (
                    [old.newL, old.newR] if polygons[0] is not None else None
                )
                row["legacy_after"] = (
                    metrics(oldcopy) if polygons[0] is not None else None
                )
                row["legacy_errors"] = (
                    captured.getvalue() if "Traceback" in captured.getvalue() else ""
                )
            rows.append(row)
report = {
    "host": "Glyphs " + str(Glyphs.versionString),
    "build": Glyphs.buildNumber,
    "flavor": flavor,
    "scenarios": scenarios,
    "rows": rows,
}
path = output + "/glyphs-" + flavor + ".json"
json.dump(report, open(path, "w"), indent=2)
print(
    "WROTE",
    path,
    "rows",
    len(rows),
    "errors",
    sum(bool(r["errors"] or r.get("legacy_errors")) for r in rows),
)
