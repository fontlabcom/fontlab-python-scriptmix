---
this_file: src_docs/md/scripts/anchors/duplicates-finder.md
tags: ["Anchors"]
categories: ["Anchors"]
---

# Duplicates Finder

Find and remove duplicate anchors across the whole font or opening selection.

Both scopes scan every master. Keep the first anchor in layer order; numbered
copies count only when their immediate stem exists. Coincident groups use
rounded points and are kept unless explicitly enabled. Automatic layers are
reported and kept. Fix applies every pending finding, independent of table rows.

The complete candidate uses direct pin removals and one final layer/glyph
notification. Unsafe automatic dependants and changed sources refuse before
history. A partial native failure is diagnosed for Edit > Undo; pins are never
reconstructed as rollback. Refresh keeps the original opening selection.
Requires Fly and App 1.2.0. Native PythonQt/full-font, genuine
Undo/Redo, dirty state, saved/reopened preservation and lifetime remain pending.

Run **Anchors > Duplicates Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `ef2073682b849a48b338861fe47978e705cfa037667b7d378a52afd502766937`

[Python source at `b52710a04ed5`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/b52710a04ed5e9e3759b7086daeb0b09ec65b6f3/Scripts/Anchors/Duplicates%20Finder.py)
