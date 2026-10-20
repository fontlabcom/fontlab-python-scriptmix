---
this_file: src_docs/md/scripts/masters/overview.md
tags: ["Masters"]
categories: ["Masters"]
---

# Overview

One table of all masters: axis location, vertical metrics and italic angle.

Rows follow the font's master order; the current master is bold. Vertical metrics come from
``fontlab.FontMetrics(package, master)``; FontLab has no per-master italic-angle accessor, so each
master is made current for the read and the original master is restored. Double-click a row to
make that master current. Read-only otherwise.

Run **Masters > Overview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4e0de2e71ab69e3983debe74ca1a3e117e2cd545b8f989660e8864ec24f57bad.py)
<!--/codeinclude-->
