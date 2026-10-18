# this_file: Scripts/Guides/Copy Guides Between Masters.py
# SPDX-License-Identifier: Apache-2.0
"""Merge or replace glyph guides on explicitly selected target masters.

Select glyphs and choose From, To, merge/replace and optional width scaling.
Inspect every add/remove row, then use Copy. Nonpositive widths cannot be scaled.
Matching target guides retain native colour, tags and geometry; hints are kept.
Unsafe automatic dependants are refused before history. Close releases signals.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    guide_rewrite_api,
    guide_rewrite_dialog_type,
    guides_api,
    masters_make_table,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Copy Guides Between Masters", "guides_copy_between_masters"
_api, _guide = guide_rewrite_api(), guides_api()
master_layers, guide_record, glyph_guides = (
    _guide.master_layers,
    _guide.guide_record,
    _guide.glyph_guides,
)
target_records, scaled = _api.target_records, _api.scaled


class CopyGuides(guide_rewrite_dialog_type()):
    """Complete original guide controls on the shared owned lifecycle."""

    ACTION = "Copy"

    def __init__(self, parent: Any = None) -> None:
        """Finish controls before any native source read."""
        super().__init__(parent, TITLE, KEY)

    def build(self) -> None:
        """Retain every original control and callback."""
        self.setMinimumWidth(560)
        self.last_result = None
        self.glyphs = []
        self.glyph = None
        self.pending_targets = set()
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.source = QtGui.QComboBox()
        self.source.addItems(self.masters)
        if self.current_master in self.masters:
            self.source.setCurrentIndex(self.masters.index(self.current_master))
        targets = QtGui.QGridLayout()
        self.targets_grid = targets
        targets.setHorizontalSpacing(14)
        self.target_checks = {}
        for index, master in enumerate(self.masters):
            check = QtGui.QCheckBox(master)
            check.setChecked(True)
            self.target_checks[master] = check
            targets.addWidget(check, index // 3, index % 3)
        self.mode = QtGui.QComboBox()
        self.mode.addItems(["Add to the target guides", "Replace the target guides"])
        self.follow_width = QtGui.QCheckBox(
            "Scale x positions by the advance-width ratio"
        )
        self.follow_width.setChecked(True)
        form.addWidget(QtGui.QLabel("From"), 0, 0)
        form.addWidget(self.source, 0, 1)
        form.addWidget(QtGui.QLabel("To"), 1, 0, QtCore.Qt.AlignTop)
        form.addLayout(targets, 1, 1)
        form.addWidget(QtGui.QLabel("Mode"), 2, 0)
        form.addWidget(self.mode, 2, 1)
        form.addWidget(self.follow_width, 3, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.table = masters_make_table(
            ["Glyph · master", "Guide", "Position", "Action"], 220
        )
        root.addWidget(self.table, 1)
        self._connect(self.source.currentIndexChanged, lambda *a: self.refresh())
        for check in self.target_checks.values():
            self._connect(check.toggled, lambda *a: self.refresh())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.follow_width.toggled, lambda *a: self.refresh())

    def targets(self) -> Any:
        source = self.source.currentText
        return [
            m for m in self.masters if m != source and self.target_checks[m].isChecked()
        ]

    def position(self, record: Any) -> Any:
        x, y, angle, _ = record
        return (
            f"y {y:g}"
            if angle == 0
            else f"x {x:g}"
            if angle == 90
            else f"{x:g}, {y:g} · {angle:g}°"
        )

    def plan(self) -> Any:
        """[(glyph, master, layer, old records, new records or None, note)]."""
        self.check_binding()
        planned = []
        source_master = self.source.currentText
        for glyph in self.glyphs:
            source = glyph.findLayer(source_master)
            if source is None or source.isNull:
                continue
            for master, layer in master_layers(glyph, self.targets()):
                old = [guide_record(g) for g in glyph_guides(layer)]
                if layer.autoLayer:
                    planned.append(
                        (glyph, master, layer, old, None, "auto layer, skipped")
                    )
                    continue
                new = target_records(
                    source,
                    layer,
                    self.mode.currentIndex == 1,
                    self.follow_width.isChecked(),
                )
                note = "zero advance width, skipped" if new is None else ""
                planned.append((glyph, master, layer, old, new, note))
        self.pending_targets = {
            g.name
            for g, m, layer, old, new, note in planned
            if new is not None and new != old
        }
        return planned

    @masters_snapshot_refresh
    def refresh(self) -> Any:
        for master, check in self.target_checks.items():
            check.setEnabled(master != self.source.currentText)
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again."
            )
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (
                " …" if count > 8 else ""
            )
            self.subtitle.setText(
                f"Copies glyph guides in {count} glyph{('s' if count != 1 else '')}: {names}"
            )
        rows, changes = ([], 0)
        for glyph, master, _layer, old, new, note in self.plan() if self.glyphs else []:
            label = f"{glyph.name} · {master}"
            if new is None:
                rows.append((label, note, "", ""))
                continue
            rows.extend(
                (label, record[3] or "(unnamed)", self.position(record), "remove")
                for record in old
                if record not in new
            )
            rows.extend(
                (label, record[3] or "(unnamed)", self.position(record), "add")
                for record in new
                if record not in old
            )
            if new != old:
                changes += 1
        self.fill_guide_rows(rows, {2}, 3)
        self.apply_button.setEnabled(changes > 0)
        self.status.setText(f"{changes} layer{('s' if changes != 1 else '')} to change")
        self.guard_apply(changes)

    @components_action
    def apply(self) -> Any:
        jobs = [
            (glyph, layer, new)
            for glyph, master, layer, old, new, note in self.plan()
            if new is not None and new != old
        ]
        self.last_result = _api.replace_guides(self.package, jobs, TITLE)
        self.refresh()
        self.status.setText(f"Copied guides to {self.last_result['layers']} layers")


def main() -> Any:
    """Replace and show the complete owned guide editor."""
    return show_script_dialog(CopyGuides, KEY)


if __name__ == "__main__":
    main()
