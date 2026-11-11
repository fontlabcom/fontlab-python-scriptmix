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

Source: Original workflows on shared App report providers, Apache-2.0
(fly.ap.fontui.font_revision_comparison). Requires the App with WP08 S62 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Font Revision Comparison** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `9db4551948243d12c11ddad7b545754c71a3a9c3d92dc59e3a6a5fab74aae3b2`

[Python source at `dc797fffaa31`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/dc797fffaa31fa6c47959870966e2642fe1df6f7/Scripts/Reports/Font%20Revision%20Comparison.py)
