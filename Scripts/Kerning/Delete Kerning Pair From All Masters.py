# this_file: Scripts/Kerning/Delete Kerning Pair From All Masters.py
# SPDX-License-Identifier: Apache-2.0
"""Delete the selected adjacent kerning pairs on every master.

What: Remove each selected pair's class kerning, or glyph kerning when no
class exists, from all masters. Existing exceptions remain separate records.
How: Capture ordered Glyph-window slots. Resolve side-specific groups for
each master. Preflight the complete edit through the shared kerning writer.
Why: One shortcut clears a whole selected sequence across all masters;
The Metrics bar Remove pair command affects only the current pair/master.
Pair Editor requires separate cell edits. Ambiguous groups refuse the action.
Use: Select two or more adjacent glyphs in one Glyph-window text block, then
run. Capture includes selected OR active slots; an active slot outside the
selection must also be adjacent. A lone active slot is refused. Selection
replaces the Glyphs text-cursor fallback. No dialog is needed.
Benefit: Remove class spacing consistently without changing unrelated pairs.
Each changing action is recorded as one Undo step by the shared kerning writer.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Kerning/Delete Kerning Pair From All Masters.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.
"""

from itertools import pairwise
from time import monotonic
from typing import Any

TITLE = "Delete Kerning Pair From All Masters"


def selected_pairs() -> tuple[Any, list[tuple[Any, Any]]]:
    """Require adjacent plain-master slots from the active owned font."""
    import fly.ap.layer_selection as selection
    import fly.ap.scripting as scripting  # noqa: PLR0402

    captured = selection.capture(monotonic() + 2.0)
    package = scripting.current_package()
    rows = captured.occurrences
    if package is None or captured.context[0] != package.id:
        raise ValueError("Open a font and select adjacent glyphs first.")
    if captured.context[2] != "editor" or len(rows) < 2:
        raise ValueError("Select at least two adjacent glyphs in a Glyph window.")
    pairs = list(pairwise(rows))
    for left, right in pairs:
        if left.block_id != right.block_id or right.index != left.index + 1:
            raise ValueError("Select consecutive glyphs in one text block.")
        if any(not row.layer.isMasterLayer for row in (left, right)):
            raise ValueError("Select master layers; auxiliary layers have no kerning.")
        if left.layer.name != right.layer.name:
            raise ValueError("Both glyphs of each pair must show the same master.")
        if str(left.layer.name) not in tuple(package.masters):
            raise ValueError("The selected layer is not a declared master.")
    return package, pairs


def pair_key(groups: dict, left: str, right: str) -> tuple:
    """Use lossless typed identities; refuse multiple groups on one side."""
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
    """Delete existing records once; list exceptions that can override the result."""
    import fly.ap.kerning_batch as kerning

    package, pairs = selected_pairs()
    before = kerning.snapshot_kerning(package, typed=True)
    edits, overrides = {}, []
    for master in package.masters:
        records = before.pairs[master]
        edits[master] = {}
        for left, right in pairs:
            key = pair_key(before.groups[master], left.glyph_name, right.glyph_name)
            if key in records:
                edits[master][key] = None
            glyphs = ((left.glyph_name, "glyphMode"), (right.glyph_name, "glyphMode"))
            for candidate in dict.fromkeys(
                (glyphs, (glyphs[0], key[1]), (key[0], glyphs[1]))
            ):
                if candidate != key and candidate in records:
                    overrides.append(
                        f"{master}: {candidate[0][0]} · {candidate[1][0]} = {records[candidate]:g}"
                    )
    removed = sum(len(values) for values in edits.values())
    changed = kerning.write_kerning(package, edits, TITLE, expected=before)
    return {
        "removed": removed,
        "changed": changed,
        "overrides": list(dict.fromkeys(overrides)),
    }


def main() -> None:
    """Print the planned cell count or a diagnosed refusal."""
    try:
        result = run()
        message = (
            f"Removed {result['removed']} pair/master records."
            if result["changed"]
            else "No kerning to delete for the selected pairs."
        )
        print(f"{TITLE}: {message}")
        for line in result["overrides"]:
            print(f"Overriding exception kept: {line}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
