# this_file: Scripts/Kerning/Kerning Energy Report.py
# SPDX-License-Identifier: MIT
"""Show a read-only kerning energy and spacing-bias report for selected glyphs.

What: Report the sum of squared effective pair values and independent row/column
means on the current master. The report is read-only and changes no font data.
How: Build side-class indexes once, then resolve typed glyph and class pairs.
Explicit zero exceptions win. Ambiguous pairs are named and kept out of totals;
other pairs still contribute. The report retains totals and suggestions rather
than a full square matrix. At most 200 kept-pair details are displayed.
Why: FontLab's Compress to Class Kerning converts pair representation. That
command is unrelated to this spacing-bias diagnostic.
Use: Select glyphs in the Font window and run. Copy the selectable JSON report
for comparison after a spacing pass. Run again for fresh measurements.
Benefit: Find recurring spacing biases before editing sidebearings or kerning.
Energy uses font units squared, without the source's arbitrary scale factor.

Independent behaviour rewrite after Simon Cozens, Kern Optimizer.py, MIT.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.
"""

from collections.abc import Sequence
from math import isfinite
from typing import Any

TITLE, KEY = "Kerning Energy Report", "kerning_energy_report"
DETAIL_LIMIT = 200


def side_index(groups: dict) -> tuple[dict, dict]:
    """Index membership by glyph and pair side once per captured master."""
    indexes: tuple[dict, dict] = ({}, {})
    for key, (members, mode) in groups.items():
        sides = {"KernLeft": (0,), "KernRight": (1,), "KernBothSide": (0, 1)}.get(
            mode, ()
        )
        for side in sides:
            for name in dict.fromkeys(members):
                indexes[side].setdefault(name, []).append(key)
    return indexes


def effective(
    left: str, right: str, pairs: dict, groups: dict, *, index: tuple | None = None
) -> float:
    """Resolve one pair; an explicit glyph pair needs no class disambiguation."""
    direct = ((left, "glyphMode"), (right, "glyphMode"))
    indexes = side_index(groups) if index is None else index
    choices = []
    for side, name in enumerate((left, right)):
        found = indexes[side].get(name, [])
        if direct not in pairs and len(found) > 1:
            raise ValueError(
                f"Ambiguous kerning classes for {name} on side {side + 1}."
            )
        choices.append([(name, "glyphMode")] + [(key, "groupMode") for key in found])
    for a in choices[0]:
        for b in choices[1]:
            if (a, b) in pairs:
                value = float(pairs[a, b])
                if not isfinite(value):
                    raise ValueError("Kerning values must be finite.")
                return value
    return 0.0


def energy(matrix: Sequence[Sequence[float]]) -> float:
    """Return the sum of squared effective values in font units squared."""
    return sum(value * value for row in matrix for value in row)


def analyze(names: list[str], pairs: dict, groups: dict) -> dict:
    """Accumulate totals without storing a square matrix; keep only bad pairs."""
    if not names:
        raise ValueError("Select glyphs in the Font window first.")
    index = side_index(groups)
    rows, columns = [0.0] * len(names), [0.0] * len(names)
    row_counts, column_counts = [0] * len(names), [0] * len(names)
    score, evaluated, kept_count, kept = 0.0, 0, 0, []
    for i, left in enumerate(names):
        for j, right in enumerate(names):
            try:
                value = effective(left, right, pairs, groups, index=index)
            except ValueError as error:
                kept_count += 1
                if len(kept) < DETAIL_LIMIT:
                    kept.append(
                        {"left": left, "right": right, "reason": f"{error} Pair kept."}
                    )
                continue
            score += value * value
            evaluated += 1
            rows[i] += value
            columns[j] += value
            row_counts[i] += 1
            column_counts[j] += 1
    return {
        "read_only": True,
        "glyphs": names,
        "energy": score,
        "evaluated_pairs": evaluated,
        "kept_pair_count": kept_count,
        "kept_pairs": kept,
        "independent_spacing_suggestions": [
            {
                "glyph": name,
                "right_sidebearing_delta": rows[i] / row_counts[i]
                if row_counts[i]
                else None,
                "left_sidebearing_delta": columns[i] / column_counts[i]
                if column_counts[i]
                else None,
                "right_sample_count": row_counts[i],
                "left_sample_count": column_counts[i],
            }
            for i, name in enumerate(names)
        ],
        "usage": "Read-only report. Test one suggestion at a time; remeasure after each spacing change.",
    }


def run() -> Any:
    """Capture the current master and publish a detached read-only report."""
    import fly.ap.kerning_batch as batch
    import fly.ap.reports as reports  # noqa: PLR0402 - qualified Fly submodule
    import fly.ap.scripting as scripting  # noqa: PLR0402 - qualified Fly submodule

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font first.")
    master = str(package.master)
    names = list(dict.fromkeys(scripting.names_selected_names()))
    source = batch.snapshot_kerning(package, typed=True)
    result = analyze(names, source.pairs[master], source.groups[master])
    batch.ensure_snapshot(package, source)
    result["master"] = master
    return reports.show_report(result, title=f"{TITLE} — Read-only", key=KEY)


def main() -> None:
    """Contain host failures without clearing the Output panel."""
    try:
        run()
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
