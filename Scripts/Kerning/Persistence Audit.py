#FLM: Kerning · Persistence Audit
# this_file: Scripts/Kerning/Persistence Audit.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect explicit kerning pairs against FontLab's measured VFJ load limit.

What it does:
    Open a font and choose the current master or all masters, then filter the audit
    rows. Values outside twice the UPM are reported as persistence risks. This
    read-only check makes no font changes and is not a universal persistence proof.

How it works:
    Use the shared App audit to read explicit pairs on the chosen master
    scope. Compare values with the measured twice-UPM VFJ loading boundary.

Why this design:
    The measured numeric boundary identifies a persistence risk; passing it
    cannot prove every aspect of a saved font.

How to use:
    Open a font and run Kerning > Persistence Audit. Choose current or all
    masters, filter the rows and review the reported values before deciding
    which pairs need correction.

Benefit:
    Locate risky explicit kerning values without changing pairs or claiming a
    complete save/reopen test.
"""

from typing import Any

from fly.ap.scripting import kerning_persistence_dialog_type, show_script_dialog

KEY = "kerning_persistence_audit"


def main() -> Any:
    """Show the shared App audit using its owned replacement and Close lifecycle."""
    return show_script_dialog(kerning_persistence_dialog_type(), KEY)


if __name__ == "__main__":
    main()
