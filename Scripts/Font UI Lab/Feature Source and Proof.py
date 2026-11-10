# this_file: Scripts/Font UI Lab/Feature Source and Proof.py
# SPDX-License-Identifier: Apache-2.0
"""Edit stored feature source and refresh an independent glyph proof.

What: Link feature source and the existing glyph sequence for one captured font.
Use: Edit a block, choose explicit proof text or /glyph names, then Apply source.
Accepted Apply refreshes the proof once. Refresh proof retries only the view.
Feature source is stored, not compiled. Unicode and kerning placement does not
apply OpenType substitutions or positioning; unchanged positions are expected.

Safety: Use an owned test font. Active-font changes do not retarget this window.
External changes retain dirty drafts with a warning; explicit Apply can overwrite
newer source. Revert reloads stored source. Original paragraph separators remain
inspect-only; unsupported input is refused. Closing never saves or closes the
borrowed font. Native history, painting and saved-font acceptance remain separate.
"""


def main():
    """Capture the current borrowed font once and return the retained owner."""
    from fly.ap.fontui.feature_proof import show
    from fly.fp.world import FontWorld

    font = FontWorld().CurrentFont()
    return show(None if font is None else font)


if __name__ == "__main__":
    main()
