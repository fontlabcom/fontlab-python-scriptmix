# this_file: tests/test_migrate_app_paths.py
"""Keep the migration exact at identifier boundaries and safe to rerun."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "migrate_app_paths", Path(__file__).parents[1] / "tools/migrate_app_paths.py"
)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


@pytest.mark.parametrize("root", ["fly.ap", "fontlabapp"])
def test_rewrite_when_dotted_names_then_exact_longest_match_and_idempotent(root):
    aliases = {"fontlabapp.old": "fontlabapp.core.new",
               "fontlabapp.old_more": "fontlabapp.core.more",
               "fontlabapp.domain": "fontlabapp.domain.inspect.model",
               "fontlabapp.locations": "fontlabapp.domain.locations"}
    before = (f'{root}.old.call {root}.old_more "{root}.old" '
              f'{root}.oldish other.{root}.old prefix_{root}.old '
              f'{root}.domain.attribute {root}.domain.inspect.model.call')
    after = (f'{root}.core.new.call {root}.core.more "{root}.core.new" '
             f'{root}.oldish other.{root}.old prefix_{root}.old '
             f'{root}.domain.inspect.model.attribute {root}.domain.inspect.model.call')
    assert tool.rewrite(before, aliases) == after
    assert tool.rewrite(after, aliases) == after


def test_rewrite_when_short_ap_then_requires_fly_import():
    aliases = {"fontlabapp.old": "fontlabapp.core.new"}
    assert tool.rewrite("ap.old", aliases) == "ap.old"
    assert tool.rewrite("from fly import ap\nap.old", aliases) == "from fly import ap\nap.core.new"
