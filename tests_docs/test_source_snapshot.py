# this_file: tests_docs/test_source_snapshot.py
"""Parentheses in source names must not disappear through codeinclude's grammar."""

import hashlib
import importlib.util
import re
from pathlib import Path

import pytest
from codeinclude.plugin import RE_SNIPPET

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "name", ["A (B).py", "Accented Ż.py", "Tick's Proof.py", "Dots.A.py"]
)
def test_menu_source_when_filename_contains_punctuation_then_exact_safe_include(
    tmp_path, name
):
    spec = importlib.util.spec_from_file_location(
        "owned_menu_docs", ROOT / "src_docs/build.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = tmp_path / "Scripts/Reports" / name
    source.parent.mkdir(parents=True)
    data = b'"""Owned report fixture."""\nprint("source is not executed")\n'
    source.write_bytes(data)
    module.catalogue(tmp_path)
    pages = [
        p
        for p in (tmp_path / "src_docs/md/scripts").glob("*/*.md")
        if p.name != "index.md"
    ]
    assert len(pages) == 1
    include = (
        pages[0]
        .read_text()
        .split("<!--codeinclude-->", 1)[1]
        .split("<!--/codeinclude-->", 1)[0]
    )
    match = re.search(RE_SNIPPET, include)
    assert match is not None, (
        "The real plugin grammar must recognize the whole filename"
    )
    target = (pages[0].parent / match.group("filename")).resolve()
    assert target.read_bytes() == data
    assert target.name == hashlib.sha256(data).hexdigest() + ".py"
    assert source.read_bytes() == data
