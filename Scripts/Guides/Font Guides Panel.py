# this_file: Scripts/Guides/Font Guides Panel.py
# SPDX-License-Identifier: Apache-2.0
"""List font-guide names and add named horizontal or vertical glyph guides.

Select glyphs, run the script, name a guide and choose its position and master
scope. Inspect every planned row, then use Add glyph guide. Existing matching
guides and automatic layers are kept. Fonts whose automatic dependants cannot
be restored by Undo are refused before editing. Close releases owned signals.
This panel adds glyph guides; it does not add font-wide guides.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    components_action,
    current_package,  # noqa: F401 - retain the original public helper.
    guides_api,
    guides_dialog_type,
    masters_make_table,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
TITLE, KEY = "Font Guides Panel", "guides_font_guides_panel"
_api = guides_api()
font_guide_names, master_layers, guide_record, glyph_guides = (
    _api.font_guide_names,
    _api.master_layers,
    _api.guide_record,
    _api.glyph_guides,
)


class FontGuidesPanel(guides_dialog_type()):
    """List font-guide names and add a complete named glyph guide."""

    ACTION = "Add glyph guide"

    def __init__(self, parent: Any = None) -> None:
        """Use the shared owned shell, with status and Close before font binding."""
        super().__init__(parent, TITLE, KEY)

    def build(self) -> None:
        """Build the original controls before the first native source access."""
        self.setMinimumWidth(540)
        self.glyphs = []
        self.pending_targets = set()
        self.last_result = None
        root = self.root
        self.font_guides = QtGui.QLabel()
        self.font_guides.setWordWrap(True)
        root.addWidget(self.font_guides)
        self.notice = QtGui.QLabel(
            "Font guide names are shown above. Add a glyph guide to the selected glyphs below."
        )
        self.notice.setWordWrap(True)
        self.notice.setStyleSheet(
            f"color: {self.palette.color(QtGui.QPalette.Link).name()};"
        )
        root.addWidget(self.notice)
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.direction = QtGui.QComboBox()
        self.direction.addItems(["Horizontal", "Vertical"])
        self.position = self._spin(-5000, 5000, 0)
        self.guide_name = QtGui.QLineEdit()
        self.guide_name.setPlaceholderText("guide name")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Direction"), 0, 0)
        form.addWidget(self.direction, 0, 1)
        form.addWidget(QtGui.QLabel("Position"), 0, 2)
        form.addWidget(self.position, 0, 3)
        form.addWidget(QtGui.QLabel("Name"), 1, 0)
        form.addWidget(self.guide_name, 1, 1, 1, 3)
        form.addWidget(QtGui.QLabel("Masters"), 2, 0)
        form.addWidget(self.scope, 2, 1, 1, 3)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(3, 1)
        root.addLayout(form)
        self.table = masters_make_table(
            ["Glyph · master", "Glyph guides now", "Action"], 180
        )
        root.addWidget(self.table, 1)
        self._connect(self.direction.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.position.valueChanged, lambda *a: self.refresh())
        self._connect(self.guide_name.textChanged, lambda *a: self.refresh())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())

    def record(self) -> tuple:
        """Read the original named horizontal/vertical guide coordinates."""
        value = float(self.position.value)
        name = self.guide_name.text.strip()
        return (
            (0.0, value, 0.0, name)
            if self.direction.currentIndex == 0
            else (value, 0.0, 90.0, name)
        )

    def plan(self) -> list:
        """[(glyph, master, layer, guide count, action)]; action is add / exists / auto layer."""
        self.check_binding()
        record = self.record()
        planned = []
        for glyph in self.glyphs:
            for master, layer in master_layers(glyph, self.chosen_masters()):
                existing = [guide_record(g) for g in glyph_guides(layer)]
                action = (
                    "auto layer, skipped"
                    if layer.autoLayer
                    else "exists"
                    if record in existing
                    else "add"
                )
                planned.append((glyph, master, layer, len(existing), action))
        self.pending_targets = {
            g.name for (g, m, layer, n, action) in planned if action == "add"
        }
        return planned

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Show all planned rows and current font-guide names before Apply."""
        if self.package is None:
            self.font_guides.setText("Open a font first.")
        else:
            names = font_guide_names(self.package)
            listed = ", ".join(names) if names else "none"
            self.font_guides.setText(f"Font guides in {self.current_master}: {listed}")
        count = len(self.glyphs)
        if self.package is not None and (not count):
            self.subtitle.setText(
                "Select glyphs in the Font window, then run this script again."
            )
        elif count:
            names = ", ".join(g.name for g in self.glyphs[:8]) + (
                " …" if count > 8 else ""
            )
            self.subtitle.setText(
                f"{count} glyph{('s' if count != 1 else '')}: {names}"
            )
        rows = [
            (f"{g.name} · {m}", str(n), action)
            for (g, m, layer, n, action) in (self.plan() if self.glyphs else [])
        ]
        self.fill_guide_rows(rows, {1}, 2)
        adds = sum(1 for cells in rows if cells[2] == "add")
        named = bool(self.guide_name.text.strip())
        self.apply_button.setEnabled(adds > 0 and named)
        self.status.setText(
            f"{adds} layer{('s' if adds != 1 else '')} to change"
            if named
            else "Name the guide to add it"
        )
        self.guard_apply(adds)

    @components_action
    def apply(self) -> None:
        """Recheck the complete source and write the original jobs as one Undo step."""
        record = self.record()
        jobs = [
            (g, layer, [record])
            for (g, m, layer, n, action) in self.plan()
            if action == "add"
        ]
        self.last_result = _api.add_guides(self.package, jobs, TITLE)
        self.refresh()
        self.status.setText(f"Added {self.last_result['guides']} glyph guides")

    def option_values(self) -> tuple:
        """Bind the exact record and master scope shown in the preview."""
        return (self.scope.currentIndex, self.record())


def main() -> Any:
    """Replace and show the complete owned modeless guide panel."""
    return show_script_dialog(FontGuidesPanel, KEY)


if __name__ == "__main__":
    main()
