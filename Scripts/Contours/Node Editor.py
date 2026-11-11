# this_file: Scripts/Contours/Node Editor.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Node Editor
"""Duplicate and inspect selected nodes in one captured-font workspace.

What: Per-glyph Duplicator uses each glyph's own selected reference layer, with
master compatibility and optional coincident handles. Current Layer, All
Foreground Layers and Two Handles preserve the three distinct original source
policies. Coordinates follows selected nodes live and copies checked coordinates.

How: Open a font and select nodes, then choose a task. Preview Changes accepts
its captured plan and shows a read-only TGlyph view. Apply Changes rechecks the
source, selection and layer before one guarded history operation. Discard staged
changes before Refresh; changing tabs keeps each task's staged state. Switching
fonts does not retarget this window: close it and reopen for the other font.

Safety: Locked, shared, automatic and unsupported outlines remain protected by
the selected policy. A partial failure retains recovery diagnostics; inspect the
font and its Undo history before retrying. Close stops the owned live timer and
releases connections. Retry Close if a native cleanup operation is refused.

Credit: Independent behaviour rewrite after Fernando Díaz, Reset Type Studio,
https://github.com/Reset-Type-Studio/Glyphs-Scripts (Apache-2.0 in README).
FontLab App provides the shared shell, node engines, history and live preview.
Setup: install the matching FontLab App and Fly packages, including App's Fontport
extra for the live glyph view. This menu contains no archived script execution.
"""


def main():
    """Open the shared App Node Editor without importing sibling menu scripts."""
    from fly.ap.studios.node_editor import show

    return show()


if __name__ == "__main__":
    main()
