---
this_file: src_docs/md/scripts/metrics/vertical-metrics.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Vertical Metrics

Open Vertical Metrics with a live preview and named tools.

What it does:
    Zones prepares alignment-zone changes for inspection. Diagram shows vertical metrics for the selected master. Refresh after changing the font, and use the diagram to compare the displayed values before further work.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.vertical_metrics.app, matching Fly and Fontport, and FontLab 9.

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

Run **Metrics > Vertical Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `717c818e588049d714b618181832cc874dd16d1cf24dade5aa67a6d7a538dd72`

[Python source at `e537cab9364b`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/e537cab9364bf34af3d36190d5c471795140f722/Scripts/Metrics/Vertical%20Metrics.py)
