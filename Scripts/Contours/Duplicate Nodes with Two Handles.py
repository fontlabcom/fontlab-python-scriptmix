# this_file: Scripts/Contours/Duplicate Nodes with Two Handles.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Contours · Duplicate Nodes with Two Handles
"""Duplicate Nodes with Two Handles using the distinct original source policy.

What: Use only the first selected layer, matching the source implementation despite
its historical all-masters filename. For each selected on-curve, insert two new
coincident cubic controls and a copy of that target node as the following curve
endpoint. Selected node identities are processed in their captured order. The
controls are fresh; the endpoint retains the target's copied metadata.

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
https://github.com/Reset-Type-Studio/Glyphs-Scripts . Source: Paths/Node Duplicator + 2 Handles (all masters).py.
Apache-2.0 declared in the upstream README; no original body is redistributed.
"""


from typing import Any


def main() -> dict[str, Any]:
    """Run the original handles policy through the shared native boundary."""
    import fly.ap.node_duplicator_native as node_duplicator

    return node_duplicator.duplicate_selected_nodes('handles')


if __name__ == "__main__":
    main()
