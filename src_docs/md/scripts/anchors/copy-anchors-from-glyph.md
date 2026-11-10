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

## Source identity

SHA256: `0965587509f7942c8b55b5a62b425ebffe162bdbcda7859a18c0fe86a1f62aab`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Anchors/Copy%20Anchors%20From%20Glyph.py)
