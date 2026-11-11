---
this_file: src_docs/md/scripts/kerning/copy-between-masters.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Copy Between Masters

Copy the kerning of one master to other masters, optionally scaled.

What it does:
    Start a new master's kerning from an existing one, or push corrections from the Regular to its
    neighbours. "Replace" makes the targets identical to the source, "Add missing" only adds pairs
    the target lacks, "Overwrite matching" updates pairs both have. The summary shows, per target,
    how many pairs are added, changed and removed. One Apply is one Undo step for all targets.

How it works:
    Stage source pairs and target differences under Replace, Add missing or
    Overwrite matching, with optional percentage scaling. Commit the complete
    checked target batch.

Why this design:
    The per-target added/changed/removed summary makes destructive replacement
    visible before the write begins.

How to use:
    Run Kerning > Copy Between Masters. Choose source and targets, set mode
    and scale, inspect every target summary and press Apply.

Benefit:
    Seed or update family kerning with explicit scope; Apply is recorded as
    one Undo step.

Run **Kerning > Copy Between Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `8a1d271a7e9d75dee66e1e6756643632960be43ca4a8f20f46acc4aaea999d07`

[Python source at `cb3a95057641`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/cb3a95057641f3b2382a887172fab524dbc4901a/Scripts/Kerning/Copy%20Between%20Masters.py)
