"""FontLab live component dependency graph and affine compensation."""

from collections import defaultdict


def references(package, master_names):
    reverse = defaultdict(list)
    seen = set()

    def visit(shape, layer, glyph, ancestry):
        if shape.id in ancestry:
            raise ValueError("Cyclic component graph in " + glyph.name)
        # Do not descend into a component: that content belongs to its base.
        if shape.isComponent:
            name = shape.shapeData.componentGlyph
            if name and shape.id not in seen:
                reverse[(str(name), layer.name)].append((shape, layer, glyph))
                seen.add(shape.id)
            return
        for child in shape.includesList:
            visit(child, layer, glyph, ancestry | {shape.id})

    for fg in package.fgPackage.glyphs:
        glyph = package.findName(fg.name)
        for master in master_names:
            layer = glyph.findLayer(master)
            if layer is not None and not layer.isNull:
                for shape in layer.shapes:
                    visit(shape, layer, glyph, set())
    return reverse


def compensate(refs, delta):
    from PythonQt import QtGui

    for shape, layer, glyph in refs:
        tx = shape.transform
        # Translation of base coordinates passes through the component's
        # linear map, including reflection, rotation, shear and scaling.
        shape.transform = QtGui.QTransform(
            tx.m11(),
            tx.m12(),
            tx.m21(),
            tx.m22(),
            tx.dx() - delta * tx.m11(),
            tx.dy() - delta * tx.m12(),
        )
        shape.changed()
        layer.changed()
        glyph.update()
