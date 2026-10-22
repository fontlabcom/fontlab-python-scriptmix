---
this_file: src_docs/md/scripts/kerning/persistence-audit.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Persistence Audit

Inspect explicit kerning pairs against FontLab's measured VFJ load limit.

What it does:
    Open a font and choose the current master or all masters, then filter the audit
    rows. Values outside twice the UPM are reported as persistence risks. This
    read-only check makes no font changes and is not a universal persistence proof.

How it works:
    Use the shared App audit to read explicit pairs on the chosen master
    scope. Compare values with the measured twice-UPM VFJ loading boundary.

Why this design:
    The measured numeric boundary identifies a persistence risk; passing it
    cannot prove every aspect of a saved font.

How to use:
    Open a font and run Kerning > Persistence Audit. Choose current or all
    masters, filter the rows and review the reported values before deciding
    which pairs need correction.

Benefit:
    Locate risky explicit kerning values without changing pairs or claiming a
    complete save/reopen test.

Run **Kerning > Persistence Audit** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5c248ae70e78971f8f519ecb46f8546814c53165f770a7ceba5100c8328d8d45.py)
<!--/codeinclude-->
