---
this_file: src_docs/md/scripts/reports/open-contours-app.md
tags: ["Reports"]
categories: ["Reports"]
---

# Open Contours App

Report open contours of every master with a Select glyphs action in one window.

What: The Open Contours report: every open contour of the open font across all masters (glyph, master, contour, nodes, end gap), as a tab of one shared App
window with a Select glyphs button, an About tab (source links and credits) and a Close button.

Use: Run Reports > Open Contours App. Press Refresh after editing contours; Select glyphs selects the glyphs listed, if the font is still the one reported.
Close the window with Close or Escape. If cleanup is refused, the window stays open and Close can be retried.

Safety: The report is read-only. Only Select glyphs changes the glyph selection, and only for the font that was scanned. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflow on shared App report providers, Apache-2.0
(fly.ap.fontui.open_contours). Requires the App with WP08 S65 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Open Contours App** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `fceb33b529d4b4923d8f17a6f4f1a61aa2f27a406ad452c12b60b552708b29f7`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Reports/Open%20Contours%20App.py)
