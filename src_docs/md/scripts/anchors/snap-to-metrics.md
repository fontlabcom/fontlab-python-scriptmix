---
this_file: src_docs/md/scripts/anchors/snap-to-metrics.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Snap To Metrics

Launch the preserved Snap To Metrics sample.

Purpose: The preserved sample describes this task:
Move named anchors vertically onto a font metric of their own master, plus
an offset.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Anchors > Snap To Metrics in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/anchors_snap_to_metrics.py

Run **Anchors > Snap To Metrics** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d4f81dc6e807587d3317c0b11df3156308d2d998d1faa152af076a2d88b04170.py)
<!--/codeinclude-->
