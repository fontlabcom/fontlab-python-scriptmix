# this_file: Scripts/Reporters/Duplicate Anchor Rings.py
# SPDX-License-Identifier: Apache-2.0
"""Highlight anchor pairs less than one font unit apart in the Glyph window.

Open a Glyph window, then run this script. Choose handle size5,8 or12.
Every matching unordered pair gets an unfilled red/yellow ring at its first
anchor. Three coincident anchors produce three rings. Disable or Close removes
the overlay and callbacks. Reopen after changing font, master or Glyph window.
No font data or preferences are written.

This original implementation adapts mekkablue's Apache-2.0 duplicate-anchor
reporter. Drawing is foreground across tools, with explicit handle sizes.
Glyphs background ordering and text/hand-tool suppression are not provided.
Shared capture, painting and native ownership live in Fontlabapp. See its NOTICE.
"""

from typing import Any

from fly.ap.scripting import canvas_anchor_rings_dialog_type, show_script_dialog

TITLE, KEY = "Duplicate Anchor Rings", "canvas_duplicate_anchor_rings"


def main() -> Any:
    """Replace only this reporter's owned panel; preserve other open tools."""
    return show_script_dialog(canvas_anchor_rings_dialog_type(), KEY)


if __name__ == "__main__":
    main()
