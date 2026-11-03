"""Small PythonQt compatibility helpers (Qt properties can be non-callable)."""


def prop(obj, name):
    value = getattr(obj, name)
    return value() if callable(value) else value


def compose(a, b):
    """QTransform a followed by b; PythonQt does not expose matrix __mul__."""
    from PythonQt import QtGui

    return QtGui.QTransform(
        a.m11() * b.m11() + a.m12() * b.m21(),
        a.m11() * b.m12() + a.m12() * b.m22(),
        a.m21() * b.m11() + a.m22() * b.m21(),
        a.m21() * b.m12() + a.m22() * b.m22(),
        a.dx() * b.m11() + a.dy() * b.m21() + b.dx(),
        a.dx() * b.m12() + a.dy() * b.m22() + b.dy(),
    )
