# this_file: Scripts/Kerning/Same Kerning Groups.py
# SPDX-License-Identifier: Apache-2.0
"""Open a fresh proof of the first selected glyph's left and right group peers.

Select a glyph in a Font or Glyph window and run this command. The first proof
row contains that first selected glyph. Labelled L: and R: rows contain all other
members of each corresponding visual-side kerning group, in font order. No selected layer or later selected parent is resolved. Only sides present on the
current glyph are queried for peers. Current
master class membership is used independently on each side. The current glyph
is excluded by identity; unencoded peers and repeated names stay explicit.

The proof keeps the original literal labels, spacing, blank-row policy and final
newline. Empty or singleton groups produce the original No Kerning Groups
message when neither side has peers. No selection produces Script Error.
Multiple distinct applicable groups on one side produce Ambiguous Kerning Groups
before opening a tab; nonkerning groups do not participate.
Existing App fresh-tab safeguards check the source font/master and preserve
activation flags; failures can leave a new tab and are reported without replacing
the existing tab. No font data, selection, preferences, history or Output is edited.

Independent implementation of Reza Bohloul's Same Kerning Groups.py workflow.
The inspected source has no licence declaration; its body is not redistributed.
See NOTICE and additional-tools.json. Requires Fly and App0.2.82.dev0.
Native tab/cursor/workspace and complete font/cache preservation remain pending.
"""


def main() -> object | None:
    """Run the complete named-glyph proof action through the shared App API."""
    from fly.ap.kerning_group_proof import run

    return run()


if __name__ == "__main__":
    main()
