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

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ea6711552728cf4bc3a57dd3b67fa236e3e0dcd845e2519c530648423ea412c5.py)
<!--/codeinclude-->
