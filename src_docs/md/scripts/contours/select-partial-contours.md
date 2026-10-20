---
this_file: src_docs/md/scripts/contours/select-partial-contours.md
tags: ["Contours"]
categories: ["Contours"]
---

# Select Partial Contours

Fill stored-order spans between originally selected nodes in the first layer.

Each selected node toggles the fill state. State carries across contour bounds;
the command never wraps around to the first node or chooses a shortest arc.
Controls count as nodes. Components, other non-node selections and other layers
stay unchanged. No geometry or Undo step is created.

Adapted independently from Pedro Arilla's Paths/Select partial path.py
(2018–2022). See NOTICE and additional-tools.json for exact hashes and Apache
terms. Requires fontlab-fly and App 0.2.71.dev0. Native acceptance is pending.

Run **Contours > Select Partial Contours** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/92922efdc4b4d9cb9641a3f8a9c6477c26f348eac5a026952a231f54c80b6362.py)
<!--/codeinclude-->
