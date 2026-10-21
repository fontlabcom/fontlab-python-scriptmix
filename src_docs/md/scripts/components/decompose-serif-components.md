---
this_file: src_docs/md/scripts/components/decompose-serif-components.md
tags: ["Components"]
categories: ["Components"]
---

# Decompose Serif Components

Decompose only components whose base name starts with Serif.

What: Replace matching components in selected glyphs on chosen masters.
How: Preview each replacement, then use the shared component writer. Nested
components remain components. Other components and own contours stay.
Why: A prefix filter keeps reusable letter parts while releasing serif parts.
Use: Select glyphs, run this tool, choose masters and press Decompose.
Benefit: One filtered batch is recorded as one Undo step. Other reusable parts
stay linked. Automatic layers and their bases are refused.

Independent behaviour rewrite after Pedro Arilla, glyphs-scripts,
Components/Decompose all serif components.py, Apache-2.0.
Repository: https://github.com/pedroarilla/glyphs-scripts . No source code copied.

Run **Components > Decompose Serif Components** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/8e5a9f4e44aa09903957d82ec43c25c60a4aa58699fad7327ebe0e898d4f9e2e.py)
<!--/codeinclude-->
