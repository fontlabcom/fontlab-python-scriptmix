# this_file: Scripts/Font UI Lab/Detached Transform Preview.py
# SPDX-License-Identifier: Apache-2.0
"""Preview one explicitly chosen layer/glyph without writing the captured font.

What: Compare a detached affine result with its immutable before snapshot.
Use: Choose a layer and glyph, Capture, then edit the existing transform fields.
Refresh reads the same captured font. Save settings creates a chosen new JSON;
Show script displays text without execution. Closing never closes the source.
Snapshot: Capture reads backend-stored outlines, not unfinished changes held in
borrowed scripting wrappers. Only the selected glyph, its reachable component
bases and required image bytes enter the private models. Missing bases, cycles
or unavailable resources refuse the snapshot. Changing the layer or glyph clears
the prior proof; choose the new target explicitly before Capture. Switching the
host's current font never retargets an already opened window. After closing the
source, the detached copy can still be inspected, but Refresh cannot read it.
Safety: Use an owned test font. No font Apply/save/export is provided. Native
metadata/resource completeness and FontLab lifetime/rendering remain unqualified.
"""


def main():
    """Capture exactly once and return the actual retained composition owner."""
    from fly.ap.fontui.detached_transform import show
    from fly.fp.world import FontWorld

    font = FontWorld().CurrentFont()
    return show(None if font is None else font)


if __name__ == '__main__':
    main()
