---
this_file: src_docs/md/scripts/features/feature-explorer.md
tags: ["Features"]
categories: ["Features"]
---

# Feature Explorer

Feature Explorer: Compare alternate glyphs, find ligature names and inspect suffix families. These reports use glyph names and source relationships. Naming matches identify candidates; they do not prove that an OpenType lookup selects a glyph during shaping. Reports preserve the original master and source scopes.

Tabs: Alternate Preview; Ligature Finder; Suffix Report.

How to use: Open the font and choose this tool from Features. Choose the
named tab for the task, enter its inputs and inspect its result before using
an action. Refresh reads the tool's source context. Preview Changes prepares
the selected task for review; Apply Changes is available for supported edits.
Read-only tasks keep their inspection, copy or export actions separate from
font changes. A refusal explains which input or context must be corrected.

The window groups the original task controls with a shared preview and resizeable
layout. Switching fonts elsewhere is not a request to transfer an existing
plan to that font. Recheck the selected glyphs, source, target and layer before
applying work, and refresh when the source changes. Close ends the tool session;
it does not save the borrowed font. Source credits and help appear in About.
Requires FontLab 9 and matching Fly/App packages containing this studio.

Run **Features > Feature Explorer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `9ee4b890d9855fd360e237e16d21d014858915e0b40966333400a5ab467bb8fa`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Features/Feature%20Explorer.py)
