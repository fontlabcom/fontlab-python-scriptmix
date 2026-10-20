---
this_file: src_docs/md/scripts/names/suffix-tool.md
tags: ["Names"]
categories: ["Names"]
---

# Suffix Tool

Launch the preserved Suffix Tool sample.

Purpose: The preserved sample describes this task:
Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt…) on the
selected glyphs.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Names > Suffix Tool in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/names_suffix_tool.py

Run **Names > Suffix Tool** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/37793af5b7973a2e75f9babe6f4d08f2ff8abacc8dd180fb5c327a994990f54f.py)
<!--/codeinclude-->
