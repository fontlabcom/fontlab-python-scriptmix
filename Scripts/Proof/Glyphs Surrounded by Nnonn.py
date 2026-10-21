# this_file: Scripts/Proof/Glyphs Surrounded by Nnonn.py
# SPDX-License-Identifier: Apache-2.0
"""Open a new native Glyph tab with glyphs surrounded by nnonn.

Select glyphs in a Font window or occurrences in a Glyph window, then run this
Proof command. Keep their actual order and repeated editor occurrences. The
new tab uses the font's current master; source layer overrides are not copied.
The selected glyph name appears between each context name, or inside repeated
H, I, HHOHH or nnonn contexts, as indicated by the command. Between sequences
end with the selected glyph and two newlines per occurrence. Surround sequences
end with one final context. With no selection, Between opens an empty tab;
Surround opens its context alone. The original behavior is retained.

App builds all glyph-name rows before opening. Named native symbols retain
unencoded glyphs and oldstyle .osf names without slash-text or Unicode fallback.
No context is filtered or substituted when a name is missing; native missing-name
behavior still needs qualification. One deadline covers selected-layer capture,
generation, symbols and preflight. A changed source selection/font or invalid
input refuses the complete operation. A named-content writer can target only a
verified new active tab belonging to the captured source font. It never populates
an existing or foreign tab. Native failure can leave a new tab; no atomic UI
rollback is claimed. The owned native sender is disconnected and deleted.

This adaptation preserves Output instead of clearing/printing status. It calls
no glyph geometry, history, preference or master writer. Native tab text/order,
missing names, selection/focus and complete font/history/dirty preservation remain
pending. Requires App>=0.2.40.dev0 and Fly in FontLab9 Python3.11.
Adapted from Pedro Arilla's Apache-2.0 Glyphs between/Glyphs surrounded by nnonn.py.
See NOTICE and additional-tools.json for complete source/license provenance.
"""


def main() -> None:
    """Run the complete selected-glyph proof through the shared App helper."""
    from fly.ap.context_proofs import run

    run('nnonn')


if __name__ == "__main__":
    main()
