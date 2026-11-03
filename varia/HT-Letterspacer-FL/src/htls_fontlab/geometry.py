"""Exact Bezier scanline intersections (no flattening or raster approximation)."""

import math

EPS = 1e-9


def value(poly, t):
    result = 0.0
    for coefficient in poly:
        result = result * t + coefficient
    return result


def roots01(poly):
    """All real polynomial roots in [0,1], including tangent/end roots."""
    poly = list(poly)
    while len(poly) > 1 and abs(poly[0]) < 1e-12:
        poly.pop(0)
    degree = len(poly) - 1
    if degree == 0:
        return []
    if degree == 1:
        t = -poly[1] / poly[0]
        return [max(0.0, min(1.0, t))] if -EPS <= t <= 1 + EPS else []
    cuts = [0.0] + roots01([c * (degree - i) for i, c in enumerate(poly[:-1])]) + [1.0]
    cuts = sorted(set(cuts))
    roots = []
    for t in cuts:
        if abs(value(poly, t)) < EPS:
            roots.append(t)
    for lo, hi in zip(cuts, cuts[1:]):
        flo, fhi = value(poly, lo), value(poly, hi)
        if flo * fhi >= 0:
            continue
        for _ in range(48):
            mid = (lo + hi) / 2
            fm = value(poly, mid)
            if flo * fm <= 0:
                hi = mid
            else:
                lo = mid
                flo = fm
        roots.append((lo + hi) / 2)
    return sorted(set(round(t, 14) for t in roots))


def coefficients(values):
    if len(values) == 2:
        return [values[1] - values[0], values[0]]
    a, b, c, d = values
    return [-a + 3 * b - 3 * c + d, 3 * a - 6 * b + 3 * c, -3 * a + 3 * b, a]


class Outline:
    def __init__(self, segments):
        self.segments = tuple(tuple(tuple(p) for p in s) for s in segments)
        self.y_ranges = [
            (min(p[1] for p in s), max(p[1] for p in s)) for s in self.segments
        ]
        self.polynomials = [
            (coefficients([p[0] for p in s]), coefficients([p[1] for p in s]))
            for s in self.segments
        ]
        points = []
        for xp, yp in self.polynomials:
            ts = {0.0, 1.0}
            for poly in (xp, yp):
                degree = len(poly) - 1
                ts.update(roots01([c * (degree - i) for i, c in enumerate(poly[:-1])]))
            points.extend((value(xp, t), value(yp, t)) for t in ts)
        self.bounds = (
            (
                min(p[0] for p in points),
                min(p[1] for p in points),
                max(p[0] for p in points),
                max(p[1] for p in points),
            )
            if points
            else (0.0, 0.0, 0.0, 0.0)
        )

    def intersections(self, y):
        xs = []
        for (xp, yp), (ymin, ymax) in zip(self.polynomials, self.y_ranges):
            if y < ymin - EPS or y > ymax + EPS:
                continue
            target = yp[:-1] + [yp[-1] - y]
            if all(abs(c) < EPS for c in target):
                xs.extend((value(xp, 0), value(xp, 1)))
                degree = len(xp) - 1
                xs.extend(
                    value(xp, t)
                    for t in roots01([c * (degree - i) for i, c in enumerate(xp[:-1])])
                )
            else:
                xs.extend(value(xp, t) for t in roots01(target))
        return sorted(set(round(x, 8) for x in xs))

    def glyphs_intersections(self, y):
        """Glyphs' directed scanline convention: (start, end], no horizontal edges.

        Including both endpoints is mathematically reasonable but not what the
        original host does; HTLS samples exactly on outline extrema, so that
        difference can move bearings by several font units. Keep full precision
        here because the upstream engine applies ceil to derived areas.
        """
        xs = []
        for (xp, yp), (ymin, ymax) in zip(self.polynomials, self.y_ranges):
            if y < ymin - EPS or y > ymax + EPS:
                continue
            target = yp[:-1] + [yp[-1] - y]
            if all(abs(c) < EPS for c in target):
                continue
            xs.extend(value(xp, t) for t in roots01(target) if t > 1e-12)
        return sorted(set(xs))

    def deslant(self, angle, xheight):
        tangent = math.tan(math.radians(angle))
        return Outline(
            [
                [(x - (y - xheight / 2) * tangent, y) for x, y in s]
                for s in self.segments
            ]
        )


def from_qpath(path):
    segments = []
    current = None
    start = None
    i = 0
    count = path.elementCount()
    while i < count:
        e = path.elementAt(i)
        point = (e.x, e.y)
        kind = int(e.type)
        if kind == 0:
            current = start = point
        elif kind == 1:
            segments.append((current, point))
            current = point
        elif kind == 2:
            c2 = path.elementAt(i + 1)
            end = path.elementAt(i + 2)
            segments.append((current, point, (c2.x, c2.y), (end.x, end.y)))
            current = (end.x, end.y)
            i += 2
        i += 1
    return Outline(segments)
