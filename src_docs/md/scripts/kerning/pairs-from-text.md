---
this_file: src_docs/md/scripts/kerning/pairs-from-text.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Pairs From Text

Type a word, see each adjacent pair's kerning on every master, and set the ones you tick.

Pairs are taken inside words (spaces separate words; /glyphname tokens work too). The table
shows what FontLab applies now on each master, marking values that come from a class pair.
Set or Add writes explicit glyph pairs for the ticked rows on the chosen masters; one Apply is
one Undo step.

Run **Kerning > Pairs From Text** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/813044df6b23eff64ee02a3e7fda6d3501002c55770578e04684e42eae105495.py)
<!--/codeinclude-->
