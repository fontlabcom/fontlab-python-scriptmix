---
this_file: src_docs/md/scripts/names/glyph-identity.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Identity

Glyph Identity: Find and replace glyph names, add or remove suffixes, derive Unicode values from names and inspect duplicate Unicode assignments. Rename and encoding are separate operations. Duplicate groups retain individual glyph/codepoint choices, so inspect the proposed keeper and checked assignments before removing codes.

Tabs: Batch Rename; Duplicate Unicodes; Suffix Tool; Unicode From Names.

How to use: Open the font and choose this tool from Names. Choose the
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

Run **Names > Glyph Identity** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `65f31d0cd8d443ce7245dc586adf9578be1f6bcf3eee22dd068b3f1c9042d896`

[Python source at `e537cab9364b`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/e537cab9364bf34af3d36190d5c471795140f722/Scripts/Names/Glyph%20Identity.py)
