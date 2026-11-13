---
this_file: src_docs/md/scripts/names/glyph-browser.md
tags: ["Names"]
categories: ["Names"]
---

# Glyph Browser

Glyph Browser: Inspect character information, search glyph names, browse the metadata tree and use glyph-name completion. These tabs help locate existing glyphs and inspect their stored metadata. A match does not rename or encode a glyph. Keep the glyph preview and its layer context in view when comparing results.

Tabs: Character Info; Glyph Finder; Glyph Metadata Tree; Glyph Name Completion.

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

Run **Names > Glyph Browser** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `18577a4e525e5d6fc6beaf86aa86f7adf444b79f26fa6a6e4dd8f449f913d3b6`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Names/Glyph%20Browser.py)
