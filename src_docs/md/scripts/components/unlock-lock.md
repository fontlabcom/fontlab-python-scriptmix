---
this_file: src_docs/md/scripts/components/unlock-lock.md
tags: ["Components"]
categories: ["Components"]
---

# Unlock Lock

Launch the preserved Unlock Lock sample.

Purpose: The preserved sample describes this task:
Show which components of the selected glyphs are locked, and lock or unlock
them per master.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Components > Unlock Lock in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/components_unlock_lock.py

Run **Components > Unlock Lock** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ddb118f58eb0dbc921caf72bdf506c7677ee9bbfdd6233db84b90b8b5deb714e.py)
<!--/codeinclude-->
