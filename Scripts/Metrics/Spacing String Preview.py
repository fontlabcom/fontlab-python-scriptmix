# this_file: Scripts/Metrics/Spacing String Preview.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Metrics · Spacing String Preview
"""Render a spacing control string such as HOHnono from the font's own outlines and advances.

Type characters or /glyphname tokens, pick a master, and judge the rhythm of straight and round
sidebearings without generating a font. Advance boxes and LSB/RSB numbers can be shown under
each glyph. Nothing is edited; the preview follows the outlines as they are now."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package as current_package,  # noqa: PLC0414 - original public helper
)
from fly.ap.scripting import (
    inspectors_api,
    inspectors_dialog_type,
    inspectors_snapshot_refresh,
    inspectors_view_types,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = inspectors_api()
muted = _api.muted
parse_text = _api.parse_text
outline = _api.outline
layout = _api.layout
Canvas = inspectors_view_types().Canvas
TITLE = "Spacing String Preview"
KEY = "metrics_spacing_string_preview"
DEFAULT_TEXT = "HHOHOOH nnonoon"
MARGIN = 24


class SampleDialog(inspectors_dialog_type()):
    """Original menu shell on the existing owned Proof/Names/Masters lifecycle."""

    def __init__(self, parent: Any = None) -> None:
        """Finish controls/status/Close before fallible font reads."""
        super().__init__(parent, TITLE, KEY)


class SpacingPreview(SampleDialog):
    """Complete original inspector with complete snapshots and owned cleanup."""

    ACTION = None

    def build(self) -> None:
        """Retain every original control/default before reading native data."""
        self.setMinimumWidth(640)
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.text = QtGui.QLineEdit(DEFAULT_TEXT)
        self.text.setPlaceholderText("Characters, or /glyphname tokens")
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        self.show_boxes = QtGui.QCheckBox("Advance boxes")
        self.show_boxes.setChecked(True)
        self.show_numbers = QtGui.QCheckBox("LSB / RSB numbers")
        self.show_numbers.setChecked(True)
        form.addWidget(QtGui.QLabel("Text"), 0, 0)
        form.addWidget(self.text, 0, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Master"), 1, 0)
        form.addWidget(self.master, 1, 1)
        form.addWidget(self.show_boxes, 1, 2)
        form.addWidget(self.show_numbers, 1, 3)
        form.setColumnStretch(1, 1)
        self.root.addLayout(form)

        self.canvas = Canvas(self)
        self.root.addWidget(self.canvas, 1)

        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.show_boxes.toggled, lambda *a: self.canvas.update())
        self._connect(self.show_numbers.toggled, lambda *a: self.canvas.update())

    def chosen_master(self) -> Any:
        """Return the original selector master without changing the font master."""
        return self.masters[self.master.currentIndex] if self.masters else ""

    def path(self, name: Any) -> Any:
        """Return only a path captured by the completed refresh."""
        return self.paths[(name, self.chosen_master())]

    def empty_message(self) -> str:
        """Keep the original no-font and empty-text canvas messages."""
        if self.package is None:
            return "Open a font first."
        return "Type characters or /glyphname tokens above."

    @inspectors_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete original report under the shared font/master snapshot guard."""
        self.sync_controls()
        self.ascender = self.package.ascender_value if self.package else 800
        self.descender = self.package.descender_value if self.package else -200
        self.paths, self._outline_sources = {}, {}
        if self.package is None:
            self.rows = []
            self.subtitle.setText("Open a font first.")
        else:
            names = parse_text(self.text.text, self.package)
            self.rows = layout(self.package, names, self.chosen_master())
            self.paths = {
                (name, self.chosen_master()): outline(
                    self.package.findName(name).findLayer(self.chosen_master())
                )
                for name, *_ in self.rows
            }
            self._outline_sources = {
                (name, self.chosen_master()): _api.outline_source(
                    self.package.findName(name).findLayer(self.chosen_master())
                )
                for name, *_ in self.rows
            }
            self.subtitle.setText(
                f"{self.chosen_master()} master · {len(names)} glyphs drawn from their outlines and advances, no kerning",
            )
        width = self.rows[-1][1] + self.rows[-1][2] if self.rows else 0
        self.status.setText(f"{len(self.rows)} glyphs · line width {width:g} units")
        self.canvas.update()


def main() -> Any:
    """Replace and show the complete original owned inspector."""
    return show_script_dialog(SpacingPreview, KEY)


if __name__ == "__main__":
    main()
