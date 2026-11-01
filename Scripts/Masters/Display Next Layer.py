# this_file: Scripts/Masters/Display Next Layer.py
# SPDX-License-Identifier: Apache-2.0
"""Show the next layer of each selected glyph in the Glyph window.

What it does:
    Cycle the displayed layer of the selected glyph slot(s) to the next layer
    of the same master. After the last layer, wrap to the first one.

How it works:
    FontLab binds a layer to a master by its name. The text before the first
    "@" (or "#") identifies master and alternate layers. Backups use
    <master> backup <suffix>; legacy @ and space-prefixed backups also take
    part, resolved by the longest master prefix. Masks and service layers stay out.
    The script reads the shown layer of each selected slot, lists the glyph layers
    of the same master in glyph order, and picks the next one. A slot with an
    explicit layer name gets the new name. A slot that follows the active layer
    gets a new active layer for its glyph.

Why this design:
    - fly.ap.masters.associated_master resolves native layer names; the same
      backup resolver as Restore Backup Layer adds plain backup names.
    - All slots are planned first. One bad slot stops the run before any change.
    - The script writes no font data. No Undo step is needed.

How to use:
    Open a Glyph window. Select a glyph. Run the script. Assign a shortcut to
    this script and to "Display Previous Layer" to walk through backups fast.

Benefit:
    One key press compares master, backup and alternate layers in place.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Display next layer"
    (Apache-2.0). Independent rewrite. No source code was copied.
"""

from collections.abc import Sequence
from time import monotonic
from typing import Any

TITLE = "Display Next Layer"
STEP = 1  # +1 = next layer, -1 = previous layer
DEADLINE_SECONDS = 2.0


def backup_master(name: str, masters: Sequence[str]) -> str | None:
    """Resolve backup layers through the shared App rule."""
    import fly.ap.masters as masters_api

    return masters_api.backup_master(name, masters)


def layer_cycle(
    layers: Sequence[tuple[str, bool]], current: str, masters: Sequence[str]
) -> list[str]:
    """List the body layer names that share the master of `current`.

    `layers` holds (name, is_body) in glyph order. Mask and service layers
    have is_body False. Raise ValueError when `current` has no master.
    """
    from fly.ap.masters import associated_master

    master = associated_master(current, masters) or backup_master(current, masters)
    if master is None:
        raise ValueError(f"Layer '{current}' belongs to no master.")
    names = [
        name
        for name, body in layers
        if body and (associated_master(name, masters) or backup_master(name, masters)) == master
    ]
    if current not in names:
        raise ValueError(f"Layer '{current}' is not a body layer.")
    return names


def pick_layer(cycle: Sequence[str], current: str, step: int) -> str:
    """Return the layer `step` places after `current`, with wrap-around."""
    if len(cycle) < 2:
        raise ValueError(f"Layer '{current}' is the only layer of its master.")
    return cycle[(cycle.index(current) + step) % len(cycle)]


def plan(step: int) -> tuple[Any, list[tuple[Any, str, str]]]:
    """Read the selected slots and choose the target layer of each one.

    Return (selection, [(occurrence, current name, target name)]).
    """
    from fly.ap.layer_selection import capture
    from fly.ap.scripting import current_package

    selection = capture(monotonic() + DEADLINE_SECONDS)
    if selection.context[2] != "editor":
        raise ValueError("Activate a Glyph window and select a glyph first.")
    package = current_package()
    if package is None or not selection.occurrences:
        raise ValueError("Select a glyph in a Glyph window first.")
    masters = tuple(str(name) for name in package.masters)
    jobs = []
    for occurrence in selection.occurrences:
        layers = [
            (str(layer.name), not (layer.isMaskLayer or layer.isService))
            for layer in occurrence.glyph.layers
        ]
        cycle = layer_cycle(layers, occurrence.layer_name, masters)
        jobs.append(
            (occurrence, occurrence.layer_name, pick_layer(cycle, occurrence.layer_name, step))
        )
    return selection, jobs


def show_layer(selection: Any, occurrence: Any, target: str) -> None:
    """Make one editor slot show layer `target` and prove that it did."""
    from fly.ap.qtsafe import qt_list

    canvas = selection.carriers[0]
    blocks = qt_list(canvas.textBlocks)
    block = next(b for b in blocks if int(b.id) == occurrence.block_id)
    glyph = occurrence.glyph
    if str(block.getGlyphAt(occurrence.index).symbol.layerName):
        block.getGlyphAt(occurrence.index).symbol.layerName = target
        shown = str(block.getGlyphAt(occurrence.index).symbol.layerName)
    else:
        glyph.findLayer(target).setActive()
        shown = str(glyph.updateActiveLayer(False).name)
    if shown != target:
        raise RuntimeError(
            f"FontLab did not switch '{occurrence.glyph_name}' to layer '{target}'."
        )
    block.changed()


def run(step: int = STEP) -> list[str]:
    """Plan all slots, then switch them. Return one message per slot."""
    selection, jobs = plan(step)
    messages = []
    for occurrence, current, target in jobs:
        show_layer(selection, occurrence, target)
        messages.append(f"{occurrence.glyph_name}: '{current}' -> '{target}'")
    return messages


def main() -> None:
    """Menu entry. Print each result or the reason for a refusal."""
    try:
        for line in run():
            print(f"{TITLE}: {line}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
