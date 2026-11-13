---
this_file: src_docs/md/scripts/font-ui-lab/master-compatibility-browser.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Master Compatibility Browser

Browse glyphs and inspect their existing master-layer compatibility report.

What: Select a glyph to view its preview alongside the layer compatibility findings. The report compares the registered master layers and keeps missing or unsupported data visible. Use the browser to move between glyphs without changing the document selection or current master.

Use: Open a FontLab font, then run this menu command. The window borrows the
captured document handles and owns only its controls, preview and callbacks.
Changing the active document does not retarget a captured font silently. Close
this window when finished; reopening it captures the available documents again.

Safety: These are read-only reports of stored font data, not unfinished edits
held in a different scripting wrapper. No font is created, saved, edited or
closed, and no master or document selection is changed by the report. A missing
or closed font is reported by the shared window. Native rendering, window
lifetime and complete font/history preservation require separate host checks.

Run **Font UI Lab > Master Compatibility Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `04c0cd48962f35283d66aa6c978bae5bc75e1efc6ff91229fd5bbe9f54ff7435`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Master%20Compatibility%20Browser.py)
