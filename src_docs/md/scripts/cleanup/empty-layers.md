---
this_file: src_docs/md/scripts/cleanup/empty-layers.md
tags: ["Cleanup"]
categories: ["Cleanup"]
---

# Empty Layers

Launch the preserved Empty Layers sample.

Purpose: The preserved sample describes this task:
Delete empty auxiliary layers (no outlines, anchors, guides, note or other
data) from the selected glyphs.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Cleanup > Empty Layers in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/cleanup_empty_layers.py

Run **Cleanup > Empty Layers** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6af75b5087513bd7f47cf022e70ab0c80dfb3d1899d7ba259b93270258c6b45f.py)
<!--/codeinclude-->
