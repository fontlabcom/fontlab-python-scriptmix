---
this_file: src_docs/md/scripts/font-info/font-identity.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Font Identity

Font Identity: Inspect names and credits, prepare version changes and create a trial font using the retained task controls. Font-level identity fields belong to the captured font; a version change does not rename glyphs or regenerate feature code. Trial font creation retains its own destination and export checks.

Tabs: Bump Font Version; Names and Credits; Trial Font Maker.

How to use: Open the font and choose this tool from Font Info. Choose the
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

Run **Font Info > Font Identity** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `69e44cd93064aedf7c375412f118ea02c7e434531df379412fcd79d076534285`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Font%20Info/Font%20Identity.py)
