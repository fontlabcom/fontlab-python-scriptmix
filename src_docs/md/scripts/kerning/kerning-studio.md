---
this_file: src_docs/md/scripts/kerning/kerning-studio.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kerning Studio

Open Kerning Studio with a live preview and named tools.

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

Run **Kerning > Kerning Studio** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `7a6d95748cfcc594aa6867bbd588a1781b34001ae06c5563cfb75254e329b947`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Kerning/Kerning%20Studio.py)
