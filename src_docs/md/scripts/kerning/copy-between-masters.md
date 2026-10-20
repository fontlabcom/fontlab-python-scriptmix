---
this_file: src_docs/md/scripts/kerning/copy-between-masters.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Copy Between Masters

Copy the kerning of one master to other masters, optionally scaled.

Start a new master's kerning from an existing one, or push corrections from the Regular to its
neighbours. "Replace" makes the targets identical to the source, "Add missing" only adds pairs
the target lacks, "Overwrite matching" updates pairs both have. The summary shows, per target,
how many pairs are added, changed and removed. One Apply is one Undo step for all targets.

Run **Kerning > Copy Between Masters** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/fb9bb91736945a3cf1fb968188bacbfdbe6ae49e0696872de126b69920c42861.py)
<!--/codeinclude-->
