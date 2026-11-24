---
this_file: src_docs/md/plugins.md
---

# Documentation build

The site uses fly-january 0.3.0 or later for the FontLab menu and footer, and MaterialX for English search. The Python 3.13 build pins ProperDocs 1.6.7, MkDocs 1.6.1, MaterialX 10.1.8 and PyMdown Extensions 11.0.1 in `src_docs/requirements.txt`.

Every main commit builds the complete catalogue. A second job checks the immutable generated commit, source parent, source epoch and every output file before an eligible public Pages request. Menu source snapshots and frozen provenance remain separate from the published pages.
