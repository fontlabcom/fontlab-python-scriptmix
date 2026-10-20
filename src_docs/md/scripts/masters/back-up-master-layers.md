---
this_file: src_docs/md/scripts/masters/back-up-master-layers.md
tags: ["Masters"]
categories: ["Masters"]
---

# Back Up Master Layers

Launch the preserved Back Up Master Layers sample.

Purpose: The preserved sample describes this task:
Copy the master layers of the selected glyphs to named backup layers before
risky edits.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Masters > Back Up Master Layers in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/masters_backup_layer.py

Run **Masters > Back Up Master Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/99560e2eb702d20b676651301bf26b6123f378c25df8ac4d3ca25d0f4413e3e2.py)
<!--/codeinclude-->
