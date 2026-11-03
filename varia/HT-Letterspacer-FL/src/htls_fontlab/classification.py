"""GlyphsInfo classification, with name/Unicode fallback and explicit overrides."""

from pathlib import Path
import unicodedata
import xml.etree.ElementTree as ET

_cache = None


def _data():
    global _cache
    if _cache is None:
        names, unicodes = {}, {}
        for filename in ("GlyphData.xml", "GlyphData_Ideographs.xml"):
            for element in ET.parse(
                str(Path(__file__).parent / "data" / filename)
            ).getroot():
                a = element.attrib
                names[a["name"]] = a
                for alias in (
                    a.get("altNames", "") + "," + a.get("production", "")
                ).split(","):
                    if alias.strip():
                        names.setdefault(alias.strip(), a)
                if a.get("unicode"):
                    unicodes.setdefault(int(a["unicode"], 16), a)
        _cache = names, unicodes
    return _cache


def classify(name, codes=(), overrides=None):
    names, unicodes = _data()
    base = name.split(".")[0]
    named = names.get(name)
    encoded = next((unicodes[c] for c in codes if c in unicodes), None)
    # Legacy production names (Omega=Ohm, mu=micro) can disagree with modern
    # GlyphsInfo names. The actual encoding disambiguates these glyphs.
    a = (
        encoded
        if (named and encoded and named.get("unicode") != encoded.get("unicode"))
        else named or encoded or names.get(base) or {}
    )
    # Glyphs 3's original database treats this legacy currency name separately
    # from the modern letter name fhook, even though both encode U+0192.
    if base == "florin" and (not codes or 0x0192 in codes):
        a = dict(a, category="Symbol", subCategory="Currency", script="latin", case="")
    if not a and "_" in base:
        a = dict(names.get(base.split("_")[0]) or {})
        a["subCategory"] = "Ligature"
    char = None
    if codes:
        char = chr(codes[0])
    if not char and a.get("unicode"):
        char = chr(int(a["unicode"], 16))
    if not char:
        try:
            if base.startswith("uni") and len(base) == 7:
                char = chr(int(base[3:], 16))
            elif base.startswith("u") and 5 <= len(base) <= 7:
                char = chr(int(base[1:], 16))
        except ValueError:
            pass
    uc = unicodedata.category(char) if char else ""
    category = a.get("category") or {
        "L": "Letter",
        "N": "Number",
        "P": "Punctuation",
        "S": "Symbol",
        "M": "Mark",
        "Z": "Separator",
    }.get(uc[:1], "Other")
    case = {"upper": 1, "lower": 2, "smallCaps": 3, "minor": 4, "other": 5}.get(
        a.get("case"), 0
    )
    if not case and char and category == "Letter":
        case = 1 if char.isupper() else 2 if char.islower() else 0
    suffixes = name.split(".")[1:]
    if any(s in ("sc", "smcp", "c2sc") for s in suffixes):
        case = 3
    elif any(s in ("sups", "subs", "numr", "dnom", "sinf") for s in suffixes):
        case = 4
    result = {
        "category": category,
        "subCategory": a.get("subCategory") or None,
        "script": a.get("script") or None,
        "case": case,
    }
    result.update(overrides or {})
    return result
