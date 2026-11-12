# this_file: Scripts/Kerning/Kerning Studio.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Kerning · Kerning Studio
"""Open Kerning Studio with a live preview and named tools.

What it does:
    Use Pair Editor for staged cells across masters, Kern To Max for selected occurrences, and the named selected-pair tabs for deletion or copying the next pair. Punctuation provides the punctuation conversion workflow.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.kerning_studio, matching Fly and Fontport, and FontLab 9.

How to use:
    Open a font, run this menu and choose a tab. Use Refresh to read the current
    data. For editing tools, review the selected glyphs, masters and proposed rows
    with Preview Changes, then use the named apply action to accept that plan.
    Read-only views display results without changing font data. After changing a
    source font or closing it, reopen the studio before preparing another edit.

Benefit:
    Related actions share one window and a generous preview. Resize the window
    and table columns to inspect longer names and values. Close releases the
    studio's owned callbacks and child previews; keep any reported cleanup error
    visible and retry Close before opening another instance.
"""


def main() -> object:
    """Return the shared studio owner; menu discovery performs no host work."""
    from fly.ap.studios.kerning_studio import show

    return show(consolidated=True)


if __name__ == "__main__":
    main()
