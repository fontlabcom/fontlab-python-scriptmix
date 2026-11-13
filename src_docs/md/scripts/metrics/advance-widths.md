---
this_file: src_docs/md/scripts/metrics/advance-widths.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Advance Widths

Open Advance Widths with a live preview and named tools.

What it does:
    Inspect advances in Table, prepare Round and Scale edits, use Tabular for setting or checking equal widths, and review Marks before setting mark advances. Choose the master scope and inspect excluded layers.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.advance_widths, matching Fly and Fontport, and FontLab 9.

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

Run **Metrics > Advance Widths** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `ca0b1017e850fd54fe7303c5c68091fd142b0de36002a1a44322dc8d91dbc143`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Metrics/Advance%20Widths.py)
