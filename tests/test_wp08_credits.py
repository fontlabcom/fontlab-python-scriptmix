# this_file: tests/test_wp08_credits.py
"""WP08 candidate launchers name the real authors and licences of the originals they adapt."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "Scripts"
EXPECTED = {
    "Reports/Font Revision Comparison.py": ("Jens Kutilek", "MIT", "Copyright (c) 2017"),
    "Reports/Metric Reports.py": ("Pedro Arilla", "Apache-2.0"),
    "Reports/Geometry Audit.py": ("Simon Cozens", "Alex Slobzheninov", "Reza Bohloul", "independent implementation inspired by", "no code copied"),
    "Reports/Master Structure Audit.py": ("Fernando Diaz", "Reset Type Studio", "Simon Cozens"),
    "Reports/Open Contours App.py": ("Original workflow",),
    "Reports/Nodes Near Zones App.py": ("Original workflow",),
    "Utilities/Reference Image Viewer App.py": ("Original workflow",),
}


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_launcher_when_docstring_read_then_source_line_names_original_authors(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    source = next(line for line in text.splitlines() if line.startswith("Source:"))
    for needle in EXPECTED[name]:
        assert needle in source, (name, needle)
    assert "Original workflows" not in source


def test_font_audit_when_docstring_read_then_credits_line_names_original_authors():
    text = (ROOT / "Reports/Font Audit.py").read_text(encoding="utf-8")
    start = text.index("Credits:")
    credits = " ".join(text[start:text.index("See NOTICE", start)].split())
    for needle in ("FontLab App contributors (Apache-2.0)", "mekkablue", "(Apache-2.0)", "Simon Cozens", "(MIT)"):
        assert needle in credits, needle
