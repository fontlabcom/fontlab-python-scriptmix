# this_file: Scripts/Cleanup/Empty Layers.py
# SPDX-License-Identifier: Apache-2.0
"""Delete the empty extra layers of the selected glyphs.

What it does:
    Remove every extra layer that holds nothing: no shapes, anchors, guides,
    note, recipe, library data, TrueType hints or data, metrics links, and no
    mask that holds any of these. An empty mask of such a layer goes with it. Print the
    deleted layers (the first ten by name) and what was skipped.

How it works:
    The script checks each layer of the selected glyphs against the list of
    data fields above. Master layers, automatic, mask, service, image and
    temporary "|temp|" layers are never deleted on their own. The empty
    mask of a deleted layer is removed first, so no orphan mask stays. All
    deletions run in one Undo step through the shared module fly.ap.history.
    FontLab records the step only for layers plus their glyph, so the
    notification holds the first master layer of each glyph, which stays.
    Then the script checks by layer id that each deleted layer and mask is
    gone.

Why this design:
    - No dialog: the script deletes only layers that carry no data, and
      the deletion is recorded as one Undo step. A preview would show only
      names.
    - The shown (active) layer of a glyph is kept, so FontLab never has to
      pick another shown layer. A locked layer, or one with a locked mask,
      is kept: a lock is a deliberate "keep".
    - The deleted layers and masks hold no shapes, so no component has to
      be retained for Undo (fl#7641).
    - Glyphs with automatic layers and bases of automatic composites (also
      through manual composites) are skipped and named in the result. A
      notification there makes FontLab rebuild the automatic glyphs, and
      Undo does not restore them.
    - The run is refused while FontLab has pending glyph updates.

How to use:
    Select glyphs in the Font window (Select All for the whole font), or
    open one glyph. Run the script. Read the result in the Output panel.
    Use "Layer Cleanup" to delete layers that hold data.

Benefit:
    Leftover empty layers from imports and experiments go in one key press.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (cleanup_empty_layers.py, "Remove Empty Auxiliary Layers").
"""

from collections.abc import Sequence
from typing import Any

TITLE = "Empty Layers"
TEMP_PREFIX = "|temp|"
#: Layer fields that make a layer "not empty" when they hold any value.
DATA_FIELDS = (
    "shapes", "anchors", "guidelines", "note", "recipe", "lib",
    "hasTTH", "hasTTData", "metricsLeft", "metricsRight", "metricsWidth",
)  # fmt: skip
MAX_LISTED = 10  # deleted layers and skipped items named in the result


def is_empty_auxiliary(layer: Any, masters: Sequence[str]) -> bool:
    """True for an extra layer that holds no data and no mask content."""
    name = str(layer.name)
    if name.lower() in {str(m).lower() for m in masters} or name.startswith(TEMP_PREFIX):
        return False
    if layer.autoLayer or layer.isMaskLayer or layer.isService or layer.isImgLayer:
        return False
    if any(getattr(layer, field) for field in DATA_FIELDS):
        return False
    mask = layer.getMaskLayer(False)
    return mask is None or mask.isNull or not any(getattr(mask, field) for field in DATA_FIELDS)


def plan(package: Any, names: Sequence[str], facts: Any) -> tuple[list[tuple[Any, Any]], list[str]]:
    """Return ([(glyph, layer)] to delete, [skip texts]). Change nothing."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    masters = [str(m) for m in package.masters]
    jobs: list[tuple[Any, Any]] = []
    skipped: list[str] = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            continue
        reason = history.refusal(facts, str(glyph.name), "geometry")
        if reason:
            skipped.append(f"{glyph.name}: {reason}")
            continue
        active = glyph.updateActiveLayer(False)
        shown = int(active.id) if active is not None and not active.isNull else None
        for layer in glyph.layers:
            if not is_empty_auxiliary(layer, masters):
                continue
            mask = layer.getMaskLayer(False)
            if int(layer.id) == shown:
                skipped.append(f"{glyph.name}/{layer.name}: shown layer")
            elif layer.isLocked or (mask is not None and not mask.isNull and mask.isLocked):
                skipped.append(f"{glyph.name}/{layer.name}: locked layer")
            else:
                jobs.append((glyph, layer))
    return jobs, skipped


def doomed_layers(jobs: Sequence[tuple[Any, Any]]) -> list[tuple[Any, Any, str]]:
    """Return [(glyph, layer, name)] in removal order: each empty mask, then its layer.

    Names are read now, before the layers go.
    """
    found = []
    for glyph, layer in jobs:
        mask = layer.getMaskLayer(False)
        if mask is not None and not mask.isNull:
            found.append((glyph, mask, str(mask.name)))
        found.append((glyph, layer, str(layer.name)))
    return found


def undo_layer(glyph: Any, doomed: set[int], masters: Sequence[str]) -> Any:
    """Return the first master layer of ``glyph`` that stays.

    FontLab records an Undo step only for a list of layers plus their glyph;
    a glyph alone adds no step. ``doomed`` holds layer ids. Raise ValueError
    when no master layer is left.
    """
    for master in masters:
        layer = glyph.findLayer(master)
        if layer is not None and not layer.isNull and int(layer.id) not in doomed and not layer.autoLayer:
            return layer
    raise ValueError(f"'{glyph.name}' has no layer left to record the Undo step.")


def remove(jobs: Sequence[tuple[Any, Any]], masters: Sequence[str], facts: Any) -> list[str]:
    """Delete the planned layers as ONE Undo step. Return the read-back mismatches."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    glyphs = list({str(g.name): g for g, _ in jobs}.values())
    names = doomed_layers(jobs)
    doomed = {int(layer.id) for _, layer, _ in names}
    carriers = [undo_layer(glyph, doomed, masters) for glyph in glyphs]

    def mutate() -> None:
        for glyph, layer, _ in names:
            glyph.removeLayer(layer)

    def read_back() -> list[str]:
        return [
            f"{glyph.name}: layer '{name}' is still there"
            for glyph, layer, name in names
            if int(layer.id) in {int(x.id) for x in glyph.layers}
        ]

    done = history.commit(TITLE, carriers, glyphs, mutate, operation="geometry", facts=facts, read_back=read_back)
    return list(done.mismatches)


def plural(count: int, word: str) -> str:
    """Return "1 glyph" or "2 glyphs"."""
    return f"{count} {word}{'' if count == 1 else 's'}"


def run() -> str:
    """Plan and delete. Return the result text. Raise ValueError for a refusal."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.scripting as scripting  # noqa: PLR0402

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font first.")
    names = scripting.names_selected_names()
    if not names:
        raise ValueError("Select glyphs in the Font window first.")
    facts = history.scan_auto_facts(package)
    jobs, skipped = plan(package, names, facts)
    if not jobs:
        raise ValueError("No empty layer in the selected glyphs.")
    mismatches = remove(jobs, [str(m) for m in package.masters], facts)
    glyphs = len({str(g.name) for g, _ in jobs})
    shown = ", ".join(f"{g.name}/{x.name}" for g, x in jobs[:MAX_LISTED])
    extra = f" and {len(jobs) - MAX_LISTED} more" if len(jobs) > MAX_LISTED else ""
    text = f"Deleted {plural(len(jobs), 'empty layer')} from {plural(glyphs, 'glyph')}: {shown}{extra}."
    if skipped:
        more = f" and {len(skipped) - MAX_LISTED} more" if len(skipped) > MAX_LISTED else ""
        text += f" Skipped {len(skipped)}: {'; '.join(skipped[:MAX_LISTED])}{more}."
    if mismatches:
        text += " Did not read back as planned: " + "; ".join(mismatches) + "."
    return text


def main() -> None:
    """Menu entry. Print the result or the reason for a refusal."""
    try:
        print(f"{TITLE}: {run()}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
