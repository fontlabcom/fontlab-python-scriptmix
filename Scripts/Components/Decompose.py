# this_file: Scripts/Components/Decompose.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Decompose
"""Decompose the components of the selected glyphs into plain outlines.

What: Lists every component of the selected glyphs on the chosen masters and
what it becomes: the contours of its base glyph. Decompose replaces each
component with editable copies of those contours, at the same place.

How: One Decompose replaces each component with the parts of its base glyph,
placed by the component transform. A part that is itself a component stays a
component; the table says so, and the next Decompose takes it apart too. The
new contours are unlocked, as after FontLab's own Decompose. Raw node flags,
element names and element notes that a native copy drops are copied back;
some per-node and per-contour properties, such as corner smoothing and contour
names, are not yet copied back. Auto layers are listed and kept.

Why: Decomposed outlines no longer follow later edits of the base glyph. Use
it before an outline change that must be local, or for a build tool that
cannot handle components. One level per press keeps every step visible.

Use: Select composite glyphs. Run the script. Choose the masters. Press
Decompose. Press Reload selection after you change the selection.

Benefit: Decomposes many glyphs and masters as one Undo step, with a preview.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates);
- a base glyph has no plain layer for the master, holds a perspective
  transform or a composite shape that is not a component, or the components
  loop or nest more than 64 levels (the row says which).

After the write, the script reads the layers back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
The write is recorded as one Undo step: it hands FontLab each removed
component, with its data and builder. Edit > Undo of removed components
depends on FontLab (fl#7641). The copy, the base checks, the history write, the panel, the
automatic-layer rule and the pending-update check are shared with other
scripts (fly.ap.component_writer, fly.ap.component_panel, fly.ap.history,
fly.ap.edit_guards); the planner and the panel controls belong to this
script.

Source: the author's own FontLab sample
components_decompose.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap import scripting

QtGui = qt.QtGui
TITLE = "Decompose Components"
KEY = "components_decompose"


# ---------------------------------------------------------------- decompose logic
def decompose_changes(
    package: Any, glyph: Any, layer: Any, master: str
) -> list[component_writer.Change]:
    """One row per component of the layer: its base and what it becomes."""
    rows: list[component_writer.Change] = []
    for shape in component_writer.components(layer):
        why = component_writer.copy_problem(
            package, (glyph.name, master), shape, master
        )
        if why:
            rows.append(
                component_writer.Change(
                    component_writer.base_of(shape), "", "", problem=why
                )
            )
            continue
        contours, inner = component_writer.part_counts(package, shape, master)
        becomes = component_writer.parts_text(contours, inner)
        if inner:
            becomes += " (nested: press again)"
        rows.append(
            component_writer.Change(
                component_writer.base_of(shape), "", becomes, shape.id
            )
        )
    return rows


class Decompose(component_panel.panel_type()):
    """Master scope; one row per component."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Decompose", "Decomposed"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Component", "Becomes")
    WIDTH = 540

    def build_controls(self) -> None:
        self.scope = self.scope_box()
        self.form.addWidget(QtGui.QLabel("Masters"), 0, 0)
        self.form.addWidget(self.scope, 0, 1)
        self.watch(self.scope.currentIndexChanged)

    def planner(self) -> component_writer.Planner:
        package = self.package
        return lambda glyph, master, layer: decompose_changes(
            package, glyph, layer, master
        )

    def editor(self) -> component_writer.Editor:
        return component_writer.EjectEditor(unlock=True)


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(Decompose, KEY)


if __name__ == "__main__":
    main()
