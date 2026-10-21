# this_file: Scripts/Anchors/Remove Extraneous Mark Anchors.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Anchors · Remove Extraneous Mark Anchors
"""Remove opposite-side anchors from selected marks on all masters.

What: Remove bottom where _top exists, and top where _bottom exists.
How: Preview conditional removals across named masters. Keep all other pins
and automatic layers; refuse unsafe dependencies before writing.
Why: A conditional rule preserves useful stacking anchors that an
unconditional name-based removal would also delete.
Use: Select glyphs, inspect the non-modal preview, then click Remove.
Benefit: Clean mark attachments consistently across masters. Each
application is recorded as one Undo step.

Source: Simon Cozens, https://github.com/simoncozens/GlyphsScripts,
MIT, copyright 2017 Simon Cozens. Independent behaviour rewrite; no source
code was copied.
"""

from typing import Any

import fly.ap.anchor_panel as anchor_panel  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup
import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly submodule import avoids native attribute lookup

TITLE = "Remove Extraneous Mark Anchors"
KEY = "anchors_remove_extraneous_mark_anchors"


def opposite_changes(layer: Any) -> list[anchor_writer.Change]:
    """Remove only the opposite plain anchor when its mark anchor exists."""
    names = {pin.name for pin in layer.anchors}
    obsolete = {
        plain
        for mark, plain in (("_top", "bottom"), ("_bottom", "top"))
        if mark in names and plain in names
    }
    return [
        anchor_writer.Change(name, "present", "remove", ("remove", name, None))
        for name in sorted(obsolete)
    ]


class MarkAnchorCleanup(anchor_panel.panel_type()):
    """Preview the conditional removals on every master of the selection."""

    TITLE, KEY, ACTION = TITLE, KEY, "Remove"

    def refresh(self) -> None:
        """Contain scan errors inside the panel and disable its write action."""
        try:
            super().refresh()
        except (ValueError, RuntimeError, TimeoutError) as error:
            self.apply_button.setEnabled(False)
            self.status.setText(str(error))

    def planner(self) -> anchor_writer.Planner:
        """Re-read anchor names on Apply; never retain pin objects."""
        return lambda glyph, master, layer: opposite_changes(layer)


def main() -> Any:
    """Show or raise the owned non-modal preview."""
    return scripting.show_script_dialog(MarkAnchorCleanup, KEY)


if __name__ == "__main__":
    main()
