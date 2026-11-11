---
this_file: src_docs/md/scripts/contours/duplicate-nodes-current-layer.md
tags: ["Contours"]
categories: ["Contours"]
---

# Duplicate Nodes Current Layer

Duplicate Nodes Current Layer using the distinct original source policy.

What: Duplicate only the selected on-curve nodes of the first selected layer. Other
selected layers and glyphs remain outside this action. The captured original
selection identities survive index shifts as copies are inserted in reverse order.
Each copy becomes a line endpoint, keeping the target node's coordinates, name,
raw connection flags and explicitly preserved copy properties.

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
https://github.com/Reset-Type-Studio/Glyphs-Scripts . Source: Paths/Node Duplicator (current layer).py.
Apache-2.0 declared in the upstream README; no original body is redistributed.

Run **Contours > Duplicate Nodes Current Layer** from FontLab's Scripts menu.

Read [installation](../../install.md) and [working with scripts](../../use.md) before use.

## Source identity

SHA256: `f5fa53d87345852d41ddd4474404f6bc38f52b25a25f772e6cdc463b224b9436`

[Python source at `370bf9829bc1`](https://github.com/fontlabcom/fontlab-python-scriptmix/blob/370bf9829bc141c1c9f88be0018cbc285b502a5d/Scripts/Contours/Duplicate%20Nodes%20Current%20Layer.py)
