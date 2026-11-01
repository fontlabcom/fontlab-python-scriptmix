# this_file: Scripts/Masters/Common Glyphs.py
# SPDX-License-Identifier: Apache-2.0
"""Report glyph names common to every open font, including unencoded glyphs.

What: Intersect exact glyph names across the registered open fonts. Show the
sorted names, reusable slash text and each font's complete Unicode assignments.
How: Read the registered fonts twice within a deadline. Refuse changed data.
Map AllFonts() FontGate fonts to registered workspace packages by font ID,
then read each canonical font.glyphs list. Errors print a short diagnosis.
Use: Open the fonts to compare, make one current, then run the script. Select
and copy the report text for proofing. Run again to replace the report with a
fresh snapshot. With one font open, all its glyph names are reported.
Why: Exact names keep alternates and unencoded glyphs. Per-font Unicode lists
expose different encodings of a shared name. FontLab has no verified equivalent
of Glyphs' productionGlyphName conversion; the report uses stored FontLab names.
Over FontLab's Glyph-window multi-master text views and Text By Master, this
adds an exact-name proof set shared by every open font, with per-font encodings.
Benefit: Copy shared glyph names or the current font's encoded proof text.

Credit: Luke Prowse (LukeProwse), NaN-xyz/GlyphsApp-Scripts, CommonGlyphs.py,
MIT (root LICENSE), copyright 2019 LukeProwse. The README also declares Apache-2.0.
https://github.com/NaN-xyz/GlyphsApp-Scripts
Independent rewrite of behaviour. No source code was copied.
"""

from time import monotonic
from typing import Any

TITLE = "Common Glyphs"
FontRows = tuple[tuple[int, str, tuple[tuple[str, tuple[int, ...]], ...]], ...]


def common_report(fonts: FontRows, current_id: int) -> dict[str, Any]:
    """Intersect exact names; retain every font's Unicode order and empty sets."""
    if not fonts or current_id not in {row[0] for row in fonts}:
        raise ValueError("Open a font and make it current first.")
    shared = {name for name, _ in fonts[0][2]}
    for _, _, glyphs in fonts[1:]:
        shared.intersection_update(name for name, _ in glyphs)
    ordered = sorted(shared)
    current_glyphs = dict(
        next(glyphs for identity, _, glyphs in fonts if identity == current_id)
    )
    return {
        "text": "".join(chr(code) for name in ordered for code in current_glyphs[name]),
        "count": len(ordered),
        "glyph_names": ordered,
        "slash_text": "".join("/" + name for name in ordered),
        "unicode_by_font": [
            {
                "font": title,
                "package_id": identity,
                "glyphs": {
                    name: [f"U+{code:04X}" for code in codes]
                    for name, codes in glyphs
                    if name in shared
                },
            }
            for identity, title, glyphs in fonts
        ],
        "scope": "Exact stored FontLab glyph names in every open font; Unicode assignments are reported separately. The report includes current-font encoded proof text.",
    }


def read_fonts(deadline: float) -> FontRows:
    """Read registered packages only; stop before returning a partial report."""
    if monotonic() >= deadline:
        raise TimeoutError("Open-font scan expired; run again.")
    from fly import fl

    workspace = fl.flWorkspace.instance()
    rows = []
    registered_fonts = {}
    for registered in workspace.packages():
        if monotonic() >= deadline:
            raise TimeoutError("Open-font scan expired; run again.")
        package = fl.flPackage(registered)
        if package is None or package.isNull:
            raise ValueError("Open font registration changed; run again.")
        identity = int(package.fgId)
        if identity <= 0 or identity in registered_fonts:
            raise ValueError(
                "An open font has invalid or duplicate FontGate registration."
            )
        registered_fonts[identity] = package
    seen = set()
    for font in fl.AllFonts():
        identity = int(font.id)
        package = registered_fonts.get(identity)
        if package is None or identity in seen:
            raise ValueError(
                "An open font is not uniquely registered in the workspace."
            )
        seen.add(identity)
        glyphs = []
        names = set()
        for glyph in font.glyphs:
            if monotonic() >= deadline:
                raise TimeoutError("Open-font scan expired; run again.")
            name, codes = str(glyph.name), tuple(glyph.unicodes)
            if not name or name in names:
                raise ValueError("A font has empty or duplicate glyph names.")
            if any(
                type(code) is not int or not 0 <= code <= 0x10FFFF for code in codes
            ):
                raise ValueError(f"Invalid Unicode assignment in '{name}'.")
            names.add(name)
            glyphs.append((name, codes))
        rows.append((int(package.id), str(package.title_name()), tuple(glyphs)))
    if seen != set(registered_fonts):
        raise ValueError("A registered font is absent from AllFonts; run again.")
    if len(rows) != len({row[0] for row in rows}):
        raise ValueError("Open font registration contains duplicate identities.")
    if monotonic() >= deadline:
        raise TimeoutError("Open-font scan expired; run again.")
    return tuple(rows)


def capture_common() -> dict[str, Any]:
    """Fence the current font and all compared scalar values with double reads."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font first.")
    identity = int(package.id)
    deadline = monotonic() + 2.0
    fonts = read_fonts(deadline)
    if fonts != read_fonts(deadline) or scripting.current_package(identity) is None:
        raise ValueError("Open fonts changed during the scan; run again.")
    return common_report(fonts, identity)


def main() -> Any:
    """Publish a complete selectable report in the shared non-modal shell."""
    import fly.ap.reports as reports  # noqa: PLR0402

    try:
        return reports.show_report(
            capture_common(), title=TITLE, key="masters_common_glyphs"
        )
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
