# this_file: Scripts/Kerning/Missing Pairs.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Missing Pairs
"""List the combinations of two glyph groups that no kerning pair covers on a master.

What it does:
    Enter left and right glyphs: names separated by spaces, plain characters (“AVT”), or @class
    tokens that stand for all their members. Every left + right combination that neither a glyph
    pair nor a class pair reaches is listed, ready to proof or to kern. "Copy list" puts the
    missing pairs on the clipboard, one "left right" per line. Nothing is edited.

How it works:
    Expand character, glyph-name and class tokens into ordered unique sets.
    Test every left/right combination against explicit glyph and side-
    appropriate class coverage.

Why this design:
    An explicit zero pair still covers a combination; the report must not
    confuse zero adjustment with an absent kerning rule.

How to use:
    Run Kerning > Missing Pairs. Choose a master, enter left and right sets
    and inspect uncovered combinations. Use Copy list to prepare the shown
    pairs for proofing.

Benefit:
    Find uncovered pair combinations without adding kerning values or editing
    class membership.
"""

from typing import Any

from fly import ap, qt

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
# The tiny facade stays lazy until a native menu script asks for its panel.
from fly.ap.scripting import (
    kerning_class_lists as class_lists,
)
from fly.ap.scripting import (
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

TITLE = "Missing Kerning Pairs"
KEY = "kerning_missing_pairs"


# ---------------------------------------------------------------- core
def parse_glyphs(text: str, package: Any, members: dict[str, list[str]]) -> list[str]:
    """Glyph names from 'names', 'characters' and '@class' tokens, unique, in order."""
    out = []
    for token in text.split():
        if token.startswith("@") and token[1:] in members:
            names = members[token[1:]]
        elif package.findName(token) is not None:
            names = [token]
        else:
            names = [
                g.name
                for g in (package.findUnicode(ord(c)) for c in token)
                if g is not None
            ]
        out += [n for n in names if n not in out]
    return out


def covered(
    pairs: dict[tuple[str, str], float],
    left_classes: dict[str, list[str]],
    right_classes: dict[str, list[str]],
    left: str,
    right: str,
) -> bool:
    """Report explicit glyph/class coverage, including pairs stored with zero.

    Class indexes contain only classes allowed on their respective pair side.
    Any explicit combination of the glyph and its applicable classes covers it.
    """
    lefts = [left, *left_classes.get(left, [])]
    rights = [right, *right_classes.get(right, [])]
    return any((a, b) in pairs for a in lefts for b in rights)


def missing(
    package: Any, master: str, lefts: list[str], rights: list[str]
) -> list[tuple[str, str]]:
    """Return uncovered left/right Cartesian-product pairs in input order.

    Read the native FontLab package on the named master without switching it.
    A glyph pair or applicable class pair, even with a zero value, covers a pair.
    """
    pairs = kerning_pairs(package, master)
    left_classes, right_classes, _ = class_lists(package, master)
    return [
        (l, r)
        for l in lefts
        for r in rights
        if not covered(pairs, left_classes, right_classes, l, r)
    ]


# ---------------------------------------------------------------- GUI


class MissingPairs(KerningDialog):
    """Retain the original Missing Pairs controls on the shared owned panel."""

    def __init__(self, parent: Any = None) -> None:
        """Initialize owned controls without changing the font."""
        KerningDialog.__init__(self, parent, TITLE, KEY)

        self.lefts, self.rights, self.missing = [], [], []
        root = self.root

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.left_text = QtGui.QLineEdit("AFLPTVWY")
        self.left_text.setPlaceholderText("Left glyphs: names, characters or @class")
        self.right_text = QtGui.QLineEdit("aeosuy")
        self.right_text.setPlaceholderText("Right glyphs: names, characters or @class")
        self.master = QtGui.QComboBox()
        for name in self.masters:
            self.master.addItem(name)
        if self.current_master in self.masters:
            self.master.setCurrentIndex(self.masters.index(self.current_master))
        form.addWidget(QtGui.QLabel("Left"), 0, 0)
        form.addWidget(self.left_text, 0, 1)
        form.addWidget(QtGui.QLabel("Right"), 1, 0)
        form.addWidget(self.right_text, 1, 1)
        form.addWidget(QtGui.QLabel("Master"), 2, 0)
        form.addWidget(self.master, 2, 1)
        form.setColumnStretch(1, 1)
        root.addLayout(form)

        self.table = QtGui.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Left", "Right"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setMinimumHeight(220)
        root.addWidget(self.table, 1)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.copy_button = QtGui.QPushButton("Copy list")
        self.copy_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.copy_button)
        root.addLayout(footer)

        for line in (self.left_text, self.right_text):
            self._connect(line.textChanged, lambda *a: self.refresh())
        self._connect(self.master.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def chosen_master(self) -> str:
        """Return the master named by the original combo box."""
        return self.masters[self.master.currentIndex] if self.masters else ""

    @snapshot_refresh
    def refresh(self) -> None:
        """Read and render a complete native snapshot for the chosen controls."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        _, _, members = class_lists(self.package, self.chosen_master())
        self.lefts = parse_glyphs(self.left_text.text, self.package, members)
        self.rights = parse_glyphs(self.right_text.text, self.package, members)
        self.missing = missing(
            self.package,
            self.chosen_master(),
            self.lefts,
            self.rights,
        )
        combos = len(self.lefts) * len(self.rights)
        self.subtitle.setText(
            f"{len(self.lefts)} left × {len(self.rights)} right glyphs = {combos} combinations on "
            f"{self.chosen_master()}; listed are those no glyph or class pair covers.",
        )
        self.table.setRowCount(len(self.missing))
        for row, (left, right) in enumerate(self.missing):
            self.table.setItem(row, 0, QtGui.QTableWidgetItem(left))
            self.table.setItem(row, 1, QtGui.QTableWidgetItem(right))
        share = f" ({100 * len(self.missing) // combos} %)" if combos else ""
        self.status.setText(
            f"{len(self.missing)} of {combos} combinations unkerned{share}",
        )
        self.copy_button.setEnabled(bool(self.missing))

    def copy(self) -> str:
        """Copy the complete missing-pair list after checking the font binding."""
        self.ensure_snapshot()
        text = "\n".join(f"{l} {r}" for l, r in self.missing)
        QtGui.QApplication.clipboard().setText(text)
        self.status.setText(f"Copied {len(self.missing)} pairs to the clipboard")
        return text


def main() -> Any:
    """Replace the original registry window and show this owned modeless panel."""
    return ap.scripting.show_script_dialog(MissingPairs, KEY)


if __name__ == "__main__":
    main()
