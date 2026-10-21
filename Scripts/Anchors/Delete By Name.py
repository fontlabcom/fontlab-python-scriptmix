# this_file: Scripts/Anchors/Delete By Name.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Delete By Name
"""Delete anchors by name from the selected glyphs.

What: Shows every anchor name found on the selected glyphs, with the number of
layers that carry it. Tick the names to delete. Choose the masters.

How: Delete removes every anchor with a ticked name from every editable layer
in scope. Layers with an auto role are counted, shown and kept.

Why: The checklist is the preview: you see which names exist before you delete.
Nothing else changes: contours, components and other anchors stay.

Use: Select glyphs. Run the script. Tick names. Press Delete. Press Reload
selection after you change the selection.

Benefit: Removes stray or obsolete anchors in many glyphs and masters in one step.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads the result back and reports any gap.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_delete_by_name.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from collections.abc import Iterable
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap import scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
TITLE = "Delete Anchors by Name"
KEY = "anchors_delete_by_name"


# ---------------------------------------------------------------- delete logic
def census(glyphs: Iterable[Any], masters: Iterable[str]) -> dict[str, list[int]]:
    """{anchor name: [editable layers, auto layers]} over the glyphs and masters."""
    counts: dict[str, list[int]] = {}
    masters = list(masters)
    for glyph in glyphs:
        for master in masters:
            layer = anchor_writer.layer_of(glyph, master)
            for name in (
                {pin.name for pin in layer.anchors} if layer is not None else ()
            ):
                entry = counts.setdefault(name, [0, 0])
                entry[1 if layer.autoLayer else 0] += 1
    return dict(sorted(counts.items()))


def delete_changes(layer: Any, names: set[str]) -> list[anchor_writer.Change]:
    """One row per distinct ticked name on the layer. Duplicates go together."""
    present = sorted({pin.name for pin in layer.anchors} & names)
    return [
        anchor_writer.Change(name, "present", "delete", ("remove", name, None))
        for name in present
    ]


class DeleteByName(anchor_panel.panel_type()):
    """Master scope plus a checklist of the anchor names found."""

    TITLE, KEY, ACTION = TITLE, KEY, "Delete"
    HEADERS: tuple[str, ...] = ("Glyph · master", "Anchor", "Action")

    def build_controls(self) -> None:
        self.checked: set[str] = set()
        self.counts: dict[str, list[int]] = {}
        self.scope = self.scope_box()
        self.list = QtGui.QListWidget()
        self.list.setAlternatingRowColors(True)
        self.list.setMinimumHeight(180)
        self.form.addWidget(QtGui.QLabel("Masters"), 0, 0)
        self.form.addWidget(self.scope, 0, 1)
        self.form.addWidget(self.list, 1, 0, 1, 2)
        self.watch(self.scope.currentIndexChanged, self.rebuild)
        scripting.connect_guarded(self, self.list.itemChanged, self.toggled)

    def chosen_masters(self) -> list[str]:
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    def on_reload(self) -> None:
        self.rebuild()

    def rebuild(self) -> None:
        """Refill the checklist: names with layer counts. Keep the ticks."""
        self.counts = census(self.glyphs, self.chosen_masters())
        self.checked &= set(self.counts)
        self.list.blockSignals(True)
        self.list.clear()
        for name, (editable, auto) in self.counts.items():
            note = f"{editable} layer{'s' if editable != 1 else ''}" + (
                f", {auto} auto (kept)" if auto else ""
            )
            item = QtGui.QListWidgetItem(f"{name}    -  {note}")
            item.setForeground(anchor_panel.ink())
            item.setData(QtCore.Qt.UserRole, name)
            item.setFlags(int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable))
            item.setCheckState(
                QtCore.Qt.Checked if name in self.checked else QtCore.Qt.Unchecked
            )
            self.list.addItem(item)
        self.list.blockSignals(False)
        self.refresh()

    def apply(self) -> None:
        """Write, then rebuild the checklist: the deleted names disappear."""
        super().apply()
        message = self.status.text
        self.rebuild()
        self.status.setText(message)

    def toggled(self, item: Any) -> None:
        name = item.data(QtCore.Qt.UserRole)
        if item.checkState() == QtCore.Qt.Checked:
            self.checked.add(name)
        else:
            self.checked.discard(name)
        self.refresh()

    def planner(self) -> anchor_writer.Planner:
        if not self.checked:
            raise ValueError(
                f"{len(self.counts)} anchor names found. Tick the names to delete."
            )
        names = set(self.checked)
        return lambda glyph, master, layer: delete_changes(layer, names)


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(DeleteByName, KEY)


if __name__ == "__main__":
    main()
