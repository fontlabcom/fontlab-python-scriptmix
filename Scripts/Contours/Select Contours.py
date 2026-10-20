# this_file: Scripts/Contours/Select Contours.py
# SPDX-License-Identifier: Apache-2.0
"""Select each own contour with any selected node in the first selected layer.

Select a node or control handle, then run this command. All nodes in its contour
become selected. Existing components and other non-node selections stay intact.
Other selected layers stay unchanged. No geometry or Undo step is created.

Adapted independently from Pedro Arilla's Paths/Select paths.py (2018–2022).
See NOTICE and additional-tools.json for exact source hashes and Apache terms.
Requires fontlab-fly and App 0.2.71.dev0. Native acceptance remains pending.
"""


def main() -> int:
    """Run the shared native action through Fly and report selected contour count."""
    from fly.ap.contour_selection import select_contours

    count = select_contours()
    print(f"{count} contours selected.")
    return count


if __name__ == "__main__":
    main()
