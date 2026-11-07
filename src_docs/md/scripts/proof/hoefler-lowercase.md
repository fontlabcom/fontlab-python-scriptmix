---
this_file: src_docs/md/scripts/proof/hoefler-lowercase.md
tags: ["Proof"]
categories: ["Proof"]
---

# Hoefler Lowercase

Open the complete Hoefler Lowercase kerning proof in 1 new FontLab Glyph tab(s).

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

Requires App>=1.2.0 and Fly with FontLab Python3.11.
Adapted from Pedro Arilla's Apache-2.0 Kerning/Hoefler Lowercase.py. Complete original and
proof-text credits, resource hashes and licence are in NOTICE/additional-tools.json.

Run **Proof > Hoefler Lowercase** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `b405f57793af421b7ba3f19d2c94096a6db0901de46940423cb0e4a0ca4f7a21`

[Python source at `c2b34988556c`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/c2b34988556c9214a67f800f68565b7a32df832a/Scripts/Proof/Hoefler%20Lowercase.py)
