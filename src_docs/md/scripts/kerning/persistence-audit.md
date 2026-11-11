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

## Source identity

SHA256: `c8f49143594412c52d77f811147a441dcf855bb49c5897c560533480d1653d87`

[Python source at `8852124d9fe2`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/8852124d9fe2b69cf663e1c6db8d6db4bf5e8454/Scripts/Kerning/Persistence%20Audit.py)
