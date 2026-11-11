---
this_file: src_docs/md/scripts/reports/master-structure-audit.md
tags: ["Reports"]
categories: ["Reports"]
---

# Master Structure Audit

Check master structure in one window: node compatibility and the reason masters do not interpolate.

What: Two compatibility reports: Master Node Compatibility Report and Why You Not Compatible.
Each report keeps its own capture and text, now as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Master Structure Audit. Pick a tab, read the report and copy or save its
text from the tab. Close the window with Close or Escape. If cleanup is
refused, the window stays open and Close can be retried.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflows on shared App report providers, Apache-2.0
(fly.ap.fontui.master_structure_audit). Requires the App with WP08 S61 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Master Structure Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a4f9085767c0037720123cccb2b0b1432050cf333a5b7c99a3c9d358cbbc7e5a`

[Python source at `bf9287c6130a`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/bf9287c6130a3083b3c1047050305dfceecbee2b/Scripts/Reports/Master%20Structure%20Audit.py)
