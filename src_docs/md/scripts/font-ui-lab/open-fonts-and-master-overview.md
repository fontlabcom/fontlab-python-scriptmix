---
this_file: src_docs/md/scripts/font-ui-lab/open-fonts-and-master-overview.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Open Fonts and Master Overview

Browse every currently open font and inspect its current master metrics.

What: Select a font in the browser to read its current master name and available vertical metrics. Refresh the browser after opening or closing documents. The overview uses the existing master inspection and metrics reports; it does not switch the font or its current master.

Use: Open a FontLab font, then run this menu command. The window borrows the
captured document handles and owns only its controls, preview and callbacks.
Changing the active document does not retarget a captured font silently. Close
this window when finished; reopening it captures the available documents again.

Safety: These are read-only reports of stored font data, not unfinished edits
held in a different scripting wrapper. No font is created, saved, edited or
closed, and no master or document selection is changed by the report. A missing
or closed font is reported by the shared window. Native rendering, window
lifetime and complete font/history preservation require separate host checks.

Run **Font UI Lab > Open Fonts and Master Overview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `5aaa6d61cee8042bdaea69552610a30c08c7a04fed1f42085a3d3506b4014f02`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Open%20Fonts%20and%20Master%20Overview.py)
