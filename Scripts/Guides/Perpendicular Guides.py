# this_file: Scripts/Guides/Perpendicular Guides.py
# SPDX-License-Identifier: Apache-2.0
"""Add a perpendicular guide through selected nodes and centre guides to components.

Use the first selected layer, retaining stored node order and both independent
branches. Existing guides remain. One Undo step; unsafe automatic dependants and
pending native updates are refused. Full native history qualification is pending.
"""

from typing import Any

from fly.ap.perpendicular_guides import run


def main() -> dict[str, Any]:
    """Run the complete shared selection-driven writer through the public facade."""
    return run()


if __name__ == "__main__":
    main()
