# this_file: Scripts/Kerning/Classes Browser.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Classes Browser
"""Browse kerning classes: their side, members, and every pair that uses them on each master.

What it does:
    The list on the left shows each class with its side (left = first glyph of a pair, right =
    second) and size; filter it by class or member name. Pick a class to see its members and the
    pairs that use it with one value column per master. "Select members" selects the class's glyphs
    in the Font window. Nothing is edited.

How it works:
    Read side-specific kerning classes and their members, then collect
    explicit pairs using the selected class across masters. Filter class names
    or exact member names.

Why this design:
    Class membership and pair use are different questions; showing both avoids
    mistaking an unused class for an active kerning rule.

How to use:
    Run Kerning > Classes Browser. Enter a filter, choose a class and inspect
    its members and pair values. Use Select members to locate its glyphs in
    the Font window.

Benefit:
    Trace kerning-class use without changing membership or pair data.
"""

from typing import Any

from fly import ap, qt

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
# The tiny facade stays lazy until a native menu script asks for its panel.
from fly.ap.scripting import (
    kerning_classes,
    kerning_dialog_type,
    kerning_pairs,
)
from fly.ap.scripting import (
    kerning_snapshot_refresh as snapshot_refresh,
)
from fly.ap.scripting import (
    names_muted as muted,
)

KerningDialog = kerning_dialog_type()

TITLE = "Kerning Classes"
KEY = "kerning_classes_browser"
SIDES = {"KernLeft": "left", "KernRight": "right", "KernBothSide": "both"}


# ---------------------------------------------------------------- core
def pairs_using(package: Any, masters: list[str], name: str) -> dict:
    """{(left, right): {master: value}} for pairs with @name on either side."""
    tag, rows = "@" + name, {}
    for master in masters:
        for (left, right), value in kerning_pairs(package, master).items():
            if tag in {left, right}:
                rows.setdefault((left, right), {})[master] = value
    return rows


def matches(name: str, members: list[str], text: str) -> bool:
    """Class name contains the text (any case), or a member is exactly the text (glyph names are case-sensitive)."""
    text = text.strip()
    return not text or text.lower() in name.lower() or text in members


# ---------------------------------------------------------------- GUI


class ClassesBrowser(KerningDialog):
    """Retain the original Classes Browser controls on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize owned controls without changing the font."""
        KerningDialog.__init__(self, parent, TITLE, KEY)

        self.classes = (
            kerning_classes(self.package, self.current_master) if self.package else {}
        )
        self.names, self.selected = [], None
        root = self.root

        self.filter = QtGui.QLineEdit()
        self.filter.setPlaceholderText("Filter by class name or member glyph")
        self.filter.setClearButtonEnabled(True)
        root.addWidget(self.filter)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.list = QtGui.QListWidget()
        self.list.setAlternatingRowColors(True)
        self.list.setMinimumWidth(220)
        self.splitter.addWidget(self.list)

        detail = QtGui.QWidget()
        side = QtGui.QVBoxLayout(detail)
        side.setContentsMargins(12, 0, 0, 0)
        side.setSpacing(8)
        self.title = QtGui.QLabel()
        title_font = self.title.font
        title_font.setBold(True)
        title_font.setPointSizeF(title_font.pointSizeF() * 1.15)
        self.title.setFont(title_font)
        side.addWidget(self.title)
        self.members = QtGui.QLabel()
        self.members.setWordWrap(True)
        self.members.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        side.addWidget(self.members)
        self.pairs = QtGui.QTableWidget(0, len(self.masters) + 1)
        self.pairs.setHorizontalHeaderLabels(["Pair", *self.masters])
        self.pairs.verticalHeader().setVisible(False)
        self.pairs.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.pairs.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.pairs.setAlternatingRowColors(True)
        self.pairs.setShowGrid(False)
        header = self.pairs.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.pairs.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        side.addWidget(self.pairs, 1)
        self.splitter.addWidget(detail)
        self.splitter.setStretchFactor(1, 1)
        root.addWidget(self.splitter, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.select_button = QtGui.QPushButton("Select members")
        self.select_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.select_button)
        root.addLayout(footer)

        self._connect(self.filter.textChanged, lambda *a: self.fill())
        self._connect(self.list.currentRowChanged, self.show_class)
        self._connect(self.select_button.clicked, lambda *a: self.select_members())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.fill()

    @snapshot_refresh
    def fill(self) -> None:
        """Render the complete filtered rows from the current snapshot."""
        text = self.filter.text
        self.names = sorted(
            n for n, (members, _) in self.classes.items() if matches(n, members, text)
        )
        if self.package is None:
            self.subtitle.setText("Open a font first.")
        else:
            counts = {
                s: sum(1 for _, side in self.classes.values() if side == s)
                for s in ("left", "right", "both")
            }
            self.subtitle.setText(
                f"{len(self.classes)} classes: {counts['left']} left, {counts['right']} right, "
                f"{counts['both']} both sides. Values are shown for all {len(self.masters)} masters.",
            )
        self.list.clear()
        for name in self.names:
            members, side = self.classes[name]
            self.list.addItem(f"@{name}   {side} · {len(members)}")
        self.status.setText(f"{len(self.names)} of {len(self.classes)} classes")
        if self.names:
            self.list.setCurrentRow(0)
        else:
            self.show_class(-1)

    @snapshot_refresh
    def show_class(self, row: int) -> None:
        """Show the selected class members and every master pair value."""
        if row < 0 or row >= len(self.names):
            self.selected = None
            self.title.setText("No class")
            self.members.setText("")
            self.pairs.setRowCount(0)
            self.select_button.setEnabled(False)
            return
        name = self.names[row]
        members, side = self.classes[name]
        self.selected = name
        self.title.setText(f"@{name} · {side} side")
        self.members.setText(" ".join(members))
        rows = pairs_using(self.package, self.masters, name)
        QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
        self.pairs.setRowCount(len(rows))
        for r, pair in enumerate(sorted(rows)):
            label = QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}")
            self.pairs.setItem(r, 0, label)
            for column, master in enumerate(self.masters, 1):
                value = rows[pair].get(master)
                item = QtGui.QTableWidgetItem("–" if value is None else f"{value:g}")
                item.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                )
                if value is None:
                    item.setForeground(QtGui.QBrush(QtGui.QColor(muted(self))))
                self.pairs.setItem(r, column, item)
        self.select_button.setEnabled(True)
        self.status.setText(
            f"@{name}: {len(members)} members, used in {len(rows)} pairs",
        )
        self.pair_rows = {f"{l} {r}": v for (l, r), v in rows.items()}

    def select_class(self, name: str) -> None:
        """Show a class by name (used by tests and handy from the console)."""
        self.list.setCurrentRow(self.names.index(name))

    def select_members(self) -> None:
        """Select validated class members only in the scanned current font."""
        self.ensure_snapshot()
        if self.selected is None:
            return
        members = self.classes[self.selected][0]
        self.select_names(members)
        self.status.setText(
            f"Selected {len(members)} glyphs of @{self.selected} in the Font window",
        )


def main() -> Any:
    """Replace the original registry window and show this owned modeless panel."""
    return ap.scripting.show_script_dialog(ClassesBrowser, KEY)


if __name__ == "__main__":
    main()
