from pathlib import Path
import os

PROJECT = Path(__file__).resolve().parents[2]
UPSTREAM = Path(os.environ.get("HTLS_UPSTREAM", PROJECT.parent / "HTLetterspacer"))
OUTPUT = Path(os.environ.get("HTLS_PARITY_DIR", PROJECT / ".test-output" / "parity"))
OUTPUT.mkdir(parents=True, exist_ok=True)
import json, collections
from pathlib import Path

p = OUTPUT
report = []


def key(r):
    return r["scenario"], r["master"], r["glyph"]


def diff(x, y):
    if x is None or y is None:
        return 0 if x is None and y is None else float("inf")
    return max(abs(a - b) for a, b in zip(x, y))


for flavor in ("upright", "italic"):
    gs = json.load(open(p / ("glyphs-" + flavor + ".json")))["rows"]
    fl = json.load(open(p / ("fontlab-" + flavor + ".json")))["rows"]
    lookup = {key(r): r for r in gs}
    for scenario in dict.fromkeys(r["scenario"] for r in gs):
        pairs = [(lookup[key(r)], r) for r in fl if r["scenario"] == scenario]
        misses = [
            (a, b) for a, b in pairs if diff(a.get("after"), b.get("after")) > 1 + 1e-7
        ]
        old = [
            a
            for a, b in pairs
            if "legacy_after" in a
            and diff(a.get("legacy_after"), b.get("after")) > 1 + 1e-7
        ]
        item = {
            "font": flavor,
            "scenario": scenario,
            "comparisons": len(pairs),
            "measurable": sum(a.get("after") is not None for a, b in pairs),
            "over_1": len(misses),
            "max_delta": max(diff(a.get("after"), b.get("after")) for a, b in pairs),
            "over_1_rounded": sum(
                diff([round(v) for v in a["after"]], [round(v) for v in b["after"]]) > 1
                for a, b in pairs
                if a.get("after") is not None and b.get("after") is not None
            ),
            "legacy_over_1": len(old),
            "legacy_max_delta": max(
                [
                    diff(a.get("legacy_after"), b.get("after"))
                    for a, b in pairs
                    if "legacy_after" in a
                ],
                default=0,
            ),
        }
        report.append(item)
        print(item)
        for a, b in misses[:5]:
            print(
                "  FRACTIONAL OUTLIER",
                a["glyph"],
                a["master"],
                a.get("after"),
                b.get("after"),
            )
json.dump(report, open(p / "summary.json", "w"), indent=2)
