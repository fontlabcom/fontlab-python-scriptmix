# this_file: Scripts/Proof/Show All Layers.py
# SPDX-License-Identifier: Apache-2.0
"""Open every foreground layer of each selected glyph occurrence in a new proof.

Keep selected occurrence order, repeated parents, stored layer order, mixed
masters/auxiliaries and a trailing newline for each parent. Empty selection opens
no tab. Exact layer names are used, without Unicode/slash-text substitution.
Masks/service records are backgrounds.

How to use: activate the Font window, select one or more glyphs, then run this
command. The new proof lists each parent's layers in stored order, so a repeated
selection stays repeated and compatible masters can be compared side by side.
Nothing in the font is edited, and no existing proof tab is replaced or reused.
Requires Fly and App 0.2.26.dev325.
"""

from typing import Any


def main() -> Any:
    """Invoke the complete shared layer-aware proof only when selected."""
    from fly.ap.masters.layers.show_all.model import run

    return run()


if __name__ == "__main__":
    main()
