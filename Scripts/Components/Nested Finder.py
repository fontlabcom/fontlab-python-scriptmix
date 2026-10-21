# this_file: Scripts/Components/Nested Finder.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Nested Finder
"""Find nested components and unnest them by one level.

What: Lists every component whose base glyph is itself a composite, on the
chosen masters of the selected glyphs or of the whole font. Unnest replaces
each such component with the parts of its base glyph: the inner components
and the base's own contours, placed where they appear now.

How: The base's parts are copied with the outer component transform applied,
so the glyph looks the same. Inner components stay components and keep
following their own base glyphs. Raw node flags, element names and element
notes that a native copy drops are copied back; some per-node and
per-contour properties, such as corner smoothing and contour names, are not
yet copied back. Auto layers are listed and kept.

Why: Nested components are legal, but some build tools and formats flatten
them badly or not at all. One level keeps the shared parts shared; only the
middle step goes.

Use: Select glyphs and run the script. It looks at every master; choose
Whole font to search all glyphs, or the current master to narrow it. A
whole-font run is refused while any glyph in it has an automatic layer or is
the base of one. Press Unnest. Press Reload selection after you change the
font or the selection.

Benefit: Finds every nesting in the selection or the font and fixes it as
one Undo step.

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
components_nested_finder.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap import scripting

QtGui = qt.QtGui
TITLE = "Nested Components"
KEY = "components_nested_finder"


# ---------------------------------------------------------------- nesting logic
def nested_changes(
    package: Any, glyph: Any, layer: Any, master: str
) -> list[component_writer.Change]:
    """One row per component whose base glyph has components on this master."""
    rows: list[component_writer.Change] = []
    for shape in component_writer.components(layer):
        contours, inner = component_writer.part_counts(package, shape, master)
        if not inner:
            continue
        source = package.findName(component_writer.base_of(shape))
        base = component_writer.layer_of(
            source, shape.shapeData.componentLayer or master
        )
        names = (
            " + ".join(
                component_writer.base_of(s) for s in component_writer.components(base)
            )
            if base
            else ""
        )
        why = component_writer.copy_problem(
            package, (glyph.name, master), shape, master
        )
        if why:
            rows.append(
                component_writer.Change(
                    component_writer.base_of(shape), names, "", problem=why
                )
            )
            continue
        rows.append(
            component_writer.Change(
                component_writer.base_of(shape),
                names,
                component_writer.parts_text(contours, inner),
                shape.id,
            )
        )
    return rows


class NestedFinder(component_panel.panel_type()):
    """Glyph scope and master scope; one row per nested component."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Unnest", "Unnested"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Component", "Contains", "Becomes")

    def build_controls(self) -> None:
        self.glyph_scope = QtGui.QComboBox()
        self.glyph_scope.addItem("Selected glyphs")
        self.glyph_scope.addItem("Whole font")
        self.scope = self.scope_box()
        self.scope.setCurrentIndex(1)  # every master, like the sample
        self.form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
        self.form.addWidget(self.glyph_scope, 0, 1)
        self.form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        self.form.addWidget(self.scope, 1, 1)
        self.watch(self.glyph_scope.currentIndexChanged, self.reload)
        self.watch(self.scope.currentIndexChanged)

    def glyph_names(self) -> list[str]:
        if self.glyph_scope.currentIndex == 1:
            return [name for name, _ in scripting.names_font_glyphs()]
        return scripting.names_selected_names()

    def summary(self, plan: component_writer.Plan) -> str:
        if not plan.rows:
            return "No nested components found"
        return super().summary(plan)

    def planner(self) -> component_writer.Planner:
        package = self.package
        return lambda glyph, master, layer: nested_changes(
            package, glyph, layer, master
        )

    def editor(self) -> component_writer.Editor:
        return component_writer.EjectEditor(unlock=False)


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(NestedFinder, KEY)


if __name__ == "__main__":
    main()
