# this_file: Scripts/Proof/Context Proof.py
# SPDX-License-Identifier: Apache-2.0
"""Preview and open eight exact glyph context proofs in one tabbed tool.

Select glyphs, including repeated Glyph-window occurrences, and choose a named
context tab. Preview and Copy preserve the original proof text. Open creates a
new Glyph tab in the current master without editing font data.
Requires App and Fly. Original Pedro Arilla scripts: Apache-2.0; see NOTICE,
additional-tools.json and menu-consolidations.json for provenance.

The window captures the source font when it opens. Refresh reads that captured
source; switching the active document does not silently retarget an existing
proof. Use the named modes to retain their distinct contexts and repetitions.
The bottom Close action releases the owned controls and preview. It does not
save or close the source font. Copy sends the generated text to the clipboard;
Open creates a separate proof view. These actions do not apply outline, metrics,
anchor or component changes. Use the original menus when a separate window is
more convenient; they remain available alongside this combined view.
"""


def main() -> None:
    """Open the shared Context Proof app lazily inside FontLab."""
    from fly.ap.studios.proof_studio.practical import show_context

    show_context()


if __name__ == "__main__":
    main()
