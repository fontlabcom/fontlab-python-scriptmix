# this_file: Scripts/Font UI Lab/Kerning Proof Workbench.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect explicit kerning and group fallback beside a linked glyph proof.

Use: Open a font and launch this window. Select a stored pair or type the left
and right glyph/group names. Apply writes the value; Delete removes the explicit
pair and reveals any group fallback. Zero is an explicit value. Reload rereads
the same font; the sequence also accepts independent slash-prefixed glyph names.
Group proofs use the first group member. Toggle proof kerning to compare spacing.

Safety: Apply and Delete change kerning in the font captured at launch. Switching
the active font does not retarget the window. Native edits follow the captured
font's current master and refuse unsupported fractional history. Use an owned
test font. Closing this window does not save or close the borrowed font. Missing
or stale fonts refuse editing; native Undo/Redo and saved-font qualification
remain separate from ordinary source tests.
"""


def main():
    """Capture one current borrowed font and return its retained workbench."""
    from fly.ap.fontui.kerning_proof import show
    from fly.fp.world import FontWorld

    font = FontWorld().CurrentFont()
    return show(None if font is None else font)


if __name__ == "__main__":
    main()
