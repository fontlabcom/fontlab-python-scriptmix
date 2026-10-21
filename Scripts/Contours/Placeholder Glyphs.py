# this_file: Scripts/Contours/Placeholder Glyphs.py
# SPDX-License-Identifier: Apache-2.0
"""Create empty placeholder glyphs from typed glyph names or characters, on every master.

What it does:
    Type or paste glyph names and characters, separated by spaces, commas or
    new lines. The script creates one empty glyph per entry, with a layer on
    every master and the chosen advance width. A single non-ASCII character becomes
    uniXXXX (or uXXXXX) and gets that code point. A name of that form also
    gets its code point, unless another glyph has it already. ASCII tokens
    are glyph names: A stays A; & and 1 are invalid names.

How it works:
    A small non-modal panel shows a live table: the name, the code point and
    what will happen. Existing glyphs, repeated entries and invalid names
    are listed and skipped. Create checks the font again. FontLab's own Add
    Glyph command makes each new glyph with a layer on every master, the
    advance width and the code point (shared module fly.ap.glyph_creation).
    After the write the script reads every new glyph back, and checks that
    no automatic glyph of the font changed.

Why this design:
    - Placeholders let you build features, classes, kerning groups and test
      strings before the drawings exist. Unlike Font > Add Glyphs, the panel
      takes characters directly, previews every name and code point, and
      skips what exists instead of asking.
    - An existing glyph is never overwritten, and a code point that another
      glyph has is never assigned twice.
    - FontLab's text conversion can change some characters, so the script
      refuses text with NUL, no-break space or the Unicode line and paragraph
      separators instead of creating changed names.
    - A code point write needs an active Font window and no open Glyph
      window, as every Unicode writer of this menu does. Create is
      refused while FontLab has pending glyph updates. The script does not
      call UpdateAll (fl#8537).
    - FontLab can rebuild an automatic glyph when a new name appears. When
      the font has automatic glyphs without a recipe whose names share a
      dotted suffix with a new name (a new e.sc and eacute.sc), the row
      shows "may rebuild auto ..." and is skipped unless you tick "Create
      even if FontLab may rebuild these auto glyphs". A change of the text
      clears the tick.
    - Each new glyph is recorded as its own Undo step.

How to use:
    Open a font and activate its Font window. Run the script. Type the names
    or characters, set the advance width, check the table and press Create.

Benefit:
    A complete glyph set skeleton, named and encoded, in seconds.

Credit:
    Adapted from the author's own FontLab sample, Apache-2.0
    (generate_placeholder_glyphs.py, "Placeholder Glyphs").
"""

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

TITLE = "Placeholder Glyphs"
KEY = "generate_placeholder_glyphs"
NAME = re.compile(r"[A-Za-z_.][A-Za-z0-9_.-]*")
UNI = re.compile(r"uni([0-9A-F]{4})|u([0-9A-F]{5,6})")
UNSAFE = (
    ("\x00", "NUL"),
    ("\u00a0", "no-break space"),
    ("\u2028", "line separator"),
    ("\u2029", "paragraph separator"),
)  # characters that FontLab's text conversion can change
MAX_ROWS = 500  # preview rows shown; Create always uses every row


@dataclass(frozen=True)
class Entry:
    """One typed token, the glyph name it stands for, and a parse problem (or "")."""

    token: str
    name: str
    problem: str = ""


@dataclass(frozen=True)
class Row:
    """One planned glyph: code point to assign (or None), note, problem (set: skipped).

    ``rebuild``: automatic glyphs that FontLab may rebuild when the glyph
    appears (``glyph_creation.auto_candidates``).
    """

    name: str
    code: int | None
    note: str = ""
    problem: str = ""
    rebuild: tuple[str, ...] = ()


def check_text(text: str) -> None:
    """Raise ValueError when ``text`` holds a character that FontLab can change."""
    found = [label for char, label in UNSAFE if char in text]
    if found:
        raise ValueError(
            "Refused: the text holds "
            + ", ".join(found)
            + ". FontLab's text conversion can change it; "
            "remove it and type the names again."
        )


def char_name(char: str) -> str:
    """Return uniXXXX for a BMP character, uXXXXX above it."""
    code = ord(char)
    return f"uni{code:04X}" if code <= 0xFFFF else f"u{code:X}"


def code_of(name: str) -> int | None:
    """Return the code point that a uniXXXX / uXXXXX name stands for, else None.

    Surrogates and values above U+10FFFF are not characters: None.
    """
    match = UNI.fullmatch(name)
    if match is None:
        return None
    code = int(match.group(1) or match.group(2), 16)
    return None if 0xD800 <= code <= 0xDFFF or code > 0x10FFFF else code


def parse(text: str) -> list[Entry]:
    """Return one Entry per token. A single non-ASCII character becomes uniXXXX."""
    check_text(text)
    entries: list[Entry] = []
    seen: set[str] = set()
    for token in re.split(r"[\s,]+", text.strip()):
        if not token:
            continue
        name = char_name(token) if len(token) == 1 and not token.isascii() else token
        if not NAME.fullmatch(name):
            entries.append(Entry(token, name, "invalid name"))
        elif name in seen:
            entries.append(Entry(token, name, "repeated"))
        else:
            seen.add(name)
            entries.append(Entry(token, name))
    return entries


def font_codes() -> dict[int, str]:
    """Return {code point: glyph name} from the font-owned glyph records."""
    from fly import ap

    font = ap.fontlab.CurrentFont()
    if font is None:
        return {}
    return {
        int(code): str(record.name)
        for record in font.glyphs
        for code in record.unicodes
    }


def plan(
    entries: Sequence[Entry], exists: Callable[[str], bool], codes: dict[int, str]
) -> list[Row]:
    """Return one Row per entry: skip problems and existing glyphs, never reuse a code point."""
    rows: list[Row] = []
    for entry in entries:
        if entry.problem:
            rows.append(Row(entry.name, None, problem=entry.problem))
            continue
        if exists(entry.name):
            rows.append(Row(entry.name, None, problem="exists"))
            continue
        code = code_of(entry.name)
        if code is None:
            rows.append(Row(entry.name, None))
        elif code in codes:
            rows.append(
                Row(entry.name, None, f"U+{code:04X} is on {codes[code]}: not assigned")
            )
        else:
            rows.append(Row(entry.name, code, f"U+{code:04X}"))
    return rows


def gate(
    package: Any, rows: Sequence[Row], facts: Any, allow_rebuild: bool
) -> list[Row]:
    """Mark each ready row that can make FontLab rebuild automatic glyphs.

    The row gets ``rebuild``; without ``allow_rebuild`` its problem is the
    "may rebuild auto ..." note, so it is skipped.
    """
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    found = glyph_creation.auto_candidates(
        package, facts, [r.name for r in rows if not r.problem]
    )
    gated = []
    for row in rows:
        owners = () if row.problem else found.get(row.name, ())
        problem = (
            glyph_creation.rebuild_note(owners)
            if owners and not allow_rebuild
            else row.problem
        )
        gated.append(Row(row.name, row.code, row.note, problem, owners))
    return gated


def create(
    package: Any,
    rows: Sequence[Row],
    advance: int,
    facts: Any,
    allow_rebuild: bool = False,
) -> dict[str, Any]:
    """Create every ready row as an empty glyph on all masters with FontLab's Add Glyph command.

    Return ``{"glyphs", "layers", "codes", "mismatches"}``. Nothing ready
    returns zeros and makes no native call. A name or code point that is
    taken now, an unconsented rebuild, a code point without an active Font
    window or with an open Glyph window, or pending native updates raise
    ValueError before any change. A failure after the first glyph exists
    raises RuntimeError that names the new glyphs.
    """
    import fly.ap.edit_guards as edit_guards  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.glyph_copies as glyph_copies  # noqa: PLR0402
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402
    from fly import ap

    ready = [r for r in rows if not r.problem]
    coded = [r for r in ready if r.code is not None]
    masters = list(package.masters)
    if not ready:
        return {"glyphs": 0, "layers": 0, "codes": 0, "mismatches": []}
    if coded:
        edit_guards.require_selection_window(int(package.id))
        edit_guards.require_no_editors()
    taken = font_codes()
    for row in ready:
        if row.code is not None and row.code in taken:
            raise ValueError(
                f"Refused: U+{row.code:04X} is on {taken[row.code]} now. Check the list again."
            )
    specs = [
        glyph_creation.NewGlyph(
            row.name,
            tuple((m, advance) for m in masters),
            () if row.code is None else (row.code,),
        )
        for row in ready
    ]

    def read_back() -> list[str]:
        font = ap.fontlab.CurrentFont()
        found = (
            {int(record.id): record for record in font.glyphs}
            if coded and font is not None
            else {}
        )
        problems = []
        for row in ready:
            glyph = package.findName(row.name)
            if glyph is None:
                problems.append(f"{row.name}: missing after the write")
                continue
            for master in masters:
                layer = glyph.findLayer(master)
                width = (
                    glyph_copies.half_up(layer.advanceWidth)
                    if layer is not None and not layer.isNull
                    else None
                )
                if width != advance:
                    problems.append(
                        f"{row.name} · {master}: width {width}, planned {advance}"
                    )
            if row.code is not None:
                record = found.get(int(glyph.fgGlyphId))
                codes = list(record.unicodes) if record is not None else []
                if codes != [row.code]:
                    problems.append(
                        f"{row.name}: Unicode is {codes}, planned U+{row.code:04X}"
                    )
        return problems

    done = glyph_creation.create_glyphs(
        package, specs, TITLE, facts, read_back=read_back, allow_rebuild=allow_rebuild
    )
    return {
        "glyphs": len(ready),
        "layers": len(ready) * len(masters),
        "codes": len(coded),
        "mismatches": list(done.mismatches),
    }


def panel_type() -> type:
    """Build the panel class once Qt is available (inside FontLab)."""
    import fly.ap.glyph_creation as glyph_creation  # noqa: PLR0402 - fontlabapp.__getattr__ is native
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.layer_writer as layer_writer  # noqa: PLR0402
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    QtGui = qt.QtGui
    plural = layer_writer.plural

    class PlaceholderPanel(QtGui.QDialog):
        """Names, advance width, rebuild consent, live preview table, status and buttons."""

        def __init__(self, parent: Any = None) -> None:
            QtGui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.rows: list[Row] = []
            self.package_id: int | None = None
            self.facts: Any = None
            self.last_result: dict[str, Any] = {}
            self.setWindowTitle(TITLE)
            self.setMinimumWidth(540)
            root = QtGui.QVBoxLayout(self)
            root.setContentsMargins(20, 18, 20, 16)
            root.setSpacing(12)
            heading = QtGui.QLabel(TITLE)
            face = heading.font
            face.setPointSizeF(face.pointSizeF() * 1.35)
            face.setBold(True)
            heading.setFont(face)
            root.addWidget(heading)
            self.subtitle = QtGui.QLabel("")
            self.subtitle.setWordWrap(True)
            root.addWidget(self.subtitle)
            self.names = QtGui.QPlainTextEdit()
            self.names.setPlaceholderText("e.g.  A.alt  ampersand.ss01  Ω  ₿")
            self.names.setMaximumHeight(90)
            root.addWidget(self.names)
            grid = QtGui.QGridLayout()
            grid.setHorizontalSpacing(10)
            self.advance = QtGui.QSpinBox()
            self.advance.setRange(0, 4000)
            self.advance.setSuffix(" units")
            self.advance.setValue(600)
            grid.addWidget(QtGui.QLabel("Advance width"), 0, 0)
            grid.addWidget(self.advance, 0, 1)
            self.consent = QtGui.QCheckBox(glyph_creation.REBUILD_LABEL)
            grid.addWidget(self.consent, 1, 0, 1, 3)
            grid.setColumnStretch(2, 1)
            root.addLayout(grid)
            self.table = QtGui.QTableWidget(0, 3)
            self.table.setHorizontalHeaderLabels(["Glyph", "Unicode", "Action"])
            self.table.verticalHeader().setVisible(False)
            self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            self.table.horizontalHeader().setSectionResizeMode(
                QtGui.QHeaderView.Stretch
            )
            self.table.setMinimumHeight(200)
            root.addWidget(self.table, 1)
            footer = QtGui.QHBoxLayout()
            self.status = QtGui.QLabel("")
            self.status.setWordWrap(True)
            footer.addWidget(self.status, 1)
            self.close_button = QtGui.QPushButton("Close")
            self.apply_button = QtGui.QPushButton("Create")
            self.apply_button.setDefault(True)
            footer.addWidget(self.close_button)
            footer.addWidget(self.apply_button)
            root.addLayout(footer)
            for signal, slot in (
                (self.names.textChanged, lambda *a: self.text_changed()),
                (self.consent.toggled, lambda *a: self.refresh()),
                (self.apply_button.clicked, lambda *a: self.apply()),
                (self.close_button.clicked, lambda *a: self.close()),
            ):
                scripting.connect_guarded(self, signal, slot)
            try:
                package = scripting.current_package()
                if package is not None:
                    self.package_id = package.id
                    self.facts = history.scan_auto_facts(package)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))
            self.refresh()

        def font_package(self) -> Any:
            """Return the bound font. Refuse a closed or switched font."""
            if self.package_id is None:
                raise ValueError("Open a font first. Then run this script again.")
            package = scripting.current_package()
            if package is None or package.id != self.package_id:
                raise ValueError("The font changed. Run this script again.")
            return package

        def consented(self) -> bool:
            """True when the user ticked the rebuild consent."""
            return bool(self.consent.isChecked())

        def plan(self, facts: Any = None) -> list[Row]:
            """Plan the typed text against the live font; gate rebuild candidates."""
            package = self.font_package()
            entries = parse(self.names.toPlainText())
            rows = plan(
                entries, lambda name: package.findName(name) is not None, font_codes()
            )
            if facts is None:
                if self.facts is None:
                    self.facts = history.scan_auto_facts(package)
                facts = self.facts
            return gate(package, rows, facts, self.consented())

        def text_changed(self) -> None:
            """New text: clear the rebuild consent, then plan again."""
            self.consent.setChecked(False)
            self.refresh()

        def refresh(self) -> None:
            """Recompute the preview. A refusal disables Create and shows its reason."""
            try:
                self.rows = self.plan()
                masters = len(self.font_package().masters)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.rows = []
                self.table.setRowCount(0)
                self.subtitle.setText(str(error))
                self.apply_button.setEnabled(False)
                return
            self.subtitle.setText(
                f"Creates empty glyphs on all {masters} masters. Existing glyphs are never overwritten."
            )
            visible = self.rows[:MAX_ROWS]
            self.table.setRowCount(len(visible))
            for number, row in enumerate(visible):
                action = (
                    f"{row.problem}: skipped"
                    if row.problem
                    else f"create on {masters} masters"
                )
                if row.rebuild and not row.problem:
                    action += " · " + glyph_creation.rebuild_note(row.rebuild)
                for column, text in enumerate((row.name, row.note, action)):
                    self.table.setItem(number, column, QtGui.QTableWidgetItem(text))
            ready = sum(1 for r in self.rows if not r.problem)
            self.apply_button.setEnabled(ready > 0)
            more = (
                f" (table shows the first {MAX_ROWS})"
                if len(self.rows) > MAX_ROWS
                else ""
            )
            self.status.setText(
                f"{plural(ready, 'glyph')} to create · {len(self.rows) - ready} skipped{more}"
            )

        def apply(self) -> None:
            """Scan the font again, plan, then create each glyph with FontLab's Add Glyph command."""
            try:
                package = self.font_package()
                facts = history.scan_auto_facts(package)
                rows = self.plan(facts)
                result = create(
                    package, rows, int(self.advance.value), facts, self.consented()
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.refresh()
                self.status.setText(str(error))
                return
            self.facts = facts
            self.last_result = result
            self.refresh()
            if not result["glyphs"]:
                self.status.setText("Nothing to create")
                return
            text = (
                f"Created {plural(result['glyphs'], 'glyph')} ({plural(result['layers'], 'master layer')}, "
                f"{plural(result['codes'], 'code point')})"
            )
            if result["mismatches"]:
                text += " · did not read back as planned: " + "; ".join(
                    result["mismatches"][:5]
                )
            self.status.setText(text)

        def closeEvent(self, event: Any) -> None:
            """Disconnect owned signals, then delete the panel."""
            scripting.close_script_dialog(self, event, KEY)

    return PlaceholderPanel


def main() -> Any:
    """Open the panel. A second run replaces the first panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - fontlabapp.__getattr__ is native

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
