# this_file: Scripts/Font Info/Names and Credits.py
# SPDX-License-Identifier: Apache-2.0
# FLM: Font Info · Names & Credits
"""Edit family, style, credits and version naming for the current font.

Family, designer, copyright and version name are font-wide; the style name belongs
to the current master (FontLab stores it per master). A table previews the changed
fields before Apply.

Open with a font active. Edit the fields, review the table, then choose Apply.
Blank family or style names and invalid version text disable Apply. The undoable
edit leaves outlines and other masters' style names intact. Reopen after changing
the active master or font so the displayed style scope stays explicit.
"""

import re
from typing import Any

from fly import ap, qt
from fly.ap.scripting import (
    font_info_dialog_type,
    show_script_dialog,
    write_font_info,
)

fontlab = ap.fontlab
QtCore, QtGui = qt.QtCore, qt.QtGui

TITLE = "Names & Credits"
KEY = "fontinfo_names_editor"


def write_changes(package: Any, changes: list[tuple]) -> dict[str, int]:
    """Apply this tool's explicit validated metadata plan using shared history."""
    return write_font_info(package, changes, undo_name=TITLE)


FIELDS = [
    ("familyName", "Family"),
    ("styleName", "Style"),
    ("openTypeNameDesigner", "Designer"),
    ("copyright", "Copyright"),
    ("openTypeNameVersion", "Version name"),
]


def validate_names(values: dict[str, str]) -> dict[str, str]:
    """Require nonempty family/style and valid single-line naming."""
    for field in ("familyName", "styleName"):
        if not values[field].strip():
            msg = "Family and style must not be blank."
            raise ValueError(msg)
    if any(any(ord(c) < 32 for c in text) for text in values.values()):
        msg = "Use single-line text without control characters."
        raise ValueError(msg)
    if not re.fullmatch(
        r"Version [0-9]+\.[0-9]{1,3}(?:[ ;].*)?",
        values["openTypeNameVersion"],
    ):
        msg = "Version name must start with Version major.minor (1–3 minor digits)."
        raise ValueError(
            msg,
        )
    return values


def run(package: Any, values: Any) -> Any:
    """Validate naming text and apply one font-wide/current-master plan."""
    validate_names(values)
    return write_changes(
        package,
        [
            (
                package.master if k == "styleName" else None,
                k,
                getattr(package.info, k) or "",
                v,
            )
            for k, v in values.items()
        ],
    )


FontInfoDialog = font_info_dialog_type()


class Dialog(FontInfoDialog):
    MASTER_BOUND = True

    def __init__(self, parent: Any = None) -> None:
        """Open the shared Font Info panel with this tool's controls and preview."""
        FontInfoDialog.__init__(
            self,
            parent,
            title=TITLE,
            subtitle="Edit family, style, credits and version naming for the current font.",
            key=KEY,
        )

    def setup(self) -> None:
        """Build all original controls and connect owned signals."""
        self.fields = {}
        for row, (field, title) in enumerate(FIELDS):
            edit = QtGui.QLineEdit(
                str(getattr(self.package.info, field) or "") if self.package else "",
            )
            self.fields[field] = edit
            if (
                field == "styleName" and self.package
            ):  # style name is stored per master (measured)
                title = f"Style ({self.package.master} master)"
            self.form.addWidget(QtGui.QLabel(title), row, 0)
            self.form.addWidget(edit, row, 1)
            self._connect(edit.textChanged, lambda *a: self.refresh())

    def values(self) -> Any:
        """Read and validate the complete names form."""
        return validate_names({key: edit.text for key, edit in self.fields.items()})

    def refresh(self) -> None:
        """Validate and display a complete preview before enabling Apply."""
        self._preview_valid = False
        self.apply_button.setEnabled(False)
        if self.package is None:
            return
        self.ensure_font()
        values = self.values()
        changes = [
            (label, getattr(self.package.info, field) or "", values[field])
            for field, label in FIELDS
            if (getattr(self.package.info, field) or "") != values[field]
        ]
        self._plan = [
            (
                self.preview_master if field == "styleName" else None,
                field,
                getattr(self.package.info, field) or "",
                values[field],
            )
            for field, _ in FIELDS
        ]
        self.rows(["Field", "Current", "Proposed"], changes)
        self.apply_button.setEnabled(bool(changes))
        self.status.setText(
            f"{len(changes)} fields changed · style name applies to the current master only",
        )
        self._preview_valid = True

    def apply(self) -> None:
        """Apply the last successful preview to its original font."""
        self.ensure_preview()
        self.last_result = write_changes(self.package, self._plan)
        self.refresh()
        self.status.setText(f"Applied {self.last_result['changed']} fields")


def main() -> Any:
    """Replace this tool's owned dialog using the shared script registry."""
    return show_script_dialog(Dialog, KEY)


if __name__ == "__main__":
    main()
