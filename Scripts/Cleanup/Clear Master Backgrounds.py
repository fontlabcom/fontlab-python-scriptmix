# MenuTitle: Clear Master Backgrounds
# this_file: Scripts/Cleanup/Clear Master Backgrounds.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect every current-font glyph, then clear entire mapped backgrounds.

What it does:
    Only declared master foreground layers are included. Refresh rereads the original
    font; Clear removes complete background objects in one history batch. Shared
    master/auxiliary masks and automatic-layer dependencies refuse before writing.
    See the background-cleaning guide for scope and supported background types.

How it works:
    Delegate background inspection and removal to the shared App workflow. Map
    declared master foreground layers and refuse shared masks or unsafe
    automatic dependencies.

Why this design:
    Restricting scope to declared masters keeps auxiliary foreground
    backgrounds outside this cleaning operation.

How to use:
    Run Cleanup > Clear Master Backgrounds. Inspect the current-font preview,
    use Refresh after edits and press Clear for the shown master-layer
    proposal. Read the background-cleaning guide before use.

Benefit:
    Remove mapped master backgrounds in one recorded history batch while
    retaining auxiliary scope boundaries.
"""
from typing import Any


def main() -> Any:
    """Open the complete nonmodal FontLab background-cleaning workflow."""
    from fly.ap.background_clear import show_masters

    return show_masters()


if __name__ == "__main__":
    main()
