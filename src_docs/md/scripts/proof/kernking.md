---
this_file: src_docs/md/scripts/proof/kernking.md
tags: ["Proof"]
categories: ["Proof"]
---

# KernKing

Open the complete KernKing kerning proof in 2 new FontLab Glyph tab(s).

Open a font and run this Proof command. Use the native nonmodal Glyph editor to
inspect spacing and kerning. Existing tabs remain. KernKing creates lowercase
first, then mixed case; the other commands create one tab. Every original word,
Unicode character, repeated space, slash-name escape and blank line is retained.
No missing character is filtered or replaced by this script. Native /quoteright
and /germandbls names stay names; doubled slash requests a literal slash.

Fly loads the shared App implementation. Complete resources load before native
work. Font and current master are captured once and checked before each tab.
A switched source or expired preflight refuses; later-tab failure can leave an
earlier new tab. The native creation call is not preemptible and UI rollback is
not claimed. Shared ownership disconnects/deletes senders and restores original
shape activation. No font geometry, kerning, history, preference or Output writer
is called. The source's undefined Font global is repaired by explicit lookup;
its Output clearing/printing is omitted to preserve the user's existing Output.

Requires App>=0.2.149.dev0 and Fly with FontLab Python3.11. Source/artifact tests
do not establish actual tab rendering, missing-name behavior or full-font/
workspace/history preservation; final native qualification remains pending.
Adapted from Pedro Arilla's Apache-2.0 Kerning/KernKing.py. Complete original and
proof-text credits, resource hashes and licence are in NOTICE/additional-tools.json.

Run **Proof > KernKing** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/1346a957d4059a3c713bee361989f7eb15f91feb77943cf971ec38fdceb8051d.py)
<!--/codeinclude-->
