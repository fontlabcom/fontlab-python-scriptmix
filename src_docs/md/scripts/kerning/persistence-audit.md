---
this_file: src_docs/md/scripts/kerning/persistence-audit.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Persistence Audit

Inspect explicit kerning pairs against FontLab's measured VFJ load limit.

Open a font and choose the current master or all masters, then filter the audit
rows. Values outside twice the UPM are reported as persistence risks. This
read-only check makes no font changes and is not a universal persistence proof.

Run **Kerning > Persistence Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/9c7aa64aab52cefe218a42fb1abed349861bb8b0beef910b898868caea3ba629.py)
<!--/codeinclude-->
