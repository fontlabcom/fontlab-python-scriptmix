# FLM: HTLS FontLab Smoke Test (disposable font)
# this_file: varia/HT-Letterspacer-FL/src/tests/fontlab_smoke.py
"""Run inside FontLab 9. Creates/closes only its own test fonts."""
import json
import math
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fly import fl, fg, pr as fontpr
from fly.qt import QtCore, QtGui
from htls_fontlab.service import Session
from htls_fontlab.model import qpath, from_qpath, STORAGE_KEY


def assert_segments_equal(a, b):
    assert len(a) == len(b)
    assert all(
        abs(x - y) < 1e-7
        for aa, bb in zip(a, b)
        for ap, bp in zip(aa, bb)
        for x, y in zip(ap, bp)
    )


def run():
    original = fl.flWorkspace.instance().currentPackage
    original_id = (
        original.fgPackage.id if original is not None and not original.isNull else None
    )
    created = []
    out = Path(tempfile.mkdtemp(prefix="htls-fontlab-smoke-"))
    try:
        fontpr.new_font(family_name="HTLS Adapter Smoke Test", style_name="Regular")
        p = fl.flWorkspace.instance().currentPackage
        created.append(p.fgPackage.id)
        p.xHeight_value = 500
        for name in (
            "htlsTestBase",
            "htlsTestComposite",
            "htlsTestEmpty",
            "htlsTestStroke",
        ):
            p.addGlyph(fg.fgGlyph(name))
        base = p.findName("htlsTestBase")
        layer = base.activeLayer
        layer.advanceWidth = 500
        shape = fl.flShape()
        shape.addContour(
            fl.flContour(
                [
                    fl.flNode(QtCore.QPointF(x, y), nodeType="on")
                    for x, y in [(100, 0), (300, 0), (300, 500), (100, 500)]
                ],
                closed=True,
            ),
            True,
        )
        layer.addShape(shape)
        comp = p.findName("htlsTestComposite")
        cl = comp.activeLayer
        cl.advanceWidth = 600
        cl.addComponent(
            ("htlsTestBase", QtGui.QTransform(0.8, 0.2, 0.0, 1.0, 40.0, 20.0))
        )
        fl.flItems.notifyChangesApplied("HTLS test fixtures", [base, comp], True)
        orig = from_qpath(qpath(cl)).segments
        s = Session.current()
        s.rules = {}
        m = s.master()
        m.customParameters.update(paramArea=400.0, paramDepth=15.0, paramOver=0.0)
        old_round = fl.flPreferences().editorStrongRound
        r = s.apply(names=["htlsTestBase"])
        assert r[0]["after"] == (80, 80, 360.0)
        assert_segments_equal(orig, from_qpath(qpath(cl)).segments)
        assert fl.flPreferences().editorStrongRound == old_round
        print(
            "PASS rectangle, affine component preservation, rounding preference restoration"
        )
        l = s.font.glyphs["htlsTestBase"].layers[p.master]
        l.refresh()
        left = l.LSB
        width = l.width
        s.apply(
            names=["htlsTestBase"],
            params={"paramArea": 500},
            manual={"LSB": False, "RSB": True},
        )
        l.refresh()
        assert l.LSB == left and l.width > width
        width = l.width
        s.apply(
            names=["htlsTestBase"], params={"paramArea": 700}, manual={"tabular": True}
        )
        l.refresh()
        assert l.width == width
        s.apply(names=["htlsTestBase"], manual={"tabular": True, "width": 595})
        l.refresh()
        assert l.width == 595 and abs(l.LSB + l.RSB + 200 - 595) < 1e-7
        print("PASS side toggles, fixed width and explicit tabular width")
        # Ordinary FontLab pen strokes are measured as rendered outlines.
        stroke = p.findName("htlsTestStroke")
        sl = stroke.activeLayer
        sl.advanceWidth = 500
        ss = fl.flShape()
        ss.addContour(
            fl.flContour(
                [fl.flNode(QtCore.QPointF(200, y), nodeType="on") for y in (0, 500)],
                closed=False,
            ),
            True,
        )
        pen = QtGui.QPen(QtGui.QColor("black"))
        pen.setWidthF(100)
        ss.pen = pen
        sl.addShape(ss)
        outline = from_qpath(qpath(sl))
        assert abs(outline.bounds[2] - outline.bounds[0] - 100) < 1e-7
        assert "after" in s.calculate(names=["htlsTestStroke"])[0]
        print("PASS ordinary pen stroke expansion")
        original_angle = p.italicAngle_value
        p.italicAngle_value = -12
        shear = math.tan(math.radians(12))
        layer.applyTransform(QtGui.QTransform(1.0, 0.0, shear, 1.0, -250 * shear, 0.0))
        s = Session.current()
        s.rules = {}
        r = s.apply(names=["htlsTestBase"], params={"paramArea": 400, "paramOver": 0})
        l = r[0]["layer"]
        l.refresh()
        assert l.master.italicAngle == 12
        assert (
            abs(l.LSB - r[0]["after"][0]) < 1e-7
            and abs(l.RSB - r[0]["after"][1]) < 1e-7
        )
        p.italicAngle_value = original_angle
        print("PASS italic sign and sidebearings")
        s = Session.current()
        s.rules = {}
        assert "skip" in s.calculate(names=["htlsTestEmpty"])[0]
        assert base.hasHistoryStates
        print("PASS empty skip and native history registration")
        s.rules = s.upstream.config.default_rules()
        s.master().customParameters["paramFreq"] = 7
        s.save()
        expected = json.loads(p.packageLib[STORAGE_KEY])
        s.export_setup(out / "setup.json")
        reloaded = Session.current()
        assert (
            reloaded.rules == s.rules
            and reloaded.master().customParameters["paramFreq"] == 7
        )
        print("PASS embedded settings")
        for extension in ("vfj", "vfc"):
            path = str(out / ("roundtrip." + extension))
            fontpr.save_font(font_id=p.fgPackage.id, path=path)
            fontpr.open_font(path=path)
            loaded = fl.flWorkspace.instance().currentPackage
            loaded_id = loaded.fgPackage.id
            created.append(loaded_id)
            assert json.loads(loaded.packageLib[STORAGE_KEY]) == expected
            fontpr.close_font(font_id=loaded_id, save=False)
            created.remove(loaded_id)
            fontpr.set_active_font(font_id=p.fgPackage.id)
            print("PASS " + extension + " save/reopen")
        print("HTLS FontLab smoke tests passed. Test artifacts: " + str(out))
    finally:
        for font_id in reversed(created):
            fontpr.close_font(font_id=font_id, save=False)
        if original_id is not None:
            fontpr.set_active_font(font_id=original_id)


if __name__ == "__main__":
    run()
