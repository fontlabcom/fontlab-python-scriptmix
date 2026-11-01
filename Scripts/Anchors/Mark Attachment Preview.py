# this_file: Scripts/Anchors/Mark Attachment Preview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Mark Attachment Preview
"""Preview a mark attached to a base glyph by matching anchors (top + _top), side by side for every master.

What it does:
    Pick a base glyph, a mark glyph and an anchor family; the mark is drawn where
    mark positioning would put it: base anchor minus mark anchor. Offsets per master
    are listed under the drawing. Nothing in the font is changed.

How it works:
    Find a shared anchor family between the chosen base and mark. Draw the
    mark at base-anchor minus mark-anchor and list the offset for each master.

Why this design:
    The offset preview exposes missing or inconsistent anchor pairs without
    constructing a composite or compiling mark features.

How to use:
    Run Anchors > Mark Attachment Preview. Choose base, mark and family, then
    inspect every master panel and its offset or missing-anchor message.

Benefit:
    Check anchor-based placement before editing anchors or building a marked
    glyph.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    anchors_action,
    anchors_api,
    anchors_dialog_type,
    anchors_snapshot_refresh,
    anchors_view_types,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = anchors_api()
current_package = _api.current_package
selected_names = _api.selected_names
font_glyph_names = _api.font_glyph_names
anchor_points = _api.anchor_points
classify = _api.classify
families = _api.families
attachment = _api.attachment
glyph_path = _api.glyph_path
pen = _api.pen
muted = _api.muted
layer_of = _api.attachment_layer_of
AttachmentView = anchors_view_types().AttachmentView

TITLE = "Mark Attachment Preview"
KEY = "anchors_mark_attachment_preview"


class MarkPreview(anchors_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build all original controls before reading native font or anchor values."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(640)
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        self.base = QtGui.QComboBox()
        self.base.addItems(self.bases)
        self.mark = QtGui.QComboBox()
        self.mark.addItems(self.marks)
        self.family = QtGui.QComboBox()
        for column, (label, combo) in enumerate(
            (("Base", self.base), ("Mark", self.mark), ("Anchor", self.family))
        ):
            form.addWidget(QtGui.QLabel(label), 0, column * 2)
            form.addWidget(combo, 0, column * 2 + 1)
            form.setColumnStretch(column * 2 + 1, 1)
        root.addLayout(form)
        self.view = AttachmentView()
        root.addWidget(self.view, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setDefault(True)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(self.base.currentIndexChanged, lambda *a: self.pair_changed())
        self._connect(self.mark.currentIndexChanged, lambda *a: self.pair_changed())
        self._connect(self.family.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    @anchors_action
    def choose(self, base: Any = None, mark: Any = None, family: Any = None) -> None:
        """Select combo entries by name (used by tests and for the initial pair)."""
        for combo, value in ((self.base, base), (self.mark, mark)):
            if value is not None and combo.findText(value) >= 0:
                combo.setCurrentIndex(combo.findText(value))
        if family is not None and self.family.findText(family) >= 0:
            self.family.setCurrentIndex(self.family.findText(family))

    @anchors_snapshot_refresh
    def pair_changed(self) -> None:
        """Keep the previous matching family while rebuilding base and mark choices."""
        base = (
            layer_of(self.package, self.base.currentText, self.current_master)
            if self.package
            else None
        )
        mark = (
            layer_of(self.package, self.mark.currentText, self.current_master)
            if self.package
            else None
        )
        common = families(base, mark) if base is not None and mark is not None else []
        previous = self.family.currentText
        self.family.blockSignals(True)
        self.family.clear()
        self.family.addItems(common)
        if previous in common:
            self.family.setCurrentIndex(common.index(previous))
        self.family.blockSignals(False)
        self.refresh()

    @anchors_snapshot_refresh
    def refresh(self) -> None:
        """Rebuild all original display data for the current source and selectors."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        (base_name, mark_name, family) = (
            self.base.currentText,
            self.mark.currentText,
            self.family.currentText,
        )
        self.subtitle.setText(
            f"{mark_name or '–'} attached to {base_name or '–'} with {family or '–'} / _{family or '–'} on {len(self.masters)} masters. {len(self.bases)} base and {len(self.marks)} mark glyphs found."
        )
        (panels, self.offsets) = ([], {})
        for master in self.masters:
            base = layer_of(self.package, base_name, master)
            mark = layer_of(self.package, mark_name, master)
            if base is None:
                continue
            offset = (
                attachment(base, mark, family) if mark is not None and family else None
            )
            self.offsets[master] = offset
            mark_path = None
            point = None
            if offset is not None:
                mark_path = QtGui.QTransform(1, 0, 0, 1, offset[0], offset[1]).map(
                    glyph_path(mark)
                )
                point = anchor_points(base)[family]
            note = (
                f"offset {offset[0]}, {offset[1]}"
                if offset is not None
                else "no matching anchors"
            )
            panels.append(
                (master, glyph_path(base), mark_path, point, base.advanceWidth, note)
            )
        self.view.set_panels(panels)
        missing = [m for (m, o) in self.offsets.items() if o is None]
        self.status.setText(
            f"Missing anchors on {', '.join(missing)}"
            if missing
            else "Mark offset = base anchor − mark anchor"
        )


def main() -> Any:
    """Replace and show the complete original owned anchor panel."""
    return show_script_dialog(MarkPreview, KEY)


if __name__ == "__main__":
    main()
