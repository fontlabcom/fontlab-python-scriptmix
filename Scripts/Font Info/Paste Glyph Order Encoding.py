# this_file: Scripts/Font Info/Paste Glyph Order Encoding.py
# SPDX-License-Identifier: Apache-2.0
"""Insert pasted names into the current font's order and save a FontLab encoding.

Select a glyph, run the tool, and paste space-separated glyph names. Preview
moves known names before the selected glyph, keeping pasted order and removing
repetitions. Unknown names are listed. The insertion position stays defined
even when the selected glyph is among the pasted names.

Save a new .enc file anywhere, then use File > Import > Encoding. Choose the
encoding in the Font window; use the encoding chooser's Refresh button as needed. This produces an
ordered Encoding view; it does not change the font's stored glyph indices.
FontLab's File > Export > Encoding saves a visible order; this tool adds
insertion by pasted names. Existing files are kept. No font edit or Undo step
is made. The preview shows up to 200 rows; the file contains every supported glyph.
Non-ASCII or unsafe glyph names get named kept rows and stay out of the file.
Why: Glyphs glyphOrder has no bound FontLab glyph-reorder API. An encoding
provides a persistent order that FontLab can import without changing glyph indices.
Benefit: Move a pasted sequence in one action and reuse its order in FontLab.

Independent behaviour rewrite after Alex Slobzheninov, Glyphs-Scripts,
Font Info/glyphOrder - Paste.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts .
No upstream code, private identifiers or comments are used.
"""

from pathlib import Path
from time import monotonic
from typing import Any


def insert_names(
    names: tuple[str, ...], text: str, before: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Move known tokens once; retain all other glyphs and report unknown tokens."""
    if not names or len(set(names)) != len(names) or before not in names:
        raise ValueError("Use a nonempty font order and an existing insertion glyph.")
    if any(character in text for character in "\x00\u00a0\u2028\u2029"):
        raise ValueError("Remove NUL, NBSP and Unicode line/paragraph separators.")
    tokens = tuple(dict.fromkeys(text.split()))
    known = set(names)
    moved = tuple(name for name in tokens if name in known)
    missing = tuple(name for name in tokens if name not in known)
    if not moved:
        raise ValueError("Paste at least one glyph name from the current font.")
    moving = set(moved)
    position = sum(name not in moving for name in names[: names.index(before)])
    remaining = tuple(name for name in names if name not in moving)
    return remaining[:position] + moved + remaining[position:], missing


def encoding_rows(names: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Keep unsupported names out of the encoding and report each by name."""
    if not names or len(set(names)) != len(names):
        raise ValueError("The encoding must contain unique glyph names.")
    kept = tuple(
        name
        for name in names
        if not name
        or len(name) > 500
        or name.startswith("%")
        or any(ord(c) < 33 or ord(c) > 126 or c in ",;" for c in name)
    )
    refused = set(kept)
    return tuple(name for name in names if name not in refused), kept


def save_encoding(path: Path, names: tuple[str, ...]) -> tuple[str, ...]:
    """Save supported rows in a new file; return every named kept row."""
    if path.suffix.lower() != ".enc":
        raise ValueError("Choose a new file with the .enc extension.")
    if any(c in path.stem for c in "\x00\r\n\u00a0\u2028\u2029"):
        raise ValueError(
            "Use an encoding file name without control or lossy characters."
        )
    supported, kept = encoding_rows(names)
    if not supported:
        raise ValueError("No supported encoding rows; kept: " + repr(kept))
    payload = f"%%FONTLAB ENCODING: -1; {path.stem}\n%%GROUP:Custom\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload + "\n".join(supported) + "\n")
    return kept


def capture_names() -> tuple[str, ...]:
    """Read current font order with a fresh budget, without requiring selection."""
    import fly.ap.glyph_catalog as catalog

    return tuple(row[0] for row in catalog.capture(deadline=monotonic() + 2.0).rows)


def capture_order() -> tuple[tuple[str, ...], str]:
    """Read font order and the first selected glyph without writing selection."""
    import fly.ap.layer_selection as selection

    names = capture_names()
    selected = selection.capture(deadline=monotonic() + 2.0).occurrences
    if not selected:
        raise ValueError("Select an insertion glyph before opening the tool.")
    before = selected[0].glyph_name
    if before not in names or names != capture_names():
        raise ValueError("Font order changed during capture; reopen the tool.")
    return names, before


def main() -> Any:
    """Open a modeless preview with guarded callbacks and owned signal cleanup."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly module alias
    from fly import qt

    gui = qt.QtGui
    key = "paste_glyph_order_encoding"

    class OrderPanel(gui.QDialog):
        """Keep a source-bound order preview until Save or Close."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            self._connections = []
            self.source_names: tuple[str, ...] = ()
            self.insertion_name = ""
            self.setWindowTitle("Paste Glyph Order Encoding")
            self.setMinimumWidth(620)
            column = gui.QVBoxLayout(self)
            hint = gui.QLabel(
                "Paste names to move before the selected glyph. Save a new .enc anywhere, "
                "then use File > Import > Encoding and the encoding chooser’s Refresh button. "
                "Stored glyph indices stay unchanged."
            )
            hint.setWordWrap(True)
            column.addWidget(hint)
            self.pasted_names = gui.QPlainTextEdit()
            self.pasted_names.setPlaceholderText("Space-separated glyph names")
            column.addWidget(self.pasted_names)
            self.order_preview = gui.QPlainTextEdit()
            self.order_preview.setReadOnly(True)
            column.addWidget(self.order_preview)
            self.status = gui.QLabel("")
            self.status.setWordWrap(True)
            column.addWidget(self.status)
            buttons = gui.QHBoxLayout()
            column.addLayout(buttons)
            for title, action in (
                ("Preview", self.preview_order),
                ("Save Encoding…", self.choose_file),
                ("Close", lambda: self.close()),
            ):
                button = gui.QPushButton(title)
                buttons.addWidget(button)
                scripting.connect_guarded(
                    self, button.clicked, lambda *a, fn=action: self.safe_action(fn)
                )
            self.file_chooser = None
            self.safe_action(self.read_source)

        def safe_action(self, action: Any) -> None:
            """Contain capture, conversion and file errors in the panel."""
            try:
                action()
            except (ValueError, RuntimeError, OSError) as error:
                self.status.setText(str(error))

        def read_source(self) -> None:
            """Capture the order before taking focus away from the source window."""
            self.source_names, self.insertion_name = capture_order()
            self.status.setText(f"Insert before {self.insertion_name}.")

        def preview_order(self) -> tuple[str, ...]:
            """Show a bounded preview while retaining the complete result for saving."""
            if not self.source_names:
                raise ValueError("Select a glyph and reopen this tool.")
            names, missing = insert_names(
                self.source_names, self.pasted_names.toPlainText(), self.insertion_name
            )
            supported, kept = encoding_rows(names)
            self.order_preview.setPlainText(
                "\n".join(
                    [
                        *supported[:200],
                        *(
                            f"kept {name!r}: unsupported encoding token"
                            for name in kept
                        ),
                    ]
                )
            )
            message = f"{len(names)} glyphs; first {min(200, len(names))} shown. " + (
                "Unknown names kept out: " + " ".join(missing)
                if missing
                else "All pasted names found."
            )
            if kept:
                message += f" Kept {len(kept)} names out of the file."
            self.status.setText(message)
            return names

        def choose_file(self) -> None:
            """Open an owned modeless chooser; Save never overwrites an existing file."""
            self.preview_order()
            if self.file_chooser is None:
                self.file_chooser = gui.QFileDialog(self)
                self.file_chooser.setAcceptMode(gui.QFileDialog.AcceptSave)
                self.file_chooser.setNameFilter("FontLab encoding (*.enc)")
                self.file_chooser.setDefaultSuffix("enc")
                scripting.connect_guarded(
                    self,
                    self.file_chooser.fileSelected,
                    lambda path: self.safe_action(lambda: self.write_file(str(path))),
                )
            self.file_chooser.show()

        def write_file(self, path: str) -> None:
            """Save the current form's complete order; do not touch the font."""
            if capture_names() != self.source_names:
                raise ValueError("Font order changed since preview; reopen the tool.")
            names = self.preview_order()
            kept = save_encoding(Path(path), names)
            self.status.setText(
                f"Saved {len(names) - len(kept)} glyphs to {Path(path).name}. "
                + " ".join(
                    f"kept {name!r}: unsupported encoding token" for name in kept
                )
            )

        def closeEvent(self, event: Any) -> None:
            """Disconnect signals before deleting the owned panel and chooser."""
            scripting.close_script_dialog(
                self,
                event,
                key,
                children=(() if self.file_chooser is None else (self.file_chooser,)),
            )

    return scripting.show_script_dialog(OrderPanel, key)


if __name__ == "__main__":
    main()
