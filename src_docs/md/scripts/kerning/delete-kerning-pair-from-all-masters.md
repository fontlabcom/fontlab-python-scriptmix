---
this_file: src_docs/md/scripts/kerning/delete-kerning-pair-from-all-masters.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Delete Kerning Pair From All Masters

Delete the selected adjacent kerning pairs on every master.

What: Remove each selected pair's class kerning, or glyph kerning when no
class exists, from all masters. Existing exceptions remain separate records.
How: Capture ordered Glyph-window slots. Resolve side-specific groups for
each master. Preflight the complete edit through the shared kerning writer.
Why: One shortcut clears a whole selected sequence across all masters;
The Metrics bar Remove pair command affects only the current pair/master.
Pair Editor requires separate cell edits. Ambiguous groups refuse the action.
Use: Select two or more adjacent glyphs in one Glyph-window text block, then
run. Capture includes selected OR active slots; an active slot outside the
selection must also be adjacent. A lone active slot is refused. Selection
replaces the Glyphs text-cursor fallback. No dialog is needed.
Benefit: Remove class spacing consistently without changing unrelated pairs.
Each changing action is recorded as one Undo step by the shared kerning writer.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Kerning/Delete Kerning Pair From All Masters.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.

Run **Kerning > Delete Kerning Pair From All Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `0f252998a0e1e32786fd173e80a9807cf1e33f2d15915942004f7fdc6627f75a`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Kerning/Delete%20Kerning%20Pair%20From%20All%20Masters.py)
