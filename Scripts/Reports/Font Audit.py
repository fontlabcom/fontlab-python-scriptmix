# this_file: Scripts/Reports/Font Audit.py
# SPDX-License-Identifier: Apache-2.0 AND MIT
# FLM: Reports · Font Audit
"""Inspect whole-font inventory, encoding, categories and case consistency.

Eight named report tabs retain the original report controls, CSV export,
selection guards and case-coverage proof workflow. The shared App shell has
an independent read-only TMetrics preview. Category XML includes every glyph
in font order; select the fragment for manual insertion into a UFO lib.

Credits: FontLab App contributors (Apache-2.0); mekkablue Casefolding Report
workflow (Apache-2.0); Simon Cozens Categories to XML lib key workflow (MIT).
See NOTICE for full source credits. Requires App's WP08 Font Audit assembly,
Fontport, Fly and Glyport with maintained glyphsLib GlyphData.

Open the tool with the intended font active, then select the named report tab.
Refresh rereads the captured source. Report controls retain their own selection
and export actions; the shared preview is read-only. Switching to another font
does not silently retarget an existing audit window. Close releases the owned
report controls and preview without saving or closing the source document.
Use the individual report menus for separate windows when comparing results.
"""

from collections.abc import Callable
from typing import Any

from fly.gp.glyphsapp.glyph_info import glyph_categories


def metadata(
    name: str, codes: tuple[int, ...], *, checkpoint: Callable = lambda: None
) -> tuple[str | None, str | None]:
    """Use maintained GlyphData, distinguishing known uncategorized subtypes."""
    checkpoint()
    formatted = []
    for code in codes:
        checkpoint()
        formatted.append(f"{code:04X}")
    category, subcategory = glyph_categories(name, formatted)
    checkpoint()
    return (subcategory or "") if category else None, None


def preferred(text: str, *, checkpoint: Callable = lambda: None) -> str | None:
    """Resolve all scalar names through actual GlyphData; retain whole expansions."""
    from glyphsLib import glyphdata

    checkpoint()
    glyphdata.get_glyph("A")
    checkpoint()
    if text == "SS":
        return "SS"
    names = []
    for char in text:
        checkpoint()
        record = glyphdata.GLYPHDATA.unicodes.get(f"{ord(char):04X}")
        if record is None:
            return None
        names.append(record["name"])
    checkpoint()
    result = "_".join(names) or None
    checkpoint()
    return result


def main() -> Any:
    """Open the shared report owner with the original foreign metadata policies."""
    from fly.ap.studios.font_audit.practical import show

    return show(classify=glyph_categories, case_metadata=metadata, case_preferred=preferred)


if __name__ == "__main__":
    main()
