# this_file: Scripts/Masters/Master Text Comparison.py
# SPDX-License-Identifier: Apache-2.0
"""Open comparison tabs whose glyph slots name exact master layers.

What: Resolve comma-separated words and repeat each word on every master.
How: Use proof.font_maps for first-encoded-name-wins Unicode lookup, check all
requested layers, then call public named_tab.open_layer_rows once.
The shared tab helper saves and restores shape activation flags.
Use: Enter words or /glyphname tokens and press Open comparison. Side by side
puts each word group on one row, with a space between master copies.
Stacked puts each word/master on one row, with blank group separators.
Keep the non-modal panel open for repeated proofs. Enter an absolute UTF-8
preset-file path and press Load presets; each nonempty line is one preset.
The path stays in the panel until it closes. BOM and line endings are normalized;
NUL, NBSP and Unicode line/paragraph separators are refused.
Why: Over FontLab's Glyph-window multi-master text views and Text By Master,
this adds comma-separated word groups and file presets with exact per-slot layers.
Benefit: Prepare repeatable master comparisons from one short word list.

Credit: Luke Prowse (LukeProwse), NaN-xyz/GlyphsApp-Scripts,
MasterBlaster/MasterBlaster.py, MIT (root LICENSE), copyright 2019 LukeProwse.
The repository README also declares Apache-2.0.
https://github.com/NaN-xyz/GlyphsApp-Scripts
Independent rewrite of behaviour. No source code or preset text was copied.
"""

from pathlib import Path
from time import monotonic
from typing import Any

TITLE, KEY = "Master Text Comparison", "masters_text_comparison"
Rows = tuple[tuple[tuple[str | None, str], ...], ...]


def check_text(text: str) -> None:
    """Refuse characters that native Qt text conversion can change."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Remove NUL, NBSP and Unicode line/paragraph separators.")


def read_presets(path: str) -> tuple[str, ...]:
    """Read complete UTF-8 lines; normalize BOM and platform line endings."""
    target = Path(path).expanduser()
    if not target.is_absolute():
        raise ValueError("Enter an absolute preset-file path.")
    with target.open(encoding="utf-8-sig", newline=None) as source:
        text = source.read()
    check_text(text)
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines:
        raise ValueError("The preset file contains no text.")
    return lines


def comparison_rows(
    text: str,
    cmap: dict[int, str],
    names: set[str],
    masters: tuple[str, ...],
    stacked: bool,
) -> Rows:
    """Resolve words first, then repeat each word in the font's master order."""
    import fly.ap.proof as proof  # noqa: PLR0402

    check_text(text)
    if not masters or any(not m for m in masters) or len(set(masters)) != len(masters):
        raise ValueError("The font needs distinct, nonempty master names.")
    words = [word.strip() for word in text.split(",") if word.strip()]
    if not words:
        raise ValueError("Enter at least one word or /glyphname token.")
    rows = []
    for word in words:
        run = proof.parse_text(word, cmap, names)
        if not run or None in run:
            raise ValueError(
                f"Missing glyph in '{word}'. Use /glyphname for unencoded glyphs."
            )
        copies = [tuple((name, master) for name in run) for master in masters]
        if stacked:
            if rows:
                rows.append(())
            rows.extend(copies)
        else:
            rows.append(
                tuple(
                    item
                    for i, copy in enumerate(copies)
                    for item in (((None, ""),) if i else ()) + copy
                )
            )
    return tuple(rows)


def open_comparison(text: str, stacked: bool, package_id: int) -> int:
    """Preflight all rows, then open one exact-layer comparison tab."""
    import fly.ap.named_tab as named_tab  # noqa: PLR0402
    import fly.ap.proof as proof  # noqa: PLR0402
    import fly.ap.scripting as scripting  # noqa: PLR0402

    deadline = monotonic() + 2.0
    package = scripting.current_package(package_id)
    if package is None:
        raise ValueError("The source font changed or closed; reopen this panel.")
    master = str(package.master)
    masters = tuple(str(name) for name in package.masters)
    cmap, names = proof.font_maps()
    rows = comparison_rows(text, cmap, names, masters, stacked)
    checked = set()
    for row in rows:
        for name, layer_name in row:
            if name is None:
                continue
            if monotonic() >= deadline:
                raise TimeoutError("Comparison preflight expired; no tab opened.")
            check_text(name)
            check_text(layer_name)
            if (name, layer_name) in checked:
                continue
            glyph = package.findName(name)
            layer = (
                None if glyph is None or glyph.isNull else glyph.findLayer(layer_name)
            )
            if layer is None or layer.isNull:
                raise ValueError(f"Missing layer '{layer_name}' in '{name}'.")
            checked.add((name, layer_name))
    if tuple(str(name) for name in package.masters) != masters:
        raise ValueError("The font's master list changed; run again.")
    named_tab.open_layer_rows(
        rows, expected_id=package_id, master=master, deadline=deadline
    )
    return 1


def panel_type() -> type:
    """Build a PythonQt panel lazily; reuse shared signal and close handling."""
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    gui = qt.QtGui

    class ComparisonPanel(gui.QDialog):
        """Keep repeated proof controls bound to the opening font."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            self._connections: list = []
            package = scripting.current_package()
            if package is None:
                raise ValueError("Open a font first.")
            self.package_id = int(package.id)
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(460)
            root = gui.QVBoxLayout(self)
            root.addWidget(
                gui.QLabel(
                    "Words, separated by commas · /glyphname for unencoded glyphs"
                )
            )
            self.words_edit = gui.QLineEdit("Hamburgefonts,0123456789")
            root.addWidget(self.words_edit)
            self.arrangement = gui.QComboBox()
            self.arrangement.addItems(
                ["Side by side · one row per word", "Stacked · one row per word/master"]
            )
            root.addWidget(self.arrangement)
            self.path_edit = gui.QLineEdit()
            self.path_edit.setPlaceholderText(
                "UTF-8 presets, e.g. /Users/Shared/proof-words.txt"
            )
            root.addWidget(self.path_edit)
            self.preset_box = gui.QComboBox()
            root.addWidget(self.preset_box)
            self.status = gui.QLabel(
                "One comparison tab; duplicate Unicode uses the first glyph."
            )
            self.status.setWordWrap(True)
            root.addWidget(self.status)
            buttons = gui.QHBoxLayout()
            root.addLayout(buttons)
            for label, callback in (
                ("Load presets", self.load_presets),
                ("Open comparison", self.open_proof),
                ("Close", lambda: self.close()),
            ):
                button = gui.QPushButton(label)
                buttons.addWidget(button)
                scripting.connect_guarded(
                    self, button.clicked, lambda *args, action=callback: action()
                )
            scripting.connect_guarded(
                self,
                self.preset_box.currentIndexChanged,
                lambda *args: self.choose_preset(),
            )

        def load_presets(self) -> None:
            """Populate once per file load; report normalization explicitly."""
            try:
                lines = read_presets(str(self.path_edit.text))
                self.preset_box.clear()
                self.preset_box.addItems(list(lines))
                self.status.setText(
                    f"{len(lines)} presets loaded; UTF-8 BOM and line endings normalized."
                )
            except (OSError, ValueError, UnicodeError) as error:
                self.status.setText(str(error))

        def choose_preset(self) -> None:
            """Copy the selected complete preset into the editable field."""
            text = str(self.preset_box.currentText)
            if text:
                self.words_edit.setText(text)

        def open_proof(self) -> None:
            """Keep refusal and timeout messages inside the owned panel."""
            try:
                count = open_comparison(
                    str(self.words_edit.text),
                    self.arrangement.currentIndex == 1,
                    self.package_id,
                )
                self.status.setText(
                    f"Opened {count} comparison tabs; duplicate Unicode uses the first glyph."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def closeEvent(self, event: Any) -> None:
            """Disconnect all owned callbacks before deferred deletion."""
            scripting.close_script_dialog(self, event, KEY)

    return ComparisonPanel


def main() -> Any:
    """Show one owned non-modal panel, or explain why no font can be bound."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        if scripting.current_package() is None:
            raise ValueError("Open a font first.")
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
