"""HT Letterspacer adapter for FontLab 9 (Apache-2.0)."""

__version__ = "1.0.0"


def show():
    from .compact import show as open_window

    return open_window()


def apply_selection(**kwargs):
    from .service import Session

    return Session.current().apply(scope="selection", **kwargs)


def show_manager():
    from .ui import show as open_window

    return open_window()
