---
this_file: src_docs/md/scripts/components/decompose-named-components.md
tags: ["Components"]
categories: ["Components"]
---

# Decompose Named Components

Decompose a named component subtree across selected glyphs and masters.

What: Replace occurrences of one source glyph with independent outlines.
Flatten nested components inside each matched occurrence. Keep other direct
components, including those with the same names as nested parts.

How: Preview matching occurrences on all masters by default. Copy each
matched subtree only on Apply, before history starts, through the shared
component writer. Preview reads source-layer counts without native copies.
It composes the native transforms and repairs raw node connection flags,
element names and notes. Keep source glyphs, anchors and metrics unchanged.
Some per-node and per-contour properties are outside the shared copy helper.
Each action is recorded as one Undo step. Component removal uses retained
history objects; removed-component history depends on FontLab (fl#7641).

Why: Glyph > Decompose works on selected components or a whole layer. This
tool adds a source-name filter, all-master preview and recursive subtree
decomposition across several selected glyphs. A refused glyph or layer is
listed as kept; other eligible occurrences can still change.
Decompose Serif Components uses a fixed Serif prefix and removes one level;
this tool uses an exact source name and flattens its complete subtree.

Use: Select composite glyphs. Run this script. Enter the exact source glyph
name. Review the preview, then press Decompose. Use Reload selection after
changing the selection. The panel stays open for another source name.

Benefit: Make a repeated part independent without decomposing its siblings.
Automatic layers, their owners and their dependent bases are kept. Locked
layers, missing bases, cyclic components and unsupported transforms are kept.
Components with an interpolated # location are kept: the copy helper needs
a plain source layer. Reset their locations before decomposing them here.

Credit: Independent behaviour rewrite after Fernando Díaz, Reset Type Studio,
Glyphs-Scripts/Components/Decompose Specific Components (all masters).py.
Repository: https://github.com/Reset-Type-Studio/Glyphs-Scripts .
Source licence: Apache-2.0, declared in README.md; no LICENSE file.
Copyright 2025 Fernando Díaz & Reset Type Studio. No source code was copied.
Unlike the source's second name scan, nested parts are flattened only inside
matched occurrences, so unrelated sibling components stay linked.

Run **Components > Decompose Named Components** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/bff227723026aa6bf5a43d31296b30954e90222ba1fae69d623cb842c6ea0d5e.py)
<!--/codeinclude-->
