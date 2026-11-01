# this_file: Scripts/Contours/Optimize Start Points.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Optimize Start Points
"""Move the start node of every closed contour to its bottom-left on-curve
node.

What: For each selected glyph and master, the table lists every contour
whose start node moves, and the node that becomes the start. Optimize
applies the moves.

How: The bottom-left node is the lowest on-curve node; on a tie, the
leftmost one. "Match current master" finds it in the current master and uses
the same node number in every other master whose contour has the same node
count, so the masters stay compatible. "Bottom-left in each master" finds it
in each master on its own. FontLab's own flContour.setStartPoint turns the
node list round in place; this is meant to keep the node flags. See Safety
for VFJ reopen.

Why: A predictable start node makes masters easier to compare, helps
interpolation and keeps the order of points in exported fonts stable.

Use: Select glyphs. Run the script. Choose the rule and the masters. Press
Optimize. Press Reload selection after you change the selection.

Benefit: Sets consistent start points over many glyphs and masters in one
Undo step.

Safety: A status note reports only a newly introduced final off-curve with
raw Smooth (fl#8517), which FontLab may change on save. Check node types
after VFJ reopen. Open contours keep their start. These shapes are listed
and kept:

- shared outline data (an edit would change other glyphs too);
- shapes with scale, slant or rotation (bottom-left in stored coordinates is
  not bottom-left on screen).

A new start renumbers the nodes, so the panel opens with All masters chosen.
With "Keep masters compatible" ticked, a glyph is kept when its masters
would get different start nodes, or when other masters need the move too but
are not chosen.

A glyph that has an automatic layer is listed and skipped. So is a glyph
that is a base of an automatic composite, also through other composites,
unless you tick "Also edit bases of automatic composites" (FontLab then
rebuilds those composites; Undo may not restore their anchors). The script
keeps the compatibility check; writes disclose queued ids and possible date
changes.
Every move is planned before the first one is written, so the current master
stays a valid reference. After the write, the script reads the start nodes
back. If FontLab fails part-way, the error says that native changes may
remain. The change is recorded as one Undo step. The one-step write, the
automatic-layer rule, the pending-update check and the panel are shared
(fly.ap.outline_writer, fly.ap.outline_panel); the planner belongs to this
script.

Source: the author's own FontLab sample outlines_optimize_start_points.py,
Apache-2.0. Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.outline_panel as outline_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.outline_writer as outline_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt

QtGui = qt.QtGui
TITLE = "Optimize Start Points"
KEY = "outlines_optimize_start_points"
RULES = (
    "Match current master (keeps masters compatible)",
    "Bottom-left in each master",
)


# ---------------------------------------------------------------- start point logic
def bottom_left(points: list[outline_writer.Point]) -> int | None:
    """Index of the lowest, then leftmost on-curve point; None if there is none."""
    candidates = [(y, x, i) for i, (x, y, on) in enumerate(points) if on]
    return min(candidates)[2] if candidates else None


def own_contours(layer: Any) -> tuple[list[Any], list[str]]:
    """Contours of the editable shapes, in layer order, and notes for kept
    shapes.
    """
    shapes, notes = outline_writer.outline_shapes(layer)
    return [contour for shape in shapes for contour in shape.contours], notes


def start_changes(layer: Any, reference: Any | None) -> list[outline_writer.Change]:
    """One row per closed contour whose start moves; notes for kept shapes.

    With a `reference` layer, contour n uses the bottom-left node number of
    reference contour n when both have the same node count. Edit: (contour,
    new start index, position of that node).
    """
    contours, notes = own_contours(layer)
    sources = own_contours(reference)[0] if reference is not None else []
    rows = []
    for number, contour in enumerate(contours, start=1):
        if not contour.closed:
            continue
        points = outline_writer.node_points(contour)
        source = contour
        if (
            number <= len(sources)
            and sources[number - 1].nodesCount == contour.nodesCount
        ):
            source = sources[number - 1]
        index = bottom_left(outline_writer.node_points(source))
        if not index or not points[index][2]:
            continue
        x, y, _ = points[index]
        rows.append(
            outline_writer.Change(
                f"contour {number}",
                f"node 0 at {outline_writer.fmt(points[0][0])}, {outline_writer.fmt(points[0][1])}",
                f"node {index} at {outline_writer.fmt(x)}, {outline_writer.fmt(y)}",
                (contour, index, (x, y)),
                key=(number, index),
            )
        )
    return rows + outline_writer.note_rows(notes)


def final_smooth_points(contours: list[Any]) -> set[tuple[float, float]]:
    """Coordinates of existing final off-curves with raw Smooth; read only."""
    result = set()
    for contour in contours:
        nodes = contour.nodes()
        if contour.closed and nodes and not nodes[-1].isOn() and nodes[-1].smooth:
            result.add((float(nodes[-1].x), float(nodes[-1].y)))
    return result


class StartEditor(outline_writer.Editor):
    """Rotate the node list with FontLab's own flContour.setStartPoint."""

    def __init__(self) -> None:
        self.before: dict[int, set[tuple[float, float]]] = {}
        self.advice: list[str] = []

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        """Snapshot existing save-risk conditions before any history starts."""
        for edit in edits:
            contour = edit[0]
            self.before[id(contour)] = final_smooth_points([contour])
        return list(edits)

    def write(self, layer: Any, steps: list[Any]) -> None:
        for contour, index, _ in steps:
            if contour.setStartPoint(index) is False:
                raise RuntimeError(
                    f"FontLab refused start node {index} in {layer.name}."
                )

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for contour, _, (x, y) in steps:
                introduced = final_smooth_points([contour]) - self.before[id(contour)]
                if introduced:
                    message = (
                        f"{layer.name}: a final off-curve with raw Smooth was "
                        "introduced; FontLab may change on save (fl#8517). "
                        "Check node types after VFJ reopen."
                    )
                    if message not in self.advice:
                        self.advice.append(message)
                first = outline_writer.node_points(contour)[0]
                if abs(first[0] - x) > 0.01 or abs(first[1] - y) > 0.01:
                    missed.append(
                        f"{layer.name}: start {outline_writer.fmt(first[0])}, {outline_writer.fmt(first[1])}"
                    )
        return missed


class OptimizeStartPoints(outline_panel.panel_type()):
    """Rule and master scope; one row per moved start node."""

    TITLE, KEY, ACTION, DONE, UNIT = TITLE, KEY, "Optimize", "Moved", "start node"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Contour", "Start now", "New start")
    STRUCTURAL = True  # a new start renumbers the nodes

    def build_controls(self) -> None:
        self.rule = QtGui.QComboBox()
        for text in RULES:
            self.rule.addItem(text)
        self.add_row("Rule", self.rule)
        self.watch(self.rule.currentIndexChanged)

    def planner(self) -> outline_writer.Planner:
        match, current = self.rule.currentIndex == 0, self.current_master

        def plan(glyph: Any, master: str, layer: Any) -> list[outline_writer.Change]:
            reference = None
            if match and master != current:
                found = outline_writer.layer_of(glyph, current)
                reference = None if found is None or found.autoLayer else found
            return start_changes(layer, reference)

        return plan

    def editor(self) -> outline_writer.Editor:
        self.risk_editor = StartEditor()
        return self.risk_editor

    def apply(self) -> None:
        """Append save-risk advice to the result without calling it a failed
        store.
        """
        self.risk_editor = None
        super().apply()
        if self.risk_editor is not None and self.risk_editor.advice:
            note = "; ".join(self.risk_editor.advice)
            self.status.setText(f"{self.status.text} · {note}")


def main() -> Any:
    """Open the panel, or replace the one that is already open."""
    return scripting.show_script_dialog(OptimizeStartPoints, KEY)


if __name__ == "__main__":
    main()
