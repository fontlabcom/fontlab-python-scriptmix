# this_file: Scripts/Names/Unicode From Names.py
# SPDX-License-Identifier: Apache-2.0
# Adapted from the archived Apache-2.0 FontLab samples
# (rescued/samples/names_unicode_from_names.py); provenance in NOTICE.
# FLM: Names · Unicode From Names
"""Assign Unicode code points that the glyph names imply. Preview first.

WHAT: A non-modal panel reads glyph names and lists the code point each name
implies. It knows uniXXXX and uXXXX[XX] names, a built-in table of Adobe Glyph
List names, and accented Latin names (Wacute is LATIN CAPITAL LETTER W WITH
ACUTE, found with unicodedata). Names with a suffix (a.ss01), ligature names
(f_i) and surrogate code points (U+D800 to U+DFFF) are left alone. Assign writes all rows marked "assign".

HOW: The script scans the font and plans each row: "same" (already right),
"encoded differently" (the glyph has another code and Replace is off), "used by
X" (another glyph already owns the code, or an earlier row claims it), a
refusal reason, or "assign". The write rescans, then sets the code points on
the font-owned FontGate record as one Undo step. It reads each list back and
compares it with the plan. The scan, the refusal policy and the one-step write
come from the App helper fly.ap.names_edit. If a write fails part way, every
planned glyph is still notified and stamped, and the message asks you to use
Edit > Undo.

WHY: A code point must belong to one glyph only. The plan never steals a code
from another glyph and never lets two rows claim one code. FontLab rebuilds all
auto layers when an auto layer, or the base glyph of an auto composite (also
through other composites), is notified, and Undo does not restore them. So the
script REFUSES such glyphs. It never reads flGlyph.fgGlyph, never calls
UpdateAll (fl#8537), and refuses to write while native updates are pending.
Before it writes, the script applies the guards of the App Unicode writer: a
regular Font window must be active and no Glyph editor may be open.

USE: Select glyphs in the Font window, or choose "All glyphs in the font". Run
the script. Check the table. Press Assign.

BENEFIT: Fonts built from named outlines get a correct character map in one
previewed, undoable step.

Credit: adapted from the author's own archived Apache-2.0
FontLab samples. Native acceptance pending.
"""

import re
import unicodedata
from typing import Any

import fly.ap.names_edit as names_edit  # noqa: PLR0402 - fontlabapp.__getattr__ is native

TITLE = "Unicode from Names"
KEY = "names_unicode_from_names"
OPERATION = "unicode"  # names_edit refusal policy for this write
AGL_TEXT = (
    "space 0020 exclam 0021 quotedbl 0022 numbersign 0023 dollar 0024 percent 0025 ampersand 0026 quotesingle 0027 "
    "parenleft 0028 parenright 0029 asterisk 002A plus 002B comma 002C hyphen 002D period 002E slash 002F zero 0030 "
    "one 0031 two 0032 three 0033 four 0034 five 0035 six 0036 seven 0037 eight 0038 nine 0039 colon 003A semicolon "
    "003B less 003C equal 003D greater 003E question 003F at 0040 A 0041 B 0042 C 0043 D 0044 E 0045 F 0046 G 0047 "
    "H 0048 I 0049 J 004A K 004B L 004C M 004D N 004E O 004F P 0050 Q 0051 R 0052 S 0053 T 0054 U 0055 V 0056 W "
    "0057 X 0058 Y 0059 Z 005A bracketleft 005B backslash 005C bracketright 005D asciicircum 005E underscore 005F "
    "grave 0060 a 0061 b 0062 c 0063 d 0064 e 0065 f 0066 g 0067 h 0068 i 0069 j 006A k 006B l 006C m 006D n 006E o "
    "006F p 0070 q 0071 r 0072 s 0073 t 0074 u 0075 v 0076 w 0077 x 0078 y 0079 z 007A braceleft 007B bar 007C "
    "braceright 007D asciitilde 007E exclamdown 00A1 cent 00A2 sterling 00A3 currency 00A4 yen 00A5 brokenbar 00A6 "
    "section 00A7 dieresis 00A8 copyright 00A9 ordfeminine 00AA guillemotleft 00AB logicalnot 00AC registered 00AE "
    "macron 00AF degree 00B0 plusminus 00B1 acute 00B4 mu 00B5 paragraph 00B6 periodcentered 00B7 cedilla 00B8 "
    "ordmasculine 00BA guillemotright 00BB onequarter 00BC onehalf 00BD threequarters 00BE questiondown 00BF Agrave "
    "00C0 Aacute 00C1 Acircumflex 00C2 Atilde 00C3 Adieresis 00C4 Aring 00C5 AE 00C6 Ccedilla 00C7 Egrave 00C8 "
    "Eacute 00C9 Ecircumflex 00CA Edieresis 00CB Igrave 00CC Iacute 00CD Icircumflex 00CE Idieresis 00CF Eth 00D0 "
    "Ntilde 00D1 Ograve 00D2 Oacute 00D3 Ocircumflex 00D4 Otilde 00D5 Odieresis 00D6 multiply 00D7 Oslash 00D8 "
    "Ugrave 00D9 Uacute 00DA Ucircumflex 00DB Udieresis 00DC Yacute 00DD Thorn 00DE germandbls 00DF agrave 00E0 "
    "aacute 00E1 acircumflex 00E2 atilde 00E3 adieresis 00E4 aring 00E5 ae 00E6 ccedilla 00E7 egrave 00E8 eacute "
    "00E9 ecircumflex 00EA edieresis 00EB igrave 00EC iacute 00ED icircumflex 00EE idieresis 00EF eth 00F0 ntilde "
    "00F1 ograve 00F2 oacute 00F3 ocircumflex 00F4 otilde 00F5 odieresis 00F6 divide 00F7 oslash 00F8 ugrave 00F9 "
    "uacute 00FA ucircumflex 00FB udieresis 00FC yacute 00FD thorn 00FE ydieresis 00FF Amacron 0100 amacron 0101 "
    "Abreve 0102 abreve 0103 Aogonek 0104 aogonek 0105 Cacute 0106 cacute 0107 Ccircumflex 0108 ccircumflex 0109 "
    "Cdotaccent 010A cdotaccent 010B Ccaron 010C ccaron 010D Dcaron 010E dcaron 010F Dcroat 0110 dcroat 0111 "
    "Emacron 0112 emacron 0113 Ebreve 0114 ebreve 0115 Edotaccent 0116 edotaccent 0117 Eogonek 0118 eogonek 0119 "
    "Ecaron 011A ecaron 011B Gcircumflex 011C gcircumflex 011D Gbreve 011E gbreve 011F Gdotaccent 0120 gdotaccent "
    "0121 Hcircumflex 0124 hcircumflex 0125 Hbar 0126 hbar 0127 Itilde 0128 itilde 0129 Imacron 012A imacron 012B "
    "Ibreve 012C ibreve 012D Iogonek 012E iogonek 012F Idotaccent 0130 dotlessi 0131 IJ 0132 ij 0133 Jcircumflex "
    "0134 jcircumflex 0135 kgreenlandic 0138 Lacute 0139 lacute 013A Lcaron 013D lcaron 013E Ldot 013F ldot 0140 "
    "Lslash 0141 lslash 0142 Nacute 0143 nacute 0144 Ncaron 0147 ncaron 0148 napostrophe 0149 Eng 014A eng 014B "
    "Omacron 014C omacron 014D Obreve 014E obreve 014F Ohungarumlaut 0150 ohungarumlaut 0151 OE 0152 oe 0153 Racute "
    "0154 racute 0155 Rcaron 0158 rcaron 0159 Sacute 015A sacute 015B Scircumflex 015C scircumflex 015D Scedilla "
    "015E scedilla 015F Scaron 0160 scaron 0161 Tcaron 0164 tcaron 0165 Tbar 0166 tbar 0167 Utilde 0168 utilde 0169 "
    "Umacron 016A umacron 016B Ubreve 016C ubreve 016D Uring 016E uring 016F Uhungarumlaut 0170 uhungarumlaut 0171 "
    "Uogonek 0172 uogonek 0173 Wcircumflex 0174 wcircumflex 0175 Ycircumflex 0176 ycircumflex 0177 Ydieresis 0178 "
    "Zacute 0179 zacute 017A Zdotaccent 017B zdotaccent 017C Zcaron 017D zcaron 017E longs 017F florin 0192 "
    "circumflex 02C6 caron 02C7 breve 02D8 dotaccent 02D9 ring 02DA ogonek 02DB tilde 02DC hungarumlaut 02DD endash "
    "2013 emdash 2014 underscoredbl 2017 quoteleft 2018 quoteright 2019 quotesinglbase 201A quotereversed 201B "
    "quotedblleft 201C quotedblright 201D quotedblbase 201E dagger 2020 daggerdbl 2021 bullet 2022 onedotenleader "
    "2024 twodotenleader 2025 ellipsis 2026 perthousand 2030 minute 2032 second 2033 guilsinglleft 2039 "
    "guilsinglright 203A exclamdbl 203C fraction 2044 Euro 20AC trademark 2122 arrowleft 2190 arrowup 2191 "
    "arrowright 2192 arrowdown 2193 partialdiff 2202 existential 2203 emptyset 2205 Delta 2206 gradient 2207 "
    "element 2208 notelement 2209 suchthat 220B product 220F summation 2211 minus 2212 asteriskmath 2217 radical "
    "221A proportional 221D infinity 221E orthogonal 221F angle 2220 logicaland 2227 logicalor 2228 intersection "
    "2229 integral 222B therefore 2234 similar 223C congruent 2245 approxequal 2248 notequal 2260 equivalence 2261 "
    "lessequal 2264 greaterequal 2265 lozenge 25CA "
    "twosuperior 00B2 threesuperior 00B3 onesuperior 00B9 nbspace 00A0 fi FB01 fl FB02"
)
AGL = dict(
    zip(
        AGL_TEXT.split()[0::2],
        (int(v, 16) for v in AGL_TEXT.split()[1::2]),
        strict=False,
    ),
)
ACCENTS = {
    "acute": "ACUTE",
    "grave": "GRAVE",
    "circumflex": "CIRCUMFLEX",
    "dieresis": "DIAERESIS",
    "tilde": "TILDE",
    "ring": "RING ABOVE",
    "caron": "CARON",
    "breve": "BREVE",
    "macron": "MACRON",
    "ogonek": "OGONEK",
    "cedilla": "CEDILLA",
    "dotaccent": "DOT ABOVE",
    "hungarumlaut": "DOUBLE ACUTE",
    "commaaccent": "COMMA BELOW",
    "dotbelow": "DOT BELOW",
    "hookabove": "HOOK ABOVE",
    "stroke": "STROKE",
}
UNI = re.compile(r"^uni([0-9A-F]{4})$")
U = re.compile(r"^u([0-9A-F]{4,6})$")
MAX_CODE = 0x10FFFF
SURROGATES = range(0xD800, 0xE000)  # never a character


# ------------------------------------------------------------------ core
def code_for_name(name: str) -> tuple[int | None, str]:
    """Return (code point, source) implied by NAME, or (None, "").

    Source is "uni", "u", "AGL" or "derived". Names with a dot after the first
    character (suffixes) or with an underscore (ligatures) imply nothing.
    """
    if "." in name[1:] or "_" in name:
        return None, ""
    match = UNI.match(name) or U.match(name)
    if match:
        code = int(match.group(1), 16)
        if code > MAX_CODE or code in SURROGATES:
            return None, ""
        return code, "uni" if name.startswith("uni") else "u"
    if name in AGL:
        return AGL[name], "AGL"
    for accent, words in ACCENTS.items():
        if name.endswith(accent) and len(name) > len(accent):
            base = name[: -len(accent)]
            if len(base) == 1 and base.isalpha():
                case = "CAPITAL" if base.isupper() else "SMALL"
                try:
                    letter = unicodedata.lookup(
                        f"LATIN {case} LETTER {base.upper()} WITH {words}"
                    )
                except KeyError:
                    return None, ""
                return ord(letter), "derived"
    return None, ""


def plan_unicodes(
    facts: names_edit.Facts, names: list[str], overwrite: bool
) -> list[tuple[str, list[int], int, str, str]]:
    """Return (name, current codes, implied code, source, status) for each implying name.

    Status is "same", "assign", "encoded differently", "used by <glyph>" or a
    refusal reason. A row that is "assign" claims its code, so a later row with
    the same code reads "used by <first glyph>".
    """
    owners: dict[int, str] = {}
    for glyph_name, entry in facts.entries.items():
        for code in entry.record.unicodes:
            owners.setdefault(int(code), glyph_name)
    rows = []
    for name in names:
        code, source = code_for_name(name)
        if code is None:
            continue
        if name not in facts.entries:
            rows.append((name, [], code, source, "not in font"))
            continue
        current = [int(c) for c in facts.entries[name].record.unicodes]
        if code in current:
            status = "same"
        elif reason := names_edit.refusal(facts, name, OPERATION):
            status = reason
        elif current and not overwrite:
            status = "encoded differently"
        elif owners.get(code, name) != name:
            status = f"used by {owners[code]}"
        else:
            status = "assign"
            owners[code] = name
        rows.append((name, current, code, source, status))
    return rows


def unicode_write_guard(package_id: int) -> None:
    """Apply the App Unicode writer guards before any history call.

    A regular Font window must be active, and no Glyph editor may be open, even
    inactive (the host has a Unicode save-cache gap). The public App guards
    (fly.ap.edit_guards) do both checks; the editor scan has a 2-second limit.
    """
    import fly.ap.edit_guards as edit_guards  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    edit_guards.require_selection_window(package_id)
    edit_guards.require_no_editors()


def apply_unicodes(
    native: Any, qtcore: Any, package_id: int, names: list[str], overwrite: bool
) -> list[str]:
    """Assign the implied code points to NAMES. One Undo step. Return names changed.

    Rescan first, so a stale preview cannot write. Raise ValueError for an
    empty selection, a switched font or pending host updates.
    """
    if not names:
        raise ValueError("Select at least one glyph.")
    facts = names_edit.fresh_facts(package_id, native=native)
    todo = [
        (facts.entries[name], code)
        for name, _, code, _, status in plan_unicodes(facts, names, overwrite)
        if status == "assign"
    ]
    if not todo:
        return []
    unicode_write_guard(package_id)

    def mutate() -> None:
        for entry, code in todo:
            entry.record.unicodes = [code]
            if [int(c) for c in entry.record.unicodes] != [code]:
                raise RuntimeError(
                    f"Native Unicode of {entry.name} differs from the plan."
                )

    names_edit.commit(
        TITLE,
        [entry for entry, _ in todo],
        mutate,
        operation=OPERATION,
        facts=facts,
        native=native,
        stamp=qtcore.QDateTime.currentDateTimeUtc(),
    )
    return [entry.name for entry, _ in todo]


def hexes(codes: list[int]) -> str:
    """Return codes as "U+0041 U+0042", or an en dash for none."""
    return " ".join(f"U+{c:04X}" for c in codes) or "–"


# ------------------------------------------------------------------ panel
def _dialog_type() -> type:
    """Build the panel class lazily. Import Qt and App code only inside FontLab."""
    from fly import ap, qt
    from fly.ap.scripting import names_dialog_type, names_selected_names

    native = ap.fontlab
    QtCore, QtGui = qt.QtCore, qt.QtGui

    class UnicodeFromNames(names_dialog_type()):
        """Modeless Unicode assigner with a preview."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.setMinimumWidth(560)
            self.facts: names_edit.Facts | None = None
            self.names: list[str] = []
            self.plan: list[tuple[str, list[int], int, str, str]] = []
            form = QtGui.QGridLayout()
            form.setHorizontalSpacing(10)
            form.setVerticalSpacing(8)
            self.scope = QtGui.QComboBox()
            self.scope.addItem("Selected glyphs (0)")
            self.scope.addItem("All glyphs in the font")
            self.overwrite = QtGui.QCheckBox(
                "Replace existing code points (the glyph's other code points are dropped)"
            )
            form.addWidget(QtGui.QLabel("Glyphs"), 0, 0)
            form.addWidget(self.scope, 0, 1)
            form.addWidget(self.overwrite, 1, 1)
            form.setColumnStretch(1, 1)
            self.root.addLayout(form)
            self.table = self.make_table(
                ["Glyph", "Current", "From name", "Source", "Action"]
            )
            self.table.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(QtGui.QHeaderView.Stretch)
            header.setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.table.setMinimumHeight(240)
            self.root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel()
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.show_all = QtGui.QCheckBox("Show unchanged")
            footer.addWidget(self.show_all)
            self.reload_button = QtGui.QPushButton("Reload selection")
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Assign")
            self.apply_button.setDefault(True)
            footer.addWidget(self.reload_button)
            footer.addWidget(self.close_button)
            footer.addWidget(self.apply_button)
            self.root.addLayout(footer)
            self._connect(self.scope.currentIndexChanged, lambda *a: self.refresh())
            self._connect(self.overwrite.toggled, lambda *a: self.refresh())
            self._connect(self.show_all.toggled, lambda *a: self.refresh())
            self._connect(self.reload_button.clicked, lambda *a: self.reload())
            self._connect(self.apply_button.clicked, lambda *a: self.apply())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.reload()

        def invalidate(self) -> None:
            """Also disable Assign when the snapshot is stale."""
            super().invalidate()
            button = getattr(self, "apply_button", None)
            if button is not None:
                button.setEnabled(False)

        def scope_names(self) -> list[str]:
            """Return the glyph names the scope combo selects."""
            if self.facts is None:
                return []
            return (
                self.names if self.scope.currentIndex == 0 else list(self.facts.entries)
            )

        def reload(self) -> None:
            """Rescan the font and re-read the selection."""
            try:
                self.facts = names_edit.scan(native)
                self.names = [
                    n for n in names_selected_names() if n in self.facts.entries
                ]
            except ValueError as error:
                self.facts, self.names = None, []
                self.subtitle.setText(str(error))
            self.scope.setItemText(0, f"Selected glyphs ({len(self.names)})")
            if not self.names:
                self.scope.setCurrentIndex(1)
            self.refresh()

        def refresh(self) -> None:
            """Rebuild the preview from the snapshot."""
            if self.facts is None:
                self.apply_button.setEnabled(False)
                self.plan = []
                self.table.setRowCount(0)
                return
            names = self.scope_names()
            self.plan = plan_unicodes(self.facts, names, self.overwrite.isChecked())
            shown = [
                r for r in self.plan if r[4] != "same" or self.show_all.isChecked()
            ]
            self.subtitle.setText(
                f"{len(names)} glyph{'s' if len(names) != 1 else ''} checked. Names like uni0141, "
                "u1F600, Lslash or Wacute give a code point. Suffixed names are skipped."
            )
            accent = QtGui.QColor(self.palette.color(QtGui.QPalette.Link))
            alert = QtGui.QColor("#d33")
            self.table.setRowCount(len(shown))
            for row, (name, current, code, source, status) in enumerate(shown):
                cells = [name, hexes(current), hexes([code]), source, status]
                for column, text in enumerate(cells):
                    item = QtGui.QTableWidgetItem(text)
                    if column == 2 and status == "assign":
                        item.setForeground(QtGui.QBrush(accent))
                    if column == 4 and status not in {"assign", "same"}:
                        item.setForeground(QtGui.QBrush(alert))
                    self.table.setItem(row, column, item)
            todo = sum(1 for r in self.plan if r[4] == "assign")
            same = sum(1 for r in self.plan if r[4] == "same")
            blocked = len(self.plan) - todo - same
            self.apply_button.setEnabled(todo > 0)
            self.status.setText(
                f"{todo} to assign · {blocked} blocked · {same} already right"
            )

        def apply(self) -> None:
            """Assign the implied code points. One Undo step."""
            changed = apply_unicodes(
                native,
                QtCore,
                self.facts.package_id if self.facts else -1,
                self.scope_names(),
                self.overwrite.isChecked(),
            )
            self.last_result = {"changed": changed}
            self.reload()
            noun = "code point" if len(changed) == 1 else "code points"
            self.status.setText(f"Assigned {len(changed)} {noun}")

    return UnicodeFromNames


def main() -> Any:
    """Open or replace the Unicode from Names panel."""
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(_dialog_type(), KEY)


if __name__ == "__main__":
    main()
