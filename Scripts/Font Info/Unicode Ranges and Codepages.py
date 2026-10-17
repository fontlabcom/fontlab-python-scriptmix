# this_file: Scripts/Font Info/Unicode Ranges and Codepages.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font Info · Unicode Ranges & Codepage Hints
"""Report OS/2 range bits and complete printable codepage coverage from every glyph encoding; no font changes.

Open with a font active. Read covered OS/2 Unicode ranges and printable single-byte
codepage coverage, then use Refresh report after encoding edits. Every encoding
on each glyph is counted. Multibyte codepages need manual review. This report
does not change export flags: coverage alone does not establish a correct flag.
"""

from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    current_package,
    font_info_dialog_type,
    show_script_dialog,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Unicode Ranges & Codepage Hints"
KEY = "fontinfo_unicode_ranges"


def glyph_records(package: Any) -> Any:
    """Read all Unicode assignments, including secondary encodings, in font order."""
    FL = ap.FL

    active = current_package()
    if active is None or active.id != package.id:
        msg = "Activate the original font and reopen this tool."
        raise ValueError(msg)
    legacy = FL.fl.font
    return [
        (legacy[i].name, list(package.findName(legacy[i].name).fgGlyph.unicodes))
        for i in range(len(legacy))
    ]


# OS/2 v4 range assignments: https://learn.microsoft.com/en-us/typography/opentype/spec/os2#ur
# Numeric specification data, transcribed from the FontTools OS/2 range table.
UNICODE_RANGES = (
    (("Basic Latin", (0, 127)),),
    (("Latin-1 Supplement", (128, 255)),),
    (("Latin Extended-A", (256, 383)),),
    (("Latin Extended-B", (384, 591)),),
    (
        ("IPA Extensions", (592, 687)),
        ("Phonetic Extensions", (7424, 7551)),
        ("Phonetic Extensions Supplement", (7552, 7615)),
    ),
    (
        ("Spacing Modifier Letters", (688, 767)),
        ("Modifier Tone Letters", (42752, 42783)),
    ),
    (
        ("Combining Diacritical Marks", (768, 879)),
        ("Combining Diacritical Marks Supplement", (7616, 7679)),
    ),
    (("Greek and Coptic", (880, 1023)),),
    (("Coptic", (11392, 11519)),),
    (
        ("Cyrillic", (1024, 1279)),
        ("Cyrillic Supplement", (1280, 1327)),
        ("Cyrillic Extended-A", (11744, 11775)),
        ("Cyrillic Extended-B", (42560, 42655)),
    ),
    (("Armenian", (1328, 1423)),),
    (("Hebrew", (1424, 1535)),),
    (("Vai", (42240, 42559)),),
    (("Arabic", (1536, 1791)), ("Arabic Supplement", (1872, 1919))),
    (("NKo", (1984, 2047)),),
    (("Devanagari", (2304, 2431)),),
    (("Bengali", (2432, 2559)),),
    (("Gurmukhi", (2560, 2687)),),
    (("Gujarati", (2688, 2815)),),
    (("Oriya", (2816, 2943)),),
    (("Tamil", (2944, 3071)),),
    (("Telugu", (3072, 3199)),),
    (("Kannada", (3200, 3327)),),
    (("Malayalam", (3328, 3455)),),
    (("Thai", (3584, 3711)),),
    (("Lao", (3712, 3839)),),
    (("Georgian", (4256, 4351)), ("Georgian Supplement", (11520, 11567))),
    (("Balinese", (6912, 7039)),),
    (("Hangul Jamo", (4352, 4607)),),
    (
        ("Latin Extended Additional", (7680, 7935)),
        ("Latin Extended-C", (11360, 11391)),
        ("Latin Extended-D", (42784, 43007)),
    ),
    (("Greek Extended", (7936, 8191)),),
    (
        ("General Punctuation", (8192, 8303)),
        ("Supplemental Punctuation", (11776, 11903)),
    ),
    (("Superscripts And Subscripts", (8304, 8351)),),
    (("Currency Symbols", (8352, 8399)),),
    (("Combining Diacritical Marks For Symbols", (8400, 8447)),),
    (("Letterlike Symbols", (8448, 8527)),),
    (("Number Forms", (8528, 8591)),),
    (
        ("Arrows", (8592, 8703)),
        ("Supplemental Arrows-A", (10224, 10239)),
        ("Supplemental Arrows-B", (10496, 10623)),
        ("Miscellaneous Symbols and Arrows", (11008, 11263)),
    ),
    (
        ("Mathematical Operators", (8704, 8959)),
        ("Supplemental Mathematical Operators", (10752, 11007)),
        ("Miscellaneous Mathematical Symbols-A", (10176, 10223)),
        ("Miscellaneous Mathematical Symbols-B", (10624, 10751)),
    ),
    (("Miscellaneous Technical", (8960, 9215)),),
    (("Control Pictures", (9216, 9279)),),
    (("Optical Character Recognition", (9280, 9311)),),
    (("Enclosed Alphanumerics", (9312, 9471)),),
    (("Box Drawing", (9472, 9599)),),
    (("Block Elements", (9600, 9631)),),
    (("Geometric Shapes", (9632, 9727)),),
    (("Miscellaneous Symbols", (9728, 9983)),),
    (("Dingbats", (9984, 10175)),),
    (("CJK Symbols And Punctuation", (12288, 12351)),),
    (("Hiragana", (12352, 12447)),),
    (("Katakana", (12448, 12543)), ("Katakana Phonetic Extensions", (12784, 12799))),
    (("Bopomofo", (12544, 12591)), ("Bopomofo Extended", (12704, 12735))),
    (("Hangul Compatibility Jamo", (12592, 12687)),),
    (("Phags-pa", (43072, 43135)),),
    (("Enclosed CJK Letters And Months", (12800, 13055)),),
    (("CJK Compatibility", (13056, 13311)),),
    (("Hangul Syllables", (44032, 55215)),),
    (("Non-Plane 0 *", (55296, 57343)),),
    (("Phoenician", (67840, 67871)),),
    (
        ("CJK Unified Ideographs", (19968, 40959)),
        ("CJK Radicals Supplement", (11904, 12031)),
        ("Kangxi Radicals", (12032, 12255)),
        ("Ideographic Description Characters", (12272, 12287)),
        ("CJK Unified Ideographs Extension A", (13312, 19903)),
        ("CJK Unified Ideographs Extension B", (131072, 173791)),
        ("Kanbun", (12688, 12703)),
    ),
    (("Private Use Area (plane 0)", (57344, 63743)),),
    (
        ("CJK Strokes", (12736, 12783)),
        ("CJK Compatibility Ideographs", (63744, 64255)),
        ("CJK Compatibility Ideographs Supplement", (194560, 195103)),
    ),
    (("Alphabetic Presentation Forms", (64256, 64335)),),
    (("Arabic Presentation Forms-A", (64336, 65023)),),
    (("Combining Half Marks", (65056, 65071)),),
    (("Vertical Forms", (65040, 65055)), ("CJK Compatibility Forms", (65072, 65103))),
    (("Small Form Variants", (65104, 65135)),),
    (("Arabic Presentation Forms-B", (65136, 65279)),),
    (("Halfwidth And Fullwidth Forms", (65280, 65519)),),
    (("Specials", (65520, 65535)),),
    (("Tibetan", (3840, 4095)),),
    (("Syriac", (1792, 1871)),),
    (("Thaana", (1920, 1983)),),
    (("Sinhala", (3456, 3583)),),
    (("Myanmar", (4096, 4255)),),
    (
        ("Ethiopic", (4608, 4991)),
        ("Ethiopic Supplement", (4992, 5023)),
        ("Ethiopic Extended", (11648, 11743)),
    ),
    (("Cherokee", (5024, 5119)),),
    (("Unified Canadian Aboriginal Syllabics", (5120, 5759)),),
    (("Ogham", (5760, 5791)),),
    (("Runic", (5792, 5887)),),
    (("Khmer", (6016, 6143)), ("Khmer Symbols", (6624, 6655))),
    (("Mongolian", (6144, 6319)),),
    (("Braille Patterns", (10240, 10495)),),
    (("Yi Syllables", (40960, 42127)), ("Yi Radicals", (42128, 42191))),
    (
        ("Tagalog", (5888, 5919)),
        ("Hanunoo", (5920, 5951)),
        ("Buhid", (5952, 5983)),
        ("Tagbanwa", (5984, 6015)),
    ),
    (("Old Italic", (66304, 66351)),),
    (("Gothic", (66352, 66383)),),
    (("Deseret", (66560, 66639)),),
    (
        ("Byzantine Musical Symbols", (118784, 119039)),
        ("Musical Symbols", (119040, 119295)),
        ("Ancient Greek Musical Notation", (119296, 119375)),
    ),
    (("Mathematical Alphanumeric Symbols", (119808, 120831)),),
    (
        ("Private Use (plane 15)", (983040, 1048573)),
        ("Private Use (plane 16)", (1048576, 1114109)),
    ),
    (
        ("Variation Selectors", (65024, 65039)),
        ("Variation Selectors Supplement", (917760, 917999)),
    ),
    (("Tags", (917504, 917631)),),
    (("Limbu", (6400, 6479)),),
    (("Tai Le", (6480, 6527)),),
    (("New Tai Lue", (6528, 6623)),),
    (("Buginese", (6656, 6687)),),
    (("Glagolitic", (11264, 11359)),),
    (("Tifinagh", (11568, 11647)),),
    (("Yijing Hexagram Symbols", (19904, 19967)),),
    (("Syloti Nagri", (43008, 43055)),),
    (
        ("Linear B Syllabary", (65536, 65663)),
        ("Linear B Ideograms", (65664, 65791)),
        ("Aegean Numbers", (65792, 65855)),
    ),
    (("Ancient Greek Numbers", (65856, 65935)),),
    (("Ugaritic", (66432, 66463)),),
    (("Old Persian", (66464, 66527)),),
    (("Shavian", (66640, 66687)),),
    (("Osmanya", (66688, 66735)),),
    (("Cypriot Syllabary", (67584, 67647)),),
    (("Kharoshthi", (68096, 68191)),),
    (("Tai Xuan Jing Symbols", (119552, 119647)),),
    (
        ("Cuneiform", (73728, 74751)),
        ("Cuneiform Numbers and Punctuation", (74752, 74879)),
    ),
    (("Counting Rod Numerals", (119648, 119679)),),
    (("Sundanese", (7040, 7103)),),
    (("Lepcha", (7168, 7247)),),
    (("Ol Chiki", (7248, 7295)),),
    (("Saurashtra", (43136, 43231)),),
    (("Kayah Li", (43264, 43311)),),
    (("Rejang", (43312, 43359)),),
    (("Cham", (43520, 43615)),),
    (("Ancient Symbols", (65936, 65999)),),
    (("Phaistos Disc", (66000, 66047)),),
    (
        ("Carian", (66208, 66271)),
        ("Lycian", (66176, 66207)),
        ("Lydian", (67872, 67903)),
    ),
    (("Domino Tiles", (127024, 127135)), ("Mahjong Tiles", (126976, 127023))),
)
CODEPAGES = [
    (0, "cp1252"),
    (1, "cp1250"),
    (2, "cp1251"),
    (3, "cp1253"),
    (4, "cp1254"),
    (5, "cp1255"),
    (6, "cp1256"),
    (7, "cp1257"),
    (8, "cp1258"),
    (16, "cp874"),
    (17, "cp932"),
    (18, "gbk"),
    (19, "cp949"),
    (20, "cp950"),
    (21, "johab"),
]


def coverage(unicodes: set[int]) -> tuple[list[int], list[tuple]]:
    """Assess all Unicode range bits and printable codepage coverage."""
    codes = set(unicodes)
    rows, bits = [], []
    for bit, blocks in enumerate(UNICODE_RANGES):
        hits = {
            code
            for code in codes
            if any(low <= code <= high for _, (low, high) in blocks)
        }
        if bit == 57:
            hits = {code for code in codes if 0x10000 <= code <= 0x10FFFF}
        if hits:
            bits.append(bit)
            rows.append(
                (
                    f"Unicode bit {bit}",
                    ", ".join(name for name, _ in blocks),
                    len(hits),
                    "Present",
                ),
            )
    for bit, codec in CODEPAGES:
        required = set()
        # Single-byte pages only: multibyte entries are explicitly unassessed.
        if bit >= 17:
            rows.append(
                (f"Codepage bit {bit}", codec, "—", "Multibyte: review manually"),
            )
            continue
        for byte in range(32, 256):
            try:
                character = bytes([byte]).decode(codec)
            except UnicodeDecodeError:
                continue
            if character.isprintable():
                required.add(ord(character))
        missing = required - codes
        rows.append(
            (
                f"Codepage bit {bit}",
                codec,
                len(required & codes),
                "Complete printable coverage"
                if not missing
                else f"{len(missing)} missing",
            ),
        )
    return bits, rows


def run(records: list[tuple[str, list[int]]]) -> tuple[list[int], list[tuple]]:
    """Report coverage of every valid Unicode assignment in the font."""
    return coverage({u for _, codes in records for u in codes if 0 <= u <= 0x10FFFF})


FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    def __init__(self, parent: Any = None) -> None:
        """Open the shared Font Info panel with this tool's controls and preview."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle="Report OS/2 range bits and complete printable codepage coverage from every glyph encoding; no font changes.",
            key=KEY,
        )

    def setup(self) -> None:
        """Build all original controls and connect owned signals."""
        self.records = glyph_records(self.package) if self.package else []
        self.apply_button.setText("Refresh report")

    def refresh(self) -> None:
        """Validate and display a complete preview before enabling Apply."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is None:
            return
        self.ensure_font()
        self.records = glyph_records(self.package)
        bits, rows = run(self.records)
        self.last_result = {"bits": bits, "rows": rows}
        self.rows(["OS/2 flag", "Range / encoding", "Covered", "Assessment"], rows)
        self.status.setText(
            f"{len(bits)} Unicode bits · codepage hints are coverage checks, not export flag recommendations.",
        )
        self.apply_button.setEnabled(True)
        self._preview_valid = True

    def apply(self) -> None:
        """Refresh the original font's coverage without changing font data."""
        self.ensure_preview()
        self.records = glyph_records(self.package)
        self.refresh()


def main() -> Any:
    """Replace this tool's owned dialog using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
