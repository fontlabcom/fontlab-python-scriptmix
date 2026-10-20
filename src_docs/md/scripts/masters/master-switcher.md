---
this_file: src_docs/md/scripts/masters/master-switcher.md
tags: ["Masters"]
categories: ["Masters"]
---

# Master Switcher

Choose the font's current master from a compact modeless palette.

Run the script with a font open. Click a master button; its axis location appears
below its name. The current master is checked and bold. Use the first nine button
shortcuts while the palette has focus. The controls change the package master,
using FontLab's native setMaster/UpdateAll behavior. Close releases owned signals.
Reopen the palette after changing the font's masters or their locations.

Run **Masters > Master Switcher** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/4c5acdf64eb680f6351902fcc8d5864e8e656496c3cc2d7b952fe87cc936c6a4.py)
<!--/codeinclude-->
