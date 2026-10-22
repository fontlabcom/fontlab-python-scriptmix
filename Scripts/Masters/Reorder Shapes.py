# this_file: Scripts/Masters/Reorder Shapes.py
# SPDX-License-Identifier: Apache-2.0
"""Apply a reference shape order across matching layers of selected glyphs.

What: Sort outlines by total node count then rounded y/x, and components by
base name then rounded y/x. Derive the index permutation once from the current
master, or the first declared master present in the glyph.
How: Apply that same permutation only to layers whose ordered shape signatures
match the reference. Keep shape groups and internal contour order intact.
Why: Bring to Front and Send to Back act on individual elements. Native contour
sorting works inside shapes. This tool orders shape groups across glyphs and
matching masters without sorting each master's geometry independently.
Use: Select glyphs and run. Automatic owners, bases of auto composites and
glyphs with locked layers are skipped and listed. Other glyphs still change.
Layers with different component bases or contour node counts are listed and
kept. Mask and service layers are never notified. Capture includes selected
or active glyph slots. Each glyph has its own scan budget.
Benefit: Apply one shape permutation consistently across matching layers.
Each changing action is recorded as one Undo step, followed by an order check.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Glyphs/Reorder Shapes.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.
"""

from time import monotonic
from typing import Any

TITLE = "Reorder Shapes"


def ordered_ids(shapes: list[Any]) -> list[int]:
    """Return stable shape IDs without detaching, cloning or editing outlines."""
    import fly.ap.component_writer as components

    def key(shape: Any) -> tuple:
        bounds = shape.boundingBox
        position = (round(float(bounds.y()), -1), round(float(bounds.x()), -1))
        if shape.isComponent:
            return (1, components.base_of(shape), *position)
        return (0, sum(int(c.nodesCount) for c in shape.contours), *position)

    return [int(shape.id) for shape in sorted(shapes, key=key)]


def shape_signature(shapes: list[Any]) -> tuple:
    """Match components and ordered contour node counts, without coordinates."""
    import fly.ap.component_writer as components

    return tuple(
        ("component", components.base_of(shape))
        if shape.isComponent
        else ("outline", tuple(int(c.nodesCount) for c in shape.contours))
        for shape in shapes
    )


def glyph_jobs(
    glyph: Any, master: str, masters: tuple[str, ...]
) -> tuple[list, list[str]]:
    """Derive one permutation per glyph and skip layers with different signatures."""
    deadline = monotonic() + 2.0
    layers = [
        layer for layer in glyph.layers if not (layer.isMaskLayer or layer.isService)
    ]
    reference = next((layer for layer in layers if str(layer.name) == master), None)
    if reference is None:
        reference = next(
            (layer for name in masters for layer in layers if str(layer.name) == name),
            None,
        )
    if reference is None:
        return [], [f"{glyph.name}: no declared master layer"]
    source = list(reference.shapes)
    indices = {int(shape.id): index for index, shape in enumerate(source)}
    permutation = [indices[ident] for ident in ordered_ids(source)]
    signature = shape_signature(source)
    jobs, skipped = [], []
    for layer in layers:
        if monotonic() >= deadline:
            return [], [f"{glyph.name}: layer scan exceeded its per-glyph time limit"]
        shapes = list(layer.shapes)
        if shape_signature(shapes) != signature:
            skipped.append(
                f"{glyph.name}/{layer.name}: shapes do not match the reference master"
            )
            continue
        order = [int(shapes[index].id) for index in permutation]
        if order != [int(shape.id) for shape in shapes]:
            jobs.append((layer, order))
    return jobs, skipped


def run() -> dict:
    """Skip refused glyphs and apply one reference permutation to matching layers."""
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.layer_selection as selection
    import fly.ap.scripting as scripting  # noqa: PLR0402

    captured = selection.capture(monotonic() + 2.0)
    package = scripting.current_package()
    if package is None or not captured.occurrences:
        raise ValueError("Open a font and select glyphs first.")
    if package.id != captured.context[0]:
        raise ValueError("The active font changed; select glyphs again.")
    glyphs = list(
        {int(row.glyph.id): row.glyph for row in captured.occurrences}.values()
    )
    facts = history.scan_auto_facts(package)
    refused = history.refusals(facts, [str(glyph.name) for glyph in glyphs], "geometry")
    jobs, skipped, edited_glyphs = [], [], []
    for glyph in glyphs:
        reason = refused.get(str(glyph.name), "")
        if not reason and any(
            layer.isLocked or layer.autoLayer for layer in glyph.layers
        ):
            reason = "has locked or automatic layers"
        if reason:
            skipped.append(f"{glyph.name}: {reason}")
            continue
        planned, notes = glyph_jobs(glyph, str(package.master), tuple(package.masters))
        skipped.extend(notes)
        jobs.extend(planned)
        if planned:
            edited_glyphs.append(glyph)
    if not jobs:
        return {"pending_updates": (), "pending_note": "", "changed": 0, "skipped": skipped}
    current = scripting.current_package()
    if current is None or current.id != package.id:
        raise ValueError("The active font changed before writing.")

    def mutate() -> None:
        """Keep ownership and signal each native layer after reordering its IDs."""
        for layer, order in jobs:
            layer.reorderShapes(order)
            # Native Shapes panel: Proteus/workspace2/shapespanel.cpp:2887-2888.
            layer.changed()

    def read_back() -> list[str]:
        """Name any layer whose native shape order did not match the plan."""
        return [
            str(layer.name)
            for layer, order in jobs
            if [int(shape.id) for shape in layer.shapes] != order
        ]

    result = history.commit(
        TITLE,
        [layer for layer, _ in jobs],
        edited_glyphs,
        mutate,
        operation="geometry",
        facts=facts,
        read_back=read_back,
    )
    if result.mismatches:
        raise RuntimeError(
            "Shape order differs. Native changes may remain; use Edit > Undo."
        )
    return {"pending_note": result.pending_note, "pending_updates": result.pending_updates, "changed": len(jobs), "skipped": skipped}


def main() -> None:
    """Report changed layer count or contain selection/history failures."""
    import fly.ap.edit_guards as result_guards
    try:
        result = run()
        print(result_guards.append_note(f"{TITLE}: changed {result['changed']} layers.", result))
        for line in result["skipped"]:
            print(f"Skipped: {line}")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
