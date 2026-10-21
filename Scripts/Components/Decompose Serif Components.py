# this_file: Scripts/Components/Decompose Serif Components.py
# SPDX-License-Identifier: Apache-2.0
"""Decompose only components whose base name starts with Serif.

What: Replace matching components in selected glyphs on chosen masters.
How: Preview each replacement, then use the shared component writer. Nested
components remain components. Other components and own contours stay.
Why: A prefix filter keeps reusable letter parts while releasing serif parts.
Use: Select glyphs, run this tool, choose masters and press Decompose.
Benefit: One filtered batch is recorded as one Undo step. Other reusable parts
stay linked. Automatic layers and their bases are refused.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Components/Decompose all serif components.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code copied.
"""

from typing import Any

import fly.ap.component_panel as panel
import fly.ap.component_writer as writer
import fly.ap.scripting as scripting  # noqa: PLR0402

TITLE = "Decompose Serif Components"
KEY = "components_decompose_serifs"


def changes(package: Any, glyph: Any, master: str, layer: Any) -> list[writer.Change]:
    """Describe only Serif-prefixed components; block unsafe base copies."""
    result = []
    for part in writer.components(layer):
        base = writer.base_of(part)
        if not base.startswith("Serif"):
            continue
        problem = writer.copy_problem(package, (glyph.name, master), part, master)
        result.append(
            writer.Change(base, "component", "editable parts", part.id, problem=problem)
        )
    return result


class SerifPanel(panel.panel_type()):
    """Reuse the component preview and guarded master scope."""

    TITLE, KEY, ACTION, DONE = TITLE, KEY, "Decompose", "Decomposed"
    HEADERS = ("Glyph · master", "Component", "Becomes")

    def build_controls(self) -> None:
        self.scope = self.scope_box()
        from fly import qt

        self.form.addWidget(qt.QtGui.QLabel("Masters"), 0, 0)
        self.form.addWidget(self.scope, 0, 1)
        self.watch(self.scope.currentIndexChanged)

    def planner(self) -> writer.Planner:
        return lambda glyph, master, layer: changes(self.package, glyph, master, layer)

    def editor(self) -> writer.Editor:
        return writer.EjectEditor(unlock=True)


def main() -> Any:
    """Show the non-modal filtered-decomposition panel."""
    try:
        return scripting.show_script_dialog(SerifPanel, KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        from fly import ap, qt

        qt.QtGui.QMessageBox.warning(ap.fontlab.MainWindow(), TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
