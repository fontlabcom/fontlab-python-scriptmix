---
this_file: src_docs/md/scripts/guides/suggest-zones-from-overshoots.md
tags: ["Guides"]
categories: ["Guides"]
---

# Suggest Zones From Overshoots

Launch the preserved Suggest Zones From Overshoots sample.

Purpose: The preserved sample describes this task:
Set PostScript alignment zones from the overshoots of H/O (baseline, caps)
and x/o (x-height).

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Guides > Suggest Zones From Overshoots in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/zones_from_glyphs.py

Run **Guides > Suggest Zones From Overshoots** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ec0d9fbe22d6ead299806ee78ba7bf5d9b9429f3932b78873447cb96fe13eda4.py)
<!--/codeinclude-->
