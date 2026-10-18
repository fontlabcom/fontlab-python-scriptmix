#FLM: Kerning · Persistence Audit
# this_file: Scripts/Kerning/Persistence Audit.py
# SPDX-License-Identifier: Apache-2.0
"""Inspect explicit kerning pairs against FontLab's measured VFJ load limit.

Open a font and choose the current master or all masters, then filter the audit
rows. Values outside twice the UPM are reported as persistence risks. This
read-only check makes no font changes and is not a universal persistence proof.
"""

from typing import Any

from fly.ap.scripting import kerning_persistence_dialog_type, show_script_dialog

KEY = "kerning_persistence_audit"


def main() -> Any:
    """Show the shared App audit using its owned replacement and Close lifecycle."""
    return show_script_dialog(kerning_persistence_dialog_type(), KEY)


if __name__ == "__main__":
    main()
