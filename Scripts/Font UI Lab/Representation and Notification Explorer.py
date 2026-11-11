# this_file: Scripts/Font UI Lab/Representation and Notification Explorer.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect selected glyph representations and observed cache refresh notifications.

Use: Open a font, run this tool and select glyphs in its browser. Inspect the
representation results and notification/cache status; unsupported capabilities
remain explicit. The window keeps the font captured when it opened.
Safety: This explorer does not edit glyph geometry or save the source. Native
FontLab notification delivery, cache preservation and UI lifetime still require
qualification.

Select a glyph in the inspector browser to attach its supported change observer
and read the representation values and cache-presence observations. Refresh
reads that same selected glyph again. A notification refresh is reported only
when the observer callback actually arrives; an unsupported notification or
cache API is shown as unavailable. No global font update queue is cleared.
Close the window to detach its observer and release the preview callbacks.
Selecting a different glyph changes only the inspector target."""


def main():
    """Capture the current borrowed font once and return its owned inspector."""
    from fontlabapp.fontui.representation_notifications import show
    from fontlab_fontport.world import FontWorld

    return show(FontWorld().CurrentFont())


if __name__ == "__main__":
    main()
