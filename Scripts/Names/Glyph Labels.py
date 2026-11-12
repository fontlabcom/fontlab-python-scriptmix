# this_file: Scripts/Names/Glyph Labels.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Names · Glyph Labels
"""Glyph Labels: Edit glyph notes and tags, assign mark colours and select glyphs by mark. Selection actions retain the Font-window requirement and their original additive or replacement scope. Notes, tags and colours are separate metadata fields; changing one does not imply changing the others.

Tabs: Batch Glyph Notes; Glyph Notes; Glyph Tags; Mark Color Palette; Select Different Mark Colours; Select by Mark.

How to use: Open the font and choose this tool from Names. Choose the
named tab for the task, enter its inputs and inspect its result before using
an action. Refresh reads the tool's source context. Preview Changes prepares
the selected task for review; Apply Changes is available for supported edits.
Read-only tasks keep their inspection, copy or export actions separate from
font changes. A refusal explains which input or context must be corrected.

The window groups the original task controls with a shared preview and resizeable
layout. Switching fonts elsewhere is not a request to transfer an existing
plan to that font. Recheck the selected glyphs, source, target and layer before
applying work, and refresh when the source changes. Close ends the tool session;
it does not save the borrowed font. Source credits and help appear in About.
Requires FontLab 9 and matching Fly/App packages containing this studio.
"""


def main() -> object:
    """Open the shared tabbed tool without importing Qt before invocation."""
    from fly.ap.studios.glyph_labels.app import show

    return show()


if __name__ == "__main__":
    main()
