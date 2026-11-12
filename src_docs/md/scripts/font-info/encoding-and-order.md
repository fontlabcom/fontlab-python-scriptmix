---
this_file: src_docs/md/scripts/font-info/encoding-and-order.md
tags: ["Font Info"]
categories: ["Font Info"]
---

# Encoding and Order

Encoding and Order: Inspect and export glyph order, paste an order encoding and inspect Unicode ranges and codepages. The order preview and encoding inputs are distinct tasks: exporting a report does not itself reorder the font. Review the exact names and order in the selected tab before requesting a write.

Tabs: Glyph Order Preview and Export; Paste Glyph Order Encoding; Unicode Ranges and Codepages.

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

Run **Font Info > Encoding and Order** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `ae73b8906df153638fc397aefe02d8e3c3016b32abf6e4e0a421a7ccfa930a6f`

[Python source at `e537cab9364b`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/e537cab9364bf34af3d36190d5c471795140f722/Scripts/Font%20Info/Encoding%20and%20Order.py)
