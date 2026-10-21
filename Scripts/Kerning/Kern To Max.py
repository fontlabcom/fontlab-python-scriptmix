# this_file: Scripts/Kerning/Kern To Max.py
# SPDX-License-Identifier: Apache-2.0
"""Set a selected pair to minus half the narrower advance width.

What: Set class kerning, or glyph kerning without a class, on the shown master.
How: Read two adjacent selected master layers. Truncate half the smaller
advance toward zero, negate it, and pass a typed pair to the shared kerning writer.
Why: Unlike entering a value in the Metrics bar, this derives the limit from
the narrower advance in one action, independent of outline bounds. It
does not measure collisions. Ambiguous side-group membership is refused.
Use: Select exactly two adjacent glyph slots in a Glyph window and run.
Capture includes selected OR active slots. An active slot outside the pair
makes the count larger and is refused; a lone active slot is also refused.
Explicit selection replaces the Glyphs insertion-cursor fallback.
Benefit: One shortcut gives a consistent tight starting value. Each changing
action is recorded as one Undo step. No panel or font-wide redraw is needed.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Kerning/Kern to max.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.
"""

import math
from time import monotonic
from typing import Any

TITLE = "Kern To Max"


def selected_pair() -> tuple[Any, Any, Any]:
    """Refuse nonadjacent, cross-master and auxiliary occurrences."""
    import fly.ap.layer_selection as selection
    import fly.ap.scripting as scripting  # noqa: PLR0402

    captured = selection.capture(monotonic() + 2.0)
    package = scripting.current_package()
    rows = captured.occurrences
    if package is None or captured.context[0] != package.id:
        raise ValueError("Open a font and select a pair first.")
    if captured.context[2] != "editor" or len(rows) != 2:
        raise ValueError("Select exactly two adjacent glyphs in a Glyph window.")
    left, right = rows
    if left.block_id != right.block_id or right.index != left.index + 1:
        raise ValueError("Select consecutive glyphs in one text block.")
    if any(not row.layer.isMasterLayer for row in rows):
        raise ValueError("Select master layers; auxiliary layers have no kerning.")
    if left.layer.name != right.layer.name or left.layer.name not in package.masters:
        raise ValueError("Both glyphs must show the same declared master.")
    return package, left, right


def pair_key(groups: dict, left: str, right: str) -> tuple:
    """Resolve one side-specific group per glyph, with typed fallback names."""
    result = []
    for index, name in enumerate((left, right)):
        permitted = (
            ("KernLeft", "KernBothSide")
            if index == 0
            else ("KernRight", "KernBothSide")
        )
        matches = [
            key
            for key, (members, mode) in groups.items()
            if name in members and mode in permitted
        ]
        if len(matches) > 1:
            raise ValueError(f"Glyph {name} has multiple kerning groups on one side.")
        result.append((matches[0], "groupMode") if matches else (name, "glyphMode"))
    return tuple(result)


def run() -> dict:
    """Read the live pair and write a checked whole-number kerning value."""
    import fly.ap.kerning_batch as kerning

    package, left, right = selected_pair()
    widths = [float(row.layer.advanceWidth) for row in (left, right)]
    if any(not math.isfinite(width) or width < 0 for width in widths):
        raise ValueError("Both advance widths must be finite and nonnegative.")
    value = -int(min(widths) / 2)
    master = str(left.layer.name)
    before = kerning.snapshot_kerning(package, typed=True)
    pair = pair_key(before.groups[master], left.glyph_name, right.glyph_name)
    records = before.pairs[master]
    glyphs = ((left.glyph_name, "glyphMode"), (right.glyph_name, "glyphMode"))
    overrides = [
        f"{master}: {candidate[0][0]} · {candidate[1][0]} = {records[candidate]:g}"
        for candidate in dict.fromkeys(
            (glyphs, (glyphs[0], pair[1]), (pair[0], glyphs[1]))
        )
        if candidate != pair and candidate in records
    ]
    changed = records.get(pair) != value
    written = kerning.write_kerning(
        package, {master: {pair: value}}, TITLE, expected=before
    )
    return {
        "value": value,
        "changed": bool(changed and written),
        "overrides": overrides,
    }


def main() -> None:
    """Report the written limit, or contain a host refusal."""
    try:
        result = run()
        state = "Set" if result["changed"] else "Kerning unchanged at"
        print(f"{TITLE}: {state} {result['value']} units.")
        for line in result["overrides"]:
            print(f"Overriding exception kept: {line}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
