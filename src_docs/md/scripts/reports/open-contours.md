---
this_file: src_docs/md/scripts/reports/open-contours.md
tags: ["Reports"]
categories: ["Reports"]
---

# Open Contours

Find open contours on every master and select the glyphs that have them.

Open paths are usually unintended in a font for filling: they render
unpredictably and break overlap removal. Each row is one open contour with
its master, node count and the gap between its end points. Nothing in the
font changes.

Run **Reports > Open Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/47f01b0930d1ad4464f09a717a5c8552d74415305fe7a07f98da2842065c6d29.py)
<!--/codeinclude-->
