# this_file: Scripts/Components/Unlock Lock.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Unlock Lock
"""Show which components of the selected glyphs are locked; lock or unlock them.

What: Lists every component of the selected glyphs on the chosen masters,
with its lock state now and after the action. Lock or Unlock sets the state
of every component that differs.

How: A locked component cannot be selected or moved by accident in the Glyph
window. FontLab's Python property reports every component as locked, because
component data is always locked. So the script reads each element's own lock
flag from FontLab's glyph data (the same data that a .vfj file stores). It
trusts that data only when its elements match the layer's shapes one to one,
with the same component names. Otherwise the state shows as "unknown" and
the component is not changed. The lock is set on the existing component in
place.

Why: Locking protects finished composites while you edit their outlines.
Unlocking many components at once is tedious in the Glyph window.

Use: Select composite glyphs. Run the script. Choose Lock or Unlock and the
masters. Press Apply. Press Reload selection after you change the selection.

Benefit: Sets component locks in many glyphs and masters in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);

After the write, the script reads the lock flags again and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_unlock_lock.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtGui = qt.QtGui
TITLE = "Lock and Unlock Components"
KEY = "components_unlock_lock"

# ---------------------------------------------------------------- lock logic
Entries = list[tuple[str, bool]]  # per element: (component base name or '', locked)


def data_tool(tool: str, **arguments: Any) -> Any:
    """Call one of FontLab's own data tools in-process (fly.pr is native fontpr).

    An error answer becomes RuntimeError with FontLab's text.
    """
    from fly import pr

    result = pr.call(tool, **arguments)
    if isinstance(result, dict) and (
        result.get("error") or result.get("status") == "error"
    ):
        raise RuntimeError(str(result.get("error") or result.get("message")))
    return result


def element_name(element: Any) -> str:
    """Base glyph name of a component element, '' for any other element."""
    component = element.get("component") if isinstance(element, dict) else None
    return str(component.get("glyphName", "")) if isinstance(component, dict) else ""


def explicit_locks(package: Any, name: str) -> dict[str, Entries]:
    """{layer name: element entries} from FontLab's stored glyph data."""
    data = data_tool("get_glyph", font_id=scripting.font_id(package), glyph_name=name)
    data = data.get("glyph", data) if isinstance(data, dict) else {}
    found: dict[str, Entries] = {}
    for layer in data.get("layers", None) or []:
        elements = layer.get("elements", None) or []
        found[str(layer.get("name"))] = [
            (element_name(e), bool(e.get("locked", False))) for e in elements
        ]
    return found


def lock_states(layer: Any, entries: Entries | None) -> list[bool | None]:
    """Own lock flag per layer shape; all None when data and shapes differ.

    The data counts only when it has one element per shape, components at the
    same positions, with the same base names.
    """
    shapes = list(layer.shapes)
    unknown: list[bool | None] = [None] * len(shapes)
    if entries is None or len(entries) != len(shapes):
        return unknown
    for shape, (name, _) in zip(shapes, entries, strict=True):
        if bool(shape.isComponent) != bool(name):
            return unknown
        if shape.isComponent and name != component_writer.base_of(shape):
            return unknown
    return [locked for _, locked in entries]


def word(state: bool | None) -> str:
    """'locked', 'unlocked' or 'unknown'."""
    return "unknown" if state is None else ("locked" if state else "unlocked")


def lock_changes(
    glyph: Any, layer: Any, entries: Entries | None, locked: bool
) -> list[component_writer.Change]:
    """One row per component: state now and after the action."""
    rows: list[component_writer.Change] = []
    states = lock_states(layer, entries)
    for shape, state in zip(layer.shapes, states, strict=True):
        if not shape.isComponent:
            continue
        name, now = component_writer.base_of(shape), word(state)
        if state is None:
            rows.append(component_writer.Change(name, now, "unknown, kept"))
        elif state == locked:
            rows.append(component_writer.Change(name, now, "already " + now))
        else:
            edit = (shape.id, locked, glyph.name)
            rows.append(component_writer.Change(name, now, word(locked), edit))
    return rows


class LockEditor(component_writer.Editor):
    """Set the own lock flag of each planned component in place."""

    def __init__(self, package: Any) -> None:
        self.package = package

    def prepare(self, layer: Any, edits: list[Any]) -> list[Any]:
        return [
            (layer.shapes[component_writer.shape_index(layer, shape_id)], locked, name)
            for shape_id, locked, name in edits
        ]

    def write(self, layer: Any, steps: list[Any]) -> None:
        for shape, locked, _ in steps:
            shape.contentLocked = locked
            shape.changed()

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed: list[str] = []
        stored: dict[str, dict[str, Entries]] = {}
        for layer, steps in prepared:
            for shape, locked, name in steps:
                if name not in stored:
                    stored[name] = explicit_locks(self.package, name)
                states = lock_states(layer, stored[name].get(str(layer.name)))
                if states[component_writer.shape_index(layer, shape.id)] is not locked:
                    missed.append(
                        f"{name}/{layer.name}/{component_writer.base_of(shape)}"
                    )
        return missed


class LockUnlock(component_panel.panel_type()):
    """Action (Lock or Unlock) plus master scope; one row per component."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Apply", "Changed"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Component", "Now", "After")

    def build_controls(self) -> None:
        self.flags: dict[str, dict[str, Entries]] = {}
        self.action = QtGui.QComboBox()
        self.action.addItem("Lock")
        self.action.addItem("Unlock")
        self.scope = self.scope_box()
        self.form.addWidget(QtGui.QLabel("Action"), 0, 0)
        self.form.addWidget(self.action, 0, 1)
        self.form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        self.form.addWidget(self.scope, 1, 1)
        self.watch(self.action.currentIndexChanged)
        self.watch(self.scope.currentIndexChanged)

    def locking(self) -> bool:
        return self.action.currentIndex == 0

    def read_flags(self) -> None:
        """Read the stored lock flags of the scanned glyphs from FontLab."""
        package = scripting.current_package(self.package_id)
        if package is None:
            self.flags = {}
            if self.package is not None:
                raise ValueError("The font changed; press Reload selection.")
            return
        self.flags = {g.name: explicit_locks(package, g.name) for g in self.glyphs}

    def on_reload(self) -> None:
        self.read_flags()

    def summary(self, plan: component_writer.Plan) -> str:
        if plan.rows and not plan.work:
            return "Nothing to change"
        return super().summary(plan)

    def planner(self) -> component_writer.Planner:
        flags, locked = self.flags, self.locking()
        return lambda glyph, master, layer: lock_changes(
            glyph, layer, flags.get(glyph.name, {}).get(str(layer.name)), locked
        )

    def editor(self) -> component_writer.Editor:
        return LockEditor(self.package)

    def apply(self) -> None:
        """Read the stored flags again, then plan and write."""
        self.read_flags()
        super().apply()

    def after_apply(self) -> None:
        """Show the stored state after the write; a read error leaves 'unknown'."""
        try:
            self.read_flags()
        except (ValueError, RuntimeError, TimeoutError):
            self.flags = {}
        self.refresh()


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(LockUnlock, KEY)


if __name__ == "__main__":
    main()
