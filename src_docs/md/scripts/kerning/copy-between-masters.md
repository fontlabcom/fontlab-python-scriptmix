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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/caa0a564eb7e2536afad16b33382f5600a62b86cd310a39ba0c8991779aebe00.py)
<!--/codeinclude-->
