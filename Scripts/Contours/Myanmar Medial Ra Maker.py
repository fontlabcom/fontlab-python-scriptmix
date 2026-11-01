# this_file: Scripts/Contours/Myanmar Medial Ra Maker.py
# SPDX-License-Identifier: Apache-2.0
"""Generate width-fitted Myanmar medial-ra variants on every FontLab master.

What: Group consonants on the current master. Fit the same group members on
all masters, using each master's mean advance minus its own template enclosure.
Names use the current master's group means floored to tens. Also create eight
unstretched omission variants. Existing names and targets with a bad master
are kept, with the master and reason listed.
How: Read U+1000–U+1020 by Unicode or hexadecimal name. Verify the five pieces:
stem, top rail, top hook, bottom rail, bottom hook. The stem must be tallest;
top pieces above bottom pieces; hooks right of rails. The rails' closing edges
must be on their right, the hooks' on their left. Copy through the shared App
contour copier. Show every target's extension and node/handle bounds on every
master in the Preview table. Apply refuses source data changed since Preview.
Why: Fit this five-part Myanmar outline to consonant width groups.
All-master output keeps the generated glyph structure
consistent across masters; a failed template keeps the entire target.
Use: Select one template, or leave the selection empty to use U+103C. Inspect
Preview and consent to any listed automatic-glyph rebuilds, then Apply.
Each new glyph is recorded as its own Undo step, and the outlines as one more Undo step.
Benefit: Produce a compatible set of fitted medial-ra variants for refinement.

Credit: Independent behaviour-only rewrite of Simon Cozens,
GlyphsScripts/Myanmar Medial Ra Maker.py, MIT, copyright 2017.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.
"""

import math
import re
from typing import Any, NamedTuple

TITLE = "Myanmar Medial Ra Maker"
KEY = "contours_myanmar_medial_ra"
VARIANTS = (
    "",
    ".notop",
    ".notophook",
    ".nobottom",
    ".nobottomhook",
    ".notop.nobottom",
    ".notophook.nobottom",
    ".notop.nobottomhook",
    ".notophook.nobottomhook",
)


class RaRow(NamedTuple):
    """One target, all master layers, frozen geometry and any kept reason."""

    source: str
    target: str
    layers: tuple[tuple[str, Any], ...] = ()
    note: str = ""
    rebuild: tuple[str, ...] = ()
    extensions: tuple[tuple[str, float], ...] = ()
    variant: str = ""
    bounds: tuple[tuple[str, tuple[float, float, float, float]], ...] = ()
    members: tuple[str, ...] = ()
    source_state: tuple[Any, ...] = ()


def width_groups(
    values: list[tuple[str, float]], count: int
) -> list[tuple[int, tuple[str, ...]]]:
    """Optimal contiguous groups, preserving glyph identities and multiplicities.

    Names use means floored to tens. Groups with the same rounded name merge
    their members so that the target is unique. Other masters reuse these
    memberships; they do not regroup by their own advances.
    """
    if (
        not values
        or count < 1
        or any(not math.isfinite(v) or v <= 0 for _, v in values)
    ):
        raise ValueError(
            "Need positive finite consonant widths and at least one width group."
        )
    data = sorted(values, key=lambda pair: (pair[1], pair[0]))
    count = min(count, len({v for _, v in data}))
    origin = data[0][1]
    totals, squares = [0.0], [0.0]
    for _, value in data:
        offset = value - origin
        totals.append(totals[-1] + offset)
        squares.append(squares[-1] + offset * offset)
    length = len(data)
    costs = [[math.inf] * (length + 1) for _ in range(count + 1)]
    cuts = [[0] * (length + 1) for _ in range(count + 1)]
    costs[0][0] = 0
    for groups in range(1, count + 1):
        for end in range(groups, length + 1):
            candidates = []
            for start in range(groups - 1, end):
                total = totals[end] - totals[start]
                error = max(
                    0.0, squares[end] - squares[start] - total * total / (end - start)
                )
                candidates.append((costs[groups - 1][start] + error, start))
            costs[groups][end], cuts[groups][end] = min(candidates)
    grouped: dict[int, list[str]] = {}
    end = length
    for groups in range(count, 0, -1):
        start = cuts[groups][end]
        width = math.floor(sum(v for _, v in data[start:end]) / (end - start) / 10) * 10
        grouped.setdefault(width, []).extend(name for name, _ in data[start:end])
        end = start
    return [
        (width, tuple(sorted(members))) for width, members in sorted(grouped.items())
    ]


def width_classes(values: list[float], count: int) -> list[int]:
    """Return the rounded names of the width groups."""
    return [
        width
        for width, _ in width_groups([(str(i), v) for i, v in enumerate(values)], count)
    ]


def piece_indices(variant: str) -> list[int]:
    """Choose the stem, rails and hooks present in an omission variant."""
    parts = set(variant.split("."))
    return [
        index
        for index, excluded in enumerate(
            (
                False,
                "notop" in parts,
                bool(parts & {"notop", "notophook"}),
                "nobottom" in parts,
                bool(parts & {"nobottom", "nobottomhook"}),
            )
        )
        if not excluded
    ]


def piece_points(
    points: list[tuple[float, float]], piece: int, extension: float
) -> list[tuple[float, float]]:
    """Stretch closing-edge endpoints and move hook bodies on detached copies."""
    if piece == 0:
        return list(points)
    hook = piece in (2, 4)
    last = len(points) - 1
    result = []
    for index, (x, y) in enumerate(points):
        shift = extension if hook else 0.0
        if index in (0, last):
            shift += -extension / 2 if hook else extension / 2
        result.append((x + shift, y))
    return result


def stem_measure(contour: Any) -> float:
    """Distance between the two longest distinct vertical straight edges."""
    nodes = list(contour.nodes())
    edges = sorted(
        (
            (abs(a.y - b.y), float(a.x))
            for a, b in zip(nodes, nodes[1:] + nodes[:1], strict=True)
            if a.isOn() and b.isOn() and a.x == b.x and a.y != b.y
        ),
        reverse=True,
    )
    if len(edges) < 2 or edges[0][1] == edges[1][1]:
        raise ValueError(
            "Stem and bottom hook each need two distinct vertical straight edges."
        )
    return abs(edges[0][1] - edges[1][1])


PIECES = ("stem", "top rail", "top hook", "bottom rail", "bottom hook")


def point_bounds(
    points: list[tuple[float, float]],
) -> tuple[float, float, float, float]:
    """Return bounds of nodes and handles, a conservative contour envelope."""
    if not points or any(not math.isfinite(v) for point in points for v in point):
        raise ValueError("Contours need finite node coordinates.")
    xs, ys = zip(*points, strict=True)
    return min(xs), min(ys), max(xs), max(ys)


def template_contours(layer: Any) -> tuple[list[Any], float]:
    """Copy five contours, verify piece roles and stretch sides, measure enclosure."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
    from fly import qt

    problem = glyph_copies.source_problem(layer)
    if problem:
        raise ValueError(problem)
    if layer.isMaskLayer or layer.isService:
        raise ValueError("Choose a foreground master layer.")
    if not math.isfinite(layer.advanceWidth):
        raise ValueError("Template advance must be finite.")
    contours = contour_copy.copy_contours(layer, qt.QtGui.QTransform())
    if len(contours) != 5 or any(not c.closed for c in contours):
        raise ValueError(
            "Template needs exactly five closed contours in the documented order."
        )
    boxes = [
        point_bounds([(float(n.x), float(n.y)) for n in c.nodes()]) for c in contours
    ]
    if boxes[0][3] - boxes[0][1] <= max(b[3] - b[1] for b in boxes[1:]):
        raise ValueError("piece 0 (stem): must be the tallest piece.")
    centres = [((a + c) / 2, (b + d) / 2) for a, b, c, d in boxes]
    if min(centres[i][1] for i in (1, 2)) <= max(centres[i][1] for i in (3, 4)):
        raise ValueError(
            "pieces 1/2 (top rail/hook): must lie above bottom pieces 3/4."
        )
    for rail, hook in ((1, 2), (3, 4)):
        if centres[hook][0] <= centres[rail][0] or boxes[hook][2] <= boxes[rail][2]:
            raise ValueError(
                f"piece {hook} ({PIECES[hook]}): must lie to the right of its rail."
            )
    for index, contour in enumerate(contours[1:], start=1):
        nodes = list(contour.nodes())
        label = f"piece {index} ({PIECES[index]})"
        if (
            len(nodes) < 3
            or not nodes[0].isOn()
            or not nodes[-1].isOn()
            or nodes[0].x != nodes[-1].x
        ):
            raise ValueError(
                f"{label}: start and end must form a vertical straight edge."
            )
        hook = index in (2, 4)
        wanted = boxes[index][0] if hook else boxes[index][2]
        if nodes[0].x != wanted:
            side = "left" if hook else "right"
            raise ValueError(f"{label}: stretch edge must be its {side} edge.")
    box = layer.boundingBox
    enclosure = (
        float(box.width() + 2 * box.x())
        - stem_measure(contours[0])
        - stem_measure(contours[4])
    )
    if not math.isfinite(enclosure) or enclosure <= 0:
        raise ValueError("The measured enclosure must be positive.")
    return contours, enclosure


def consonant_widths(
    package: Any, records: list[Any]
) -> tuple[list[tuple[str, float]], list[RaRow]]:
    """Read named current-master advances; retain invalid consonants as kept rows."""
    widths, notes = [], []
    for record in records:
        codes = [int(code) for code in record.unicodes]
        match = re.fullmatch(r"(?:uni)?([0-9A-Fa-f]{4})", str(record.name))
        if match:
            codes.append(int(match[1], 16))
        if not any(0x1000 <= code <= 0x1020 for code in codes):
            continue
        glyph = package.findName(str(record.name))
        layer = glyph.findLayer(package.master) if glyph is not None else None
        if layer is None or layer.isNull:
            notes.append(
                RaRow(str(record.name), "", note=f"kept: no {package.master} layer")
            )
        elif not math.isfinite(layer.advanceWidth) or layer.advanceWidth <= 0:
            notes.append(
                RaRow(str(record.name), "", note="kept: invalid consonant width")
            )
        else:
            widths.append((str(record.name), float(layer.advanceWidth)))
    return widths, notes


def master_extension(
    package: Any, master: str, members: tuple[str, ...], enclosure: float
) -> float:
    """Mean advance of the same consonant members, minus this master's enclosure."""
    widths = []
    for name in members:
        glyph = package.findName(name)
        layer = glyph.findLayer(master) if glyph is not None else None
        if (
            layer is None
            or layer.isNull
            or not math.isfinite(layer.advanceWidth)
            or layer.advanceWidth <= 0
        ):
            raise ValueError(
                f"{master}: missing or invalid consonant advance for {name}"
            )
        widths.append(float(layer.advanceWidth))
    return sum(widths) / len(widths) - enclosure


def fitted_bounds(
    contours: list[Any], variant: str, extension: float
) -> tuple[float, float, float, float]:
    """Envelope of all fitted nodes and handles, for the pre-write table."""
    points = []
    for index in piece_indices(variant):
        points.extend(
            piece_points(
                [(float(n.x), float(n.y)) for n in contours[index].nodes()],
                index,
                extension,
            )
        )
    return point_bounds(points)


def survey(
    package: Any, source: str, records: list[Any], count: int, facts: Any, consent: bool
) -> list[RaRow]:
    """Plan each target on every master. One failed master keeps the whole target."""
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402

    glyph = package.findName(source)
    layers, templates, problems, state = [], {}, [], []
    for master in package.masters:
        layer = glyph.findLayer(master) if glyph is not None else None
        try:
            contours, enclosure = template_contours(layer)
        except (ValueError, RuntimeError, TimeoutError) as error:
            problems.append(f"{master}: {error}")
            continue
        layers.append((str(master), layer))
        templates[str(master)] = (contours, enclosure)
        state.append(
            (
                str(master),
                float(layer.advanceWidth),
                tuple(
                    (
                        bool(c.closed),
                        tuple(
                            (float(n.x), float(n.y), str(n.name), int(n.nodeState))
                            for n in c.nodes()
                        ),
                    )
                    for c in contours
                ),
            )
        )
    widths, rows = consonant_widths(package, records)
    topologies = {
        master: tuple(
            (bool(contour.closed), tuple(bool(node.isOn()) for node in contour.nodes()))
            for contour in contours
        )
        for master, (contours, _) in templates.items()
    }
    if topologies:
        first_master, expected = next(iter(topologies.items()))
        problems.extend(
            f"{master}: template node topology differs from {first_master}"
            for master, topology in topologies.items()
            if topology != expected
        )
    groups = width_groups(widths, count) if widths else []
    if not widths:
        rows.append(
            RaRow(source, "", note="kept: no consonant widths; only omission variants")
        )
    targets = [
        (f"medial-ra.w{width}", width, members, variant)
        for width, members in groups
        for variant in VARIANTS
    ]
    targets += [("medial-ra", None, (), variant) for variant in VARIANTS[1:]]
    effects = glyph_creation.auto_candidates(
        package, facts, [base + variant for base, _, _, variant in targets]
    )
    for base, width, members, variant in targets:
        target = base + variant
        reasons, extensions, boxes = list(problems), [], []
        for master, (contours, enclosure) in templates.items():
            try:
                extension = (
                    master_extension(package, master, members, enclosure)
                    if members
                    else 0.0
                )
                if members and extension <= 0:
                    reasons.append(
                        f"{master}: w{width}: not wider than the template enclosure ({enclosure:g})"
                    )
            except ValueError as error:
                reasons.append(str(error))
                continue
            extensions.append((master, extension))
            boxes.append((master, fitted_bounds(contours, variant, extension)))
        rebuild = effects.get(target, ())
        if package.findName(target) is not None:
            reasons.append("name exists")
        if rebuild and not consent:
            reasons.append("may rebuild auto " + ", ".join(rebuild))
        rows.append(
            RaRow(
                source,
                target,
                tuple(layers),
                "kept: " + "; ".join(reasons) if reasons else "",
                rebuild,
                tuple(extensions),
                variant,
                tuple(boxes),
                members,
                tuple(state),
            )
        )
    return rows


def prepare(rows: list[RaRow]) -> list[Any]:
    """Prepare every master on detached contours before any Add Glyph command."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402

    jobs = []
    for row in rows:
        if row.note:
            continue
        fitted = []
        for master, layer in row.layers:
            contours, _ = template_contours(layer)
            chosen = []
            for index in piece_indices(row.variant):
                contour = contours[index]
                nodes = list(contour.nodes())
                points = piece_points(
                    [(float(n.x), float(n.y)) for n in nodes],
                    index,
                    dict(row.extensions)[master],
                )
                for node, (x, y) in zip(nodes, points, strict=True):
                    node.x, node.y = x, y
                chosen.append(contour)
            fitted.append((master, chosen, glyph_copies.half_up(layer.advanceWidth)))
        jobs.append((row.target, fitted))
    return jobs


def default_source(records: list[Any]) -> str:
    """Use the encoded medial ra when the selection is not one template glyph."""
    return next(
        (str(record.name) for record in records if 0x103C in record.unicodes), ""
    )


def preview_key(rows: list[RaRow]) -> tuple[Any, ...]:
    """Immutable target and source values that the user saw before Apply."""
    return tuple(
        (
            r.source,
            r.target,
            r.note,
            r.rebuild,
            r.extensions,
            r.bounds,
            r.members,
            r.source_state,
        )
        for r in rows
    )


def panel_type() -> type:
    """Use the shared non-modal creation panel, with a complete multi-master preview."""
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
    import fly.ap.history as history  # noqa: PLR0402
    from fly import ap, qt

    class MedialRaPanel(glyph_copies.panel_type()):
        """Every glyph, each master's extension and node/handle bounds before Apply."""

        TITLE, KEY, NOUN, ACTION = TITLE, KEY, "template glyphs", "Apply"
        HEADERS = ("New glyph", "Extensions by master", "Node/handle bounds and action")
        WIDTH = 860

        def build_controls(self) -> None:
            """Choose width groups and provide an explicit Preview action."""
            self.group_count = qt.QtGui.QSpinBox()
            self.group_count.setRange(1, 5)
            self.group_count.setValue(5)
            self.add_row("Width groups", self.group_count)
            self.watch(self.group_count.valueChanged)
            self.preview_button = qt.QtGui.QPushButton("Preview")
            self.add_row("", self.preview_button)
            self.watch(self.preview_button.clicked, self.refresh)

        def plan(self) -> list[RaRow]:
            """Resolve the encoded medial ra before the shared selection preflight."""
            self.font_package()
            if not self.names:
                source = default_source(list(ap.fontlab.CurrentFont().glyphs))
                if source:
                    self.names = [source]
            return super().plan()

        def survey(self, package: Any, facts: Any, allow_rebuild: bool) -> list[RaRow]:
            """Choose the explicit template or U+103C, then survey every master."""
            records = list(ap.fontlab.CurrentFont().glyphs)
            source = (
                self.names[0] if len(self.names) == 1
                else default_source(records) if not self.names else ""
            )
            if not source:
                return [
                    RaRow(
                        ", ".join(self.names),
                        "",
                        note="kept: select exactly one five-contour template, or encode it U+103C",
                    )
                ]
            return survey(
                package,
                source,
                records,
                int(self.group_count.value),
                facts,
                allow_rebuild,
            )

        def jobs(self, rows: list[RaRow]) -> list[Any]:
            """Prepare all permitted master layers."""
            return prepare(rows)

        def write(self, package: Any, rows: list[RaRow]) -> dict[str, Any]:
            """Refuse a changed preview; create all masters through the shared writer."""
            if preview_key(rows) != preview_key(self.rows):
                raise ValueError("Font data changed. Press Preview before Apply.")
            return glyph_copies.create(
                package,
                self.jobs(rows),
                TITLE,
                history.scan_auto_facts(package),
                allow_rebuild=self.consented(),
            )

        def cells(self, row: RaRow) -> list[str]:
            """Show every extension and conservative bounding box, including kept rows."""
            measured = dict(row.extensions)
            extensions = "; ".join(
                f"{m}: {measured[m]:+g}" if m in measured else f"{m}: unavailable"
                for m in self.font_package().masters
            )
            bounds = "; ".join(
                f"{m}: [{', '.join(f'{v:g}' for v in box)}]" for m, box in row.bounds
            )
            action = row.note or f"create on {len(row.layers)} masters"
            if row.rebuild and not row.note:
                action += " · may rebuild auto " + ", ".join(row.rebuild)
            return [row.target or row.source, extensions, bounds + " · " + action]

        def intro(self) -> str:
            """Name the grouping master and state the history granularity."""
            return (
                f"Preview: groups from {self.font_package().master}; fit every master. Bounds include nodes and handles. "
                "Each new glyph is recorded as its own Undo step, and the outlines as one more Undo step."
            )

    return MedialRaPanel


def main() -> Any:
    """Open or replace the owned generator panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
