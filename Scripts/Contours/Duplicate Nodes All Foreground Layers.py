# this_file: Scripts/Contours/Duplicate Nodes All Foreground Layers.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Duplicate Nodes All Foreground Layers
"""Duplicate Nodes All Foreground Layers using the distinct original source policy.

What: Read on-curve indices from the first selected layer. Apply those fixed indices
to every stored foreground layer of every selected parent occurrence, including
auxiliary layers with duplicate names. A parent selected twice is processed twice.
Targets do not need their own selected nodes. Missing path/node indices are listed
rather than substituted. Background, mask and service layers are not targets.

How: The shared App engine captures selection and layer identities twice, stages
all detached node copies before history, and applies one recorded action. It
repairs known native clone metadata loss and restores exact fractional positions
after insertion. Original nodes and shape names/notes are checked after the write.

Use: Select the source nodes and run this menu action. An all-layer broadcast
needs a Font window when it includes glyphs outside the active Glyph editor.
This is an immediate action. Use the separate Node Duplicator panel when you want
its per-glyph reference selection, preview and declared-master controls instead.

Safety: Automatic dependants, shared owners, unsupported generated/nested paths,
hinted topology and unsafe control mappings are refused before editing. Queued
glyph updates are disclosed without being cleared. A late failure preserves
recovery details and says to inspect the font and its Undo history before retrying.
A read-only owned result window lists skipped target indices and queued glyph ids.

Credit: Independent behaviour rewrite after Fernando Díaz and Reset Type Studio,
https://github.com/Reset-Type-Studio/Glyphs-Scripts . Source: Paths/Node Duplicator (all masters).py.
Apache-2.0 declared in the upstream README; no original body is redistributed.
"""


from typing import Any


def main() -> dict[str, Any]:
    """Run the original all policy through the shared native boundary."""
    import fly.ap.node_duplicator_native as node_duplicator

    return node_duplicator.duplicate_selected_nodes('all')


if __name__ == "__main__":
    main()
