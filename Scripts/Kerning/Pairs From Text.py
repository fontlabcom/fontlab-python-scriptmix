# this_file: Scripts/Kerning/Pairs From Text.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Pairs From Text
"""Type a word, see each adjacent pair's kerning on every master, and set the ones you tick.

What it does:
    Pairs are taken inside words (spaces separate words; /glyphname tokens work too). The table
    shows what FontLab applies now on each master, marking values that come from a class pair.
    Set or Add writes explicit glyph pairs for the ticked rows on the chosen masters; one Apply is
    one Undo step.

How it works:
    Parse adjacent glyph pairs inside words, resolve effective kerning on each
    master and stage Set or Add values only for checked rows.

Why this design:
    An effective class-pair value supplies the displayed baseline, while the
    requested write creates an explicit glyph pair.

How to use:
    Run Kerning > Pairs From Text. Enter text or slash-name tokens, tick
    pairs, choose masters and Set or Add, inspect the values and press Apply.

Benefit:
    Kern a specific proof-text batch; Apply is recorded as one Undo step.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import kerning_edit_dialog_type, kerning_selection_api
from fly.ap.scripting import kerning_editor_apply as editor_apply
from fly.ap.scripting import kerning_editor_make_table as make_table
from fly.ap.scripting import kerning_editor_refresh as editor_refresh
from fly.ap.scripting import names_muted as muted

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui
api = kerning_selection_api()
KerningEditDialog = kerning_edit_dialog_type()
current_package = ap.scripting.current_package
kerning_pairs = ap.scripting.kerning_pairs

TITLE = "Kerning Pairs from Text"
KEY = "kerning_pairs_from_text"
MODES = [("Set to", "set"), ("Add to current", "add")]


explicit_pairs = api.explicit_pairs
parse_words = api.parse_words
adjacent_pairs = api.adjacent_pairs
current_value = api.current_value


def write_kerning(
    package: Any, edits: dict[str, dict[tuple[str, str], int | None]]
) -> None:
    """Retain the original console interface through the shared preflight writer."""
    ap.scripting.kerning_editor_api().write_kerning(package, edits, TITLE)


class PairsFromText(KerningEditDialog):
    """Preserve all original controls on the shared snapshot-bound native panel."""

    def __init__(self, parent: Any = None) -> None:
        """Create original controls; connect every callback through owned guards."""
        KerningEditDialog.__init__(self, parent, TITLE, KEY)
        self.setMinimumWidth(600)
        self.resize(640, 560)
        self.pairs = []
        self.values = {}
        self.filling = False
        root = self.root

        self.text = QtGui.QLineEdit("AVATAR Type")
        self.text.setPlaceholderText("Words to kern, e.g. AVATAR Type /Aacute/V")
        root.addWidget(self.text)

        self.table = make_table(["Pair", *self.masters])
        root.addWidget(self.table, 1)

        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.mode = QtGui.QComboBox()
        for label, _ in MODES:
            self.mode.addItem(label)
        self.value = QtGui.QSpinBox()
        self.value.setRange(-2000, 2000)
        self.value.setAlignment(QtCore.Qt.AlignRight)
        self.value.setSuffix(" units")
        self.scope = QtGui.QComboBox()
        self.scope.addItem(f"Current master ({self.current_master})")
        self.scope.addItem(f"All masters ({len(self.masters)})")
        form.addWidget(QtGui.QLabel("Ticked pairs"), 0, 0)
        form.addWidget(self.mode, 0, 1)
        form.addWidget(self.value, 0, 2)
        form.addWidget(QtGui.QLabel("Masters"), 1, 0)
        form.addWidget(self.scope, 1, 1, 1, 2)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(2, 1)
        root.addLayout(form)

        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.close_button = QtGui.QPushButton("Close")
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.setDefault(True)
        footer.addWidget(self.close_button)
        footer.addWidget(self.apply_button)
        root.addLayout(footer)

        self.add_refresh(footer, self.refresh)
        self._connect(self.text.textChanged, lambda *a: self.refresh())
        self._connect(self.table.itemChanged, lambda *a: self.count())
        self._connect(self.mode.currentIndexChanged, lambda *a: self.count())
        self._connect(self.value.valueChanged, lambda *a: self.count())
        self._connect(self.scope.currentIndexChanged, lambda *a: self.count())
        self._connect(self.apply_button.clicked, lambda *a: self.apply())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def chosen_masters(self) -> list[str]:
        """Return current or all originally captured masters, retaining scope semantics."""
        return [self.current_master] if self.scope.currentIndex == 0 else self.masters

    @editor_refresh
    def refresh(self, keep_ticks: list[tuple[str, str]] | None = None) -> None:
        """Publish the complete effective/explicit preview and original default ticks."""
        if self.package is None:
            self.subtitle.setText("Open a font first.")
            return
        self.pairs = adjacent_pairs(parse_words(self.text.text, self.package))
        self.values = api.text_values(self.package, self.masters, self.pairs)
        self.subtitle.setText(
            f"{len(self.pairs)} pairs from the text. Values are what each master applies now; "
            "“class” marks values inherited from a class pair.",
        )
        dim = QtGui.QColor(muted(self))
        self.filling = True
        self.table.setRowCount(len(self.pairs))
        for row, pair in enumerate(self.pairs):
            name = QtGui.QTableWidgetItem(f"{pair[0]}  {pair[1]}")
            ticked = keep_ticks is None or pair in keep_ticks
            name.setCheckState(QtCore.Qt.Checked if ticked else QtCore.Qt.Unchecked)
            self.table.setItem(row, 0, name)
            for column, master in enumerate(self.masters, 1):
                value, own = self.values[pair, master]
                item = QtGui.QTableWidgetItem(
                    f"{value:g}" if own else (f"{value:g}  class" if value else "–"),
                )
                item.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter),
                )
                if not own:
                    item.setForeground(QtGui.QBrush(dim))
                self.table.setItem(row, column, item)
        self.filling = False
        self.count()

    def ticked(self) -> list[tuple[str, str]]:
        """Read actual table check states; never substitute stored tick intentions."""
        return [
            self.pairs[r]
            for r in range(self.table.rowCount)
            if self.table.item(r, 0).checkState() == QtCore.Qt.Checked
        ]

    def tick(self, pairs: list[tuple[str, str]]) -> None:
        """Tick exactly these pairs (used by tests and handy from the console)."""
        self.filling = True
        for row, pair in enumerate(self.pairs):
            self.table.item(row, 0).setCheckState(
                QtCore.Qt.Checked if pair in pairs else QtCore.Qt.Unchecked,
            )
        self.filling = False
        self.count()

    def plan(self) -> dict[str, dict[tuple[str, str], int]]:
        """Stage only ticked pairs using the displayed effective baseline for Add."""
        return api.text_plan(
            self.chosen_masters(),
            self.ticked(),
            self.values,
            MODES[self.mode.currentIndex][1],
            self.value.value,
        )

    def count(self) -> None:
        """Update original tick counts and enable Apply only for selected rows."""
        if self.filling:
            return
        edits = self.plan()
        cells = sum(len(p) for p in edits.values())
        self.status.setText(
            f"{len(self.ticked())} of {len(self.pairs)} pairs ticked · {cells} values to write",
        )
        self.apply_button.setEnabled(bool(cells))

    @editor_apply
    def apply(self) -> None:
        """Preflight the complete ticked batch, write once, then refresh its baseline."""
        edits = self.plan()
        self.write_edits(edits, TITLE)
        self.last_result = {m: len(p) for m, p in edits.items()}
        fontlab.UpdateAll()
        keep_ticks = self.ticked()
        self.refresh_after_apply(lambda: self.refresh(keep_ticks=keep_ticks))
        self.status.setText(f"Wrote {sum(self.last_result.values())} pair values")


def main() -> Any:
    """Replace only this tool's registry entry and show its owned modeless dialog."""
    return ap.scripting.show_script_dialog(PairsFromText, KEY)


if __name__ == "__main__":
    main()
