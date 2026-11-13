---
this_file: src_docs/md/scripts/names/character-consistency.md
tags: ["Names"]
categories: ["Names"]
---

# Character Consistency

Character Consistency: Inspect case pairs, compare character sets between fonts and review style-link information. The comparison uses the selected source and target context, not an assumption that every open font has the same encoding. The Style Linker retains its explicit limits on unsupported instance writes.

Tabs: Case Pairs; Character Set Compare; Style Linker.

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

Run **Names > Character Consistency** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `975ec5ce540bc6c4cd15745ae514011c560c72a3476e4b42f9f3f06c8b5801ff`

[Python source at `3bf7b47dd22f`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3bf7b47dd22f44334af5f83d5c2becb59ce3874f/Scripts/Names/Character%20Consistency.py)
