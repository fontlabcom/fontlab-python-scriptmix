---
this_file: src_docs/md/scripts/kerning/kerning-cutoff.md
tags: ["Kerning"]
categories: ["Kerning"]
---

# Kerning Cutoff

Clamp every master's explicit kerning to the inclusive range -250 to 100.

Open a font and run this immediate action. Glyph pairs, class pairs and both
mixed exception kinds retain their identities. Existing zero and absent pairs
stay distinct. Every master reports its changed count without clearing Output.
Any changed master enters one complete Undo batch, including earlier masters
when the last master has no edits. No options or current-master subset apply.

Requires Fontlabapp >=1.2.0 and Fly in FontLab9 Python3.11. The shared
writer refuses stale fonts/masters/classes/pairs, fractional source history and
invalid save ranges before mutation. On a native failure, use Undo and inspect
all masters.

Independent implementation of Science Gothic SG-Font-Kerning-Cutoff.py v1.1,
Vassil Kateliev and Karandash Type Foundry (2025). Its source has no declared
licence; no original body is copied. Exact source attribution is in NOTICE.

Run **Kerning > Kerning Cutoff** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `a0b0e2fbe7c2f6c7cb82c63f8406a0b6ac926f627a1aaf53b24ce0ddcaeefc5d`

[Python source at `3dc87d8a0e3d`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/3dc87d8a0e3dec803dc9255436da39eb19abefb2/Scripts/Kerning/Kerning%20Cutoff.py)
