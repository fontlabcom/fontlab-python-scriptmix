# this_file: tests/_wp05_outline_routes.py
"""Current callable App routes and independently verified historical menu bytes."""
from pathlib import Path

from menu_layout import _menu_bytes

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    'Transform', 'Slant', 'Smart Slant', 'Rotate Selection',
    'Reflect Horizontally', 'Reflect Vertically', 'Align And Distribute',
    'Interpolated Nudge', 'Overlap Nodes', 'Superaligner',
    'Add Extremes', 'Correct Contour Direction', 'Delete Close Points',
    'Delete Duplicate Contours', 'Delete Small Contours', 'Fix Zero Handles',
    'Optimize Start Points', 'Remove Overlap', 'Round Coordinates',
    'Curve All Straights', 'Straighten All Curves', 'Straighten Short Curves',
    'Retract Handles', 'Simplify Selected Nodes',
}


def route_path(title: str) -> Path:
    if title not in TITLES:
        return ROOT / 'Scripts/Contours' / (title + '.py')
    relative = ('superaligner.py' if title == 'Superaligner' else
                'outline_routes/' + title.lower().replace(' ', '_') + '.py')
    return ROOT.parent / 'fontlab-fontlabapp/src/fontlabapp/fontui' / relative


def source_text(title: str) -> str:
    """Read exact prior current bytes via the existing hash-checked resolver."""
    return _menu_bytes(ROOT, f'Scripts/Contours/{title}.py').decode()
