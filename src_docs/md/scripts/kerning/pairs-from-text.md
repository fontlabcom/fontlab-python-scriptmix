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

## Source identity

SHA256: `0dbe9a5444a761f393baee12d98bb9ccb44509b71cb55976e71ff0435441ffcc`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Kerning/Pairs%20From%20Text.py)
