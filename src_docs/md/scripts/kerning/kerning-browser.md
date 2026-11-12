---
this_file: src_docs/md/scripts/kerning/kerning-browser.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kerning Browser

Open Kerning Browser with a live preview and named tools.

What it does:
    Browse Pairs, Classes, Masters, Energy and Missing pairs. Persistence reports values against the measured save/reopen limit. Same groups opens the selected group proof. Exceptions can remove explicitly ticked rows.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.kerning_browser, matching Fly and Fontport, and FontLab 9.

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

Run **Kerning > Kerning Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1e02e60b9ba7058275f09cb29fc04018d14a1fdc684604ae58c6fb6e6c68442c`

This source is not committed at `38d3549fc6f0`; no immutable link is offered.
