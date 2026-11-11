---
this_file: src_docs/md/scripts/reports/font-revision-comparison.md
tags: ["Reports"]
categories: ["Reports"]
---

# Font Revision Comparison

Compare the open fonts in one window: composite differences and glyph-set differences.

What: Two difference reports from the current font against the other open fonts: Report Composite Differences and Report Glyph Set Differences.
Each report keeps its own capture and text, now as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Font Revision Comparison. Pick a tab, read the report and press Refresh after opening or changing fonts.
Close the window with Close or Escape. If cleanup is refused, the window stays open and Close can be retried. Compare Open Font Revisions keeps its own
menu and dialog and is not part of this window.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Adapted from Jens Kutilek's MIT Glyphs-Scripts (Copyright (c) 2017 Jens Kutilek) on shared App report providers; FontLab additions Apache-2.0.
(fly.ap.fontui.font_revision_comparison). Requires the App with WP08 S62 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Font Revision Comparison** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `974d62d8cc53c388426a521d1e30e8f7cb090276361e1d9acb2efd0ea3fcedb2`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Reports/Font%20Revision%20Comparison.py)
