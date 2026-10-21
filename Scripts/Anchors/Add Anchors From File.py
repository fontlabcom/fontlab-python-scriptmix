# this_file: Scripts/Anchors/Add Anchors From File.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Add Anchors From File
"""Import named anchor coordinates from a UTF-8 CSV file.

What: Add or move named anchors on the current master for every CSV glyph row.
How: Use name or glyph plus paired anchor_x,anchor_y columns. Strip header
whitespace; refuse unknown columns, missing glyphs and malformed rows. Two
empty coordinate cells leave that anchor unchanged. Coordinates round half up
to font units before preview and writing. Report BOM and newline conversions
only when they occur. Existing pins keep their appearance and expressions.
Why: A checked table avoids repeated manual entry and preference-dependent
fractional writes. Automatic layers are kept; unsafe writes are refused.
Use: Browse for a CSV, click Load, inspect the non-modal preview, then Import.
Benefit: Apply a complete coordinate table consistently. Each application
is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

import csv
import io
import math
from pathlib import Path
from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
from fly import qt

TITLE = "Add Anchors From File"
KEY = "anchors_add_anchors_from_file"


def parse_table(text: str) -> dict[str, dict[str, tuple[float, float]]]:
    """Parse the entire CSV before planning any writes. Reject ambiguous input."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("CSV contains text that FontLab cannot preserve.")
    reader = csv.DictReader(io.StringIO(text))
    fields = [field.strip() for field in (reader.fieldnames or [])]
    reader.fieldnames = fields
    unknown = [
        field
        for field in fields
        if field not in ("name", "glyph")
        and not (field.endswith(("_x", "_y")) and len(field) > 2)
    ]
    if unknown:
        raise ValueError("Unknown CSV columns: " + ", ".join(unknown))
    if len(fields) != len(set(fields)):
        raise ValueError("CSV column names must be unique.")
    identity = "name" if "name" in fields else "glyph"
    if identity not in fields:
        raise ValueError("CSV needs a name or glyph column.")
    labels = [field[:-2] for field in fields if field.endswith("_x")]
    if not labels or any(not name or name + "_y" not in fields for name in labels):
        raise ValueError("Pair every anchor _x column with an _y column.")
    if any(field.endswith("_y") and field[:-2] not in labels for field in fields):
        raise ValueError("An anchor _y column has no _x column.")
    table: dict[str, dict[str, tuple[float, float]]] = {}
    for row in reader:
        name = (row.get(identity) or "").strip()
        if (
            not name
            or name in table
            or None in row
            or any(v is None for v in row.values())
        ):
            raise ValueError("CSV has an empty/repeated glyph name or a ragged row.")
        table[name] = {}
        for label in labels:
            cells = (row[label + "_x"].strip(), row[label + "_y"].strip())
            if cells == ("", ""):
                continue
            try:
                point = tuple(float(value) for value in cells)
            except ValueError as error:
                raise ValueError(
                    f"{name}/{label}: enter both numeric coordinates."
                ) from error
            if not all(math.isfinite(value) for value in point):
                raise ValueError(f"{name}/{label}: coordinates must be finite.")
            table[name][label] = tuple(anchor_writer.half_up(value) for value in point)
    if not table:
        raise ValueError("CSV has no glyph rows.")
    return table


def load_table(path: str) -> tuple[dict, str]:
    """Decode UTF-8 once, normalize newlines, and report only actual conversions."""
    if not path:
        raise ValueError("Choose an anchor CSV file.")
    try:
        raw = Path(path).read_bytes()
        with io.TextIOWrapper(
            io.BytesIO(raw), encoding="utf-8-sig", newline=None
        ) as stream:
            records = parse_table(stream.read())
        conversions = ["BOM removed"] if raw.startswith(b"\xef\xbb\xbf") else []
        if b"\r" in raw:
            conversions.append("CR/CRLF read as LF")
        return records, "; ".join(
            ["Coordinates round half up to font units", *conversions]
        ) + "."
    except (OSError, UnicodeError, csv.Error) as error:
        raise ValueError(f"Cannot read CSV: {error}") from error


def file_table(path: str) -> dict[str, dict[str, tuple[int, int]]]:
    """Read the rounded table for callers that do not need its conversion report."""
    return load_table(path)[0]


def import_changes(
    layer: Any, values: dict[str, tuple[float, float]]
) -> list[anchor_writer.Change]:
    """Keep equal points untouched; refuse repeated target names through the writer."""
    current = anchor_writer.anchor_points(layer)
    return [
        anchor_writer.Change(
            name, str(current.get(name, "missing")), str(point), ("set", name, point)
        )
        for name, point in values.items()
        if current.get(name) != point
    ]


class AnchorFileImport(anchor_panel.panel_type()):
    """A path field, explicit Load button, preview, and current-master Import."""

    TITLE, KEY, ACTION = TITLE, KEY, "Import"

    def refresh(self) -> None:
        """Contain scan errors inside the panel and disable its write action."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.apply_button.setEnabled(False)
            self.status.setText(str(error))

    def build_controls(self) -> None:
        self.csv_path = qt.QtGui.QLineEdit("")
        self.load_button = qt.QtGui.QPushButton("Load")
        self.browse_button = qt.QtGui.QPushButton("Browse…")
        self.form.addWidget(qt.QtGui.QLabel("UTF-8 CSV path"), 0, 0)
        self.form.addWidget(self.csv_path, 0, 1)
        self.form.addWidget(self.browse_button, 0, 2)
        self.form.addWidget(self.load_button, 0, 3)
        self.watch(self.browse_button.clicked, self.choose_csv)
        self.watch(self.load_button.clicked, self.reload)
        self.watch(self.csv_path.returnPressed, self.reload)
        self.csv_info = qt.QtGui.QLabel("Coordinates round half up to font units.")
        self.form.addWidget(self.csv_info, 1, 0, 1, 4)

    def choose_csv(self) -> None:
        """Choose a CSV through one owned dialog, then load its complete preview."""
        import fly.ap.qt_dialogs as qt_dialogs  # noqa: PLR0402 - Fly submodule import

        def configure(kind: Any, dialog: Any) -> None:
            dialog.setFileMode(kind.ExistingFile)
            dialog.setNameFilter("Anchor table (*.csv)")

        paths = qt_dialogs.run_file_dialog(
            qt.QtGui, configure, "Open Anchor CSV", "", (self,)
        )
        if paths:
            self.csv_path.setText(paths[0])
            self.reload()

    def glyph_names(self) -> list[str]:
        if not hasattr(self, "csv_path") or not self.csv_path.text.strip():
            return []
        self.records, report = load_table(self.csv_path.text.strip())
        self.csv_info.setText(report)
        missing = [name for name in self.records if self.package.findName(name) is None]
        if missing:
            raise ValueError("Missing glyphs: " + ", ".join(missing))
        return list(self.records)

    def chosen_masters(self) -> list[str]:
        return [self.current_master]

    def planner(self) -> anchor_writer.Planner:
        records, report = load_table(self.csv_path.text.strip())
        self.csv_info.setText(report)
        if set(records) != {glyph.name for glyph in self.glyphs}:
            raise ValueError("CSV glyph rows changed; press Load.")
        for glyph in self.glyphs:
            if anchor_writer.layer_of(glyph, self.current_master) is None:
                raise ValueError(f"{glyph.name}: missing current master layer.")
        return lambda glyph, master, layer: import_changes(layer, records[glyph.name])


def main() -> Any:
    """Show the reusable CSV preview and importer."""
    return scripting.show_script_dialog(AnchorFileImport, KEY)


if __name__ == "__main__":
    main()
