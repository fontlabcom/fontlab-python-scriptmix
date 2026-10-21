# this_file: Scripts/Anchors/Mirror Across Masters.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Mirror Across Masters
"""Copy the anchors of one master into the other masters of the same glyphs.

What: Takes the anchors of a source master. Moves the same-named anchors in the
ticked target masters, and adds the missing ones. Optional: add only the
missing anchors.

How: The x value can scale with the advance-width ratio, target over source.
An anchor in the middle of a narrow Light glyph then lands in the middle
of the wide Bold glyph. Positions round half up to whole units. A new
anchor gets its name-derived appearance.

Why: One master carries the reference design. The others follow in one step.
This is a start: interpolation or hand work refines the result.

Use: Select glyphs. Run the script. Choose the source master. Tick the target
masters. Check the table. Press Mirror.

Benefit: Fast, consistent anchor sets in all masters of many glyphs.

Safety: Auto layers are listed and never edited. The script refuses the whole
batch, before any history exists, when:

- an existing anchor would move to 0, 0 (FontLab cannot Redo that);
- a glyph has an automatic layer, or is the base of an automatic composite,
  also through other composites (FontLab rebuilds the composite and Undo does
  not restore it);
- several anchors on a layer share a name (the edit is ambiguous);
- FontLab holds queued glyph updates (they would alter other glyph dates).

After the write, the script reads every value back. It reports any value
that FontLab did not keep, for example under a strong rounding preference.
If FontLab fails part-way, the error says that native changes may remain.
Edit > Undo restores the font. The plan, the safety checks, the one-step
write and the panel base are shared with the other anchor scripts
(fly.ap.anchor_writer, fly.ap.anchor_panel); the planner and the controls
belong to this script.

Source: the author's own FontLab sample
anchors_mirror_across_masters.py, Apache-2.0.
Adapted for the current FontLab 9 API.
"""

from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - fontlabapp.__getattr__ is native
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - fontlabapp.__getattr__ is native
from fly import qt
from fly.ap import scripting

QtCore, QtGui = qt.QtCore, qt.QtGui
TITLE = "Mirror Anchors Across Masters"
KEY = "anchors_mirror_across_masters"


# ---------------------------------------------------------------- mirror logic
def mirror_changes(
    source: Any, target: Any, scale: bool, only_missing: bool
) -> list[anchor_writer.Change]:
    """Rows to bring `target` in line with `source`. Positions round half up."""
    ratio = (
        target.advanceWidth / source.advanceWidth
        if scale and source.advanceWidth
        else 1.0
    )
    wanted = anchor_writer.duplicated(source, [pin.name for pin in source.anchors])
    if wanted:
        return anchor_writer.refusal(wanted)
    current = anchor_writer.anchor_points(target)
    changes: list[anchor_writer.Change] = []
    for name, (x, y) in anchor_writer.anchor_points(source).items():
        if only_missing and name in current:
            continue
        new = (anchor_writer.half_up(x * ratio), anchor_writer.half_up(y))
        old = current.get(name)
        if old is not None and tuple(old) == new:
            continue
        before = (
            "–"
            if old is None
            else f"{anchor_writer.fmt(old[0])}, {anchor_writer.fmt(old[1])}"
        )
        changes.append(
            anchor_writer.Change(
                name, before, f"{new[0]}, {new[1]}", ("set", name, new)
            )
        )
    clash = anchor_writer.duplicated(target, [c.name for c in changes])
    return anchor_writer.refusal(clash) if clash else changes


class MirrorAcrossMasters(anchor_panel.panel_type()):
    """Source master, scaling, only-missing, target checklist."""

    TITLE, KEY, ACTION = TITLE, KEY, "Mirror"

    def build_controls(self) -> None:
        self.source = QtGui.QComboBox()
        self.scale = QtGui.QCheckBox("Scale x by advance-width ratio")
        self.scale.setChecked(True)
        self.only_missing = QtGui.QCheckBox("Only add missing anchors")
        self.targets = QtGui.QListWidget()
        self.fill_masters()
        self.form.addWidget(QtGui.QLabel("From master"), 0, 0)
        self.form.addWidget(self.source, 0, 1)
        self.form.addWidget(self.scale, 1, 1)
        self.form.addWidget(self.only_missing, 2, 1)
        self.form.addWidget(QtGui.QLabel("To masters"), 3, 0)
        self.form.addWidget(self.targets, 3, 1)
        for signal in (
            self.source.currentIndexChanged,
            self.scale.toggled,
            self.only_missing.toggled,
            self.targets.itemChanged,
        ):
            self.watch(signal)

    def fill_masters(self) -> None:
        """Fill the source combo and the target checklist from the font masters."""
        self.source.clear()
        self.source.addItems(self.masters)
        if self.current_master in self.masters:
            self.source.setCurrentIndex(self.masters.index(self.current_master))
        self.targets.clear()
        for master in self.masters:
            item = QtGui.QListWidgetItem(master)
            item.setForeground(anchor_panel.ink())
            item.setFlags(int(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable))
            item.setCheckState(
                QtCore.Qt.Unchecked
                if master == self.current_master
                else QtCore.Qt.Checked
            )
            self.targets.addItem(item)
        self.targets.setMaximumHeight(min(120, 26 * max(1, len(self.masters)) + 6))

    def on_reload(self) -> None:
        """Refill the master lists only when another font brought other masters."""
        known = [self.targets.item(row).text() for row in range(self.targets.count)]
        if known != self.masters:
            self.fill_masters()

    def source_master(self) -> str:
        return self.source.currentText

    def chosen_masters(self) -> list[str]:
        """Ticked target masters, without the source master."""
        items = [self.targets.item(row) for row in range(self.targets.count)]
        return [
            item.text()
            for item in items
            if item.checkState() == QtCore.Qt.Checked
            and item.text() != self.source_master()
        ]

    def planner(self) -> anchor_writer.Planner:
        if len(self.masters) < 2:
            raise ValueError("This font has one master. Nothing to mirror into.")
        if not self.chosen_masters():
            raise ValueError("Tick the masters to copy into.")
        source_master = self.source_master()
        scale, only_missing = self.scale.isChecked(), self.only_missing.isChecked()

        def plan(glyph: Any, master: str, layer: Any) -> list[anchor_writer.Change]:
            source = anchor_writer.layer_of(glyph, source_master)
            if source is None:
                return []
            return mirror_changes(source, layer, scale, only_missing)

        return plan


def main() -> Any:
    """Open the panel, or raise the one that is already open."""
    return scripting.show_script_dialog(MirrorAcrossMasters, KEY)


if __name__ == "__main__":
    main()
