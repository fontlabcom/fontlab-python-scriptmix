---
this_file: src_docs/md/scripts/masters/duplicate-current-layer.md
tags: ["Masters"]
categories: ["Masters"]
---

# Duplicate Current Layer

Back up the current master layer or all master layers of selected glyphs.

What it does:
    Choose current or all masters, a custom suffix and inspect existing
    backups.
    Names use <master> backup <suffix>, with (2), (3) on collisions.
    Names with @, # or |temp|, exact master names, and names that Restore
    would read as another master are refused.

How it works:
    The non-modal panel uses fly.ap.selection_panel. Copies keep repaired shape
    and node metadata (fl#8516, fl#8538). The shown layer stays active. Each
    Apply
    is recorded as one Undo step through fly.ap.history and read back. Auto
    owners and bases are listed and kept. Apply discloses queued ids and their
    possible date changes.

Why this design:
    FontLab's Layers panel duplicates one layer. This adds all-master backup,
    custom naming and an inventory before risky edits.

How to use:
    Select glyphs, open the panel, choose the scope and suffix, then Back up.

Benefit:
    Keep copies of several masters with one action before redesigning them.

Credit:
    Independent rewrite after Pedro Arilla's "Duplicate current layer"
    (Apache-2.0), extended from the author's own FontLab sample
    masters_backup_layer.py, Apache-2.0.

Run **Masters > Duplicate Current Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6c9027e0c81f1528bbac28c4d5987b52db305f4e51cd011bbec597c560621f93.py)
<!--/codeinclude-->
