# this_file: Scripts/Reports/Unicode Coverage.py
# SPDX-License-Identifier: Apache-2.0
"""Unicode coverage of the current font, block by block, with progress bars.

What it does:
    For every Unicode block that the font touches, shows how many of the
    block's assigned characters (per Python's unicodedata) have a glyph.
    Double-click a block to select its glyphs in the Font window. Block ranges
    are embedded (planes 0 and 1). Nothing in the font changes.

How it works:
    Collect all font encodings and compare them with embedded Unicode block
    ranges. Count assigned characters with Python's Unicode data and report
    codes outside those ranges.

Why this design:
    Block percentages depend on the assigned-character denominator; displaying
    counts avoids implying complete Unicode support from a progress bar alone.

How to use:
    Run Reports > Unicode Coverage. Inspect covered and assigned counts,
    change the block visibility option and double-click a block to select its
    encoded glyphs.

Benefit:
    Review the reported Unicode-block coverage without assigning code points
    or changing export flags.
"""

import unicodedata
from typing import Any

from fly import ap, qt
from fly.ap.scripting import current_package, select_glyphs

fontlab = ap.fontlab
(QtCore, QtGui) = (qt.QtCore, qt.QtGui)
TITLE = "Unicode Coverage"
KEY = "report_unicode_coverage"
BLOCKS_TEXT = "\n0000 007F Basic Latin\n0080 00FF Latin-1 Supplement\n0100 017F Latin Extended-A\n0180 024F Latin Extended-B\n0250 02AF IPA Extensions\n02B0 02FF Spacing Modifier Letters\n0300 036F Combining Diacritical Marks\n0370 03FF Greek and Coptic\n0400 04FF Cyrillic\n0500 052F Cyrillic Supplement\n0530 058F Armenian\n0590 05FF Hebrew\n0600 06FF Arabic\n0700 074F Syriac\n0750 077F Arabic Supplement\n0780 07BF Thaana\n07C0 07FF NKo\n0800 083F Samaritan\n0840 085F Mandaic\n0860 086F Syriac Supplement\n0870 089F Arabic Extended-B\n08A0 08FF Arabic Extended-A\n0900 097F Devanagari\n0980 09FF Bengali\n0A00 0A7F Gurmukhi\n0A80 0AFF Gujarati\n0B00 0B7F Oriya\n0B80 0BFF Tamil\n0C00 0C7F Telugu\n0C80 0CFF Kannada\n0D00 0D7F Malayalam\n0D80 0DFF Sinhala\n0E00 0E7F Thai\n0E80 0EFF Lao\n0F00 0FFF Tibetan\n1000 109F Myanmar\n10A0 10FF Georgian\n1100 11FF Hangul Jamo\n1200 137F Ethiopic\n1380 139F Ethiopic Supplement\n13A0 13FF Cherokee\n1400 167F Unified Canadian Aboriginal Syllabics\n1680 169F Ogham\n16A0 16FF Runic\n1700 171F Tagalog\n1720 173F Hanunoo\n1740 175F Buhid\n1760 177F Tagbanwa\n1780 17FF Khmer\n1800 18AF Mongolian\n18B0 18FF Unified Canadian Aboriginal Syllabics Extended\n1900 194F Limbu\n1950 197F Tai Le\n1980 19DF New Tai Lue\n19E0 19FF Khmer Symbols\n1A00 1A1F Buginese\n1A20 1AAF Tai Tham\n1AB0 1AFF Combining Diacritical Marks Extended\n1B00 1B7F Balinese\n1B80 1BBF Sundanese\n1BC0 1BFF Batak\n1C00 1C4F Lepcha\n1C50 1C7F Ol Chiki\n1C80 1C8F Cyrillic Extended-C\n1C90 1CBF Georgian Extended\n1CC0 1CCF Sundanese Supplement\n1CD0 1CFF Vedic Extensions\n1D00 1D7F Phonetic Extensions\n1D80 1DBF Phonetic Extensions Supplement\n1DC0 1DFF Combining Diacritical Marks Supplement\n1E00 1EFF Latin Extended Additional\n1F00 1FFF Greek Extended\n2000 206F General Punctuation\n2070 209F Superscripts and Subscripts\n20A0 20CF Currency Symbols\n20D0 20FF Combining Diacritical Marks for Symbols\n2100 214F Letterlike Symbols\n2150 218F Number Forms\n2190 21FF Arrows\n2200 22FF Mathematical Operators\n2300 23FF Miscellaneous Technical\n2400 243F Control Pictures\n2440 245F Optical Character Recognition\n2460 24FF Enclosed Alphanumerics\n2500 257F Box Drawing\n2580 259F Block Elements\n25A0 25FF Geometric Shapes\n2600 26FF Miscellaneous Symbols\n2700 27BF Dingbats\n27C0 27EF Miscellaneous Mathematical Symbols-A\n27F0 27FF Supplemental Arrows-A\n2800 28FF Braille Patterns\n2900 297F Supplemental Arrows-B\n2980 29FF Miscellaneous Mathematical Symbols-B\n2A00 2AFF Supplemental Mathematical Operators\n2B00 2BFF Miscellaneous Symbols and Arrows\n2C00 2C5F Glagolitic\n2C60 2C7F Latin Extended-C\n2C80 2CFF Coptic\n2D00 2D2F Georgian Supplement\n2D30 2D7F Tifinagh\n2D80 2DDF Ethiopic Extended\n2DE0 2DFF Cyrillic Extended-A\n2E00 2E7F Supplemental Punctuation\n2E80 2EFF CJK Radicals Supplement\n2F00 2FDF Kangxi Radicals\n2FF0 2FFF Ideographic Description Characters\n3000 303F CJK Symbols and Punctuation\n3040 309F Hiragana\n30A0 30FF Katakana\n3100 312F Bopomofo\n3130 318F Hangul Compatibility Jamo\n3190 319F Kanbun\n31A0 31BF Bopomofo Extended\n31C0 31EF CJK Strokes\n31F0 31FF Katakana Phonetic Extensions\n3200 32FF Enclosed CJK Letters and Months\n3300 33FF CJK Compatibility\n3400 4DBF CJK Unified Ideographs Extension A\n4DC0 4DFF Yijing Hexagram Symbols\n4E00 9FFF CJK Unified Ideographs\nA000 A48F Yi Syllables\nA490 A4CF Yi Radicals\nA4D0 A4FF Lisu\nA500 A63F Vai\nA640 A69F Cyrillic Extended-B\nA6A0 A6FF Bamum\nA700 A71F Modifier Tone Letters\nA720 A7FF Latin Extended-D\nA800 A82F Syloti Nagri\nA830 A83F Common Indic Number Forms\nA840 A87F Phags-pa\nA880 A8DF Saurashtra\nA8E0 A8FF Devanagari Extended\nA900 A92F Kayah Li\nA930 A95F Rejang\nA960 A97F Hangul Jamo Extended-A\nA980 A9DF Javanese\nA9E0 A9FF Myanmar Extended-B\nAA00 AA5F Cham\nAA60 AA7F Myanmar Extended-A\nAA80 AADF Tai Viet\nAAE0 AAFF Meetei Mayek Extensions\nAB00 AB2F Ethiopic Extended-A\nAB30 AB6F Latin Extended-E\nAB70 ABBF Cherokee Supplement\nABC0 ABFF Meetei Mayek\nAC00 D7AF Hangul Syllables\nD7B0 D7FF Hangul Jamo Extended-B\nD800 DB7F High Surrogates\nDB80 DBFF High Private Use Surrogates\nDC00 DFFF Low Surrogates\nE000 F8FF Private Use Area\nF900 FAFF CJK Compatibility Ideographs\nFB00 FB4F Alphabetic Presentation Forms\nFB50 FDFF Arabic Presentation Forms-A\nFE00 FE0F Variation Selectors\nFE10 FE1F Vertical Forms\nFE20 FE2F Combining Half Marks\nFE30 FE4F CJK Compatibility Forms\nFE50 FE6F Small Form Variants\nFE70 FEFF Arabic Presentation Forms-B\nFF00 FFEF Halfwidth and Fullwidth Forms\nFFF0 FFFF Specials\n10000 1007F Linear B Syllabary\n10080 100FF Linear B Ideograms\n10100 1013F Aegean Numbers\n10140 1018F Ancient Greek Numbers\n10190 101CF Ancient Symbols\n101D0 101FF Phaistos Disc\n10280 1029F Lycian\n102A0 102DF Carian\n102E0 102FF Coptic Epact Numbers\n10300 1032F Old Italic\n10330 1034F Gothic\n10350 1037F Old Permic\n10380 1039F Ugaritic\n103A0 103DF Old Persian\n10400 1044F Deseret\n10450 1047F Shavian\n10480 104AF Osmanya\n104B0 104FF Osage\n10500 1052F Elbasan\n10530 1056F Caucasian Albanian\n10570 105BF Vithkuqi\n105C0 105FF Todhri\n10600 1077F Linear A\n10780 107BF Latin Extended-F\n10800 1083F Cypriot Syllabary\n10840 1085F Imperial Aramaic\n10860 1087F Palmyrene\n10880 108AF Nabataean\n108E0 108FF Hatran\n10900 1091F Phoenician\n10920 1093F Lydian\n10940 1095F Sidetic\n10980 1099F Meroitic Hieroglyphs\n109A0 109FF Meroitic Cursive\n10A00 10A5F Kharoshthi\n10A60 10A7F Old South Arabian\n10A80 10A9F Old North Arabian\n10AC0 10AFF Manichaean\n10B00 10B3F Avestan\n10B40 10B5F Inscriptional Parthian\n10B60 10B7F Inscriptional Pahlavi\n10B80 10BAF Psalter Pahlavi\n10C00 10C4F Old Turkic\n10C80 10CFF Old Hungarian\n10D00 10D3F Hanifi Rohingya\n10D40 10D8F Garay\n10E60 10E7F Rumi Numeral Symbols\n10E80 10EBF Yezidi\n10EC0 10EFF Arabic Extended-C\n10F00 10F2F Old Sogdian\n10F30 10F6F Sogdian\n10F70 10FAF Old Uyghur\n10FB0 10FDF Chorasmian\n10FE0 10FFF Elymaic\n11000 1107F Brahmi\n11080 110CF Kaithi\n110D0 110FF Sora Sompeng\n11100 1114F Chakma\n11150 1117F Mahajani\n11180 111DF Sharada\n111E0 111FF Sinhala Archaic Numbers\n11200 1124F Khojki\n11280 112AF Multani\n112B0 112FF Khudawadi\n11300 1137F Grantha\n11380 113FF Tulu-Tigalari\n11400 1147F Newa\n11480 114DF Tirhuta\n11580 115FF Siddham\n11600 1165F Modi\n11660 1167F Mongolian Supplement\n11680 116CF Takri\n116D0 116FF Myanmar Extended-C\n11700 1174F Ahom\n11800 1184F Dogra\n118A0 118FF Warang Citi\n11900 1195F Dives Akuru\n119A0 119FF Nandinagari\n11A00 11A4F Zanabazar Square\n11A50 11AAF Soyombo\n11AB0 11ABF Unified Canadian Aboriginal Syllabics Extended-A\n11AC0 11AFF Pau Cin Hau\n11B00 11B5F Devanagari Extended-A\n11B60 11B7F Sharada Supplement\n11BC0 11BFF Sunuwar\n11C00 11C6F Bhaiksuki\n11C70 11CBF Marchen\n11D00 11D5F Masaram Gondi\n11D60 11DAF Gunjala Gondi\n11DB0 11DEF Tolong Siki\n11DF0 11DFF Bengali Supplement\n11EE0 11EFF Makasar\n11F00 11F5F Kawi\n11FB0 11FBF Lisu Supplement\n11FC0 11FFF Tamil Supplement\n12000 123FF Cuneiform\n12400 1247F Cuneiform Numbers and Punctuation\n12480 1254F Early Dynastic Cuneiform\n12550 1268F Archaic Cuneiform Numerals\n12F90 12FFF Cypro-Minoan\n13000 1342F Egyptian Hieroglyphs\n13430 1345F Egyptian Hieroglyph Format Controls\n13460 143FF Egyptian Hieroglyphs Extended-A\n14400 1467F Anatolian Hieroglyphs\n16100 1613F Gurung Khema\n16800 16A3F Bamum Supplement\n16A40 16A6F Mro\n16A70 16ACF Tangsa\n16AD0 16AFF Bassa Vah\n16B00 16B8F Pahawh Hmong\n16D40 16D7F Kirat Rai\n16E40 16E9F Medefaidrin\n16EA0 16EDF Beria Erfe\n16F00 16F9F Miao\n16FE0 16FFF Ideographic Symbols and Punctuation\n17000 187FF Tangut\n18800 18AFF Tangut Components\n18B00 18CFF Khitan Small Script\n18D00 18D7F Tangut Supplement\n18D80 18DFF Tangut Components Supplement\n18E00 1919F Jurchen\n191A0 191DF Jurchen Radicals\n1AFF0 1AFFF Kana Extended-B\n1B000 1B0FF Kana Supplement\n1B100 1B12F Kana Extended-A\n1B130 1B16F Small Kana Extension\n1B170 1B2FF Nushu\n1BC00 1BC9F Duployan\n1BCA0 1BCAF Shorthand Format Controls\n1CC00 1CEBF Symbols for Legacy Computing Supplement\n1CEC0 1CEFF Miscellaneous Symbols Supplement\n1CF00 1CFCF Znamenny Musical Notation\n1D000 1D0FF Byzantine Musical Symbols\n1D100 1D1FF Musical Symbols\n1D200 1D24F Ancient Greek Musical Notation\n1D250 1D28F Musical Symbols Supplement\n1D2C0 1D2DF Kaktovik Numerals\n1D2E0 1D2FF Mayan Numerals\n1D300 1D35F Tai Xuan Jing Symbols\n1D360 1D37F Counting Rod Numerals\n1D400 1D7FF Mathematical Alphanumeric Symbols\n1D800 1DAAF Sutton SignWriting\n1DB00 1DBFF Miscellaneous Symbols and Arrows Extended\n1DF00 1DFFF Latin Extended-G\n1E000 1E02F Glagolitic Supplement\n1E030 1E08F Cyrillic Extended-D\n1E100 1E14F Nyiakeng Puachue Hmong\n1E290 1E2BF Toto\n1E2C0 1E2FF Wancho\n1E4D0 1E4FF Nag Mundari\n1E5D0 1E5FF Ol Onal\n1E6C0 1E6FF Tai Yo\n1E7E0 1E7FF Ethiopic Extended-B\n1E800 1E8DF Mende Kikakui\n1E900 1E95F Adlam\n1EC70 1ECBF Indic Siyaq Numbers\n1ED00 1ED4F Ottoman Siyaq Numbers\n1EE00 1EEFF Arabic Mathematical Alphabetic Symbols\n1F000 1F02F Mahjong Tiles\n1F030 1F09F Domino Tiles\n1F0A0 1F0FF Playing Cards\n1F100 1F1FF Enclosed Alphanumeric Supplement\n1F200 1F2FF Enclosed Ideographic Supplement\n1F300 1F5FF Miscellaneous Symbols and Pictographs\n1F600 1F64F Emoticons\n1F650 1F67F Ornamental Dingbats\n1F680 1F6FF Transport and Map Symbols\n1F700 1F77F Alchemical Symbols\n1F780 1F7FF Geometric Shapes Extended\n1F800 1F8FF Supplemental Arrows-C\n1F900 1F9FF Supplemental Symbols and Pictographs\n1FA00 1FA6F Chess Symbols\n1FA70 1FAFF Symbols and Pictographs Extended-A\n1FB00 1FBFF Symbols for Legacy Computing\n"
BLOCKS = [
    (int(a, 16), int(b, 16), name)
    for (a, b, name) in (
        line.split(" ", 2) for line in BLOCKS_TEXT.strip().splitlines()
    )
]


def font_codes() -> Any:
    """{code point: glyph name} of the current font (first glyph wins)."""
    font = fontlab.CurrentFont()
    out = {}
    for glyph in font.glyphs if font is not None else []:
        for code in glyph.unicodes:
            out.setdefault(code, glyph.name)
    return out


def assigned(start: Any, end: Any) -> Any:
    """Number of assigned characters (not Cn) in a range."""
    return sum(
        1 for code in range(start, end + 1) if unicodedata.category(chr(code)) != "Cn"
    )


def coverage(codes: Any, show_all: Any = False) -> Any:
    """[(start, end, block, covered, assigned)] for blocks the font touches (or all blocks)."""
    (rows, outside) = ([], set(codes))
    for start, end, name in BLOCKS:
        inside = [c for c in codes if start <= c <= end]
        outside.difference_update(inside)
        if inside or show_all:
            rows.append((start, end, name, len(inside), assigned(start, end)))
    return (rows, sorted(outside))


def muted(widget: Any) -> Any:
    """Muted."""
    color = QtGui.QColor(widget.palette.color(QtGui.QPalette.WindowText))
    color.setAlpha(150)
    return color.name(QtGui.QColor.HexArgb)


class Coverage(QtGui.QDialog):
    def __init__(self, parent: Any = None) -> None:
        """Build the original modeless report controls and connect owned signals."""
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(TITLE)
        palette = self.palette
        palette.setColor(QtGui.QPalette.Text, palette.color(QtGui.QPalette.WindowText))
        self.setPalette(palette)
        self.setMinimumWidth(600)
        self.resize(640, 520)
        self._connections = []
        self.rows = []
        self.codes = {}
        root = QtGui.QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(12)
        heading = QtGui.QLabel(TITLE)
        font = heading.font
        font.setPointSizeF(font.pointSizeF() * 1.35)
        font.setBold(True)
        heading.setFont(font)
        root.addWidget(heading)
        self.subtitle = QtGui.QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"color: {muted(self)};")
        root.addWidget(self.subtitle)
        self.table = QtGui.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Block", "Range", "Coverage", "Glyphs"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QtGui.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtGui.QHeaderView.Stretch)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        root.addWidget(self.table, 1)
        footer = QtGui.QHBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setStyleSheet(f"color: {muted(self)};")
        footer.addWidget(self.status, 1)
        self.show_all = QtGui.QCheckBox("Show untouched blocks")
        self.refresh_button = QtGui.QPushButton("Refresh")
        self.close_button = QtGui.QPushButton("Close")
        footer.addWidget(self.show_all)
        footer.addWidget(self.refresh_button)
        footer.addWidget(self.close_button)
        root.addLayout(footer)
        self._connect(self.show_all.toggled, lambda *a: self.refresh())
        self._connect(self.refresh_button.clicked, lambda *a: self.refresh())
        self._connect(
            self.table.cellDoubleClicked, lambda row, *a: self.select_block(row)
        )
        self._connect(self.close_button.clicked, lambda *a: self.close())
        self.refresh()

    def _connect(self, signal: Any, slot: Any) -> None:
        """Connect through the shared guarded native lifecycle."""
        ap.scripting.connect_guarded(self, signal, slot)

    def refresh(self) -> None:
        """Rebuild the current snapshot and publish it only after display succeeds."""
        self.package_id = None
        self.codes = {}
        self.rows = []
        self.outside = []
        self.table.setRowCount(0)
        try:
            package = current_package()
            if package is None:
                self.subtitle.setText("Open a font first.")
                return
            result_codes = font_codes()
            (result_rows, result_outside) = coverage(
                list(result_codes), self.show_all.isChecked()
            )
            if not result_codes:
                self.subtitle.setText("Open a font with encoded glyphs first.")
            else:
                full = sum(1 for r in result_rows if r[3] and r[3] >= r[4])
                self.subtitle.setText(
                    f"{len(result_codes)} code points in {sum(1 for r in result_rows if r[3])} blocks; {full} complete. Double-click a block to select its glyphs."
                )
            self.table.setRowCount(len(result_rows))
            for row, (start, end, name, covered, total) in enumerate(result_rows):
                self.table.setItem(row, 0, QtGui.QTableWidgetItem(name))
                span = QtGui.QTableWidgetItem(f"{start:04X}–{end:04X}")
                span.setForeground(QtGui.QBrush(QtGui.QColor(muted(self))))
                self.table.setItem(row, 1, span)
                bar = QtGui.QProgressBar()
                bar.setRange(0, max(1, total))
                bar.setValue(min(covered, max(1, total)))
                bar.setTextVisible(True)
                bar.setFormat(f"{100.0 * covered / total:.0f}%" if total else "–")
                bar.setMaximumHeight(16)
                self.table.setCellWidget(row, 2, bar)
                count = QtGui.QTableWidgetItem(f"{covered} / {total}")
                count.setTextAlignment(
                    int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                )
                self.table.setItem(row, 3, count)
            extra = (
                f" · {len(result_outside)} code points outside planes 0–1"
                if result_outside
                else ""
            )
            self.status.setText(f"{len(result_rows)} blocks listed{extra}")
            self.codes = result_codes
            self.rows = result_rows
            self.outside = result_outside
            self.package_id = package.id
        except Exception:
            self.package_id = None
            self.codes = {}
            self.rows = []
            self.outside = []
            self.table.setRowCount(0)
            raise

    def select_block(self, row: Any) -> None:
        """Select encoded glyphs in the requested block of the scanned font."""
        if self.package_id is None:
            raise ValueError("Refresh the report before selecting glyphs.")
        package = current_package()
        if package is None or package.id != self.package_id:
            raise ValueError("stale font: Refresh the report.")
        if not 0 <= row < len(self.rows):
            return
        (start, end, name) = self.rows[row][:3]
        names = [glyph for (code, glyph) in self.codes.items() if start <= code <= end]
        selected = select_glyphs(names, package_id=self.package_id)
        self.last_result = {"block": name, "selected": selected}
        self.status.setText(
            f"{name}: selected {len(selected)} glyph{('s' if len(selected) != 1 else '')}"
        )

    def closeEvent(self, event: Any) -> None:
        """Release the owned report and its connections."""
        ap.scripting.close_script_dialog(self, event, KEY)


def main() -> Any:
    """Show the persistent modeless report."""
    return ap.scripting.show_script_dialog(Coverage, KEY)


if __name__ == "__main__":
    main()
