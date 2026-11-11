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

## Source identity

SHA256: `2b080c061236321280bbbbee21dee8a5cbcfafe4bc50861acc3f4a1d5c651bd2`

[Python source at `4bab81718f97`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/4bab81718f976cbdb0cf33c249fc85b5df530a9a/Scripts/Components/Decompose%20Serif%20Components.py)
