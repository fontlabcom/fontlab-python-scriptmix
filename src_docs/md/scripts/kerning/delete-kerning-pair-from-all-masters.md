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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a4463e00306363129bd99c6474168d11bb9fb7dc7f6f5d2dcc1f25c7c95c0aed.py)
<!--/codeinclude-->
