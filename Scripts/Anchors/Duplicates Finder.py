# this_file: Scripts/Anchors/Duplicates Finder.py
# SPDX-License-Identifier: Apache-2.0
"""Find and remove duplicate anchors across the whole font or opening selection.

Both scopes scan every master. Keep the first anchor in layer order; numbered
copies count only when their immediate stem exists. Coincident groups use
rounded points and are kept unless explicitly enabled. Automatic layers are
reported and kept. Fix applies every pending finding, independent of table rows.

The complete candidate uses direct pin removals and one final layer/glyph
notification. Unsafe automatic dependants and changed sources refuse before
history. A partial native failure is diagnosed for Edit > Undo; pins are never
reconstructed as rollback. Refresh keeps the original opening selection.
Requires Fly and App 0.2.102.dev0. Native PythonQt/full-font, genuine
Undo/Redo, dirty state, saved/reopened preservation and lifetime remain pending.
"""

from typing import Any


def main() -> Any:
    """Open the complete owned writer only when the menu is invoked."""
    from fly.ap.anchor_duplicates import show

    return show()


if __name__ == "__main__":
    main()
