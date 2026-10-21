---
this_file: src_docs/md/scripts/masters/use-layer-as-master.md
tags: ["Masters"]
categories: ["Masters"]
---

# Use Layer As Master

Make a backup or alternate layer the master layer of its glyph.

What it does:
    Swap the roles of the shown layer and the master layer it belongs to. The
    shown layer becomes the master layer. The old master layer is kept as
    "<Master>@ HH:MM:SS, DD/MM/YY". Backgrounds (mask layers) travel with their
    layers: the background of the chosen layer becomes the master background.

How it works:
    FontLab decides by layer name which layer is the master layer of a master
    (see "Display Next Layer"). So the script only renames. It renames the old
    master layer to the backup name, then the chosen layer to the master name,
    and renames their mask layers to match the FontLab mask-name rule
    ("mask.<layer name>", or plain "mask" for the layer of a single-master font).
    Shapes, anchors, guides and metrics stay in the layer objects. Nothing is
    cloned, so nothing is lost. One notification covers all layers: one Undo step.

Why this design:
    - Renaming keeps every property of both layers. The Glyphs original must copy
      paths, components, anchors and sidebearing keys one by one.
    - Names are simulated before the first rename. A clash stops the run early.
    - If a rename fails, the script puts the old names back.
    - Locked, mask, service, automatic and image layers are refused. So is a
      glyph that is a base of an automatic layer: FontLab cannot undo it.

How to use:
    Show a backup layer (see "Display Next Layer"). Run the script. Check
    compatibility with the other masters afterwards: a swapped layer can have
    a different point structure.

Benefit:
    Restore an earlier state of a master in one step and keep the current one.

Credit:
    Behaviour after Pedro Arilla's Glyphs script "Use layer as master"
    (Apache-2.0). Independent rewrite. No source code was copied.

Run **Masters > Use Layer As Master** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8e2b01d202dcdd7f947eb1919a52be4de1248f98fa262c676914950a96296e35.py)
<!--/codeinclude-->
