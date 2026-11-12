---
this_file: src_docs/md/scripts/metrics/spacing-studio.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Spacing Studio

Open Spacing Studio with a live preview and named tools.

What it does:
    Use Sidebearings, Reference and Italic to prepare spacing edits. Strings provides an unkerned text preview, the raw spacing inspector, selected-layer offsets and an editable TMetrics child. The child also requires fontlabapp.fontui.tmetrics.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.spacing_studio, matching Fly and Fontport, and FontLab 9.

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

Run **Metrics > Spacing Studio** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1d8b9388f53989538018a0cbb0480354d3d8dfc46c1150da141642328e9221f3`

This source is not committed at `38d3549fc6f0`; no immutable link is offered.
