---
this_file: src_docs/md/scripts/guides/clear-glyph-guides.md
tags: ["Guides"]
categories: ["Guides"]
---

# Clear Glyph Guides

Remove matching glyph guides while preserving hints and retained guides.

What it does:
    Select glyphs. Choose current or all masters, direction and name text. Inspect
    every matching guide, then use Remove. Retained native colour, tags and geometry
    are kept. Batches with unsafe automatic dependants are refused before history.
    Changed font, selection or source clears the plan; Close releases owned signals.

How it works:
    Filter each selected layer's glyph guides by direction and name text. Plan
    removals separately from retained native guides, preserving hints and
    unrelated properties.

Why this design:
    A removal preview exposes exactly which guides match before a broad
    master-scope operation starts.

How to use:
    Select glyphs and run Guides > Clear Glyph Guides. Choose master scope and
    filters, inspect matching guide rows and press Remove. Refresh the plan
    after source changes.

Benefit:
    Remove a targeted guide subset; the action is recorded as one Undo step.

Run **Guides > Clear Glyph Guides** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d5903492b3438aef20b1e0649d86dd25c3f553aa2cd9bb00819629c41031a86a.py)
<!--/codeinclude-->
