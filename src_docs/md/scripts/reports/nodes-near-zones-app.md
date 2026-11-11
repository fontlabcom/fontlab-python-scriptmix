---
this_file: src_docs/md/scripts/reports/nodes-near-zones-app.md
tags: ["Reports"]
categories: ["Reports"]
---

# Nodes Near Zones App

Report open contours of every master with a Select glyphs action in one window.

What: The Nodes Near Zones report: on-curve nodes of the selected glyphs (or all glyphs) that sit 1 to 30 units off the baseline, x-height, cap height, ascender or descender
(glyph, master, zone, node, offset), as a tab of one shared App window with a tolerance control, a Select glyphs button, an About tab and a Close button.

Use: Run Reports > Nodes Near Zones App. Change the tolerance to rescan, or press Refresh after editing; Select glyphs selects the glyphs listed, if the font is still the one reported.
Close the window with Close or Escape. If cleanup is refused, the window stays open and Close can be retried.

Safety: The report is read-only. Only Select glyphs changes the glyph selection, and only for the font that was scanned. Run it
from the main UI thread; the window owns its dialogs and releases them on close.

Source: Original workflow on shared App report providers, Apache-2.0
(fly.ap.fontui.nodes_near_zones). Requires the App with WP08 S66 assembly and
fontlab-fly in FontLab 9 Python 3.11.

Run **Reports > Nodes Near Zones App** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `05000cc94966a28b6c3efc0c7e80a2ef684fa378f71436e469a038221d3c2f13`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Reports/Nodes%20Near%20Zones%20App.py)
