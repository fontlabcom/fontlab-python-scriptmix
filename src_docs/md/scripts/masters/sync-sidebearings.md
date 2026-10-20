---
this_file: src_docs/md/scripts/masters/sync-sidebearings.md
tags: ["Masters"]
categories: ["Masters"]
---

# Sync Sidebearings

Launch the preserved Sync Sidebearings sample.

Purpose: The preserved sample describes this task:
Copy side-bearings from a reference master to the other masters,
proportionally or as-is.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Masters > Sync Sidebearings in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/masters_sync_metrics.py

Run **Masters > Sync Sidebearings** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/125d02cec7e6c38bafa67b0ede6ca0726a801669eaa5a1fc30882061290dbd7e.py)
<!--/codeinclude-->
