# this_file: tests/test_lint_baseline_docs.py
"""README and AGENTS must quote the same Ruff baseline count."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNT = re.compile(r"Ruff 0\.14\.10 reports\s+(\d+) existing findings")


def test_ruff_baseline_when_documented_then_readme_and_agents_agree():
    counts = {
        name: COUNT.search((ROOT / name).read_text()) for name in ("README.md", "AGENTS.md")
    }
    assert all(counts.values()), "both guides must state the Ruff 0.14.10 baseline"
    assert counts["README.md"].group(1) == counts["AGENTS.md"].group(1)
