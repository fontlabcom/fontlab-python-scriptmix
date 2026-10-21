# this_file: Scripts/Kerning/Kerning Cutoff.py
# SPDX-License-Identifier: Apache-2.0
"""Clamp every master's explicit kerning to the inclusive range -250 to 100.

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
"""


def main() -> dict[str, int]:
    """Run the complete all-master writer through the lazy public Fly facade."""
    from fly.ap.kerning_cutoff import run

    return run()


if __name__ == "__main__":
    main()
