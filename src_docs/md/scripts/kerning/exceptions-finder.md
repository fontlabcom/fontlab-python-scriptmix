---
this_file: src_docs/md/scripts/kerning/exceptions-finder.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Exceptions Finder

Find kerning exceptions: pairs that override a class pair, and remove the ones you tick.

What it does:
    An exception is a pair whose glyph side belongs to a kerning class that already has a pair
    with the same partner (A V overriding @A V). Exceptions with the same value as the class pair
    are redundant and safe to delete; the others are deliberate overrides worth a second look.
    Tick rows (or "Tick redundant") and Remove; one Undo step for all masters.

How it works:
    Compare explicit exceptions with applicable class pairs on the chosen
    masters. Mark equal-value rows as redundant and stage deletion only for
    checked rows.

Why this design:
    An unequal exception can be intentional; listing it beside the class
    baseline supports review before removal.

How to use:
    Run Kerning > Exceptions Finder. Choose the master scope, inspect override
    values and use Tick redundant if suitable. Press Remove for the checked
    rows only.

Benefit:
    Remove a reviewed exception subset in one recorded Undo step without
    rewriting class pairs.

Run **Kerning > Exceptions Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `897c73e3d1cb15cbb67e29663782a279b2232c869933b8909aed7d1772f06387`

[Python source at `83142fd0a0ef`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/83142fd0a0efad5aec2ed5ca10642beb376d3f0f/Scripts/Kerning/Exceptions%20Finder.py)
