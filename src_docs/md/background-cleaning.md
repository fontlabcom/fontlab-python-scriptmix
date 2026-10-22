---
this_file: src_docs/md/background-cleaning.md
---

# Clear Backgrounds Across a Font

Open **Cleanup > Clear All Layer Backgrounds** to scan every glyph and every
physical foreground layer in the current font. **Clear Master Backgrounds**
includes only declared master layers, including non-interpolating masters.
Auxiliary layers with interpolatable names are not treated as declared masters.

The table follows original glyph and layer order. **Clear backgrounds** removes
the entire original background object, including outlines, anchors, guidelines,
images and stored properties. It does not rebuild a partial copy or clear only
contours. **Refresh** rereads the original font. Closing the window cancels
future actions; it cannot reverse an already applied edit.

One native mask can be shared by several foreground layers. The all-layer tool
removes it once. The master-only tool refuses a mask shared with an excluded
auxiliary layer. Unmapped masks and ambiguous identities refuse before history;
no layer is silently omitted. Automatic layers/dependants and pending native
updates also prevent writing because their complete history preservation has
not been qualified. Switching fonts invalidates the original tool.

An unchanged scan performs no history or date writes. A successful edit uses one
final native notification. If a native operation fails after removal begins,
the tool reports an explicit partial outcome and recommends **Edit > Undo**.
It never reconstructs deleted backgrounds or claims an exception rolled back.

These are independent Python 3.11 FontLab implementations of Pedro Arilla's
Apache-2.0 scripts **Clear background in all layers.py** and **Clear background
in all master layers.py** from `pedroarilla/glyphs-scripts`, with shared logic
available through `fly.ap.background_clear`. The originals remain in the
source corpus, unchanged. See NOTICE for attribution.

## Qualification

Source and ordinary installed-artifact controls are separate from FontLab
acceptance. The complete native whole-font background mapping, survivor
metadata, one Undo/Redo, dirty state, timestamps and save/reopen workflow remain
pending owned-font qualification. Native limitations are not completion of the
original workflow. Existing source-migration denominators remain unchanged.

## Active and Locked Background Boundary

An active background cannot be removed while preserving that active layer. The
tool refuses it before history. Locked backgrounds also refuse: the bound
read-only resolver does not reveal whether the stored active pointer is locked.
These cases remain part of the original required workflow and are **not accepted
through refusal**. The complete original target list remains in the preview.

The scan uses `updateActiveLayer(False)`, which does not assign a replacement.
It never reads `activeLayer` or `isActive`, whose native getters can initialize a
previously null active pointer. Null/unreadable resolution on a nonempty glyph
refuses the scan. Final source and pending-update fences occur after all staged
inputs, immediately before history preparation.

After any attempted removal, every pre/post date error is collected and exactly
one final notification is attempted even if stamping fails. A notification
failure remains an explicit partial outcome. No-op and no-attempt paths never
notify or write dates. Expected survivor order is prepared in checked per-glyph
passes before history, not a quadratic whole-font traversal after it.
