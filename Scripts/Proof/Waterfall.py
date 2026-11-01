# this_file: Scripts/Proof/Waterfall.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Proof · Waterfall
"""Render a line of text in a cascade of sizes, drawn straight from the glyph outlines.

What it does:
    Type any text (use /glyphname for unencoded glyphs, e.g. /a.ss01), pick a
    master and edit the list of pixel sizes. Characters the font lacks show as
    red boxes. Advance widths only: kerning is not applied. Nothing in the font
    changes.

How it works:
    Resolve characters and slash-name tokens against the captured font maps.
    Draw the chosen master at the requested pixel sizes and mark missing
    characters visibly.

Why this design:
    Drawing the current outlines avoids generating a test font, while the
    missing boxes prevent unsupported text from disappearing unnoticed.

How to use:
    Run Proof > Waterfall. Enter text, choose a master and edit the size list.
    Scroll through the cascade to compare the drawings at small and large
    sizes.

Benefit:
    Judge the same text at several sizes with advance spacing and no kerning
    or font edits.
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
character_map = _api.character_map
font_maps = _api.font_maps
layer_path = _api.layer_path
parse_text = _api.parse_text
parse_sizes = _api.parse_sizes
glyph_run = _api.glyph_run
WaterfallView = proof_view_types().WaterfallView
TITLE = "Waterfall"
KEY = "proof_waterfall"
DEFAULT_TEXT = "Hamburgefonstiv 0123"
DEFAULT_SIZES = "10 12 14 18 24 32 48 64 96"


class Waterfall(proof_dialog_type()):
    """Retain the original Proof controls on the shared owned dialog."""

    def __init__(self, parent: Any = None) -> None:
        """Build the original controls and retain only owned native UI resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(620)
        self.resize(760, 600)
        self.cmap, self.names = {}, set()
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.text = QtGui.QLineEdit(DEFAULT_TEXT)
        self.sizes = QtGui.QLineEdit(DEFAULT_SIZES)
        self.master = QtGui.QComboBox()
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Sizes (px)"), 1, 0)
        form.addWidget(self.sizes, 1, 1)
        form.addWidget(QtGui.QLabel("Master"), 1, 2)
        form.addWidget(self.master, 1, 3)
        form.setColumnStretch(1, 2)
        form.setColumnStretch(3, 1)
        root.addLayout(form)
        self.view = WaterfallView()
        self.add_proof_view(self.view, background=True, horizontal_off=True)
        self.add_proof_footer()
        for line in (self.text, self.sizes):
            self._connect(line.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def load_initial(self) -> None:
        """Read maps and master choices atomically, preserving the initial active master."""
        cmap, names = font_maps()
        masters = list(self.package.masters) if self.package else []
        active = self.package.master if self.package else ""
        blocked = self.master.blockSignals(True)
        try:
            self.master.clear()
            for name in masters:
                self.master.addItem(name)
            if active in masters:
                self.master.setCurrentIndex(masters.index(active))
        finally:
            self.master.blockSignals(blocked)
        self.cmap, self.names = cmap, names

    @proof_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete bound-font proof for the original controls."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        master = self.master.currentText
        master = master() if callable(master) else master
        self.glyph_names = parse_text(self.text.text, self.cmap, self.names)
        missing = sum(1 for n in self.glyph_names if n is None)
        glyphs = glyph_run(self.package, self.glyph_names, master)
        size_list = parse_sizes(self.sizes.text)
        self.view.set_content(
            glyphs, size_list, self.package.upm, self.package.ascender_value
        )
        self.subtitle.setText(
            f"Master {master} · {len(self.glyph_names)} glyphs · advance widths, no kerning. Use /name for unencoded glyphs."
        )
        note = f" · {missing} missing (red boxes)" if missing else ""
        self.status.setText(
            f"Line width {self.view.width_units:g} units · {len(size_list)} sizes{note}"
        )


def main() -> Any:
    """Replace the original registry entry with this owned modeless Proof tool."""
    return show_script_dialog(Waterfall, KEY)


if __name__ == "__main__":
    main()
