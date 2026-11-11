---
this_file: src_docs/md/scripts/kerning/compare-masters.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Compare Masters

Line up every kerning pair across all masters and flag the ones that look inconsistent.

What it does:
    Each row is one pair (glyph or @class sides) with its value on every master; a pair missing
    on a master shows a dash. Rows are flagged when the sign flips between masters, when a pair
    exists on some masters only, or when neighbouring masters differ by more than the jump
    threshold. Tick "Only flagged" to proof just those. Nothing is edited.

How it works:
    Union explicit pair keys across masters, preserve missing values as absent
    cells and flag sign changes, partial presence or jumps above the chosen
    threshold.

Why this design:
    A missing pair differs from an explicit zero; separate display values help
    identify the type of inconsistency.

How to use:
    Run Kerning > Compare Masters. Set the jump threshold, inspect reasons and
    use Only flagged to reduce the table to candidates for manual proofing.

Benefit:
    Review family kerning differences without filling absent pairs or changing
    values.

Run **Kerning > Compare Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `c1b547cc45e9dfddae55c4021d184e6f5109af2556b7f17faa4e255d5ad5ada2`

[Python source at `75235791e388`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/75235791e3880a7bc761f4bbc9c5dccc08813705/Scripts/Kerning/Compare%20Masters.py)
