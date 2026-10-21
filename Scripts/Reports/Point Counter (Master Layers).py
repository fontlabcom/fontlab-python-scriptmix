# this_file: Scripts/Reports/Point Counter (Master Layers).py
# SPDX-License-Identifier: Apache-2.0
"""Count own paths and nodes in every master layer for each selected occurrence.

Select glyphs in a Font window or layer occurrences in a Glyph window. Each
selected occurrence contributes all its parent's master layers in stored order,
including empty masters and repeated selections. Auxiliary, mask and service
layers are excluded by the native master property. Components are not decomposed.

A normal fixed400×300 Point Counter window shows the complete read-only text.
Select and copy it normally; close and rerun for a fresh snapshot. No font,
selection, history, preferences, clipboard or Output writer is called. Empty
selection or no masters gives the original empty report. Read failures produce
no partial window. Requires App>=0.2.118.dev0 and Fly in FontLab9 Python3.11.

Independently implements Reza Bohloul's Path/Point Counter.py workflow; the
inspected source declares no licence, so its body is not redistributed. Cubic
and line reports preserve original text. Quadratic endpoints are included in
Points/Nodes, explicitly correcting the original omission. Native layer order,
reader preservation and window lifecycle qualification remain pending.
"""


def main() -> None:
    """Load the complete shared master-only workflow through public Fly lazily."""
    from fly.ap.master_point_counts import show

    show()


if __name__ == "__main__":
    main()
