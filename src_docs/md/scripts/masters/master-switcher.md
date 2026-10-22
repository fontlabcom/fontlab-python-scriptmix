---
this_file: src_docs/md/scripts/masters/master-switcher.md
tags: ["Masters"]
categories: ["Masters"]
---

# Master Switcher

Choose the font's current master from a compact modeless palette.

What it does:
    Run the script with a font open. Click a master button; its axis location appears
    below its name. The current master is checked and bold. Use the first nine button
    shortcuts while the palette has focus. The controls change the package master,
    using FontLab's native setMaster/UpdateAll behavior. Close releases owned signals.
    Reopen the palette after changing the font's masters or their locations.

How it works:
    Use the shared App master-switcher panel with one exclusive button per
    master. Show axis locations and highlight the current master after a
    guarded switch.

Why this design:
    A compact palette keeps master navigation available without repeatedly
    opening a larger font-info view.

How to use:
    Open a font and run Masters > Master Switcher. Click a master or use the
    first nine shortcuts while the palette has focus. Reopen after changing
    the masters list or locations.

Benefit:
    Navigate the family masters with visible current state while keeping
    master definitions unchanged.

Run **Masters > Master Switcher** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/07e2dc1bb6868e0c7feb6a0a6238b64968c598cb10b4af3b17233ecae8b208ab.py)
<!--/codeinclude-->
