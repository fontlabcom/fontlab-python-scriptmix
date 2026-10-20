---
this_file: src_docs/md/scripts/components/compatibility.md
tags: ["Components"]
categories: ["Components"]
---

# Compatibility

Compare component names and order across masters; glyphs that differ cannot interpolate their components.

One row per composite glyph, one column per master. Masters whose component list
differs from the first master are shown in red, and mismatching glyphs are listed
first. Double-click a row to select the glyph in the Font window. Nothing is changed.

Run **Components > Compatibility** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/df701b5ebd9fc0605bf8553d40b8f29a0fc00f904e5bdce43a06d34be37feb0e.py)
<!--/codeinclude-->
