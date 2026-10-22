---
this_file: src_docs/md/scripts/kerning/pairs-from-text.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Pairs From Text

Type a word, see each adjacent pair's kerning on every master, and set the ones you tick.

What it does:
    Pairs are taken inside words (spaces separate words; /glyphname tokens work too). The table
    shows what FontLab applies now on each master, marking values that come from a class pair.
    Set or Add writes explicit glyph pairs for the ticked rows on the chosen masters; one Apply is
    one Undo step.

How it works:
    Parse adjacent glyph pairs inside words, resolve effective kerning on each
    master and stage Set or Add values only for checked rows.

Why this design:
    An effective class-pair value supplies the displayed baseline, while the
    requested write creates an explicit glyph pair.

How to use:
    Run Kerning > Pairs From Text. Enter text or slash-name tokens, tick
    pairs, choose masters and Set or Add, inspect the values and press Apply.

Benefit:
    Kern a specific proof-text batch; Apply is recorded as one Undo step.

Run **Kerning > Pairs From Text** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9739f2adade5329f5c913c82bf30fcce58dc102b2372a3ab87ab6eb291605f19.py)
<!--/codeinclude-->
