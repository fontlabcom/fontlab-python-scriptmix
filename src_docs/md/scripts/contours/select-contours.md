---
this_file: src_docs/md/scripts/contours/select-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Select Contours

Select each own contour with any selected node in the first selected layer.

Select a node or control handle, then run this command. All nodes in its contour
become selected. Existing components and other non-node selections stay intact.
Other selected layers stay unchanged. No geometry or Undo step is created.

Adapted independently from Pedro Arilla's Paths/Select paths.py (2018–2022).
See NOTICE and additional-tools.json for exact source hashes and Apache terms.
Requires fontlab-fly and App 0.2.71.dev0. Native acceptance remains pending.

Run **Contours > Select Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/87496bb17833845dedfc18cf21d207181c59623060a7ed54d51a73a43bdea530.py)
<!--/codeinclude-->
