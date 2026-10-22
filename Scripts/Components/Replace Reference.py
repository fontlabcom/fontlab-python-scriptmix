# this_file: Scripts/Components/Replace Reference.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Replace Reference
"""Replace the base glyph of matching components, and keep their placement.

What: Every component that refers to glyph X now refers to glyph Y. Offset,
scale, slant, name, note and lock of each component stay. Works on the
selected glyphs or on the whole font, on one or all masters. The table lists
every component that changes.

How: The script sets the base glyph name of the existing component in place,
then lets FontLab rebuild the component. It does not delete and re-create
the component, so nothing that a re-created element would lose is lost.

Why: Swapping a mark or a figure variant in many composites by hand is slow
and easy to get wrong. This keeps every placement exactly where it was.

Use: Run the script. Type the glyph to replace and the new glyph (both fields
complete names). Choose the glyphs and masters. Press Replace. Press Reload
selection after you change the selection.

Benefit: Changes a component in the whole font in one Undo step.

Safety: Auto layers are listed and never edited (change their recipe). A
component is blocked, with the reason in red, when:

- the new glyph has no layer for that master;
- the new glyph uses the edited glyph, directly or through other components
  (the result would refer to itself);
- the component shares its element data with other elements (the change
  would reach them too).

The script refuses the whole batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);

After the write, the script reads the components back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_replace_reference.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.history as history  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
TITLE = "Replace Component Reference"
KEY = "components_replace_reference"

# ---------------------------------------------------------------- replace logic
DEBOUNCE_MS = 250  # replan this long after the last key press


def users_of(facts: history.AutoFacts, name: str) -> set[str]:
    """Every glyph that shows `name`, directly or through other components.

    When the new base is among the users of the edited glyph, the edited glyph
    would contain itself.
    """
    seen, todo = {name}, [name]
    while todo:
        for user in facts.users.get(todo.pop(), ()):
            if user not in seen:
                seen.add(user)
                todo.append(user)
    return seen - {name}


def matrix_of(shape: Any) -> tuple[float, ...]:
    """The six transform numbers, to prove that the placement did not move."""
    m = shape.transform
    return (m.m11(), m.m12(), m.m21(), m.m22(), m.dx(), m.dy())


def replace_changes(
    package: Any,
    glyph: Any,
    layer: Any,
    master: str,
    names: tuple[str, str],
    facts: history.AutoFacts,
) -> list[component_writer.Change]:
    """One row per component of `old` on the layer, with its block reason if any."""
    old, new = names
    rows: list[component_writer.Change] = []
    for shape in component_writer.components(layer):
        if component_writer.base_of(shape) != old:
            continue
        where = component_writer.offset_text(component_writer.offset(shape))
        problem = replace_problem(package, glyph, shape, master, new, facts)
        if problem:
            rows.append(component_writer.Change(old, where, "", problem=problem))
        else:
            rows.append(component_writer.Change(old, where, new, (shape.id, new)))
    return rows


def replace_problem(
    package: Any,
    glyph: Any,
    shape: Any,
    master: str,
    new: str,
    facts: history.AutoFacts,
) -> str:
    """Why `shape` cannot show `new`, or "".

    The new base needs the layer the component reads: its own layer name, if
    it names one, else the master.
    """
    wanted = shape.shapeData.componentLayer or master
    target = package.findName(new)
    if target is None or component_writer.layer_of(target, wanted) is None:
        return f"{new} has no layer {wanted}"
    if new == glyph.name or new in users_of(facts, glyph.name):
        return f"{new} uses {glyph.name}: the component would show itself"
    if int(shape.shapeData.referenceCount) > 1:
        return "shared element data: change it in FontLab"
    return ""


class ReplaceEditor(component_writer.Editor):
    """Set the base glyph name of each planned component in place."""

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        steps = []
        for shape_id, new in edits:
            shape = layer.shapes[component_writer.shape_index(layer, shape_id)]
            steps.append((shape, new, matrix_of(shape)))
        return steps

    def write(self, layer: Any, steps: list[Any]) -> None:
        for shape, new, _ in steps:
            shape.shapeData.componentGlyph = new
            component_writer.refreshed(shape)

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        for layer, steps in prepared:
            for shape, new, matrix in steps:
                now = matrix_of(shape)
                moved = any(
                    abs(a - b) >= component_writer.EPSILON
                    for a, b in zip(now, matrix, strict=True)
                )
                if component_writer.base_of(shape) != new or moved:
                    missed.append(f"{layer.name}/{new}")
        return missed


class ReplaceReference(component_panel.panel_type()):
    """Old and new glyph names, glyph scope and master scope."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Replace", "Replaced"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Component", "Offset", "Becomes")
    WIDTH = 560

    def build_controls(self) -> None:
        self.old_edit = QtGui.QLineEdit()
        self.old_edit.setPlaceholderText("component to replace, e.g. period")
        self.new_edit = QtGui.QLineEdit()
        self.new_edit.setPlaceholderText("new component glyph, e.g. period.alt")
        self.glyph_scope = QtGui.QComboBox()
        self.glyph_scope.addItem("Selected glyphs")
        self.glyph_scope.addItem("Whole font")
        self.scope = self.scope_box()
        self.form.addWidget(QtGui.QLabel("Replace"), 0, 0)
        self.form.addWidget(self.old_edit, 0, 1)
        self.form.addWidget(QtGui.QLabel("With"), 1, 0)
        self.form.addWidget(self.new_edit, 1, 1)
        self.form.addWidget(QtGui.QLabel("Glyphs"), 2, 0)
        self.form.addWidget(self.glyph_scope, 2, 1)
        self.form.addWidget(QtGui.QLabel("Masters"), 3, 0)
        self.form.addWidget(self.scope, 3, 1)
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(DEBOUNCE_MS)
        self.timers.append(self.timer)
        self.watch(self.timer.timeout)
        for edit in (self.old_edit, self.new_edit):
            self.watch(edit.textChanged, self.typed)
        self.watch(self.glyph_scope.currentIndexChanged, self.reload)
        self.watch(self.scope.currentIndexChanged)

    def on_reload(self) -> None:
        """Offer every glyph name of the font for completion."""
        names = [name for name, _ in scripting.names_font_glyphs()]
        for edit in (self.old_edit, self.new_edit):
            completer = QtGui.QCompleter(names, self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            completer.setFilterMode(QtCore.Qt.MatchContains)
            edit.setCompleter(completer)

    def typed(self) -> None:
        """Wait for a pause in typing before the preview scans again."""
        self.apply_button.setEnabled(False)
        self.timer.start()

    def glyph_names(self) -> list[str]:
        if self.glyph_scope.currentIndex == 1:
            return [name for name, _ in scripting.names_font_glyphs()]
        return scripting.names_selected_names()

    def names(self) -> tuple[str, str]:
        """(old, new), checked. ValueError tells what to type."""
        old, new = str(self.old_edit.text).strip(), str(self.new_edit.text).strip()
        if not old or not new:
            raise ValueError("Type both glyph names.")
        if old == new:
            raise ValueError("The two names are the same.")
        if self.package is None or self.package.findName(new) is None:
            raise ValueError(f"No glyph named {new}.")
        return old, new

    def summary(self, plan: component_writer.Plan) -> str:
        if not plan.rows:
            try:
                self.names()
            except ValueError as error:
                return str(error)
            return "No component of that glyph in scope"
        return super().summary(plan)

    def planner(self) -> component_writer.Planner:
        package, names, facts = self.package, self.names(), self.facts
        return lambda glyph, master, layer: replace_changes(
            package, glyph, layer, master, names, facts
        )

    def editor(self) -> component_writer.Editor:
        return ReplaceEditor()


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(ReplaceReference, KEY)


if __name__ == "__main__":
    main()
