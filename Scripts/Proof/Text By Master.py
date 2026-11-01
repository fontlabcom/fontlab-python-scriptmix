# this_file: Scripts/Proof/Text By Master.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Proof · Text By Master
"""Render the same text once per master, stacked, to compare weight and width at a glance.

What it does:
    Each row is drawn from that master's outlines with its line width in units.
    Type text (use /glyphname for unencoded glyphs), adjust the size and scroll
    through the masters. Advance widths only: kerning is not applied. Nothing in
    the font changes.

How it works:
    Parse characters and slash-name tokens, read each master's glyph run and
    draw stacked rows with their total advances. Use the same requested proof
    size.

Why this design:
    A repeated text line makes width and weight changes easier to compare
    across the complete master set.

How to use:
    Run Proof > Text By Master. Enter proof text, adjust the size and scroll
    through the master rows. Inspect missing-character counts as well as the
    drawings.

Benefit:
    Compare master text with advance spacing while keeping kerning and font
    data unchanged.
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
font_maps = _api.font_maps
layer_path = _api.layer_path
parse_text = _api.parse_text
glyph_run = _api.glyph_run
MasterRows = proof_view_types().MasterRows
TITLE = "Text by Master"
KEY = "proof_text_by_master"
DEFAULT_TEXT = "Hamburgefonstiv"


class TextByMaster(proof_dialog_type()):
    """Retain the original Proof controls on the shared owned dialog."""

    def __init__(self, parent: Any = None) -> None:
        """Build the original controls and retain only owned native UI resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(600)
        self.resize(720, 600)
        self.cmap, self.names = {}, set()
        self.rows = []
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.text = QtGui.QLineEdit(DEFAULT_TEXT)
        self.size_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setRange(12, 160)
        self.size_slider.setValue(48)
        self.size_label = QtGui.QLabel()
        self.size_label.setMinimumWidth(48)
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 2)
        form.addWidget(QtGui.QLabel("Size"), 1, 0)
        form.addWidget(self.size_slider, 1, 1)
        form.addWidget(self.size_label, 1, 2)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.view = MasterRows()
        self.add_proof_view(self.view, background=True)
        self.add_proof_footer()
        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.size_slider.valueChanged, lambda *a: self.refresh())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def load_initial(self) -> None:
        """Read the complete encoding/name maps after the empty UI and Close exist."""
        self.cmap, self.names = font_maps()

    @proof_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete bound-font proof for the original controls."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        glyph_names = parse_text(self.text.text, self.cmap, self.names)
        self.rows = []
        for master in self.package.masters:
            run = glyph_run(self.package, glyph_names, master)
            self.rows.append((master, run, sum((advance for _, advance in run))))
        frame = (self.package.descender_value, self.package.ascender_value)
        self.view.set_content(
            self.rows, self.size_slider.value, self.package.upm, frame
        )
        self.size_label.setText(f"{self.size_slider.value} px")
        missing = sum(1 for n in glyph_names if n is None)
        self.subtitle.setText(
            f"{len(self.rows)} masters · {len(glyph_names)} glyphs · advance widths, no kerning."
        )
        widths = [w for _, _, w in self.rows]
        spread = f" · widths {min(widths):g}–{max(widths):g} units" if widths else ""
        self.status.setText(
            f"{len(self.rows)} rows{spread}"
            + (f" · {missing} missing" if missing else "")
        )


def main() -> Any:
    """Replace the original registry entry with this owned modeless Proof tool."""
    return show_script_dialog(TextByMaster, KEY)


if __name__ == "__main__":
    main()
