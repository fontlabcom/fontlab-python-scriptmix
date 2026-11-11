---
this_file: src_docs/md/scripts/reports/metric-reports.md
tags: ["Reports"]
categories: ["Reports"]
---

# Metric Reports

Report vertical metrics of every master in every open font in one window.

What: The Vertical Metrics Reporter report: eight stored vertical metric values for every master in every open font, as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Metric Reports. Read the report and press Refresh after changing metrics or opening fonts.
Close the window with Close or Escape. If cleanup is refused, the window stays open and Close can be retried. Sidebearing Direction Marker is a live
Glyph-window overlay and keeps its own menu.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflows on shared App report providers, Apache-2.0
(fly.ap.fontui.metric_reports). Requires the App with WP08 S63 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Metric Reports** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `3c07761900f6774e89efe91daa3503e546e365145e232326859b8c371b682fdc`

[Python source at `dc797fffaa31`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/dc797fffaa31fa6c47959870966e2642fe1df6f7/Scripts/Reports/Metric%20Reports.py)
