# this_file: Scripts/Font Info/Bump Font Version.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font Info · Bump Font Version
"""Bump the numeric version and version name; optionally append a dated font note.

Open with a font active. Choose a major or minor bump and optional dated notes,
review the field changes, then choose Apply. Minor 999 carries into the major.
Version fields are global; notes are appended to each master's existing note.
The edit is undoable. Reopen the panel after switching fonts.
"""

from datetime import date
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    font_info_dialog_type,
    show_script_dialog,
    write_font_info,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Bump Font Version"
KEY = "fontinfo_version_bumper"


def write_changes(package: Any, changes: list[tuple]) -> dict[str, int]:
    """Apply this tool's explicit validated metadata plan using shared history."""
    return write_font_info(package, changes, undo_name=TITLE)


LABELS = {
    "versionMajor": "Major version",
    "versionMinor": "Minor version",
    "openTypeNameVersion": "Version name",
    "note": "Note",
}


def bumped(major: int, minor: int, mode: str) -> tuple[int, int]:
    """Calculate a bounded integer version, carrying the minor at 999."""
    if (
        mode not in ("minor", "major")
        or not isinstance(major, int)
        or not isinstance(minor, int)
        or not 0 <= minor <= 999
        or not 0 <= major <= 65535
    ):
        msg = "Version must have major 0–65535 and minor 0–999."
        raise ValueError(msg)
    new = (
        (major + 1, 0)
        if mode == "major"
        else (major + (minor == 999), (minor + 1) % 1000)
    )
    if new[0] > 65535:
        msg = "The major version would exceed 65535."
        raise ValueError(msg)
    return new


def version_plan(package: Any, mode: Any, dated: Any, day: Any) -> Any:
    """Plan numeric version, naming and optional notes across masters."""
    major, minor = bumped(int(package.versionMajor), int(package.versionMinor), mode)
    name = f"Version {major}.{minor:03d}"
    values = {"versionMajor": major, "versionMinor": minor, "openTypeNameVersion": name}
    changes = [
        (None, key, getattr(package.info, key), value) for key, value in values.items()
    ]
    if dated:  # the note is stored per master (measured): append the line to every master's note
        original = package.master
        try:
            for master in package.masters:
                package.setMaster(master)
                old = str(package.info.note or "")
                changes.append(
                    (
                        master,
                        "note",
                        old,
                        old + ("\n" if old else "") + f"{day}: {name}",
                    ),
                )
        finally:
            package.setMaster(original)
    return changes


def run(package: Any, mode: Any, dated: Any, day: Any) -> Any:
    """Build and apply one numeric-version, naming and optional-note plan."""
    return write_changes(package, version_plan(package, mode, dated, day))


FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    def __init__(self, parent: Any = None) -> None:
        """Open the shared Font Info panel with this tool's controls and preview."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle="Bump the numeric version and version name; optionally append a dated font note.",
            key=KEY,
        )

    def setup(self) -> None:
        """Build all original controls and connect owned signals."""
        self.mode = QtGui.QComboBox()
        self.mode.addItems(["Minor (+0.001, carry at 999)", "Major (+1, reset minor)"])
        self.date_note = QtGui.QCheckBox("Append a dated line to every master's note")
        self.date_note.setChecked(True)
        self.form.addWidget(self.mode, 0, 0)
        self.form.addWidget(self.date_note, 0, 1)
        self._connect(self.mode.currentIndexChanged, lambda *a: self.refresh())
        self._connect(self.date_note.toggled, lambda *a: self.refresh())

    def changes(self) -> Any:
        """Build explicit per-master changes from the selected controls."""
        return version_plan(
            self.package,
            "major" if self.mode.currentIndex else "minor",
            self.date_note.isChecked(),
            date.today().isoformat(),  # noqa: DTZ011 - user-local calendar note
        )

    def refresh(self) -> None:
        """Validate and display a complete preview before enabling Apply."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is None:
            return
        self.ensure_font()
        self._plan = self.changes()
        self.rows(
            ["Field", "Current", "Proposed"],
            [
                (LABELS[k] if m is None else f"{LABELS[k]} · {m}", old, new)
                for m, k, old, new in self._plan
            ],
        )
        self.apply_button.setEnabled(True)
        self.status.setText("Minor uses three digits; existing notes are preserved.")
        self._preview_valid = True

    def apply(self) -> None:
        """Apply the last successful preview to its original font."""
        self.ensure_preview()
        self.last_result = write_changes(self.package, self._plan)
        self.refresh()
        self.status.setText("Version applied; preview now shows the next bump.")


def main() -> Any:
    """Replace this tool's owned dialog using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
