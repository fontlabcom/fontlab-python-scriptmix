# this_file: Scripts/Masters/Common Glyphs.py
# SPDX-License-Identifier: Apache-2.0
"""Report exact glyph names common to every open font, including unencoded glyphs.

What:
    Show analysed family names, count, first-open-font character strings, exact
    stored nice names and verified GlyphData production names. Unknown production
    mappings remain explicit. Alternative encodings are listed separately.

How:
    Shared App double-reads registered font-owned records within a deadline;
    this caller supplies real glyphsLib production metadata. One font retains
    its glyph order. Multiple fonts use sorted names because the original set
    intersection order was unspecified. Character strings use the first assigned
    scalar, never the current font, alternate concatenation or inferred ligatures.
    Each nonempty string and each name retains its final source space.

Use:
    Run Masters > Common Glyphs with one or more open fonts; none need be current.
    Use Copy Characters or Copy Original Report for exact detached source MIME
    payloads, or inspect the encoding/metadata details. Refresh after changing
    fonts, and Close when done. Opening/Refresh changes no clipboard, Output or
    font data. Ordinary selection copying can normalize Unicode spaces/separators;
    escaped JSON retains exact strings. The literal MIME callbacks/OS clipboard
    handoff and native rendering still need qualification.
    The optional charcoal control is visible, unchecked and unavailable: FontLab
    lacks a supported glyph-only mark/history path (FontLab issue 8564).

Status:
    Partial source improvement. The original optional all-open-font charcoal
    action remains required and unimplemented; native report acceptance remains
    pending. This is not a complete equivalent of the original workflow.

Credits:
    Independent rewrite of behaviour, not copied source code. Luke Prowse
    (LukeProwse), NaN-xyz/GlyphsApp-Scripts/CommonGlyphs.py. MIT root LICENSE,
    Copyright (c) 2019 LukeProwse; upstream README also declares Apache-2.0.
    Exact MIT notice is retained in NOTICE.
    https://github.com/NaN-xyz/GlyphsApp-Scripts
"""

from collections.abc import Callable
from typing import Any
import fly.ap.common_glyphs_controller as controller
from fly.ap.common_glyphs import Production


def metadata(name: str, *, checkpoint: Callable = lambda: None) -> Production:
    """Use actual GlyphData production_name with explicit provenance/unknowns.

    get_glyph may sanitize unknown names into an unchanged fallback. Accept
    exact database/alias/production keys or derivations with verified base and
    ligature-component keys; never call an unknown stored name a conversion.
    """
    checkpoint()
    from glyphsLib import glyphdata

    record = glyphdata.get_glyph(name)
    checkpoint()
    data = glyphdata.GLYPHDATA

    def known(value: str) -> bool:
        """Membership, not nonempty API fallback, proves known GlyphData."""
        checkpoint()
        return any(
            value in index
            for index in (data.names, data.alternative_names, data.production_names)
        )

    if known(name):
        status = "database"
    else:
        base = name.partition(".")[0]
        parts = base.split("_")
        status = "derived" if all(known(part) for part in parts) else "unknown"
    checkpoint()
    if status == "unknown" or not record.production_name:
        return Production(None, "unknown")
    return Production(record.production_name, status)


def main() -> Any:
    """Launch the complete detached report through the installed Fly/App alias."""
    try:
        return controller.show(metadata)
    except (
        ValueError,
        RuntimeError,
        TimeoutError,
        InterruptedError,
        ExceptionGroup,
        ImportError,
    ) as error:
        print(f"Common Glyphs: {error}")
        return None


if __name__ == "__main__":
    main()
