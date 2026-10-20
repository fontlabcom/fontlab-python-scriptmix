---
this_file: src_docs/md/scripts/metrics/alignment-zones.md
tags: ["Metrics"]
categories: ["Metrics"]
---

# Alignment Zones

Launch the preserved Alignment Zones sample.

Purpose: The preserved sample describes this task:
Edit the PostScript alignment zones (blue zones) of each master in a table.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Metrics > Alignment Zones in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/metrics_zones_editor.py

Run **Metrics > Alignment Zones** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c99db407b31000f5897c57ff3bd532fed0a3d244859778dc26dfe4264fcd5084.py)
<!--/codeinclude-->
