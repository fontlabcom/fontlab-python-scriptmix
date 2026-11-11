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

SHA256: `f50a63982f8ff078f0590f659d69b512bf4021028f420def788235062c526322`

[Python source at `cb3a95057641`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cb3a95057641f3b2382a887172fab524dbc4901a/Scripts/Font%20UI%20Lab/Master%20Compatibility%20Browser.py)
