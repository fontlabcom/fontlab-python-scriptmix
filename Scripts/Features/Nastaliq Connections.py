# this_file: Scripts/Features/Nastaliq Connections.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Nastaliq Connections
"""Nastaliq Connections: Inspect pairs of joining glyphs and edit their connection choices using the retained connection editor. Choose source glyphs and inspect the preview before saving a connection. Existing source snapshots and exact glyph references remain part of the write checks; missing or stale targets require a fresh capture.

Tabs: Nastaliq Connection Editor.

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
    from fly.ap.studios.nastaliq_connections.app import show

    return show()


if __name__ == "__main__":
    main()
