# this_file: Scripts/Proof/Word Finder.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Proof · Word Finder
"""Find real words to proof with: words the font can set, that use the letters you are working on.

Searches a small embedded English and Latin word list. Keep only words
whose every letter has a glyph, require some letters (e.g. the new 'k'),
or restrict to a set of letters (e.g. what is drawn so far). Copy the
result as proof text. Nothing in the font changes."""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    names_muted as muted,  # noqa: F401 - original public interface
)
from fly.ap.scripting import (
    proof_api,
    proof_dialog_type,
    proof_snapshot_refresh,
    show_script_dialog,
)

QtCore, QtGui = (qt.QtCore, qt.QtGui)
fontlab = ap.fontlab
_api = proof_api()
font_chars = _api.font_chars
cased = _api.cased
find_words = _api.find_words
ENGLISH = _api.ENGLISH
LATIN = _api.LATIN
WORDS = _api.WORDS
CASES = _api.CASES
TITLE = "Word Finder"
KEY = "proof_word_finder"


class WordFinder(proof_dialog_type()):
    """Retain the original Proof controls on the shared owned dialog."""

    def __init__(self, parent: Any = None) -> None:
        """Build the original controls and retain only owned native UI resources."""
        super().__init__(parent, TITLE, KEY)
        self.setMinimumWidth(560)
        self.resize(600, 520)
        self.available = set()
        self.words = []
        root = self.root
        form = QtGui.QGridLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        self.must = QtGui.QLineEdit()
        self.must.setPlaceholderText("e.g. kz")
        self.only = QtGui.QLineEdit()
        self.only.setPlaceholderText("e.g. hamburgefonstiv (empty = any)")
        self.case = QtGui.QComboBox()
        for label in CASES:
            self.case.addItem(label)
        self.min_len = QtGui.QSpinBox()
        self.min_len.setRange(1, 20)
        self.min_len.setValue(3)
        self.max_len = QtGui.QSpinBox()
        self.max_len.setRange(1, 20)
        self.max_len.setValue(12)
        lengths = QtGui.QHBoxLayout()
        lengths.addWidget(self.min_len)
        lengths.addWidget(QtGui.QLabel("to"))
        lengths.addWidget(self.max_len)
        lengths.addStretch(1)
        form.addWidget(QtGui.QLabel("Must contain"), 0, 0)
        form.addWidget(self.must, 0, 1)
        form.addWidget(QtGui.QLabel("Case"), 0, 2)
        form.addWidget(self.case, 0, 3)
        form.addWidget(QtGui.QLabel("Only letters"), 1, 0)
        form.addWidget(self.only, 1, 1)
        form.addWidget(QtGui.QLabel("Length"), 1, 2)
        form.addLayout(lengths, 1, 3)
        form.setColumnStretch(1, 1)
        root.addLayout(form)
        self.result_view = QtGui.QPlainTextEdit()
        self.result_view.setReadOnly(True)
        bigger = self.result_view.font
        bigger.setPointSizeF(bigger.pointSizeF() * 1.2)
        self.result_view.setFont(bigger)
        root.addWidget(self.result_view, 1)
        self.add_proof_footer(copy_words=True)
        for line in (self.must, self.only):
            self._connect(line.textChanged, lambda *a: self.refresh())
        for spin in (self.min_len, self.max_len):
            self._connect(spin.valueChanged, lambda *a: self.refresh())
        self._connect(self.case.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.copy_button.clicked, lambda *a: self.copy())
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.initial_refresh()

    def load_initial(self) -> None:
        """Read encoded characters only after the empty results and Close exist."""
        self.available = font_chars()

    @proof_snapshot_refresh
    def refresh(self) -> None:
        """Read a complete bound-font proof for the original controls."""
        case = CASES[self.case.currentIndex]
        self.words = find_words(
            WORDS,
            self.available,
            case,
            self.must.text.strip(),
            self.only.text.strip(),
            self.min_len.value,
            self.max_len.value,
        )
        if not self.available:
            self.subtitle.setText("Open a font with encoded glyphs first.")
        else:
            self.subtitle.setText(
                f"{len(WORDS)} English and Latin words; showing those the font can set with its {len(self.available)} characters."
            )
        self.result_view.setPlainText(" ".join(self.words))
        self.copy_button.setEnabled(bool(self.words))
        self.status.setText(
            f"{len(self.words)} word{('s' if len(self.words) != 1 else '')}"
        )

    def copy(self) -> None:
        """Copy exactly the filtered words after checking the bound font snapshot."""
        self.ensure_snapshot()
        QtGui.QApplication.clipboard().setText(" ".join(self.words))
        self.status.setText(f"Copied {len(self.words)} words")


def main() -> Any:
    """Replace the original registry entry with this owned modeless Proof tool."""
    return show_script_dialog(WordFinder, KEY)


if __name__ == "__main__":
    main()
