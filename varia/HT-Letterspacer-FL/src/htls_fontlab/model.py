"""Read-only Glyphs-shaped facade over FontLab; writes are in service.py."""

import copy
import json
from contextlib import contextmanager
from types import SimpleNamespace

from .upstream import Point
from .geometry import from_qpath
from .classification import classify
from .qt import compose

STORAGE_KEY = "com.htfonts.letterspacer.fontlab.v1"


class UserData(dict):
    def __getitem__(self, key):
        return self.get(key)


@contextmanager
def master_context(package, name):
    old = package.master
    if old != name:
        package.setMaster(name, False)
    try:
        yield
    finally:
        if package.master != old:
            package.setMaster(old, False)


def qpath(layer):
    """Rendered paths include transformed references; never change source data."""
    from PythonQt import QtGui, QtCore

    result = QtGui.QPainterPath()

    def collect(shape, tx, ancestors):
        if shape.excluded:
            return
        if shape.id in ancestors:
            raise ValueError("Cyclic element reference")
        transform = compose(shape.transform, tx)
        children = shape.includesList
        if children:
            for child in children:
                collect(child, transform, ancestors | {shape.id})
            return
        closed = shape.closedPath
        result.addPath(transform.map(closed))
        pen = shape.pen
        if pen.style() != QtCore.Qt.NoPen and pen.widthF() > 0:
            stroker = QtGui.QPainterPathStroker(pen)
            stroke_source = QtGui.QPainterPath(closed)
            stroke_source.addPath(shape.openedPath)
            result.addPath(transform.map(stroker.createStroke(stroke_source)))

    for shape in layer.shapes:
        collect(shape, QtGui.QTransform(), set())
    return result


class GlyphCollection:
    def __init__(self, font):
        self.font = font
        self.cache = {}

    def __getitem__(self, name):
        if name in self.cache:
            return self.cache[name]
        raw = self.font.raw.findName(name)
        if raw is None or raw.isNull:
            return None
        glyph = Glyph(self.font, raw)
        self.cache[name] = glyph
        return glyph

    def __iter__(self):
        # flPackage's sequence iterator does NOT terminate at glyphsCount.
        for raw in self.font.raw.fgPackage.glyphs:
            yield self[raw.name]


class LayerCollection:
    def __init__(self, glyph):
        self.glyph = glyph
        self.cache = {}

    def __getitem__(self, name):
        if name not in self.cache:
            raw = self.glyph.raw.findLayer(name)
            if raw is None or raw.isNull:
                return None
            if name not in self.glyph.parent.master_by_name:
                return None
            self.cache[name] = Layer(
                self.glyph, raw, self.glyph.parent.master_by_name[name]
            )
        return self.cache[name]

    def __iter__(self):
        for name in self.glyph.parent.master_by_name:
            layer = self[name]
            if layer:
                yield layer


class Font:
    def __init__(self, raw):
        import fontlab as fl

        self.raw = raw
        self.upm = raw.upm
        self.familyName = raw.info.familyName
        lib = dict(raw.packageLib)
        saved = lib.get(STORAGE_KEY)
        data = (
            json.loads(saved) if isinstance(saved, str) else copy.deepcopy(saved or {})
        )
        self.userData = UserData(data.get("userData", {}))
        # Read Glyphs userData that survives import, if the adapter has no setup yet.
        for key, value in lib.items():
            if (
                key.startswith(
                    ("com.htfonts.letterspacer.", "com.eweracs.HTLSManager.")
                )
                and key != STORAGE_KEY
            ):
                self.userData.setdefault(key, value)
        self.classifications = copy.deepcopy(data.get("classifications", {}))
        self.masters = []
        for name in raw.masters:
            with master_context(raw, name):
                ml = dict(raw.masterLib)
                saved_master = data.get("masters", {}).get(name, {})
                params = UserData()
                for key in ("paramArea", "paramDepth", "paramOver", "paramFreq"):
                    value = ml.get(
                        "com.schriftgestaltung.fontMaster." + key, ml.get(key)
                    )
                    if value is not None:
                        try:
                            params[key] = float(value)
                        except (TypeError, ValueError):
                            pass
                params.update(saved_master.get("parameters", {}))
                user = UserData(
                    {
                        k: v
                        for k, v in ml.items()
                        if k.startswith("com.htfonts.letterspacer.")
                    }
                )
                user.update(saved_master.get("userData", {}))
                self.masters.append(
                    SimpleNamespace(
                        name=name,
                        id=name,
                        xHeight=fl.FontMetrics(raw, name).xHeight,
                        italicAngle=-float(raw.italicAngle_value),
                        customParameters=params,
                        userData=user,
                    )
                )
        self.master_by_name = {m.name: m for m in self.masters}
        self.glyphs = GlyphCollection(self)

    def commit(self):
        data = {
            "version": 1,
            "userData": dict(self.userData),
            "classifications": self.classifications,
            "masters": {
                m.name: {
                    "parameters": dict(m.customParameters),
                    "userData": dict(m.userData),
                }
                for m in self.masters
            },
        }
        lib = dict(self.raw.packageLib)
        lib[STORAGE_KEY] = json.dumps(data, ensure_ascii=False, allow_nan=False)
        self.raw.packageLib = lib
        self.raw.changed()


class Glyph:
    def __init__(self, font, raw):
        self.parent = font
        self.raw = raw
        self.name = raw.name
        attrs = classify(
            self.name, list(raw.fgGlyph.unicodes), font.classifications.get(self.name)
        )
        self.__dict__.update(attrs)
        self.layers = LayerCollection(self)
        self.leftMetricsKey = None
        self.rightMetricsKey = None


class Layer:
    def __init__(self, glyph, raw, master):
        self.parent = glyph
        self.raw = raw
        self.master = master
        self.name = raw.name
        self.layerId = raw.name
        self.associatedMasterId = master.id
        self.attributes = {}
        self.components = []
        self.refresh()

    def refresh(self):
        self.path = qpath(self.raw)
        self.outline = from_qpath(self.path)
        self.bounds = self.outline.bounds
        self.paths = [self.outline] if self.outline.segments else []
        self.width = float(self.raw.advanceWidth)
        slanted = self.outline.deslant(self.master.italicAngle, self.master.xHeight)
        self.LSB = slanted.bounds[0]
        self.RSB = self.width - slanted.bounds[2]
        self.parent.leftMetricsKey = self.raw.metricsLeft or None
        self.parent.rightMetricsKey = self.raw.metricsRight or None

    def hasAlignedWidth(self):
        return bool(self.raw.autoLayer)

    def copyDecomposedLayer(self):
        return self  # Already a detached numeric snapshot.

    def calculateIntersectionsStartPoint_endPoint_(self, start, end):
        return (
            [start]
            + [Point(x, start.y) for x in self.outline.glyphs_intersections(start.y)]
            + [end]
        )
