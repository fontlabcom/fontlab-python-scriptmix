# this_file: Scripts/Features/Build Suffix Substitution.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Features · Build Suffix Substitution
"""Preview a font-wide suffix substitution. Append to source only; compile and test in the Features panel.

Run with a font active. All original controls use the shared fly panel lifecycle.
Feature data is font-wide; reopen after switching fonts or changing source.
"""

import re
from typing import Any

from fly import ap, qt
from fly.ap.feature_code import (
    feature_text,
    safe_name,  # noqa: F401 - preserve sample helper interface
    suffix_pairs,
)
from fly.ap.scripting import (
    features_dialog_type,
    read_feature_blocks,
    show_script_dialog,
    write_feature_blocks,
)

fontlab = ap.fontlab
QtCore, QtGui = (qt.QtCore, qt.QtGui)
FeaturesDialog = features_dialog_type()


TITLE = "Suffix Substitution Builder"
KEY = "features_build_substitution"
SUBTITLE = "Preview a font-wide suffix substitution. Append to source only; compile and test in the Features panel."
ACTION = "Append to feature"


def append_code(old: str, tag: str, pairs: list[tuple[str, str]]) -> str:
    """Insert before a complete feature's closing tag, preserving existing source."""
    if not pairs:
        msg = "No valid base / alternate pairs for this suffix."
        raise ValueError(msg)
    snippet = feature_text(tag, pairs)
    if not old.strip():
        return snippet
    closing = re.search("}\\s*" + re.escape(tag) + "\\s*;\\s*$", old)
    if not closing:
        msg = "Existing feature has no simple closing tag; copy the preview instead."
        raise ValueError(msg)
    statements = snippet.split("{\n", 1)[1].rsplit("\n}", 1)[0]
    if any(
        (
            re.search(
                "\\bsub\\s+" + re.escape(base) + "\\s+by\\b",
                re.sub("#[^\\n]*", "", old),
            )
            for base, _ in pairs
        )
    ):
        msg = "Existing feature already substitutes a source glyph; review it manually."
        raise ValueError(msg)
    prefix = old[: closing.start()]
    return (
        prefix
        + ("" if prefix.endswith("\n") else "\n")
        + statements
        + "\n"
        + old[closing.start() :]
    )


def run(
    package: Any,
    layout: Any,
    tag: str,
    old: str,
    new: str,
    *,
    expected_blocks: dict,
    references: list[str],
) -> dict:
    """Append via the shared exact-source writer; retain the original run arguments.

    layout is retained for compatibility, but writes never use the unsafe raw
    feature setter. The full preview snapshot binds prefix and unrelated blocks.
    """
    blocks = {
        "prefix": expected_blocks["prefix"],
        "features": list(expected_blocks["features"]),
    }
    existing = dict(blocks["features"])
    if existing.get(tag, "") != old:
        raise ValueError("Feature preview does not match its source snapshot.")
    for index, (stored_tag, code) in enumerate(blocks["features"]):
        if stored_tag == tag:
            blocks["features"][index] = (tag, new)
            break
    else:
        blocks["features"].append((tag, new))
    receipt = write_feature_blocks(
        package, expected_blocks, blocks, references=references, undo_name=TITLE
    )
    return {"tag": tag, "code": new, **receipt}


class Dialog(FeaturesDialog):
    def __init__(self, parent: Any = None) -> None:
        """Initialize this owned tool and preserve its original controls."""
        super().__init__(parent, title=TITLE, subtitle=SUBTITLE, key=KEY)

    def setup(self) -> None:
        """Build the original controls inside the shared owned panel."""
        root = self.prepare()
        self.apply_button.setText(ACTION)
        form = QtGui.QGridLayout()
        self.suffix = QtGui.QLineEdit("sc")
        self.tag = QtGui.QLineEdit("smcp")
        self.tag.setMaxLength(4)
        form.addWidget(QtGui.QLabel("Suffix"), 0, 0)
        form.addWidget(self.suffix, 0, 1)
        form.addWidget(QtGui.QLabel("Feature tag"), 0, 2)
        form.addWidget(self.tag, 0, 3)
        root.addLayout(form)
        self.table = self.make_table(["Base", "Alternate"])
        root.addWidget(self.table, 1)
        self.code = QtGui.QPlainTextEdit()
        mono = QtGui.QFont("Menlo")
        mono.setStyleHint(QtGui.QFont.Monospace)
        self.code.setFont(mono)
        self.code.setReadOnly(True)
        root.addWidget(self.code, 1)
        self.copy_button = QtGui.QPushButton("Copy preview")
        root.addWidget(self.copy_button)
        self._connect(
            self.copy_button.clicked, lambda *a: self.copy_text(self.code.toPlainText())
        )
        self._connect(self.suffix.textChanged, lambda *a: self.refresh())
        self._connect(self.tag.textChanged, lambda *a: self.refresh())

    def refresh(self) -> None:
        """Capture one full ordered source snapshot and a complete suffix plan."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self._copy_preview_valid = False
        self.old_code = self.new_code = ""
        if self.package is None:
            self.status.setText("Open a font first.")
            return
        self.ensure_font()
        self.names = sorted(g.name for g in fontlab.CurrentFont().glyphs)
        self.pairs = suffix_pairs(self.names, self.suffix.text.strip())
        self.fill(self.pairs)
        tag = self.tag.text.strip()
        snippet = feature_text(tag, self.pairs)
        self.code.setPlainText(snippet)
        # Copy remains useful if native history preflight refuses a changing write.
        self.copy_button.setEnabled(bool(self.pairs))
        self._copy_preview_valid = bool(self.pairs)
        self._feature_blocks = read_feature_blocks(self.package)
        self.old_code = dict(self._feature_blocks["features"]).get(tag, "")
        try:
            self.new_code = append_code(self.old_code, tag, self.pairs)
            if not self.new_code.endswith("\n"):
                self.new_code += "\n"
        except ValueError as error:
            self.status.setText(str(error))
            return
        self._preview_tag = tag
        self._preview_pairs = list(self.pairs)
        self.code.setPlainText(self.new_code)
        self.apply_button.setEnabled(True)
        self.status.setText(
            f"{len(self.pairs)} pairs · font-wide, all masters · existing code preserved"
        )
        self._preview_valid = True

    def apply(self) -> None:
        """Apply the last complete preview, refusing stale controls and references."""
        self.ensure_preview()
        if (
            self.tag.text.strip() != self._preview_tag
            or suffix_pairs(
                [g.name for g in fontlab.CurrentFont().glyphs], self.suffix.text.strip()
            )
            != self._preview_pairs
        ):
            self._preview_valid = False
            raise ValueError(
                "Referenced glyphs or controls changed; refresh the preview."
            )
        self.last_result = run(
            self.package,
            self.font_data.features,
            self._preview_tag,
            self.old_code,
            self.new_code,
            expected_blocks=self._feature_blocks,
            references=[name for pair in self._preview_pairs for name in pair],
        )
        self.refresh()
        self.status.setText(
            "Feature source appended. Compile it in the Features panel to test."
        )


def main() -> Any:
    """Replace this tool through the shared owned-window registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
