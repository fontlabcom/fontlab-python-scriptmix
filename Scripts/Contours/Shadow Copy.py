# this_file: Scripts/Contours/Shadow Copy.py
# SPDX-License-Identifier: Apache-2.0
"""Add a shifted copy of the outline behind each selected glyph, as its own element.

What it does:
    For each selected glyph and chosen master, the script copies the contours
    of the layer, moves the copy by a horizontal and a vertical offset, and
    puts it behind the outline as a new element named "shadow". The original
    outline and the advance width do not change.

How it works:
    A non-modal panel lists every glyph and master with its contour count, or
    the reason why the layer is skipped. Apply reads the font again and
    writes all layers in one Undo step through the shared module
    fly.ap.history. The copy is made from each contour with its element
    transform applied; FontLab can drop node names and raw node flags in a
    contour copy (fl#8569), so the script copies them back and clears the
    selection bit. After the write it checks that every layer starts with the
    shadow element and reports any difference. The contour copy and the panel
    are shared (fly.ap.contour_copy, fly.ap.selection_panel).

Copy limits:
    Only node names and raw node flags are repaired (fl#8569); selection is
    cleared. Other node properties and contour names are not repaired.
    Copied contours are merged into one element; source element names and
    notes are not copied.

Why this design:
    - A separate element is easy to recolour, move or delete as one unit, and
      a layer font workflow can split it into shadow glyphs. Filled together
      with the outline it gives an extruded silhouette.
    - Layers with components are skipped: a copy of the contours alone would
      not be the full glyph. Locked layers and layers that already hold a
      shadow element are skipped too.
    - Automatic layers and glyphs with automatic layers are never edited. A
      base of automatic composites is skipped unless you tick "Edit bases of
      auto glyphs anyway": FontLab then rebuilds those composites, can drop
      their anchors and locks, and Undo does not restore them.
    - Apply is refused while FontLab has pending glyph updates. The script
      does not call UpdateAll (fl#8537). The panel binds to the font that was
      current when it opened.

How to use:
    Select glyphs in the Font window. Run the script. Set the offsets, choose
    the current master or all masters, check the table and press Add Shadow.
    The panel stays open; press "Use selection" after you select other
    glyphs. Each Apply is recorded as one Undo step.

Benefit:
    Shadowed or extruded display styles start from the real outline in one
    step, and the shadow stays a separate element.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_shadow.py, "Shadow Copy").
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Shadow Copy"
KEY = "generate_shadow"
SHADOW = "shadow"  # element name of the added copy


@dataclass(frozen=True)
class Row:
    """One glyph/master layer. ``note`` is empty when the layer gets a shadow."""

    glyph: Any
    master: str
    layer: Any
    contours: int = 0
    note: str = ""


def _valid(layer: Any) -> bool:
    """True for a real native layer object."""
    return layer is not None and not layer.isNull


def layer_note(layer: Any, reason: str) -> str:
    """Return why ``layer`` gets no shadow, or "" when it can get one."""
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    if layer.autoLayer:
        return "auto layer (skipped)"
    if reason:
        return f"{reason} (skipped)"
    if layer.isLocked:
        return "locked layer (skipped)"
    if any(shape.isComponent for shape in layer.shapes):
        return "built from components (skipped)"
    if any(str(shape.name) == SHADOW for shape in layer.shapes):
        return "has a shadow already (skipped)"
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


def add_shadows(
    rows: Sequence[Row], dx: int, dy: int, facts: Any, allow_bases: bool
) -> dict[str, Any]:
    """Insert one shifted shadow element first in every planned layer, as ONE Undo step.

    Return ``{"layers", "glyphs", "contours", "mismatches"}``. Nothing to do
    returns zeros and makes no history call. A refusal raises ValueError; a
    failure after history started raises RuntimeError with the Undo hint.
    """
    import fly.ap.contour_copy as contour_copy  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.history as history  # noqa: PLR0402
    from fly import ap, qt

    fontlab = ap.fontlab
    todo = [r for r in rows if not r.note]
    if not todo:
        return {"layers": 0, "glyphs": 0, "contours": 0, "mismatches": []}
    move = qt.QtGui.QTransform(1, 0, 0, 1, dx, dy)
    prepared = [
        (row, contour_copy.copy_contours(row.layer, move)) for row in todo
    ]  # read before history
    glyphs = list({str(r.glyph.name): r.glyph for r in todo}.values())

    def mutate() -> None:
        for row, contours in prepared:
            shape = fontlab.flShape()
            shape.addContours(contours, True)
            shape.name = SHADOW
            row.layer.insertShape(0, shape)

    def read_back() -> list[str]:
        found = []
        for row, contours in prepared:
            first = row.layer.shapes[0] if len(row.layer.shapes) else None
            if (
                first is None
                or str(first.name) != SHADOW
                or len(first.contours) != len(contours)
            ):
                found.append(
                    f"{row.glyph.name} · {row.master}: no shadow element after the write"
                )
        return found

    done = history.commit(
        TITLE, [r.layer for r in todo], glyphs, mutate,
        operation="geometry", facts=facts, allow_bases=allow_bases, read_back=read_back,
    )  # fmt: skip
    return {
        "layers": len(todo),
        "glyphs": len(glyphs),
        "contours": sum(len(c) for _, c in prepared),
        "mismatches": list(done.mismatches),
    }


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.layer_writer as layer_writer  # noqa: PLR0402
    import fly.ap.selection_panel as selection_panel  # noqa: PLR0402
    from fly import qt

    QtGui = qt.QtGui

    class ShadowPanel(selection_panel.panel_type()):
        """Offsets, masters, bases opt-in, preview table, status and buttons."""

        TITLE, KEY, ACTION = TITLE, KEY, "Add Shadow"
        HEADERS = ("Glyph · master", "Contours copied")

        def build_controls(self) -> None:
            """Horizontal and vertical offset."""
            self.dx, self.dy = QtGui.QSpinBox(), QtGui.QSpinBox()
            for spin, value in ((self.dx, 40), (self.dy, -40)):
                spin.setRange(-1000, 1000)
                spin.setSuffix(" units")
                spin.setValue(value)
            self.add_row("Offset x", self.dx)
            self.add_row("Offset y", self.dy)

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
                f"{layer_writer.plural(len(todo), 'layer')} will get a shadow"
                if todo
                else "Nothing to shadow"
            )

        def write(self, package: Any, rows: list[Row]) -> dict[str, Any]:
            """Add the shadows with fresh facts. One Undo step."""
            facts = history.scan_auto_facts(package)
            return add_shadows(
                rows, int(self.dx.value), int(self.dy.value), facts, self.consented()
            )

        def result_text(self, result: dict[str, Any]) -> str:
            """Status after Apply."""
            if not result["layers"]:
                return "Nothing to shadow"
            plural = layer_writer.plural
            return f"Added a shadow to {plural(result['layers'], 'layer')} of {plural(result['glyphs'], 'glyph')}"

    return ShadowPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
