# this_file: Scripts/Proof/Show All Layers.py
# SPDX-License-Identifier: Apache-2.0
"""Open every foreground layer of each selected glyph occurrence in a new proof.

Keep selected occurrence order, repeated parents, stored layer order, mixed
masters/auxiliaries and a trailing newline for each parent. Empty selection opens
no tab. Exact layer names are used, without Unicode/slash-text substitution.
Masks/service records are backgrounds. Requires Fly and App0.2.110.dev0.
Native selected-slot/role/tab and complete preservation acceptance is pending.
"""

from typing import Any


def main() -> Any:
    """Invoke the complete shared layer-aware proof only when selected."""
    from fly.ap.show_all_layers import run

    return run()


if __name__ == "__main__":
    main()
