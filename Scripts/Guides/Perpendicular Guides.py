# this_file: Scripts/Guides/Perpendicular Guides.py
# SPDX-License-Identifier: Apache-2.0
"""Add a perpendicular guide through selected nodes and centre guides to components.

What it does:
    Use the first selected layer, retaining stored node order and both independent
    branches. Existing guides remain. One Undo step; unsafe automatic dependants and
    pending native updates are refused.

How it works:
    Delegate the two guide branches to App: perpendicular construction from
    selected nodes and centre-guide construction for selected components on
    the first layer.

Why this design:
    Keeping both branches independent preserves mixed node/component selection
    behaviour and leaves existing guides available.

How to use:
    Open a glyph, select the required nodes or components and run Guides >
    Perpendicular Guides. Review any refusal before changing the selection and
    running it again.

Benefit:
    Add construction references through shared history; each successful edit
    is recorded as one Undo step.
"""

from typing import Any

from fly.ap.perpendicular_guides import run


def main() -> dict[str, Any]:
    """Run the complete shared selection-driven writer through the public facade."""
    return run()


if __name__ == "__main__":
    main()
