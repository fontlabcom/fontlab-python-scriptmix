# this_file: Scripts/Features/Generate Random Alternates Feature.py
# SPDX-License-Identifier: Apache-2.0
"""Generate seeded contextual alternate feature source for the current font.

What: Build random context classes and substitution lookups from user-supplied
base/alternate rows. Keep the seed to reproduce exactly the same source.
How: Read the current glyph catalogue. Assign category members to nonempty
classes, then choose a target and context for each rule using a local RNG.
Why: OpenType contextual substitutions are deterministic. Random generation
makes varied rules; it does not make the shaping engine choose randomly.
The native Features editor accepts source, but does not generate seeded contexts.
Use: Open a font, enter one base and its alternates per line, adjust counts,
categories and seed, then Preview. Copy feature sends the complete generated
source to the clipboard. Write feature replaces the code for the previewed
feature tag only after Replace existing feature is ticked for a differing
block. Preview shows existing and generated code side by side. Adding a tag
or writing identical code needs no confirmation. Changing input or refreshing
resets the tick. The shared source-bound writer preserves other
features and the prefix stay unchanged. Each changing write is recorded as one
Undo step. Compile and test in FontLab's Features panel after writing.
Benefit: Review and reproduce varied alternates without manual rule entry.
The non-modal panel shows the exact block that Write feature stores. The category filter
uses Unicode general categories, with base-name inheritance for suffix glyphs;
unencoded names without an encoded base match only All. Export flags are not
used. Classes stay inside the generated feature block.

Independent behaviour rewrite after Alex Slobzheninov,
Glyphs-Scripts/Features/Generate Random Alternates Feature.py, Apache-2.0.
Repository: https://github.com/slobzheninov/Glyphs-Scripts . No code copied.
"""

import random
import re
import unicodedata
from typing import Any

TITLE = "Generate Random Alternates Feature"
KEY = "features_random_alternates"


def generate(
    text: str,
    names: list[str],
    context: list[str],
    tag: str,
    lines: int,
    sequence: int,
    lookups: int,
    classes: int,
    seed: int,
) -> str:
    """Build complete reproducible FEA; reject missing or unsafe references."""
    import fly.ap.feature_code as feature_code  # noqa: PLR0402

    if any(character in text for character in ("\x00", "\u00a0", "\u2028", "\u2029")):
        raise ValueError(
            "Use plain spaces and line breaks; NUL, NBSP and Unicode line separators are refused."
        )
    if not re.fullmatch(r"[A-Za-z0-9]{4}", tag):
        raise ValueError("Feature tag must contain four ASCII letters or digits.")
    if any(
        type(value) is not int or value < 1
        for value in (lines, sequence, lookups, classes)
    ):
        raise ValueError("All counts must be positive whole numbers.")
    if lines * sequence * lookups > 100000:
        raise ValueError(
            "Reduce the rule counts or sequence length below 100000 tokens."
        )
    known, alternatives = set(names), {}
    for row in text.splitlines():
        tokens = list(dict.fromkeys(row.split()))
        if not tokens:
            continue
        if len(tokens) < 2 or tokens[0] in alternatives:
            raise ValueError(
                "Use one unique base and at least one different alternate per row."
            )
        if any(
            name not in known or not feature_code.safe_name(name) for name in tokens
        ):
            raise ValueError(
                "Every base and alternate must be a safe existing glyph name."
            )
        alternatives[tokens[0]] = tokens[1:]
    if not alternatives:
        raise ValueError("Enter at least one base and alternate row.")
    members = list(dict.fromkeys(context))
    if classes > len(members) or any(
        name not in known or not feature_code.safe_name(name) for name in members
    ):
        raise ValueError("Each context class needs at least one safe existing glyph.")
    if type(seed) is not int:
        raise ValueError("Seed must be a whole number.")
    namespace = f"{tag}_{'m' if seed < 0 else 'p'}{abs(seed)}"
    rng = random.Random(seed)
    rng.shuffle(members)
    buckets: list[list[str]] = [[] for _ in range(classes)]
    for index, name in enumerate(members):
        buckets[index if index < classes else rng.randrange(classes)].append(name)
    output = [f"feature {tag} {{", f"# Contextual alternates; generation seed {seed}."]
    for index, bucket in enumerate(buckets):
        output.append(
            f"@ContextChoice_{namespace}_{index} = ["
            + " ".join("\\" + n for n in bucket)
            + "];"
        )
    for number in range(lookups):
        label = f"ContextVariation_{namespace}_{number}"
        output.append(f"lookup {label} {{")
        for _ in range(lines):
            base = rng.choice(list(alternatives))
            target = rng.choice(alternatives[base])
            position = rng.randrange(sequence)
            parts = [
                f"@ContextChoice_{namespace}_{rng.randrange(classes)}"
                for _ in range(sequence)
            ]
            parts[position] = "\\" + base + "'"
            output.append("    sub " + " ".join(parts) + " by \\" + target + ";")
        output.append(f"}} {label};")
    output.append(f"}} {tag};")
    return "\n".join(output) + "\n"


def category_members(rows: tuple, categories: str) -> list[str]:
    """Map Unicode category names to prefixes; inherit from the base glyph."""
    prefixes = {
        "Letter": "L",
        "Punctuation": "P",
        "Number": "N",
        "Mark": "M",
        "Symbol": "S",
        "Separator": "Z",
        "Other": "C",
    }
    requested = categories.split()
    if not requested or any(name not in {*prefixes, "All"} for name in requested):
        raise ValueError(
            "Categories: Letter Punctuation Number Mark Symbol Separator Other All."
        )
    codes = {name: unicode_text.split() for name, unicode_text, _ in rows}
    result = []
    for name, values in codes.items():
        points = values or codes.get(name.split(".", 1)[0], [])
        if "All" in requested or any(
            unicodedata.category(chr(int(point[2:], 16)))[0]  # noqa: FURB166 - catalogue uses U+XXXX
            in {prefixes[category] for category in requested}
            for point in points
        ):
            result.append(name)
    return result


def write_feature(
    package: Any, expected: dict, tag: str, code: str, *, replace: bool = False
) -> dict:
    """Replace one exact previewed feature block through the shared Undo writer."""
    import fly.fp.feature_blocks as feature_blocks  # noqa: PLR0402

    if feature_blocks.read_feature_blocks(package) != expected:
        raise ValueError("Feature source changed; press Preview again.")
    blocks = list(expected["features"])
    matches = [index for index, (name, _) in enumerate(blocks) if name == tag]
    if len(matches) > 1:
        raise ValueError(
            "Feature tag occurs more than once; resolve it in the Features panel."
        )
    if matches:
        if blocks[matches[0]][1] != code and not replace:
            raise ValueError(
                f"Feature {tag} already exists; tick Replace existing feature."
            )
        blocks[matches[0]] = (tag, code)
    else:
        blocks.append((tag, code))
    updated = {"prefix": expected["prefix"], "features": blocks}
    references = list(
        dict.fromkeys(re.findall(r"\\([A-Za-z_][A-Za-z0-9_.\-]*|\.notdef)", code))
    )
    try:
        return feature_blocks.write_feature_blocks(
            package, expected, updated, references=references, undo_name=TITLE
        )
    except RuntimeError as error:
        raise RuntimeError(
            f"{error} Native changes may remain; use Edit > Undo."
        ) from error


def panel_type() -> type:
    """Load PythonQt only when opening the owned modeless panel."""
    import fly.ap.glyph_catalog as catalog
    import fly.ap.scripting as scripting  # noqa: PLR0402
    import fly.fp.feature_blocks as feature_blocks  # noqa: PLR0402
    from fly import qt

    gui = qt.QtGui

    class AlternatesPanel(scripting.features_dialog_type()):
        """Reuse shared binding, guarded signals and disconnect-on-close logic."""

        def __init__(self, parent: Any = None) -> None:
            """Bind one owned panel to the font that was current on opening."""
            super().__init__(
                parent,
                title=TITLE,
                key=KEY,
                subtitle="Compare existing and generated code. Tick Replace existing feature to replace a differing block.",
            )

        def setup(self) -> None:
            """Build the source editor, compact numeric controls and output."""
            body = self.prepare()
            self.source_edit = gui.QPlainTextEdit()
            self.source_edit.setPlaceholderText("a a.ss01 a.ss02\nb b.ss01 b.ss02")
            body.addWidget(self.source_edit)
            grid = gui.QGridLayout()
            self.option_edits = {}
            defaults = [
                ("Feature", "calt"),
                ("Lines", "20"),
                ("Sequence", "3"),
                ("Lookups", "4"),
                ("Classes", "5"),
                ("Seed", "0"),
                ("Categories", "Letter Punctuation"),
            ]
            for index, (label, value) in enumerate(defaults):
                field = gui.QLineEdit(value)
                self.option_edits[label] = field
                grid.addWidget(gui.QLabel(label), index // 2, (index % 2) * 2)
                grid.addWidget(field, index // 2, (index % 2) * 2 + 1)
                self._connect(field.textChanged, lambda *a: self.invalidate_preview())
            body.addLayout(grid)
            preview_button = gui.QPushButton("Preview")
            body.addWidget(preview_button)
            previews = gui.QHBoxLayout()
            old_column, new_column = gui.QVBoxLayout(), gui.QVBoxLayout()
            self.existing_label = gui.QLabel("Existing feature")
            old_column.addWidget(self.existing_label)
            self.existing_edit = gui.QPlainTextEdit()
            self.existing_edit.setReadOnly(True)
            old_column.addWidget(self.existing_edit, 1)
            new_column.addWidget(gui.QLabel("Generated feature"))
            self.output_edit = gui.QPlainTextEdit()
            self.output_edit.setReadOnly(True)
            new_column.addWidget(self.output_edit, 1)
            previews.addLayout(old_column, 1)
            previews.addLayout(new_column, 1)
            body.addLayout(previews, 1)
            self.replace_check = gui.QCheckBox("Replace existing feature")
            self.replace_check.setChecked(False)
            body.addWidget(self.replace_check)
            self.apply_button.setText("Write feature")
            self.copy_button = gui.QPushButton("Copy feature")
            self.copy_button.setEnabled(False)
            body.addWidget(self.copy_button)
            self._connect(self.copy_button.clicked, lambda *a: self.copy_preview())
            self._connect(preview_button.clicked, lambda *a: self.refresh())
            self._connect(
                self.source_edit.textChanged, lambda *a: self.invalidate_preview()
            )

        def invalidate_preview(self) -> None:
            """Prevent copying output made from earlier controls."""
            self._preview_valid = False
            self.apply_button.setEnabled(False)
            self.copy_button.setEnabled(False)
            self.replace_check.setChecked(False)

        def refresh(self) -> None:
            """Regenerate complete current-font output; failures disable Copy."""
            self.invalidate_preview()
            self.ensure_font()
            table = catalog.capture()
            fields = {
                name: str(edit.text).strip() for name, edit in self.option_edits.items()
            }
            try:
                counts = [
                    int(fields[name])
                    for name in ("Lines", "Sequence", "Lookups", "Classes", "Seed")
                ]
            except ValueError as error:
                raise ValueError(
                    "Lines, Sequence, Lookups, Classes and Seed must be whole numbers."
                ) from error
            self.preview_rows = table.rows
            self.preview_code = generate(
                self.source_edit.toPlainText(),
                [row[0] for row in table.rows],
                category_members(table.rows, fields["Categories"]),
                fields["Feature"],
                *counts,
            )
            self.preview_tag = fields["Feature"]
            self.preview_blocks = feature_blocks.read_feature_blocks(self.package)
            self.existing_code = dict(self.preview_blocks["features"]).get(
                self.preview_tag
            )
            self.existing_label.setText(
                f"Existing {self.preview_tag}"
                if self.existing_code is not None
                else f"Existing {self.preview_tag} (not present)"
            )
            self.existing_edit.setPlainText(self.existing_code or "")
            self.output_edit.setPlainText(self.preview_code)
            self._preview_valid = True
            self.apply_button.setEnabled(True)
            self.copy_button.setEnabled(True)
            if (
                self.existing_code is not None
                and self.existing_code != self.preview_code
            ):
                self.status.setText(
                    f"Feature {self.preview_tag} exists ({len(self.existing_code.splitlines())} lines). "
                    "Write will replace it only after you tick Replace existing feature."
                )
            else:
                self.status.setText(
                    "Write adds this tag or keeps identical source. Compile and test in the Features panel."
                )

        def check_catalogue(self) -> None:
            """Refuse a stale preview or changed current-font glyph catalogue."""
            self.ensure_preview()
            if catalog.capture().rows != self.preview_rows:
                self.invalidate_preview()
                raise ValueError("Glyph catalogue changed; press Preview again.")

        def copy_preview(self) -> None:
            """Copy the exact preview without changing feature source."""
            self.check_catalogue()
            self.copy_text(self.preview_code)

        def apply(self) -> None:
            """Write exactly the previewed block, leaving other feature tags intact."""
            self.check_catalogue()
            if (
                self.existing_code is not None
                and self.existing_code != self.preview_code
                and not self.replace_check.isChecked()
            ):
                self.status.setText(
                    f"Feature {self.preview_tag} already exists; tick Replace existing feature."
                )
                return
            try:
                result = write_feature(
                    self.package,
                    self.preview_blocks,
                    self.preview_tag,
                    self.preview_code,
                    replace=self.replace_check.isChecked(),
                )
            except (ValueError, RuntimeError, TimeoutError):
                self.invalidate_preview()
                raise
            self.preview_blocks = feature_blocks.read_feature_blocks(self.package)
            self.existing_code = dict(self.preview_blocks["features"]).get(
                self.preview_tag
            )
            self.existing_label.setText(f"Existing {self.preview_tag}")
            self.existing_edit.setPlainText(self.existing_code or "")
            self.replace_check.setChecked(False)
            self.status.setText(
                "Feature source written; compile and test in the Features panel."
                if result["changed"]
                else "Feature source is unchanged."
            )

    return AlternatesPanel


def main() -> Any:
    """Replace this tool's panel through the shared lifetime registry."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
