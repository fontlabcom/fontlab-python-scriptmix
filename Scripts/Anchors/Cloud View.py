# this_file: Scripts/Anchors/Cloud View.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Cloud View
"""Overlay the selected glyphs faintly and show every anchor of one name as a cloud of dots, per master.

A tight cloud means marks will sit consistently; a stray dot is a glyph whose anchor
is off. Hover-free and read-only: the list under each panel gives the extreme values.
Nothing in the font is changed."""

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
selected_glyphs = _api.selected_glyphs
anchor_names = _api.anchor_names
cloud = _api.cloud
glyph_path = _api.glyph_path
pen = _api.pen
muted = _api.muted
frame = _api.frame
layer_of = _api.cloud_layer_of
CloudView = anchors_view_types().CloudView

TITLE = "Anchor Cloud"
KEY = "anchors_cloud_view"


class AnchorCloud(anchors_dialog_type()):
    def __init__(self, parent: Any = None) -> None:
        """Build all original controls before reading native font or anchor values."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(660)
        root = self.root
        bar = QtGui.QHBoxLayout()
        bar.setSpacing(10)
        self.name = QtGui.QComboBox()
        bar.addWidget(QtGui.QLabel("Anchor"))
        bar.addWidget(self.name, 1)
        root.addLayout(bar)
        self.view = CloudView()
        root.addWidget(self.view, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setDefault(True)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(self.name.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    @anchors_action
    def choose(self, name: Any) -> None:
        """Select named original options while checking the prior displayed source."""
        if self.name.findText(name) >= 0:
            self.name.setCurrentIndex(self.name.findText(name))

    @anchors_snapshot_refresh
    def refresh(self) -> None:
        """Rebuild all original display data for the current source and selectors."""
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again."
            )
        else:
            names = ", ".join(g.name for g in self.glyphs[:10]) + (
                " …" if count > 10 else ""
            )
            self.subtitle.setText(
                f"{count} glyph{('s' if count != 1 else '')} overlaid: {names}"
            )
        name = self.name.currentText
        (panels, self.points) = ([], {})
        for master in self.masters:
            paths = [
                glyph_path(l)
                for l in (layer_of(g, master) for g in self.glyphs)
                if l is not None
            ]
            self.points[master] = cloud(self.glyphs, master, name) if name else []
            panels.append((master, paths, self.points[master]))
        self.view.set_panels(panels if self.glyphs else [])
        found = sum(len(p) for p in self.points.values())
        self.status.setText(
            f"{found} “{name}” anchors on {len(self.masters)} masters"
            if name
            else "No anchors"
        )


def main() -> Any:
    """Replace and show the complete original owned anchor panel."""
    return show_script_dialog(AnchorCloud, KEY)


if __name__ == "__main__":
    main()
