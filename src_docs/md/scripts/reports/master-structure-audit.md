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

Source: Adapted from Fernando Diaz and Reset Type Studio (Apache-2.0, 2025: Master Node Compatibility Report) and Simon Cozens (MIT: Why You Not Compatible) on shared App report providers; FontLab additions Apache-2.0.
(fly.ap.fontui.master_structure_audit). Requires the App with WP08 S61 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Master Structure Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b6d19a38339e9eb77a940bab00bead27ffc4646f10c03bc2b2c401dfd9649194`

[Python source at `cca80db1b47f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cca80db1b47f998bbbf4a26427a1e5949ccf7230/Scripts/Reports/Master%20Structure%20Audit.py)
