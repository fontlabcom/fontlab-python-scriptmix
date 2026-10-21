# this_file: Scripts/Masters/Duplicate Current Layer.py
# SPDX-License-Identifier: Apache-2.0
"""Copy the selected glyph layer into a new time-stamped layer.

What it does:
    Make an exact copy of the shown layer of each selected glyph. The copy is a
    normal body layer named "<Master>@ HH:MM:SS, DD/MM/YY". It stays attached to
    the same master, so "Display Next Layer" finds it.

How it works:
    FontLab binds a layer to a master by the name text before the first "@".
    The script keeps that prefix, adds the time stamp, and adds " (2)", " (3)"
    when the name is taken. It clones the layer, renames the clone, and adds it
    to the glyph. One notification covers all new layers: one Undo step.

Why this design:
    - A plain backup layer never joins interpolation: FontLab does not treat the
      "@" name as a second master location.
    - The time stamp has seconds. Two quick copies do not collide.
    - Mask (background), service and automatic layers are refused. Their copies
      would break background naming or re-run automatic recipes. A glyph that
      has an automatic layer, or is a base of one (also through manual
      composites), is refused too: FontLab cannot undo it. So is a run while
      FontLab has pending glyph updates. The shared App helper fly.ap.history
      does these checks and the one-step write.
    - FontLab clone() drops shape notes and names, active and selected flags,
      and the raw state and name of nodes. The script copies them back and
      checks the shape count before it adds the layer.
    - Every layer is checked before the first change.

How to use:
    Select glyphs (Font window) or open a Glyph window. Run the script. Use it
    before a risky edit, then use "Use Layer As Master" to swap back if needed.

Benefit:
    A safe copy in one key press, without the Layers panel dialog.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Duplicate current layer"
    (Apache-2.0). Independent rewrite. No source code was copied.
    Known limit: clone() recalculates smooth flags (fl#8516); the script
    restores node states.
"""

from collections.abc import Collection, Sequence
from datetime import datetime
from time import monotonic
from typing import Any

TITLE = "Duplicate Current Layer"
STAMP_FORMAT = "%H:%M:%S, %d/%m/%y"
DEADLINE_SECONDS = 2.0


def backup_name(base: str, taken: Collection[str], stamp: str) -> str:
    """Return "<base>@ <stamp>", made unique with " (2)", " (3)" when needed.

    FontLab compares layer names without case. So does this test.
    """
    used = {name.lower() for name in taken}
    name, number = f"{base}@ {stamp}", 2
    while name.lower() in used:
        name = f"{base}@ {stamp} ({number})"
        number += 1
    return name


SELECTED = 0x0020  # node state bit: selected


def restore_shape(old: Any, new: Any, keep_view_state: bool, indexes: Sequence[int] | None = None) -> None:
    """Copy back what FontLab's clone() drops (fl#8516, fl#8538).

    Restore shape note and name, the raw state and name of every node, and,
    with `keep_view_state`, the active and selected flags of the shape. Without
    it, node selection bits stay as the clone has them. `indexes` picks the
    contours of `old` that `new` holds (default: all, in order).
    """
    new.shapeData.note, new.shapeData.name = old.shapeData.note, old.shapeData.name
    if keep_view_state:
        new.active, new.selected = old.active, old.selected
    contours = list(old.contours)
    if indexes is not None:
        contours = [contours[i] for i in indexes]
    for before, after in zip(contours, new.contours, strict=True):
        for source, target in zip(before.nodes(), after.nodes(), strict=True):
            if keep_view_state:
                target.nodeState = source.nodeState
            else:
                target.nodeState = (source.nodeState & ~SELECTED) | (target.nodeState & SELECTED)
            target.name = source.name


def plan() -> list[tuple[Any, Any, str]]:
    """Choose the new layer name of every selected layer. Return jobs.

    A job is (glyph, layer, new name). Raise ValueError before any change.
    """
    from fly.ap.layer_selection import capture
    from fly.ap.masters import associated_master
    from fly.ap.scripting import current_package

    selection = capture(monotonic() + DEADLINE_SECONDS)
    package = current_package()
    if package is None or not selection.occurrences:
        raise ValueError("Select a glyph first.")
    masters = tuple(str(name) for name in package.masters)
    stamp = datetime.now().astimezone().strftime(STAMP_FORMAT)
    taken: dict[int, set[str]] = {}
    seen: set[tuple[int, int]] = set()
    jobs = []
    for item in selection.occurrences:
        key = (item.glyph_id, item.layer_id)
        if key in seen:
            continue
        seen.add(key)
        layer = item.layer
        if layer.isMaskLayer or layer.isService or layer.autoLayer:
            raise ValueError(
                f"Layer '{item.layer_name}' of '{item.glyph_name}' is a mask, service "
                "or automatic layer; select a body layer."
            )
        names = taken.setdefault(item.glyph_id, {str(x.name) for x in item.glyph.layers})
        base = associated_master(item.layer_name, masters) or item.layer_name
        name = backup_name(base, names, stamp)
        names.add(name)
        jobs.append((item.glyph, layer, name))
    return jobs


def duplicate(jobs: Sequence[tuple[Any, Any, str]]) -> list[Any]:
    """Clone each layer, name the clone, add it to its glyph. One Undo step.

    The shared App history commit refuses the whole run before any change when
    FontLab has pending glyph updates, or when a glyph owns an automatic layer
    or is a base of one (also through manual composites).
    """
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly.ap.scripting import current_package

    def mutate() -> list[Any]:
        created = []
        for glyph, layer, name in jobs:
            clone = layer.clone()
            if len(clone.shapes) != len(layer.shapes):
                raise RuntimeError(f"FontLab clone changed the shape count of '{glyph.name}'.")
            for old, new in zip(layer.shapes, clone.shapes, strict=True):
                restore_shape(old, new, True)
            clone.name = name
            glyph.addLayer(clone)
            found = glyph.findLayer(name)
            if found is None or found.isNull:
                raise RuntimeError(f"FontLab did not add layer '{name}'.")
            glyph.bindDependencies()
            created.append(found)
        return created

    glyphs = list({int(glyph.id): glyph for glyph, _, _ in jobs}.values())
    facts = history.scan_auto_facts(current_package())
    done = history.commit(TITLE, [], glyphs, mutate, operation="geometry", facts=facts)
    return list(done.created)


def run() -> list[str]:
    """Plan, then duplicate. Return one message per new layer."""
    jobs = plan()
    duplicate(jobs)
    return [f"{glyph.name}: new layer '{name}'" for glyph, _, name in jobs]


def main() -> None:
    """Menu entry. Print each result or the reason for a refusal."""
    try:
        for line in run():
            print(f"{TITLE}: {line}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
