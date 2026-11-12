# this_file: Scripts/Features/Feature Explorer.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Feature Explorer
"""Feature Explorer: Compare alternate glyphs, find ligature names and inspect suffix families. These reports use glyph names and source relationships. Naming matches identify candidates; they do not prove that an OpenType lookup selects a glyph during shaping. Reports preserve the original master and source scopes.

Tabs: Alternate Preview; Ligature Finder; Suffix Report.

How to use: Open the font and choose this tool from Features. Choose the
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
    from fly.ap.studios.feature_explorer.app import show

    return show()


if __name__ == "__main__":
    main()
