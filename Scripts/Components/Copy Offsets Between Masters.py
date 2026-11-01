# this_file: Scripts/Components/Copy Offsets Between Masters.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Copy Offsets Between Masters
"""Copy component offsets from one master to other masters of the selected glyphs.

What: Takes the component offsets of the source master and sets them on the
same components in the ticked target masters. The table shows the current
and the new offset of every component that changes.

How: Components are matched by position and base glyph name. A target layer
with other components, or in another order, is listed and kept. With "Scale x
by advance-width ratio", the horizontal offset is multiplied by target width
/ source width and rounded half up, so a mark at 40 % of the width stays at
40 %. The vertical offset is copied as it is. Only the offset changes: scale,
slant and the component itself stay.

Why: Composites often need the same mark placement in every master. Copying
the offsets once is faster and more exact than moving marks by hand.

Use: Select composite glyphs. Run the script. Choose the source master, tick
the targets. Press Copy. Press Reload selection after you change the
selection.

Benefit: Brings the masters of many composites into line in one Undo step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);

After the write, the script reads the offsets back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Use Edit > Undo then. The
one-step write, the panel, the automatic-layer rule and the pending-update
check are shared with other scripts (fly.ap.component_writer,
fly.ap.component_panel, fly.ap.history, fly.ap.edit_guards); the planner
and the panel controls belong to this script.

Source: the author's own FontLab sample
components_copy_offsets_between_masters.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.component_panel as component_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.component_writer as component_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
import fly.ap.scripting as scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
TITLE = "Copy Component Offsets"
KEY = "components_copy_offsets_between_masters"


# ---------------------------------------------------------------- copy logic
def offset_changes(
    source: Any, target: Any, scale: bool
) -> list[component_writer.Change]:
    """One row per component of the target: current and new offset.

    Different component lists give one note row and no edit.
    """
    src, dst = component_writer.components(source), component_writer.components(target)
    if not src:
        return []
    if [component_writer.base_of(s) for s in src] != [
        component_writer.base_of(s) for s in dst
    ]:
        names = " + ".join(component_writer.base_of(s) for s in dst) or "none"
        return [component_writer.Change(names, "", "different components, kept")]
    ratio = 1.0
    if scale and source.advanceWidth:
        ratio = float(target.advanceWidth) / float(source.advanceWidth)
    rows: list[component_writer.Change] = []
    for old_shape, shape in zip(src, dst, strict=True):
        dx, dy = component_writer.offset(old_shape)
        new = (float(component_writer.half_up(dx * ratio)) if scale else dx, dy)
        old = component_writer.offset(shape)
        if all(
            abs(new[axis] - old[axis]) < component_writer.EPSILON for axis in (0, 1)
        ):
            rows.append(
                component_writer.Change(
                    component_writer.base_of(shape),
                    component_writer.offset_text(old),
                    "same",
                )
            )
        else:
            rows.append(
                component_writer.Change(
                    component_writer.base_of(shape),
                    component_writer.offset_text(old),
                    component_writer.offset_text(new),
                    (shape.id, new),
                )
            )
    return rows


class CopyOffsets(component_panel.panel_type()):
    """Source master, target checklist, scale option; one row per component."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Copy", "Moved"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Component", "Offset", "New")

    def build_controls(self) -> None:
        self.ticked: set[str] = set()
        self.source_box = QtGui.QComboBox()
        self.scale_box = QtGui.QCheckBox("Scale x by advance-width ratio")
        self.target_list = QtGui.QListWidget()
        self.target_list.setAlternatingRowColors(True)
        self.target_list.setMinimumHeight(90)
        self.form.addWidget(QtGui.QLabel("From"), 0, 0)
        self.form.addWidget(self.source_box, 0, 1)
        self.form.addWidget(QtGui.QLabel("To"), 1, 0)
        self.form.addWidget(self.target_list, 1, 1)
        self.form.addWidget(self.scale_box, 2, 1)
        self.watch(self.source_box.currentIndexChanged, self.retarget)
        self.watch(self.scale_box.toggled)
        scripting.connect_guarded(self, self.target_list.itemChanged, self.toggled)

    def on_reload(self) -> None:
        """Refill the source combo; keep the chosen source when it still exists."""
        keep = self.source()
        self.source_box.blockSignals(True)
        self.source_box.clear()
        self.source_box.addItems(self.masters)
        start = keep if keep in self.masters else self.current_master
        if start in self.masters:
            self.source_box.setCurrentIndex(self.masters.index(start))
        self.source_box.blockSignals(False)
        if not self.ticked:
            self.ticked = set(self.masters)
        self.fill_targets()

    def source(self) -> str:
        """Chosen source master name, or '' without a font."""
        if self.source_box.currentIndex < 0:
            return ""
        return str(self.source_box.currentText)

    def fill_targets(self) -> None:
        """Every master except the source, ticked as before."""
        self.target_list.blockSignals(True)
        self.target_list.clear()
        for master in self.masters:
            if master == self.source():
                continue
            item = QtGui.QListWidgetItem(master)
            item.setForeground(component_panel.ink())
            item.setData(QtCore.Qt.UserRole, master)
            item.setFlags(int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable))
            item.setCheckState(
                QtCore.Qt.Checked if master in self.ticked else QtCore.Qt.Unchecked
            )
            self.target_list.addItem(item)
        self.target_list.blockSignals(False)

    def retarget(self) -> None:
        self.fill_targets()
        self.refresh()

    def toggled(self, item: Any) -> None:
        master = item.data(QtCore.Qt.UserRole)
        if item.checkState() == QtCore.Qt.Checked:
            self.ticked.add(master)
        else:
            self.ticked.discard(master)
        self.refresh()

    def chosen_masters(self) -> list[str]:
        source = self.source()
        return [m for m in self.masters if m != source and m in self.ticked]

    def planner(self) -> component_writer.Planner:
        source, scale = self.source(), bool(self.scale_box.isChecked())
        if not self.chosen_masters():
            raise ValueError("Tick at least one target master.")

        def plan(glyph: Any, master: str, layer: Any) -> list[component_writer.Change]:
            origin = component_writer.layer_of(glyph, source)
            return offset_changes(origin, layer, scale) if origin is not None else []

        return plan

    def editor(self) -> component_writer.Editor:
        return component_writer.MoveEditor()


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(CopyOffsets, KEY)


if __name__ == "__main__":
    main()
