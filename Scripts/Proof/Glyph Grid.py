# this_file: Scripts/Proof/Glyph Grid.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Proof · Glyph Grid
"""Show the selected glyphs on every master side by side, drawn from their outlines.

What it does:
    Rows are glyphs, columns are masters; all cells share one scale so weights
    and widths compare directly. The slider zooms. Composites are drawn with
    their components in place. Nothing in the font changes.

How it works:
    Read selected glyph layers and build a grid with glyphs as rows and
    masters as columns. Fit outlines and advance labels at one common scale.

Why this design:
    A shared scale keeps width and weight differences visible rather than
    fitting each glyph independently.

How to use:
    Select glyphs and run Proof > Glyph Grid. Adjust the zoom slider and
    inspect each master column. Use Reload selection after choosing another
    set in the Font window.

Benefit:
    Compare master drawings directly without exporting fonts or altering the
    current outlines.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - original public interface
    proof_api,
    proof_dialog_type,
    proof_snapshot_refresh,
    proof_view_types,
    show_script_dialog,
)
from fly.ap.scripting import (
    names_muted as muted,  # noqa: F401 - original public interface
)

QtCore, QtGui = (qt.QtCore, qt.QtGui)
fontlab = ap.fontlab
_api = proof_api()
selected_glyphs = _api.selected_glyphs
layer_path = _api.layer_path
metrics = _api.metrics
Grid = proof_view_types().Grid
TITLE = "Glyph Grid"
KEY = "proof_glyph_grid"


class GlyphGrid(proof_dialog_type()):
    """Retain the original Proof controls on the shared owned dialog."""

    def __init__(self, parent: Any = None) -> None:
        """Build the original controls and retain only owned native UI resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(560)
        self.resize(640, 560)
        self.glyphs, self.masters = [], []
        root = self.root
        form = QtGui.QHBoxLayout()
        form.setSpacing(10)
        form.addWidget(QtGui.QLabel("Zoom"))
        self.zoom = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.zoom.setRange(48, 240)
        self.zoom.setValue(110)
        form.addWidget(self.zoom, 1)
        self.zoom_label = QtGui.QLabel()
        self.zoom_label.setMinimumWidth(48)
        form.addWidget(self.zoom_label)
        root.addLayout(form)
        self.grid = Grid()
        self.add_proof_view(self.grid)
        self.add_proof_footer(reload_selection=True)
        self._connect(self.zoom.valueChanged, lambda *a: self.refresh())
        self._connect(self.reload_button.clicked, lambda *a: self.reload())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def load_initial(self) -> None:
        """Read selection and masters inside the complete guarded initial transaction."""
        glyphs = selected_glyphs(self.package) if self.package else []
        masters = list(self.package.masters) if self.package else []
        self.glyphs, self.masters = glyphs, masters

    def reload(self) -> None:
        """Explicitly reload the current font and selection without changing either."""
        self._initial_ready = self._binding_set = False
        self.refresh()

    @proof_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete bound-font proof for the original controls."""
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then click Reload selection."
            )
        else:
            self.subtitle.setText(
                f"{count} glyph{('s' if count != 1 else '')} × {len(self.masters)} masters, one scale for all cells; numbers are advance widths."
            )
        cells = []
        for glyph in self.glyphs:
            row = []
            for master in self.masters:
                layer = glyph.findLayer(master)
                if layer is None or layer.isNull:
                    row.append((master, None, 0))
                else:
                    row.append((master, layer_path(layer), layer.advanceWidth))
            cells.append((glyph.name, row))
        frame = metrics(self.package) if self.package else (-250, 750)
        for _, row in cells:
            for _, path, _ in row:
                if path is not None and (not path.isEmpty()):
                    box = path.boundingRect()
                    frame = (min(frame[0], box.top()), max(frame[1], box.bottom()))
        self.grid.set_content(cells, self.masters, frame, self.zoom.value)
        self.zoom_label.setText(f"{self.zoom.value} px")
        self.status.setText(f"{count * len(self.masters)} cells")


def main() -> Any:
    """Replace the original registry entry with this owned modeless Proof tool."""
    return show_script_dialog(GlyphGrid, KEY)


if __name__ == "__main__":
    main()
