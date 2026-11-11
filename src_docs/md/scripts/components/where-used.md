---
this_file: src_docs/md/scripts/components/where-used.md
tags: ["Components"]
categories: ["Components"]
---

# Where Used

Find every glyph that uses a given glyph as a component, on any master.

What it does:
    Type a glyph name (the field completes as you type). The table lists the composites,
    the masters where the component appears and whether those layers are auto layers.
    Click a row to select that glyph in the Font window; "Select all" selects them all.

How it works:
    Search component references on all masters through App and list the owning
    composite glyphs. Keep the captured source guarded when selecting results.

Why this design:
    Reverse lookup shows which composites need review after a base glyph
    changes, without rewriting those composites.

How to use:
    Run Components > Where Used. Enter a base glyph name, inspect the
    composites and master columns, then click a row or use Select all to
    select the results.

Benefit:
    Trace component use across masters while leaving references, transforms
    and outlines intact.

Run **Components > Where Used** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `e0f97c011212d6ccedae4c14c19e6d0ae16a3d5f375d729b63e531595d6472b3`

[Python source at `6064e3e08a50`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/6064e3e08a50137c10a3e1789855917be9874916/Scripts/Components/Where%20Used.py)
