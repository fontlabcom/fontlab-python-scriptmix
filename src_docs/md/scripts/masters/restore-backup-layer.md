---
this_file: src_docs/md/scripts/masters/restore-backup-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Restore Backup Layer

Launch the preserved Restore Backup Layer sample.

Purpose: The preserved sample describes this task:
Restore a backup layer (such as "Regular backup") into the master it was
taken from.

Setup: Use FontLab 9 with Python 3.11, fontlab-fly and fontlab-fontlabapp.
Keep Scripts and rescued together in this repository layout. Read the source
below for its controls, selection requirements and any resource dependencies.
Open a disposable copy of a font; select the glyphs needed by the sample.

Use: Run Masters > Restore Backup Layer in the Scripts menu.
Review its preview and controls before applying any font changes.

Result: This launcher asks App to run the exact preserved sample. Its native
compatibility is pending; a window or successful dispatch alone does not prove
correct edits, Undo, saved output or cleanup. Check those results separately.
Source: rescued/samples/masters_restore_backup.py

Run **Masters > Restore Backup Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/569bb013688a5e456270862a389bad8ef8aeabc030c209bf569ea42bb3661b87.py)
<!--/codeinclude-->
