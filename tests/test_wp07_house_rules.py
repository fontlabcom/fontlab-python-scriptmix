# this_file: tests/test_wp07_house_rules.py
# SPDX-License-Identifier: Apache-2.0
"""WP07 oracles must still fail on a wrong ``this_file`` path or a missing SPDX line."""

from pathlib import Path

import pytest
from _wp07_routes import ROUTES, behavior_path, expected_this_file

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("script", sorted(ROUTES))
def test_routed_app_source_when_checked_then_exact_this_file_and_spdx(script: str) -> None:
    target = behavior_path(ROOT / script)
    lines = target.read_text().splitlines()
    assert lines[0] == f"# this_file: {expected_this_file(ROOT / script)}"
    assert "SPDX-License-Identifier: Apache-2.0" in "\n".join(lines[:4])


def test_expected_this_file_when_unrouted_then_scriptmix_relative_path() -> None:
    assert expected_this_file(ROOT / "Scripts/Masters/Master Twins.py") == "Scripts/Masters/Master Twins.py"


def test_expected_this_file_when_routed_then_app_relative_path_not_scriptmix() -> None:
    value = expected_this_file(ROOT / "Scripts/Names/Suffix Tool.py")
    assert value == "src/fontlabapp/glyphs/identity_tools/glyph_identity/suffix_tool.py"
    assert value != "Scripts/Names/Suffix Tool.py"


def test_oracle_when_header_wrong_or_spdx_missing_then_check_rejects() -> None:
    expected = expected_this_file(ROOT / "Scripts/Names/Suffix Tool.py")
    wrong = "# this_file: Scripts/Names/Suffix Tool.py\n# SPDX-License-Identifier: Apache-2.0\n"
    assert wrong.splitlines()[0] != f"# this_file: {expected}"
    no_spdx = f"# this_file: {expected}\n# note\n\"\"\"doc\"\"\"\n"
    assert "SPDX-License-Identifier: Apache-2.0" not in "\n".join(no_spdx.splitlines()[:4])
