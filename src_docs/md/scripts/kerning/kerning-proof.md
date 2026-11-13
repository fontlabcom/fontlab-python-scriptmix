---
this_file: src_docs/md/scripts/kerning/kerning-proof.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kerning Proof

Open Kerning Proof with a live preview and named tools.

What it does:
    Pairs From Text collects candidate pairs and supports Set or Add values. Text Preview shows the chosen master. Symmetry prepares corresponding pairs for inspection before applying its plan.

How it works:
    The menu opens the shared App studio through Fly. Importing the menu for
    discovery does not open a window or read a font. The studio owns its controls,
    preview and callbacks; its About tab records the underlying tools and credits.
    Requires fontlabapp.studios.kerning_proof, matching Fly and Fontport, and FontLab 9.

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

Run **Kerning > Kerning Proof** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `c061f4864ea4dcc3cc30d0ebfb5b1901370fe90a73b65f8ee650659b27670d31`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Kerning/Kerning%20Proof.py)
