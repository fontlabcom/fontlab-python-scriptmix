# this_file: Scripts/Masters/Interpolation Preview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Masters · Interpolation Preview
"""Preview a glyph between two masters with a slider, from the masters' own nodes.

What it does:
    Pick two masters and drag the slider: the painter blends every node linearly (0 % = first
    master, 100 % = second) and draws the result over faint outlines of both masters. Incompatible
    layers (different contour or node structure) are reported instead of drawn. Read-only.

How it works:
    Use the shared Masters preview to compare contour and node structure
    before blending corresponding node coordinates linearly between two chosen
    masters.

Why this design:
    The tool reports incompatible structures instead of drawing a misleading
    blend from unrelated node positions.

How to use:
    Select a glyph and run Masters > Interpolation Preview. Choose two
    masters, move the percentage slider and compare the blended path with the
    faint source paths.

Benefit:
    Inspect a node-based interpolation proposal without adding instances or
    changing master outlines.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - Original public helper re-export.
    interpolation_api,
    interpolation_view_type,
    review_dialog_type,
    review_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = interpolation_api()
selected_names, master_layers = _api.selected_names, _api.master_layers
node_points, outline, problem, blend = (
    _api.node_points,
    _api.outline,
    _api.problem,
    _api.blend,
)
outline_path, fit_transform = _api.outline_path, _api.fit_transform
muted = _api.muted
SampleDialog = review_dialog_type()
BlendView = interpolation_view_type()
TITLE = "Interpolation Preview"
KEY = "masters_interpolation_preview"


class Interpolation(SampleDialog):
    """Keep the original complete two-master node interpolation panel."""

    ACTION = None

    def __init__(self, parent: Any = None) -> None:
        """Build every original control and Close before native source binding."""
        super().__init__(parent, TITLE, KEY)
        self.build()
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.close_button)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.root.addLayout(footer)
        self.initial_refresh()

    def build(self) -> None:
        """Build every original glyph/master/position control and the full preview."""
        self.setMinimumWidth(560)
        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        self.root.addLayout(grid)
        self.glyph_combo = QtGui.QComboBox()
        for name in self.names:
            self.glyph_combo.addItem(name)
        self.first, self.second = (QtGui.QComboBox(), QtGui.QComboBox())
        for combo in (self.first, self.second):
            for master in self.masters:
                combo.addItem(master)
        if len(self.masters) > 1:
            self.second.setCurrentIndex(len(self.masters) - 1)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.percent = QtGui.QLabel("50 %")
        self.percent.setMinimumWidth(48)
        self.percent.setAlignment(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter))
        for combo in (self.glyph_combo, self.first, self.second):
            self._connect(combo.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.slider.valueChanged, lambda *a: self.refresh())
        grid.addWidget(QtGui.QLabel("Glyph"), 0, 0)
        grid.addWidget(self.glyph_combo, 0, 1, 1, 3)
        grid.addWidget(QtGui.QLabel("Between"), 1, 0)
        grid.addWidget(self.first, 1, 1)
        grid.addWidget(QtGui.QLabel("and"), 1, 2)
        grid.addWidget(self.second, 1, 3)
        grid.addWidget(QtGui.QLabel("Position"), 2, 0)
        grid.addWidget(self.slider, 2, 1, 1, 2)
        grid.addWidget(self.percent, 2, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        self.view = BlendView()
        self.view.report = self.paint_report
        self.root.addWidget(self.view, 1)

    @review_snapshot_refresh
    def refresh(self) -> None:
        """Blend complete corresponding nodes after validating the old cached source."""
        if not hasattr(self, "view"):
            return
        self.mix = []
        if not self.describe_selection():
            self.view.a = self.view.b = self.view.mix = []
            self.view.update()
            return
        glyph = self.package.findName(self.glyph_combo.currentText)
        layers = master_layers(glyph, self.masters)
        first, second = (
            layers.get(self.first.currentText),
            layers.get(self.second.currentText),
        )
        t = self.slider.value / 100.0
        self.percent.setText(f"{self.slider.value} %")
        a = outline(first) if first is not None else []
        b = outline(second) if second is not None else []
        why = problem(a, b)
        self.view.a, self.view.b = (a, b)
        if why is None:
            self.mix = blend(a, b, t)
            self.view.message = ""
            self.status.setText(
                f"{glyph.name}: {self.slider.value} % from {self.first.currentText} to {self.second.currentText} · {sum(len(c) for c in a)} nodes"
            )
        else:
            self.view.message = f"Not compatible: {why}"
            self.status.setText(
                f"{glyph.name} cannot interpolate between these masters: {why}"
            )
        self.view.mix = self.mix
        self.view.update()


def main() -> Any:
    """Show the original non-modal interpolation controls and complete painter."""
    return show_script_dialog(Interpolation, KEY)


if __name__ == "__main__":
    main()
