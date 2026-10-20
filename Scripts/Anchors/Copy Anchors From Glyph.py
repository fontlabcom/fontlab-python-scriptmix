# this_file: Scripts/Anchors/Copy Anchors From Glyph.py
# SPDX-License-Identifier: Apache-2.0
"""Copy a source glyph's anchors to selected glyphs, master by master.

Type a source name with fontwide completion; choose merge/replace, width scaling
and current/all masters. Automatic layers are skipped. Unsafe automatic
dependants and stale source previews refuse the complete write before history.
One Copy is one native Undo. Close disconnects every owned callback.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    anchor_copy_api,
    anchor_copy_dialog_type,
    anchor_copy_snapshot_refresh,
    components_action,
    masters_make_table,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Copy Anchors from Glyph", "anchors_copy_from_glyph"
_api = anchor_copy_api()
layer_of, anchor_points, plan = _api.layer_of, _api.anchor_points, _api.plan


def fmt(point: tuple[int, int] | None) -> str:
    """Format a rounded anchor pair, or label an anchor removal."""
    return "removed" if point is None else f"{point[0]}, {point[1]}"


class CopyAnchors(anchor_copy_dialog_type()):
    """Original complete copy workflow on the shared owned lifecycle."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent, TITLE, KEY)

    def build(self) -> None:
        """Retain all original copy controls before binding any native font data."""
        self.setMinimumWidth(560)
        self._scanning = False
        self.last_result = None
        self.glyphs = []
        self.pending_targets = set()
        self.pending_origins = []
        root = self.root
        form = QtGui.QFormLayout()
        form.setVerticalSpacing(8)
        self.source = QtGui.QLineEdit()
        self.source.setPlaceholderText("source glyph name, e.g. n")
        self.completer = QtGui.QCompleter(self)
        self.completion_model = QtGui.QStringListModel(self.completer)
        self.completer.setModel(self.completion_model)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self.source.setCompleter(self.completer)
        self.mode = QtGui.QComboBox()
        self.mode.addItem("Add and move (keep other anchors)")
        self.mode.addItem("Replace (remove anchors the source lacks)")
        self.scale = QtGui.QCheckBox("Scale x by advance-width ratio")
        self.scale.setChecked(True)
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addRow("Source glyph", self.source)
        form.addRow("Mode", self.mode)
        form.addRow("", self.scale)
        form.addRow("Masters", self.scope)
        root.addLayout(form)
        self.table = masters_make_table(
            ["Glyph · master", "Anchor", "Current", "New"], 220
        )
        self.table.setWordWrap(False)
        root.addWidget(self.table, 1)
        self.rebuild_label = QtGui.QLabel()
        self.rebuild_label.setWordWrap(True)
        root.addWidget(self.rebuild_label)
        self._connect(self.source.textChanged, lambda *a: self.refresh())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.scale.toggled, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())

    def source_glyph(self) -> "fontlab.flGlyph | None":
        """Return the named native glyph, or None without a source font or name."""
        name = self.source.text.strip()
        return self.package.findName(name) if self.package and name else None

    @anchor_copy_snapshot_refresh
    def refresh(self) -> None:
        self.pending_targets = set()
        self.pending_origins = []
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select the glyphs to receive anchors, then run this script again."
            )
        else:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (
                " …" if count > 8 else ""
            )
            self.subtitle.setText(
                f"Anchors go to {count} glyph{('s' if count != 1 else '')}: {names}"
            )
        source = self.source_glyph()
        rows = []
        if source is not None:
            replace = self.mode.currentIndex == 1
            for glyph in self.glyphs:
                if glyph.name == source.name:
                    continue
                for master in self.chosen_masters():
                    (src, dst) = (layer_of(source, master), layer_of(glyph, master))
                    if src is None or dst is None:
                        continue
                    tag = f"{glyph.name} · {master}"
                    if dst.autoLayer:
                        rows.append(((tag, "auto layer", "", "skipped"), False))
                        continue
                    for name, old, new in plan(
                        src, dst, self.scale.isChecked(), replace
                    ):
                        if old != new:
                            self.pending_targets.add(glyph.name)
                            if old is not None and new == (0, 0):
                                self.pending_origins.append((glyph.name, master, name))
                        rows.append(
                            (
                                (tag, name, "–" if old is None else fmt(old), fmt(new)),
                                old != new,
                            )
                        )
        self.fill_rows(rows)
        pending = sum(1 for (_, changed) in rows if changed)
        self.apply_button.setEnabled(pending > 0)
        if not self.source.text.strip():
            self.status.setText("Type the source glyph name")
        elif source is None:
            self.status.setText(f"No glyph named “{self.source.text.strip()}”")
        else:
            self.status.setText(
                f"{pending} anchor change{('s' if pending != 1 else '')} from {source.name}"
            )
        self.guard_apply()

    @components_action
    def apply(self) -> Any:
        self.last_result = _api.run(
            self.source_glyph(),
            self.glyphs,
            self.chosen_masters(),
            self.scale.isChecked(),
            self.mode.currentIndex == 1,
            package=self.package,
            title=TITLE,
        )
        self._snapshot_valid = False
        self.refresh()
        result = self.last_result
        note = (
            f" · {len(result['skipped'])} auto layers skipped"
            if result["skipped"]
            else ""
        )
        self.status.setText(
            f"Copied {result['anchors']} anchor changes to {result['layers']} layers{note}"
        )


def main() -> Any:
    """Replace and show one complete owned copy panel."""
    return show_script_dialog(CopyAnchors, KEY)


if __name__ == "__main__":
    main()
