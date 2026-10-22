# this_file: Scripts/Components/Count Badges.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Components · Count Badges
"""A painted card per selected glyph: its drawing plus component and contour counts for every master.

What it does:
    Accent badges count components, muted badges count the glyph's own contours; a
    master that differs from the first one is marked with a dot, and auto layers are
    labelled. A quick way to see which glyphs are composites, outlines or a mix.
    Nothing in the font is changed.

How it works:
    Use the shared component card view for the selected glyphs. Draw each
    glyph and count its own contours and components per master, marking
    differences from the first master.

Why this design:
    Counts beside the drawing make mixed outline/component construction easier
    to spot than names alone.

How to use:
    Select glyphs and run Components > Count Badges. Inspect each master's
    badges, mismatch dots and automatic-layer labels; scroll or resize to view
    more cards.

Benefit:
    Review construction differences without decomposing components or editing
    layer geometry.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_api,
    components_dialog_type,
    components_snapshot_refresh,
    components_view_types,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = components_api()
current_package = _api.current_package
selected_glyphs = _api.selected_glyphs
layer_of = _api.layer_of
counts = _api.counts
glyph_path = _api.glyph_path
pen = _api.pen
muted = _api.muted
frame = _api.frame
BadgeGrid = components_view_types().BadgeGrid

TITLE = "Component Count Badges"
KEY = "components_count_badges"
(CARD_W, DRAW_H, LINE_H, PAD) = (212, 92, 20, 10)
COLUMNS = 3


class CountBadges(components_dialog_type()):
    """Complete original component inspector with owned read-only source guards."""

    def __init__(self, parent: Any = None) -> None:
        """Build every original control and Close before reading native sources."""
        super().__init__(parent, TITLE, KEY)
        root = self.root
        self.setMinimumWidth(COLUMNS * (CARD_W + 8) + 84)
        self.grid = BadgeGrid()
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidget(self.grid)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QtGui.QFrame.NoFrame)
        self.scroll_area.setMinimumHeight(self.grid_height_hint())
        root.addWidget(self.scroll_area, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.close_button.setDefault(True)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def grid_height_hint(self) -> Any:
        """Preserve the original grid height hint calculation and native interface."""
        lines = DRAW_H + LINE_H + len(self.masters) * LINE_H + 2 * PAD
        return (
            min(2, max(1, (len(self.glyphs) + COLUMNS - 1) // COLUMNS)) * (lines + 8)
            + 6
        )

    @components_snapshot_refresh
    def refresh(self) -> None:
        """Preserve the original refresh calculation and native interface."""
        count = len(self.glyphs)
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        elif not count:
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again."
            )
        else:
            self.subtitle.setText(
                f"{count} glyph{('s' if count != 1 else '')}, drawn from {self.current_master}. Accent: components · grey: own contours · dot: auto layer (blue) or differs (red)."
            )
        (cards, self.counts) = ([], {})
        for glyph in self.glyphs:
            per = {
                m: counts(l)
                for (m, l) in ((m, layer_of(glyph, m)) for m in self.masters)
                if l is not None
            }
            self.counts[glyph.name] = {m: list(v) for (m, v) in per.items()}
            first = next(iter(per.values()), None)
            lines = [
                (m, c, k, auto, first is not None and (c, k) != first[:2])
                for (m, (c, k, auto)) in per.items()
            ]
            shown = layer_of(glyph, self.current_master) or next(
                (
                    l
                    for l in (layer_of(glyph, m) for m in self.masters)
                    if l is not None
                ),
                None,
            )
            path = glyph_path(shown) if shown is not None else QtGui.QPainterPath()
            box = QtCore.QRectF(
                0, -250, max(shown.advanceWidth if shown else 500, 1), 1000
            ).united(path.boundingRect())
            cards.append((glyph.name, path, box, lines))
        self.grid.set_cards(
            cards, max(self.scroll_area.viewport().width, COLUMNS * (CARD_W + 8) + 4)
        )
        composites = sum(
            1 for per in self.counts.values() if any(v[0] for v in per.values())
        )
        self.status.setText(f"{composites} of {count} glyphs use components")

    def resizeEvent(self, event: Any) -> None:
        """Preserve the original resizeEvent calculation and native interface."""
        QtGui.QDialog.resizeEvent(self, event)
        self.grid.relayout(self.scroll_area.viewport().width)


def select_in_font(names: list[str]) -> None:
    """Route the original helper alias through the active panel's source guard."""
    import sys

    dialog = getattr(sys, "_fontlab_samples", {}).get(KEY)
    if dialog is None:
        raise ValueError("Open this panel before selecting its results.")
    dialog.select_names(names)


def main() -> Any:
    """Replace and display the complete original owned component inspector."""
    return show_script_dialog(CountBadges, KEY)


if __name__ == "__main__":
    main()
