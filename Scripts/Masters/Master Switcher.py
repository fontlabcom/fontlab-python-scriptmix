# this_file: Scripts/Masters/Master Switcher.py
# SPDX-License-Identifier: Apache-2.0
"""Choose the font's current master from a compact modeless palette.

Run the script with a font open. Click a master button; its axis location appears
below its name. The current master is checked and bold. Use the first nine button
shortcuts while the palette has focus. The controls change the package master,
using FontLab's native setMaster/UpdateAll behavior. Close releases owned signals.
Reopen the palette after changing the font's masters or their locations.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,  # noqa: F401 - Original public interface.
    master_switcher_api,
    master_switcher_dialog_type,
    masters_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = qt.QtCore, qt.QtGui
fontlab = ap.fontlab
_api = master_switcher_api()
master_order, location_label, switch = (
    _api.master_order,
    _api.location_label,
    _api.switch,
)
TITLE, KEY = "Master Switcher", "masters_switcher_palette"
BUTTON_COLUMNS = 3


class SampleDialog(master_switcher_dialog_type()):
    """Keep the original shell interface on the existing guarded Masters dialog."""

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent, TITLE, KEY)


class Switcher(SampleDialog):
    """Complete original master buttons, populated only after native binding."""

    ACTION = None

    def build(self) -> None:
        """Create the owned row/group before the first native source read."""
        self.setMinimumWidth(360)
        self.buttons = {}
        self.button_grid = QtGui.QGridLayout()
        self.button_grid.setHorizontalSpacing(8)
        self.button_grid.setVerticalSpacing(8)
        self.group = QtGui.QButtonGroup(self)
        self.group.setExclusive(True)
        self.root.addLayout(self.button_grid)

    def populate_buttons(self, values: tuple) -> None:
        """Retain original labels, sizes, shortcuts and exclusive checkable state."""
        for index, (master, where) in enumerate(values):
            if master in self.buttons:
                continue
            button = QtGui.QToolButton(self)
            button.setText(master + (f"\n{where}" if where else ""))
            button.setCheckable(True)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
            button.setMinimumSize(96, 52)
            button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
            if index < 9:
                button.setToolTip(
                    f"{master} (⌘{index + 1} while this palette is focused)"
                )
                button.setShortcut(QtGui.QKeySequence(f"Ctrl+{index + 1}"))
            self.group.addButton(button)
            self.buttons[master] = button
            self.button_grid.addWidget(
                button, index // BUTTON_COLUMNS, index % BUTTON_COLUMNS
            )
            self._connect(button.clicked, lambda *a, m=master: self.choose(m))

    def choose(self, master: str) -> None:
        """Check the bound source before making an explicit master current."""
        self.ensure_snapshot()
        switch(self.package, master)
        self.refresh()

    @masters_snapshot_refresh
    def refresh(self) -> None:
        """Publish original current-master emphasis from the bound font."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        current = self.package.master
        self.subtitle.setText(
            f"{len(self.masters)} masters · click to make one current"
        )
        for master, button in self.buttons.items():
            button.setChecked(master == current)
            font = button.font
            font.setBold(master == current)
            button.setFont(font)
        self.status.setText(f"Current master: {current}")


def main() -> Any:
    """Replace and show the owned palette through the shared script registry."""
    return show_script_dialog(Switcher, KEY)


if __name__ == "__main__":
    main()
