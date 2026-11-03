"""Non-destructive Glyph-window overlay via FontLab 9 Python painters."""

import json
from PythonQt import QtCore, QtGui
import fontlab as fl


class Reporter:
    def __init__(self, window):
        self.window = window
        self.canvas = None
        self.token = None
        self.cache = {}
        self.items = []
        self.timer = QtCore.QTimer(window.dialog)
        self.timer.connect("timeout()", self.refresh)

    def start(self):
        if not hasattr(fl.flCanvas, "appendPythonPainter"):
            raise RuntimeError(
                "This FontLab build lacks Python painters; use the Parameters preview or update FontLab 9."
            )
        self.refresh()
        self.timer.start(700)

    def stop(self):
        self.timer.stop()
        if self.canvas is not None and self.token is not None:
            try:
                self.canvas.removePythonPainter(self.token)
                self.canvas.update()
            except (RuntimeError, ValueError):
                pass
        self.canvas = None
        self.token = None
        self.items = []
        self.cache = {}

    def refresh(self):
        try:
            self.window.session.assert_current()
            canvas = fl.flWorkspace.instance().getActiveCanvas()
            if canvas is None or canvas.isNull:
                return
            if self.canvas is None or self.canvas.id != canvas.id:
                self.stop()
                self.canvas = canvas
                self.token = canvas.appendPythonPainter(self.paint, canvas.OverOwner)
                self.timer.start(700)
            session = self.window.session
            signature = json.dumps(
                {
                    "rules": session.rules,
                    "masters": {
                        m.id: [dict(m.customParameters), dict(m.userData)]
                        for m in session.font.masters
                    },
                    "classification": session.font.classifications,
                },
                sort_keys=True,
            )
            items = []
            cache = {}
            for block in canvas.textBlocks():
                for info in block.getAllGlyphs():
                    if len(items) >= 100:
                        break
                    glyph = info.glyph
                    if glyph.package.id != session.raw.id:
                        continue
                    raw = glyph.activeLayer
                    key = (glyph.name, raw.name)
                    # Geometry signatures also invalidate composites when their
                    # base changes; never run spacing inside a paint callback.
                    layer = session.font.glyphs[glyph.name].layers[raw.name]
                    if layer is None:
                        continue
                    layer.refresh()
                    stamp = (layer.outline.segments, raw.advanceWidth, signature)
                    old = self.cache.get(key)
                    if old and old[0] == stamp:
                        result = old[1]
                    else:
                        result = session.calculate(names=[glyph.name], master=raw.name)[
                            0
                        ]
                    cache[key] = (stamp, result)
                    if result.get("polygons"):
                        items.append((info, result))
            self.cache = cache
            self.items = items
            canvas.update()
        except Exception as exc:
            self.stop()
            self.window.overlay.setChecked(False)
            self.window.status.setText("Areas overlay stopped: " + str(exc))

    def paint(self, painter, canvas):
        # The host owns and invalidates this painter after the callback returns.
        palette = ["#008f9b", "#c36c31", "#6970b6", "#5c9146", "#ac568b"]
        for info, result in self.items:
            if info.isNull or not info.isPresent:
                continue
            rid = result["engine"].matched_rule_id
            ids = list(self.window.session.rules)
            color = QtGui.QColor(
                palette[ids.index(rid) % len(palette)] if rid in ids else "#888888"
            )
            color.setAlpha(85)
            painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            painter.setBrush(QtGui.QBrush(color))
            for polygon in result["polygons"]:
                path = QtGui.QPainterPath()
                for index, p in enumerate(polygon):
                    point = canvas.mapToViewportF(
                        info.transform.map(QtCore.QPointF(p.x, p.y))
                    )
                    if index == 0:
                        path.moveTo(point)
                    else:
                        path.lineTo(point)
                path.closeSubpath()
                painter.drawPath(path)
            if info.isActive:
                anchor = canvas.mapToViewportF(
                    info.transform.map(QtCore.QPointF(0.0, result["layer"].bounds[1]))
                )
                label = (
                    self.window.title_rule(result["engine"].matched_rule or {})
                    if rid
                    else "No matching rule"
                )
                painter.setPen(QtGui.QPen(QtGui.QColor("#666666")))
                painter.drawText(QtCore.QPointF(anchor.x(), anchor.y() + 30.0), label)
