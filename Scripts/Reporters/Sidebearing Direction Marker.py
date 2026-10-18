# this_file: Scripts/Reporters/Sidebearing Direction Marker.py
# SPDX-License-Identifier: Apache-2.0
"""Mark each laid-out glyph's advance edge in the active FontLab Glyph window.

Open a Glyph window, then run this script. Choose LTR or RTL explicitly.
The modeless panel draws a foreground line and triangle across tools. It does
not edit fonts. Disable or Close removes its overlay and callbacks. Reopen the
panel after changing the font, master or Glyph window.

This original implementation adapts akufadhl's Apache-2.0 RSBline behavior.
Glyphs background ordering and automatic text-tool gating are not provided.
Shared geometry and native ownership live in Fontlabapp. See its NOTICE.
"""

from typing import Any

from fly.ap.scripting import canvas_rsb_dialog_type, show_script_dialog

TITLE, KEY = "Sidebearing Direction Marker", "canvas_right_sidebearing_line"


def main() -> Any:
    """Replace only this reporter's owned panel; preserve other open tools."""
    return show_script_dialog(canvas_rsb_dialog_type(), KEY)


if __name__ == "__main__":
    main()
