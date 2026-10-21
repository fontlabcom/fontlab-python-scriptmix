# this_file: Scripts/Names/Style Linker.py
# SPDX-License-Identifier: Apache-2.0
"""Preview style linking for the exportable instances of the current font.

What:
    Link whole-word Bold, Italic and Oblique styles to an available base.
    Width groups remain separate. ExtraBold and SemiBold are not Bold.
How:
    A non-modal table previews FontLab style-group names and link flags.
    Apply obtains fresh instance values and changes only matching rows.
    The package owns instance values; assign the complete instance list back.
    Notifications follow FontLab Font Info: package and masters container
    before assignment, then the same list after assignment.
Why:
    FontLab uses a style-group name and bold/italic flags instead of Glyphs
    linkStyle. Native autoSLV/autoSGN and the Instances multi-select controls
    already set these values. This tool adds whole-word base matching across
    width groups in one preview. Per-instance family names (tfn) can differ
    from the font family and are not exposed by the Python instance API.
    Therefore an automatic base group is kept: set that base group explicitly
    in Font Info first. Only explicit base groups are copied. Instance family
    names and other hidden properties stay in the native value objects.
Use:
    Open a font with instances. Run this tool, check the table, then Apply.
    Refresh reads the current font again. Close releases owned signals.
Benefit:
    Preview regular/bold/italic relationships across the complete family.
Credit:
    Giuseppe Salerno / Resistenza Type, StyleLinker.py,
    https://github.com/rsztype/Scripts, Apache-2.0.
    Independent behaviour-only rewrite. No source code was copied.
"""

from typing import Any

TITLE, KEY = "Style Linker", "names_style_linker"


def instance_state(values: list[Any]) -> tuple[Any, ...]:
    """Snapshot naming, flags, export state and visible weight information."""
    return tuple(
        tuple(
            getattr(i, key)
            for key in (
                "name",
                "tsn",
                "sgn",
                "slv",
                "exportable",
                "weight",
                "width",
                "weightValue",
            )
        )
        for i in values
    )


def link_rows(values: list[Any]) -> list[tuple[int, str, int, str]]:
    """List every exportable style, including missing style text and kept rows."""
    import fly.ap.instance_style_names as rules

    active = [(n, i) for n, i in enumerate(values) if i.exportable]
    styles = [str(i.tsn).strip() for _, i in active if str(i.tsn).strip()]
    if len(styles) != len(set(styles)):
        raise ValueError("Duplicate exportable style names; make them unique first.")
    by_style = {str(i.tsn).strip(): i for _, i in active if str(i.tsn).strip()}
    result = []
    for index, value in active:
        style = str(value.tsn).strip()
        link = rules.style_link(style, styles) if style else None
        reason = (
            ""
            if link
            else "no whole-word base link"
            if style
            else "missing typographic style name; set it in Font Info"
        )
        group, flags = str(value.sgn), int(value.slv)
        if link is not None:
            base = by_style[link.base]
            group = str(base.sgn)
            if not group:
                reason = "base Style Group is automatic; set it explicitly in Font Info (instance family may differ)"
            elif any(c in group for c in "\x00\u00a0\u2028\u2029"):
                reason = "base Style Group cannot be represented as plain text"
            else:
                flags = int(link.italic) | (int(link.bold) << 1)
        result.append((index, group, flags, reason))
    return result


def link_plan(values: list[Any]) -> list[tuple[int, str, int]]:
    """Return only links whose base has an explicit export style group."""
    return [
        (n, group, flags) for n, group, flags, reason in link_rows(values) if not reason
    ]


def apply_links(
    package_id: int, expected: tuple[Any, ...], plan: list[tuple[int, str, int]]
) -> int:
    """Check the preview and use the Font Info notification list and order."""
    import fly.ap.edit_guards as guards
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import fl

    package = scripting.current_package()
    if package is None or int(package.fgId) != package_id:
        raise ValueError("The font changed; refresh the preview.")
    values = list(package.instances)
    if instance_state(values) != expected:
        raise ValueError("Instances changed; refresh the preview.")
    if link_plan(values) != plan:
        raise ValueError("Naming changed; refresh the preview.")
    changes = [
        (n, group, flags)
        for n, group, flags in plan
        if str(values[n].sgn) != group or int(values[n].slv) != flags
    ]
    if not changes:
        return 0
    guards.require_settled()
    original = list(package.instances)
    notification = [package, package.mastersContainer()]
    try:
        package.checkInitHistoryState(0)
        fl.flItems.notifyChangesApplied(TITLE, notification)
        try:
            for index, group, flags in changes:
                values[index].sgn = group
                values[index].setSLV(bool(flags & 2), bool(flags & 1))
            package.instances = values
            actual = list(package.instances)
            if len(actual) != len(values) or any(
                str(actual[n].sgn) != group or int(actual[n].slv) != flags
                for n, group, flags in changes
            ):
                raise RuntimeError("Instance values did not read back.")
        except Exception:
            package.instances = original
            raise
        finally:
            fl.flItems.notifyChangesApplied(TITLE, notification)
            fl.UpdateAll()
    except Exception as error:
        raise RuntimeError(
            f"{error} Native changes may remain; use Edit > Undo"
        ) from error
    return len(changes)


def panel_type() -> type:
    """Build the non-modal preview with the shared owned-signal shell."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - lazy Fly module alias
    from fly import qt

    gui = qt.QtGui

    class LinkingPanel(scripting.names_dialog_type()):
        """Keep the preview bound to one font until the user refreshes it."""

        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent, TITLE, KEY)
            self.package_id: int | None = None
            self.expected: tuple[Any, ...] = ()
            self.proposals: list[tuple[int, str, int]] = []
            self.table = self.make_table(
                ["Style", "Style group", "Bold", "Italic", "Action"]
            )
            self.table.setMinimumHeight(230)
            self.root.addWidget(self.table)
            self.status = gui.QLabel("")
            self.status.setWordWrap(True)
            self.root.addWidget(self.status)
            footer = gui.QHBoxLayout()
            self.refresh_button = gui.QPushButton("Refresh")
            self.apply_button = gui.QPushButton("Apply")
            self.close_button = gui.QPushButton("Close")
            for button in (self.refresh_button, self.close_button, self.apply_button):
                footer.addWidget(button)
            self.root.addLayout(footer)
            self._connect(self.refresh_button.clicked, lambda *a: self.read_font())
            self._connect(self.apply_button.clicked, lambda *a: self.write_links())
            self._connect(self.close_button.clicked, lambda *a: self.close())
            self.read_font()

        def read_font(self) -> None:
            """Read the current font once and fill the preview table."""
            self.apply_button.setEnabled(False)
            self.package_id = None
            self.table.setRowCount(0)
            try:
                package = scripting.current_package()
                if package is None:
                    raise ValueError("Open a font with instances first.")
                values = list(package.instances)
                if not values:
                    raise ValueError("Add instances in Font Info first.")
                rows = link_rows(values)
                self.proposals = link_plan(values)
                self.expected = instance_state(values)
                self.package_id = int(package.fgId)
                self.table.setRowCount(len(rows))
                for row, (index, group, flags, reason) in enumerate(rows):
                    for column, text in enumerate(
                        (
                            str(values[index].tsn or values[index].name),
                            group,
                            "✓" if flags & 2 else "",
                            "✓" if flags & 1 else "",
                            f"kept: {reason}" if reason else "link",
                        )
                    ):
                        self.table.setItem(row, column, gui.QTableWidgetItem(text))
                self.subtitle.setText(
                    f"{len(self.proposals)} links · other instances stay as they are"
                )
                self.status.setText("Check the native style groups, then Apply.")
                self.apply_button.setEnabled(bool(self.proposals))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def write_links(self) -> None:
            """Apply the exact preview or show a refusal in the panel."""
            try:
                count = apply_links(self.package_id, self.expected, self.proposals)
                self.read_font()
                self.status.setText(f"Updated {count} instances.")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

    return LinkingPanel


def main() -> Any:
    """Open one owned Style Linker panel."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - lazy Fly module alias

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
