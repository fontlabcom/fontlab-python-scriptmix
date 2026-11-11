# this_file: tests/test_wp05_outline_order.py
"""Run the existing direction/start behavioral oracles against migrated App code."""
import importlib

import pytest
import test_issue122_S6 as original

world = original.world


@pytest.fixture
def migrated(world, monkeypatch):
    module = importlib.import_module('fontlabapp.fontui.outline_order')
    monkeypatch.setattr(original, 'load', lambda name: vars(module))
    return module


def test_direction_nested_quadratic_and_correct_winding(migrated, world):
    original.test_direction_when_outer_cw_and_counter_ccw_then_both_wrong(world)


@pytest.mark.parametrize('rotation', range(4))
def test_overlap_is_not_nesting(migrated, world, rotation):
    original.test_direction_when_outers_overlap_then_kept_for_every_start(world, rotation)


def test_shared_scaled_and_separate_shapes_remain_held(migrated, world):
    original.test_direction_when_outer_is_shared_scaled_then_counter_still_nested(world)
    original.test_direction_when_separate_element_inside_then_left_with_note(world)


@pytest.mark.parametrize('editor', ['ReverseEditor', 'StartEditor'])
@pytest.mark.parametrize('preexisting', [False, True])
def test_new_final_smooth_is_advice_not_store_failure(migrated, world, editor, preexisting):
    original.test_readback_when_final_smooth_introduced_then_advice_not_store_failure(
        world, 'ignored', editor, preexisting)


def test_start_indices_writes_and_native_refusal(migrated, world):
    assert migrated.bottom_left([(5, 0, True), (0, 0, True), (0, 0, False)]) == 1
    assert migrated.bottom_left([(0, 0, False)]) is None
    world.same('A', [(10,10,1), (0,10,1), (0,0,1), (10,0,1)])
    layer = world.layer('A')
    rows = migrated.start_changes(layer, None)
    writer = migrated.StartEditor()
    edits = writer.prepare(layer, [r.edit for r in rows if r.edit])
    assert edits[0][1] == 2
    writer.write(layer, edits)
    assert writer.check([(layer, edits)]) == []
    assert migrated.start_changes(layer, layer) == []


def test_direction_native_write_and_readback(migrated, world):
    world.same('A', original.square(0, 0, 100, clockwise=True))
    layer = world.layer('A')
    edits = [r.edit for r in migrated.direction_changes(layer) if r.edit]
    writer = migrated.ReverseEditor()
    edits = writer.prepare(layer, edits)
    assert writer.check([(layer, edits)])
    writer.write(layer, edits)
    assert writer.check([(layer, edits)]) == []
