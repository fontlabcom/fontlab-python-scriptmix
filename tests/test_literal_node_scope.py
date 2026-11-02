# this_file: tests/test_literal_node_scope.py
"""All-foreground identity scope, first-reference broadcast and repeated parents."""

from copy import deepcopy
from types import SimpleNamespace as NS

from test_literal_node_actions import boundary, load_menu  # noqa: F401 - pytest fixture


def test_all_action_when_parents_repeat_then_broadcasts_first_reference_to_all_layer_identities(
    boundary,
):
    owned, native, qt, notifications, first_contour, selected = boundary("all")
    first, initial = owned.bound[30]
    second_state, *_ = boundary.host("all")
    second, other = second_state.bound[30]
    first.isNull = second.isNull = False
    second.id, second.name, other.id = 41, "b", 31
    auxiliary_a = boundary.host("all")[0].bound[30][1]
    auxiliary_b = boundary.host("all")[0].bound[30][1]
    auxiliary_a.id, auxiliary_b.id = 32, 33
    layers = [initial, auxiliary_a, other, auxiliary_b]
    originals, before = [], []
    for index, layer in enumerate(layers):
        layer.name = "Regular"  # Deliberate duplicates within each glyph.
        shape = layer.shapes[0]
        shape.id, shape.shapeData.id = 70 + index * 2, 71 + index * 2
        contour = shape.contours[0]
        contour.id = 20 + index
        node = contour.nodes()[0]
        if index:
            node.nodeState &= ~32  # No independent selection in other targets.
        node.name = f"target-{index}"
        layer.advanceWidth = 500.125 + index
        layer.anchors = [("top", 120.25, 730.5)]
        layer.guides = [("owned", 90.0)]
        layer.custom = {"keep": [index]}
        originals.append(node)
        before.append(
            deepcopy(
                (
                    layer.note,
                    layer.advanceWidth,
                    layer.anchors,
                    layer.guides,
                    layer.custom,
                )
            )
        )
    first.layers, second.layers = layers[:2], layers[2:]
    package = first.package
    second.package = package
    package.findName = lambda name: {"a": first, "b": second}[name]
    native.CurrentFont = lambda: NS(id=60, glyphs=[NS(name="a"), NS(name="b")])
    displayed = [first, first, second]
    canvas = NS(
        isNull=False,
        selectedNodes=lambda: [NS(node=originals[0])],
        selection=lambda: [],
        textBlocks=lambda: [
            NS(glyphsCount=lambda: 3, getGlyphAt=lambda i: NS(glyph=displayed[i]))
        ],
    )
    native.flWorkspace.instance().getActiveCanvas = lambda: canvas
    selected.context, selected.carriers = (50, "Regular", "editor", 1), (canvas,)
    selected.occurrences = tuple(
        NS(
            package=package,
            glyph=glyph,
            layer=layer,
            package_id=50,
            glyph_id=glyph.id,
            layer_id=layer.id,
            block_id=0,
            index=i,
        )
        for i, (glyph, layer) in enumerate(
            [(first, initial), (first, auxiliary_a), (second, other)]
        )
    )
    outcome = load_menu("Duplicate Nodes All Foreground Layers").main()
    assert outcome["inserted"] == 6 and len(notifications) == 1
    assert [len(layer.shapes[0].contours[0].nodes()) for layer in layers] == [
        3,
        3,
        2,
        2,
    ]
    assert len(notifications[0][1]) == 6, (
        "Four distinct layers and both owners share one notification"
    )
    for index, layer in enumerate(layers):
        nodes = layer.shapes[0].contours[0].nodes()
        assert nodes[0] is originals[index]
        assert all(n.name == f"target-{index}" for n in nodes)
        assert all(n.getProperty("corner_smooth") == 0.375 for n in nodes)
        assert (
            layer.note,
            layer.advanceWidth,
            layer.anchors,
            layer.guides,
            layer.custom,
        ) == before[index]


def test_current_action_when_other_layers_selected_then_only_first_identity_changes(
    boundary,
):
    owned, native, qt, notifications, contour, selected = boundary("current")
    other, *_ = boundary.host("current")
    second_glyph, second_layer = other.bound[30]
    selected.occurrences += (
        NS(
            package=second_glyph.package,
            glyph=second_glyph,
            layer=second_layer,
            package_id=50,
            glyph_id=41,
            layer_id=31,
            block_id=0,
            index=1,
        ),
    )
    outcome = load_menu("Duplicate Nodes Current Layer").main()
    assert outcome["inserted"] == 1 and len(contour.nodes()) == 2
    assert len(second_layer.shapes[0].contours[0].nodes()) == 1
    assert len(notifications[0][1]) == 2, (
        "The extra selected owner is outside this profile"
    )
