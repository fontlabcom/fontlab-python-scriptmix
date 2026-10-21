# this_file: Scripts/Anchors/Derive Anchors From Components.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Derive Anchors From Components
"""Recover missing base anchors from positioned mark components.

What: Scan manual composites across named masters and infer base attachments.
How: Transform the first mark per underscored label into base coordinates.
The first mark in component order supplies the label in a stacked accent.
Honour explicit mark-layer references. Base destinations must be master
layers. Keep existing anchors. Ambiguous marks, missing or automatic
references, non-master bases, conflicts and layer timeouts become note rows.
A conflict removes only that base label; clean labels and layers still run.
Capture the glyph catalogue once per scan; give each layer its own budget.
Why: Recover deliberate accent placement without moving components or
rejecting a whole font because some evidence is doubtful.
Use: Open the non-modal preview, inspect edits and notes, then click Derive.
Benefit: Recover anchors for scaled or shifted bases and stacked marks.
Each application is recorded as one Undo step. Unsafe writes are refused.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

import math
from time import monotonic
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

TITLE = "Derive Anchors From Components"
KEY = "anchors_derive_anchors_from_components"


Matrix = tuple[float, float, float, float, float, float]


def attachment_in_base(
    point: tuple[float, float], mark_matrix: Matrix, base_matrix: Matrix
) -> tuple[float, float]:
    """Transform a mark point into the base's own coordinates, with a checked inverse."""
    a, b, c, d, tx, ty = mark_matrix
    x, y = point
    px, py = a * x + c * y + tx, b * x + d * y + ty
    a, b, c, d, tx, ty = base_matrix
    determinant = a * d - b * c
    if (
        not all(math.isfinite(v) for v in (*point, *mark_matrix, *base_matrix))
        or abs(determinant) < 1e-12
    ):
        raise ValueError("Component transforms must be finite and invertible.")
    px, py = px - tx, py - ty
    result = ((d * px - c * py) / determinant, (a * py - b * px) / determinant)
    if not all(math.isfinite(value) for value in result):
        raise ValueError("Component attachment coordinates must be finite.")
    return result


def coefficients(shape: Any) -> Matrix:
    """Read Qt's six affine coefficients; refuse perspective transforms."""
    matrix = shape.transform
    if not matrix.isAffine():
        raise ValueError("Perspective components cannot supply an anchor.")
    return (
        matrix.m11(),
        matrix.m12(),
        matrix.m21(),
        matrix.m22(),
        matrix.dx(),
        matrix.dy(),
    )


def layer_evidence(
    package: Any, composite: Any, master: str, masters: list[str], deadline: float
) -> tuple[tuple[str, str] | None, dict, list[str]]:
    """Resolve one composite completely; the first mark per label supplies evidence."""
    marks, bases, messages = [], [], []
    doubtful = False
    for shape in composite.shapes:
        if monotonic() >= deadline:
            raise TimeoutError("layer time budget exceeded, skipped")
        if not shape.isComponent:
            continue
        reference = shape.shapeData
        glyph = package.findName(str(reference.componentGlyph))
        layer_name = str(reference.componentLayer) or master
        layer = anchor_writer.layer_of(glyph, layer_name) if glyph else None
        if layer is None or layer.autoLayer:
            messages.append(
                f"{reference.componentGlyph}: missing or automatic referenced layer, skipped"
            )
            doubtful = True
            continue
        pins = [pin for pin in layer.anchors if pin.name.startswith("_")]
        if len(pins) > 1:
            messages.append(f"{glyph.name}: ambiguous mark, skipped")
        elif pins:
            marks.append((shape, pins[0]))
        else:
            bases.append((shape, glyph, layer_name, layer))
    if doubtful or not marks or len(bases) != 1:
        return None, {}, messages
    base_shape, base_glyph, layer_name, base_layer = bases[0]
    if layer_name not in masters:
        return (
            None,
            {},
            messages + [f"{base_glyph.name}: non-master base reference, skipped"],
        )
    present = {pin.name for pin in base_layer.anchors}
    candidates = {}
    for mark_shape, pin in marks:
        if monotonic() >= deadline:
            raise TimeoutError("layer time budget exceeded, skipped")
        label = pin.name[1:]
        if not label or label in present or label in candidates:
            continue
        x, y = attachment_in_base(
            anchor_writer.raw_point(pin),
            coefficients(mark_shape),
            coefficients(base_shape),
        )
        candidates[label] = (anchor_writer.half_up(x), anchor_writer.half_up(y))
    return (base_glyph.name, layer_name), candidates, messages


def derived_points(
    package: Any, names: list[str], masters: list[str], notes: dict | None = None
) -> dict:
    """Keep clean evidence across all layers; doubtful evidence becomes note rows."""
    result: dict[tuple[str, str], dict[str, tuple[int, int]]] = {}
    notes = {} if notes is None else notes
    conflicts: set[tuple[str, str, str]] = set()
    for name in names:
        for master in masters:
            owner = (name, master)
            composite = anchor_writer.layer_of(package.findName(name), master)
            if composite is None or composite.autoLayer:
                continue
            try:
                target, candidates, messages = layer_evidence(
                    package, composite, master, masters, monotonic() + 1.5
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                target, candidates, messages = None, {}, [f"{error}; layer skipped"]
            for message in messages:
                notes.setdefault(owner, []).append(
                    anchor_writer.Change("components", "", message)
                )
            if target is None:
                continue
            destination = result.setdefault(target, {})
            for label, point in candidates.items():
                identity = (*target, label)
                if identity in conflicts:
                    continue
                if label in destination and destination[label] != point:
                    destination.pop(label)
                    conflicts.add(identity)
                    notes.setdefault(target, []).append(
                        anchor_writer.Change(label, "", "conflicting evidence, skipped")
                    )
                else:
                    destination[label] = point
    return result


class ComponentAnchorDerivation(anchor_panel.panel_type()):
    """Preview missing base anchors inferred from the entire current font."""

    TITLE, KEY, ACTION = TITLE, KEY, "Derive"

    def refresh(self) -> None:
        """Contain scan errors inside the panel and disable its write action."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.apply_button.setEnabled(False)
            self.status.setText(str(error))

    def glyph_names(self) -> list[str]:
        import fly.ap.glyph_catalog as glyph_catalog  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

        self.catalog_names = [row[0] for row in glyph_catalog.capture().rows]
        return list(self.catalog_names)

    def planner(self) -> anchor_writer.Planner:
        notes: dict[tuple[str, str], list[anchor_writer.Change]] = {}
        inferred = derived_points(self.package, self.catalog_names, self.masters, notes)

        def changes(glyph: Any, master: str, layer: Any) -> list[anchor_writer.Change]:
            return [
                anchor_writer.Change(name, "missing", str(point), ("set", name, point))
                for name, point in inferred.get((glyph.name, master), {}).items()
            ] + notes.get((glyph.name, master), [])

        return changes


def main() -> Any:
    """Open the all-master inference preview."""
    return scripting.show_script_dialog(ComponentAnchorDerivation, KEY)


if __name__ == "__main__":
    main()
