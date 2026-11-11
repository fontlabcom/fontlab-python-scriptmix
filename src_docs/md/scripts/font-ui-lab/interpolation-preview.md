---
this_file: src_docs/md/scripts/font-ui-lab/interpolation-preview.md
tags: ["Font UI Lab"]
categories: ["Font UI Lab"]
---

# Interpolation Preview

Inspect a read-only interpolation preview at a designspace location.

What: Designspace location controls drive the existing two-master linear outline
preview. Choose a glyph and location to inspect the result; unsupported source
configurations and incompatible outlines are reported instead of being changed.

Use: Open a FontLab font and run this tool. The shared show(font, parent=None)
entry captures that font once; switching the current document does not retarget
the window. Close the window to release its owned controls and callbacks.

Safety: This is an inspection workflow. It never applies interpolation, creates
an instance, edits or saves the font, or switches its master or selection.
The existing preview's two-master linear scope is not a general multi-axis
variation model. Native FontLab rendering and complete font/history/cache
preservation remain separate qualification checks.

Run **Font UI Lab > Interpolation Preview** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `9e761eae1faaee19eddaeb896f7b0c13a55aa596d3752d19069643686cec09fa`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Font%20UI%20Lab/Interpolation%20Preview.py)
