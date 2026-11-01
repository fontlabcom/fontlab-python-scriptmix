# this_file: Scripts/Kerning/Steal Kerning From Next Pair.py
# SPDX-License-Identifier: Apache-2.0
"""Match one selected pair's outline gap to the following pair at a set height.

What: Measure four consecutive same-master glyph slots as two pairs. Set the
first pair's kerning so its gap matches the second pair at the chosen height.
How: Read own and transformed component contours. Elevate quadratic spans to
cubics, flatten with the shared twelve-step curve helper, then find horizontal
ray crossings. Write the integer gap difference plus the second pair's effective
kerning through the shared checked kerning writer. Preserve target exceptions.
Why: The Metrics bar accepts a kerning value, but does not derive it from two
outline gaps at a specified height. Curve flattening is an approximation.
Use: Select four adjacent glyphs in one Glyph-window text block. The capture
includes selected OR active slots; an extra active slot or a lone active slot
is refused. Set Height (default: half the shown master's x-height), then Preview
and Apply. Use a height that crosses all four outlines. No cursor API is needed.
Benefit: Compare pairs such as AV and VA at a repeatable measurement height.
The non-modal panel keeps the height. Each changing action is recorded as one
Undo step. Zero gaps are valid; a computed zero removes the target pair record.
Open contours are skipped and reported by glyph name. A missing closed-outline
crossing refuses the complete action. Flat edges at the measuring height count.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Kerning/Steal Kerning From Next Pair at Cursor's Y.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.
"""

import math
from itertools import pairwise
from time import monotonic
from typing import Any

TITLE = "Steal Kerning From Next Pair"
KEY = "kerning_steal_next_pair"
Point = tuple[float, float, bool]


def quadratic_cubics(points: list[Point]) -> list[Point]:
    """Elevate quadratic spans, including implied on-curves, before flattening."""
    if not points:
        return []
    start = next((i for i, point in enumerate(points) if point[2]), None)
    if start is None:
        first, last = points[0], points[-1]
        origin = ((first[0] + last[0]) / 2, (first[1] + last[1]) / 2, True)
        ordered = [origin, *points, origin]
    else:
        ordered = points[start:] + points[:start] + [points[start]]
    result, handles = [ordered[0]], []
    current = ordered[0]
    for point in ordered[1:]:
        if not point[2]:
            handles.append(point)
            continue
        for index, handle in enumerate(handles):
            end = (
                point
                if index == len(handles) - 1
                else (
                    (handle[0] + handles[index + 1][0]) / 2,
                    (handle[1] + handles[index + 1][1]) / 2,
                    True,
                )
            )
            result.extend(
                [
                    (
                        current[0] + (handle[0] - current[0]) * 2 / 3,
                        current[1] + (handle[1] - current[1]) * 2 / 3,
                        False,
                    ),
                    (
                        end[0] + (handle[0] - end[0]) * 2 / 3,
                        end[1] + (handle[1] - end[1]) * 2 / 3,
                        False,
                    ),
                    end,
                ]
            )
            current = end
        if not handles:
            result.append(point)
        current, handles = point, []
    return result


def extents(
    layer: Any, height: float, *, glyph_name: str = "", notices: list[str] | None = None
) -> tuple[float, float]:
    """Find the leftmost/rightmost scanline crossings of the decomposed outline."""
    import fly.ap.masters as masters  # noqa: PLR0402

    contours = masters.layer_contours(layer)
    kinds = [
        (bool(c.isTT), bool(c.closed)) for shape in layer.shapes for c in shape.contours
    ]
    if len(contours) != len(kinds):
        raise ValueError("Outline structure changed during measurement; Preview again.")
    name = glyph_name or str(layer.name)
    skipped = sum(not closed for _, closed in kinds)
    note = f"{name}: skipped {skipped} open contour{'' if skipped == 1 else 's'}."
    if skipped and notices is not None:
        notices.append(note)
    crossings = []
    deadline = monotonic() + 2.0
    for points, (is_quadratic, closed) in zip(contours, kinds, strict=True):
        if monotonic() >= deadline:
            raise TimeoutError("Outline measurement exceeded its per-glyph time limit.")
        if not closed:
            continue
        polygon = masters.polygon(quadratic_cubics(points) if is_quadratic else points)
        if any(not math.isfinite(value) for point in polygon for value in point):
            raise ValueError("Outline coordinates must be finite.")
        for (x1, y1), (x2, y2) in pairwise(polygon + polygon[:1]):
            if min(y1, y2) <= height <= max(y1, y2):
                if y1 == y2:
                    crossings.extend((x1, x2))
                else:
                    crossings.append(x1 + (height - y1) * (x2 - x1) / (y2 - y1))
    if not crossings:
        detail = f" {note}" if skipped else ""
        raise ValueError(
            f"{name}: No closed outline crossing at height {height:g} in {layer.name}.{detail}"
        )
    return min(crossings), max(crossings)


def target_key(groups: dict, records: dict, left: str, right: str) -> tuple:
    """Keep the most specific existing exception; otherwise use native side groups."""
    sides = []
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
        sides.append((matches[0], "groupMode") if matches else (name, "glyphMode"))
    glyphs = ((left, "glyphMode"), (right, "glyphMode"))
    candidates = (glyphs, (glyphs[0], sides[1]), (sides[0], glyphs[1]), tuple(sides))
    return next((pair for pair in candidates if pair in records), tuple(sides))


def plan(height: float, expected_id: int | None = None) -> dict:
    """Read four selected slots, their outline gaps and the complete kerning snapshot."""
    import fly.ap.kerning_batch as kerning
    import fly.ap.layer_selection as selection
    import fly.ap.scripting as scripting  # noqa: PLR0402

    if not math.isfinite(height):
        raise ValueError("Height must be a finite number.")
    captured = selection.capture(monotonic() + 2.0)
    package = scripting.current_package()
    if (
        package is None
        or package.id != captured.context[0]
        or (expected_id is not None and package.id != expected_id)
    ):
        raise ValueError("Activate the original font and select four glyphs.")
    rows = captured.occurrences
    if captured.context[2] != "editor" or len(rows) != 4:
        raise ValueError("Select exactly four adjacent glyphs in a Glyph window.")
    if any(
        a.block_id != b.block_id or b.index != a.index + 1 for a, b in pairwise(rows)
    ):
        raise ValueError("Select four consecutive glyphs in one text block.")
    master = str(rows[0].layer.name)
    if master not in package.masters or any(
        not row.layer.isMasterLayer or str(row.layer.name) != master for row in rows
    ):
        raise ValueError("All four glyphs must show the same declared master.")
    widths = [float(row.layer.advanceWidth) for row in rows]
    if any(not math.isfinite(width) or width < 0 for width in widths):
        raise ValueError("Advance widths must be finite and nonnegative.")
    before = kerning.snapshot_kerning(package, typed=True)
    notices: list[str] = []
    bounds = [
        extents(row.layer, height, glyph_name=row.glyph_name, notices=notices)
        for row in rows
    ]
    notices = list(dict.fromkeys(notices))
    gaps = (
        widths[0] - bounds[0][1] + bounds[1][0],
        widths[2] - bounds[2][1] + bounds[3][0],
    )
    reference = float(
        scripting.kerning_pair_value(
            package.kerning(master), rows[2].glyph_name, rows[3].glyph_name
        )
    )
    if not math.isfinite(reference):
        raise ValueError("Reference kerning must be finite.")
    value = int(gaps[1] - gaps[0] + reference)
    pair = target_key(
        before.groups[master],
        before.pairs[master],
        rows[0].glyph_name,
        rows[1].glyph_name,
    )
    return {
        "package": package,
        "selection": captured,
        "before": before,
        "height": height,
        "edits": {master: {pair: None if value == 0 else value}},
        "value": value,
        "record": " · ".join(
            ("@" if mode == "groupMode" else "") + name for name, mode in pair
        ),
        "notices": notices,
        "fingerprint": (
            captured,
            before,
            tuple(widths),
            tuple(bounds),
            reference,
            pair,
            tuple(notices),
        ),
        "names": tuple(row.glyph_name for row in rows),
        "gaps": gaps,
    }


def write(preview: dict) -> dict:
    """Re-measure before writing; refuse stale selection, outlines or kerning."""
    import fly.ap.kerning_batch as kerning

    current = plan(preview["height"], preview["package"].id)
    if current["fingerprint"] != preview["fingerprint"]:
        raise ValueError("Pair preview changed; press Preview again.")
    try:
        changed = kerning.write_kerning(
            current["package"], preview["edits"], TITLE, expected=preview["before"]
        )
    except RuntimeError as error:
        raise RuntimeError(
            f"{error} Native changes may remain; use Edit > Undo."
        ) from error
    return {
        "value": preview["value"],
        "changed": changed,
        "notices": preview["notices"],
    }


def run(height: float) -> dict:
    """Measure and apply a live four-slot pair action without opening a panel."""
    return write(plan(height))


def default_height(package: Any) -> float:
    """Use half the shown master's x-height, falling back to the current master."""
    import fly.ap.layer_selection as selection
    from fly import fl

    if package is None:
        return 0.0
    captured = selection.capture(monotonic() + 2.0)
    if captured.context[0] != package.id:
        raise ValueError("The active font changed; reopen this tool.")
    rows = captured.occurrences
    master = str(rows[0].layer.name) if rows else str(package.master)
    if master not in package.masters:
        master = str(package.master)
    return float(fl.FontMetrics(package, master).xHeight) / 2


def panel_type() -> type:
    """Build a small owned non-modal panel using the shared font-bound shell."""
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    class GapPanel(scripting.font_info_dialog_type()):
        """Retain height, and bind every Apply to the exact visible measurement."""

        def __init__(self, parent: Any = None) -> None:
            """Capture the original font and build all controls before preview."""
            super().__init__(
                parent,
                title=TITLE,
                key=KEY,
                subtitle="Select four adjacent glyphs. Match the first pair to the second at Height.",
            )

        def setup(self) -> None:
            """Default the measurement height to half the shown master's x-height."""
            captured = scripting.current_package()
            default = default_height(captured)
            self.height_edit = qt.QtGui.QLineEdit(f"{default:g}")
            self.form.addWidget(qt.QtGui.QLabel("Height"), 0, 0)
            self.form.addWidget(self.height_edit, 0, 1)
            self.preview_button = qt.QtGui.QPushButton("Preview")
            self.form.addWidget(self.preview_button, 0, 2)
            self._connect(
                self.height_edit.textChanged, lambda *a: self.invalidate_preview()
            )
            self._connect(self.preview_button.clicked, lambda *a: self.refresh())

        def invalidate_preview(self) -> None:
            """Disable Apply as soon as the height changes."""
            self._preview_valid = False
            self.apply_button.setEnabled(False)

        def refresh(self) -> None:
            """Show the exact target, reference and integer value before Apply."""
            self.invalidate_preview()
            self.ensure_font()
            try:
                height = float(self.height_edit.text)
            except ValueError as error:
                raise ValueError("Height must be a finite number.") from error
            self.pair_preview = plan(height, self.package_id)
            data = self.pair_preview
            self.rows(
                ["Target", "Reference", "Record", "Height", "Computed value"],
                [
                    (
                        " ".join(data["names"][:2]),
                        " ".join(data["names"][2:]),
                        data["record"],
                        height,
                        data["value"],
                    )
                ],
            )
            self._preview_valid = True
            self.apply_button.setEnabled(True)
            self.status.setText(
                f"Unkerned gaps: {data['gaps'][0]:g} and {data['gaps'][1]:g} units. "
                + " ".join(data["notices"])
            )

        def apply(self) -> None:
            """Write one source-bound action; report no-op distinctly."""
            self.ensure_preview()
            result = write(self.pair_preview)
            self.refresh()
            if result["value"] == 0:
                message = (
                    "Pair record removed."
                    if result["changed"]
                    else "Pair record already absent."
                )
            else:
                message = f"Kerning {'set to' if result['changed'] else 'unchanged at'} {result['value']} units."
            self.status.setText(message + " " + " ".join(result["notices"]))

    return GapPanel


def main() -> Any:
    """Open or replace this tool's shared-lifetime panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
