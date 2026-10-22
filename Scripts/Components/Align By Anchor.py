# this_file: Scripts/Components/Align By Anchor.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Align By Anchor
"""Align mark components on their base component by anchors.

What: In each selected composite, the first component is the base. Every
later component (a mark) moves so that its "_name" anchor lands on the base's
"name" anchor. The table shows the anchor pair, the current offset and the new
offset per master.

How: New offset = base offset + base anchor - mark anchor, rounded half up to
whole units. The anchors come from the base and mark glyphs on the same master.
"Automatic" takes the first pair the two glyphs share; or choose one anchor
name. Only the offset changes: the component itself stays in place in the
layer, with its name, note and lock.

Why: Marks drift when anchors move after a composite was built. This puts
them back without a rebuild, and keeps manual composites manual. Components
with scale, slant or rotation are listed and kept: the anchor sum is exact
only for a plain move.

Use: Select composite glyphs. Run the script. Choose the anchor and the
masters. Press Align. Press Reload selection after you change the selection.

Benefit: Re-aligns many marks over many masters in one Undo step.

Safety: Auto layers are listed and never edited (FontLab aligns them itself).
The script refuses the whole batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the offsets back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_align_by_anchor.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from collections.abc import Iterable
from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtGui = qt.QtGui
TITLE = "Align Components by Anchor"
KEY = "components_align_by_anchor"

# ---------------------------------------------------------------- align logic
AUTOMATIC = "Automatic (first matching pair)"


def anchor_points(layer: Any | None) -> dict[str, tuple[float, float]]:
    """{name: (x, y)} of the layer. Duplicate names: the first one wins."""
    found: dict[str, tuple[float, float]] = {}
    for pin in layer.anchors if layer is not None else ():
        found.setdefault(pin.name, (float(pin.point.x()), float(pin.point.y())))
    return found


def base_layer(package: Any, shape: Any, master: str) -> Any | None:
    """The layer that a component shows: its base glyph on this master."""
    glyph = package.findName(component_writer.base_of(shape))
    if glyph is None:
        return None
    return component_writer.layer_of(glyph, shape.shapeData.componentLayer or master)


def pairs(base: dict[str, tuple[float, float]], mark: dict) -> list[str]:
    """Anchor names X with X on the base and _X on the mark, in base order."""
    return [n for n in base if not n.startswith("_") and "_" + n in mark]


def align_changes(
    package: Any, layer: Any, master: str, wanted: str | None
) -> list[component_writer.Change]:
    """One row per mark component: anchor pair, current and new offset.

    `wanted` None takes the first shared pair. A row without `edit` is shown
    only: no pair, a scaled component, or a mark that already sits right.
    """
    shapes = component_writer.components(layer)
    if len(shapes) < 2:
        return []
    first = shapes[0]
    base = anchor_points(base_layer(package, first, master))
    bx, by = component_writer.offset(first)
    rows: list[component_writer.Change] = []
    for shape in shapes[1:]:
        name, old = component_writer.base_of(shape), component_writer.offset(shape)
        mark = anchor_points(base_layer(package, shape, master))
        found = pairs(base, mark)
        family = (found[0] if found else None) if wanted is None else wanted
        if family not in found:
            rows.append(
                component_writer.Change(
                    name, component_writer.offset_text(old), "no matching anchors"
                )
            )
            continue
        if not component_writer.plain_move(shape) or not component_writer.plain_move(
            first
        ):
            rows.append(
                component_writer.Change(
                    name, component_writer.offset_text(old), "scaled or slanted, kept"
                )
            )
            continue
        (ax, ay), (mx, my) = base[family], mark["_" + family]
        new = (
            float(component_writer.half_up(bx + ax - mx)),
            float(component_writer.half_up(by + ay - my)),
        )
        label = f"{name} @ {family}"
        if all(
            abs(new[axis] - old[axis]) < component_writer.EPSILON for axis in (0, 1)
        ):
            rows.append(
                component_writer.Change(
                    label, component_writer.offset_text(old), "in place"
                )
            )
        else:
            rows.append(
                component_writer.Change(
                    label,
                    component_writer.offset_text(old),
                    component_writer.offset_text(new),
                    (shape.id, new),
                )
            )
    return rows


def families(package: Any, glyphs: Iterable[Any], master: str) -> list[str]:
    """Anchor pairs any selected composite could use on `master`, in order."""
    found: list[str] = []
    for glyph in glyphs:
        layer = component_writer.layer_of(glyph, master)
        shapes = component_writer.components(layer) if layer is not None else []
        if len(shapes) < 2:
            continue
        base = anchor_points(base_layer(package, shapes[0], master))
        for shape in shapes[1:]:
            mark = anchor_points(base_layer(package, shape, master))
            found.extend(n for n in pairs(base, mark) if n not in found)
    return found


class AlignByAnchor(component_panel.panel_type()):
    """Anchor choice plus master scope; one row per mark component."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Align", "Moved"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Mark @ anchor", "Offset", "New")

    def build_controls(self) -> None:
        self.family = QtGui.QComboBox()
        self.family.addItem(AUTOMATIC)
        self.scope = self.scope_box()
        self.form.addWidget(QtGui.QLabel("Anchor"), 0, 0)
        self.form.addWidget(self.family, 0, 1)
        self.form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        self.form.addWidget(self.scope, 1, 1)
        self.watch(self.family.currentIndexChanged)
        self.watch(self.scope.currentIndexChanged)

    def on_reload(self) -> None:
        """Offer the anchor pairs of the selection. Keep the choice if it still exists."""
        keep = self.wanted()
        names = families(self.package, self.glyphs, self.current_master)
        self.family.blockSignals(True)
        self.family.clear()
        self.family.addItem(AUTOMATIC)
        self.family.addItems(names)
        if keep in names:
            self.family.setCurrentIndex(names.index(keep) + 1)
        self.family.blockSignals(False)

    def wanted(self) -> str | None:
        """Chosen anchor name, or None for Automatic."""
        if self.family.currentIndex <= 0:
            return None
        return str(self.family.currentText)

    def summary(self, plan: component_writer.Plan) -> str:
        if not plan.work and plan.rows:
            return "All marks already sit on their anchors"
        return super().summary(plan)

    def planner(self) -> component_writer.Planner:
        package, wanted = self.package, self.wanted()
        return lambda glyph, master, layer: align_changes(
            package, layer, master, wanted
        )

    def editor(self) -> component_writer.Editor:
        return component_writer.MoveEditor()


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(AlignByAnchor, KEY)


if __name__ == "__main__":
    main()
