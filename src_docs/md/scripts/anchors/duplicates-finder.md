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
Requires Fly and App 0.2.102.dev0. Native PythonQt/full-font, genuine
Undo/Redo, dirty state, saved/reopened preservation and lifetime remain pending.

Run **Anchors > Duplicates Finder** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c853e3e80d446f333074e1dd7fd3214f3db690fc22aec86c41fbfb958e5931b7.py)
<!--/codeinclude-->
