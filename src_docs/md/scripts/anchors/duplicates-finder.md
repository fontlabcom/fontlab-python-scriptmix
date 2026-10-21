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
Requires Fly and reviewed App 0.2.102.dev0. Native PythonQt/full-font, genuine
Undo/Redo, dirty state, saved/reopened preservation and lifetime remain pending.

Run **Anchors > Duplicates Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d56f720b404d6020413607143fccd199f2576e04b86e87528a90ec8c63274832.py)
<!--/codeinclude-->
