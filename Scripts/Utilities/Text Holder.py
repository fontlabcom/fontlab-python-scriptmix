# this_file: Scripts/Utilities/Text Holder.py
# SPDX-License-Identifier: Apache-2.0
"""Keep proof text in an editable, persistent floating scratchpad.

What it does:
    Find highlights the first literal match. Find & Replace changes matches in the
    selection or the whole text. Save stays open; Save & Close and Ignore & Close
    retain their distinct actions. Saved UTF8 text recovers on the next launch.

    Independently implemented from Reza Bohloul, Window/Text holder.py.
    No original body is copied or executed; original licence is undeclared.
    See NOTICE and additional-tools.json. Requires Fly and App 0.2.91.dev0.

How it works:
    Open the shared App text-holder editor through Fly. Use its persistent
    text store, literal Find and selection-aware replacement without accessing
    glyph geometry.

Why this design:
    A persistent scratchpad keeps proof text between launches without putting
    temporary material into a glyph note or font metadata.

How to use:
    Run Utilities > Text Holder. Enter text, use Find or Find & Replace and
    choose Save, Save & Close or Ignore & Close according to the required
    persistence action.

Benefit:
    Keep reusable proof text available beside FontLab without changing the
    font.
"""


from typing import Any


def main() -> Any:
    """Open the complete shared editor through Fly without font mutation."""
    from fly.ap.text_holder import show

    return show()


if __name__ == "__main__":
    main()
