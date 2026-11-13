---
this_file: src_docs/md/scripts/font-ui-lab/node-counts-across-masters.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Node Counts Across Masters

Compare glyph point counts across the captured font masters.

What: Choose a reference master and select a glyph in the browser to compare its point counts. Differences describe stored contour points; they do not change outlines or repair compatibility. Missing master layers remain explicit rather than appearing as empty outlines.

Use: Open a FontLab font, then run this menu command. The window borrows the
captured document handles and owns only its controls, preview and callbacks.
Changing the active document does not retarget a captured font silently. Close
this window when finished; reopening it captures the available documents again.

Safety: These are read-only reports of stored font data, not unfinished edits
held in a different scripting wrapper. No font is created, saved, edited or
closed, and no master or document selection is changed by the report. A missing
or closed font is reported by the shared window. Native rendering, window
lifetime and complete font/history preservation require separate host checks.

Run **Font UI Lab > Node Counts Across Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `6d7667a6957ab5691043c80509bc72f0400772ccd8921220d71ae886a4ad752e`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20UI%20Lab/Node%20Counts%20Across%20Masters.py)
