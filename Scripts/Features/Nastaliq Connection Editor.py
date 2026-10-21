# this_file: Scripts/Features/Nastaliq Connection Editor.py
# SPDX-License-Identifier: Apache-2.0
"""Edit Qalmi Nastaliq connections and save reverse substitutions in the font.

What: Choose a left medial/final glyph, a right medial/initial family and its
numbered alternate. Preview entry/exit alignment on any master. Previous and
Next step through actual alternates, including s/sd forms.
How: Save connection writes a named lookup inside rlig through Fontport's
exact-source writer. A JSON comment in that lookup stores the choices, so
reopening the tool restores them. Each save is recorded as one Undo step.
Existing rlig statements and all other feature blocks stay in place. Earlier
unmanaged reverse rules are listed as a warning because they can run first.
Saved pairs with missing glyphs appear as named kept rows and produce no rules;
their records stay in the font until Drop stale pairs on Save is ticked.
Why: FontLab's Features panel edits source text. This panel adds Qalmi pair
selection, aligned outlines and grouped reverse contextual substitutions.
Use: Open a Qalmi-named font. Choose a pair and alternate, inspect the preview,
then Save connection. Compile and test the feature in FontLab's Features panel.
Reload reads saved choices. Closing without Save does not change that pair.
Benefit: Review and persist connections without editing feature syntax.

Credit: Independent behaviour-only rewrite of Simon Cozens,
GlyphsScripts/Nastaliq Connection Editor.py, MIT, copyright 2017.
Repository: https://github.com/simoncozens/GlyphsScripts . No source code copied.
"""

import json
import re
from typing import Any

TITLE = "Nastaliq Connection Editor"
KEY = "features_nastaliq_connections"
START = "# FontLab Qalmi connections begin"
END = "# FontLab Qalmi connections end"
DATA = "# Qalmi choices: "
LOOKUP = "FontLabQalmiConnections"
FORM = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*?)([mif])(sd|s)?([0-9]+)$")
Choices = dict[tuple[str, str], str]


def name_order(name: str) -> tuple[str, int, str]:
    """Sort by family and numeric suffix, with the source's paired rasm order."""
    match = re.fullmatch(r"(.*?)([0-9]+)", name)
    head, number = (match[1], int(match[2])) if match else (name, 0)
    head = re.sub(r"^GAF", "KAF", re.sub(r"^TE", "BE", head))
    return head, number, name


def inventory(names: list[str]) -> tuple[list[str], list[str], dict[str, list[str]]]:
    """Return left glyphs, right families and actual numbered variants."""
    left, alternatives = [], {}
    has_medial = False
    for name in sorted(set(names), key=name_order):
        match = FORM.fullmatch(name)
        if match is None or re.fullmatch(r"uni[0-9A-Fa-f]{4,6}", name):
            continue
        stem, form, _modifier, _ = match.groups()
        if form in "mf":
            left.append(name)
        if form == "m":
            has_medial = True
        if form in "mi":
            alternatives.setdefault(stem + form, []).append(name)
    if not has_medial:
        raise ValueError(
            "No Qalmi medial names. Use names such as BEm1, BEi1 and BEf1."
        )
    alternatives = {
        stem: variants for stem, variants in alternatives.items() if stem + "1" in names
    }
    if not alternatives:
        raise ValueError(
            "No right family has its numbered default glyph, such as BEm1."
        )
    return left, sorted(alternatives), alternatives


def saved_choices(code: str) -> Choices:
    """Read our exact managed comment; refuse ambiguous or malformed records."""
    if START not in code and END not in code:
        return {}
    if (
        code.count(START) != 1
        or code.count(END) != 1
        or code.index(START) >= code.index(END)
    ):
        raise ValueError("Connection source markers are incomplete or repeated.")
    section = code.split(START, 1)[1].split(END, 1)[0]
    records = [
        line[len(DATA) :] for line in section.splitlines() if line.startswith(DATA)
    ]
    if len(records) != 1:
        raise ValueError("Connection source needs one saved-choice record.")
    try:
        rows = json.loads(records[0])
    except (ValueError, TypeError) as error:
        raise ValueError("Saved connection choices are not valid JSON.") from error
    if not isinstance(rows, list) or any(
        not isinstance(row, list)
        or len(row) != 3
        or any(not isinstance(value, str) for value in row)
        for row in rows
    ):
        raise ValueError("Saved connection choices must contain three names per row.")
    result = {(left, stem): replacement for left, stem, replacement in rows}
    if len(result) != len(rows):
        raise ValueError("A saved connection pair is listed twice.")
    return result


def pair_problem(left: str, stem: str, replacement: str, names: set[str]) -> str:
    """Explain an invalid pair without losing its saved record."""
    left_form, right_form = FORM.fullmatch(left), FORM.fullmatch(replacement)
    if (
        left_form is None
        or left_form[2] not in "mf"
        or right_form is None
        or right_form[2] not in "mi"
        or right_form[1] + right_form[2] != stem
        or re.fullmatch(r"uni[0-9A-Fa-f]{4,6}", left)
        or re.fullmatch(r"uni[0-9A-Fa-f]{4,6}", replacement)
    ):
        return f"invalid Qalmi names: {left} / {stem} / {replacement}"
    missing = sorted({left, stem + "1", replacement} - names)
    return "missing glyphs: " + ", ".join(missing) if missing else ""


def partition_choices(
    choices: Choices, names: set[str]
) -> tuple[Choices, dict[tuple[str, str], str]]:
    """Separate usable choices from stale records; the caller keeps both."""
    valid, stale = {}, {}
    for (left, stem), replacement in choices.items():
        reason = pair_problem(left, stem, replacement, names)
        if reason:
            stale[left, stem] = reason
        else:
            valid[left, stem] = replacement
    return valid, stale


def connection_block(choices: Choices, names: set[str]) -> str:
    """Compile valid pairs only; retain stale choices as JSON without rules."""
    valid, stale = partition_choices(choices, names)
    rules: dict[tuple[str, str], list[str]] = {}
    saved = []
    for (left, stem), replacement in sorted(choices.items()):
        if (left, stem) not in stale and replacement == stem + "1":
            continue
        saved.append([left, stem, replacement])
        if (left, stem) in valid:
            rules.setdefault((stem + "1", replacement), []).append(left)
    lines = [
        START,
        DATA + json.dumps(saved, separators=(",", ":")),
        f"lookup {LOOKUP} {{",
        "lookupflag IgnoreMarks;",
    ]
    for (base, replacement), context in sorted(rules.items()):
        group = context[0] if len(context) == 1 else "[" + " ".join(context) + "]"
        lines.append(f"rsub {base}' {group} by {replacement};")
    if not rules:
        return "\n".join(lines[:2] + [END]) + "\n"
    return "\n".join(lines + [f"}} {LOOKUP};", END]) + "\n"


def unmanaged_rule_bases(blocks: dict[str, Any]) -> list[str]:
    """Find earlier bare reverse rules outside the tool's managed region."""
    code = "\n".join(text for tag, text in blocks["features"] if tag == "rlig")
    saved_choices(code)
    if START in code:
        code = code[: code.index(START)] + code[code.index(END) + len(END) :]
    plain = re.sub(r"#[^\n]*", "", code)
    return sorted(set(re.findall(r"\brsub\s+([A-Za-z_][A-Za-z0-9_.-]*1)\s*'", plain)))


def merge_feature(blocks: dict[str, Any], snippet: str) -> dict[str, Any]:
    """Replace our region, or insert before a single rlig closing statement."""
    features = list(blocks["features"])
    matches = [i for i, (tag, _) in enumerate(features) if tag == "rlig"]
    if len(matches) > 1:
        raise ValueError(
            "Several rlig blocks exist. Consolidate them in the Features panel first."
        )
    index = matches[0] if matches else len(features)
    code = features[index][1] if matches else "feature rlig {\n} rlig;\n"
    saved_choices(code)  # Validate ownership markers before any replacement.
    outside = code
    if START in code:
        outside = code[: code.index(START)] + code[code.index(END) + len(END) :]
    outside += (
        "\n"
        + blocks["prefix"]
        + "\n"
        + "\n".join(text for i, (_, text) in enumerate(features) if i != index)
    )
    if re.search(r"\b" + LOOKUP + r"\b", re.sub(r"#[^\n]*", "", outside)):
        raise ValueError(
            "The connection lookup name is already in use outside its own block."
        )
    if START in code:
        begin, end = code.index(START), code.index(END) + len(END)
        if code[end : end + 1] == "\n":
            end += 1
        updated = code[:begin] + snippet + code[end:]
    else:
        # Mask comments for syntax checks without changing source offsets.
        plain = re.sub(r"#[^\n]*", lambda m: " " * len(m[0]), code)
        opening = re.findall(r"\bfeature\s+rlig\s*\{", plain)
        closing = list(re.finditer(r"}\s*rlig\s*;", plain))
        if len(opening) != 1 or len(closing) != 1 or plain[closing[0].end() :].strip():
            raise ValueError(
                "rlig needs one complete feature block. Review its source first."
            )
        if re.search(r"\b" + LOOKUP + r"\b", plain):
            raise ValueError("The connection lookup name is already in use.")
        point = closing[0].start()
        updated = code[:point] + "\n" + snippet + code[point:]
    if matches:
        features[index] = ("rlig", updated)
    else:
        features.append(("rlig", updated))
    return {"prefix": blocks["prefix"], "features": features}


def save_pair(
    package: Any, expected: dict[str, Any], choices: Choices, names: set[str]
) -> dict[str, int]:
    """Use Fontport's source-bound writer; expose partial failures with Undo advice."""
    import fly.fp.feature_blocks as feature_blocks  # noqa: PLR0402

    updated = merge_feature(expected, connection_block(choices, names))
    valid, _ = partition_choices(choices, names)
    references = {
        n for (left, stem), target in valid.items() for n in (left, stem + "1", target)
    }
    try:
        return feature_blocks.write_feature_blocks(
            package,
            expected,
            updated,
            references=sorted(references),
            undo_name=TITLE,
        )
    except RuntimeError as error:
        raise RuntimeError(
            f"{error} Native changes may remain; use Edit > Undo."
        ) from error


def panel_type() -> type:
    """Create the owned modeless editor and the shared attachment drawing."""
    import fly.ap.anchor_writer as anchor_writer  # noqa: PLR0402
    import fly.ap.scripting as scripting  # noqa: PLR0402
    import fly.fp.feature_blocks as feature_blocks  # noqa: PLR0402
    from fly import qt

    gui = qt.QtGui
    api = scripting.anchors_api()
    drawing_type = scripting.anchors_view_types().AttachmentView

    class ConnectionPanel(scripting.features_dialog_type()):
        """Edit one pair at a time; save choices in feature source, not panel memory."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(
                parent,
                title=TITLE,
                key=KEY,
                subtitle="Choose a connection. Save writes rlig source; compile it in the Features panel.",
            )

        def setup(self) -> None:
            """Build selectors once; retain the shared Close and failure lifecycle."""
            body = self.prepare()
            self.setMinimumWidth(680)
            self.apply_button.setText("Save connection")
            self.left_pick, self.family_pick = gui.QComboBox(), gui.QComboBox()
            self.variant_pick, self.master_pick = gui.QComboBox(), gui.QComboBox()
            for label, control in (
                ("Left glyph", self.left_pick),
                ("Right family", self.family_pick),
                ("Right alternate", self.variant_pick),
                ("Preview master", self.master_pick),
            ):
                row = gui.QHBoxLayout()
                row.addWidget(gui.QLabel(label))
                row.addWidget(control, 1)
                body.addLayout(row)
            self.pair_view = drawing_type()
            body.addWidget(self.pair_view, 1)
            self.source_view = gui.QPlainTextEdit()
            self.source_view.setReadOnly(True)
            body.addWidget(self.source_view, 1)
            self.kept_view = gui.QPlainTextEdit()
            self.kept_view.setReadOnly(True)
            body.addWidget(gui.QLabel("Saved pairs kept without rules"))
            body.addWidget(self.kept_view)
            self.drop_stale = gui.QCheckBox("Drop stale pairs on Save")
            body.addWidget(self.drop_stale)
            self.warning_label = gui.QLabel("")
            self.warning_label.setWordWrap(True)
            body.addWidget(self.warning_label)
            self._connect(self.drop_stale.toggled, lambda *a: self.preview_pair())
            buttons = gui.QHBoxLayout()
            for label, callback in (
                ("Previous", lambda: self.step_variant(-1)),
                ("Next", lambda: self.step_variant(1)),
                ("Reload", self.refresh),
            ):
                button = gui.QPushButton(label)
                buttons.addWidget(button)
                self._connect(button.clicked, lambda *a, cb=callback: cb())
            body.addLayout(buttons)
            self._connect(
                self.family_pick.currentIndexChanged, lambda *a: self.fill_variants()
            )
            self._connect(
                self.left_pick.currentIndexChanged, lambda *a: self.fill_variants()
            )
            self._connect(
                self.variant_pick.currentIndexChanged, lambda *a: self.variant_changed()
            )
            self._connect(
                self.master_pick.currentIndexChanged, lambda *a: self.preview_pair()
            )

        def refresh(self) -> None:
            """Reload saved font choices and retain the current pair when possible."""
            self._preview_valid = False
            self.ensure_font()
            self.known_names = {
                str(g.name)
                for g in self.font_data.glyphs
                if self.package.findName(str(g.name)) is not None
            }
            left, families, self.alternatives = inventory(list(self.known_names))
            self.source_snapshot = feature_blocks.read_feature_blocks(self.package)
            self.saved = saved_choices(
                dict(self.source_snapshot["features"]).get("rlig", "")
            )
            for combo, values in (
                (self.left_pick, left),
                (self.family_pick, families),
                (self.master_pick, list(self.package.masters)),
            ):
                previous = str(combo.currentText)
                combo.blockSignals(True)
                combo.clear()
                combo.addItems(values)
                if previous in values:
                    combo.setCurrentIndex(values.index(previous))
                combo.blockSignals(False)
            self.drop_stale.blockSignals(True)
            self.drop_stale.setChecked(False)
            self.drop_stale.blockSignals(False)
            self.fill_variants()

        def fill_variants(self) -> None:
            """Select the saved alternate, or the family's numbered default."""
            family, left = (
                str(self.family_pick.currentText),
                str(self.left_pick.currentText),
            )
            values = self.alternatives.get(family, [])
            wanted = self.saved.get((left, family), family + "1")
            self.fallback_pair = (
                (left, family)
                if wanted not in values and (left, family) in self.saved
                else None
            )
            self.variant_touched = False
            self.variant_pick.blockSignals(True)
            self.variant_pick.clear()
            self.variant_pick.addItems(values)
            if wanted in values:
                self.variant_pick.setCurrentIndex(values.index(wanted))
            self.variant_pick.blockSignals(False)
            self.preview_pair()

        def variant_changed(self) -> None:
            """An explicit alternate choice can replace a stale choice for this pair."""
            self.variant_touched = True
            self.preview_pair()

        def step_variant(self, amount: int) -> None:
            """Step through actual variants without wrapping."""
            index = int(self.variant_pick.currentIndex) + amount
            if 0 <= index < int(self.variant_pick.count):
                self.variant_pick.setCurrentIndex(index)

        def proposed_choices(self) -> Choices:
            """Add the shown pair to a copy of the saved font choices."""
            result = dict(self.saved)
            if self.drop_stale.isChecked():
                _, stale = partition_choices(result, self.known_names)
                result = {
                    pair: target for pair, target in result.items() if pair not in stale
                }
            pair = str(self.left_pick.currentText), str(self.family_pick.currentText)
            if pair != self.fallback_pair or self.variant_touched:
                result[pair] = str(self.variant_pick.currentText)
            return result

        def preview_pair(self) -> None:
            """Show exact generated source and entry-minus-exit outline placement."""
            self._preview_valid = False
            self.ensure_font()
            self.known_names = {
                str(g.name)
                for g in self.font_data.glyphs
                if self.package.findName(str(g.name)) is not None
            }
            shown_left, shown_family, shown_target = (
                str(self.left_pick.currentText),
                str(self.family_pick.currentText),
                str(self.variant_pick.currentText),
            )
            reason = pair_problem(
                shown_left, shown_family, shown_target, self.known_names
            )
            if reason:
                raise ValueError(f"Shown pair refused: {reason}. Press Reload.")
            _, stale = partition_choices(self.saved, self.known_names)
            self.kept_view.setPlainText(
                "\n".join(
                    f"kept: {left} / {stem} -> {self.saved[left, stem]}: {why}"
                    for (left, stem), why in sorted(stale.items())
                )
            )
            earlier = unmanaged_rule_bases(self.source_snapshot)
            self.warning_label.setText(
                "Existing rlig rules for "
                + ", ".join(earlier)
                + " run first; review them in the Features panel."
                if earlier
                else ""
            )
            choices = self.proposed_choices()
            snippet = connection_block(choices, self.known_names)
            updated = merge_feature(self.source_snapshot, snippet)
            self.source_view.setPlainText(dict(updated["features"])["rlig"])
            master = str(self.master_pick.currentText)
            left_glyph = self.package.findName(str(self.left_pick.currentText))
            right_glyph = self.package.findName(str(self.variant_pick.currentText))
            if (
                left_glyph is None
                or right_glyph is None
                or left_glyph.isNull
                or right_glyph.isNull
            ):
                raise ValueError("Connection glyphs changed; press Reload.")
            left = left_glyph.findLayer(master)
            right = right_glyph.findLayer(master)
            panels = []
            if (
                left is not None
                and right is not None
                and not left.isNull
                and not right.isNull
            ):
                a = anchor_writer.anchor_points(left).get("entry")
                b = anchor_writer.anchor_points(right).get("exit")
                offset = (
                    (a[0] - b[0], a[1] - b[1])
                    if a is not None and b is not None
                    else None
                )
                moved = (
                    qt.QtGui.QTransform(1, 0, 0, 1, *offset).map(api.glyph_path(right))
                    if offset
                    else None
                )
                note = (
                    f"entry − exit: {offset}"
                    if offset
                    else "Missing entry or exit anchor"
                )
                panels.append(
                    (master, api.glyph_path(left), moved, a, left.advanceWidth, note)
                )
            self.pair_view.set_panels(panels)
            self._preview_valid = True
            self.apply_button.setEnabled(updated != self.source_snapshot)
            self.status.setText(
                (f"{len(stale)} saved pairs kept without rules. " if stale else "")
                + "Save connection persists this pair. Stale records stay unless Drop stale pairs on Save is ticked."
            )

        def apply(self) -> None:
            """Write one source-bound plan; refresh from the font after success."""
            self.ensure_preview()
            self.last_result = save_pair(
                self.package,
                self.source_snapshot,
                self.proposed_choices(),
                self.known_names,
            )
            self.refresh()
            self.status.setText(
                "Connection saved. The change is recorded as one Undo step. Compile rlig in the Features panel."
            )

    return ConnectionPanel


def main() -> Any:
    """Open or replace the connection editor through the shared registry."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    return scripting.show_script_dialog(panel_type(), KEY)


if __name__ == "__main__":
    main()
