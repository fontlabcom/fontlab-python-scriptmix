# this_file: Scripts/Proof/KernSym.py
# SPDX-License-Identifier: Apache-2.0
"""Open the complete KernSym kerning proof in 1 new FontLab Glyph tab(s).

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

Requires App>=0.2.149.dev0 and Fly with FontLab Python3.11.
Adapted from Pedro Arilla's Apache-2.0 Kerning/KernSym.py. Complete original and
proof-text credits, resource hashes and licence are in NOTICE/additional-tools.json.
"""


def main() -> None:
    """Open every source-defined proof tab through Fly and shared App ownership."""
    from fly.ap.kerning_proofs import run

    run('kernsym')


if __name__ == "__main__":
    main()
