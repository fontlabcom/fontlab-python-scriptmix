# this_file: Scripts/Contours/Outline Effect.py
# SPDX-License-Identifier: Apache-2.0
"""Turn the selected glyphs into outlined (hollow) letters of a chosen line width.

What it does:
    For each selected glyph and chosen master, the script replaces the
    contours of the layer with a ring of the chosen line width, centred on the
    old outline. The advance width does not change.

How it works:
    A non-modal panel lists every glyph and master with its contour count, or
    the reason why the layer is skipped. Apply first builds every ring: Qt's
    path stroker draws the contours with round joins and caps, the script
    turns the stroke into closed FontLab contours (cubic handles stay
    cubic), and FontGate's Remove Overlap cleans the small loops that the
    stroker leaves inside corners. Then it writes all layers in one Undo
    step through the shared module fly.ap.history: each old contour element is
    removed and the ring is added as one new element. Images and empty
    elements stay in the layer. After the write it
    counts the contours again and reports any difference. The path-to-contour
    step and the panel are shared (fly.ap.contour_copy, fly.ap.selection_panel).

Why this design:
    - FontLab has no Python call that strokes an outline, so the script uses
      the Qt stroker and FontLab's own overlap removal. FontGate puts the
      result on the integer grid.
    - The geometry is built before history starts, so a failed stroke never
      leaves a half-edited layer.
    - Layers with components are skipped: the components would stay filled.
      Locked layers are skipped too. Element names and notes of the old
      outline do not carry over to the ring.
    - Automatic layers and glyphs with automatic layers are never edited. A
      base of automatic composites is skipped unless you tick "Edit bases of
      auto glyphs anyway": FontLab then rebuilds those composites, can drop
      their anchors and locks, and Undo does not restore them.
    - Apply is refused while FontLab has pending glyph updates. The script
      does not call UpdateAll (fl#8537).

How to use:
    Select glyphs in the Font window. Run the script. Set the line width,
    choose the current master or all masters, check the table and press
    Outline. Each Apply is recorded as one Undo step.

Benefit:
    An inline or outline style starts from the real drawing, in every master,
    in one step.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_outline_effect.py, "Outline Effect").
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Outline Effect"
KEY = "generate_outline_effect"


@dataclass(frozen=True)
class Row:
    """One glyph/master layer. ``note`` is empty when the layer gets a ring."""

    glyph: Any
    master: str
    layer: Any
    contours: int = 0
    note: str = ""


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull


def ring_shape(layer: Any, line: int) -> Any:
    """Return one flShape: the stroked outline of ``layer`` with join loops removed."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    from fly import ap, qt

    QtGui, QtCore = qt.QtGui, qt.QtCore
    path = QtGui.QPainterPath()
    for shape in contour_copy.contour_shapes(layer):
        for contour in shape.contours:
            path.addPath(contour.cloneMapped(shape.transform).path())
    stroker = QtGui.QPainterPathStroker()
    stroker.setWidth(line)
    stroker.setJoinStyle(QtCore.Qt.RoundJoin)
    stroker.setCapStyle(QtCore.Qt.RoundCap)
    raw = ap.fontlab.flShape()
    raw.addContours(contour_copy.path_contours(stroker.createStroke(path)), True)
    merged = ap.fontgate.fgShape()
    raw.convertToFgShape(merged)
    merged.removeOverlap()
    return ap.fontlab.flShape(merged)


def layer_note(layer: Any, reason: str) -> str:
    """Return why ``layer`` gets no ring, or "" when it can get one."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    if layer.autoLayer:
        return "auto layer (skipped)"
    if reason:
        return f"{reason} (skipped)"
    if layer.isLocked:
        return "locked layer (skipped)"
    if any(shape.isComponent for shape in layer.shapes):
        return "built from components (skipped)"
    if not contour_copy.contour_shapes(layer):
        return "no outline (skipped)"
    return ""


def survey(
    package: Any,
    names: Sequence[str],
    masters: Sequence[str],
    facts: Any,
    allow_bases: bool,
) -> list[Row]:
    """Plan every glyph/master. Change nothing."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.history as history  # noqa: PLR0402

    rows: list[Row] = []
    for name in names:
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            continue
        reason = history.refusal(
            facts, str(glyph.name), "geometry", allow_bases=allow_bases
        )
        for master in masters:
            layer = glyph.findLayer(master)
            if not _valid(layer):
                rows.append(Row(glyph, master, None, note="no layer in this master"))
                continue
            note = layer_note(layer, reason)
            count = (
                0
                if note
                else sum(len(s.contours) for s in contour_copy.contour_shapes(layer))
            )
            rows.append(Row(glyph, master, layer, count, note))
    return rows


def outline(
    rows: Sequence[Row], line: int, facts: Any, allow_bases: bool
) -> dict[str, Any]:
    """Replace the outline of every planned layer by its ring, as ONE Undo step.

    Return ``{"layers", "glyphs", "contours", "mismatches"}``; ``contours``
    counts the ring contours. Nothing to do returns zeros and makes no history
    call. A refusal raises ValueError; a failure after history started raises
    RuntimeError with the Undo hint.
    """
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    todo = [r for r in rows if not r.note]
    if not todo:
        return {"layers": 0, "glyphs": 0, "contours": 0, "mismatches": []}
    prepared = [
        (row, ring_shape(row.layer, line)) for row in todo
    ]  # all geometry before history
    glyphs = list({str(r.glyph.name): r.glyph for r in todo}.values())

    def mutate() -> None:
        for row, ring in prepared:
            for shape in contour_copy.contour_shapes(row.layer):
                row.layer.removeShape(shape)
            row.layer.addShape(ring)

    def read_back() -> list[str]:
        found = []
        for row, ring in prepared:
            shapes = contour_copy.contour_shapes(row.layer)
            count = sum(len(s.contours) for s in shapes)
            if (
                len(shapes) != 1
                or shapes[0].id != ring.id
                or count != ring.contoursCount
            ):
                found.append(
                    f"{row.glyph.name} · {row.master}: {count} contours, planned {ring.contoursCount}"
                )
        return found

    done = history.commit(
        TITLE, [r.layer for r in todo], glyphs, mutate,
        operation="geometry", facts=facts, allow_bases=allow_bases, read_back=read_back,
    )  # fmt: skip
    return {
        "layers": len(todo),
        "glyphs": len(glyphs),
        "contours": sum(ring.contoursCount for _, ring in prepared),
        "mismatches": list(done.mismatches),
    }


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.layer_writer as layer_writer  # noqa: PLR0402
    import fly.ap.selection_panel as selection_panel  # noqa: PLR0402
    from fly import qt

    QtGui = qt.QtGui

    class OutlineEffectPanel(selection_panel.panel_type()):
        """Line width, masters, bases opt-in, preview table, status and buttons."""

        TITLE, KEY, ACTION = TITLE, KEY, "Outline"
        HEADERS = ("Glyph · master", "Contours now")

        def build_controls(self) -> None:
            """Line width."""
            self.line = QtGui.QSpinBox()
            self.line.setRange(2, 400)
            self.line.setSuffix(" units")
            self.line.setValue(30)
            self.add_row("Line width", self.line)

        def plan_rows(self, package: Any, masters: list[str]) -> list[Row]:
            """Plan with fresh auto-layer facts and the bases opt-in."""
            return survey(
                package,
                self.names,
                masters,
                history.scan_auto_facts(package),
                self.consented(),
            )

        def cells(self, row: Row) -> list[str]:
            """Glyph · master, and the note or the contour count."""
            return [f"{row.glyph.name} · {row.master}", row.note or str(row.contours)]

        def pending(self, todo: Sequence[Row]) -> str:
            """Status before Apply."""
            return (
                f"{layer_writer.plural(len(todo), 'layer')} will be outlined"
                if todo
                else "Nothing to outline"
            )

        def write(self, package: Any, rows: list[Row]) -> dict[str, Any]:
            """Build the rings, then replace the outlines with fresh facts. One Undo step."""
            return outline(
                rows,
                int(self.line.value),
                history.scan_auto_facts(package),
                self.consented(),
            )

        def result_text(self, result: dict[str, Any]) -> str:
            """Status after Apply."""
            if not result["layers"]:
                return "Nothing to outline"
            plural = layer_writer.plural
            return (
                f"Outlined {plural(result['layers'], 'layer')} of {plural(result['glyphs'], 'glyph')} "
                f"({plural(result['contours'], 'contour')})"
            )

    return OutlineEffectPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
