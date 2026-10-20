---
this_file: src_docs/md/scripts/masters/layer-cleanup.md
tags: ["Masters"]
categories: ["Masters"]
---

# Layer Cleanup

Launch the preserved Layer Cleanup sample.

Purpose: The preserved sample describes this task:
List the non-master layers of the selected glyphs (masks, backups, others)
and delete the ticked ones.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Masters > Layer Cleanup in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/masters_layer_cleanup.py

Run **Masters > Layer Cleanup** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3365526018394932fea7929f1f99e17c630270652d512766bf04240c468828d8.py)
<!--/codeinclude-->
