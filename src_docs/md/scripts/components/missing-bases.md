---
this_file: src_docs/md/scripts/components/missing-bases.md
tags: ["Components"]
categories: ["Components"]
---

# Missing Bases

Find components that point to glyphs which do not exist, or to a base glyph without that master.

What it does:
    Such components draw nothing and break exports. The tree groups the problems by
    the missing base glyph; expand a group to see the composites and masters affected.
    Select affected glyphs puts them in the Font window selection. Nothing is changed.

How it works:
    Read component references through App and group missing glyphs or missing
    master layers by base name. Retain the affected owners for guarded
    selection.

Why this design:
    A missing base can make several composite drawings disappear, so grouping
    by base helps expose the common cause.

How to use:
    Run Components > Missing Bases. Expand a missing-base group, inspect the
    composite and master entries and use Select affected glyphs to locate the
    owners.

Benefit:
    Locate broken component dependencies without adding placeholder bases or
    changing references.

Run **Components > Missing Bases** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `1fccc9cd53cef65a37cfbbb83055135b5a69225162359ce01d0c37d86ba6c3fa`

[Python source at `8e06999ef5a2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8e06999ef5a237c79364b4efd0758bf8fbd5dee8/Scripts/Components/Missing%20Bases.py)
