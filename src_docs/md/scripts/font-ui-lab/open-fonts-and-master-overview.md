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

SHA256: `888ebbf8f485d7c807fa776ac430d6905d69f39c75cde5be30904e7c9ab79dd9`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Font%20UI%20Lab/Open%20Fonts%20and%20Master%20Overview.py)
