# this_file: tests/test_wp08_font_audit_menu.py
"""The S59 launcher preserves the original complete Case Coverage callbacks."""

import runpy
from unittest.mock import Mock

import pytest
import test_case_coverage as original

SCRIPT = original.SCRIPT.with_name('Font Audit.py')


@pytest.fixture
def menu(monkeypatch):
    monkeypatch.setattr(original, 'SCRIPT', SCRIPT)
    return original.menu.__wrapped__(monkeypatch)


def test_policy_when_consolidated_then_original_oracles_still_pass(menu):
    original.test_caller_metadata_and_whole_expansion_policy(menu)


def test_policy_when_cancelled_then_propagates_original_refusal(menu):
    original.test_caller_metadata_and_preferred_names_propagate_cooperative_cancellation(menu)


def test_main_when_invoked_then_shared_owner_receives_all_policies(menu, monkeypatch):
    import fontlabapp.studios.font_audit.practical as practical
    module, categories = menu
    show = Mock(return_value='owned')
    monkeypatch.setattr(practical, 'show', show)
    assert module['main']() == 'owned'
    assert show.call_args.kwargs == dict(
        classify=categories, case_metadata=module['metadata'], case_preferred=module['preferred'],
    )
    runpy.run_path(str(SCRIPT), run_name='__main__')
    assert show.call_count == 2
    show.side_effect = ValueError('native source unavailable')
    with pytest.raises(ValueError, match='native source'):
        module['main']()
