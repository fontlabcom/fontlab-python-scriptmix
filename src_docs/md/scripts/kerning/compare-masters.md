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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/78be84906a2c0c02e96236cc39ee21b790422c1803f84b69baf508eae33706fb.py)
<!--/codeinclude-->
