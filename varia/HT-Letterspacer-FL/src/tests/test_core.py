import json
import math
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from htls_fontlab.geometry import Outline, roots01
from htls_fontlab.upstream import load, Point
from htls_fontlab.classification import classify
from htls_fontlab.model import UserData
from htls_fontlab.service import validate_parameters, validate_rules


def rectangle(x0, y0, x1, y1):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return Outline([(a, b) for a, b in zip(pts, pts[1:] + pts[:1])])


class FakeLayer:
    def __init__(self, outline, xheight=500, upm=1000, angle=0, params=None, name="H"):
        self.outline = outline
        self.bounds = outline.bounds
        self.name = "Regular"
        self.layerId = "Regular"
        self.associatedMasterId = "Regular"
        self.master = NS(
            italicAngle=angle,
            xHeight=xheight,
            customParameters=UserData(params or {}),
            userData=UserData(),
        )
        font = NS(upm=upm, glyphs={}, userData=UserData())
        self.parent = NS(
            name=name,
            parent=font,
            leftMetricsKey=None,
            rightMetricsKey=None,
            category="Letter",
            subCategory=None,
            case=1,
            script="latin",
        )
        self.parent.layers = {"Regular": self}
        font.glyphs[name] = self.parent
        self.paths = [outline] if outline.segments else []
        self.components = []
        self.attributes = {}
        self.width = 500
        self.LSB = 100
        self.RSB = 200

    def hasAlignedWidth(self):
        return False

    def copyDecomposedLayer(self):
        return self

    def calculateIntersectionsStartPoint_endPoint_(self, a, b):
        return (
            [a] + [Point(x, a.y) for x in self.outline.glyphs_intersections(a.y)] + [b]
        )


class GeometryTests(unittest.TestCase):
    def test_rectangle_scanlines(self):
        outline = rectangle(100, 0, 300, 500)
        for y in (0, 100, 500):
            self.assertEqual(outline.intersections(y), [100, 300])
        self.assertEqual(outline.intersections(501), [])

    def test_glyphs_directed_scanline_endpoints(self):
        outline = rectangle(100, 0, 300, 500)
        self.assertEqual(outline.glyphs_intersections(0), [100])
        self.assertEqual(outline.glyphs_intersections(500), [300])
        self.assertEqual(outline.glyphs_intersections(250), [100, 300])
        horizontal = Outline([((100, 0), (300, 0))])
        self.assertEqual(horizontal.glyphs_intersections(0), [])

    def test_cubic_tangent(self):
        outline = Outline([((0, 0), (0, 200), (100, 200), (100, 0))])
        self.assertEqual(outline.bounds, (0, 0, 100, 150))
        self.assertEqual(outline.intersections(150), [50])
        xs = outline.intersections(75)
        self.assertEqual(len(xs), 2)
        self.assertAlmostEqual(sum(xs), 100)

    def test_cubic_three_roots(self):
        roots = roots01([1, -1.5, 0.66, -0.08])
        for got, want in zip(roots, [0.2, 0.5, 0.8]):
            self.assertAlmostEqual(got, want)
        self.assertEqual(len(roots), 3)

    def test_horizontal_segment_extrema(self):
        outline = Outline([((0, 10), (100, 10), (-100, 10), (0, 10))])
        xs = outline.intersections(10)
        self.assertAlmostEqual(min(xs), -28.86751346)
        self.assertAlmostEqual(max(xs), 28.86751346)


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.u = load()

    def engine(self, layer, rules=None):
        return self.u.engine.HTLSEngine(layer, font_rules=rules or {})

    def test_rectangle_golden(self):
        self.assertEqual(
            self.engine(
                FakeLayer(rectangle(100, 0, 300, 500))
            ).current_layer_sidebearings(),
            (80, 80),
        )

    def test_upm_scaling(self):
        self.assertEqual(
            self.engine(
                FakeLayer(rectangle(200, 0, 600, 1000), xheight=1000, upm=2000)
            ).current_layer_sidebearings(),
            (160, 160),
        )

    def test_reference_and_percent(self):
        layer = FakeLayer(rectangle(100, 0, 300, 500))
        rule = self.u.config.make_rule(
            category="Letter", area={"mode": "percent", "value": 125}
        )
        self.assertEqual(
            self.engine(layer, {"r": rule}).current_layer_sidebearings(), (100, 100)
        )

    def test_tabular(self):
        e = self.engine(FakeLayer(rectangle(100, 0, 300, 500)))
        e.tabVersion = True
        self.assertEqual(e.current_layer_sidebearings(), (150, 150))
        self.assertEqual(e.newWidth, 500)

    def test_explicit_tabular_width(self):
        e = self.engine(FakeLayer(rectangle(100, 0, 300, 500)))
        e.tabVersion = True
        e.width = 595
        self.assertEqual(e.current_layer_sidebearings(), (197.5, 197.5))
        self.assertEqual(e.newWidth, 595)

    def test_left_disabled(self):
        e = self.engine(FakeLayer(rectangle(100, 0, 300, 500)))
        e.LSB = False
        self.assertEqual(e.current_layer_sidebearings(), (100, 80))

    def test_metrics_keys(self):
        layer = FakeLayer(rectangle(100, 0, 300, 500))
        layer.parent.leftMetricsKey = "H"
        layer.parent.rightMetricsKey = "H"
        self.assertIsNone(self.engine(layer).current_layer_sidebearings())

    def test_empty(self):
        self.assertIsNone(
            self.engine(FakeLayer(Outline([]))).current_layer_sidebearings()
        )

    def test_master_override(self):
        layer = FakeLayer(rectangle(100, 0, 300, 500))
        rule = self.u.config.make_rule()
        layer.master.userData[self.u.config.MASTER_RULES_KEY] = {
            "r": {"area": {"mode": "absolute", "value": 500}}
        }
        self.assertEqual(
            self.engine(layer, {"r": rule}).current_layer_sidebearings(), (100, 100)
        )

    def test_private_imports(self):
        before = {
            n: sys.modules.get(n) for n in ("GlyphsApp", "Foundation", "objc", "htls")
        }
        self.engine(FakeLayer(rectangle(100, 0, 300, 500))).calculate_polygons()
        self.assertEqual(before, {n: sys.modules.get(n) for n in before})

    def test_rule_specificity(self):
        g = FakeLayer(rectangle(0, 0, 1, 1)).parent
        generic = self.u.config.make_rule(category="Letter")
        target = self.u.config.make_rule(glyphlist=["H"])
        self.assertEqual(self.u.rules.find_rule(g, {"a": generic, "b": target})[0], "b")


class ClassificationTests(unittest.TestCase):
    def test_common_categories(self):
        for name, field, want in [
            ("H", "case", 1),
            ("x", "case", 2),
            ("h.sc", "case", 3),
            ("dollar", "subCategory", "Currency"),
            ("zero.tf", "category", "Number"),
            ("quotedbl", "subCategory", "Quote"),
            ("alef-hb", "script", "hebrew"),
        ]:
            self.assertEqual(classify(name)[field], want, name)

    def test_legacy_encoded_names(self):
        self.assertEqual(classify("Omega", [0x2126])["category"], "Symbol")
        self.assertEqual(classify("Omega", [0x03A9])["category"], "Letter")
        self.assertEqual(classify("mu", [0x00B5])["case"], 0)
        self.assertEqual(classify("mu", [0x03BC])["case"], 2)
        self.assertEqual(classify("florin", [0x0192])["subCategory"], "Currency")
        self.assertEqual(classify("fhook", [0x0192])["category"], "Letter")

    def test_unicode_and_overrides(self):
        self.assertEqual(classify("custom", [0x3B1])["script"], "greek")
        self.assertEqual(
            classify("custom", [], {"category": "Mark"})["category"], "Mark"
        )

    def test_invalid_parameters(self):
        for value in (float("nan"), float("inf"), -1):
            with self.assertRaises(ValueError):
                validate_parameters({"paramArea": value})
        with self.assertRaises(ValueError):
            validate_parameters({"paramFreq": 0})

    def test_invalid_rules(self):
        with self.assertRaises(ValueError):
            validate_rules({"a": {"area": {"mode": "percent", "value": float("nan")}}})
        with self.assertRaises(ValueError):
            validate_rules({"a": {"glyphlist": "H"}})


if __name__ == "__main__":
    unittest.main()
