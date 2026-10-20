# this_file: Scripts/Proof/Highest & Lowest Glyphs.py
# SPDX-License-Identifier: Apache-2.0
"""Open the exact highest and lowest foreground layers in a fresh FontLab tab.

Run this Proof command with a font open. Scan all foreground masters and ordinary auxiliary layers; omit masks/service caches.
Keep font glyph order and the first layer on equal coordinates. Empty bounds
participate, and the same winner appears twice when it is both extrema. Preserve
unencoded glyph names and exact layer names rather than substituting Unicode or
slash text. Missing/ambiguous layers and stale/slow reads fail before a proof.
A modeless coordinate panel preserves the source messages without changing Output. Run Again repeats the complete scan and new-tab action.

Fly loads shared App capture, extrema selection and native named-layer tabs.
No missing layer is created; no master/selection/font/history/Output writer or
application-wide event loop is used. A native tab failure can leave a new tab;
no atomic UI rollback is claimed. Native scope/order/role/bounds/tab and full
font/history/dirty/save/reopen preservation still require owned qualification.
Requires reviewed unpublished App>=0.2.49.dev0 and Fly in FontLab9/Python3.11.
Modified from slobzheninov--Glyphs-Scripts/Testing/Highest & Lowest Glyphs.py; see NOTICE/additional-tools.json.
The port fixes zero being mistaken for an unset extrema value.
"""

from typing import Any


def main() -> Any:
    """Run the complete source scope through the shared App/Fly workflow."""
    from fly.ap.extrema_proof import show_all

    return show_all()


if __name__ == "__main__":
    main()
