# MenuTitle: Clear Master Backgrounds
# this_file: Scripts/Cleaning/Clear Master Backgrounds.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect every current-font glyph, then clear entire mapped backgrounds.

Only declared master foreground layers are included. Refresh rereads the original
font; Clear removes complete background objects in one history batch. Shared
master/auxiliary masks and automatic-layer dependencies refuse before writing.
See the background-cleaning guide for scope and native qualification limits.
"""
from typing import Any


def main() -> Any:
    """Open the complete nonmodal FontLab background-cleaning workflow."""
    from fly.ap.background_clear import show_masters

    return show_masters()


if __name__ == "__main__":
    main()
