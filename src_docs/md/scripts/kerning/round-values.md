---
this_file: src_docs/md/scripts/kerning/round-values.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Round Values

Round kerning values to a step (5, 10 …) on one or all masters, previewing every change.

What it does:
    Rounded kerning is easier to read, compare and edit by hand, and interpolates to tidier
    instances. Halves round away from zero, as FontLab rounds. Pairs that round to 0 can be deleted
    instead of being kept as explicit zeros. One Apply is one Undo step for all masters.

How it works:
    Build a complete explicit-pair plan for current or all masters. Round
    values to the chosen step with halves away from zero and apply the
    selected zero-pair policy.

Why this design:
    Previewing zero deletions separately avoids treating an explicit zero pair
    as interchangeable with an absent pair.

How to use:
    Run Kerning > Round Values. Choose a step, master scope and zero-pair
    option. Review the old/new rows, then Apply to write the displayed batch.

Benefit:
    Make stored kerning values easier to inspect; Apply is recorded as one
    Undo step.

Run **Kerning > Round Values** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1855835ff8f6a270bac92c03d3fc85b1b179010e0a24d8677e1c3d4c9bcff774.py)
<!--/codeinclude-->
