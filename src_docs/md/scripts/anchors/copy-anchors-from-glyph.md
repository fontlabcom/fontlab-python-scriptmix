---
this_file: src_docs/md/scripts/anchors/copy-anchors-from-glyph.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Copy Anchors From Glyph

Copy a source glyph's anchors to selected glyphs, master by master.

What it does:
    Type a source name with fontwide completion; choose merge/replace, width scaling
    and current/all masters. Automatic layers are skipped. Unsafe automatic
    dependants and stale source previews refuse the complete write before history.
    One Copy is one native Undo. Close disconnects every owned callback.

How it works:
    Plan source anchors master by master through App. Apply merge or replace
    with optional width scaling; retain automatic layers and refuse unsafe or
    stale sources.

Why this design:
    A preview makes replacement and scaling decisions explicit before the
    selected target anchor sets change.

How to use:
    Select target glyphs and run Anchors > Copy Anchors From Glyph. Enter the
    source, choose scope and options, inspect the preview and press Copy.

Benefit:
    Reuse anchor placement across a selected set; Copy is recorded as one Undo
    step.

Run **Anchors > Copy Anchors From Glyph** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/3ab1b1965bc3c2a78632b8114e41ff8975070c449df096c51402c0ef44068877.py)
<!--/codeinclude-->
