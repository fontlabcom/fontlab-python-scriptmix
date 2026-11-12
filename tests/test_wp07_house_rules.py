# this_file: tests/test_wp07_house_rules.py
# SPDX-License-Identifier: Apache-2.0
"""WP07 oracles must still fail on a wrong ``this_file`` path or a missing SPDX line."""

from pathlib import Path

import pytest
from _wp07_routes import ROUTES, assert_house_header, behavior_path, expected_this_file

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("script", sorted(ROUTES))
def test_routed_app_source_when_checked_then_exact_this_file_and_spdx(script: str) -> None:
    target = behavior_path(ROOT / script)
    assert_house_header(target.read_text(), expected_this_file(ROOT / script))


def test_expected_this_file_when_unrouted_then_scriptmix_relative_path() -> None:
    assert expected_this_file(ROOT / "Scripts/Masters/Master Twins.py") == "Scripts/Masters/Master Twins.py"


def test_expected_this_file_when_routed_then_app_relative_path_not_scriptmix() -> None:
    value = expected_this_file(ROOT / "Scripts/Names/Suffix Tool.py")
    assert value == "src/fontlabapp/glyphs/identity_tools/glyph_identity/suffix_tool.py"
    assert value != "Scripts/Names/Suffix Tool.py"


def test_oracle_when_routed_file_has_scriptmix_this_file_then_raises() -> None:
    script = ROOT / "Scripts/Names/Suffix Tool.py"
    text = behavior_path(script).read_text()
    wrong = text.replace(f"# this_file: {expected_this_file(script)}", "# this_file: Scripts/Names/Suffix Tool.py", 1)
    assert wrong != text
    with pytest.raises(AssertionError, match="this_file must be"):
        assert_house_header(wrong, expected_this_file(script))


def test_oracle_when_routed_file_lacks_spdx_then_raises() -> None:
    script = ROOT / "Scripts/Names/Suffix Tool.py"
    text = behavior_path(script).read_text()
    stripped = text.replace("# SPDX-License-Identifier: Apache-2.0\n", "", 1)
    assert stripped != text
    with pytest.raises(AssertionError, match="missing SPDX"):
        assert_house_header(stripped, expected_this_file(script))
