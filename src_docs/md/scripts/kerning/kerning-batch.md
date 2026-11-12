---
this_file: src_docs/md/scripts/kerning/kerning-batch.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kerning Batch

Open Kerning Batch with a live preview and named tools.

What it does:
    Choose Copy masters, Round, Scale, Remove small or Clamp. Each action shows its affected pairs and master scope. Copy masters keeps the source master separate from the ticked destinations.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.kerning_batch, matching Fly and Fontport, and FontLab 9.

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

Run **Kerning > Kerning Batch** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `74aba1c4220ab6bbd1abe644c482af91e2c177362a9ba24cfa596c4f52adafa6`

[Python source at `e537cab9364b`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/e537cab9364bf34af3d36190d5c471795140f722/Scripts/Kerning/Kerning%20Batch.py)
