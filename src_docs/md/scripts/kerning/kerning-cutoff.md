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

Requires Fontlabapp >=0.2.132.dev0 and Fly in FontLab9 Python3.11. The shared
writer refuses stale fonts/masters/classes/pairs, fractional source history and
invalid save ranges before mutation. On a native failure, use Undo and inspect
all masters. Final native full-font/history/save/reopen qualification is pending.

Independent implementation of Science Gothic SG-Font-Kerning-Cutoff.py v1.1,
Vassil Kateliev and Karandash Type Foundry (2025). Its source has no declared
licence; no original body is copied. Exact source attribution is in NOTICE.

Run **Kerning > Kerning Cutoff** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/6f0ca16a2cdf2822fce5298f9d53d7f574e73ee934e76909deb3b4a600758d37.py)
<!--/codeinclude-->
