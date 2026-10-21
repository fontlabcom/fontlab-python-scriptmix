# this_file: Scripts/Cleaning/Delete Stickers.py
# SPDX-License-Identifier: Apache-2.0
"""Remove FontLab stickers from all layers or master layers.

What: Delete text, arrow and symbol stickers from selected glyphs or the whole
font. Choose every stored layer, including backgrounds, or master layers only.
How: Preview each layer's sticker count, then remove only ShapeSticker shapes.
Contours, components, anchors, image shapes and layer notes stay.
Why: Stickers are FontLab's equivalent of the source tools' layer annotations.
Use: Choose the glyph and layer scope. For the whole font, press Preview, then
Delete and confirm the font and counts. Other scopes use the live table.
Benefit: Clear annotations over many layers in one action. The deletion is
recorded as one Undo step. Glyphs with automatic layers are listed and kept.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Cleaning/Delete annotations in all layers.py and Delete annotations in all
master layers.py, Apache-2.0. Repository:
https://github.com/pedroarilla/glyphs-scripts . No source code copied.
"""

from dataclasses import dataclass
from typing import Any

import fly.ap.glyph_catalog as glyph_catalog  # noqa: PLR0402
import fly.ap.history as history  # noqa: PLR0402
import fly.ap.scripting as scripting  # noqa: PLR0402
import fly.ap.selection_panel as selection_panel  # noqa: PLR0402

TITLE = "Delete Stickers"
KEY = "cleaning_delete_stickers"


@dataclass(frozen=True)
class Row:
    """One layer, its stickers, and any reason to keep it."""

    glyph: Any
    layer: Any
    stickers: tuple[Any, ...]
    note: str = ""


def sticker_kind() -> Any:
    """Resolve the native enum name; PythonQt dictionaries can pad their keys."""
    from fly import ap

    for name, value in ap.fontlab.ShapeType.items():
        if str(name).strip() == "ShapeSticker":
            return value
    raise ValueError("FontLab does not expose the ShapeSticker enum.")


def survey(package: Any, names: list[str], masters_only: bool) -> list[Row]:
    """Read every chosen stored layer once; list automatic owners as kept."""
    kind = sticker_kind()
    facts = history.scan_auto_facts(package)
    rows = []
    for name in dict.fromkeys(names):
        glyph = package.findName(name)
        if glyph is None or glyph.isNull:
            raise ValueError(f"{name}: glyph is no longer in this font.")
        for layer in glyph.layers:
            if masters_only and str(layer.name) not in package.masters:
                continue
            stickers = tuple(shape for shape in layer.shapes if shape.shapeType == kind)
            if stickers:
                note = history.refusal(facts, str(glyph.name), "metadata")
                if layer.isLocked:
                    note = "locked layer"
                rows.append(Row(glyph, layer, stickers, note))
    return rows


def remove(package: Any, rows: list[Row]) -> dict[str, int]:
    """Remove the previewed sticker objects through one history commit."""
    ready = [row for row in rows if not row.note]
    if not ready:
        return {"stickers": 0, "layers": 0}
    kind = sticker_kind()
    for row in ready:
        if (
            package.findName(str(row.glyph.name)) is None
            or int(package.findName(str(row.glyph.name)).id) != int(row.glyph.id)
            or row.layer not in row.glyph.layers
        ):
            raise ValueError("The font changed; Preview again.")
        if row.layer.isLocked or any(
            shape not in row.layer.shapes or shape.shapeType != kind
            for shape in row.stickers
        ):
            raise ValueError("Layer stickers changed; Preview again.")
    glyphs = list({str(row.glyph.name): row.glyph for row in ready}.values())
    retained = [
        item
        for row in ready
        for shape in row.stickers
        for item in (shape, shape.shapeData)
    ]
    ids = {int(shape.id) for row in ready for shape in row.stickers}

    def mutate() -> None:
        for row in ready:
            for shape in row.stickers:
                row.layer.removeShape(shape)
            row.layer.changed()

    def read_back() -> list[str]:
        return [
            str(row.layer.name)
            for row in ready
            if any(int(shape.id) in ids for shape in row.layer.shapes)
        ]

    result = history.commit(
        TITLE,
        [row.layer for row in ready],
        glyphs,
        mutate,
        operation="metadata",
        facts=history.scan_auto_facts(package),
        retain=retained,
        read_back=read_back,
    )
    if result.mismatches:
        raise RuntimeError(
            "Some stickers remain. Native changes may remain; use Edit > Undo."
        )
    return {"stickers": sum(len(row.stickers) for row in ready), "layers": len(ready)}


def panel_type() -> type:
    """Use the shared non-modal table and signal-lifetime handling."""
    from fly import qt

    class StickerPanel(selection_panel.panel_type()):
        """Glyph scope and layer scope; every preview row represents one layer."""

        TITLE, KEY, ACTION = TITLE, KEY, "Delete"
        HEADERS = ("Glyph", "Layer", "Stickers", "Action")
        SCOPE, CONSENT, ALIGN = False, "", False

        def build_controls(self) -> None:
            self.preview_key: tuple | None = None
            self.preview_button = qt.QtGui.QPushButton("Preview")
            self.add_row("", self.preview_button)
            self.watch(self.preview_button.clicked, self.preview)
            self.glyph_scope = qt.QtGui.QComboBox()
            self.glyph_scope.addItems(["Whole font", "Selected glyphs"])
            self.layer_scope = qt.QtGui.QComboBox()
            self.layer_scope.addItems(["All layers", "Master layers"])
            self.add_row("Glyphs", self.glyph_scope)
            self.add_row("Layers", self.layer_scope)
            self.watch(self.glyph_scope.currentIndexChanged)
            self.watch(self.layer_scope.currentIndexChanged)

        def plan(self) -> list[Row]:
            package = self.font_package()
            names = (
                [str(row[0]) for row in glyph_catalog.capture().rows]
                if self.glyph_scope.currentIndex == 0
                else self.names
            )
            if not names:
                raise ValueError("Select glyphs, then press Use selection.")
            return survey(package, names, bool(self.layer_scope.currentIndex))

        def cells(self, row: Row) -> list[str]:
            return [
                str(row.glyph.name),
                str(row.layer.name),
                str(len(row.stickers)),
                "kept: " + row.note if row.note else "delete",
            ]

        def intro(self) -> str:
            return "Only stickers are removed; other shapes and notes stay."

        def fingerprint(self, package: Any, rows: list[Row]) -> tuple:
            """Bind confirmation to the font, scopes and every previewed sticker."""
            return (
                int(package.id),
                int(self.glyph_scope.currentIndex),
                int(self.layer_scope.currentIndex),
                tuple(
                    (
                        int(row.glyph.id),
                        int(row.layer.id),
                        row.note,
                        tuple(int(shape.id) for shape in row.stickers),
                    )
                    for row in rows
                ),
            )

        def refresh(self) -> None:
            super().refresh()
            if self.glyph_scope.currentIndex == 0:
                try:
                    ready = any(not row.note for row in self.rows)
                    self.apply_button.setEnabled(
                        ready
                        and self.preview_key
                        == self.fingerprint(self.font_package(), self.rows)
                    )
                except (ValueError, RuntimeError, TimeoutError):
                    self.apply_button.setEnabled(False)

        def preview(self) -> None:
            self.preview_key = None
            self.refresh()
            if any(not row.note for row in self.rows):
                self.preview_key = self.fingerprint(self.font_package(), self.rows)
                self.apply_button.setEnabled(True)
                self.status.setText(
                    "Preview ready. Whole-font deletion asks for confirmation."
                )

        def write(self, package: Any, rows: list[Row]) -> dict[str, int]:
            if self.glyph_scope.currentIndex == 0:
                if (
                    self.preview_key is None
                    or self.fingerprint(package, rows) != self.preview_key
                ):
                    self.preview_key = None
                    raise ValueError("The plan changed. Press Preview before Delete.")
                ready = [row for row in rows if not row.note]
                glyphs = len({int(row.glyph.id) for row in ready})
                count = sum(len(row.stickers) for row in ready)
                message = f'Delete stickers in "{package.name}"?\n{glyphs} glyphs, {len(ready)} layers, {count} stickers.'
                box = qt.QtGui.QMessageBox
                answer = box.question(
                    self, TITLE, message, box.StandardButtons(box.Yes | box.No), box.No
                )
                if answer != box.Yes:
                    return {"stickers": 0, "layers": 0}
                package = self.font_package()
                rows = self.plan()
                if self.fingerprint(package, rows) != self.preview_key:
                    self.preview_key = None
                    raise ValueError(
                        "The plan changed during confirmation. Press Preview again."
                    )
            self.preview_key = None
            return remove(package, rows)

        def result_text(self, result: dict[str, int]) -> str:
            return (
                f"Deleted {result['stickers']} stickers on {result['layers']} layers."
            )

    return StickerPanel


def main() -> Any:
    """Open the sticker cleanup preview; no change on opening."""
    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import ap, qt

        qt.QtGui.QMessageBox.warning(ap.fontlab.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
