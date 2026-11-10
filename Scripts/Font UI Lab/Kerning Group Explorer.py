# this_file: Scripts/Font UI Lab/Kerning Group Explorer.py
# SPDX-License-Identifier: Apache-2.0
"""Explore groups and kerning with two linked previews in one retained window.

Use: Select a group, then Use selected group as left or right to stage that key.
The opposite key and typed value stay unchanged. Group actions edit membership;
accepted edits revalidate the pair. Rename/delete does not rewrite kerning keys.
The group preview shows the selected member; the pair proof uses each group's
first member with its actual effective kerning, which may differ from the group
row value; it does not show every combination. Apply/Delete write explicit kerning.

Safety: Use an owned test font. Both editors capture one font at launch; changing
active fonts does not retarget them. Native edits follow its current master and
may refuse unsupported history data. Closing does not save or close the borrowed
font. Native Undo/Redo, painting and saved-font acceptance remain separate.
"""


def main():
    """Capture one current borrowed font and return its retained workbench."""
    from fly.ap.fontui.kerning_groups import show
    from fly.fp.world import FontWorld

    font = FontWorld().CurrentFont()
    return show(None if font is None else font)


if __name__ == "__main__":
    main()
