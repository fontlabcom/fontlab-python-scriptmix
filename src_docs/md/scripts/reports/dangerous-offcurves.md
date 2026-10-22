---
this_file: src_docs/md/scripts/reports/dangerous-offcurves.md
tags: ["Reports"]
categories: ["Reports"]
---

# Dangerous Offcurves

Find dangerous offcurves throughout every glyph and foreground layer.

Scan all own paths, including auxiliary and empty layers, without selection
filtering or component decomposition. Each first offcurve retains the original
four-node neighbour window (also for open/quadratic paths), four finite axis
probes at ±10000, all-four-hit gate and any strict distance below0.05 units.
Open a genuine new tab containing every distinct matching exact layer in stored
order, and show every per-curve finding in an owned selectable result window.
No matches gives the complete original diagnosis. Close and rerun for a fresh
scan. No font, selection, history, clipboard, preferences or Output writer runs.

Requires App[fontui]>=0.2.117.dev0 and public Fly in FontLab9 Python3.11.
fontTools analytic intersections use ascending curve t for first-result choice,
an explicit adaptation of unspecified Glyphs ordering. Exact endpoints and
finite-line bounds use the shared geometry code; coincident intersections follow
the geometry backend. A failure yields
no partial report; failed tab creation can leave a new owned tab.

Adapted from Alex Slobzheninov's Bug fixing/Dangerous Offcurves.py,
Apache-2.0; upstream attribution and exact source pin are retained in NOTICE.

Run **Reports > Dangerous Offcurves** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/04d94256f6f0171c2b579e4d36c73a0a2833cc33d6f2a974d9ad504d52b370e0.py)
<!--/codeinclude-->
