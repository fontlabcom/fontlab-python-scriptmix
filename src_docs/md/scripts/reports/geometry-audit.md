---
this_file: src_docs/md/scripts/reports/geometry-audit.md
tags: ["Reports"]
categories: ["Reports"]
---

# Geometry Audit

Audit glyph geometry in one window: near-misses, dangerous off-curves, SVG path dump and point counts.

What: Five geometry reports on the current glyph and master layers: Close But No Cigar, Dangerous Offcurves, Dump to Svg Path Commands, Point Counter (Master Layers) and Point Counter.
Each report keeps its own capture and text, now as a tab of one shared App
window with an About tab (source links and credits) and a Close button.

Use: Run Reports > Geometry Audit. Pick a tab, read the report and copy or save its
text from the tab. Close the window with Close or Escape. If cleanup is
refused, the window stays open and Close can be retried.

Safety: Reports are read-only. They do not change glyphs, layers, selection,
history, preferences or the clipboard unless you choose to copy text. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Adapted from Simon Cozens (MIT: Close But No Cigar, Dump to SVG), Alex Slobzheninov (Apache-2.0: Dangerous Offcurves, Point Counter) and Reza Bohloul (independent implementation, no licence declared: Point Counter (Master Layers)) on shared App report providers; FontLab additions Apache-2.0.
(fly.ap.fontui.geometry_audit). Requires the App with WP08 S60 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Geometry Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `429e5483b5f02dabd7041241e984e9730adf47f242c7b0bee78623be908e6521`

[Python source at `6b1048c4f1db`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6b1048c4f1dbc64ebe49d419db9193ccb3d9a9f0/Scripts/Reports/Geometry%20Audit.py)
