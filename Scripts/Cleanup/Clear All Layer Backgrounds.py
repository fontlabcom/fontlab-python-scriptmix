# MenuTitle: Clear All Layer Backgrounds
# this_file: Scripts/Cleanup/Clear All Layer Backgrounds.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect every current-font glyph, then clear entire mapped backgrounds.

What it does:
    All physical foreground layers are included. Refresh rereads the original
    font; Clear removes complete background objects in one history batch. Shared
    master/auxiliary masks and automatic-layer dependencies refuse before writing.
    See the background-cleaning guide for scope and supported background types.

How it works:
    Delegate background inspection and removal to the shared App workflow. Map
    every physical foreground layer and refuse unsafe shared masks or
    automatic dependencies.

Why this design:
    Removing a complete background object differs from deleting only its
    outlines, so the preview shows the actual mapped scope.

How to use:
    Run Cleanup > Clear All Layer Backgrounds. Inspect the preview for the
    current font, use Refresh after changes and press Clear only for the shown
    proposal. Read the background-cleaning guide for supported domains.

Benefit:
    Clear mapped backgrounds across foreground layers in one recorded history
    batch.
"""
from typing import Any


def main() -> Any:
    """Open the complete nonmodal FontLab background-cleaning workflow."""
    from fly.ap.background_clear import show_all

    return show_all()


if __name__ == "__main__":
    main()
