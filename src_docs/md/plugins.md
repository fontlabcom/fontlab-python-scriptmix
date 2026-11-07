---
this_file: src_docs/md/plugins.md
---

# Documentation build

ProperDocs 1.6.7, MkDocs 1.6.1, MaterialX 10.1.8 and PyMdown Extensions 11.0.1 use the exact 31-package hash lock in `src_docs/requirements.txt`. The light fltheme26 menu, footer and local search share the qualified site layout.

Every main commit builds the complete catalogue. A second job checks the immutable generated commit, source parent, source epoch and every output file before an eligible public Pages request. Menu source snapshots and frozen provenance remain separate from the published pages.
